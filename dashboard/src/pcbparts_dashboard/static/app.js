// PCB Parts usage dashboard: one page over /api/data. Days and times are Eastern. Every number covers
// the selected range; where the range crosses the latest deploy (payload.problems_since), problem
// counts also say how many came since that version. Notices the reader dismissed are kept by the
// dashboard's backend (/api/dismissals) and come back once something new happens after the dismissal.
import {
  addDays, ago, compact, dateTimeET, dayHourET, dayLabel, dayTimeET, delta, etMidnight, full, h, hourET,
  latencyText, ms, parseIso, parseQuotaTime, partsET, percent, percentile, resetHour, serverDay, timeET, tzAbbr, weekdayDateET,
} from "./format.js";
import {
  AMOUNT, NOT_NAMED_APPS, RANGES, addressBound, aggregate, allLatency, allStarts, budgetPause, budgetPool, buildView, callsByApp, completeDay,
  countedFrom, daily, digikeyPaths, heldBackOf, hourly, limitSplit, mouserDayStartHour, namedApps, own, pathsOf, pausedNow, problemHours,
  sumArr, sumObj, totals, trendDays, upstreamCounts,
} from "./data.js";
import {
  DISTRIBUTOR_LABEL, ERROR_GROUPS, HARD_ERRORS, TOOL_SHORT, badRequestLabel, heldBackLabel, isFailureReason, linkedFailure,
  reasonLabel, refusalGroupLabel, refusedLabel, upstreamLabel,
} from "./labels.js";
import { columns, hideTip, legend, lines, showTip, sparkline } from "./charts.js";

const $ = (id) => document.getElementById(id);
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const HEAT_RAMP = ["#2a2416", "#4a3418", "#71481d", "#9c6025", "#cd7f32", "#e8a94f"];
const HOUR = 3600_000;
const plural = (n, one, many = one + "s") => `${full(n)} ${n === 1 ? one : many}`;
/** A label used inside a sentence: its first letter in lower case, unless it opens with a name (JLCPCB, SamacSys, Mouser). */
const midSentence = (s) => (/^(\S*[A-Z]\S*[A-Z]|Mouser\b)/.test(s) ? s : s.charAt(0).toLowerCase() + s.slice(1));
const cap1 = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const LEVELS = { critical: 0, serious: 1, warning: 2, info: 3 };

let payload = null;
let currentView = null;
let loadError = null;
let pollTimer = null;
let dayTimer = null;
// key -> {day, count, at}: the notices dismissed, with each one's count on the day of the data it was
// dismissed on (from /api/dismissals)
const dismissed = new Map();
let dismissError = null;
const state = { range: "today", open: new Set(), sort: { key: "calls", dir: -1 }, tables: new Set(), showDismissed: false, undo: null };

// ---------------------------------------------------------------- loading

async function load({ quiet = false } = {}) {
  const main = $("main");
  if (payload && !quiet) main.classList.add("stale");
  const marks = loadDismissals();
  try {
    const r = await fetch("/api/data", { cache: "no-store" });
    if (!r.ok) throw new Error(`/api/data answered ${r.status}`);
    const next = await r.json();
    await marks;
    payload = next;
    loadError = null;
    render();
    // read again shortly after the poller's next fetch, so "Next update" never sits in the past
    clearTimeout(pollTimer);
    const wait = Date.parse(payload.next_poll_at) - Date.parse(payload.generated_at);
    if (wait > 0) pollTimer = setTimeout(() => load({ quiet: true }), wait + 45_000);
  } catch (e) {
    loadError = e.message || "no answer";
    if (!payload) {
      const boot = $("boot");
      boot.classList.add("error");
      boot.textContent = `Couldn't load the numbers: ${loadError}`;
    } else render();
  } finally {
    main.classList.remove("stale");
  }
}

async function refresh() {
  const btn = $("refresh");
  btn.disabled = true;
  btn.textContent = "Fetching";
  try {
    const r = await fetch("/api/refresh", { method: "POST", headers: { "X-Dashboard-Request": "1" } });
    const body = await r.json().catch(() => ({}));
    if (r.status === 429) {
      btn.textContent = `Wait ${body.retry_after ?? 60} s`;
      setTimeout(() => { btn.textContent = "Refresh"; btn.disabled = false; }, Math.min(60, body.retry_after ?? 10) * 1000);
      return;
    }
    if (!r.ok) throw new Error(`/api/refresh answered ${r.status}`);
    await load();
  } catch (e) {
    loadError = `Refresh failed: ${e.message || "no answer"}`;
    if (payload) render();
    else renderHeader();
  }
  btn.textContent = "Refresh";
  btn.disabled = false;
}

function setRange(key) {
  if (state.range === key) return;
  state.range = key;
  history.replaceState(null, "", `#r=${key}`);
  render({ rangeOnly: true });
}

function readHash() {
  const m = location.hash.match(/r=([a-z0-9]+)/);
  if (m && RANGES.some((r) => r.key === m[1])) state.range = m[1];
}

// ---------------------------------------------------------------- dismissals

function setDismissed(list) {
  dismissed.clear();
  for (const d of Array.isArray(list) ? list : []) {
    if (d && typeof d.key === "string" && typeof d.count === "number") dismissed.set(d.key, { day: d.day || null, count: d.count, at: d.at });
  }
}

async function loadDismissals() {
  try {
    const r = await fetch("/api/dismissals", { cache: "no-store" });
    if (!r.ok) throw new Error(`answered ${r.status}`);
    setDismissed((await r.json()).dismissals);
    dismissError = null;
  } catch (e) {
    dismissError = `Dismissed notices couldn't be loaded (${e.message || "no answer"}): they show again until they can.`;
  }
}

/** POST a dismissal ({day, count}) for a key, or DELETE it (to null); the reply is the whole list. */
async function sendDismissal(key, to) {
  const remove = to == null;
  const r = await fetch(remove ? `/api/dismissals?key=${encodeURIComponent(key)}` : "/api/dismissals", {
    method: remove ? "DELETE" : "POST", cache: "no-store",
    headers: { "X-Dashboard-Request": "1", ...(remove ? {} : { "Content-Type": "application/json" }) },
    body: remove ? undefined : JSON.stringify({ key, count: to.count, day: to.day }),
  });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.error || `answered ${r.status}`);
  setDismissed(body.dismissals);
}

/** Set a key back to `to` (a previous dismissal, or none), shown at once and undone if the server refuses. */
async function setDismissal(key, to, { undo = null, focus = null } = {}) {
  const was = dismissed.get(key) || null;
  to ? dismissed.set(key, to) : dismissed.delete(key);
  state.undo = undo;
  renderAttention(currentView);
  if (focus) ($(focus) || $("attention-head"))?.focus({ preventScroll: true });
  try {
    await sendDismissal(key, to);
    dismissError = null;
  } catch (e) {
    was ? dismissed.set(key, was) : dismissed.delete(key);
    state.undo = null;
    dismissError = `Couldn't save that (${e.message || "no answer"}).`;
  }
  const keep = document.activeElement?.id || focus;
  renderAttention(currentView);
  // the redraw replaced the focused control: focus its new copy, or the box's heading if it's gone
  if (keep && (document.activeElement === document.body || !document.activeElement?.isConnected)) ($(keep) || $("attention-head"))?.focus({ preventScroll: true });
}

/**
 * Dismiss a notice as of the data shown: its count on the data's own day is kept, so everything
 * after it (later that day, and every later day) brings the notice back, whatever range is shown.
 */
function dismiss(it) {
  const day = partsET(currentView.asOf).key;
  const rec = (payload.edays || []).find((d) => d.date === day);
  const to = { day, count: rec ? dayCounts(rec).get(it.key) || 0 : 0, at: new Date(Date.now()).toISOString() };
  return setDismissal(it.key, to, { undo: { key: it.key, what: it.what, prev: dismissed.get(it.key) || null }, focus: "undo-dismiss" });
}
const undoDismiss = () => state.undo && setDismissal(state.undo.key, state.undo.prev, { focus: noticeId(state.undo.key) });
// back in the list: focus the notice's own Dismiss button again
const restore = (it) => setDismissal(it.key, null, { focus: noticeId(it.key) });
const noticeId = (key) => `notice-${key}`;

// ---------------------------------------------------------------- shared bits

function cardHead(section, title, desc, { table = false } = {}) {
  const head = h("div", { class: "card-head" }, h("h2", { text: title, "data-text": title }));
  if (table) {
    const on = state.tables.has(section.id);
    section.classList.toggle("show-table", on);
    const btn = h("button", {
      id: `table-${section.id}`,
      type: "button", "aria-pressed": on ? "true" : "false", text: "Table", title: "Show the numbers behind the charts",
      onclick: () => {
        const now = !state.tables.has(section.id);
        now ? state.tables.add(section.id) : state.tables.delete(section.id);
        section.classList.toggle("show-table", now);
        btn.setAttribute("aria-pressed", now ? "true" : "false");
      },
    });
    head.append(h("div", { class: "head-tools" }, btn));
  }
  if (desc) head.append(h("p", {}, h("span", { text: desc })));
  return head;
}

/** Percent change, for calls and sessions only. */
function change(cur, prev, opts = {}) {
  if (cur == null || prev == null || !prev) return null;
  return delta(cur, prev, opts);
}

function deltaEl(d, vs) {
  if (!d) return null;
  return h("span", { class: "delta", "data-tone": d.tone }, (d.arrow ? d.arrow + " " : "") + d.text, vs ? h("span", { class: "vs", text: " " + vs }) : null);
}

/** What the range is compared with: "yesterday by this time", "the day before", "the 7 days before". */
function comparedWith(view) {
  if (!view.prevAgg) return null;
  if (view.key === "today") return "yesterday by this time";
  if (view.key === "yesterday") return "the day before";
  return `the ${view.dates.length} days before`;
}
const compareShort = (view) => (view.prevAgg ? `vs ${comparedWith(view)}` : null);

/** cls: one class per column ("opt-sm", "opt-md", "opt-lg" hide it on narrower screens). */
function table(headers, rows, { cls } = {}) {
  const ths = headers.map((x) => (x instanceof Node ? x : h("th", { text: x })));
  if (cls) {
    ths.forEach((th, i) => cls[i] && th.classList.add(cls[i]));
    for (const tr of rows) {
      if (tr.classList.contains("detail-row")) continue;
      [...tr.children].forEach((td, i) => cls[i] && td.classList.add(cls[i]));
    }
  }
  return h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, ths)), h("tbody", {}, rows)));
}

/** Label and value pairs. A list as the value goes under its label, one line each. */
function kv(pairs, { stack = false, cls = "" } = {}) {
  const dl = h("dl", { class: `kv${stack ? " stack" : ""}${cls ? ` ${cls}` : ""}` });
  for (const [k, v] of pairs) {
    if (k == null || v == null) continue;
    if (Array.isArray(v)) {
      dl.append(h("dt", { class: "wide", text: k }), h("dd", { class: "wide" }, h("ul", {}, v.map((x) => h("li", { text: x })))));
    } else dl.append(h("dt", { text: k }), h("dd", {}, v instanceof Node ? v : String(v)));
  }
  return dl;
}

/** Ranked horizontal bars; rows: [{name, sub, value}]. `max`: the full bar's value, for lists that share one scale. */
function ranked(rows, { limit = 12, total, color, empty = "None.", max } = {}) {
  rows = rows.filter((r) => r.value > 0);
  if (!rows.length) return h("div", { class: "empty", text: empty });
  rows.sort((a, b) => b.value - a.value);
  const shown = rows.slice(0, limit);
  max = max || shown[0].value || 1;
  const box = h("div", { class: "ranked" });
  for (const r of shown) {
    const name = h("div", { class: "n", title: r.sub ? `${r.sub}: ${r.name}` : r.name },
      r.sub ? h("span", { class: "t", text: r.sub + "  " }) : null, r.name);
    const bar = h("div", { class: "track" }, h("i", { class: "bar", style: { width: `${Math.max(0.5, (r.value / max) * 100)}%`, background: color || css("--copper") } }));
    box.append(h("div", { class: "r" }, name, bar, h("div", { class: "v" }, full(r.value), total ? h("small", { text: percent(r.value / total) }) : null)));
  }
  if (rows.length > limit) {
    const rest = rows.slice(limit).reduce((a, r) => a + r.value, 0);
    box.append(h("div", { class: "r muted" }, h("div", { class: "n", text: `${rows.length - limit} more` }), h("div"), h("div", { class: "v", text: full(rest) })));
  }
  return box;
}

/** A number cell that stays blank at zero, so real numbers stand out. */
function numCell(n, of) {
  if (!n) return h("td", { class: "zero" });
  return h("td", {}, full(n), of >= 30 ? h("span", { class: "pct", text: percent(n / of) }) : null);
}

/**
 * "7 PM to 8 PM", or "between 12 AM and 5 AM", for the hours with a non-zero value. `withDay` names
 * the day too ("Sat 7 PM"): needed whenever the range, or the hours themselves, span more than one day.
 */
function whenText(points, withDay = false) {
  const hit = points.filter((p) => p.v > 0);
  if (!hit.length) return "";
  const a = new Date(hit[0].ts), b = new Date(hit[hit.length - 1].ts + HOUR);
  const days = withDay || partsET(a).key !== partsET(new Date(b.getTime() - 1)).key;
  const at = (d) => (days ? dayHourET(d) : hourET(d));
  if (hit.length === 1) return `${at(a)} to ${hourET(b)}`;
  return `between ${at(a)} and ${at(b)}`;
}

/** At most how many addresses were behind `count` events: never more than the events themselves. */
const addressesOf = (bound, count) => (bound == null ? (count === 1 ? 1 : null) : Math.min(bound, count));

/** " from 1 address" or " from up to 4 addresses" (server 0.10.12's distinct counts); "" when unknown. */
function fromAddresses(bound, count = Infinity) {
  const n = addressesOf(bound, count);
  if (n == null || n < 1) return "";
  return n === 1 ? " from 1 address" : ` from up to ${full(n)} addresses`;
}

/** A moment shown with its weekday when it isn't on the same Eastern day as `ref`. */
function momentText(d, ref = new Date(Date.now())) {
  return partsET(d).key === partsET(ref).key ? timeET(d) : dayTimeET(d);
}
const quotaTime = (text) => { const t = parseQuotaTime(text); return t && Number.isFinite(t.getTime()) ? momentText(t) : String(text); };

// ---------------------------------------------------------------- the latest deploy

/**
 * Where the range stands against the latest deploy (payload.problems_since). Every count covers the
 * whole range; `crosses`: the deploy falls inside the range, so counts also say how many came since.
 */
function scope(view) {
  const since = view.since;
  const ver = view.sinceVersion;
  if (!since) return { crosses: false, from: null, ver, label: "", when: "" };
  const start = etMidnight(view.dates[0]);
  const end = view.key === "today" ? view.asOf.getTime() : etMidnight(addDays(view.dates[view.dates.length - 1], 1));
  const t = since.getTime();
  const when = dayTimeET(since);
  return { crosses: start < t && t < end, from: since, ver, when, label: ver ? `since ${ver}` : `since ${when}` };
}

/** "3 since 0.10.11" where the range crosses the deploy, else "". */
const sinceText = (sc, n) => (sc.crosses ? `${full(n || 0)} ${sc.label}` : "");

