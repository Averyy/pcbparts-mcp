// Turns the stored Eastern-day records (/api/data's edays) into the numbers one range shows.
// Every day here is a calendar day in America/New_York; the backend re-cuts the server's UTC days.
import { addDays, dayLabel, dayTimeET, etMidnight, parseQuotaTime, partsET } from "./format.js";

/** Older health samples omit the reset: use the server's default Mouser day start. */
export function mouserDayStartHour(health) {
  const reset = parseQuotaTime(health?.distributor_quota?.mouser?.resets_at);
  return reset && Number.isFinite(reset.getTime()) ? reset.getUTCHours() : 6;
}

export const OUTCOMES = ["ok", "similar_only", "not_found", "bad_request", "rate_limited", "failed", "unsorted"];
// the outcomes that are problems; counted only inside the problems window (since the deploy)
export const PROBLEM_OUTCOMES = ["bad_request", "rate_limited", "failed"];
export const NOT_NAMED_APPS = new Set(["other", "unknown"]);

export const RANGES = [
  { key: "today", label: "Today" },
  { key: "yesterday", label: "Yesterday" },
  { key: "7d", label: "7 days", days: 7 },
  { key: "30d", label: "30 days", days: 30 },
  { key: "90d", label: "90 days", days: 90 },
  { key: "all", label: "All" },
];

const obj = () => Object.create(null);
const HOUR_MS = 3600_000;
const hourStart = (iso) => Math.floor(Date.parse(iso) / HOUR_MS) * HOUR_MS;
export const completeDay = (d) => d.complete && !d.partial_start && !d.partial_end;

/**
 * A value from a parsed JSON object by a name the server didn't choose (app names, search words).
 * Plain objects inherit "constructor", "toString" and the like, so o[name] can return a function.
 */
export const own = (o, k) => (o != null && Object.hasOwn(o, k) ? o[k] : undefined);

// Record keys that describe the window rather than count something, and fields that can't be added.
const META = new Set(["date", "start", "end", "hours_in_window", "complete", "approx", "problems", "callers"]);
function skip(path, k) {
  if (path.length === 0) return META.has(k) || k.startsWith("_");
  if (path.length === 2 && path[0] === "tools") return k === "avg_ms";
  if (path.length === 2 && path[0] === "latency") return k.endsWith("_ms");
  if (path.length === 2 && path[0] === "parts_asked") return k === "distinct";
  return false;
}
const isMax = (path, k) => path[0] === "db_waits" && (k === "longest_ms" || k === "longest_ms_hours");

function addInto(dst, src, path) {
  for (const [k, v] of Object.entries(src)) {
    if (v == null || skip(path, k)) continue;
    const max = isMax(path, k);
    if (typeof v === "number") {
      dst[k] = max ? Math.max(dst[k] ?? 0, v) : (dst[k] ?? 0) + v;
    } else if (Array.isArray(v)) {
      // hourly lists are placed by time elsewhere; adding them index by index across days is meaningless
      if (path.length === 0 || k.endsWith("_hours") || k === "hours") continue;
      if (!Array.isArray(dst[k])) dst[k] = v.map(() => null);
      const d = dst[k];
      v.forEach((x, i) => { if (typeof x === "number") d[i] = max ? Math.max(d[i] ?? 0, x) : (d[i] ?? 0) + x; });
    } else if (typeof v === "object") {
      if (!dst[k] || typeof dst[k] !== "object" || Array.isArray(dst[k])) dst[k] = obj();
      addInto(dst[k], v, [...path, k]);
    }
  }
  return dst;
}

/** Sum window records (days, or the parts of days after the deploy), plus a calls-weighted avg_ms. */
export function aggregate(recs) {
  const sum = obj();
  for (const r of recs) addInto(sum, r, []);
  sum.days_count = recs.length;
  sum.approx = recs.some((r) => r.approx);
  const w = obj();
  for (const r of recs) for (const [t, v] of Object.entries(r.tools || {})) {
    if (typeof v?.avg_ms !== "number" || !v.calls) continue;
    w[t] ??= [0, 0];
    w[t][0] += v.avg_ms * v.calls;
    w[t][1] += v.calls;
  }
  sum.avg_ms = obj();
  for (const [t, [a, c]] of Object.entries(w)) sum.avg_ms[t] = c ? a / c : null;
  return sum;
}

