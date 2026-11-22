// PCB Parts usage dashboard: one page over /api/data. Days and times are Eastern; problems
// (failures, refusals, held-back lookups, rejected arguments, service errors) count only from the
// deploy in payload.problems_since, usage covers the whole selected range.
import {
  addDays, ago, compact, dateTimeET, dayHourET, dayLabel, dayTimeET, delta, etMidnight, full, h, hourET,
  latencyText, ms, parseIso, partsET, percent, percentile, resetHour, serverDay, timeET, tzAbbr, weekdayDateET,
} from "./format.js";
import {
  AMOUNT, NOT_NAMED_APPS, RANGES, aggregate, allLatency, buildView, callsByApp, completeDay, countedFrom, daily, hourly,
  namedApps, own, problemHours as hourPoints, sumArr, sumObj, totals, trendDays,
} from "./data.js";
import {
  DISTRIBUTOR_LABEL, STATUS_GROUPS, TOOL_SHORT, badRequestLabel, heldBackLabel, isFailureReason,
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

let payload = null;
let currentView = null;
let loadError = null;
let pollTimer = null;
let dayTimer = null;
const state = { range: "today", open: new Set(), sort: { key: "calls", dir: -1 }, tables: new Set() };

// ---------------------------------------------------------------- loading

async function load({ quiet = false } = {}) {
  const main = $("main");
  if (payload && !quiet) main.classList.add("stale");
  try {
    const r = await fetch("/api/data", { cache: "no-store" });
    if (!r.ok) throw new Error(`/api/data answered ${r.status}`);
    payload = await r.json();
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
    const r = await fetch("/api/refresh", { method: "POST" });
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

function kv(pairs, { stack = false } = {}) {
  const dl = h("dl", { class: stack ? "kv stack" : "kv" });
  for (const [k, v] of pairs) {
    if (k == null || v == null) continue;
    dl.append(h("dt", { text: k }), h("dd", {}, v instanceof Node ? v : String(v)));
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

// ---------------------------------------------------------------- the problems window

/**
 * Where problems apply in this range. Problems are counted from payload.problems_since; usage over
 * the whole range. `before`: the range ends before that moment, so it has no problem numbers at all.
 */
function scope(view) {
  const since = view.since;
  if (!since) return { applies: true, before: false, label: "", from: null, ver: null };
  const end = etMidnight(addDays(view.dates[view.dates.length - 1], 1));
  const before = end <= since.getTime();
  const ver = view.sinceVersion;
  const when = dayTimeET(since);
  return {
    applies: !before, before, from: since, ver, when,
    label: ver ? `since ${ver} went live (${when})` : `since ${when}`,
    short: `since ${when}`,
    bites: etMidnight(view.dates[0]) < since.getTime(),
  };
}

/** Everything the problems part of the range holds, as plain counts. */
function problemFigures(view) {
  const p = view.problems;
  if (!p) return null;
  const T = totals(p);
  const refused = p.per_ip_refusals?.total ?? 0;
  let held = 0;
  for (const lim of Object.values(p.distributor_limits || {})) held += sumObj(lim?.held_back);
  const links = p.datasheet_links?.refused ?? 0;
  return { T, calls: T.calls, failed: T.failed, rejected: T.bad_request, refused, held, links, turnedAway: refused + held + links };
}

// ---------------------------------------------------------------- header

function nextUpdate() {
  return payload?.next_poll_at ? new Date(payload.next_poll_at) : null;
}

/** Health has its own fetch time; distributor budgets reset at midnight UTC. */
function healthSample(view) {
  const at = parseIso(payload?.health_at);
  const known = at && Number.isFinite(at.getTime());
  const now = new Date(Math.max(view?.now?.getTime() || 0, Date.now()));
  return {
    at: known ? at : null,
    label: known ? `${dateTimeET(at)} ${tzAbbr(at)}` : "an unknown time",
    currentDay: known && serverDay(at).start.getTime() === serverDay(now).start.getTime(),
    retained: !!payload?.last_fetch?.health_error || !known || at < parseIso(payload?.as_of),
  };
}

function renderHeader() {
  const hl = payload?.health;
  const sample = healthSample();
  const problems = [];
  if (payload?.last_fetch?.health_error) problems.push("health update failed");
  if (hl) {
    if (hl.status !== "healthy") problems.push(hl.status || "unhealthy");
    if (hl.snapshot?.stale) problems.push("catalog out of date");
    const dp = hl.database_pressure;
    if (dp && (dp.stalled_seconds > 0 || dp.waiting > 0)) problems.push(`${dp.waiting} database jobs waiting`);
    for (const [k, q] of Object.entries(hl.distributor_quota || {})) if (q?.paused_until) problems.push(`${DISTRIBUTOR_LABEL[k] || k} paused`);
  }
  const led = $("led");
  led.hidden = !problems.length;
  led.dataset.state = hl && hl.status !== "healthy" ? "critical" : "warning";
  $("led-text").textContent = problems.join(", ");

  const bs = $("board-status");
  bs.querySelectorAll(".extra").forEach((e) => e.remove());
  if (hl) {
    bs.append(h("span", { class: "extra", text: `Health values from ${sample.label}` }));
    const vs = payload.version_since;
    const since = vs && vs.version === hl.version && vs.since ? ` since ${dayTimeET(new Date(vs.since))}` : "";
    bs.append(h("span", { class: "extra" }, "Server ", h("b", { text: (hl.version || "?") + since })));
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
  for (const w of warned.values()) items.push({ level: "warning", what: w.message, detail: `Noted by the dashboard, ${dayTimeET(new Date(w.at))}.` });
  const hl = payload.health;
  const sample = healthSample(view);
  if (lf?.health_error) items.push({ level: "warning", what: `Health update failed: ${lf.health_error}.`, detail: hl ? `Retained health values are from ${sample.label}.` : "No health values are available." });
  if (hl && hl.status !== "healthy") items.push({ level: "critical", what: `The server reported "${hl.status || "no status"}".`, detail: `From /health, checked ${sample.label}.` });
  if (hl?.snapshot?.stale) items.push({ level: "warning", what: "The parts catalog is out of date.", detail: `Last JLCPCB scrape ${dayTimeET(new Date(hl.snapshot.data_as_of))}.` });
  if (hl?.database_pressure?.waiting > 0) items.push({ level: "warning", what: `${plural(hl.database_pressure.waiting, "database job")} waiting when health was checked ${sample.label}.`, detail: `The oldest had waited ${hl.database_pressure.oldest_wait_seconds} s.` });

  const p = view.problems;
  if (!sc.applies || !p) return items;
  const f = problemFigures(view);
  if (f.failed) {
    const parts = Object.entries(p.tools || {}).filter(([, v]) => v.failed > 0).sort((x, y) => y[1].failed - x[1].failed).map(([t, v]) => {
      const why = Object.entries(own(p.reasons, t) || {}).filter(([c, n]) => n > 0 && isFailureReason(c)).sort((x, y) => y[1] - x[1]).map(([c]) => midSentence(reasonLabel(c)));
      return `${t} ${full(v.failed)}${why.length ? ` (${why.slice(0, 2).join("; ")})` : ""}`;
    });
    items.push({ level: "critical", what: `${plural(f.failed, "call")} failed.`, detail: parts.slice(0, 4).join(", ") + "." });
  }
  if (f.refused) {
    const pr = p.per_ip_refusals;
    const groups = ["everyone_else", "platform_ranges", "too_many_clients", "server_busy"].filter((g) => pr[g] > 0);
    const when = whenText(hourPoints(view, "refused_hours"), !view.single);
    items.push({
      level: "warning", what: `${plural(f.refused, "request")} turned away by our per-address limit${when ? ` (${when})` : ""}.`,
      detail: `${groups.map((g) => refusalGroupLabel(g)).join("; ")}. The server log's hourly line names the address.`,
    });
  }
  for (const [name, lim] of Object.entries(p.distributor_limits || {})) {
    const who = DISTRIBUTOR_LABEL[name] || name;
    const held = Object.entries(lim?.held_back || {}).filter(([, n]) => n > 0).sort((x, y) => y[1] - x[1]);
    const n = held.reduce((x, [, v]) => x + v, 0);
    if (n) {
      const when = whenText(hourPoints(view, (r) => own(r.distributor_limits, name)?.held_back_hours), !view.single);
      const why = held.slice(0, 3).map(([c, v]) => `${heldBackLabel(c, who, resetHour(view.asOf))}${held.length > 1 ? ` (${full(v)})` : ""}`);
      if (held.length > 3) why.push(`${held.length - 3} other causes (${full(held.slice(3).reduce((x, [, v]) => x + v, 0))})`);
      items.push({ level: "warning", what: `${plural(n, `${who} lookup`)} turned away by limits${when ? ` (${when})` : ""}.`, detail: `Why: ${why.join("; ")}.` });
    }
    const refused = Object.entries(lim?.refusals || {}).filter(([, v]) => v > 0);
    if (refused.length) items.push({ level: "warning", what: `${who} refused ${plural(refused.reduce((x, [, v]) => x + v, 0), "of our requests", "of our requests")}.`, detail: refused.map(([c, v]) => `${refusedLabel(c)} ${full(v)}`).join(", ") });
  }
  for (const [src, st] of Object.entries(p.upstream_status || {})) {
    const tot = sumObj(st);
    const groups = STATUS_GROUPS.slice(2).map((g) => [g.label, g.keys.reduce((x, k) => x + (st[k] || 0), 0)]).filter(([, v]) => v > 0);
    const bad = groups.reduce((x, [, v]) => x + v, 0);
    const hard = (st["5xx"] || 0) + (st.timeout || 0) + (st.connection || 0) + (st.challenge || 0) + (st.other_error || 0);
    if ((bad >= 3 && tot && bad / tot >= 0.02) || hard >= 5) {
      items.push({ level: "warning", what: `${upstreamLabel(src)}: ${full(bad)} of ${full(tot)} requests got an error answer.`, detail: groups.map(([l, v]) => `${l.toLowerCase()} ${full(v)}`).join(", ") + "." });
    }
  }
  const dl = p.datasheet_links;
  if (dl?.refused) items.push({ level: "warning", what: `${plural(dl.refused, "datasheet link")} turned away.`, detail: "Too many new links were asked for at once." });
  if (dl?.failed) items.push({ level: "warning", what: `${plural(dl.failed, "datasheet link")} failed.`, detail: "JLCPCB didn't answer." });
  for (const [t, o] of Object.entries(p.lcsc_lookups || {})) {
    if (o?.live_failed) items.push({ level: "warning", what: `${plural(o.live_failed, "live stock lookup")} in ${t} failed with nothing to fall back on.` });
  }
  if (p.db_waits?.longest_ms >= 10_000) items.push({ level: "warning", what: `A request waited ${ms(p.db_waits.longest_ms)} for the database.`, detail: `${full(p.db_waits.waited)} of ${full(p.db_waits.jobs)} database jobs had to wait.` });
  return items;
}

function renderAttention(view) {
  const box = $("attention");
  const sc = scope(view);
  const items = attentionItems(view, sc);
  // the period the problem lines cover, said once beside the title whenever it isn't the whole range
  const sub = sc.before || !sc.from || !sc.bites ? "" : sc.label;
  const title = h("h2", {}, "Worth a look", sub ? h("small", { text: sub }) : null);
  if (!items.length) {
    let text;
    if (sc.before) text = `Nothing to check here: problems are counted since ${sc.ver ? `${sc.ver} went live (${sc.when})` : sc.when}, and this range ends before that.`;
    else {
      const f = problemFigures(view);
      text = f
        ? `Nothing: ${plural(f.calls, "call")}, none failed, none turned away by limits.${f.rejected ? ` ${plural(f.rejected, "call")} had arguments the tool rejected, listed under Reasons.` : ""}`
        : "Nothing in this range.";
    }
    box.replaceChildren(title, h("p", { class: "clear", text }));
    return;
  }
  box.replaceChildren(
    title,
    h("ul", {}, items.map((it) => h("li", { "data-level": it.level },
      h("span", { class: "dot", "aria-hidden": "true" }),
      h("div", {}, h("span", { class: "what", text: it.what }), it.detail ? " " : null,
        it.detail ? h("span", { class: "detail", text: it.detail }) : null)))));
}

// ---------------------------------------------------------------- headline numbers

function usage(a) {
  if (!a) return null;
  const T = totals(a);
  const answered = T.ok + T.similar_only + T.not_found;
  const lat = allLatency(a);
  return { T, calls: T.calls, answered, nf: T.not_found, sessions: a.apps ? sumObj(a.apps) : null, lat: sumArr(lat) > 0 ? lat : null };
}

function renderKpis(view) {
  const sc = scope(view);
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

  // biggest app by sessions
  const apps = namedApps(view.agg.apps).sort((x, y) => y[1] - x[1]);
  const capped = !!view.agg.apps?.other;
  const top = apps[0];
  const nfShare = (m) => (m && m.answered ? m.nf / m.answered : null);
  const topReason = (() => {
    const all = [];
    for (const [t, labels] of Object.entries(view.agg.reasons || {})) for (const [c, n] of Object.entries(labels || {})) if (!isFailureReason(c)) all.push([t, c, n]);
    all.sort((x, y) => y[2] - x[2]);
    return all[0];
  })();
  const f = problemFigures(view);
  const latCov = countedFrom(view, AMOUNT.latency);
  // a problem tile says its own period whenever that isn't the whole range
  const period = sc.bites ? sc.short : "";
  const notes = (...parts) => parts.filter(Boolean).join("; ");
  const problemTile = (label, value, note) => sc.before
    ? { label, value: "–", note: `counted ${sc.short}` }
    : { label, value: full(value ?? 0), note: notes(period, value ? note : "") };

  const q = payload.health?.distributor_quota?.mouser;
  const sample = healthSample(view);
  const budgetDay = serverDay(sample.at || view.now);
  const budgetTile = view.key === "today" && q?.limit && sample.currentDay
    ? { label: "Mouser daily budget", value: `${full(q.used_today ?? 0)}`, small: `of ${full(q.limit)}`, note: `${sample.retained ? "Retained value" : "Checked"} ${sample.label}; used since ${dayHourET(budgetDay.start)}; resets ${dayHourET(budgetDay.end)}` }
    : (() => {
      const d = view.agg.distributors || {};
      const m = d.mouser?.sent || 0, k = d.digikey?.sent || 0;
      return { label: "Mouser and DigiKey lookups", value: compact(m + k), note: `DigiKey ${compact(k)}, Mouser ${compact(m)}` };
    })();
  const awayParts = f ? [[f.refused, "request"], [f.held, "Mouser or DigiKey lookup"], [f.links, "datasheet link"]].filter(([n]) => n > 0).map(([n, w]) => plural(n, w)).join(", ") : "";

  const tiles = [
    {
      label: "Sessions started", value: compact(cur.sessions), d: change(cur.sessions, prev?.sessions),
      note: cur.sessions ? `one each time an app connects; ${(cur.calls / cur.sessions).toFixed(1)} tool calls a session` : "one each time an app connects",
      spark: (m) => m?.sessions,
    },
    {
      label: "Biggest app", value: top ? top[0] : "–", wrapValue: true,
      note: top && cur.sessions ? `${percent(top[1] / cur.sessions)} of sessions; ${capped ? "more than " : ""}${plural(apps.length, "app")} connected` : "",
    },
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
    problemTile("Failed calls", f?.failed, "something broke here or in a service we call"),
    problemTile("Rejected arguments", f?.rejected, "the AI called a tool wrongly"),
    problemTile("Turned away by limits", f?.turnedAway, awayParts),
    budgetTile,
  ];
  $("tiles").replaceChildren(...tiles.map((t) => h("div", { class: "tile" },
    h("div", { class: "label", text: t.label }),
    h("div", { class: `value${t.wrapValue ? " name-value" : ""}` }, t.value, t.small ? h("small", { text: t.small }) : null),
    deltaEl(t.d, t.d?.tone === "neutral" ? null : vs),
    t.note ? h("div", { class: "note", text: t.note }) : null,
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

function renderTraffic(view) {
  const sec = $("traffic");
  const sc = scope(view);
  // failed is red and turned away amber here, as their dots are in the Worth-a-look box
  const copper = css("--copper"), cmpColor = css("--silk-dim"), crit = css("--critical"), serious = css("--warning");
  let points, calls, failed, refused, compare = null, markers = [], desc, peakText, peakDate = null;
  const sinceMs = sc.from ? sc.from.getTime() : null;

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
    if (view.single) {
      const prev = view.byDate.get(addDays(view.dates[0], -1));
      if (prev?.hours && (view.key === "today" || view.prevAgg)) compare = { label: view.key === "today" ? "Yesterday" : "The day before", color: cmpColor, values: hrs.map((_, i) => prev.hours[i] ?? null) };
    }
    if (sinceMs != null) {
      const i = hrs.findIndex((p) => p.ts <= sinceMs && sinceMs < p.ts + HOUR);
      if (i >= 0) markers.push({ index: i, label: `${sc.ver || "deploy"}, ${timeET(sc.from)}` });
    }
    desc = "Tool calls per hour.";
    const i = calls.reduce((best, v, k) => (v != null && v > (calls[best] ?? -1) ? k : best), 0);
    if (calls[i] != null) peakText = ["Busiest hour: ", h("strong", { text: hourSpan(hrs[i].ts, !view.single) }), `, ${full(calls[i])} calls`];
  } else {
    const rows = daily(view);
    points = rows.map((r) => ({ title: dayLabel(r.date, { weekday: true }), tick: dayLabel(r.date) }));
    calls = rows.map((r) => r.calls);
    failed = rows.map((r) => r.failed);
    refused = rows.map((r) => r.refused);
    if (sc.from) {
      const idx = view.dates.indexOf(partsET(sc.from).key);
      if (idx >= 0) markers.push({ index: idx, label: sc.ver || "deploy" });
    }
    for (const [ver, date] of Object.entries(view.seen.versions)) {
      const idx = view.dates.indexOf(date);
      if (ver !== sc.ver && idx >= 0 && !view.byDate.get(date)?.approx) markers.push({ index: idx, label: ver });
    }
    markers = markers.slice(-8);
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
  const f = problemFigures(view);
  const nFailed = f?.failed ?? 0, nRefused = f?.refused ?? 0;
  if (sc.before) {
    sec.append(h("div", { class: "chart-sub" }, h("span", { text: `Failed calls and turned-away requests are counted ${sc.label}; this range ends before that.` })));
  } else if (!nFailed && !nRefused) {
    sec.append(h("div", { class: "chart-sub" }, h("span", { text: `No failed calls and no requests turned away by the per-address limit ${sc.bites ? sc.label : "in this range"}.` })));
  } else {
    sec.append(h("div", { class: "chart-sub" }, h("span", {}, `${sc.bites ? cap1(sc.label) + ": " : ""}`, h("strong", { text: full(nFailed) }), ` failed calls, `, h("strong", { text: full(nRefused) }), ` requests turned away by the per-address limit`)));
    if (sumArr(failed) + sumArr(refused) > 0) {
      sec.append(legend([{ label: "Failed calls", color: crit }, { label: "Turned away by the per-address limit", color: serious }]));
      const c2 = h("div");
      sec.append(c2);
      columns(c2, { points, height: 110, ariaLabel: "Failed calls and turned-away requests", series: [{ label: "Failed", color: crit, values: failed }, { label: "Turned away", color: serious, values: refused }] });
    }
  }

  if (!view.single) sec.append(heatmap(view));

  const head = ["When", "Tool calls"];
  if (compare) head.push(compare.label);
  // failed and turned away exist only since the deploy: no columns for a range that ends before it
  if (!sc.before) head.push("Failed", "Turned away");
  sec.append(h("div", { class: "table-view" }, table(head, points.map((p, i) => h("tr", {},
    h("td", { text: p.title }), h("td", { text: full(calls[i]) }),
    compare ? h("td", { text: full(compare.values[i]) }) : null,
    sc.before ? null : h("td", { text: failed[i] == null ? "" : full(failed[i]) }), sc.before ? null : h("td", { text: refused[i] == null ? "" : full(refused[i]) }))))));
}
const cap1 = (s) => s.charAt(0).toUpperCase() + s.slice(1);

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

function renderTools(view) {
  const sec = $("tools");
  const sc = scope(view);
  const a = view.agg, p = view.problems;
  const prevTools = view.prevAgg?.tools;
  const bounds = view.bounds;
  const trend = trendDays(view);
  const names = new Set([...Object.keys(a.tools || {}), ...Object.keys(view.seen.tools)]);
  names.delete("unknown"); // calls to tools that don't exist: listed under rejected arguments
  const rows = [...names].map((t) => {
    const v = own(a.tools, t) || {};
    const pv = own(p?.tools, t) || {};
    const answered = (v.ok || 0) + (v.similar_only || 0) + (v.not_found || 0);
    const lat0 = own(a.latency, t)?.counts;
    const lat = sumArr(lat0) > 0 ? lat0 : null;
    return {
      t, v, pv, calls: v.calls || 0, answered, prev: prevTools ? own(prevTools, t)?.calls ?? 0 : null, lat,
      p95: percentile(lat, bounds, 0.95), probs: (pv.bad_request || 0) + (pv.rate_limited || 0) + (pv.failed || 0),
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
  // no column of blanks: problems show only where the range reaches the deploy and some tool has one
  const hasProbs = !sc.before && rows.some((r) => r.probs);
  const period = sc.bites ? ` ${sc.short}` : "";
  const cols = [
    { key: "name", label: "Tool" },
    { key: "calls", label: "Calls" },
    hasPrev && { key: "change", label: "Change", cls: "opt-sm" },
    { key: "nf", label: "Found nothing" },
    hasLat && { key: "p95", label: "95% answered within", cls: "opt-md" },
    hasProbs && { key: "probs", label: `Problems${period}` },
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
  const problemText = (pv) => [
    pv.bad_request ? `${full(pv.bad_request)} rejected` : "",
    pv.rate_limited ? `${full(pv.rate_limited)} turned away` : "",
    pv.failed ? `${full(pv.failed)} failed` : "",
  ].filter(Boolean).join(", ");
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
      probs: h("td", { class: r.pv.failed ? "hot" : null, text: problemText(r.pv) }),
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
  if (!sc.before && !hasProbs) notes.append(h("span", { text: `No tool had a problem ${sc.bites ? sc.label : "in this range"}.` }));
  // calls to a tool name that doesn't exist belong to no row; say so, so the column adds up to the tile
  const noTool = own(p?.tools, "unknown")?.bad_request || 0;
  if (noTool && !sc.before) notes.append(h("span", { text: `${plural(noTool, "more rejected call")} named a tool that doesn't exist (under Reasons).` }));
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
  const sc = scope(view);
  const a = view.agg, v = own(a.tools, t) || {}, p = view.problems, pv = own(p?.tools, t) || {};
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
  if (sc.before && !latCov.has && !appCov.has) {
    // one sentence instead of three boxes that each say "not in this range"
    wrap.append(h("div", {}, h("h3", { text: "Problems, response times and calling apps" }),
      h("div", { class: "empty", text: `Counted ${sc.label}; this range ends before that.` })));
    return wrap;
  }

  const probBox = h("div", {}, h("h3", {}, "Problems", h("small", { text: sc.before ? "" : sc.bites ? sc.short : "this range" })));
  if (sc.before) probBox.append(h("div", { class: "empty", text: `Counted ${sc.label}; this range ends before that.` }));
  else {
    const bad = Object.entries(own(p?.bad_request_reasons, t) || {}).map(([c, n]) => ({ name: badRequestLabel(c), value: n }));
    const failed = Object.entries(own(p?.reasons, t) || {}).filter(([c]) => isFailureReason(c)).map(([c, n]) => ({ name: reasonLabel(c), value: n }));
    if (!bad.length && !failed.length && !pv.rate_limited) probBox.append(h("div", { class: "empty", text: "None." }));
    if (bad.length) probBox.append(h("div", { class: "subhead", text: "Rejected arguments" }), ranked(merge(bad), { color: css("--serious") }));
    if (pv.rate_limited) probBox.append(h("div", { class: "subhead", text: `Turned away by limits: ${full(pv.rate_limited)}` }));
    if (failed.length) probBox.append(h("div", { class: "subhead", text: "Failures" }), ranked(merge(failed), { color: css("--critical") }));
  }
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
  const sc = scope(view);
  const a = view.agg, prev = view.prevAgg;
  const sessions = a.apps || {};
  const byApp = callsByApp(a);
  const probByApp = callsByApp(view.problems);
  const totalSessions = sumObj(sessions);
  const names = new Set([...Object.keys(sessions), ...Object.keys(byApp)]);
  const rows = [...names].map((n) => ({
    n, s: own(sessions, n) || 0, prev: prev ? own(prev.apps, n) ?? 0 : null,
    calls: own(byApp, n)?.calls ?? null, pr: own(probByApp, n), first: view.seen.apps[n],
  })).filter((r) => r.s > 0 || r.calls > 0);
  const named = rows.filter((r) => !NOT_NAMED_APPS.has(r.n)).sort((x, y) => y.s - x.s || (y.calls || 0) - (x.calls || 0));
  const special = rows.filter((r) => NOT_NAMED_APPS.has(r.n));
  const LIMIT = 12;
  const shown = named.slice(0, LIMIT), rest = named.slice(LIMIT);
  const maxS = Math.max(1, ...shown.map((r) => r.s));
  const storeStart = view.days.find((d) => !d.partial_start)?.date;

  const appCov = countedFrom(view, AMOUNT.toolApps);
  const problemsOf = (pr) => {
    if (sc.before || !pr) return "";
    return [pr.bad_request ? `${full(pr.bad_request)} rejected` : "", pr.rate_limited ? `${full(pr.rate_limited)} turned away` : "", pr.failed ? `${full(pr.failed)} failed` : ""].filter(Boolean).join(", ");
  };
  // columns with nothing in them for this range stay out
  const hasCalls = rows.some((r) => r.calls > 0);
  const hasProbs = rows.some((r) => problemsOf(r.pr));
  const hasPrev = !!prev;
  const firstSeen = (r) => {
    if (!r.first || NOT_NAMED_APPS.has(r.n)) return h("td");
    if (r.first === storeStart) return h("td", { class: "zero", text: `${dayLabel(r.first)} or earlier` });
    // a day rebuilt from the server's 7 PM-to-7 PM totals can be one day off
    return h("td", { text: `${view.byDate.get(r.first)?.approx ? "about " : ""}${dayLabel(r.first)}` });
  };

  sec.replaceChildren(cardHead(sec, "Apps",
    "Which apps connect, by the name they send. A session starts each time an app connects.", { table: !view.single }));

  const row = (r, label) => h("tr", {},
    h("td", { class: "name", title: r.n || label, text: label || appName(r.n) }),
    h("td", {}, h("div", { class: "barcell" }, h("div", { class: "bartrack" }, r.s ? h("i", { class: "bar", style: { width: `${(r.s / maxS) * 100}%` } }) : null), h("span", { class: "bn", text: r.s ? full(r.s) : "" }))),
    h("td", { text: totalSessions && r.s ? percent(r.s / totalSessions) : "" }),
    hasPrev ? h("td", {}, deltaEl(change(r.s, r.prev)) || "") : null,
    hasCalls ? h("td", { text: r.calls ? full(r.calls) : "" }) : null,
    hasProbs ? h("td", { text: problemsOf(r.pr) }) : null,
    firstSeen(r));
  const body = shown.map((r) => row(r));
  if (rest.length) body.push(row({ n: "", s: rest.reduce((x, r) => x + r.s, 0), prev: null, calls: rest.reduce((x, r) => x + (r.calls || 0), 0) || null }, `${rest.length} more apps`));
  for (const r of special) body.push(row(r, r.n === "other" ? "Other apps (names not kept)" : "App not identified"));
  const cols = [
    ["App", null], ["Sessions", null], ["Share of sessions", "opt-sm"], hasPrev && ["Change", "opt-sm"],
    hasCalls && [`Tool calls${appCov.text ? ` ${appCov.text}` : ""}`, null],
    hasProbs && [`Problems${sc.bites ? ` ${sc.short}` : ""}`, "opt-md"], ["First seen", "opt-md"],
  ].filter(Boolean);
  sec.append(table(cols.map((c) => c[0]), body, { cls: cols.map((c) => c[1]) }));
  const notes = h("div", { class: "chart-sub notes" });
  if (hasPrev) notes.append(h("span", { class: "opt-sm", text: `Change is in sessions, ${compareShort(view)}.` }));
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
  const sc = scope(view);
  const a = view.agg, p = view.problems;
  // "unknown" is the server's bucket for calls to a tool name that doesn't exist
  const flat = (o, keep, label) => Object.entries(o || {}).flatMap(([tool, labels]) =>
    Object.entries(labels || {}).filter(([c]) => keep(c)).map(([c, n]) => ({ sub: tool === "unknown" ? "no such tool" : tool, name: label(c), value: n })));
  sec.replaceChildren(cardHead(sec, "Reasons", "Why calls were rejected, found nothing or failed, by tool."));
  const split = h("div", { class: "split" });
  const period = sc.bites ? sc.short : "this range";

  if (!sc.before) {
    split.append(h("div", {}, h("h3", {}, "Rejected arguments", h("small", { text: period })),
      h("p", { class: "lead", text: "The AI called a tool wrongly. A reason that keeps growing means that tool's description needs work." }),
      ranked(mergeSub(flat(p?.bad_request_reasons, () => true, badRequestLabel)), { color: css("--serious"), empty: totals(p).bad_request ? "No reasons were recorded for these." : "None." })));
  }

  const nfRows = mergeSub(flat(a.reasons, (c) => !isFailureReason(c), reasonLabel));
  const nfTotal = totals(a).not_found;
  const reasonCov = countedFrom(view, AMOUNT.reasons);
  // shares are of the answers that carry a reason: reasons began later than the oldest days
  split.append(h("div", {}, h("h3", {}, "Why searches and lookups found nothing", h("small", { text: reasonCov.text ? `reasons kept ${reasonCov.text}` : "this range" })),
    h("p", { class: "lead", text: "A normal answer: the part or result doesn't exist where it was looked for." }),
    ranked(nfRows, { total: nfRows.reduce((x, r) => x + r.value, 0), color: css("--o-not_found"), limit: 10, empty: nfTotal ? "No reasons recorded for these days." : "None." })));

  if (sc.before) {
    // one sentence instead of two boxes that each say "not in this range"
    split.append(h("div", {}, h("h3", { text: "Rejected arguments and failures" }),
      h("div", { class: "empty", text: `Counted ${sc.label}; this range ends before that.` })));
  } else {
    split.append(h("div", {}, h("h3", {}, "Failures", h("small", { text: period })),
      h("p", { class: "lead", text: "Something broke here or in a service we call." }),
      ranked(mergeSub(flat(p?.reasons, isFailureReason, reasonLabel)), { color: css("--critical"), empty: "None." })));
  }
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
  const sc = scope(view);
  const a = view.agg, p = view.problems;
  const period = sc.bites ? ` ${sc.short}` : "";
  sec.replaceChildren(cardHead(sec, "Services we call", "Requests the server sent to JLCPCB, LCSC, EasyEDA, SamacSys and DigiKey, and how they answered."));

  const sources = [...new Set([...Object.keys(a.upstream || {}), ...Object.keys(p?.upstream_status || {})])];
  const info = sources.map((src) => {
    const u = own(a.upstream, src) || {}, pu = own(p?.upstream, src) || {}, st = own(p?.upstream_status, src) || null;
    const tot = st ? sumObj(st) : 0;
    const errs = st ? STATUS_GROUPS.slice(2).map((g) => [g.label.toLowerCase(), g.keys.reduce((x, k) => x + (st[k] || 0), 0)]).filter(([, v]) => v > 0) : [];
    return { src, u, tot, errs, nErr: errs.reduce((x, [, v]) => x + v, 0), held: sc.before ? 0 : pu.rate_limited || 0, served: (u.sent || 0) + (u.cached || 0) };
  });
  // columns with nothing in them for this range stay out; a sentence under the table says so instead
  const hasHeld = info.some((r) => r.held), hasErr = !sc.before && info.some((r) => r.nErr);
  const rows = info.map((r) => h("tr", {},
    h("td", { class: "name", text: upstreamLabel(r.src), title: r.src }),
    h("td", { text: full(r.u.sent) }),
    h("td", {}, r.u.cached ? full(r.u.cached) : "", r.u.cached && r.served ? h("span", { class: "pct", text: percent(r.u.cached / r.served) }) : null),
    hasHeld ? h("td", { text: r.held ? full(r.held) : "" }) : null,
    hasErr ? h("td", { class: r.nErr ? "hot" : null, text: r.nErr ? `${full(r.nErr)} of ${full(r.tot)}: ${r.errs.map(([l, v]) => (r.errs.length > 1 ? `${l} ${full(v)}` : l)).join(", ")}` : "" }) : null));
  const cols = [
    ["Service", null], ["Requests sent", null], ["Answered from our cache instead", "opt-sm"],
    hasHeld && [`Held back by our own limits${period}`, "opt-sm"], hasErr && [`Error answers${period}`, null],
  ].filter(Boolean);
  if (rows.length) sec.append(table(cols.map((c) => c[0]), rows, { cls: cols.map((c) => c[1]) }));
  else sec.append(h("div", { class: "empty", text: "Requests to these services weren't counted yet in this range." }));

  const notes = h("div", { class: "chart-sub notes" });
  const cov = countedFrom(view, AMOUNT.upstream);
  if (rows.length && cov.text) {
    // a service whose own counting began later still (DigiKey's requests) is named with its date
    const later = sources.map((src) => [src, countedFrom(view, AMOUNT.upstreamOf(src))]).filter(([, c]) => c.start && c.start > cov.start && c.text);
    notes.append(h("span", { text: `Requests are counted ${cov.text}${later.map(([src, c]) => `; ${upstreamLabel(src)} ${c.text}`).join("")}.` }));
  }
  if (rows.length && !sc.before) {
    const none = [!hasErr && "no error answers", !hasHeld && "nothing held back by our own limits"].filter(Boolean);
    if (none.length) notes.append(h("span", { text: `${cap1(none.join(" and "))} ${sc.bites ? sc.label : "in this range"}.` }));
  }
  if (notes.children.length) sec.append(notes);

  const split = h("div", { class: "split", style: { marginTop: "22px" } });
  const reset = resetHour(view.asOf);
  for (const name of ["mouser", "digikey"]) {
    const d = own(a.distributors, name);
    if (!d) continue;
    const who = DISTRIBUTOR_LABEL[name];
    const lim = own(p?.distributor_limits, name);
    const held = Object.entries(lim?.held_back || {}).filter(([, n]) => n > 0);
    const refused = Object.entries(lim?.refusals || {}).filter(([, n]) => n > 0);
    const box = h("div", {}, h("h3", {}, `${who} lookups`, h("small", { text: "this range" })));
    // requests per lookup only where both were counted over the same days
    const http = name === "digikey" && !countedFrom(view, AMOUNT.upstreamOf("digikey")).text ? own(a.upstream, "digikey")?.sent : null;
    box.append(kv([
      ["Sent to " + who, full(d.sent)],
      http && d.sent && http >= d.sent ? ["Requests each one took, on average", (http / d.sent).toFixed(1)] : [null],
      ["Answered from saved answers instead", full(d.cached)],
      ["Not real part numbers, so not sent", d.skipped ? full(d.skipped) : null],
      sc.before ? [null] : [`Turned away by limits${period}`, held.length ? held.map(([c, n]) => `${full(n)}: ${heldBackLabel(c, who, reset)}`).join("; ") : "0"],
      refused.length ? [`${who} refused us${period}`, refused.map(([c, n]) => `${full(n)} (${refusedLabel(c)})`).join(", ")] : [null],
    ]));
    if (name === "mouser" && view.key === "today") box.append(mouserQuota(view));
    split.append(box);
  }
  const da = a.distributor_apps || {};
  const apps = new Map();
  for (const [tool, byApp] of Object.entries(da)) for (const [app, o] of Object.entries(byApp || {})) {
    const r = apps.get(app) || { app, total: 0 };
    r[tool] = (r[tool] || 0) + (o.calls || 0);
    r.total += o.calls || 0;
    apps.set(app, r);
  }
  if (apps.size) {
    const tools = Object.keys(da);
    const list = [...apps.values()].sort((x, y) => y.total - x.total).slice(0, 6);
    const appCov = countedFrom(view, AMOUNT.distributorApps);
    split.append(h("div", {}, h("h3", {}, "Which apps ask for them", h("small", { text: `tool calls, ${appCov.text ? `counted ${appCov.text}` : "this range"}` })), table(["App", ...tools.map((t) => TOOL_SHORT[t] || t)],
      list.map((r) => h("tr", {}, h("td", { class: "name", text: appName(r.app), title: r.app }), tools.map((t) => h("td", { text: r[t] ? full(r[t]) : "" })))))));
  }
  sec.append(split);
}

/** Mouser's daily budget, which runs on the server's day (7 PM to 7 PM Eastern), not the range. */
function mouserQuota(view) {
  const q = payload.health?.distributor_quota?.mouser;
  if (!q?.limit) return h("div");
  const used = q.used_today || 0, limit = q.limit;
  const sample = healthSample(view);
  if (!sample.currentDay || sample.retained) return h("div", { class: "chart-sub", text: `Last Mouser budget reading, ${sample.label}: ${full(used)} of ${full(limit)} used.${sample.currentDay ? " Health update failed or is behind the stats." : " Current budget unavailable; this reading predates the reset or has no timestamp."}` });
  const now = sample.at.getTime();
  const day = serverDay(sample.at);
  const frac = Math.min(1, Math.max(0.05, (now - day.start.getTime()) / 86400_000));
  const pace = used / frac;
  const scale = Math.max(limit, pace) * 1.05;
  const pct = (v) => `${Math.min(100, (v / scale) * 100)}%`;
  const text = `Daily budget checked ${sample.label}: ${full(used)} of ${full(limit)} used since ${dayHourET(day.start)}. At this pace about ${compact(pace)} by ${dayHourET(day.end)}, when it resets.`;
  return h("div", { class: "bullet", title: text },
    h("div", { class: "track" }, h("div", { class: "zone", style: { width: pct(limit) } }), h("div", { class: "fill", style: { width: pct(used) } }), h("div", { class: "pace", style: { left: pct(pace) } })),
    h("div", { class: "cap" }, h("span", { text })));
}

// ---------------------------------------------------------------- U6 limits and queues

function renderCapacity(view) {
  const sec = $("capacity");
  const sc = scope(view);
  const a = view.agg, p = view.problems;
  sec.replaceChildren(cardHead(sec, "Limits and queues", "How close the server came to its own limits."));
  const pr = p?.per_ip_refusals;
  const dw = a.db_waits, dl = a.datasheet_links, pdl = p?.datasheet_links;
  const period = sc.bites ? ` ${sc.short}` : "";
  // a counter the server began keeping after the range's first day says from when
  const from = (amount) => { const c = countedFrom(view, amount); return c.text ? ` (${c.text})` : ""; };
  const estimated = view.recs.some((r) => r.approx);
  const lines1 = [
    [`Requests turned away by the per-address limit${sc.before ? "" : period}`,
      sc.before ? `counted ${sc.short}` : pr?.total ? `${full(pr.total)}: ${["everyone_else", "platform_ranges", "too_many_clients"].filter((g) => pr[g]).map((g) => refusalGroupLabel(g)).join("; ")}` : "0"],
    dw?.jobs ? [`Database jobs that had to wait${from(AMOUNT.dbJobs)}`, `${full(dw.waited)} of ${full(dw.jobs)} (${percent(dw.waited / dw.jobs)})${dw.longest_ms == null ? "" : `, longest wait ${ms(dw.longest_ms)}`}`] : [null],
    dl ? [`Datasheet links opened${from(AMOUNT.datasheets)}`, full(dl.visits)] : [null],
    dl && !sc.before ? [`Datasheet links turned away or failed${period}`, `${full(pdl?.refused || 0)} turned away, ${full(pdl?.failed || 0)} failed`] : [null],
    // on days rebuilt from the server's 7 PM-to-7 PM totals a restart near the boundary can land a day off
    a.restarts != null ? [`Server restarts${from(AMOUNT.restarts)}`, `${estimated && a.restarts ? "about " : ""}${full(a.restarts)}`] : [null],
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

function renderEvents(view) {
  const sec = $("events");
  const sc = scope(view);
  // a log of recent history: it always runs up to today, and back 30 days or to the range's start
  const end = view.today;
  const back = addDays(end, -29);
  const start = view.dates[0] < back ? view.dates[0] : back;
  const first = view.days.find((d) => !d.partial_start)?.date;
  const from = first && first > start ? first : start;
  sec.replaceChildren(cardHead(sec, "Deploys, restarts and new apps",
    `${dayLabel(from)} to today${view.dates[0] < back ? "" : ", whatever range is selected"}.`));
  // the current version's record so far, from every day's problems part
  if (sc.from) {
    const all = view.days.map((d) => d.problems).filter(Boolean);
    if (all.length) {
      const agg = aggregate(all);
      const T = totals(agg);
      let held = 0;
      for (const lim of Object.values(agg.distributor_limits || {})) held += sumObj(lim?.held_back);
      const away = (agg.per_ip_refusals?.total || 0) + held + (agg.datasheet_links?.refused || 0);
      sec.append(h("p", { class: "lead" }, h("strong", { text: `${sc.ver || "The current version"} so far (${sc.short}): ` }),
        `${plural(T.calls, "call")}, ${full(T.failed)} failed, ${full(away)} turned away by limits, ${plural(T.bad_request, "rejected argument")}.`));
    }
  }
  // Versions, restarts and new apps are counted per server day (7 PM to 7 PM) with no hourly
  // detail: on a day rebuilt from those totals they can't be placed, so only exact days list them.
  // The current version's start is known to the minute (problems_since).
  const deployDay = sc.from ? partsET(sc.from).key : null;
  const firstVersion = Object.entries(view.seen.versions).filter(([v]) => v !== sc.ver);
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
    if (d === deployDay) tag("deploy", "◆", h("b", { text: sc.ver || "New version" }), ` went live, ${timeET(sc.from)}`);
    if (!rec.approx) {
      for (const [v, date] of firstVersion) if (date === d) tag("deploy", "◆", h("b", { text: v }), " first ran");
      if (rec.restarts) tag("info", "↻", plural(rec.restarts, "restart"));
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
  // Recheck quota freshness at the UTC reset even while a reload is stalled or offline.
  clearTimeout(dayTimer);
  const now = new Date(Date.now());
  dayTimer = setTimeout(render, serverDay(now).end.getTime() - now.getTime());
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
  $("footer-time").textContent = `All times are Eastern. A day here runs midnight to midnight; the server's own day, which its Mouser and DigiKey budgets and per-address allowances follow, ends at ${reset}.`;
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
