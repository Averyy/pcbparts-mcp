// The numbers the page derives from /api/data. Run by tests/test_frontend.py (needs node).
import assert from "node:assert/strict";
import { test } from "node:test";
import {
  AMOUNT, aggregate, buildView, countedFrom, daily, digikeyPaths, hourly, mouserDayStartHour, own, problemHours, totals,
} from "../../src/pcbparts_dashboard/static/data.js";
import { dayHourET, delta, parseQuotaTime, resetHour, serverDay } from "../../src/pcbparts_dashboard/static/format.js";

const HOURS = Array.from({ length: 24 }, () => 100);
const tool = (calls, extra = {}) => ({ calls, ok: calls, similar_only: 0, not_found: 0, bad_request: 0, rate_limited: 0, failed: 0, ...extra });

/** One Eastern day as the backend sends it (winter: midnight Eastern is 05:00 UTC). */
function day(date, extra = {}) {
  const start = Date.parse(date + "T05:00:00Z");
  return {
    date, start: new Date(start).toISOString(), end: new Date(start + 86400_000).toISOString(),
    hours_in_window: 24, complete: true, partial_start: false, partial_end: false, approx: true, exact_calls: true,
    calls: 2400, hours: HOURS, tools: { jlc_search: tool(2400) }, apps: { "claude-code": 50 }, problems: null, ...extra,
  };
}
function dates(first, n) {
  const start = Date.parse(first + "T00:00:00Z");
  return Array.from({ length: n }, (_, i) => new Date(start + i * 86400_000).toISOString().slice(0, 10));
}
function payload(edays, at = "2026-11-21T21:35:00Z", extra = {}) {
  return { generated_at: at, as_of: at, last_success_at: at, edays, compare_today: null, ...extra };
}
/** The hours of a day after a deploy, as its problems part. */
function problems(startIso, hours, extra = {}) {
  return { start: startIso, calls: 500, tools: { jlc_search: tool(500, { ok: 480, bad_request: 20 }) }, failed_hours: hours.map(() => 0), refused_hours: hours, ...extra };
}

test("a multi-day range is compared only with a fully stored period before it", () => {
  const full = buildView(payload(dates("2026-11-06", 16).map((d) => day(d))), "7d");
  assert.deepEqual([full.dates[0], full.dates[6]], ["2026-11-14", "2026-11-20"]); // seven whole days ending yesterday
  assert.equal(full.compareLabel, "compared with the 7 days before");
  assert.equal(full.prevAgg.days_count, 7);

  const short = buildView(payload(dates("2026-11-13", 9).map((d) => day(d))), "7d"); // one day before the range
  assert.equal(short.prevAgg, null);
  assert.equal(short.compareLabel, null);
  assert.match(short.compareNote, /1 of the 7 days before/);

  const hole = buildView(payload(dates("2026-11-06", 16).filter((d) => d !== "2026-11-16").map((d) => day(d))), "7d");
  assert.equal(hole.missing, 1);
  assert.equal(hole.prevAgg, null);
});

test("today is compared with the backend's yesterday-by-this-time record", () => {
  const days = [day("2026-11-20"), day("2026-11-21", { calls: 900, complete: false, partial_end: true })];
  const cmp = { date: "2026-11-20", calls: 1600, tools: { jlc_search: tool(1600) }, apps: { "claude-code": 30 } };
  const view = buildView(payload(days, "2026-11-21T21:35:00Z", { compare_today: cmp }), "today");
  assert.deepEqual(view.dates, ["2026-11-21"]);
  assert.equal(totals(view.prevAgg).calls, 1600);
  assert.equal(view.compareLabel, "compared with yesterday by this time");
  assert.equal(buildView(payload(days), "today").prevAgg, null); // no record, no comparison
});

test("problems come only from the part of each day after the deploy", () => {
  const since = "2026-11-21T18:00:00Z";
  const wholeDay = { jlc_search: tool(2400, { ok: 2300, bad_request: 60, failed: 40 }) };
  const today = day("2026-11-21", {
    tools: wholeDay, per_ip_refusals: { total: 43 },
    problems: problems(since, [0, 3, 0, 0], { per_ip_refusals: { total: 3 } }),
  });
  const view = buildView(payload([day("2026-11-20", { tools: wholeDay }), today], "2026-11-21T21:35:00Z", { problems_since: since, problems_version: "0.10.5" }), "today");
  assert.equal(totals(view.agg).bad_request, 60); // the whole day, before and after
  assert.equal(totals(view.problems).bad_request, 20);
  assert.equal(totals(view.problems).failed, 0);
  assert.equal(view.problems.per_ip_refusals.total, 3);
  // a range that ends before the deploy has no problem numbers at all
  assert.equal(buildView(payload([day("2026-11-20", { tools: wholeDay }), today], "2026-11-21T21:35:00Z", { problems_since: since }), "yesterday").problems, null);
  // the charts take failed and turned away from the same part: the 43 from before the deploy stay out
  const hrs = hourly(view, view.dates);
  assert.equal(hrs.reduce((a, p) => a + (p.refused || 0), 0), 3);
  assert.equal(hrs.find((p) => p.refused === 3).ts, Date.parse("2026-11-21T19:00:00Z"));
  assert.equal(hrs[12].refused, null); // noon, before the deploy: not counted, not zero
  assert.equal(daily(view)[0].refused, 3);
});