export function totals(agg) {
  const out = Object.fromEntries(OUTCOMES.map((o) => [o, 0]));
  out.calls = 0;
  for (const v of Object.values(agg?.tools || {})) {
    out.calls += v.calls || 0;
    for (const o of OUTCOMES) out[o] += v[o] || 0;
  }
  if (!agg?.tools && typeof agg?.calls === "number") out.calls = agg.calls;
  return out;
}

export function sumArr(a) { return Array.isArray(a) ? a.reduce((x, y) => x + (y || 0), 0) : 0; }
export const sumObj = (o) => Object.values(o || {}).reduce((a, b) => a + (typeof b === "number" ? b : 0), 0);

/** Mouser's HTTP request counts start in 0.10.9, in upstream_status rather than upstream. */
export function upstreamCounts(record, src) {
  const counts = own(record?.upstream, src);
  if (counts) return counts;
  const status = src === "mouser" && own(record?.upstream_status, src);
  return status ? { sent: sumObj(status) } : {};
}

/** The latency buckets of every tool added up. */
export function allLatency(agg) {
  let counts = null;
  for (const v of Object.values(agg?.latency || {})) {
    if (!Array.isArray(v?.counts)) continue;
    counts ??= v.counts.map(() => 0);
    v.counts.forEach((c, i) => (counts[i] += c || 0));
  }
  return counts;
}

export function namedApps(apps) {
  return Object.entries(apps || {}).filter(([n, c]) => !NOT_NAMED_APPS.has(n) && c > 0);
}

/** Calls and outcomes by app (tool_apps, from 0.10.5), added over tools. */
export function callsByApp(agg) {
  const out = obj();
  for (const apps of Object.values(agg?.tool_apps || {})) {
    for (const [app, v] of Object.entries(apps || {})) {
      if (!(v?.calls > 0)) continue;
      out[app] ??= Object.assign(obj(), { calls: 0, ...Object.fromEntries(OUTCOMES.map((o) => [o, 0])) });
      out[app].calls += v.calls || 0;
      for (const o of OUTCOMES) out[app][o] += v[o] || 0;
    }
  }
  return out;
}

/** First Eastern day each app, version and tool appears in the store. */
export function firstSeen(days) {
  const apps = obj(), versions = obj(), tools = obj();
  for (const d of days) {
    for (const [a, c] of Object.entries(d.apps || {})) if (c > 0 && !(a in apps)) apps[a] = d.date;
    // a re-cut day can carry a version at 0 starts (its share rounded away): that isn't a sighting
    for (const [v, n] of Object.entries(d.versions || {})) if (n > 0 && !(v in versions)) versions[v] = d.date;
    for (const [t, v] of Object.entries(d.tools || {})) if (v?.calls > 0 && !(t in tools)) tools[t] = d.date;
  }
  return { apps, versions, tools };
}

function datesBack(end, n) {
  const out = [];
  for (let i = n - 1; i >= 0; i--) out.push(addDays(end, -i));
  return out;
}

/**
 * Everything one range shows. Multi-day ranges cover whole Eastern days ending yesterday, so no
 * number mixes a finished day with the one in progress. Problem numbers come only from each day's
 * `problems` part (the hours since the deploy), never from the whole day.
 */