/** Where "since <version>" counts start, said once: the dashboard's check before a deploy, not the deploy's minute. */
function sinceNote(sc) {
  if (!sc.crosses) return "";
  const vs = payload?.version_since;
  const start = sc.ver ? versionStart(sc.ver) : null;
  const when = momentText(sc.from);
  if (!sc.ver) return `“${sc.label}” counts start at ${when}.`;
  if (vs?.version === sc.ver && vs.configured) return `“${sc.label}” counts start at ${when}, as configured.`;
  if (start?.exact && start.at - sc.from > 60_000) return `“${sc.label}” counts start at ${when}, the dashboard's last check before it started at ${timeET(start.at)}.`;
  if (vs?.version === sc.ver && vs.first_seen && Date.parse(vs.first_seen) > sc.from) return `“${sc.label}” counts start at ${when}, the dashboard's last check before it went live.`;
  return `“${sc.label}” counts start at ${when}.`;
}

/**
 * When a version began: exact from the server's own start list (0.10.12), else between the
 * dashboard's last check of the version before and its first check of this one.
 */
function versionStart(version) {
  const runs = payload?.versions || [];
  const run = [...runs].reverse().find((r) => r.version === version);
  if (run?.exact) { const at = new Date(run.from); return { at, exact: true, text: `since ${dayTimeET(at)}` }; }
  if (run?.after) {
    const a = new Date(run.after), b = new Date(run.from);
    return { at: b, from: a, exact: false, text: `started between ${dayTimeET(a)} and ${momentText(b, a)}` };
  }
  const vs = payload?.version_since;
  if (vs?.version === version) {
    const a = parseIso(vs.since), b = parseIso(vs.first_seen);
    if (vs.configured && a) return { at: a, exact: true, text: `since ${dayTimeET(a)}` };
    if (a && b && a < b) return { at: b, from: a, exact: false, text: `started between ${dayTimeET(a)} and ${momentText(b, a)}` };
    if (a || b) return { at: b || a, exact: false, text: `first seen ${dayTimeET(b || a)}` };
  }
  if (run) { const at = new Date(run.from); return { at, exact: false, text: `first seen ${dayTimeET(at)}` }; }
  return null;
}

/** Everything a record holds that counts as a problem, as plain counts. */
function figures(a) {
  if (!a) return null;
  const T = totals(a);
  let held = 0, blocked = 0;
  for (const lim of Object.values(a.distributor_limits || {})) {
    for (const [cause, n] of Object.entries(pathsOf(lim?.held_back, lim?.ext_held_back))) {
      if (cause === "address_blocked") blocked += n.all; else held += n.all;
    }
  }
  const refused = a.per_ip_refusals?.total ?? 0;
  const links = a.datasheet_links?.refused ?? 0;
  return { T, calls: T.calls, failed: T.failed, rejected: T.bad_request, refused, held, blocked, links, turnedAway: refused + held + links };
}

/** Failed calls whose reason ties them to one service's error answers; null for a service with no such reason. */
function lookupsFailed(a, src) {
  if (linkedFailure(src, "") === null) return null;
  let n = 0;
  for (const labels of Object.values(a?.reasons || {})) for (const [c, v] of Object.entries(labels || {})) if (linkedFailure(src, c)) n += v || 0;
  return n;
}

/** A service's error answers by status class; Mouser's limit replies (429) have their own notices. */
function errorGroups(st, { skipMouser429 = false, src = "" } = {}) {
  return ERROR_GROUPS.map((g) => [g.label, g.keys.reduce((x, k) => x + (skipMouser429 && src === "mouser" && k === "429" ? 0 : own(st, k) || 0), 0)]).filter(([, v]) => v > 0);
}

// ---------------------------------------------------------------- header

function nextUpdate() {
  return payload?.next_poll_at ? new Date(payload.next_poll_at) : null;
}

/** Health has its own fetch time; freshness follows the selected distributor's day. */
function healthSample(view, startHourUTC = 0) {
  const at = parseIso(payload?.health_at);
  const known = at && Number.isFinite(at.getTime());
  const now = new Date(Math.max(view?.now?.getTime() || 0, Date.now()));
  return {
    at: known ? at : null,
    label: known ? `${dateTimeET(at)} ${tzAbbr(at)}` : "an unknown time",
    currentDay: known && serverDay(at, startHourUTC).start.getTime() === serverDay(now, startHourUTC).start.getTime(),
    retained: !!payload?.last_fetch?.health_error || !known || at < parseIso(payload?.as_of),
  };
}

// DigiKey's paused_until describes its API pool; an installed extension (ext) still answers while that is
// paused, but only when lookups are routed to it (ext.active) and it isn't paused itself. A pause whose
// time has passed is over, however old the sample that reported it.
function cannotAnswer(name, q, now = Date.now()) {
  if (!pausedNow(q?.paused_until, now)) return false;
  return name !== "digikey" || !(q.ext?.active === true && !pausedNow(q.ext.paused_until, now));
}

/** "DigiKey API paused" when ext's status is unknown: true whether or not an extension exists. */
function pauseLabel(name, q) {
  if (name === "digikey" && typeof q?.ext?.active !== "boolean") return "DigiKey API paused";
  return `${DISTRIBUTOR_LABEL[name] || name} paused`;
}

function renderHeader() {
  const hl = payload?.health;
  const sample = healthSample();
  const now = Date.now();
  const problems = [];
  if (payload?.last_fetch?.health_error) problems.push("health update failed");
  if (hl) {
    if (hl.status !== "healthy") problems.push(hl.status || "unhealthy");
    if (hl.snapshot?.stale) problems.push("catalog out of date");
    const dp = hl.database_pressure;
    if (dp && (dp.stalled_seconds > 0 || dp.waiting > 0)) problems.push(`${dp.waiting} database jobs waiting`);
    for (const [k, q] of Object.entries(hl.distributor_quota || {})) if (cannotAnswer(k, q, now)) problems.push(pauseLabel(k, q));
  }
  const led = $("led");
  led.hidden = !problems.length;
  led.dataset.state = hl && hl.status !== "healthy" ? "critical" : "warning";
  $("led-text").textContent = problems.join(", ");

  const bs = $("board-status");
  bs.querySelectorAll(".extra").forEach((e) => e.remove());
  if (hl) {
    // the health values' own time only where it differs from the update time
    const asOf = parseIso(payload.as_of);
    if (!sample.at || !asOf || Math.abs(sample.at - asOf) > 90_000) bs.append(h("span", { class: "extra", text: `Health values from ${sample.label}` }));
    const start = hl.version ? versionStart(hl.version) : null;
    bs.append(h("span", { class: "extra" }, "Server ", h("b", { text: (hl.version || "?") + (start ? ` ${start.text}` : "") })));
    const scraped = parseIso(hl.snapshot?.data_as_of || hl.price_tiers?.as_of);
    if (scraped) bs.append(h("span", { class: "extra" }, "Last JLCPCB scrape ", h("b", { text: dayTimeET(scraped) })));
  }

  const lf = payload?.last_fetch, fs = $("fetch-state"), ft = $("fetch-text");
  const ok = parseIso(payload?.as_of || payload?.last_success_at);
  const next = nextUpdate();
  ft.replaceChildren();
  if (loadError) {
    fs.dataset.error = "true";
    ft.append(loadError, h("br"), ok ? `Showing numbers from ${dateTimeET(ok)} ${tzAbbr(ok)}` : "No numbers loaded");
    return;
  }
  if (lf && !lf.ok) {
    fs.dataset.error = "true";
    ft.append("Update failed ", h("b", { text: timeET(new Date(lf.at)) }), h("br"), (lf.error || "").slice(0, 60));
  } else {
    fs.dataset.error = "false";
    ft.append("Updated ", h("b", { text: ok ? `${timeET(ok)} ${tzAbbr(ok)}` : "never" }), ok ? h("span", { class: "ago", text: `, ${ago(ok, Date.now())}` }) : "");
  }
  if (lf?.health_error) {
    fs.dataset.error = "true";
    ft.append(h("br"), `Health update failed: ${lf.health_error}`);
  }
  ft.append(h("br"), "Next update ", h("b", { text: next ? timeET(next) : "not scheduled" }));
}

function renderControls(view) {
  const complete = view.days.filter((d) => d.date < view.today && completeDay(d)).length;
  // a range longer than the store is the same as All: leave it out
  const shown = RANGES.filter((r) => !r.days || r.days <= 30 || complete >= r.days);
  const ranges = $("ranges");
  if (ranges.children.length !== shown.length || shown.some((r, i) => ranges.children[i]?.id !== `range-${r.key}`)) {
    ranges.replaceChildren(...shown.map((r) => h("button", {
      id: `range-${r.key}`, type: "button", text: r.label, onclick: () => setRange(r.key),
    })));
  }
  shown.forEach((r) => $(`range-${r.key}`).setAttribute("aria-pressed", r.key === view.key ? "true" : "false"));
  const rt = $("range-text");
  const asOf = timeET(view.asOf);
  if (view.key === "today") {
    rt.replaceChildren(h("strong", { text: `${view.rangeText.replace(", since midnight", "")}, midnight to ${asOf}` }),
      view.prevAgg ? `, compared with yesterday to ${asOf}` : "");
  } else if (view.single) {
    rt.replaceChildren(h("strong", { text: view.rangeText }), view.compareLabel ? `, ${view.compareLabel}` : "");
  } else {
    const first = dayLabel(view.dates[0]), last = dayLabel(view.dates[view.dates.length - 1]);
    const name = view.key === "all" ? `All ${view.dates.length} full days on record` : `Last ${view.dates.length} full days`;
    rt.replaceChildren(h("strong", { text: `${name} (${first} to ${last})` }), ", today not included",
      view.compareLabel ? `, ${view.compareLabel}` : view.compareNote ? `, ${view.compareNote}` : "");
  }
  if (view.missing) rt.append(`. ${view.missing} ${view.missing === 1 ? "day has" : "days have"} no ${view.key === "today" ? "" : "complete "}record`);
}

// ---------------------------------------------------------------- worth a look

/**
 * What a distributor refusal notice says, by cause: DigiKey's 403 pauses its lookups 10 minutes.
 * split: every day with refusals counted ext's apart, so the rest are the API's.
 */
function refusalWhat(name, cause, n, split = true) {
  const who = DISTRIBUTOR_LABEL[name] || name;
  const req = plural(n.all, "request");
  if (name === "mouser" && cause === "daily") return `Mouser refused ${req} for its daily limit (expected: lookups retry hourly or just after the next daily reset).`;
  if (cause === "daily") return `${who} refused ${req} for its daily limit${name === "digikey" ? " (429)" : ""}.`;
  if (cause === "minute") return `${who} refused ${req} for its per-minute limit${name === "digikey" ? " (429)" : ""}.`;
  if (name === "digikey" && cause === "refused") {
    if (!n.ext) return `DigiKey refused ${req} (403); each refusal paused lookups for 10 minutes.`;
    if (!split) return `DigiKey refused ${req}, ${full(n.ext)} of them through ext.`;
    const parts = [n.api ? `${full(n.api)} from the API (403, each pausing lookups for 10 minutes)` : "", `${full(n.ext)} through ext`].filter(Boolean);
    return `DigiKey refused ${req}: ${parts.join(", ")}.`;
  }
  if (cause === "refused") return `${who} refused ${req} with no reason given.`;
  return `${who} refused ${req}: ${refusedLabel(cause, name)}.`;
}

/**
 * The notices for the range, most serious first. Count-based ones carry a key (kind and subject) and
 * a count, so a dismissal can hide one until its count grows; live state has neither and clears itself.
 */