test("the hours a problem happened in come from each day, at their own time", () => {
  const since = "2026-11-21T18:00:00Z";
  const d21 = day("2026-11-21", { problems: problems(since, [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0]) });
  const d22 = day("2026-11-22", { approx: false, problems: problems("2026-11-22T05:00:00Z", [...Array(23).fill(0), 2]) });
  const view = buildView(payload([d21, d22, day("2026-11-23")], "2026-11-23T15:00:00Z", { problems_since: since }), "7d");
  const hit = problemHours(view, "refused_hours").filter((p) => p.v > 0);
  assert.deepEqual(hit.map((p) => [new Date(p.ts).toISOString(), p.v]), [["2026-11-21T19:00:00.000Z", 4], ["2026-11-23T04:00:00.000Z", 2]]);
  // the summed record has no hourly lists to read them from
  assert.equal(view.problems.refused_hours, undefined);
  assert.equal(view.problems.start, undefined);
  // a nested list, picked by a function
  const held = day("2026-11-21", { problems: problems(since, [0, 0, 0, 0], { distributor_limits: { mouser: { held_back: { minute_cap: 5 }, held_back_hours: [0, 0, 5, 0] } } }) });
  const v2 = buildView(payload([held], "2026-11-21T21:35:00Z", { problems_since: since }), "today");
  assert.deepEqual(problemHours(v2, (p) => p.distributor_limits?.mouser?.held_back_hours).filter((p) => p.v).map((p) => new Date(p.ts).toISOString()), ["2026-11-21T20:00:00.000Z"]);
});

test("a counter that began after the range's first day says from when", () => {
  const since = "2026-11-21T18:00:00Z";
  const lat = (n) => ({ latency: { jlc_search: { counts: [n, 0, 0] } } });
  const up = (n) => ({ upstream: { jlcpcb: { sent: n, cached: 0 } } });
  const days = [
    ...dates("2026-11-10", 8).map((d) => day(d)),                       // Nov 10-17: neither counter
    day("2026-11-18", up(10)), day("2026-11-19", up(20)), day("2026-11-20", { ...up(30), restarts: 0 }),
    day("2026-11-21", { ...up(40), ...lat(7), problems: problems(since, [0, 0, 0, 0], lat(7)) }),
  ];
  const view = (key, extra = {}) => buildView(payload(days, "2026-11-21T21:35:00Z", { problems_since: since, ...extra }), key);

  // began with the deploy that starts the problems window: named to the minute
  assert.deepEqual(countedFrom(view("today"), AMOUNT.latency), { has: true, text: "since Sat 1:00 PM", start: "2026-11-21" });
  assert.deepEqual(countedFrom(view("yesterday"), AMOUNT.latency), { has: false, text: "since Sat 1:00 PM", start: "2026-11-21" });
  // began on an earlier day, rebuilt from server-day totals: a date, and "about"
  assert.equal(countedFrom(view("7d"), AMOUNT.upstream).text, "from about Nov 18");
  assert.equal(countedFrom(view("7d"), AMOUNT.upstream).has, true);
  // covers the whole range: nothing to say
  assert.equal(countedFrom(view("yesterday"), AMOUNT.upstream).text, "");
  assert.equal(countedFrom(view("today"), AMOUNT.upstream).text, "");
  // a counter at zero is still a counter that was kept
  assert.equal(countedFrom(view("7d"), AMOUNT.restarts).text, "from about Nov 20");
  // never kept at all
  assert.deepEqual(countedFrom(view("7d"), AMOUNT.terms), { has: false, text: "", start: null });
  // some of it from before the deploy: that day's midnight is the start, so today's range is covered
  const mixed = days.map((d) => (d.date === "2026-11-21" ? { ...d, ...lat(9) } : d));
  assert.equal(countedFrom(buildView(payload(mixed, "2026-11-21T21:35:00Z", { problems_since: since }), "today"), AMOUNT.latency).text, "");
  // an exact day carries no "about"
  const exact = days.map((d) => (d.date === "2026-11-18" ? { ...d, approx: false } : d));
  assert.equal(countedFrom(buildView(payload(exact, "2026-11-21T21:35:00Z", { problems_since: since }), "7d"), AMOUNT.upstream).text, "from Nov 18");
});

