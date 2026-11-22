// A small DOM double exercises rendering and events without dependencies or network access.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";
import * as format from "../../src/pcbparts_dashboard/static/format.js";
import * as data from "../../src/pcbparts_dashboard/static/data.js";
import * as labels from "../../src/pcbparts_dashboard/static/labels.js";
import * as charts from "../../src/pcbparts_dashboard/static/charts.js";

class Element {
  constructor(tag = "div", text = "") {
    this.tagName = tag; this.childNodes = []; this.parentElement = null; this.attrs = {}; this.dataset = {};
    this.style = {}; this.listeners = {}; this._text = text; this.clientWidth = 600; this.offsetWidth = 120; this.offsetHeight = 60;
    this.classList = {
      contains: (c) => this.className.split(" ").includes(c),
      add: (...cs) => { this.className = [...new Set([...this.className.split(" ").filter(Boolean), ...cs])].join(" "); },
      remove: (c) => { this.className = this.className.split(" ").filter((s) => s !== c).join(" "); },
      toggle: (c, on = !this.classList.contains(c)) => on ? this.classList.add(c) : this.classList.remove(c),
    };
  }
  get id() { return this.attrs.id || ""; }
  set id(v) { this.attrs.id = v; }
  get className() { return this.attrs.class || ""; }
  set className(v) { this.attrs.class = v; }
  get tabIndex() { return this.attrs.tabindex == null ? -1 : +this.attrs.tabindex; }
  set tabIndex(v) { this.attrs.tabindex = String(v); }
  get children() { return this.childNodes.filter((e) => e.tagName !== "#text"); }
  get isConnected() { return this === document.body || !!this.parentElement?.isConnected; }
  get nextElementSibling() { const list = this.parentElement?.children || []; return list[list.indexOf(this) + 1]; }
  get textContent() { return this._text + this.childNodes.map((e) => e.textContent).join(""); }
  set textContent(v) { this.replaceChildren(); this._text = String(v); }
  setAttribute(k, v) {
    this.attrs[k] = String(v);
    if (k.startsWith("data-")) this.dataset[k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = String(v);
  }
  getAttribute(k) { return this.attrs[k] ?? null; }
  append(...els) {
    for (let el of els) {
      if (!(el instanceof Element)) el = new Element("#text", String(el));
      if (el.parentElement) el.remove();
      el.parentElement = this; this.childNodes.push(el);
    }
  }
  replaceChildren(...els) { for (const el of [...this.childNodes]) el.remove(); this._text = ""; this.append(...els); }
  contains(el) { return this === el || this.childNodes.some((c) => c.contains(el)); }
  remove() {
    if (this.contains(document.activeElement)) document.activeElement = document.body;
    if (this.parentElement) this.parentElement.childNodes = this.parentElement.childNodes.filter((c) => c !== this);
    this.parentElement = null;
  }
  after(el) { const p = this.parentElement; el.parentElement = p; p.childNodes.splice(p.childNodes.indexOf(this) + 1, 0, el); }
  matches(selector) {
    const m = /^([\w-]+)?(?:#([\w-]+))?(?:\.([\w-]+))?(?:\[([\w-]+)(?:="([^"]*)")?\])?$/.exec(selector);
    if (!m) throw Error(`Unsupported test selector: ${selector}`);
    return (!m[1] || this.tagName === m[1]) && (!m[2] || this.id === m[2]) && (!m[3] || this.classList.contains(m[3])) && (!m[4] || (this.getAttribute(m[4]) != null && (m[5] == null || this.getAttribute(m[4]) === m[5])));
  }
  querySelectorAll(selector) {
    const parts = selector.split(" ");
    const all = this.children.flatMap((e) => [e, ...e.querySelectorAll("*")]);
    if (selector === "*") return all;
    return all.filter((e) => e.matches(parts.at(-1)) && (parts.length === 1 || !!e.parentElement?.closest(parts[0])));
  }
  querySelector(s) { return this.querySelectorAll(s)[0] || null; }
  closest(s) { return this.matches(s) ? this : this.parentElement?.closest(s) || null; }
  addEventListener(type, fn) { (this.listeners[type] ??= []).push(fn); }
  dispatch(type, props = {}) {
    const e = { target: this, currentTarget: this, preventDefault() {}, ...props };
    for (const fn of this.listeners[type] || []) fn(e);
    this[`on${type}`]?.(e);
  }
  focus() { document.activeElement = this; this.dispatch("focus"); }
  getBoundingClientRect() { return { left: 0, top: 0, width: 600, height: 220 }; }
}

const source = readFileSync(new URL("../../src/pcbparts_dashboard/static/app.js", import.meta.url), "utf8");
const appCode = source.replace(/^import [\s\S]*? from "[^\n]+";\n/gm, "").split("\nreadHash();")[0];
const at = "2026-11-23T15:00:00Z";
function day(date, extra = {}) {
  return { date, start: date + "T05:00:00Z", complete: true, partial_start: false, partial_end: false, approx: false,
    hours: Array(24).fill(1), calls: 24, tools: { jlc_search: { calls: 24, ok: 24 } }, ...extra };
}
function payload(extra = {}) {
  return { generated_at: at, as_of: at, edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true })],
    last_fetch: { ok: true, at }, health_at: at, health: { status: "healthy", version: "0.10.5", distributor_quota: { mouser: { used_today: 80, limit: 1000 } } }, ...extra };
}
function setup(p = payload()) {
  const body = new Element("body");
  globalThis.document = { body, documentElement: new Element("html"), activeElement: body,
    createElement: (t) => new Element(t), createElementNS: (_, t) => new Element(t), createTextNode: (s) => new Element("#text", s),
    getElementById: (id) => [body, ...body.querySelectorAll("*")].find((e) => e.id === id) || null,
    querySelector: (s) => body.querySelector(s), querySelectorAll: (s) => body.querySelectorAll(s) };
  globalThis.Node = Element;
  globalThis.getComputedStyle = () => ({ getPropertyValue: () => "#cd7f32" });
  globalThis.innerWidth = 1200; globalThis.innerHeight = 900;
  for (const id of ["main", "boot", "app", "footer", "board-status", "led", "led-text", "fetch-state", "fetch-text", "refresh", "ranges", "range-text", "attention", "hero", "tiles", "traffic", "tools", "clients", "errors", "upstreams", "capacity", "search", "events", "footer-time", "footer-source", "tooltip"]) {
    const el = new Element(id === "refresh" ? "button" : "div"); el.id = id; body.append(el);
  }
  const frames = [];
  const timers = new Map();
  let now = Date.parse(p.generated_at), timerId = 0;
  class Clock extends Date { static now() { return now; } }
  const context = vm.createContext({ ...format, ...data, ...labels, ...charts, hourPoints: data.problemHours,
    document, Node: Element, getComputedStyle, innerWidth, innerHeight, Date: Clock, scrollY: 0, scrollTo() {},
    requestAnimationFrame: (fn) => frames.push(fn),
    setTimeout: (fn, delay = 0) => { const id = ++timerId; timers.set(id, { fn, at: now + delay }); return id; },
    clearTimeout: (id) => timers.delete(id),
    history: { replaceState() {} }, location: { hash: "" }, fetch: async () => { throw Error("offline"); } });
  vm.runInContext(appCode + "\nthis.api = { render, renderHeader, renderKpis, renderTraffic, renderTools, toolDetail, mouserQuota, attentionItems, scope, heatmap, refresh, load, setRange, state, setPayload: (p) => { payload = p; }, getError: () => loadError };", context);
  const api = context.api;
  api.setPayload(p);
  return { ...api, context, el: document.getElementById, flush: () => { while (frames.length) frames.shift()(); }, view: (key = "today") => data.buildView(p, key),
    setNow: (at) => { now = Date.parse(at); },
    runTimers: () => { for (const [id, timer] of [...timers]) if (timer.at <= now && timers.delete(id)) timer.fn(); } };
}