function attentionItems(view, sc) {
  const items = [];
  const lf = payload.last_fetch;
  const okAt = parseIso(payload.as_of || payload.last_success_at);
  if (lf && !lf.ok) items.push({ level: "critical", what: `The last update failed (${timeET(new Date(lf.at))}): ${lf.error || "no answer"}.`, detail: okAt ? `The numbers below are from ${dayTimeET(okAt)}.` : "" });
  else if (okAt && Date.now() - okAt > ((payload.poll_minutes || 60) * 2 + 10) * 60_000) {
    items.push({ level: "warning", what: `No update since ${dayTimeET(okAt)}.`, detail: "Is the dashboard's poller running?" });
  }
  const warned = new Map();
  for (const w of payload.warnings || []) {
    if (!(Date.now() - Date.parse(w.at) < 7 * 86400_000)) continue;
    warned.set(String(w.message).slice(0, 10), w);
  }
  for (const w of warned.values()) items.push({ key: `warning:${w.at}`, count: 1, level: "warning", what: w.message, detail: `Noted by the dashboard, ${dayTimeET(new Date(w.at))}.` });
  const hl = payload.health;
  const sample = healthSample(view);
  if (lf?.health_error) items.push({ level: "warning", what: `Health update failed: ${lf.health_error}.`, detail: hl ? `Retained health values are from ${sample.label}.` : "No health values are available." });
  if (hl && hl.status !== "healthy") items.push({ level: "critical", what: `The server reported "${hl.status || "no status"}".`, detail: `From /health, checked ${sample.label}.` });
  if (hl?.snapshot?.stale) items.push({ level: "warning", what: "The parts catalog is out of date.", detail: `Last JLCPCB scrape ${dayTimeET(new Date(hl.snapshot.data_as_of))}.` });
  if (hl?.database_pressure?.waiting > 0) items.push({ level: "warning", what: `${plural(hl.database_pressure.waiting, "database job")} waiting when health was checked ${sample.label}.`, detail: `The oldest had waited ${hl.database_pressure.oldest_wait_seconds} s.` });
  if (payload.kept_across_restarts === false) {
    items.push({ level: "warning", what: "The server's stats aren't kept across restarts.", detail: "Its stats file isn't set up or can't be written: each restart starts the day's counts again." });
  }
  for (const [name, q] of Object.entries(hl?.distributor_quota || {})) {
    if (q?.kept_across_restarts === false) items.push({ level: "warning", what: `${DISTRIBUTOR_LABEL[name] || name}'s budget counts aren't kept across restarts.`, detail: "A restart starts the day's count again, so more could go out than the budget allows." });
  }

  const a = view.agg, p = sc.crosses ? view.problems : null;
  const since = (n) => sinceText(sc, n);
  for (const [t, v] of Object.entries(a.tools || {})) {
    if (!(v?.failed > 0)) continue;
    const labels = Object.entries(own(a.reasons, t) || {}).filter(([c, n]) => n > 0 && isFailureReason(c)).sort((x, y) => y[1] - x[1]);
    let rest = v.failed;
    const add = (reason, n, sinceN) => items.push({
      key: `failed:${t}:${reason}`, count: n, level: "critical",
      what: `${plural(n, `${t} call`)} failed${reason === "unlabelled" ? "" : `: ${midSentence(reasonLabel(reason))}`}.`,
      detail: reason === "unlabelled" ? "No reason was recorded for these (before 0.9.0)." : "", since: since(sinceN),
    });
    for (const [c, n] of labels) {
      if (rest <= 0) break;
      add(c, Math.min(n, rest), own(own(p?.reasons, t), c));
      rest -= n;
    }
    if (rest > 0) {
      // failures from before 0.9.0 carry no reason
      const labelledSince = Object.entries(own(p?.reasons, t) || {}).reduce((x, [c, n]) => x + (isFailureReason(c) ? n : 0), 0);
      add("unlabelled", rest, Math.max(0, (own(p?.tools, t)?.failed || 0) - labelledSince));
    }
  }
  const f = figures(a);
  if (f.refused) {
    const pr = a.per_ip_refusals;
    const groups = ["everyone_else", "platform_ranges", "too_many_clients", "server_busy"].filter((g) => pr[g] > 0);
    const when = whenText(problemHours(view, "refused_hours"), !view.single);
    const bound = addressBound(view.recs, "rate_limited");
    items.push({
      key: "per_ip_refusals", count: f.refused, level: "warning",
      what: `${plural(f.refused, "request")}${fromAddresses(bound, f.refused)} turned away by our per-address limit${when ? ` (${when})` : ""}.`,
      detail: `${cap1(groups.map((g) => refusalGroupLabel(g)).join("; "))}. The server log's hourly lines name the addresses.`,
      since: since(p?.per_ip_refusals?.total),
    });
  }
  let blocked = 0, blockedSince = 0;
  const blockedBy = [];
  for (const [name, lim] of Object.entries(a.distributor_limits || {})) {
    const who = DISTRIBUTOR_LABEL[name] || name;
    const causes = pathsOf(lim?.held_back, lim?.ext_held_back);
    const pl = own(p?.distributor_limits, name);
    const pcauses = pathsOf(pl?.held_back, pl?.ext_held_back);
    const held = Object.entries(causes).filter(([c, n]) => n.all > 0 && c !== "address_blocked").sort((x, y) => y[1].all - x[1].all);
    // held_back_hours counts every cause, the block list's too: its hours are one notice's only when
    // that notice's cause is every hold
    const heldAll = Object.values(causes).reduce((x, n) => x + n.all, 0);
    const when = held.length === 1 && held[0][1].all === heldAll
      ? whenText(problemHours(view, (r) => own(r.distributor_limits, name)?.held_back_hours), !view.single) : "";
    const reset = resetHour(view.asOf, name === "mouser" ? mouserDayStartHour(payload?.health) : 0);
    for (const [cause, n] of held) {
      const bound = cause === "address_daily" ? addressBound(view.recs, "cap_reached") : null;
      items.push({
        key: `held_back:${name}:${cause}`, count: n.all, level: "warning",
        what: `${plural(n.all, `${who} lookup`)}${fromAddresses(bound, n.all)} turned away by our limits${when ? ` (${when})` : ""}.`,
        detail: `Why: ${heldBackLabel(cause, who, resetHour(view.asOf), reset)}.${n.ext ? ` ${n.api ? `${full(n.ext)} of them through ext.` : "All through ext."}` : ""}`,
        since: since(pcauses[cause]?.all),
      });
    }
    if (causes.address_blocked?.all > 0) {
      blocked += causes.address_blocked.all;
      blockedSince += pcauses.address_blocked?.all || 0;
      blockedBy.push(`${who} ${full(causes.address_blocked.all)}`);
    }
    const refusals = pathsOf(lim?.refusals, lim?.ext_refusals);
    const prefusals = pathsOf(pl?.refusals, pl?.ext_refusals);
    for (const [cause, n] of Object.entries(refusals)) {
      if (!(n.all > 0)) continue;
      items.push({ key: `refused:${name}:${cause}`, count: n.all, level: name === "mouser" && cause === "daily" ? "info" : "warning",
        what: refusalWhat(name, cause, n, limitSplit(view.recs, name, "refusals")), since: since(prefusals[cause]?.all) });
    }
  }
  if (blocked) {
    // the block list doing its job: information, never a warning
    const bound = addressesOf(addressBound(view.recs, "blocked_tried"), blocked);
    const who = bound === 1 ? "The blocked address" : bound > 1 ? `Blocked addresses (up to ${full(bound)})` : "Blocked addresses";
    items.push({ key: "held_back:address_blocked", count: blocked, level: "info",
      what: `${who} tried ${plural(blocked, "lookup")}, none sent${blockedBy.length > 1 ? ` (${blockedBy.join(", ")})` : ""}.`,
      detail: bound === 1 ? "The address is on the server's block list." : "Each address is on the server's block list.", since: since(blockedSince) });
  }
  // as in renderUpstreams: days without DigiKey's split (before server 0.10.11) hold both paths' requests
  const dkUnsplit = digikeyPaths(view.recs).unsplit > 0;
  for (const [src, st] of Object.entries(a.upstream_status || {})) {
    const tot = sumObj(st);
    // Mouser HTTP outcomes start in 0.10.9: limit replies count as 429 and have their own notices.
    const groups = errorGroups(st, { skipMouser429: true, src });
    const bad = groups.reduce((x, [, v]) => x + v, 0);
    const hard = HARD_ERRORS.reduce((x, k) => x + (own(st, k) || 0), 0);
    // error answers that cost no lookup are shown, muted, in the services table only
    const lost = lookupsFailed(a, src);
    if (lost === 0 || !((bad >= 3 && tot && bad / tot >= 0.02) || hard >= 5)) continue;
    // Mouser's transient retries, and DigiKey's API ones from server 0.10.11, are among the requests
    const retries = src === "mouser" || src === "digikey" ? own(a.distributors, src)?.retries : 0;
    const retryText = retries > 0 ? `; ${full(retries)} ${retries === 1 ? "was a retry" : "were retries"}` : "";
    const label = src === "digikey" && dkUnsplit ? DISTRIBUTOR_LABEL.digikey : upstreamLabel(src);
    const lostText = lost > 0 ? `; ${plural(lost, "lookup")} failed` : "";
    const pbad = errorGroups(own(p?.upstream_status, src), { skipMouser429: true, src }).reduce((x, [, v]) => x + v, 0);
    items.push({ key: `errors:${src}`, count: bad, level: "warning", what: `${label}: ${full(bad)} of ${full(tot)} requests got an error answer.`,
      detail: groups.map(([l, v]) => `${l} ${full(v)}`).join(", ") + lostText + retryText + ".", since: since(pbad) });
  }
  const dl = a.datasheet_links, pdl = p?.datasheet_links;
  if (dl?.refused) items.push({ key: "datasheet:refused", count: dl.refused, level: "warning", what: `${plural(dl.refused, "datasheet link")} turned away.`, detail: "Too many new links were asked for at once.", since: since(pdl?.refused) });
  if (dl?.failed) items.push({ key: "datasheet:failed", count: dl.failed, level: "warning", what: `${plural(dl.failed, "datasheet link")} failed.`, detail: "JLCPCB didn't answer.", since: since(pdl?.failed) });
  for (const [t, o] of Object.entries(a.lcsc_lookups || {})) {
    const po = own(p?.lcsc_lookups, t);
    if (o?.live_failed) items.push({ key: `lcsc:${t}:live_failed`, count: o.live_failed, level: "warning", what: `${plural(o.live_failed, "live stock lookup")} in ${t} failed with nothing to fall back on.`, since: since(po?.live_failed) });
    if (o?.fallback) items.push({ key: `lcsc:${t}:fallback`, count: o.fallback, level: "info", what: `${plural(o.fallback, "live stock lookup")} in ${t} answered from the daily snapshot instead.`, detail: "JLCPCB didn't answer: the reply was older data, not an error.", since: since(po?.fallback) });
  }
  if (a.db_waits?.longest_ms >= 10_000) {
    // its count: the hours with a wait that long, so a later one brings the notice back
    const longHours = view.recs.reduce((n, r) => n + (r.db_waits?.longest_ms_hours || []).filter((v) => v >= 10_000).length, 0);
    items.push({ key: "db_waits:long", count: longHours || 1, level: "warning", what: `A request waited ${ms(a.db_waits.longest_ms)} for the database.`, detail: `${full(a.db_waits.waited)} of ${full(a.db_waits.jobs)} database jobs had to wait.` });
  }
  // most serious first; within a level, the order above
  return items.map((it, i) => [it, i]).sort((x, y) => LEVELS[x[0].level] - LEVELS[y[0].level] || x[1] - y[1]).map(([it]) => it);
}

/**
 * Every count-based notice's count in one record (a day, or days added up), by key: the keys and
 * counts attentionItems gives its notices. recs: the days, for hourly lists the sum doesn't keep.
 */
function eventCounts(a, recs) {
  const out = new Map();
  const add = (key, n) => { if (n > 0) out.set(key, (out.get(key) || 0) + n); };
  for (const [t, v] of Object.entries(a.tools || {})) {
    if (!(v?.failed > 0)) continue;
    let rest = v.failed;
    const labels = Object.entries(own(a.reasons, t) || {}).filter(([c, n]) => n > 0 && isFailureReason(c)).sort((x, y) => y[1] - x[1]);
    for (const [c, n] of labels) {
      if (rest <= 0) break;
      add(`failed:${t}:${c}`, Math.min(n, rest));
      rest -= n;
    }
    add(`failed:${t}:unlabelled`, rest);
  }
  add("per_ip_refusals", a.per_ip_refusals?.total || 0);
  for (const [name, lim] of Object.entries(a.distributor_limits || {})) {
    for (const [c, n] of Object.entries(pathsOf(lim?.held_back, lim?.ext_held_back))) add(c === "address_blocked" ? "held_back:address_blocked" : `held_back:${name}:${c}`, n.all);
    for (const [c, n] of Object.entries(pathsOf(lim?.refusals, lim?.ext_refusals))) add(`refused:${name}:${c}`, n.all);
  }
  for (const [src, st] of Object.entries(a.upstream_status || {})) add(`errors:${src}`, errorGroups(st, { skipMouser429: true, src }).reduce((x, [, v]) => x + v, 0));
  add("datasheet:refused", a.datasheet_links?.refused || 0);
  add("datasheet:failed", a.datasheet_links?.failed || 0);
  for (const [t, o] of Object.entries(a.lcsc_lookups || {})) { add(`lcsc:${t}:live_failed`, o?.live_failed || 0); add(`lcsc:${t}:fallback`, o?.fallback || 0); }
  add("db_waits:long", (recs || []).reduce((n, r) => n + (r.db_waits?.longest_ms_hours || []).filter((v) => v >= 10_000).length, 0));
  return out;
}
const dayCountCache = new WeakMap();
function dayCounts(rec) {
  let counts = dayCountCache.get(rec);
  if (!counts) dayCountCache.set(rec, (counts = eventCounts(aggregate([rec]), [rec])));
  return counts;
}

/**
 * How many of a notice's events in the range came after it was dismissed: the rest of the day it was
 * dismissed on (its count then subtracted), and every later day in full.
 */
function newSinceDismissed(key, d, view) {
  let n = 0;
  for (const r of view.recs) {
    if (r.date < d.day) continue;
    const c = dayCounts(r).get(key) || 0;
    n += r.date === d.day ? Math.max(0, c - d.count) : c;
  }
  return n;
}

/** A dismissed notice stays hidden until something new happens after its dismissal, in the range shown. */
function isDismissed(it, view) {
  const d = it.key ? dismissed.get(it.key) : null;
  if (!d) return false;
  return d.day ? newSinceDismissed(it.key, d, view) === 0 : it.count <= d.count;
}

function noticeItem(it, { restoring = false } = {}) {
  const body = h("div", { class: "body" }, h("span", { class: "what", text: it.what }),
    it.detail ? " " : null, it.detail ? h("span", { class: "detail", text: it.detail }) : null,
    it.since ? h("span", { class: /^0 /.test(it.since) ? "since none" : "since", text: ` ${cap1(it.since.replace(/^0 /, "none "))}.` }) : null);
  const btn = it.key ? h("button", {
    id: noticeId(it.key), type: "button", class: "dismiss", text: restoring ? "Restore" : "Dismiss",
    title: restoring ? "Show this notice again" : "Hide this notice until its count grows",
    "aria-label": `${restoring ? "Restore" : "Dismiss"}: ${it.what}`,
    onclick: () => (restoring ? restore(it) : dismiss(it)),
  }) : null;
  return h("li", { "data-level": it.level }, h("span", { class: "dot", "aria-hidden": "true" }), body, btn);
}

function renderAttention(view) {
  const box = $("attention");
  if (!view) return;
  const sc = scope(view);
  const items = attentionItems(view, sc);
  const shown = items.filter((it) => !isDismissed(it, view)), hidden = items.filter((it) => isDismissed(it, view));
  const head = h("div", { class: "attention-head" }, h("h2", { id: "attention-head", tabindex: -1 }, "Worth a look"));
  if (hidden.length || state.showDismissed) {
    head.append(h("button", {
      id: "show-dismissed", type: "button", class: "quiet", "aria-pressed": state.showDismissed ? "true" : "false",
      text: state.showDismissed ? "Hide dismissed" : `Show dismissed (${hidden.length})`,
      // the button leaves once nothing is dismissed: the heading takes the focus then
      onclick: () => { state.showDismissed = !state.showDismissed; renderAttention(currentView); ($("show-dismissed") || $("attention-head"))?.focus({ preventScroll: true }); },
    }));
  }
  box.replaceChildren(head);
  if (!shown.some((it) => it.level !== "info")) {
    const f = figures(view.agg);
    const quiet = hidden.filter((it) => it.level !== "info").length;
    const text = quiet
      ? `Nothing new since ${quiet === 1 ? "the notice here was" : `the ${full(quiet)} notices here were`} dismissed.`
      : `Nothing: ${plural(f.calls, "call")}, none failed, none turned away by limits.${f.rejected ? ` ${plural(f.rejected, "call")} had arguments the tool rejected, listed under Reasons.` : ""}`;
    box.append(h("p", { class: "clear", text }));
  }
  if (shown.length) box.append(h("ul", {}, shown.map((it) => noticeItem(it))));
  if (state.undo) {
    box.append(h("p", { class: "undo" }, h("span", { text: `Dismissed: ${state.undo.what}` }), " ",
      h("button", { id: "undo-dismiss", type: "button", class: "quiet", text: "Undo", onclick: undoDismiss })));
  }
  if (state.showDismissed && hidden.length) box.append(h("ul", { class: "dismissed", "aria-label": "Dismissed notices" }, hidden.map((it) => noticeItem(it, { restoring: true }))));
  const note = items.some((it) => it.since) ? sinceNote(sc) : "";
  if (note || dismissError) box.append(h("p", { class: "foot" }, [note, dismissError].filter(Boolean).join(" ")));
}

// ---------------------------------------------------------------- headline numbers

function usage(a) {
  if (!a) return null;
  const T = totals(a);
  const answered = T.ok + T.similar_only + T.not_found;
  const lat = allLatency(a);
  return { T, calls: T.calls, answered, nf: T.not_found, sessions: a.apps ? sumObj(a.apps) : null, lat: sumArr(lat) > 0 ? lat : null };
}

/**
 * Each budget in the list, in order: shown only when there are several. in_use is the server's word
 * for the budget the pool uses next; a pause of the whole pool (q.paused_until) pauses each budget.
 */
function budgetList(pool, now, q) {
  if (!pool?.list || pool.list.length < 2) return null;
  const n = pool.list.length;
  return h("ol", { class: "budgets", "aria-label": "Daily budgets" }, pool.list.map((b, i) => {
    const used = typeof b.used_today === "number" ? b.used_today : 0;
    const pause = budgetPause(b, q, now);
    const spent = used >= b.limit;
    const status = [b.in_use ? "in use" : "", pause ? `paused until ${quotaTime(pause)}` : spent ? "spent" : ""].filter(Boolean).join(", ");
    return h("li", { "data-state": b.in_use ? "in-use" : pause ? "paused" : spent ? "spent" : "idle" },
      h("span", { class: "b-name", text: `budget ${i + 1} of ${n}` }),
      h("span", { class: "b-bar", "aria-hidden": "true" }, h("i", { style: { width: `${Math.min(100, (used / Math.max(1, b.limit)) * 100)}%` } })),
      h("span", { class: "b-num", text: `${full(used)} of ${full(b.limit)}` }),
      h("span", { class: "b-state", text: status }));
  }));
}

/** Today's Mouser budget: the one in use, then each budget in the list; otherwise the range's Mouser requests. */
function mouserTile(view, now) {
  const q = payload.health?.distributor_quota?.mouser;
  const start = mouserDayStartHour(payload?.health);
  const sample = healthSample(view, start);
  if (view.key === "today" && q?.limit && sample.currentDay) {
    const day = serverDay(sample.at || view.now, start);
    const pool = budgetPool(q);
    const which = pool?.list?.length > 1 && pool.inUse >= 0 ? ` (budget ${pool.inUse + 1} of ${pool.list.length})` : "";
    return {
      label: "Mouser daily budget", value: full(q.used_today ?? 0), small: `of ${full(q.limit)}`,
      note: `Key in use${which}. ${sample.retained ? "Retained value" : "Checked"} ${sample.label}; used since ${dayHourET(day.start)}; resets ${dayHourET(day.end)}`,
      more: [budgetList(pool, now, q)],
    };
  }
  const d = own(view.agg.distributors, "mouser") || {};
  return { label: "Requests sent to Mouser", value: compact(d.sent || 0), note: d.cached ? `and ${plural(d.cached, "lookup")} answered wholly from saved answers` : "" };
}