test("a version at zero starts on a rebuilt day is not a sighting", () => {
  const days = [day("2026-11-20", { versions: { "0.10.5": 0 } }), day("2026-11-21", { versions: { "0.10.5": 1 } })];
  assert.equal(buildView(payload(days), "today").seen.versions["0.10.5"], "2026-11-21");
});

test("names sent by clients never reach inherited properties", () => {
  const apps = JSON.parse('{"constructor": 9, "__proto__": 4, "toString": 2}');
  assert.equal(own(apps, "constructor"), 9);
  assert.equal(own(apps, "__proto__"), 4);
  assert.equal(own({ a: 1 }, "constructor"), undefined);
  assert.equal(own({ a: 1 }, "__proto__"), undefined);
  assert.equal(own(null, "a"), undefined);
  const agg = aggregate([day("2026-11-20", { apps }), day("2026-11-21", { apps: { constructor: 1, valueOf: 3 } })]);
  assert.deepEqual({ ...agg.apps }, { constructor: 10, ["__proto__"]: 4, toString: 2, valueOf: 3 });
  const view = buildView(payload([day("2026-11-20", { apps }), day("2026-11-21")]), "today");
  assert.equal(view.seen.apps.constructor, "2026-11-20");
  assert.equal(view.seen.apps.hasOwnProperty, undefined);
});

test("a change past ten times is given as a multiple, not a percent", () => {
  assert.equal(delta(18200, 1000).text, "18×");
  assert.equal(delta(1000, 100).text, "10×");
  assert.equal(delta(990, 100).text, "+890%");
  assert.equal(delta(50, 100).text, "−50%");
});

test("the server's day ends at 7 PM Eastern in winter and 8 PM in summer", () => {
  const winter = new Date("2026-11-21T21:35:00Z");
  assert.equal(resetHour(winter), "7 PM");
  assert.equal(dayHourET(serverDay(winter).start), "Fri 7 PM");
  assert.equal(dayHourET(serverDay(winter).end), "Sat 7 PM");
  assert.equal(resetHour(new Date("2026-07-04T15:00:00Z")), "8 PM");
});

for (const [at, mouserStart, digikeyStart] of [
  ["2026-11-23T23:59:59Z", "2026-11-23T06:00:00.000Z", "2026-11-23T00:00:00.000Z"],
  ["2026-11-24T00:00:00Z", "2026-11-23T06:00:00.000Z", "2026-11-24T00:00:00.000Z"],
  ["2026-11-24T05:59:59Z", "2026-11-23T06:00:00.000Z", "2026-11-24T00:00:00.000Z"],
  ["2026-11-24T06:00:00Z", "2026-11-24T06:00:00.000Z", "2026-11-24T00:00:00.000Z"],
]) test(`Mouser and DigiKey have separate budget days at ${at}`, () => {
  const now = new Date(at);
  const mouser = serverDay(now, mouserDayStartHour({}));
  assert.equal(mouser.start.toISOString(), mouserStart);
  assert.equal(mouser.end - mouser.start, 86400_000);
  assert.equal(serverDay(now).start.toISOString(), digikeyStart);
  assert.equal(resetHour(now, mouserDayStartHour({})), "1 AM");
  assert.equal(resetHour(now), "7 PM");
});

for (const [resets_at, expected] of [
  ["2026-11-24 00:00 UTC", 0], ["2026-07-05 05:00 UTC", 5], ["2026-11-24 09:00 UTC", 9],
  ["2026-11-24 23:00 UTC", 23], [undefined, 6], [null, 6], ["invalid", 6], ["2026-11-24 99:00 UTC", 6],
]) test(`Mouser reset hour from health: ${resets_at}`, () => {
  assert.equal(mouserDayStartHour({ distributor_quota: { mouser: { resets_at } } }), expected);
});

test("quota timestamps parse in UTC independently of the browser timezone", () => {
  assert.equal(parseQuotaTime("2026-11-24 09:00 UTC").toISOString(), "2026-11-24T09:00:00.000Z");
  assert.equal(mouserDayStartHour(null), 6);
});