export function buildView(payload, key) {
  const days = payload.edays || [];
  const now = new Date(payload.generated_at);
  const asOf = new Date(payload.as_of || payload.last_success_at || payload.generated_at);
  const today = partsET(now).key;
  // A fetch from yesterday can still contain yesterday's unfinished day. Only today's
  // live record may be partial; historical charts and comparisons require whole days.
  const byDate = new Map(days.filter((d) => !d.partial_start && (d.date === today || completeDay(d))).map((d) => [d.date, d]));
  const yesterday = addDays(today, -1);
  const range = RANGES.find((r) => r.key === key) || RANGES[0];
  let dates, prevDates = null, compareRec = null, compareLabel = null, compareNote = null;

  if (range.key === "today") {
    dates = [today];
    if (byDate.has(today) && payload.compare_today) {
      compareRec = payload.compare_today;
      compareLabel = "compared with yesterday by this time";
    }
  } else if (range.key === "yesterday") {
    dates = [yesterday];
    prevDates = [addDays(yesterday, -1)];
    compareLabel = "compared with the day before";
  } else if (range.days) {
    dates = datesBack(yesterday, range.days);
    prevDates = datesBack(addDays(yesterday, -range.days), range.days);
    compareLabel = `compared with the ${range.days} days before`;
  } else {
    dates = days.filter(completeDay).map((d) => d.date).filter((d) => d < today);
    if (!dates.length) dates = [yesterday];
  }

  const recs = dates.map((d) => byDate.get(d)).filter(Boolean);
  const missing = dates.length - recs.length;
  let prevRecs = prevDates ? prevDates.map((d) => byDate.get(d)).filter(Boolean) : null;
  // compare only like with like: every day on both sides, or no comparison
  if (prevRecs && (missing || prevRecs.length < prevDates.length)) {
    if (prevRecs.length && !missing) compareNote = `no comparison: only ${prevRecs.length} of the ${prevDates.length} days before are on record`;
    prevRecs = null;
    compareLabel = null;
  }
  if (compareRec) prevRecs = [compareRec];
  const prevAgg = prevRecs ? aggregate(prevRecs) : null;

  // problems: only the parts of these days after the deploy
  const since = payload.problems_since ? new Date(payload.problems_since) : null;
  const probRecs = recs.map((r) => r.problems).filter(Boolean);
  const problems = probRecs.length ? aggregate(probRecs) : null;

  let rangeText;
  if (range.key === "today") rangeText = `${dayLabel(today, { weekday: true, long: true })}, since midnight`;
  else if (dates.length === 1) rangeText = dayLabel(dates[0], { weekday: true, long: true });
  else rangeText = `${dayLabel(dates[0])} to ${dayLabel(dates[dates.length - 1])} (${dates.length} days)`;

  return {
    key: range.key, range, dates, recs, agg: aggregate(recs), prevAgg, compareLabel, compareNote,
    problems, since, sinceVersion: payload.problems_version || null,
    today, yesterday, now, asOf, days, byDate, rangeText, missing,
    approx: recs.some((r) => r.approx),
    bounds: payload.latency_bounds_ms || [50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 60000],
    seen: firstSeen(days),
    single: dates.length === 1,
  };
}

/**
 * How much of one counter a day record holds. The server began keeping these at different versions,
 * so a range can start before a counter does; countedFrom() finds where each one begins.
 */
export const AMOUNT = {
  latency: (r) => Object.values(r?.latency || {}).reduce((a, l) => a + sumArr(l?.counts), 0),
  toolApps: (r) => Object.values(r?.tool_apps || {}).reduce((a, apps) => a + Object.values(apps || {}).reduce((x, v) => x + (v?.calls || 0), 0), 0),
  terms: (r) => sumObj(r?.popular_terms),
  reasons: (r) => Object.values(r?.reasons || {}).reduce((a, labels) => a + sumObj(labels), 0),
  upstream: (r) => [...new Set([...Object.keys(r?.upstream || {}), "mouser"])].reduce((a, src) => a + AMOUNT.upstreamOf(src)(r), 0),
  upstreamOf: (src) => (r) => {
    const u = upstreamCounts(r, src);
    return (u.sent || 0) + (u.cached || 0);
  },
  dbJobs: (r) => r?.db_waits?.jobs || 0,
  datasheets: (r) => r?.datasheet_links?.visits || 0,
  distributorApps: (r) => Object.values(r?.distributor_apps || {}).reduce((a, apps) => a + Object.values(apps || {}).reduce((x, v) => x + (v?.calls || 0), 0), 0),
  restarts: (r) => (r?.restarts == null ? 0 : 1), // recorded at all, even at zero
};