test("retained health is dated and a failed health fetch is visible despite successful stats", () => {
  const p = payload({ health_at: "2026-11-22T23:45:00Z", last_fetch: { ok: true, at, health_error: "health timed out" } });
  const app = setup(p);
  app.renderHeader();
  assert.equal(app.el("fetch-state").dataset.error, "true");
  assert.match(app.el("fetch-text").textContent, /health.*failed|health timed out/i);
  assert.match(app.el("board-status").textContent, /Nov 22.*6:45 PM/);
  assert.ok(app.attentionItems(app.view(), app.scope(app.view())).some((it) => /health/i.test(it.what)));
});

test("quota from before the UTC reset is not presented as today's usage or pace", () => {
  const app = setup(payload({ health_at: "2026-11-22T23:45:00Z", last_fetch: { ok: true, at, health_error: "timeout" } }));
  app.renderKpis(app.view());
  assert.doesNotMatch(app.el("tiles").textContent, /Mouser daily budget/);
  const quota = app.mouserQuota(app.view()).textContent;
  assert.match(quota, /Nov 22.*6:45 PM/);
  assert.doesNotMatch(quota, /At this pace|used since Mon/);
});

for (const trigger of ["failed reload", "HTTP failure", "failed refresh", "UTC rollover"]) test(`quota expires at midnight after ${trigger}`, async () => {
  const checked = "2026-11-23T23:59:00Z";
  const app = setup(payload({ generated_at: checked, as_of: checked, health_at: checked,
    last_fetch: { ok: true, at: checked },
    edays: [day("2026-11-23", { complete: false, partial_end: true, distributors: { mouser: { sent: 80 } } })] }));
  app.render(); app.flush();
  app.setNow("2026-11-23T23:59:59Z"); app.runTimers();
  assert.match(app.el("tiles").textContent, /Mouser daily budget/);
  assert.match(app.el("upstreams").textContent, /At this pace/);

  app.setNow("2026-11-24T00:00:00Z");
  if (trigger === "UTC rollover") app.runTimers();
  else if (trigger === "failed refresh") await app.refresh();
  else {
    if (trigger === "HTTP failure") app.context.fetch = async () => ({ ok: false, status: 503 });
    await app.load({ quiet: true });
  }
  app.flush();
  assert.doesNotMatch(app.el("tiles").textContent, /Mouser daily budget/);
  assert.doesNotMatch(app.el("upstreams").textContent, /At this pace/);
  assert.match(app.el("upstreams").textContent, /Last Mouser budget reading, Nov 23, 6:59 PM/);
  assert.match(app.el("upstreams").textContent, /Current budget unavailable/);
});