/** DigiKey now: which path answers, how much of the API's day is left; otherwise the range's lookups. */
function digikeyTile(view, now) {
  const q = payload.health?.distributor_quota?.digikey;
  const sample = healthSample(view, 0);
  const d = own(view.agg.distributors, "digikey") || {};
  const paths = digikeyPaths(view.recs);
  const lim = own(view.agg.distributor_limits, "digikey");
  const add = (x, n) => ({ all: x.all + n.all, api: x.api + n.api, ext: x.ext + n.ext });
  const held = Object.entries(pathsOf(lim?.held_back, lim?.ext_held_back)).filter(([c]) => c !== "address_blocked").reduce((x, [, n]) => add(x, n), { all: 0, api: 0, ext: 0 });
  const refused = Object.values(pathsOf(lim?.refusals, lim?.ext_refusals)).reduce(add, { all: 0, api: 0, ext: 0 });
  // the API/ext split of what our limits and DigiKey refused, wherever ext had any; the API's figure
  // only where every day with them counted ext's apart
  const splitOf = (n, field, what) => (!n.ext ? "" : limitSplit(view.recs, "digikey", field)
    ? `${what}: API ${full(n.api)}, ext ${full(n.ext)}` : `${what}: ${full(n.all)}, ${full(n.ext)} through ext`);
  const split = [splitOf(held, "held_back", "turned away"), splitOf(refused, "refusals", "refused")].filter(Boolean);
  const splitLine = split.length ? h("div", { class: "note", text: cap1(`${view.key === "today" ? "today" : "this range"}, ${split.join("; ")}`) }) : null;
  if (view.key !== "today" || !q || !sample.currentDay) {
    return { label: "Lookups sent to DigiKey", value: compact(d.sent || 0), note: paths.ext > 0 ? `API ${compact(paths.api)}, ext ${compact(paths.ext)}${paths.unsplit ? `, ${compact(paths.unsplit)} not split` : ""}` : "", more: [splitLine] };
  }
  const pool = budgetPool(q);
  const reset = resetHour(view.asOf);
  const apiPaused = pausedNow(q.paused_until, now);
  const ext = q.ext;
  const extKnown = typeof ext?.active === "boolean";
  const extOn = ext?.active === true && !pausedNow(ext.paused_until, now);
  const daySpent = pool ? pool.left === 0 : false;
  let value, note;
  if (!apiPaused) {
    value = "API answering";
    note = pool ? `${full(pool.left)} of the day's ${full(pool.limit)} requests left; resets ${reset}` : `resets ${reset}`;
  } else if (extOn) {
    const at = parseQuotaTime(ext.active_since);
    const known = at && Number.isFinite(at.getTime());
    value = "ext answering";
    note = `${known ? `Since ${momentText(at)}; ` : ""}${daySpent ? `API day spent, resets ${reset}` : `API paused until ${quotaTime(q.paused_until)}`}`;
  } else {
    value = extKnown ? "Paused" : "API paused";
    const extText = !extKnown ? "" : pausedNow(ext.paused_until, now) ? `; ext paused until ${quotaTime(ext.paused_until)}` : "; ext not in use";
    note = `Until ${quotaTime(q.paused_until)}${daySpent ? `, when the day resets` : ""}${extText}`;
  }
  return { label: "DigiKey now", value, nameValue: true, note: `${note}. ${sample.retained ? "Retained value" : "Checked"} ${sample.label}`, more: [budgetList(pool, now, q), splitLine] };
}

function renderKpis(view) {
  const sc = scope(view);
  const now = Date.now();
  const cur = usage(view.agg), prev = usage(view.prevAgg);
  const vs = compareShort(view);
  const trend = trendDays(view);
  const tm = trend.map((r) => (r ? usage(aggregate([r])) : null));
  const partialLast = view.key === "today";
  const bounds = view.bounds;

  const hero = $("hero");
  const sub = h("div", { class: "sub" });
  if (view.key === "today") {
    const y = view.byDate.get(view.yesterday);
    const yAt = view.prevAgg ? totals(view.prevAgg).calls : null;
    if (y && completeDay(y) && yAt) sub.append(`On pace for about ${compact(cur.calls * (totals(aggregate([y])).calls / yAt))} by midnight`);
  } else if (view.dates.length > 1) sub.append(`About ${compact(cur.calls / Math.max(1, view.recs.length))} a day`);
  hero.replaceChildren(
    h("div", { class: "label", text: view.key === "today" ? "Tool calls today" : "Tool calls" }),
    h("div", { class: "value", text: full(cur.calls) }),
    deltaEl(change(cur.calls, prev?.calls), vs) || "",
    sub,
    h("div", { class: "spark" }, sparkline(tm.map((m) => m?.calls ?? null), { width: 300, height: 44, partialLast })),
  );

  // the biggest app is the one making the most tool calls (sessions count connections, most with no call)
  const byApp = callsByApp(view.agg);
  const appCalls = Object.entries(byApp).filter(([n]) => !NOT_NAMED_APPS.has(n)).sort((x, y) => y[1].calls - x[1].calls);
  const allAppCalls = Object.values(byApp).reduce((x, o) => x + o.calls, 0);
  const appCov = countedFrom(view, AMOUNT.toolApps);
  const sessionsOf = (n) => own(view.agg.apps, n) || 0;
  let biggest;
  if (appCalls.length) {
    const [name, o] = appCalls[0];
    biggest = { label: "Biggest app", value: name, wrapValue: true,
      note: [`${percent(o.calls / allAppCalls)} of tool calls${appCov.text ? ` ${appCov.text}` : ""}`, sessionsOf(name) ? plural(sessionsOf(name), "session") : ""].filter(Boolean).join("; ") };
  } else {
    const apps = namedApps(view.agg.apps).sort((x, y) => y[1] - x[1]);
    biggest = { label: "Biggest app", value: apps[0] ? apps[0][0] : "–", wrapValue: true,
      note: apps[0] && cur.sessions ? `${percent(apps[0][1] / cur.sessions)} of sessions; no tool calls by app in this range` : "" };
  }
  const nfShare = (m) => (m && m.answered ? m.nf / m.answered : null);
  const topReason = (() => {
    const all = [];
    for (const [t, labels] of Object.entries(view.agg.reasons || {})) for (const [c, n] of Object.entries(labels || {})) if (!isFailureReason(c)) all.push([t, c, n]);
    all.sort((x, y) => y[2] - x[2]);
    return all[0];
  })();
  const f = figures(view.agg);
  const pf = sc.crosses ? figures(view.problems) : null;
  const latCov = countedFrom(view, AMOUNT.latency);
  const notes = (...parts) => parts.filter(Boolean).join("; ");
  const problemTile = (label, value, sinceValue, note) => ({ label, value: full(value ?? 0), note: notes(value ? note : "", sinceText(sc, sinceValue)) });
  const awayParts = [[f.refused, "request"], [f.held, "Mouser or DigiKey lookup"], [f.links, "datasheet link"]].filter(([n]) => n > 0).map(([n, w]) => plural(n, w)).join(", ");

  const tiles = [
    { label: "Sessions started", value: compact(cur.sessions), d: change(cur.sessions, prev?.sessions), note: "one each time an app connects", spark: (m) => m?.sessions },
    biggest,
    {
      label: "Found nothing", value: percent(nfShare(cur)), small: compact(cur.nf),
      d: prev && nfShare(prev) != null ? { text: `${percent(nfShare(prev))} ${comparedWith(view)}`, tone: "neutral", arrow: "" } : null,
      note: topReason ? `a normal answer; most often: ${midSentence(reasonLabel(topReason[1]))}` : "a normal answer, not an error",
      spark: (m) => nfShare(m),
    },
    {
      label: "95% answered within", value: cur.lat ? latencyText(cur.lat, bounds, 0.95).replace("≤", "") : "–",
      note: cur.lat ? notes(`half within ${latencyText(cur.lat, bounds, 0.5).replace("≤", "")}`, latCov.text && `measured ${latCov.text}`) : latCov.text ? `measured ${latCov.text}` : "not measured yet",
      spark: (m) => (m?.lat ? percentile(m.lat, bounds, 0.95) ?? bounds[bounds.length - 1] * 1.5 : null),
    },
    problemTile("Failed calls", f.failed, pf?.failed, "something broke here or in a service we call"),
    problemTile("Rejected arguments", f.rejected, pf?.rejected, "the AI called a tool wrongly"),
    problemTile("Turned away by limits", f.turnedAway, pf?.turnedAway, awayParts),
    mouserTile(view, now),
    digikeyTile(view, now),
  ];
  // the app's name and the distributor tiles take a whole row on a phone
  for (const t of [biggest, tiles[7], tiles[8]]) t.wide = true;
  $("tiles").replaceChildren(...tiles.map((t) => h("div", { class: t.wide ? "tile wide" : "tile" },
    h("div", { class: "label", text: t.label }),
    h("div", { class: `value${t.wrapValue || t.nameValue ? " name-value" : ""}` }, t.value, t.small ? h("small", { text: t.small }) : null),
    deltaEl(t.d, t.d?.tone === "neutral" ? null : vs),
    t.note ? h("div", { class: "note", text: t.note }) : null,
    ...(t.more || []).filter(Boolean),
    t.spark ? h("div", { class: "spark" }, sparkline(tm.map((m) => (m ? t.spark(m) ?? null : null)), { partialLast })) : h("div", { class: "spark" }),
  )));
}

// ---------------------------------------------------------------- U1 traffic

function hourTitle(ts, hours = 1) {
  const a = new Date(ts), b = new Date(ts + hours * HOUR);
  const za = tzAbbr(a), zb = tzAbbr(b);
  return `${weekdayDateET(a)}, ${timeET(a)}${za === zb ? "" : ` ${za}`} to ${timeET(b)} ${zb}`;
}
/** "11 AM to 12 PM", with the day in front ("Sat, Nov 14, 2 AM to 3 AM") when the range has several. */
function hourSpan(ts, withDay) {
  const a = new Date(ts), b = new Date(ts + HOUR);
  return `${withDay ? weekdayDateET(a) + ", " : ""}${hourET(a)} to ${hourET(b)}`;
}

/** Each server version's start the dashboard knows of: [{at: ms, version, exact}], oldest first. */
function deploys() {
  return (payload?.versions || []).map((r) => ({ at: Date.parse(r.from), version: r.version, exact: !!r.exact, after: r.after ? Date.parse(r.after) : null })).filter((d) => Number.isFinite(d.at));
}

function renderTraffic(view) {
  const sec = $("traffic");
  const sc = scope(view);
  // failed is red and turned away amber here, as their dots are in the Worth-a-look box
  const copper = css("--copper"), cmpColor = css("--silk-dim"), crit = css("--critical"), serious = css("--warning");
  // per point: {problems, byTool, rec} for the breakdown by tool (an hour's, or a whole day's)
  let points, calls, failed, refused, details, compare = null, markers = [], desc, peakText, peakDate = null;
  const known = deploys();

  if (view.dates.length <= 7) {
    const hrs = hourly(view, view.dates);
    points = hrs.map((p) => {
      const d = new Date(p.ts), et = partsET(d);
      const tick = view.single ? (et.h % 3 === 0 ? hourET(d) : null) : (et.h === 0 ? weekdayDateET(d).replace(/,.*$/, "") + " " + et.d : null);
      return { title: hourTitle(p.ts), tick, partial: p.current };
    });
    calls = hrs.map((p) => p.calls);
    failed = hrs.map((p) => p.failed);
    refused = hrs.map((p) => p.refused);
    details = hrs.map((p) => ({ problems: p.problems, byTool: p.byTool, rec: p.rec, hour: true }));
    if (view.single) {
      const prev = view.byDate.get(addDays(view.dates[0], -1));
      if (prev?.hours && (view.key === "today" || view.prevAgg)) compare = { label: view.key === "today" ? "Yesterday" : "The day before", color: cmpColor, values: hrs.map((_, i) => prev.hours[i] ?? null) };
    }
    for (const dep of known) {
      // a version seen only by the dashboard's checks started before the check that first saw it
      const between = !dep.exact && dep.after ? dep.after : null;
      const pos = dep.exact ? dep.at : between ?? dep.at - 60_000;
      const i = hrs.findIndex((p) => p.ts <= pos && pos < p.ts + HOUR);
      if (i < 0) continue;
      const at = dep.exact ? timeET(new Date(dep.at)) : between != null ? `${hourET(new Date(between))}–${timeET(new Date(dep.at))}` : `by ${timeET(new Date(dep.at))}`;
      markers.push({ index: i, label: `${dep.version}, ${at}` });
    }
    desc = `Tool calls per hour.${markers.length ? " A copper line marks each server version's start." : ""}`;
    const i = calls.reduce((best, v, k) => (v != null && v > (calls[best] ?? -1) ? k : best), 0);
    if (calls[i] != null) peakText = ["Busiest hour: ", h("strong", { text: hourSpan(hrs[i].ts, !view.single) }), `, ${full(calls[i])} calls`];
  } else {
    const rows = daily(view);
    points = rows.map((r) => ({ title: dayLabel(r.date, { weekday: true }), tick: dayLabel(r.date) }));
    calls = rows.map((r) => r.calls);
    failed = rows.map((r) => r.failed);
    refused = rows.map((r) => r.refused);
    // a whole day's breakdown is its own counters, exact
    details = rows.map((r) => ({ problems: r.rec ? dayProblems(r.rec) : null, byTool: !!r.rec, rec: r.rec, hour: false }));
    const marked = new Set();
    for (const dep of known) {
      const idx = view.dates.indexOf(partsET(new Date(dep.at)).key);
      if (idx >= 0) { markers.push({ index: idx, label: dep.version }); marked.add(dep.version); }
    }
    for (const [ver, date] of Object.entries(view.seen.versions)) {
      const idx = view.dates.indexOf(date);
      if (!marked.has(ver) && idx >= 0 && !view.byDate.get(date)?.approx) markers.push({ index: idx, label: ver });
    }
    markers = markers.sort((x, y) => x.index - y.index).slice(-8);
    desc = `Tool calls per day.${markers.length ? " A copper line marks the day a server version first ran." : ""}`;
    const i = calls.reduce((best, v, k) => (v != null && v > (calls[best] ?? -1) ? k : best), 0);
    if (calls[i] != null) { peakText = ["Busiest day: ", h("strong", { text: dayLabel(view.dates[i], { weekday: true }) }), `, ${full(calls[i])} calls`]; peakDate = view.dates[i]; }
  }
  // the record across the whole store, unless the range's own busiest day is that record
  let best = view.days.filter((d) => completeDay(d) && d.date < view.today).reduce((b, d) => ((d.calls || 0) > (b?.calls || 0) ? d : b), null);
  if (best && best.date === peakDate) best = null;

  sec.replaceChildren(cardHead(sec, "Traffic", desc, { table: true }));
  const subLine = h("div", { class: "chart-sub" });
  if (peakText) subLine.append(h("span", {}, ...peakText));
  if (best) subLine.append(h("span", {}, "Busiest full day on record: ", h("strong", { text: dayLabel(best.date, { weekday: true }) }), `, ${full(best.calls)} calls`));
  sec.append(subLine);
  if (compare) sec.append(legend([{ label: "Tool calls", color: copper }, { label: compare.label, color: compare.color, line: true }]));
  const c1 = h("div");
  sec.append(c1);
  columns(c1, {
    points, series: [{ label: "Tool calls", color: copper, values: calls }], compare, markers, height: 240,
    ariaLabel: "Tool calls over the range",
    extraRows: (i) => {
      const rows = [];
      if (failed[i]) rows.push({ color: crit, value: full(failed[i]), label: "failed" });
      if (refused[i]) rows.push({ color: serious, value: full(refused[i]), label: "turned away (per-address limit)" });
      if (points[i].partial) rows.push({ value: "", label: "hour in progress" });
      return rows;
    },
  });

  // the sentence gives the same totals as the tiles and the Worth-a-look box; the chart under it
  // shows the hours (or days) they fell in
  const f = figures(view.agg), pf = sc.crosses ? figures(view.problems) : null;
  const sinceBit = pf ? ` (${full(pf.failed)} and ${full(pf.refused)} ${sc.label})` : "";
  if (!f.failed && !f.refused) {
    sec.append(h("div", { class: "chart-sub" }, h("span", { text: "No failed calls and no requests turned away by the per-address limit in this range." })));
  } else {
    sec.append(h("div", { class: "chart-sub" }, h("span", {}, h("strong", { text: full(f.failed) }), " failed calls, ", h("strong", { text: full(f.refused) }), ` requests turned away by the per-address limit${sinceBit}`)));
    if (sumArr(failed) + sumArr(refused) > 0) {
      sec.append(legend([{ label: "Failed calls", color: crit }, { label: "Turned away by the per-address limit", color: serious }]));
      const c2 = h("div");
      sec.append(c2);
      columns(c2, {
        points, markers, height: 110, ariaLabel: "Failed calls and turned-away requests, with the tools that failed",
        series: [{ label: "Failed", color: crit, values: failed }, { label: "Turned away", color: serious, values: refused }],
        seriesRows: (i, label) => breakdownRows(details[i], label, { failed: failed[i], refused: refused[i] }),
        extraRows: (i) => rejectedRows(details[i], css("--serious")),
      });
    }
  }

  if (!view.single) sec.append(heatmap(view));

  const head = ["When", "Tool calls"];
  if (compare) head.push(compare.label);
  head.push("Failed", "Turned away", "Failed and rejected, by tool");
  sec.append(h("div", { class: "table-view" }, table(head, points.map((p, i) => h("tr", {},
    h("td", { text: p.title }), h("td", { text: full(calls[i]) }),
    compare ? h("td", { text: full(compare.values[i]) }) : null,
    h("td", { text: failed[i] == null ? "" : full(failed[i]) }), h("td", { text: refused[i] == null ? "" : full(refused[i]) }),
    h("td", { class: "byTool", text: byToolText(details[i]) }))))));
}