for (const minute of [15, 45]) test(`problem bins start at the cutoff's hour (${minute} minutes past)`, () => {
  const since = `2026-11-21T18:${minute}:00Z`;
  const p = problems(since, [7, 2], { failed_hours: [3, 1], per_ip_refusals: { total: 9 } });
  const view = buildView(payload([day("2026-11-21", { problems: p })], "2026-11-21T20:00:00Z", { problems_since: since }), "today");
  const hrs = hourly(view, view.dates);
  assert.deepEqual(hrs.filter((p) => p.refused != null).map((p) => [new Date(p.ts).toISOString(), p.refused, p.failed]), [
    ["2026-11-21T18:00:00.000Z", 7, 3], ["2026-11-21T19:00:00.000Z", 2, 1],
  ]);
  assert.equal(hrs.reduce((n, p) => n + (p.refused || 0), 0), 9);
  assert.deepEqual(problemHours(view, "refused_hours").map((p) => p.ts), hrs.filter((p) => p.refused != null).map((p) => p.ts));
});

for (const flags of [{ complete: false, partial_end: true }, { complete: false }, { complete: true, partial_start: true }]) {
  test(`full-day ranges exclude incomplete records: ${JSON.stringify(flags)}`, () => {
    const days = dates("2026-11-07", 16).map((d) => day(d));
    days[15] = day("2026-11-22", { ...flags, calls: 1300, tools: { jlc_search: tool(1300) } });
    const p = payload(days, "2026-11-23T15:00:00Z", { as_of: "2026-11-22T18:00:00Z" });
    for (const key of ["yesterday", "7d"]) {
      const view = buildView(p, key);
      assert.equal(view.missing, 1);
      assert.equal(view.prevAgg, null);
      assert.equal(view.compareLabel, null);
      assert.equal(daily(view).at(-1).calls, null);
    }
    const all = buildView(p, "all");
    assert.equal(all.recs.some((r) => r.date === "2026-11-22"), false);
    // Incomplete comparison days also suppress the comparison.
    const before = buildView(payload([days[15], day("2026-11-23")], "2026-11-24T15:00:00Z"), "yesterday");
    assert.equal(before.prevAgg, null);
  });
}

test("legacy unsorted error replies are included in outcome totals", () => {
  const agg = aggregate([day("2026-11-20", { tools: { jlc_search: tool(10, { ok: 7, unsorted: 3 }) } })]);
  const t = totals(agg);
  assert.equal(t.unsorted, 3);
  assert.equal(Object.entries(t).filter(([k]) => k !== "calls").reduce((n, [, v]) => n + v, 0), t.calls);
});

test("DigiKey lookups split by path only on days that recorded ext_sent", () => {
  const dk = (digikey) => ({ distributors: { digikey, mouser: { sent: 9 } } });
  const days = [
    day("2026-11-18", dk({ sent: 40, cached: 3 })),                     // before server 0.10.11: one figure
    day("2026-11-19"),                                                  // no DigiKey lookups at all
    day("2026-11-20", dk({ sent: 30, cached: 1, ext_sent: 12 })),
    day("2026-11-21", dk({ sent: 20, cached: 0, ext_sent: 0 })),    // split, no ext lookups
  ];
  const pick = ({ api, ext, unsplit, split }) => ({ api, ext, unsplit, split });
  assert.deepEqual(pick(digikeyPaths(days)), { api: 38, ext: 12, unsplit: 40, split: true });
  assert.deepEqual(pick(digikeyPaths(days.slice(0, 2))), { api: 0, ext: 0, unsplit: 40, split: false });
  assert.deepEqual(pick(digikeyPaths([days[3]])), { api: 20, ext: 0, unsplit: 0, split: true });
  assert.deepEqual(pick(digikeyPaths([{ distributors: { digikey: { sent: 5, ext_sent: 9 } } }])),
    { api: 0, ext: 9, unsplit: 0, split: true }); // never a negative API figure
  // requests pair with their own day's lookups: a split day's API requests with its API lookups, an
  // unsplit day's requests (with any ext ones) with all of its lookups
  const up = (digikey, ext) => ({ upstream: { digikey: { sent: digikey }, ...(ext ? { digikey_ext: { sent: ext } } : {}) } });
  const paired = digikeyPaths([{ ...days[0], ...up(50) }, { ...days[2], ...up(36, 30) }, { ...dk({ sent: 10 }), ...up(6, 9) }]);
  assert.deepEqual([paired.requests, paired.lookups], [50 + 36 + 15, 40 + 18 + 10]);
  // the sum keeps the total; the split counter covers only its own days
  assert.deepEqual({ ...aggregate(days).distributors.digikey }, { sent: 90, cached: 4, ext_sent: 12 });
  const view = (key) => buildView(payload(days, "2026-11-22T21:35:00Z"), key);
  // a split with no ext lookups is still a split: counted from the first day that had one
  assert.equal(countedFrom(view("7d"), AMOUNT.digikeyPaths).text, "from about Nov 20");
  assert.equal(countedFrom(view("yesterday"), AMOUNT.digikeyPaths).text, "");
});