test("same-day retained quota is labelled with health_at, not the stats time", () => {
  const app = setup(payload({ health_at: "2026-11-23T14:00:00Z", last_fetch: { ok: true, at, health_error: "timeout" } }));
  app.renderKpis(app.view());
  assert.match(app.el("tiles").textContent, /9:00 AM/);
  assert.doesNotMatch(app.mouserQuota(app.view()).textContent, /At this pace/);
});

test("a manual refresh network failure stays visible and restores the button", async () => {
  const app = setup();
  await app.refresh();
  assert.match(app.getError() || "", /offline/);
  assert.equal(app.el("fetch-state").dataset.error, "true");
  assert.match(app.el("fetch-text").textContent, /refresh|offline/i);
  assert.equal(app.el("refresh").disabled, false);
});

test("range selection preserves keyboard focus and unchanged controls/history", () => {
  const app = setup(); app.render(); app.flush();
  const ranges = app.el("ranges").children;
  const yesterday = ranges.find((e) => e.textContent === "Yesterday");
  const history = app.el("events").children[0];
  yesterday.focus(); yesterday.dispatch("click"); app.flush();
  assert.equal(document.activeElement.textContent, "Yesterday");
  assert.equal(document.activeElement.getAttribute("aria-pressed"), "true");
  assert.equal(app.el("ranges").children[0], ranges[0]);
  assert.equal(app.el("events").children[0], history);
});

for (const selector of [".chart", ".tool-row", "th.sortable"]) test(`automatic redraw preserves focus on ${selector}`, () => {
  const app = setup(); app.render(); app.flush();
  const el = document.querySelector(selector); const label = el.getAttribute("aria-label") || el.textContent;
  el.focus(); app.render(); app.flush();
  assert.notEqual(document.activeElement, document.body);
  assert.equal(document.activeElement.getAttribute("aria-label") || document.activeElement.textContent, label);
});

test("redraw never moves focus away from a surviving control", () => {
  const app = setup(); app.render(); app.flush();
  app.el("refresh").focus(); app.render(); app.flush();
  assert.equal(document.activeElement, app.el("refresh"));
});