const BREAKDOWN_LINES = 3;
const toolName = (t) => (t === "unknown" ? "no such tool" : t);

/** A whole day's failures and rejected arguments by tool and reason, from its counters. */
function dayProblems(rec) {
  const out = {};
  for (const [t, v] of Object.entries(rec.tools || {})) {
    for (const [kind, outcome, labels, keep] of [["failed", "failed", rec.reasons, isFailureReason], ["rejected", "bad_request", rec.bad_request_reasons, () => true]]) {
      const n = v?.[outcome] || 0;
      if (!(n > 0)) continue;
      const by = {};
      for (const [c, k] of Object.entries(own(labels, t) || {})) if (k > 0 && keep(c)) by[c] = k;
      const rest = n - sumObj(by);
      if (rest > 0) by.unlabelled = rest;
      (out[kind] ??= {})[t] = by;
    }
  }
  return out.failed || out.rejected ? out : null;
}

/** "cse_search 7 · SamacSys search failed" lines, most first, the rest as "+N more". */
function breakdownLines(byTool, label) {
  const lines = [];
  for (const [t, labels] of Object.entries(byTool || {})) for (const [c, n] of Object.entries(labels || {})) if (n > 0) lines.push([t, c, n]);
  lines.sort((x, y) => y[2] - x[2]);
  const shown = lines.slice(0, BREAKDOWN_LINES).map(([t, c, n]) => ({ sub: true, value: "", label: `${toolName(t)} ${full(n)} · ${c === "unlabelled" ? "no reason recorded" : label(c)}` }));
  if (lines.length > BREAKDOWN_LINES) shown.push({ sub: true, value: "", label: `+${lines.length - BREAKDOWN_LINES} more` });
  return shown;
}

/** The note for a breakdown that covers more than its hour: a check was missed. */
function spanNote(d) {
  const p = d.problems;
  if (!d.hour || !p?.from || !p?.to) return [];
  const a = new Date(p.from), b = new Date(p.to);
  if (b - a <= 75 * 60_000) return [];
  return [{ sub: true, value: "", label: `by tool over ${hourET(a)} to ${hourET(b)}: a check was missed` }];
}

/** Under a series' tooltip row: which tools failed and why; how many addresses were turned away. */
function breakdownRows(d, label, counts) {
  if (!d) return [];
  if (label === "Failed") {
    if (!(counts.failed > 0)) return [];
    if (!d.byTool) return [{ sub: true, value: "", label: "no breakdown by tool for this day: rebuilt from daily totals" }];
    if (!d.problems?.failed) return [{ sub: true, value: "", label: "no breakdown by tool for this hour" }];
    return [...breakdownLines(d.problems.failed, reasonLabel), ...spanNote(d)];
  }
  if (label === "Turned away" && counts.refused > 0 && d.rec) {
    // turned away before any tool is known: only how many addresses, where the day counted them
    const bound = d.rec.starts_complete === false ? null : own(d.rec.addresses, "rate_limited");
    const text = fromAddresses(typeof bound === "number" ? bound : null, counts.refused);
    if (text) return [{ sub: true, value: "", label: text.trim() }];
  }
  return [];
}

/** Rejected arguments by tool, after the series, where the point has a breakdown. */
function rejectedRows(d, color) {
  const by = d?.problems?.rejected;
  if (!by) return [];
  const n = Object.values(by).reduce((x, labels) => x + sumObj(labels), 0);
  return [{ color, value: full(n), label: "Rejected arguments" }, ...breakdownLines(by, badRequestLabel),
    ...(d.problems.failed ? [] : spanNote(d))];
}

/** The same breakdown as one line of text, for the table view. */
function byToolText(d) {
  const p = d?.problems;
  if (!p) return "";
  const part = (byTool) => Object.entries(byTool || {}).map(([t, labels]) => `${toolName(t)} ${full(sumObj(labels))}`).join(", ");
  return [p.failed ? `failed: ${part(p.failed)}` : "", p.rejected ? `rejected: ${part(p.rejected)}` : ""].filter(Boolean).join("; ");
}

function heatmap(view) {
  const hrs = hourly(view, view.dates).filter((p) => !p.future);
  const rows = new Map();
  for (const p of hrs) {
    const d = new Date(p.ts), et = partsET(d);
    let r = rows.get(et.key);
    if (!r) rows.set(et.key, (r = { key: et.key, cells: new Array(24).fill(undefined), ts: new Array(24).fill(null), n: new Array(24).fill(0), total: 0 }));
    if (p.calls != null) { r.cells[et.h] = (r.cells[et.h] ?? 0) + p.calls; r.total += p.calls; }
    r.ts[et.h] ??= p.ts;
    r.n[et.h] += 1;
  }
  const list = [...rows.values()].sort((a, b) => (a.key < b.key ? 1 : -1)).slice(0, 35);
  const perHour = (r, i) => (typeof r.cells[i] === "number" ? r.cells[i] / Math.max(1, r.n[i]) : undefined);
  const max = Math.max(1, ...list.flatMap((r) => r.cells.map((_, i) => perHour(r, i)).filter((v) => typeof v === "number")));
  const color = (v) => (v ? HEAT_RAMP[Math.min(HEAT_RAMP.length - 1, Math.floor((v / max) * HEAT_RAMP.length))] : null);
  const grid = h("div", { class: "heat", role: "group", "aria-label": "Tool calls by day and hour" });
  const cellTip = (c, x, y) => {
    if (!c || !c.dataset.ts) return hideTip();
    const twice = +c.dataset.n > 1;
    const title = hourTitle(+c.dataset.ts, twice ? 2 : 1);
    const value = c.dataset.v === "" ? "no data" : full(+c.dataset.v);
    const label = twice ? "tool calls in two hours: clocks went back" : "tool calls";
    showTip(x, y, title, [{ value, label }]);
  };
  const cols = h("div", { class: "row cols" }, h("span"));
  for (let i = 0; i < 24; i++) cols.append(h("span", { text: i % 3 === 0 ? (i === 0 ? "12a" : i < 12 ? `${i}a` : i === 12 ? "12p" : `${i - 12}p`) : "" }));
  cols.append(h("span", { class: "rt muted", text: "Total" }));
  grid.append(cols);
  for (const r of list) {
    const row = h("div", { class: "row" }, h("span", { class: "rl", text: dayLabel(r.key, { weekday: true }).replace(",", "") }));
    r.cells.forEach((v, i) => {
      const c = h("span", { class: "cell", "data-v": v ?? "", "data-ts": r.ts[i] ?? "", "data-n": r.n[i] });
      if (r.ts[i] != null) {
        const twice = r.n[i] > 1;
        c.id = `heat-${r.ts[i]}`;
        c.tabIndex = 0;
        c.setAttribute("role", "img");
        c.setAttribute("aria-label", `${hourTitle(r.ts[i], twice ? 2 : 1)}: ${v == null ? "no data" : full(v)} tool calls${twice ? " in two hours: clocks went back" : ""}`);
        c.addEventListener("focus", () => { const rect = c.getBoundingClientRect(); cellTip(c, rect.left, rect.top); });
        c.addEventListener("blur", hideTip);
        c.addEventListener("keydown", (e) => { if (e.key === "Escape") hideTip(); });
      }
      if (v === undefined) c.dataset.empty = "true";
      else if (v) c.style.background = color(perHour(r, i));
      row.append(c);
    });
    row.append(h("span", { class: "rt", text: compact(r.total) }));
    grid.append(row);
  }
  grid.addEventListener("pointerover", (e) => {
    cellTip(e.target.closest(".cell"), e.clientX, e.clientY);
  });
  grid.addEventListener("pointerleave", hideTip);
  const scale = h("div", { class: "scale" }, "0", h("span", { class: "ramp" }, HEAT_RAMP.map((c) => h("i", { style: { background: c } }))), full(max), h("span", { text: " calls in an hour" }));
  return h("div", {}, h("div", { class: "chart-sub" }, h("span", {}, "Calls by day and hour", rows.size > 35 ? " (latest 35 days)" : "")), grid, scale);
}

// ---------------------------------------------------------------- U2 tools

const problemText = (o) => [
  o?.bad_request ? `${full(o.bad_request)} rejected` : "",
  o?.rate_limited ? `${full(o.rate_limited)} turned away` : "",
  o?.failed ? `${full(o.failed)} failed` : "",
].filter(Boolean).join(", ");

function renderTools(view) {
  const sec = $("tools");
  const a = view.agg;
  const prevTools = view.prevAgg?.tools;
  const bounds = view.bounds;
  const trend = trendDays(view);
  const names = new Set([...Object.keys(a.tools || {}), ...Object.keys(view.seen.tools)]);
  names.delete("unknown"); // calls to tools that don't exist: listed under rejected arguments
  const rows = [...names].map((t) => {
    const v = own(a.tools, t) || {};
    const answered = (v.ok || 0) + (v.similar_only || 0) + (v.not_found || 0);
    const lat0 = own(a.latency, t)?.counts;
    const lat = sumArr(lat0) > 0 ? lat0 : null;
    return {
      t, v, calls: v.calls || 0, answered, prev: prevTools ? own(prevTools, t)?.calls ?? 0 : null, lat,
      p95: percentile(lat, bounds, 0.95), probs: (v.bad_request || 0) + (v.rate_limited || 0) + (v.failed || 0),
    };
  });
  const { key, dir } = state.sort;
  const val = (r) => ({
    name: r.t, calls: r.calls, change: r.prev ? (r.calls - r.prev) / r.prev : -Infinity,
    nf: r.answered ? (r.v.not_found || 0) / r.answered : -1, p95: r.p95 === undefined ? -1 : r.p95 ?? Infinity, probs: r.probs,
  })[key];
  rows.sort((x, y) => {
    if (!x.calls !== !y.calls) return x.calls ? -1 : 1;
    const a1 = val(x), b1 = val(y);
    return (a1 < b1 ? -1 : a1 > b1 ? 1 : 0) * dir || y.calls - x.calls;
  });
  const maxCalls = Math.max(1, ...rows.map((r) => r.calls));
  const hasPrev = !!prevTools;
  const latCov = countedFrom(view, AMOUNT.latency);
  const hasLat = latCov.has;
  // no column of blanks: problems show only where some tool has one
  const hasProbs = rows.some((r) => r.probs);
  const cols = [
    { key: "name", label: "Tool" },
    { key: "calls", label: "Calls" },
    hasPrev && { key: "change", label: "Change", cls: "opt-sm" },
    { key: "nf", label: "Found nothing" },
    hasLat && { key: "p95", label: "95% answered within", cls: "opt-md" },
    hasProbs && { key: "probs", label: "Problems" },
    { key: null, label: "14 days", cls: "opt-md" },
  ].filter(Boolean);
  const dead = rows.filter((r) => !r.calls);

  sec.replaceChildren(cardHead(sec, "Tools",
    `How each tool was used. Found nothing is a normal answer, shown as a share of the calls the tool answered.${hasProbs ? " Problems are rejected arguments, calls turned away by limits and failures." : ""} Click a tool for details.`));
  if (dead.length) sec.append(h("div", { class: "chart-sub" }, h("span", { text: `Not called in this range: ${dead.map((r) => r.t).join(", ")}` })));

  const head = cols.map((c) => {
    if (!c.key) return h("th", { text: c.label });
    const sorted = state.sort.key === c.key;
    return h("th", {
      id: `sort-${c.key}`,
      class: "sortable", "aria-sort": sorted ? (state.sort.dir < 0 ? "descending" : "ascending") : null, tabindex: 0, text: c.label,
      onclick: () => sortBy(c.key), onkeydown: (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), sortBy(c.key)),
    });
  });
  const body = [];
  for (const r of rows.filter((x) => x.calls)) {
    const open = state.open.has(r.t);
    const v = r.v;
    const cells = {
      name: h("td", { class: "name", text: r.t, title: r.t }),
      calls: h("td", {}, h("div", { class: "barcell" }, h("div", { class: "bartrack" }, h("i", { class: "bar", style: { width: `${(r.calls / maxCalls) * 100}%` } })), h("span", { class: "bn", text: full(r.calls) }))),
      change: h("td", {}, deltaEl(change(r.calls, r.prev)) || ""),
      nf: numCell(v.not_found, r.answered),
      p95: h("td", { text: r.lat ? latencyText(r.lat, bounds, 0.95).replace("≤", "") : "" }),
      probs: h("td", { class: v.failed ? "hot" : null, text: problemText(v) }),
      "14 days": h("td", { style: { width: "96px" } }, sparkline(trend.map((d) => own(d?.tools, r.t)?.calls ?? (d ? 0 : null)), { width: 90, height: 22, partialLast: view.key === "today" })),
    };
    body.push(h("tr", {
      id: `tool-${r.t}`,
      class: `tool-row${r.calls < 30 ? " small-n" : ""}`, tabindex: 0, "aria-expanded": open ? "true" : "false",
      onclick: (e) => toggleTool(r.t, e.currentTarget), onkeydown: (e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), toggleTool(r.t, e.currentTarget)),
    }, ...cols.map((c) => cells[c.key ?? c.label])));
    if (open) body.push(detailRow(view, r.t, cols.length));
  }
  sec.append(table(head, body, { cls: cols.map((c) => c.cls) }));
  sec.querySelectorAll(".detail-inner").forEach(fitDetail);
  // each note leaves with its column on a narrow screen
  const notes = h("div", { class: "chart-sub notes" });
  const unsorted = totals(a).unsorted;
  if (unsorted) notes.append(h("span", { text: `${full(unsorted)} unsorted: error replies from before 0.6.4.` }));
  if (hasPrev) notes.append(h("span", { class: "opt-sm", text: `Change is ${compareShort(view)}.` }));
  if (hasLat && latCov.text) notes.append(h("span", { class: "opt-md", text: `Response times are measured ${latCov.text}.` }));
  if (!hasProbs) notes.append(h("span", { text: "No tool had a problem in this range." }));
  // calls to a tool name that doesn't exist belong to no row; say so, so the column adds up to the tile
  const noTool = own(a.tools, "unknown")?.bad_request || 0;
  if (noTool) notes.append(h("span", { text: `${plural(noTool, "more rejected call")} named a tool that doesn't exist (under Reasons).` }));
  if (notes.children.length) sec.append(notes);
}