/**
 * Where a counter's numbers begin, for a block that has to say so. Returns
 *   has:  whether any day of the range holds some;
 *   text: "" when the counter covers the whole range (or was never kept), else "since Sat 1:00 PM"
 *         (it began with the deploy that starts the problems window) or "from Nov 19"
 *         ("from about Nov 18" when that day was rebuilt from server-day totals, so it may be a day off).
 */
export function countedFrom(view, amount) {
  const first = view.days.find((d) => amount(d) > 0);
  const has = view.recs.some((r) => amount(r) > 0);
  if (!first) return { has: false, text: "", start: null };
  const rangeStart = view.dates[0];
  const deployDay = view.since ? partsET(view.since).key : null;
  let text = "";
  if (first.date === deployDay && first.problems && amount(first.problems) >= amount(first)) {
    // nothing of it before the deploy: it starts at that minute, not at that day's midnight
    if (etMidnight(rangeStart) < view.since.getTime()) text = `since ${dayTimeET(view.since)}`;
  } else if (first.date > rangeStart) {
    text = `from ${first.approx ? "about " : ""}${dayLabel(first.date)}`;
  }
  return { has, text, start: first.date };
}

/** The 14 days ending at the range's last day: the trend behind every sparkline. */
export function trendDays(view, n = 14) {
  const end = view.dates[view.dates.length - 1];
  return datesBack(end, n).map((d) => view.byDate.get(d) || null);
}

/** Hours in an Eastern day: 24, or 23/25 when clocks change. */
export function hoursInDay(date) { return Math.round((etMidnight(addDays(date, 1)) - etMidnight(date)) / HOUR_MS); }

/**
 * One entry per hour of the given Eastern days: {ts, date, calls, failed, refused, future, current,
 * beforeSince}. failed/refused come from each day's problems part, so hours before the deploy have none.
 */
export function hourly(view, dates) {
  const out = [];
  const asOfMs = view.asOf.getTime();
  const sinceMs = view.since ? view.since.getTime() : Infinity;
  for (const date of dates) {
    const rec = view.byDate.get(date);
    const start = rec?.start ? Date.parse(rec.start) : etMidnight(date);
    const n = hoursInDay(date);
    const p = rec?.problems;
    const pStart = p?.start ? hourStart(p.start) : null;
    for (let i = 0; i < n; i++) {
      const ts = start + i * HOUR_MS;
      const future = ts >= asOfMs;
      const current = !future && ts + HOUR_MS > asOfMs;
      const j = pStart == null ? -1 : Math.floor((ts - pStart) / HOUR_MS);
      const inP = j >= 0 && !future;
      out.push({
        ts, date, future, current, beforeSince: ts + HOUR_MS <= sinceMs,
        calls: future ? null : rec?.hours?.[i] ?? null,
        failed: inP ? p.failed_hours?.[j] ?? null : null,
        refused: inP ? p.refused_hours?.[j] ?? null : null,
      });
    }
  }
  return out;
}

/** Daily totals for the multi-day charts. */
export function daily(view) {
  return view.dates.map((d) => {
    const r = view.byDate.get(d) || null;
    const p = r?.problems ? aggregate([r.problems]) : null;
    return {
      date: d, rec: r,
      calls: r?.calls ?? (r ? totals(aggregate([r])).calls : null),
      failed: p ? totals(p).failed : null,
      refused: p ? p.per_ip_refusals?.total ?? 0 : null,
    };
  });
}

/**
 * Hourly points of one problems series over the range, each at its own time. A range's problems
 * are several days' parts added up, so the hours have to come from each day, not from the sum.
 * `pick`: the list's name, or a function from a day's problems part to the list.
 */
export function problemHours(view, pick) {
  const out = [];
  for (const r of view.recs) {
    const p = r.problems;
    const list = p && (typeof pick === "function" ? pick(p) : p[pick]);
    if (!Array.isArray(list) || !p.start) continue;
    const start = hourStart(p.start);
    list.forEach((v, i) => out.push({ ts: start + i * HOUR_MS, v: v || 0 }));
  }
  return out;
}