test("heatmap hourly values have keyboard labels, including the repeated DST hour", () => {
  const p = payload({ edays: [day("2026-11-01", { start: "2026-11-01T04:00:00Z", hours: Array.from({ length: 25 }, (_, i) => i + 1) })] });
  const app = setup(p); const heat = app.heatmap(app.view("all")); document.body.append(heat);
  const grid = heat.querySelector(".heat");
  assert.notEqual(grid.getAttribute("role"), "img");
  const cells = heat.querySelectorAll(".cell").filter((e) => e.dataset.ts);
  assert.ok(cells.length);
  for (const cell of cells) {
    assert.equal(cell.tabIndex, 0);
    assert.match(cell.getAttribute("aria-label"), /tool calls|no data/);
  }
  const repeated = cells.find((e) => +e.dataset.n === 2);
  assert.match(repeated.getAttribute("aria-label"), /5.*two hours.*clocks went back/);
  repeated.focus();
  assert.match(app.el("tooltip").textContent, /clocks went back/);
});

test("unsorted legacy replies are labelled in tool details", () => {
  const app = setup(payload({ edays: [day("2026-11-23", { tools: { jlc_search: { calls: 24, ok: 20, unsorted: 4 } } })] }));
  const detail = app.toolDetail(app.view(), "jlc_search");
  assert.match(detail.textContent, /Unsorted.*error replies from before 0\.6\.4.*4/);
});