function sortBy(key) {
  state.sort = state.sort.key === key ? { key, dir: -state.sort.dir } : { key, dir: key === "name" ? 1 : -1 };
  renderTools(currentView);
  document.querySelector("#tools th[aria-sort]")?.focus({ preventScroll: true });
}

/** Open or close one tool's detail row in place, so nothing else on the page moves. */
function toggleTool(t, tr) {
  const open = !state.open.has(t);
  open ? state.open.add(t) : state.open.delete(t);
  tr.setAttribute("aria-expanded", open ? "true" : "false");
  const next = tr.nextElementSibling;
  if (next?.classList.contains("detail-row")) next.remove();
  if (open) {
    const row = detailRow(currentView, t, tr.children.length);
    tr.after(row);
    fitDetail(row.querySelector(".detail-inner"));
  }
}
function detailRow(view, t, span) {
  return h("tr", { class: "detail-row" }, h("td", { colspan: span }, h("div", { class: "detail-inner" }, toolDetail(view, t))));
}
function fitDetail(inner) {
  const wrap = inner?.closest(".table-wrap");
  // the wrap's own 4px side padding and the cell's 14px: any wider and the open row makes the table scroll
  if (wrap) inner.style.width = `${wrap.clientWidth - 8 - 28}px`;
}

function toolDetail(view, t) {
  const a = view.agg, v = own(a.tools, t) || {};
  const wrap = h("div", { class: "split" });
  const answered = (v.ok || 0) + (v.similar_only || 0) + (v.not_found || 0);

  // answers over the range
  const ans = h("div", {}, h("h3", {}, "Answers", h("small", { text: "this range" })));
  if (!view.single) {
    const recs = view.dates.map((d) => own(view.byDate.get(d)?.tools, t) || null);
    const series = [
      { label: "Found", color: css("--o-ok"), values: recs.map((r) => (r ? (r.ok || 0) + (r.similar_only || 0) : null)) },
      { label: "Found nothing", color: css("--o-not_found"), values: recs.map((r) => (r ? r.not_found || 0 : null)) },
    ];
    const c = h("div");
    ans.append(legend(series.map((s1) => ({ label: s1.label, color: s1.color }))), c);
    requestAnimationFrame(() => columns(c, { points: view.dates.map((d) => ({ title: dayLabel(d, { weekday: true }), tick: dayLabel(d) })), height: 140, series, ariaLabel: `${t} answers per day` }));
  }
  ans.append(kv([
    ["Found something", v.ok ? `${full(v.ok)} (${percent(v.ok / answered)})` : "0"],
    v.similar_only ? ["Only similar parts", `${full(v.similar_only)} (${percent(v.similar_only / answered)})`] : [null],
    ["Found nothing", v.not_found ? `${full(v.not_found)} (${percent(v.not_found / answered)})` : "0"],
    v.unsorted ? ["Unsorted (error replies from before 0.6.4)", full(v.unsorted)] : [null],
    ["Average time", a.avg_ms?.[t] == null ? "–" : ms(Math.round(a.avg_ms[t]))],
  ]));
  wrap.append(ans);

  const nf = merge(Object.entries(own(a.reasons, t) || {}).filter(([c]) => !isFailureReason(c)).map(([c, n]) => ({ name: reasonLabel(c), value: n })));
  const reasonCov = countedFrom(view, AMOUNT.reasons);
  // shares are of the answers that carry a reason: reasons began later than the oldest days
  wrap.append(h("div", {}, h("h3", {}, "Why it found nothing", h("small", { text: reasonCov.text ? `reasons kept ${reasonCov.text}` : "this range" })),
    ranked(nf, { total: nf.reduce((x, r) => x + r.value, 0), color: css("--o-not_found"), empty: v.not_found ? "No reasons recorded for these days." : "It always found something." })));

  const counts = own(a.latency, t)?.counts;
  const latCov = countedFrom(view, AMOUNT.latency), appCov = countedFrom(view, AMOUNT.toolApps);

  const probBox = h("div", {}, h("h3", {}, "Problems", h("small", { text: "this range" })));
  const bad = Object.entries(own(a.bad_request_reasons, t) || {}).map(([c, n]) => ({ name: badRequestLabel(c), value: n }));
  const failed = Object.entries(own(a.reasons, t) || {}).filter(([c]) => isFailureReason(c)).map(([c, n]) => ({ name: reasonLabel(c), value: n }));
  if (!bad.length && !failed.length && !v.rate_limited && !v.failed && !v.bad_request) probBox.append(h("div", { class: "empty", text: "None." }));
  if (bad.length) probBox.append(h("div", { class: "subhead", text: "Rejected arguments" }), ranked(merge(bad), { color: css("--serious") }));
  else if (v.bad_request) probBox.append(h("div", { class: "subhead", text: `Rejected arguments: ${full(v.bad_request)}` }));
  if (v.rate_limited) probBox.append(h("div", { class: "subhead", text: `Turned away by limits: ${full(v.rate_limited)}` }));
  if (failed.length) probBox.append(h("div", { class: "subhead", text: "Failures" }), ranked(merge(failed), { color: css("--critical") }));
  else if (v.failed) probBox.append(h("div", { class: "subhead", text: `Failures: ${full(v.failed)}` }));
  wrap.append(probBox);

  const latBox = h("div", {}, h("h3", {}, "Response time", h("small", { text: latCov.text ? `measured ${latCov.text}` : "this range" })));
  if (counts && sumArr(counts)) {
    const b = view.bounds;
    const labels = [...b.map((x) => "≤" + ms(x)), ">" + ms(b[b.length - 1])];
    const interval = (i) => {
      if (i === b.length) return `over ${ms(b[b.length - 1])}`;
      const lower = i ? b[i - 1] : 0;
      // Share units for 50–100 ms and 1–2.5 s; keep both across 500 ms–1 s.
      const lo = (lower >= 1000) === (b[i] >= 1000) ? ms(lower).replace(/ (ms|s)$/, "") : ms(lower);
      return `${lo}–${ms(b[i])}`;
    };
    const c = h("div");
    const pct = (q) => latencyText(counts, b, q).replace("≤", "");
    latBox.append(h("div", { class: "chart-sub" }, h("span", { text: `Half within ${pct(0.5)}, 95% within ${pct(0.95)}, 99% within ${pct(0.99)}.` })), c);
    requestAnimationFrame(() => columns(c, {
      points: labels.map((l, i) => ({ title: interval(i), tick: l.replace("≤", "").replace(" ms", "ms").replace(" s", "s") })), height: 130,
      series: [{ label: "calls", color: css("--copper"), values: counts }], ariaLabel: `${t} response times`,
    }));
  } else latBox.append(h("div", { class: "empty", text: latCov.has || !latCov.text ? "No timed calls in this range." : "This range ends before that." }));
  wrap.append(latBox);

  const apps = Object.entries(own(a.tool_apps, t) || {}).filter(([, o]) => o?.calls > 0).sort((x, y) => y[1].calls - x[1].calls).slice(0, 10);
  const appBox = h("div", {}, h("h3", {}, "Apps calling it", h("small", { text: appCov.text ? `counted ${appCov.text}` : "this range" })));
  if (apps.length) appBox.append(table(["App", "Calls", "Found nothing"], apps.map(([app, o]) => h("tr", {},
    h("td", { class: "name", text: appName(app), title: app }), h("td", { text: full(o.calls) }), numCell(o.not_found, o.calls)))));
  else appBox.append(h("div", { class: "empty", text: appCov.has || !appCov.text ? "No calls by app recorded for this range." : "This range ends before that." }));
  wrap.append(appBox);
  return wrap;
}

/** Labels that read the same (two codes, one wording) are one row. */
function merge(rows) {
  const m = new Map();
  for (const r of rows) m.set(r.name, (m.get(r.name) || 0) + r.value);
  return [...m].map(([name, value]) => ({ name, value }));
}

const appName = (n) => (n === "unknown" ? "App not identified" : n === "other" ? "Other apps" : n);

// ---------------------------------------------------------------- U3 apps

function renderClients(view) {
  const sec = $("clients");
  const a = view.agg, prev = view.prevAgg;
  const sessions = a.apps || {};
  const byApp = callsByApp(a);
  const totalSessions = sumObj(sessions);
  const names = new Set([...Object.keys(sessions), ...Object.keys(byApp)]);
  const rows = [...names].map((n) => ({
    n, s: own(sessions, n) || 0, prev: prev ? own(prev.apps, n) ?? 0 : null,
    calls: own(byApp, n)?.calls ?? null, pr: own(byApp, n), first: view.seen.apps[n],
  })).filter((r) => r.s > 0 || r.calls > 0);
  const appCov = countedFrom(view, AMOUNT.toolApps);
  // apps that connected but called no tool are one row, where tool calls by app cover the whole range
  const foldIdle = appCov.has && !appCov.text;
  const named = rows.filter((r) => !NOT_NAMED_APPS.has(r.n)).sort((x, y) => y.s - x.s || (y.calls || 0) - (x.calls || 0));
  const idle = foldIdle ? named.filter((r) => !(r.calls > 0)) : [];
  const busy = foldIdle ? named.filter((r) => r.calls > 0) : named;
  const special = rows.filter((r) => NOT_NAMED_APPS.has(r.n));
  const LIMIT = 12;
  const shown = busy.slice(0, LIMIT), rest = busy.slice(LIMIT);
  const maxS = Math.max(1, ...shown.map((r) => r.s), idle.reduce((x, r) => x + r.s, 0));
  const storeStart = view.days.find((d) => !d.partial_start)?.date;

  // columns with nothing in them for this range stay out
  const hasCalls = rows.some((r) => r.calls > 0);
  const hasProbs = rows.some((r) => problemText(r.pr));
  const hasPrev = !!prev;
  const firstSeen = (r) => {
    if (!r.first || NOT_NAMED_APPS.has(r.n)) return h("td");
    if (r.first === storeStart) return h("td", { class: "zero", text: `${dayLabel(r.first)} or earlier` });
    // a day rebuilt from the server's 7 PM-to-7 PM totals can be one day off
    return h("td", { text: `${view.byDate.get(r.first)?.approx ? "about " : ""}${dayLabel(r.first)}` });
  };

  sec.replaceChildren(cardHead(sec, "Apps",
    "Which apps connect, by the name they send. A session starts each time an app connects.", { table: !view.single }));

  const row = (r, label, cls) => h("tr", { class: cls || null },
    h("td", { class: "name", title: r.n || label, text: label || appName(r.n) }),
    h("td", {}, h("div", { class: "barcell" }, h("div", { class: "bartrack" }, r.s ? h("i", { class: "bar", style: { width: `${(r.s / maxS) * 100}%` } }) : null), h("span", { class: "bn", text: r.s ? full(r.s) : "" }))),
    h("td", { text: totalSessions && r.s ? percent(r.s / totalSessions) : "" }),
    hasPrev ? h("td", {}, deltaEl(change(r.s, r.prev)) || "") : null,
    hasCalls ? h("td", { text: r.calls ? full(r.calls) : r.idle ? "0" : "" }) : null,
    hasProbs ? h("td", { text: problemText(r.pr) }) : null,
    r.idle ? h("td") : firstSeen(r));
  const body = shown.map((r) => row(r));
  if (rest.length) body.push(row({ n: "", s: rest.reduce((x, r) => x + r.s, 0), prev: null, calls: rest.reduce((x, r) => x + (r.calls || 0), 0) || null }, `${rest.length} more apps`));
  if (idle.length) body.push(row({ n: "", s: idle.reduce((x, r) => x + r.s, 0), prev: null, calls: null, idle: true }, `${plural(idle.length, "app")} that called no tool`, "muted"));
  for (const r of special) body.push(row(r, r.n === "other" ? "Other apps (names not kept)" : "App not identified"));
  const cols = [
    ["App", null], ["Sessions", null], ["Share of sessions", "opt-sm"], hasPrev && ["Change", "opt-sm"],
    hasCalls && [`Tool calls${appCov.text ? ` ${appCov.text}` : ""}`, null],
    hasProbs && ["Problems", "opt-md"], ["First seen", "opt-md"],
  ].filter(Boolean);
  sec.append(table(cols.map((c) => c[0]), body, { cls: cols.map((c) => c[1]) }));
  const notes = h("div", { class: "chart-sub notes" });
  if (hasPrev) notes.append(h("span", { class: "opt-sm", text: `Change is in sessions, ${compareShort(view)}.` }));
  if (idle.length) notes.append(h("span", { title: idle.map((r) => r.n).join(", "), text: `Apps that called no tool: ${idle.slice(0, 8).map((r) => r.n).join(", ")}${idle.length > 8 ? ` and ${idle.length - 8} more` : ""}.` }));
  if (special.some((r) => r.n === "unknown")) notes.append(h("span", { text: "App not identified: tool calls from an address with no recent connection to name it." }));
  if (notes.children.length) sec.append(notes);

  if (!view.single) {
    const top = named.slice(0, 5).map((r) => r.n);
    const colors = [css("--s1"), css("--s2"), css("--s3"), css("--s4"), css("--s5")];
    const recs = view.dates.map((d) => view.byDate.get(d) || null);
    const conn = (r, n) => { const v = own(r.apps, n); return typeof v === "number" ? v : 0; };
    const series = top.map((n, i) => ({ label: n, color: colors[i], values: recs.map((r) => (r ? conn(r, n) : null)) }));
    series.push({ label: "Everything else", color: css("--s-other"), values: recs.map((r) => (r ? sumObj(r.apps) - top.reduce((x, n) => x + conn(r, n), 0) : null)) });
    const right = h("div", { style: { marginTop: "22px" } }, h("h3", {}, "Sessions a day", h("small", { text: "five busiest apps" })), legend(series.map((s1) => ({ label: s1.label, color: s1.color, line: true }))));
    const c = h("div");
    right.append(c);
    sec.append(right);
    requestAnimationFrame(() => lines(c, { points: view.dates.map((d) => ({ title: dayLabel(d, { weekday: true }), tick: dayLabel(d) })), series, height: 220, ariaLabel: "Sessions a day by app" }));
    sec.append(h("div", { class: "table-view" }, table(["Day", ...series.map((s1) => s1.label)],
      view.dates.map((d, i) => h("tr", {}, h("td", { text: dayLabel(d, { weekday: true }) }), series.map((s1) => h("td", { text: full(s1.values[i]) })))))));
  }
}

// ---------------------------------------------------------------- U4 reasons