test("latency tooltips describe individual intervals using payload bounds", () => {
  const app = setup(payload({ latency_bounds_ms: [50, 100, 1000, 60000], edays: [day("2026-11-23", { latency: { jlc_search: { counts: [1, 2, 3, 4, 5] } } })] }));
  const detail = app.toolDetail(app.view(), "jlc_search"); document.body.append(detail); app.flush();
  const chart = detail.querySelector(".chart");
  chart.onkeydown({ key: "ArrowRight", preventDefault() {} }); // last bucket
  for (let i = 0; i < 3; i++) chart.onkeydown({ key: "ArrowLeft", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /50–100 ms/);
  assert.doesNotMatch(app.el("tooltip").textContent, /within/);
  for (let i = 0; i < 3; i++) chart.onkeydown({ key: "ArrowRight", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /over 60 s/);
});

test("hover touches only the previous/current column and skips the same column", () => {
  const app = setup(); const container = new Element(); document.body.append(container);
  charts.columns(container, { points: Array.from({ length: 100 }, (_, i) => ({ title: String(i) })), series: [{ label: "calls", values: Array(100).fill(1), color: "red" }] });
  const groups = container.querySelectorAll("g").filter((e) => e.children.some((c) => c.tagName === "path"));
  let writes = 0;
  for (const g of groups) g.style = new Proxy({}, { set(o, k, v) { if (k === "filter") writes++; o[k] = v; return true; } });
  const hit = container.querySelector("svg").children.at(-1);
  hit.dispatch("pointermove", { clientX: 49, clientY: 20 });
  assert.equal(writes, 1);
  hit.dispatch("pointermove", { clientX: 50, clientY: 22 });
  assert.equal(writes, 1);
  hit.dispatch("pointermove", { clientX: 56, clientY: 22 });
  assert.equal(writes, 3);
  hit.dispatch("pointerleave");
  assert.equal(writes, 4);
});

test("deferred tool and app charts regain focus, without stealing a later choice", () => {
  const app = setup(payload({ edays: [day("2026-11-22", { latency: { jlc_search: { counts: [1, 2, 3] } } })] }));
  app.state.range = "yesterday"; app.state.open.add("jlc_search");
  app.render(); app.flush();
  const chart = document.querySelectorAll(".chart").find((e) => /response times/.test(e.getAttribute("aria-label")));
  chart.focus(); app.render(); app.flush();
  assert.equal(document.activeElement.id, chart.id);
  document.activeElement.focus(); app.render(); app.el("refresh").focus(); app.flush();
  assert.equal(document.activeElement, app.el("refresh"));

  app.setRange("7d"); app.flush();
  const apps = document.querySelectorAll(".chart").find((e) => /Sessions a day/.test(e.getAttribute("aria-label")));
  apps.focus(); app.render(); app.flush();
  assert.equal(document.activeElement.id, apps.id);
});

test("range-independent history is redrawn when a longer range reaches farther back", () => {
  const app = setup(); app.render(); app.flush();
  const recent = app.el("events").children[0];
  app.setRange("90d"); app.flush();
  assert.notEqual(app.el("events").children[0], recent);
});

test("heatmap and Table controls retain focus on a refreshed multi-day view", () => {
  const app = setup(); app.state.range = "30d"; app.render(); app.flush();
  for (const selector of [".cell", "#table-traffic"]) {
    const target = document.querySelector(selector); target.focus(); app.render(); app.flush();
    assert.equal(document.activeElement.id, target.id);
  }
});

test("fresh quota still shows its own timestamp and budget pace", () => {
  const app = setup(); app.renderKpis(app.view());
  assert.match(app.el("tiles").textContent, /Mouser daily budget80of 1,000Checked Nov 23, 10:00 AM/);
  assert.match(app.mouserQuota(app.view()).textContent, /At this pace/);
});

test("quota with an unknown timestamp, or a reset since the last stats, is never current", () => {
  for (const health_at of [null, "2026-11-22T23:45:00Z"]) {
    const app = setup(payload({ health_at, as_of: "2026-11-22T23:45:00Z" }));
    app.renderKpis(app.view());
    assert.doesNotMatch(app.el("tiles").textContent, /Mouser daily budget/);
    assert.doesNotMatch(app.mouserQuota(app.view()).textContent, /At this pace/);
  }
});

test("refresh HTTP failures are visible even before data has loaded", async () => {
  const app = setup(); app.setPayload(null);
  app.context.fetch = async () => ({ ok: false, status: 503, json: async () => ({}) });
  await app.refresh();
  assert.match(app.el("fetch-text").textContent, /Refresh failed.*503.*No numbers loaded/);
  assert.equal(app.el("refresh").disabled, false);
});

test("latency intervals follow a non-default final bound and label the first bucket", () => {
  const app = setup(payload({ latency_bounds_ms: [25, 75, 2000], edays: [day("2026-11-23", { latency: { jlc_search: { counts: [1, 2, 3, 4] } } })] }));
  const detail = app.toolDetail(app.view(), "jlc_search"); document.body.append(detail); app.flush();
  const chart = detail.querySelector(".chart");
  chart.onkeydown({ key: "ArrowRight", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /over 2 s/);
  for (let i = 0; i < 3; i++) chart.onkeydown({ key: "ArrowLeft", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /0–25 ms/);
});

test("overflow percentile labels use the final bound in seconds or milliseconds", () => {
  for (const [bound, label] of [[2000, "2 s"], [750, "750 ms"], [60000, "60 s"]]) {
    const bounds = [25, 75, bound];
    for (const p of [0.5, 0.95, 0.99]) {
      assert.equal(format.latencyText([0, 0, 0, 10], bounds, p), ">" + label);
      assert.equal(format.latencyText([0, 0, 10, 0], bounds, p), "≤" + label);
      assert.equal(format.latencyText([0, 0, 0, 0], bounds, p), "–");
    }
  }
});

test("overflow latency agrees across the headline, tool row, percentiles and tooltip", () => {
  const app = setup(payload({ latency_bounds_ms: [25, 75, 2000],
    edays: [day("2026-11-23", { latency: { jlc_search: { counts: [0, 0, 0, 10] } } })] }));
  app.render(); app.flush();
  assert.match(app.el("tiles").textContent, /95% answered within>2 s.*half within >2 s/);
  assert.match(app.el("tools").textContent, />2 s/);
  const detail = app.toolDetail(app.view(), "jlc_search"); document.body.append(detail); app.flush();
  assert.match(detail.textContent, /Half within >2 s, 95% within >2 s, 99% within >2 s/);
  detail.querySelector(".chart").onkeydown({ key: "ArrowRight", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /over 2 s/);
});

test("missing durations do not imply a fixed overflow bound", () => {
  assert.equal(format.ms(null), "–");
  assert.equal(format.ms(undefined), "–");
});

test("chart focus ids are stable, valid HTML ids derived from the chart label", () => {
  setup(); const container = new Element();
  charts.columns(container, { points: [{ title: "Today" }], series: [], ariaLabel: "Tool calls over the range" });
  assert.ok(container.id);
  assert.doesNotMatch(container.id, /\s/);
});

test("a table scrolled sideways keeps its position when a failed reload redraws the page", async () => {
  const app = setup(); app.render(); app.flush();
  const tools = () => document.getElementById("tools").querySelector(".table-wrap");
  tools().scrollLeft = 120;
  await app.load();
  app.flush();
  assert.equal(tools().scrollLeft, 120);
});