function renderErrors(view) {
  const sec = $("errors");
  const a = view.agg;
  // "unknown" is the server's bucket for calls to a tool name that doesn't exist
  const flat = (o, keep, label) => Object.entries(o || {}).flatMap(([tool, labels]) =>
    Object.entries(labels || {}).filter(([c]) => keep(c)).map(([c, n]) => ({ sub: tool === "unknown" ? "no such tool" : tool, name: label(c), value: n })));
  sec.replaceChildren(cardHead(sec, "Reasons", "Why calls were rejected, found nothing or failed, by tool."));
  const split = h("div", { class: "split" });

  split.append(h("div", {}, h("h3", {}, "Rejected arguments", h("small", { text: "this range" })),
    h("p", { class: "lead", text: "The AI called a tool wrongly. A reason that keeps growing means that tool's description needs work." }),
    ranked(mergeSub(flat(a.bad_request_reasons, () => true, badRequestLabel)), { color: css("--serious"), empty: totals(a).bad_request ? "No reasons were recorded for these." : "None." })));

  const nfRows = mergeSub(flat(a.reasons, (c) => !isFailureReason(c), reasonLabel));
  const nfTotal = totals(a).not_found;
  const reasonCov = countedFrom(view, AMOUNT.reasons);
  // shares are of the answers that carry a reason: reasons began later than the oldest days
  split.append(h("div", {}, h("h3", {}, "Why searches and lookups found nothing", h("small", { text: reasonCov.text ? `reasons kept ${reasonCov.text}` : "this range" })),
    h("p", { class: "lead", text: "A normal answer: the part or result doesn't exist where it was looked for." }),
    ranked(nfRows, { total: nfRows.reduce((x, r) => x + r.value, 0), color: css("--o-not_found"), limit: 10, empty: nfTotal ? "No reasons recorded for these days." : "None." })));

  split.append(h("div", {}, h("h3", {}, "Failures", h("small", { text: "this range" })),
    h("p", { class: "lead", text: "Something broke here or in a service we call." }),
    ranked(mergeSub(flat(a.reasons, isFailureReason, reasonLabel)), { color: css("--critical"), empty: totals(a).failed ? "No reasons were recorded for these." : "None." })));
  sec.append(split);
}

function mergeSub(rows) {
  const m = new Map();
  for (const r of rows) {
    const k = r.sub + "\u0000" + r.name;
    const cur = m.get(k);
    if (cur) cur.value += r.value; else m.set(k, { ...r });
  }
  return [...m.values()];
}

// ---------------------------------------------------------------- U5 services we call

function renderUpstreams(view) {
  const sec = $("upstreams");
  const a = view.agg;
  sec.replaceChildren(cardHead(sec, "Services we call", "Requests the server sent to JLCPCB, LCSC, EasyEDA, SamacSys, Mouser and DigiKey, and how they answered."));

  const allSources = [...new Set([...Object.keys(a.upstream || {}), ...Object.keys(a.upstream_status || {})])];
  // DigiKey's API and ext requests are counted apart from server 0.10.11; older days have one DigiKey figure
  const dk = digikeyPaths(view.recs);
  const label = (src) => (src === "digikey" && dk.unsplit ? DISTRIBUTOR_LABEL.digikey : upstreamLabel(src));
  const info = allSources.map((src) => {
    const u = upstreamCounts(a, src), st = own(a.upstream_status, src) || null;
    const tot = st ? sumObj(st) : 0;
    const errs = st ? errorGroups(st) : [];
    // our own resends: the HTTP client's (upstream retries) and, for Mouser and DigiKey's API, the lookup's
    const resent = (u.retries || 0) + (src === "mouser" || src === "digikey" ? own(a.distributors, src)?.retries || 0 : 0);
    return { src, u, tot, errs, resent, nErr: errs.reduce((x, [, v]) => x + v, 0), lost: lookupsFailed(a, src), held: u.rate_limited || 0, served: (u.sent || 0) + (u.cached || 0) };
  }).filter((r) => r.src !== "digikey_ext" || sumObj(r.u) + r.tot + r.held > 0); // ext only has a row when it was used
  const sources = info.map((r) => r.src);
  // columns with nothing in them for this range stay out; a sentence under the table says so instead
  const hasHeld = info.some((r) => r.held), hasErr = info.some((r) => r.nErr), hasResent = info.some((r) => r.resent);
  const errCell = (r) => {
    if (!r.nErr) return h("td");
    const kinds = r.errs.map(([l, v]) => (r.errs.length > 1 ? `${l} ${full(v)}` : l)).join(", ");
    // error answers that cost no lookup (resent, or answered another way) are quiet
    if (r.lost === 0) return h("td", { class: "zero", text: `${full(r.nErr)} of ${full(r.tot)}: ${kinds}; no lookup failed` });
    return h("td", { class: "hot", text: `${full(r.nErr)} of ${full(r.tot)}: ${kinds}${r.lost ? `; ${plural(r.lost, "lookup")} failed` : ""}` });
  };
  const rows = info.map((r) => h("tr", {},
    h("td", { class: "name", text: label(r.src), title: r.src }),
    h("td", { text: full(r.u.sent) }),
    hasResent ? h("td", { text: r.resent ? full(r.resent) : "" }) : null,
    h("td", {}, r.u.cached ? full(r.u.cached) : "", r.u.cached && r.served ? h("span", { class: "pct", text: percent(r.u.cached / r.served) }) : null),
    hasHeld ? h("td", { text: r.held ? full(r.held) : "" }) : null,
    hasErr ? errCell(r) : null));
  const cols = [
    ["Service", null], ["Requests sent", null], hasResent && ["Resent", "opt-sm"], ["Answered from saved answers", "opt-sm"],
    hasHeld && ["Turned away by our limits", "opt-sm"], hasErr && ["Error answers", null],
  ].filter(Boolean);
  if (rows.length) sec.append(table(cols.map((c) => c[0]), rows, { cls: cols.map((c) => c[1]) }));
  else sec.append(h("div", { class: "empty", text: "Requests to these services weren't counted yet in this range." }));

  const notes = h("div", { class: "chart-sub notes" });
  const cov = countedFrom(view, AMOUNT.upstream);
  if (rows.length) {
    // A service whose own counting began later is named with its date. Ext is used only at times,
    // so its first request says nothing about when counting began: the note below covers it.
    const later = sources.filter((src) => src !== "digikey_ext").map((src) => [src, countedFrom(view, AMOUNT.upstreamOf(src))]).filter(([, c]) => c.start && c.start > cov.start && c.text);
    if (cov.text || later.length) notes.append(h("span", { text: `Requests are counted ${cov.text || "throughout this range"}${later.map(([src, c]) => `; ${label(src)} ${c.text}`).join("")}.` }));
    // dated from the ext row's own first day, so the note never contradicts the rows' numbers
    const apartFrom = dk.unsplit && sources.includes("digikey") && sources.includes("digikey_ext")
      ? countedFrom(view, AMOUNT.upstreamOf("digikey_ext")) : null;
    // no start: the ext row has only requests held back or outcomes, so no day to date it from
    const apart = apartFrom?.text || (apartFrom?.start ? `from ${dayLabel(apartFrom.start)}` : "");
    if (apart) notes.append(h("span", { text: `DigiKey's API and ext requests are counted apart ${apart}.` }));
    if (hasResent) notes.append(h("span", { class: "opt-sm", text: "Resent: further tries after a timeout, dropped connection, server error or redirect; included in requests sent." }));
    if (info.some((r) => r.nErr && r.lost === 0)) notes.append(h("span", { text: "Error answers in grey cost no lookup: a resend or another path answered." }));
    const none = [!hasErr && "no error answers", !hasHeld && "nothing turned away by our own limits"].filter(Boolean);
    if (none.length) notes.append(h("span", { text: `${cap1(none.join(" and "))} in this range.` }));
  }
  if (notes.children.length) sec.append(notes);

  const split = h("div", { class: "split", style: { marginTop: "22px" } });
  const reset = resetHour(view.asOf);
  for (const name of ["mouser", "digikey"]) {
    const d = own(a.distributors, name);
    if (!d) continue;
    const who = DISTRIBUTOR_LABEL[name];
    const budgetReset = resetHour(view.asOf, name === "mouser" ? mouserDayStartHour(payload?.health) : 0);
    const lim = own(a.distributor_limits, name);
    const held = Object.entries(pathsOf(lim?.held_back, lim?.ext_held_back)).filter(([, n]) => n.all > 0);
    const refused = Object.entries(pathsOf(lim?.refusals, lim?.ext_refusals)).filter(([, n]) => n.all > 0);
    const asked = own(a.parts_asked, name)?.total;
    const extBit = (n) => (n.ext ? (n.api ? `, ${full(n.ext)} through ext` : ", all through ext") : "");
    const box = h("div", {}, h("h3", {}, `${who} lookups`, h("small", { text: "this range" })));
    const turnedAway = [`Turned away by our limits`, held.length ? held.map(([c, n]) => `${full(n.all)}: ${heldBackLabel(c, who, reset, budgetReset)}${extBit(n)}`) : "0"];
    const refusedUs = refused.length ? [`${who} refused us`, refused.map(([c, n]) => `${full(n.all)}: ${refusedLabel(c, name)}${extBit(n)}`)] : [null];
    if (name === "mouser") {
      // a request goes out per lookup that the saved answers couldn't settle, and again for a resend or a
      // second batch: so the lookups answered wholly from saved answers were at least this share of all
      const settled = (d.sent || 0) - (d.retries || 0) + (d.rate_limited || 0);
      const share = d.cached && d.cached + settled > 0 ? d.cached / (d.cached + settled) : null;
      box.append(kv([
        ["Requests sent to Mouser", full(d.sent)],
        typeof asked === "number" ? ["Part numbers asked", full(asked)] : [null],
        ["Lookups answered wholly from saved answers", `${full(d.cached)}${share != null ? ` (at least ${percent(share)} of lookups)` : ""}`],
        ["Not real part numbers, so not sent", d.skipped ? full(d.skipped) : null],
        turnedAway, refusedUs,
      ], { cls: "dist" }));
      if (view.key === "today") box.append(mouserQuota(view));
    } else {
      // DigiKey's lookups by path, from the days that split them (server 0.10.11); none shown without ext lookups
      const paths = digikeyPaths(view.recs);
      const viaExt = paths.ext > 0;
      const pathsFrom = viaExt ? countedFrom(view, AMOUNT.digikeyPaths).text : "";
      const pathNote = pathsFrom ? ` (${pathsFrom})` : "";
      // requests per lookup only where both were counted over the same days, paired day by day
      // (digikeyPaths): per API lookup only when no lookup in the range is unsplit
      const http = !countedFrom(view, AMOUNT.upstreamOf("digikey")).text ? paths.requests : null;
      const lookups = paths.lookups || 0;
      box.append(kv([
        ["Lookups sent to DigiKey", full(d.sent)],
        viaExt ? [`Through the API${pathNote}`, full(paths.api)] : [null],
        viaExt ? [`Through ext${pathNote}`, full(paths.ext)] : [null],
        http && lookups > 0 && http >= lookups ? [viaExt && !paths.unsplit ? "HTTP requests per API lookup" : "HTTP requests per lookup", (http / lookups).toFixed(1)] : [null],
        typeof asked === "number" ? ["Part numbers asked", full(asked)] : [null],
        ["Answered from saved answers", `${full(d.cached)}${typeof asked === "number" && asked > 0 && d.cached ? ` (${percent(d.cached / asked)} of part numbers asked)` : ""}`],
        ["Not real part numbers, so not sent", d.skipped ? full(d.skipped) : null],
        turnedAway, refusedUs,
      ], { cls: "dist" }));
    }
    split.append(box);
  }
  const da = a.distributor_apps || {};
  const apps = new Map();
  for (const [tool, byApp] of Object.entries(da)) for (const [app, o] of Object.entries(byApp || {})) {
    const r = apps.get(app) || { app, total: 0, away: 0 };
    r[tool] = (r[tool] || 0) + (o.calls || 0);
    r.total += o.calls || 0;
    r.away += o.rate_limited || 0;
    apps.set(app, r);
  }
  if (apps.size) {
    const tools = Object.keys(da);
    const list = [...apps.values()].sort((x, y) => y.total - x.total).slice(0, 6);
    const anyAway = [...apps.values()].some((r) => r.away);
    const appCov = countedFrom(view, AMOUNT.distributorApps);
    split.append(h("div", { class: "whole" }, h("h3", {}, "Which apps ask for them", h("small", { text: `tool calls, ${appCov.text ? `counted ${appCov.text}` : "this range"}` })),
      table(["App", ...tools.map((t) => TOOL_SHORT[t] || t), ...(anyAway ? ["Turned away"] : [])],
        list.map((r) => h("tr", {}, h("td", { class: "name", text: appName(r.app), title: r.app }), tools.map((t) => h("td", { text: r[t] ? full(r[t]) : "" })),
          anyAway ? h("td", { class: r.away ? null : "zero", text: r.away ? full(r.away) : "" }) : null)))));
  }
  sec.append(split);
  const stored = payload.health?.distributor_stored?.answers;
  if (typeof stored === "number") {
    sec.append(h("div", { class: "chart-sub" }, h("span", { text: `The server keeps ${plural(stored, "saved Mouser and DigiKey answer")} (checked ${healthSample(view).label}).` })));
  }
}

/** Mouser's daily budget follows its configured UTC start; its pace is the whole pool's, every budget together. */
function mouserQuota(view) {
  const q = payload.health?.distributor_quota?.mouser;
  if (!q?.limit) return h("div");
  const sample = healthSample(view, mouserDayStartHour(payload?.health));
  if (!sample.currentDay || sample.retained) return h("div", { class: "chart-sub", text: `Last Mouser budget reading, ${sample.label}: ${full(q.used_today || 0)} of ${full(q.limit)} used.${sample.currentDay ? " Health update failed or is behind the stats." : " Current budget unavailable; this reading predates the reset or has no timestamp."}` });
  const pool = budgetPool(q);
  const several = pool?.list?.length > 1;
  const used = several ? pool.used : q.used_today || 0, limit = several ? pool.limit : q.limit;
  const now = sample.at.getTime();
  const day = serverDay(sample.at, mouserDayStartHour(payload?.health));
  const frac = Math.min(1, Math.max(0.05, (now - day.start.getTime()) / 86400_000));
  const pace = used / frac;
  const scale = Math.max(limit, pace) * 1.05;
  const pct = (v) => `${Math.min(100, (v / scale) * 100)}%`;
  const text = `Daily budget${several ? ", every budget together," : ""} checked ${sample.label}: ${full(used)} of ${full(limit)} used since ${dayHourET(day.start)}. At this pace about ${compact(pace)} by ${dayHourET(day.end)}, when it resets.`;
  return h("div", { class: "bullet", title: text },
    h("div", { class: "track" }, h("div", { class: "zone", style: { width: pct(limit) } }), h("div", { class: "fill", style: { width: pct(used) } }), h("div", { class: "pace", style: { left: pct(pace) } })),
    h("div", { class: "cap" }, h("span", { text })));
}

// ---------------------------------------------------------------- U6 limits and queues

/** How many times the server started in the range: listed starts where they're all listed (0.10.12), else the counter. */
function restartCount(view) {
  const listed = view.recs.every((r) => r.starts_complete === true);
  if (listed && view.recs.length) return { n: view.recs.reduce((x, r) => x + r.starts.length, 0), about: false };
  const a = view.agg;
  if (a.restarts == null) return null;
  return { n: a.restarts, about: view.recs.some((r) => r.approx) && a.restarts > 0 };
}

function renderCapacity(view) {
  const sec = $("capacity");
  const a = view.agg, hl = payload.health;
  sec.replaceChildren(cardHead(sec, "Limits and queues", "How close the server came to its own limits."));
  const pr = a.per_ip_refusals;
  const dw = a.db_waits, dl = a.datasheet_links;
  // a counter the server began keeping after the range's first day says from when
  const from = (amount) => { const c = countedFrom(view, amount); return c.text ? ` (${c.text})` : ""; };
  const capped = heldBackOf(a, "address_daily"), blocked = heldBackOf(a, "address_blocked");
  const waited = Object.entries(a.upstream || {}).filter(([, u]) => u?.waited > 0).sort((x, y) => y[1].waited - x[1].waited);
  const restarts = restartCount(view);
  const pl = hl?.platform_ranges;
  // the list's own time has no zone: it is UTC
  const created = typeof pl?.openai_list_created === "string" ? pl.openai_list_created : null;
  const listed = created ? parseIso(/(Z|[+-]\d\d:?\d\d)$/i.test(created) ? created : created + "Z") : null;
  const listAge = listed && Number.isFinite(listed.getTime()) ? Math.floor((Date.now() - listed.getTime()) / 86400_000) : null;
  const lines1 = [
    ["Requests turned away by the per-address limit",
      pr?.total ? `${full(pr.total)}${fromAddresses(addressBound(view.recs, "rate_limited"), pr.total)}: ${["everyone_else", "platform_ranges", "too_many_clients"].filter((g) => pr[g]).map((g) => refusalGroupLabel(g)).join("; ")}` : "0"],
    capped ? ["Lookups turned away by an address's daily allowance", `${full(capped)}${fromAddresses(addressBound(view.recs, "cap_reached"), capped)}`] : [null],
    blocked ? ["Lookups from the blocked address", `${full(blocked)}, none sent`] : [null],
    dw?.jobs ? [`Database jobs that had to wait${from(AMOUNT.dbJobs)}`, `${full(dw.waited)} of ${full(dw.jobs)} (${percent(dw.waited / dw.jobs)})${dw.longest_ms == null ? "" : `, longest wait ${ms(dw.longest_ms)}`}`] : [null],
    waited.length ? ["Requests that waited for a free request slot", waited.map(([src, u]) => `${upstreamLabel(src)} ${full(u.waited)}`).join(", ")] : [null],
    dl ? [`Datasheet links opened${from(AMOUNT.datasheets)}`, `${full(dl.visits)}${dl.not_found ? `; ${full(dl.not_found)} not found` : ""}`] : [null],
    dl ? ["Datasheet links turned away or failed", `${full(dl.refused || 0)} turned away, ${full(dl.failed || 0)} failed`] : [null],
    // on days rebuilt from the server's 7 PM-to-7 PM totals a restart near the boundary can land a day off
    restarts ? [`Server restarts${view.key === "today" ? " since midnight" : ""}${from(AMOUNT.restarts)}`, `${restarts.about ? "about " : ""}${full(restarts.n)}`] : [null],
    pl ? ["AI platform address ranges", `Anthropic ${full(pl.anthropic)}, OpenAI ${full(pl.openai)}${listAge != null ? `; OpenAI's list from ${dayLabel(partsET(listed).key)} (${plural(listAge, "day")} old)` : ""}`] : [null],
    payload.kept_across_restarts === false ? ["Stats kept across restarts", "No: each restart starts the day's counts again"] : [null],
  ];
  sec.append(kv(lines1, { stack: true }));
}

// ---------------------------------------------------------------- U7 search

function renderSearch(view) {
  const sec = $("search");
  const cov = countedFrom(view, AMOUNT.terms);
  sec.replaceChildren(cardHead(sec, "Popular search words",
    `How many searches used each word${cov.has && cov.text ? `, ${cov.text}` : ""}. The server keeps a word only once enough different callers have used it that day; rare words and whole queries are never kept.`));
  const terms = Object.entries(view.agg.popular_terms || {}).map(([name, value]) => ({ name, value })).sort((x, y) => y.value - x.value);
  if (!terms.length) {
    sec.append(h("div", { class: "empty", text: !cov.has && cov.text ? `Search words are kept ${cov.text}; this range ends before that.` : "No search word was used by enough callers in this range." }));
    return;
  }
  const split = h("div", { class: "split" });
  const half = Math.ceil(Math.min(30, terms.length) / 2);
  // two columns of one list: both drawn against the top word, so bar lengths compare across them
  split.append(h("div", {}, ranked(terms.slice(0, half), { limit: half })));
  if (terms.length > half) split.append(h("div", {}, ranked(terms.slice(half, 30), { limit: 15, max: terms[0].value })));
  sec.append(split);
}

// ---------------------------------------------------------------- U8 deploys, restarts and new apps

/**
 * What each listed server start was: a new version (its version differs from the start before),
 * the catalog update (/health's catalog time changed across it) or another restart.
 */
function startKinds(starts) {
  const runs = deploys();
  const changes = (payload?.catalog_changes || []).map((c) => [Date.parse(c.before), Date.parse(c.at)]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  return starts.map((s, i) => {
    // the version running just before: the latest of the previous start and the run the dashboard's
    // checks place before this one (a rollback between two starts of one version)
    const run = runs.filter((r) => r.at < s.at).at(-1);
    const prev = i ? starts[i - 1] : null;
    const before = prev && (!run || prev.at >= run.at) ? prev.version : run?.version;
    if (s.version && before && s.version !== before) return "deploy";
    // the latest start between the two health checks that saw the old and the new catalog
    const change = changes.find(([x, y]) => x < s.at && s.at <= y);
    if (change && !starts.some((o) => o.at > s.at && o.at <= change[1])) return "catalog";
    return "restart";
  });
}

/** "0", "<0.1", "1.5" or "12" failures per 1,000 calls. */
function perThousand(n, calls) {
  if (!calls) return "–";
  const r = (1000 * n) / calls;
  return !n ? "0" : r < 0.1 ? "<0.1" : r < 10 ? r.toFixed(1) : String(Math.round(r));
}

/** Calls, failures, refusals and response times per server version, newest first. */
function versionScorecard(view) {
  const runs = (payload?.versions || []).filter((r) => typeof r.calls === "number").slice(-6).reverse();
  if (!runs.length) return null;
  const bounds = view.bounds;
  const now = Date.now();
  const span = (r) => {
    const a = Date.parse(r.from), b = r.to ? Date.parse(r.to) : now;
    const hours = (b - a) / HOUR;
    return hours < 48 ? `${Math.max(1, Math.round(hours))} h` : `${Math.round(hours / 24)} days`;
  };
  const body = runs.map((r) => {
    const about = r.approx ? "about " : "";
    const lat = Array.isArray(r.latency) && sumArr(r.latency) > 0 ? latencyText(r.latency, bounds, 0.95).replace("≤", "") : "–";
    return h("tr", {},
      h("td", { class: "name", text: r.version }),
      h("td", { class: "opt-sm", text: `${r.exact ? "" : "seen "}${dayTimeET(new Date(r.from))}${r.to ? "" : ", running"}` }),
      h("td", { class: "opt-sm", text: `${span(r)}${r.partial ? " (stored part)" : ""}` }),
      h("td", { text: `${about}${full(r.calls)}` }),
      h("td", { class: r.failed ? "hot" : "zero", text: perThousand(r.failed, r.calls) }),
      h("td", { class: r.rejected ? null : "zero", text: full(r.rejected) }),
      h("td", { class: r.turned_away ? null : "zero", text: full(r.turned_away) }),
      h("td", { class: "opt-md", text: lat }));
  });
  return h("div", { class: "scorecard" }, h("h3", {}, "Versions", h("small", { text: "each run from its start to the next version's" })),
    table(["Version", "Started", "Ran for", "Calls", "Failed per 1,000 calls", "Rejected", "Turned away", "95% answered within"], body,
      { cls: [null, "opt-sm", "opt-sm", null, null, null, null, "opt-md"] }));
}

function renderEvents(view) {
  const sec = $("events");
  // a log of recent history: it always runs up to today, and back 30 days or to the range's start
  const end = view.today;
  const back = addDays(end, -29);
  const start = view.dates[0] < back ? view.dates[0] : back;
  const first = view.days.find((d) => !d.partial_start)?.date;
  const from = first && first > start ? first : start;
  sec.replaceChildren(cardHead(sec, "Deploys, restarts and new apps",
    `${dayLabel(from)} to today${view.dates[0] < back ? "" : ", whatever range is selected"}.`));
  const card = versionScorecard(view);
  if (card) sec.append(card);
  // Server 0.10.12 lists each start's minute and version; before it, versions, restarts and new apps
  // are counted per server day (7 PM to 7 PM) with no hourly detail: on a day rebuilt from those
  // totals they can't be placed, so only exact days list them. A version seen only by the dashboard's
  // hourly checks started between its last check of the version before and its first of this one.
  const starts = allStarts(payload.edays || []);
  const kinds = startKinds(starts);
  const runs = deploys();
  const versionsWithStarts = new Set(runs.filter((r) => r.exact).map((r) => r.version));
  const firstVersion = Object.entries(view.seen.versions).filter(([v]) => !runs.some((r) => r.version === v));
  const storeStart = first;
  const estimated = view.days.filter((d) => d.approx && !d.partial_start && d.date >= from);
  if (estimated.length) {
    const next = addDays(estimated[estimated.length - 1].date, 1);
    sec.append(h("p", { class: "lead", text: `Restarts and new apps can be dated from ${dayLabel(next, { weekday: true })} on, the first full day this dashboard recorded hour by hour.` }));
  }
  const list = h("ul", { class: "events" });
  for (let d = end; d >= from; d = addDays(d, -1)) {
    const rec = view.byDate.get(d);
    if (!rec || rec.partial_start) continue;
    const tags = [];
    const tag = (cls, icon, ...txt) => tags.push(h("span", { class: `tag ${cls}` }, h("span", { class: "icon", text: icon }), ...txt));
    runs.forEach((r, i) => {
      if (r.exact || partsET(new Date(r.at)).key !== d) return;
      const t = timeET(new Date(r.at));
      // the dashboard's first look at the store's oldest version says nothing about when it went live
      if (i === 0) return tag("deploy", "◆", h("b", { text: r.version }), ` running when first checked, ${t}`);
      const vs = versionStart(r.version);
      const after = r.after ?? (vs && !vs.exact && vs.from && vs.at.getTime() === r.at ? vs.from.getTime() : null);
      tag("deploy", "◆", h("b", { text: r.version }), ` went live ${after != null ? `between ${timeET(new Date(after))} and ${t}` : `by ${t}`}`);
    });
    const listed = starts.map((s, i) => [s, kinds[i]]).filter(([s]) => s.date === d);
    for (const [s, kind] of listed) {
      const t = timeET(new Date(s.at));
      if (kind === "deploy") tag("deploy", "◆", h("b", { text: s.version || "New version" }), ` went live ${t}`);
      else tag(kind === "catalog" ? "info catalog" : "info", "↻", `${t} restart${kind === "catalog" ? ", catalog update" : ""}`);
    }
    if (!rec.approx) {
      for (const [v, date] of firstVersion) if (date === d && !versionsWithStarts.has(v)) tag("deploy", "◆", h("b", { text: v }), " first ran");
      const unlisted = (rec.restarts || 0) - listed.length;
      if (rec.starts_complete !== true && unlisted > 0) tag("info", "↻", listed.length ? `${plural(unlisted, "more restart")}, times not kept` : plural(unlisted, "restart"));
      for (const [app, n] of namedApps(rec.apps)) if (view.seen.apps[app] === d && n >= 50 && d !== storeStart) tag("info", "+", "new app ", h("b", { text: app }), ` (${plural(n, "session")})`);
    }
    if (!tags.length) continue;
    list.append(h("li", {}, h("time", { datetime: d, text: dayLabel(d, { weekday: true }) }), h("div", { class: "tags" }, tags)));
  }
  sec.append(list.children.length ? list : h("div", { class: "empty", text: "No deploys, restarts or new apps in these days." }));
}

// ---------------------------------------------------------------- render

function render({ rangeOnly = false } = {}) {
  if (!payload) return;
  // Recheck freshness at both UTC resets even while a reload is stalled or offline.
  clearTimeout(dayTimer);
  const now = new Date(Date.now());
  const resetAt = Math.min(serverDay(now).end.getTime(), serverDay(now, mouserDayStartHour(payload?.health)).end.getTime());
  dayTimer = setTimeout(render, resetAt - now.getTime());
  const focused = document.activeElement;
  const focusId = focused?.id;
  const days = (payload.edays || []).filter((d) => !d.partial_start);
  if (!rangeOnly) renderHeader();
  if (!days.length) {
    const boot = $("boot");
    boot.hidden = false;
    boot.textContent = "No numbers stored yet. Press Refresh, or run: uv run pcbparts-dashboard collect";
    $("app").hidden = true;
    return;
  }
  $("boot").hidden = true;
  $("app").hidden = false;
  $("footer").hidden = false;
  const view = buildView({ ...payload, edays: days }, state.range);
  const previous = currentView;
  currentView = view;
  const y = scrollY;
  // A table wider than a phone scrolls sideways, and a redraw replaces it: keep each one's position,
  // found again by its section and its place in that section
  const sideways = [...document.querySelectorAll(".table-wrap")].filter((wrap) => wrap.scrollLeft).map((wrap) => {
    const section = wrap.parentElement?.closest("[id]");
    return section && [section.id, [...section.querySelectorAll(".table-wrap")].indexOf(wrap), wrap.scrollLeft];
  }).filter(Boolean);
  renderControls(view);
  renderAttention(view);
  renderKpis(view);
  renderTraffic(view);
  renderTools(view);
  renderClients(view);
  renderErrors(view);
  renderUpstreams(view);
  renderCapacity(view);
  renderSearch(view);
  // Recent events cover at least 30 days, so most range switches leave this section unchanged.
  const eventStart = (v) => v.dates[0] < addDays(v.today, -29) ? v.dates[0] : addDays(v.today, -29);
  if (!rangeOnly || !previous || eventStart(previous) !== eventStart(view)) renderEvents(view);
  scrollTo(0, y);
  for (const [id, index, left] of sideways) {
    const wrap = [...(document.getElementById(id)?.querySelectorAll(".table-wrap") || [])][index];
    if (wrap) wrap.scrollLeft = left;
  }
  const restoreFocus = () => {
    if (focusId && !focused.isConnected && document.activeElement === document.body) $(focusId)?.focus({ preventScroll: true });
  };
  restoreFocus();
  // Open tool charts are drawn on the next frame. Don't take focus if the user moved meanwhile.
  requestAnimationFrame(restoreFocus);
  if (rangeOnly) return;
  const reset = resetHour(view.asOf);
  $("footer-time").textContent = `All times are Eastern. A day here runs midnight to midnight. Mouser's budget resets at ${resetHour(view.asOf, mouserDayStartHour(payload?.health))}; DigiKey's budget, per-address allowances and the server's daily stats reset at ${reset}.`;
  const lastEst = days.filter((d) => d.approx).pop()?.date;
  const est = lastEst
    ? ` Days up to ${dayLabel(lastEst)} were rebuilt from the server's own daily totals (${reset} to ${reset}): their calls per hour are exact, their other numbers close estimates.`
    : "";
  $("footer-source").textContent = `This dashboard holds ${plural(days.length, "day")}, ${dayLabel(days[0].date)} to ${dayLabel(days[days.length - 1].date)}, and checks the server every ${payload.poll_minutes || 60} minutes.${est}`;
}

readHash();
addEventListener("hashchange", () => { readHash(); render({ rangeOnly: true }); });
let resizeTimer, lastWidth = innerWidth;
addEventListener("resize", () => {
  if (innerWidth === lastWidth) return;
  lastWidth = innerWidth;
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(render, 150);
});
$("refresh").addEventListener("click", refresh);
load();
setInterval(() => load({ quiet: true }), 5 * 60_000);
