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
/** A day whose counters are its whole day's, with the same ones as its part since the deploy. */
const whole = (problems, extra = {}) => ({ complete: false, ...problems, ...extra, problems });
// a Mouser lookup that failed: Mouser's error answers then cost a lookup, and are worth a look
const mouserLost = { tools: { jlc_search: { calls: 24, ok: 24 }, mouser_get_part: { calls: 1, failed: 1 } }, reasons: { mouser_get_part: { mouser_failed: 1 } } };
const digikeyLost = { tools: { jlc_search: { calls: 24, ok: 24 }, digikey_get_part: { calls: 1, failed: 1 } }, reasons: { digikey_get_part: { digikey_failed: 1 } } };
const notFailed = (items) => items.filter((it) => !it.key?.startsWith("failed:"));

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
  vm.runInContext(appCode + "\nthis.api = { render, renderHeader, renderKpis, renderTraffic, renderTools, renderAttention, renderEvents, renderCapacity, renderUpstreams, toolDetail, mouserQuota, attentionItems, scope, heatmap, refresh, load, setRange, state, dismissed, setPayload: (p) => { payload = p; }, getError: () => loadError, getView: () => currentView };", context);
  const api = context.api;
  api.setPayload(p);
  return { ...api, context, el: document.getElementById, flush: () => { while (frames.length) frames.shift()(); }, view: (key = "today") => data.buildView(p, key),
    setNow: (at) => { now = Date.parse(at); },
    runTimers: () => { for (const [id, timer] of [...timers]) if (timer.at <= now && timers.delete(id)) timer.fn(); } };
}

test("Mouser HTTP outcomes and retry counts load without a UI schema change", () => {
  const counts = { mouser: { "2xx": 10, "5xx": 3, connection: 1 } };
  const p = payload({ problems_since: "2026-11-23T05:00:00Z", edays: [day("2026-11-23", {
    complete: false, partial_end: true,
    distributors: { mouser: { sent: 14, cached: 2, rate_limited: 0, retries: 4 } },
    upstream_status: counts,
    problems: { start: "2026-11-23T05:00:00Z", end: at, upstream_status: counts },
  })] });
  const app = setup(p);
  app.render();
  assert.equal(app.view().agg.distributors.mouser.retries, 4);
  assert.equal(app.view().agg.upstream_status.mouser["5xx"], 3);
  assert.match(app.el("upstreams").textContent, /Mouser lookups/);
  assert.match(app.el("upstreams").textContent, /4 of 14/);
});

for (const [name, cause, level] of [
  ["mouser", "daily", "info"], ["mouser", "minute", "warning"], ["mouser", "refused", "warning"],
  ["digikey", "daily", "warning"], ["digikey", "minute", "warning"], ["digikey", "refused", "warning"],
]) test(`${name} ${cause} refusals are ${level}`, () => {
  const problems = { calls: 24, distributor_limits: { [name]: { refusals: { [cause]: 3 } } },
    ...(name === "mouser" && cause === "daily" ? { upstream_status: { mouser: { "429": 3 } } } : {}) };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems))] }));
  app.render();
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  assert.equal(items.length, 1);
  assert.equal(items[0].level, level);
  assert.match(items[0].what, /refused 3/);
  const attention = app.el("attention");
  assert.equal(attention.querySelector("li").dataset.level, level);
  if (level === "info") {
    assert.match(attention.textContent, /daily limit.*expected.*retry hourly or just after the next daily reset/i);
    assert.match(attention.querySelector(".clear").textContent, /Nothing: 24 calls, none failed, none turned away by limits/);
    assert.match(app.el("tiles").textContent, /Failed calls0/);
    assert.match(app.el("tiles").textContent, /Turned away by limits0/);
    assert.equal(app.el("led").hidden, true);
  } else assert.equal(attention.querySelector(".clear"), null);
});

for (const [daily, errors, warnings] of [[3, 6, 6], [3, 5, 5], [7, 3, 3]]) {
  test(`Mouser daily refusals ${daily} do not subtract from ${errors} HTTP 4xx errors`, () => {
    const problems = { distributor_limits: { mouser: { refusals: { daily } } },
      upstream_status: { mouser: { "2xx": 10, "4xx": errors } } };
    const app = setup(payload({ edays: [day("2026-11-23", whole(problems, mouserLost))] }));
    app.render();
    const items = app.attentionItems(app.view(), app.scope(app.view()));
    const warning = items.find((it) => it.what.startsWith("Mouser:"));
    if (warnings) {
      assert.equal(warning.what, `Mouser: ${warnings} of ${10 + errors} requests got an error answer.`);
      assert.match(warning.detail, new RegExp(`4xx answer ${warnings}; 1 lookup failed`));
    } else assert.equal(warning, undefined);
    const row = app.el("upstreams").querySelector('td[title="mouser"]').parentElement;
    assert.match(row.textContent, new RegExp(`${errors} of ${10 + errors}`));
    assert.equal(app.view().problems.upstream_status.mouser["4xx"], errors);
  });
}

for (const [otherStatus, st, bad, minute] of [
  [200, { "429": 3, "4xx": 3, "2xx": 3 }, 3, 0],
  [403, { "429": 3, "4xx": 6 }, 6, 0],
  [429, { "429": 6, "4xx": 3 }, 3, 3],
  [503, { "429": 3, "4xx": 3, "5xx": 3 }, 6, 0],
]) test(`Mouser daily refusals, unrelated 403s and HTTP ${otherStatus} keep distinct warnings`, () => {
  // Daily TooManyRequests bodies now count as 429 even when returned with HTTP 200/403/503.
  const problems = { distributor_limits: { mouser: { refusals: { daily: 3, minute } } },
    upstream_status: { mouser: st } };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems, mouserLost))] }));
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  const errors = items.filter((it) => it.what.startsWith("Mouser:"));
  assert.equal(errors.length, 1);
  assert.equal(errors[0].what, `Mouser: ${bad} of 9 requests got an error answer.`);
  assert.match(errors[0].detail, new RegExp(`4xx answer ${st["4xx"]}`));
  if (otherStatus === 503) assert.match(errors[0].detail, /5xx answer 3/);
  assert.equal(items.filter((it) => /daily limit/.test(it.what)).length, 1);
  assert.equal(items.filter((it) => /Mouser refused 3 requests for its per-minute limit/.test(it.what)).length, minute ? 1 : 0);
  assert.equal(app.view().problems.upstream_status.mouser["429"], st["429"]);
});

for (const [daily, counted429, errors4xx, errors5xx, expected] of [
  [3, 3, 0, 0, 0], [3, 3, 3, 0, 3], [3, 3, 0, 3, 3],
  [5, 3, 5, 0, 5], [3, 6, 3, 0, 3], [3, 0, 6, 0, 6],
]) test(`Mouser excludes only 429: ${daily} daily, ${counted429} at 429, ${errors4xx} at 4xx, ${errors5xx} at 5xx`, () => {
  const problems = { distributor_limits: { mouser: { refusals: { daily } } },
    upstream_status: { mouser: { "429": counted429, "4xx": errors4xx, "5xx": errors5xx } } };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems, mouserLost))] }));
  const warning = app.attentionItems(app.view(), app.scope(app.view())).find((it) => it.what.startsWith("Mouser:"));
  if (expected) assert.equal(warning.what, `Mouser: ${expected} of ${counted429 + errors4xx + errors5xx} requests got an error answer.`);
  else assert.equal(warning, undefined);
});

test("DigiKey 429 outcomes still contribute to HTTP warnings", () => {
  const problems = { upstream_status: { digikey: { "429": 3 } } };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems, digikeyLost))] }));
  assert.ok(app.attentionItems(app.view(), app.scope(app.view())).some((it) => it.what === "DigiKey API: 3 of 3 requests got an error answer."));
});

test("DigiKey HTTP warnings say plain DigiKey over unsplit days and count DigiKey's retries", () => {
  const status = { digikey: { "2xx": 10, "5xx": 6 } };
  const warning = (distributors) => {
    const problems = { upstream_status: status, distributors };
    const app = setup(payload({ edays: [day("2026-11-23", whole(problems, digikeyLost))] }));
    return app.attentionItems(app.view(), app.scope(app.view())).find((it) => it.what.includes("requests got an error answer"));
  };
  // split (server 0.10.11): the API's requests, with its retries
  let item = warning({ digikey: { sent: 12, retries: 2, ext_sent: 0 } });
  assert.equal(item.what, "DigiKey API: 6 of 16 requests got an error answer.");
  assert.match(item.detail, /; 2 were retries\.$/);
  item = warning({ digikey: { sent: 12, retries: 1, ext_sent: 0 } });
  assert.match(item.detail, /; 1 was a retry\.$/);
  // a problems window with unsplit lookups: one DigiKey figure, as in the services table
  item = warning({ digikey: { sent: 12 } });
  assert.equal(item.what, "DigiKey: 6 of 16 requests got an error answer.");
  assert.doesNotMatch(item.detail, /retr/);
});

const dkRow = (app, src) => app.el("upstreams").querySelector(`td[title="${src}"]`)?.parentElement || null;

test("DigiKey API and ext traffic are shown apart, with their HTTP outcomes", () => {
  const status = { digikey: { "2xx": 36 }, digikey_ext: { "2xx": 11, "5xx": 3 } };
  const app = setup(payload({ problems_since: "2026-11-23T05:00:00Z", edays: [day("2026-11-23", {
    complete: false, partial_end: true,
    distributors: { digikey: { sent: 30, cached: 4, rate_limited: 0, ext_sent: 12 } },
    upstream: { digikey: { sent: 36 }, digikey_ext: { sent: 14 } }, upstream_status: status,
    problems: { start: "2026-11-23T05:00:00Z", end: at, upstream_status: status },
  })] }));
  app.render();
  const api = dkRow(app, "digikey"), ext = dkRow(app, "digikey_ext");
  assert.equal(api.children[0].textContent, "DigiKey API");
  assert.equal(api.children[1].textContent, "36");
  assert.equal(ext.children[0].textContent, "DigiKey ext");
  assert.equal(ext.children[1].textContent, "14");
  assert.match(ext.textContent, /3 of 14/);
  const text = app.el("upstreams").textContent;
  assert.match(text, /Lookups sent to DigiKey30/);
  assert.match(text, /Through the API18/);
  assert.match(text, /Through ext12/);
  assert.match(text, /HTTP requests per API lookup2\.0/); // the API's 36 requests over its 18 lookups
  assert.doesNotMatch(text, /counted apart/);
  // no DigiKey lookup failed: the error answers are quiet, in the table only
  assert.match(ext.textContent, /3 of 14: 5xx answer; no lookup failed/);
  assert.equal(ext.children.at(-1).className, "zero");
  assert.ok(!app.attentionItems(app.view(), app.scope(app.view())).some((it) => it.what.includes("error answer")));
  const lost = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, ...digikeyLost,
    distributors: { digikey: { sent: 30, cached: 4, rate_limited: 0, ext_sent: 12 } },
    upstream: { digikey: { sent: 36 }, digikey_ext: { sent: 14 } }, upstream_status: status })] }));
  const items = lost.attentionItems(lost.view(), lost.scope(lost.view()));
  assert.ok(items.some((it) => it.what === "DigiKey ext: 3 of 14 requests got an error answer." && /5xx answer 3; 1 lookup failed\.$/.test(it.detail)));
  assert.ok(!items.some((it) => it.what.startsWith("DigiKey API:")));
  lost.render();
  assert.equal(dkRow(lost, "digikey_ext").children.at(-1).className, "hot");
});

test("days before the split keep one DigiKey figure, with no invented split", () => {
  const old = { distributors: { digikey: { sent: 40, cached: 2 } }, upstream: { digikey: { sent: 40 } } };
  const split = { distributors: { digikey: { sent: 30, cached: 0, ext_sent: 12 } },
    upstream: { digikey: { sent: 18 }, digikey_ext: { sent: 12 } } };
  const edays = [day("2026-11-20", old), day("2026-11-21", old), day("2026-11-22", split),
    day("2026-11-23", { complete: false, partial_end: true })];
  const app = setup(payload({ edays }));
  app.state.range = "all";
  app.render();
  let text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey"); // older days hold both paths' requests
  assert.equal(dkRow(app, "digikey").children[1].textContent, "98");
  assert.equal(dkRow(app, "digikey_ext").children[0].textContent, "DigiKey ext");
  assert.match(text, /DigiKey's API and ext requests are counted apart from Nov 22\./);
  assert.doesNotMatch(text, /DigiKey ext from/);
  assert.match(text, /Lookups sent to DigiKey110/);
  assert.match(text, /Through the API \(from Nov 22\)18/);
  assert.match(text, /Through ext \(from Nov 22\)12/);
  // the older days' requests and lookups both include ext's; the split day's API ones go together
  assert.match(text, /HTTP requests per lookup1\.0/); // not "API lookup": older days are unsplit

  app.state.range = "yesterday"; // the split day alone: no older figure, no note
  app.render();
  text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey API");
  assert.match(text, /Through the API18/);
  assert.match(text, /HTTP requests per API lookup1\.0/);
  assert.doesNotMatch(text, /counted apart|\(from /);

  const before = setup(payload({ edays: [day("2026-11-22", old), day("2026-11-23", { complete: false, partial_end: true })] }));
  before.state.range = "yesterday"; // only older days: exactly as before the split existed
  before.render();
  text = before.el("upstreams").textContent;
  assert.equal(dkRow(before, "digikey").children[0].textContent, "DigiKey");
  assert.equal(dkRow(before, "digikey_ext"), null);
  assert.match(text, /Lookups sent to DigiKey40/);
  assert.match(text, /HTTP requests per lookup1\.0/);
  assert.doesNotMatch(text, /Through the|ext/);
});

// The deploy day is unsplit (its lookups are only in sent), but its ext requests after the deploy
// already count under digikey_ext: that day's requests and lookups must still pair up.
const unsplitDeploy = { distributors: { digikey: { sent: 300, cached: 5 } },
  upstream: { digikey: { sent: 200 }, digikey_ext: { sent: 100 } } };
const olderDay = { distributors: { digikey: { sent: 40, cached: 2 } }, upstream: { digikey: { sent: 40 } } };
const splitDay = { distributors: { digikey: { sent: 30, cached: 0, ext_sent: 12 } },
  upstream: { digikey: { sent: 18 }, digikey_ext: { sent: 12 } } };

test("an unsplit day with ext requests alone keeps one lookup figure and pairs its requests", () => {
  const app = setup(payload({ edays: [day("2026-11-22", unsplitDeploy), day("2026-11-23", { complete: false, partial_end: true })] }));
  app.state.range = "yesterday";
  app.render();
  const text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey"); // it holds ext's requests before the deploy
  assert.equal(dkRow(app, "digikey").children[1].textContent, "200");
  assert.equal(dkRow(app, "digikey_ext").children[1].textContent, "100");
  assert.match(text, /Lookups sent to DigiKey300/);
  assert.match(text, /HTTP requests per lookup1\.0/); // 200 + 100 requests for 300 lookups
  assert.doesNotMatch(text, /Through the|API lookup/);
  assert.match(text, /DigiKey's API and ext requests are counted apart from Nov 22\./);
});

for (const range of ["7d", "all"]) test(`an unsplit day with ext requests in the ${range} range keeps requests per lookup`, () => {
  const edays = [...["2026-11-12", "2026-11-13", "2026-11-14", "2026-11-15", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20"]
    .map((d) => day(d, olderDay)), day("2026-11-21", unsplitDeploy), day("2026-11-22", splitDay),
    day("2026-11-23", { complete: false, partial_end: true })];
  const app = setup(payload({ edays }));
  app.state.range = range;
  app.render();
  const text = app.el("upstreams").textContent;
  const older = range === "7d" ? 5 : 9;
  assert.match(text, new RegExp(`Lookups sent to DigiKey${older * 40 + 330}`));
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey");
  assert.equal(dkRow(app, "digikey").children[1].textContent, String(older * 40 + 218));
  assert.equal(dkRow(app, "digikey_ext").children[1].textContent, "112");
  // older days 40/40, the deploy day (200 + 100)/300, the split day 18/18: 1.0, where adding the range's
  // requests and dividing by all but the split day's ext lookups gave less than one, so no figure
  assert.match(text, /HTTP requests per lookup1\.0/);
  assert.doesNotMatch(text, /API lookup/);
  assert.match(text, /Through the API \(from Nov 22\)18/);
  assert.match(text, /Through ext \(from Nov 22\)12/);
  // the ext row has requests from the deploy day, so the services note starts there
  assert.match(text, /DigiKey's API and ext requests are counted apart from Nov 21\./);
});

test("an ext row with nothing sent or answered from the cache still renders, without a dated note", () => {
  // its only counts are requests held back, so no day has any of its requests to date the split from
  const app = setup(payload({ edays: [day("2026-11-22", { distributors: { digikey: { sent: 20 } },
    upstream: { digikey: { sent: 20 }, digikey_ext: { rate_limited: 3 } } }),
  day("2026-11-23", { complete: false, partial_end: true })] }));
  app.state.range = "yesterday";
  app.render();
  const text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey_ext").children[1].textContent, "–"); // nothing sent
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey");
  assert.doesNotMatch(text, /counted apart/);
  assert.match(text, /DigiKey lookups/); // the rest of the section still rendered
});

test("a range without ext lookups shows no ext row or figure", () => {
  // ext's source can come through a re-cut day at zero
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true,
    distributors: { digikey: { sent: 20, cached: 1, ext_sent: 0 } },
    upstream: { digikey: { sent: 20 }, digikey_ext: { sent: 0, cached: 0 } },
    upstream_status: { digikey: { "2xx": 20 }, digikey_ext: {} } })] }));
  app.render();
  const text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey API");
  assert.equal(dkRow(app, "digikey_ext"), null);
  assert.match(text, /Lookups sent to DigiKey20/);
  assert.match(text, /HTTP requests per lookup1\.0/);
  assert.doesNotMatch(text, /Through the|ext/);
});

test("mixed Mouser refusals split daily info from warnings and keep held-back lookups visible", () => {
  const problems = { distributor_limits: {
    mouser: { refusals: { daily: 7, minute: 2, refused: 1 }, held_back: { distributor_daily: 4 } },
    digikey: { refusals: { daily: 5 } },
  } };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems))] }));
  app.render();
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  // one notice per cause, so each can be dismissed on its own
  assert.deepEqual([...items.map((it) => it.key)], ["held_back:mouser:distributor_daily", "refused:mouser:minute",
    "refused:mouser:refused", "refused:digikey:daily", "refused:mouser:daily"]);
  assert.ok(items.slice(0, -1).every((it) => it.level === "warning"));
  assert.equal(items.at(-1).level, "info");
  assert.match(items.at(-1).what, /Mouser refused 7 requests for its daily limit/);
  assert.equal(items[1].what, "Mouser refused 2 requests for its per-minute limit.");
  assert.equal(items[2].what, "Mouser refused 1 request with no reason given.");
  assert.equal(items[3].what, "DigiKey refused 5 requests for its daily limit (429).");
  assert.ok(items.some((it) => /4 Mouser lookups turned away by our limits/.test(it.what)));
  assert.match(app.el("tiles").textContent, /Turned away by limits4/);
  assert.equal(app.el("attention").querySelector(".clear"), null);
});

test("held-back labels keep address and DigiKey resets separate from Mouser's budget", () => {
  const distributors = { mouser: { sent: 0 }, digikey: { sent: 0 } };
  const problems = { distributor_limits: {
    mouser: { held_back: { daily_count: 2, address_daily: 1 } },
    digikey: { held_back: { daily_count: 1, address_blocked: 1 } },
  } };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems, { distributors }))] }));
  app.render();
  // the block list's holds are information, not a warning
  const blocked = app.attentionItems(app.view(), app.scope(app.view())).find((it) => it.key === "held_back:address_blocked");
  assert.equal(blocked.level, "info");
  assert.equal(blocked.what, "The blocked address tried 1 lookup, none sent.");
  for (const id of ["attention", "upstreams"]) {
    assert.match(app.el(id).textContent, /Mouser budget for the day ran out \(resets 1 AM\)/);
    assert.match(app.el(id).textContent, /address had used its daily allowance \(resets 7 PM\)/);
    assert.match(app.el(id).textContent, /DigiKey budget for the day ran out \(resets 7 PM\)/);
    assert.match(app.el(id).textContent, /address is on the server's block list/);
    assert.doesNotMatch(app.el(id).textContent, /block list \(resets/);
  }
});

test("Mouser HTTP errors and retries use the selected problems range and counting coverage", () => {
  const usage = (retries) => ({ distributors: { mouser: { sent: 100, retries } }, upstream_status: { mouser: { "2xx": 90, "5xx": 10 } } });
  const app = setup(payload({ problems_since: "2026-11-21T18:00:00Z", problems_version: "0.10.5", edays: [
    day("2026-11-20", { upstream: { jlcpcb: { sent: 50 } } }),
    day("2026-11-21", { ...usage(40), ...mouserLost, problems: { ...usage(2), start: "2026-11-21T18:00:00Z" } }),
    day("2026-11-22", { ...usage(50), ...mouserLost, problems: usage(3) }),
    day("2026-11-23", { ...usage(60), complete: false, problems: usage(60) }),
  ] }));
  app.state.range = "all";
  app.render();
  // the whole range counts, not only the part since the deploy; that part is said too
  const view = app.view("all"), items = notFailed(app.attentionItems(view, app.scope(view)));
  assert.equal(items.length, 1);
  assert.equal(items[0].what, "Mouser: 20 of 200 requests got an error answer.");
  assert.match(items[0].detail, /2 lookups failed; 90 were retries\.$/);
  assert.equal(items[0].since, "20 since 0.10.5");
  const row = app.el("upstreams").querySelector("td[title=\"mouser\"]").parentElement;
  assert.equal(row.children[0].textContent, "Mouser");
  assert.equal(row.children[1].textContent, "200");
  assert.match(row.textContent, /20 of 200/);
  assert.match(app.el("upstreams").textContent, /Mouser since Sat 1:00 PM/);
});

for (const retries of [undefined, null, 0, 1]) test(`Mouser error text handles retries=${retries}`, () => {
  const problems = { upstream_status: { mouser: { "5xx": 5 } },
    ...(retries === undefined ? {} : { distributors: { mouser: { retries } } }) };
  const app = setup(payload({ edays: [day("2026-11-23", whole(problems, mouserLost))] }));
  app.render();
  const [item] = notFailed(app.attentionItems(app.view(), app.scope(app.view())));
  assert.equal(item.what, "Mouser: 5 of 5 requests got an error answer.");
  if (retries) assert.match(item.detail, /1 was a retry\.$/);
  else assert.doesNotMatch(item.detail, /retr/);
});

test("pre-0.10.9 days need no Mouser HTTP outcomes or retry fields", () => {
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false,
    distributors: { mouser: { sent: 12 } }, problems: { calls: 24 },
  })] }));
  app.render();
  assert.equal(app.el("upstreams").querySelector("td[title=\"mouser\"]"), null);
  assert.match(app.el("upstreams").textContent, /Mouser lookups/);
  assert.match(app.el("attention").textContent, /Nothing: 24 calls/);
  assert.doesNotMatch(app.el("attention").textContent, /retr/);
});

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

for (const trigger of ["failed reload", "HTTP failure", "failed refresh", "Mouser rollover"]) test(`quota expires at 06:00 UTC after ${trigger}`, async () => {
  const checked = "2026-11-23T23:59:00Z";
  const app = setup(payload({ generated_at: checked, as_of: checked, health_at: checked,
    last_fetch: { ok: true, at: checked },
    edays: [day("2026-11-23", { complete: false, partial_end: true, distributors: { mouser: { sent: 80 } } })] }));
  app.render(); app.flush();
  app.setNow("2026-11-23T23:59:59Z"); app.runTimers();
  assert.match(app.el("tiles").textContent, /Mouser daily budget/);
  assert.match(app.el("upstreams").textContent, /At this pace/);

  app.setNow("2026-11-24T00:00:00Z");
  app.runTimers(); app.flush();
  assert.match(app.el("tiles").textContent, /Mouser daily budget/);
  assert.match(app.el("upstreams").textContent, /At this pace/);
  app.setNow("2026-11-24T05:59:59Z"); app.runTimers();
  assert.match(app.el("tiles").textContent, /Mouser daily budget/);
  app.setNow("2026-11-24T06:00:00Z");
  if (trigger === "Mouser rollover") app.runTimers();
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

test("fresh Mouser quota at 06:00 UTC uses the new day", () => {
  const checked = "2026-11-24T06:00:00Z";
  const app = setup(payload({ generated_at: checked, as_of: checked, health_at: checked,
    edays: [day("2026-11-24", { complete: false })] }));
  app.renderKpis(app.view());
  assert.match(app.el("tiles").textContent, /Mouser daily budget.*used since Tue 1 AM; resets Wed 1 AM/);
  assert.match(app.mouserQuota(app.view()).textContent, /used since Tue 1 AM.*by Wed 1 AM/);
});

for (const legacy of [false, true]) for (const paused of [false, true])
test(`${legacy ? "legacy health" : "collected private stats"} keeps budget, pace and pause notes (paused=${paused})`, () => {
  const checked = "2026-11-23T18:00:00Z";
  // The collector adds private counts to the public health entry before serving this payload.
  const quota = { used_today: 80, limit: 1000, paused_until: paused ? "2026-11-23 19:00 UTC" : null,
    ...(legacy ? {} : { api_remaining: null, kept_across_restarts: true, resets_at: "2026-11-24 06:00 UTC" }) };
  const app = setup(payload({ generated_at: checked, as_of: checked, health_at: checked,
    health: { status: "healthy", distributor_quota: { mouser: quota } },
    edays: [day("2026-11-23", { complete: false, distributors: { mouser: { sent: 500 } } })] }));
  app.render();
  assert.match(app.el("tiles").textContent, /Mouser daily budget80of 1,000/);
  assert.match(app.mouserQuota(app.view()).textContent, /80 of 1,000 used since Mon 1 AM.*At this pace about 160 by Tue 1 AM/);
  assert.equal(app.el("led-text").textContent.includes("Mouser paused"), paused);
});

test("public health without private quota counts keeps pause notes without inventing a budget", () => {
  const app = setup(payload({ health: { status: "healthy", distributor_quota: {
    mouser: { paused_until: "2026-11-23 16:00 UTC", resets_at: "2026-11-24 06:00 UTC" },
  } } }));
  app.render();
  assert.doesNotMatch(app.el("tiles").textContent, /Mouser daily budget/);
  assert.equal(app.mouserQuota(app.view()).textContent, "");
  assert.match(app.el("led-text").textContent, /Mouser paused/);
});

// expected: the header's DigiKey words, or null for none. Without ext's status the header can only
// say the API is paused, which is true with or without an extension.
for (const [name, digikey, expected] of [
  ["API paused, extension active", { paused_until: "2026-11-28 00:00 UTC", ext: { paused_until: null, active: true } }, null],
  ["API paused, extension not active (minute or 403 pause)", { paused_until: "2026-11-27 20:00 UTC", ext: { paused_until: null, active: false } }, "DigiKey paused"],
  ["API and extension both paused", { paused_until: "2026-11-28 00:00 UTC", ext: { paused_until: "2026-11-27 20:00 UTC", active: true } }, "DigiKey paused"],
  ["API paused, extension active but its pause hasn't ended", { paused_until: "2026-11-28 00:00 UTC", ext: { paused_until: "2026-11-23 15:30 UTC", active: true } }, "DigiKey paused"],
  ["API paused, extension active and its pause has ended", { paused_until: "2026-11-28 00:00 UTC", ext: { paused_until: "2026-11-23 14:00 UTC", active: true } }, null],
  ["API paused, no extension", { paused_until: "2026-11-28 00:00 UTC" }, "DigiKey API paused"],
  ["API paused, extension status unreadable (no active flag)", { paused_until: "2026-11-28 00:00 UTC", ext: { paused_until: null } }, "DigiKey API paused"],
  ["API pause has ended", { paused_until: "2026-11-23 14:59 UTC" }, null],
  ["API not paused, extension paused", { paused_until: null, ext: { paused_until: "2026-11-27 20:00 UTC", active: false } }, null],
  ["nothing paused", { paused_until: null, ext: { paused_until: null, active: false } }, null],
]) test(`DigiKey header pause: ${name}`, () => {
  const app = setup(payload({ health: { status: "healthy", distributor_quota: {
    digikey, mouser: { paused_until: "2026-11-23 16:00 UTC" },
  } } }));
  app.render();
  const text = app.el("led-text").textContent;
  assert.equal(text.match(/DigiKey( API)? paused/)?.[0] ?? null, expected);
  assert.match(text, /Mouser paused/);  // Mouser keeps its rule: any pause counts
});

test("a pause that ended before the clock reads now isn't shown, however old the sample", () => {
  const app = setup(payload({ health: { status: "healthy", distributor_quota: {
    mouser: { paused_until: "2026-11-23 14:00 UTC" }, digikey: { paused_until: "2026-11-23 16:00 UTC", ext: { active: false, paused_until: null } },
  } } }));
  app.render();
  assert.equal(app.el("led-text").textContent, "DigiKey paused");
  app.setNow("2026-11-23T16:00:01Z");
  app.render();
  assert.equal(app.el("led").hidden, true);
});

for (const [checked, dayDate, start, end] of [
  ["2026-11-23T18:00:00Z", "2026-11-23", "Mon 1 AM", "Tue 1 AM"],
  ["2026-07-04T18:00:00Z", "2026-07-04", "Sat 2 AM", "Sun 2 AM"],
]) test(`Mouser budget and pace use the 06:00 UTC day at ${checked}`, () => {
  const p = payload({ generated_at: checked, as_of: checked, health_at: checked,
    edays: [day(dayDate, { complete: false })] });
  const app = setup(p);
  app.render();
  assert.match(app.el("tiles").textContent, new RegExp(`used since ${start}; resets ${end}`));
  assert.match(app.mouserQuota(app.view()).textContent,
    new RegExp(`80 of 1,000 used since ${start}.*At this pace about 160 by ${end}`));
  assert.match(app.el("footer-time").textContent, new RegExp(`Mouser's budget resets at ${end.slice(4)}`));
});

test("same-day retained quota is labelled with health_at, not the stats time", () => {
  const app = setup(payload({ health_at: "2026-11-23T14:00:00Z", last_fetch: { ok: true, at, health_error: "timeout" } }));
  app.renderKpis(app.view());
  assert.match(app.el("tiles").textContent, /9:00 AM/);
  assert.doesNotMatch(app.mouserQuota(app.view()).textContent, /At this pace/);
});

for (const [hour, label, pace] of [[0, "7 PM", "107"], [9, "4 AM", "213"], [23, "6 PM", "101"]])
test(`configured Mouser hour ${hour} controls budget pace, reset labels and held-back explanations`, () => {
  const checked = "2026-11-23T18:00:00Z";
  const distributor_limits = {
    mouser: { held_back: { daily_count: 3 } }, digikey: { held_back: { daily_count: 2 } },
  };
  const p = payload({ generated_at: checked, as_of: checked, health_at: checked,
    health: { status: "healthy", distributor_quota: { mouser: { used_today: 80, limit: 1000,
      resets_at: `2026-11-${hour > 18 ? "23" : "24"} ${String(hour).padStart(2, "0")}:00 UTC` } } },
    edays: [day("2026-11-23", { complete: false, distributor_limits, problems: { distributor_limits },
      distributors: { mouser: { sent: 80 }, digikey: { sent: 10 } } })] });
  const app = setup(p);
  app.render();
  assert.match(app.el("tiles").textContent, new RegExp(`resets \\w+ ${label}`));
  assert.match(app.mouserQuota(app.view()).textContent, new RegExp(`At this pace about ${pace} by \\w+ ${label}`));
  assert.match(app.el("footer-time").textContent, new RegExp(`Mouser's budget resets at ${label}`));
  for (const id of ["attention", "upstreams"]) {
    assert.match(app.el(id).textContent, new RegExp(`Mouser budget for the day ran out \\(resets ${label}\\)`));
    assert.match(app.el(id).textContent, /DigiKey budget for the day ran out \(resets 7 PM\)/);
  }
});

test("configured Mouser reset controls retained sample freshness and scheduled redraws", () => {
  const checked = "2026-11-24T05:59:00Z";
  const p = payload({ generated_at: checked, as_of: checked, health_at: checked,
    health: { distributor_quota: { mouser: { used_today: 80, limit: 1000, resets_at: "2026-11-24 09:00 UTC" } } } });
  const app = setup(p);
  app.render(); app.flush();
  app.setNow("2026-11-24T06:00:00Z"); app.runTimers(); app.flush();
  assert.match(app.el("tiles").textContent, /Mouser daily budget/);
  app.setNow("2026-11-24T09:00:00Z"); app.runTimers(); app.flush();
  assert.doesNotMatch(app.el("tiles").textContent, /Mouser daily budget/);
  assert.match(app.mouserQuota(app.view()).textContent, /Current budget unavailable/);
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
  assert.match(app.el("tiles").textContent, /Mouser daily budget80of 1,000Key in use\. Checked Nov 23, 10:00 AM/);
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

// ---------------------------------------------------------------- 0.10.12: whole-range history and dismissals

const tick = () => new Promise((resolve) => setImmediate(resolve));
const refusals = (n, extra = {}) => ({ per_ip_refusals: { total: n, everyone_else: n }, ...extra });

/** A backend double for /api/data and /api/dismissals; `calls` records what the page sent. */
function backend(app, p, { refuse = null } = {}) {
  const calls = [];
  let stored = [];
  app.context.fetch = async (url, opts = {}) => {
    calls.push({ url, method: opts.method || "GET", headers: opts.headers || {}, body: opts.body ? JSON.parse(opts.body) : null });
    if (url.startsWith("/api/dismissals")) {
      if (refuse && opts.method) return { ok: false, status: 403, json: async () => ({ error: refuse }) };
      if (opts.method === "POST") { const b = JSON.parse(opts.body); stored = [...stored.filter((d) => d.key !== b.key), { ...b, at }]; }
      if (opts.method === "DELETE") { const key = decodeURIComponent(url.split("key=")[1]); stored = stored.filter((d) => d.key !== key); }
      return { ok: true, status: 200, json: async () => ({ dismissals: stored }) };
    }
    if (url === "/api/data") return { ok: true, status: 200, json: async () => p.current };
    throw Error(`unexpected ${url}`);
  };
  return calls;
}

test("a dismissed notice stays hidden until its count grows, and can be undone or restored", async () => {
  const data = (n) => payload({ edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true, ...refusals(n) })] });
  const p = { current: data(852) };
  const app = setup(p.current);
  const calls = backend(app, p);
  await app.load();
  const box = app.el("attention");
  const notices = () => box.querySelectorAll("li").filter((li) => !li.parentElement.classList.contains("dismissed"));
  assert.match(notices()[0].textContent, /852 requests turned away by our per-address limit/);
  notices()[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  const post = calls.find((c) => c.method === "POST");
  assert.deepEqual({ ...post.body }, { key: "per_ip_refusals", count: 852, day: "2026-11-23" });
  assert.equal(post.headers["X-Dashboard-Request"], "1");
  assert.equal(post.headers["Content-Type"], "application/json");
  assert.equal(notices().length, 0);
  assert.match(box.textContent, /Nothing new since the notice here was dismissed\./);
  assert.match(box.querySelector("p.undo").textContent, /Dismissed: 852 requests/);
  assert.equal(document.activeElement.id, "undo-dismiss");

  // undo: a first dismissal is removed again
  app.el("undo-dismiss").dispatch("click");
  await tick();
  assert.equal(calls.at(-1).method, "DELETE");
  assert.equal(calls.at(-1).url, "/api/dismissals?key=per_ip_refusals");
  assert.equal(notices().length, 1);

  // dismissed again, then the next reload holds the same count: still hidden; a bigger one brings it back
  notices()[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  await app.load();
  assert.equal(notices().length, 0);
  assert.equal(app.dismissed.get("per_ip_refusals").count, 852);
  p.current = data(900);
  await app.load();
  assert.match(notices()[0].textContent, /900 requests/);

  // "Show dismissed" lists what is hidden, with a way back
  p.current = data(852);
  await app.load();
  app.el("show-dismissed").dispatch("click");
  const hidden = box.querySelector("ul.dismissed").querySelectorAll("li");
  assert.equal(hidden.length, 1);
  assert.equal(hidden[0].querySelector("button.dismiss").textContent, "Restore");
  hidden[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  assert.equal(calls.at(-1).method, "DELETE");
  assert.equal(notices().length, 1);
});

test("a dismissal the server refuses is undone on the page and said", async () => {
  const p = { current: payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, ...refusals(5) })] }) };
  const app = setup(p.current);
  backend(app, p, { refuse: "Missing X-Dashboard-Request header" });
  await app.load();
  app.el("attention").querySelector("button.dismiss").dispatch("click");
  await tick();
  assert.match(app.el("attention").querySelector("li").textContent, /5 requests turned away/);
  assert.match(app.el("attention").textContent, /Couldn't save that \(Missing X-Dashboard-Request header\)/);
  assert.equal(app.el("attention").querySelector("p.undo"), null);
});

test("every count-based notice has a stable key, and live state has none", () => {
  const app = setup(payload({ kept_across_restarts: false, last_fetch: { ok: true, at, health_error: "timed out" }, edays: [day("2026-11-23", {
    complete: false, partial_end: true, ...refusals(3),
    tools: { cse_get_kicad: { calls: 10, ok: 7, failed: 3 } }, reasons: { cse_get_kicad: { cse_lookup_failed: 3 } },
    distributor_limits: { digikey: { held_back: { distributor_refused: 2, address_blocked: 4 } } },
    lcsc_lookups: { jlc_get_part: { fallback: 2 } }, datasheet_links: { visits: 9, refused: 1 },
  })] }));
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  assert.deepEqual([...items.map((it) => it.key ?? null)], ["failed:cse_get_kicad:cse_lookup_failed", null, null,
    "per_ip_refusals", "held_back:digikey:distributor_refused", "datasheet:refused", "held_back:address_blocked", "lcsc:jlc_get_part:fallback"]);
  assert.equal(items[0].what, "3 cse_get_kicad calls failed: SamacSys search failed.");
  assert.match(items[2].what, /stats aren't kept across restarts/); // live state: it clears itself
  // each keyed notice's count is the one the dismissal rule counts with
  const counts = app.context.eventCounts(app.view().agg, app.view().recs);
  for (const it of items.filter((x) => x.key && !x.key.startsWith("warning:"))) assert.equal(counts.get(it.key), it.count, it.key);
  app.render();
  assert.equal(app.el("attention").querySelectorAll("li")[2].querySelector("button.dismiss"), null);
  assert.equal(items.at(-1).level, "info");
  assert.match(items.at(-1).what, /2 live stock lookups in jlc_get_part answered from the daily snapshot/);
});

test("counts cover the whole range and say how many came since a deploy inside it", () => {
  const since = "2026-11-23T12:00:00Z";
  const app = setup(payload({ problems_since: since, problems_version: "0.10.12", edays: [day("2026-11-22"), day("2026-11-23", {
    complete: false, partial_end: true, ...refusals(10), tools: { jlc_search: { calls: 24, ok: 20, failed: 4 } },
    problems: { start: since, ...refusals(2), tools: { jlc_search: { calls: 10, ok: 9, failed: 1 } } },
  })] }));
  app.render();
  const tiles = app.el("tiles").textContent;
  assert.match(tiles, /Failed calls4[^]*1 since 0\.10\.12/);
  assert.match(tiles, /Turned away by limits10[^]*2 since 0\.10\.12/);
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  assert.equal(items.find((it) => it.key === "per_ip_refusals").since, "2 since 0.10.12");
  assert.match(app.el("attention").textContent, /“since 0\.10\.12” counts start at 7:00 AM/);
  // yesterday ends before the deploy: whole-range counts, no "since"
  app.setRange("yesterday");
  assert.doesNotMatch(app.el("tiles").textContent, /since 0\.10\.12/);
});

test("request refusals name their addresses when the server counts them", () => {
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true,
    ...refusals(852, { addresses: { rate_limited: 1, cap_reached: 0, blocked_tried: 0 } }) })] }));
  app.render();
  assert.match(app.el("attention").textContent, /852 requests from 1 address turned away by our per-address limit/);
  assert.match(app.el("capacity").textContent, /852 from 1 address: over the per-address limit for a minute/);
  const older = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, ...refusals(852) })] }));
  older.render();
  assert.match(older.el("attention").textContent, /852 requests turned away/);
  assert.doesNotMatch(older.el("attention").textContent, /from \d+ address|an address sent/);
});

for (const n of [1, 4]) test(`Mouser budgets: ${n} in the list, the key in use first, pace for the whole pool`, () => {
  const budgets = Array.from({ length: n }, (_, i) => ({ used_today: i < n - 1 ? 1000 : 80, limit: 1000, api_remaining: null,
    paused_until: null, in_use: i === n - 1 }));
  const app = setup(payload({ health: { status: "healthy", distributor_quota: { mouser: {
    used_today: 80, limit: 1000, resets_at: "2026-11-24 06:00 UTC", budgets } } } }));
  app.render();
  const tile = app.el("tiles").children[7];
  assert.match(tile.textContent, new RegExp(`Mouser daily budget80of 1,000Key in use${n > 1 ? ` \\(budget ${n} of ${n}\\)` : ""}\\. Checked`));
  const rows = tile.querySelectorAll("li");
  assert.equal(rows.length, n > 1 ? n : 0);
  if (n > 1) {
    assert.match(rows[0].textContent, new RegExp(`budget 1 of ${n}1,000 of 1,000spent`));
    assert.equal(rows.at(-1).dataset.state, "in-use");
    assert.match(rows.at(-1).textContent, /in use/);
  }
  // 9 of Mouser's 24 hours have gone by: the pool's pace, never one budget's
  const used = (n - 1) * 1000 + 80, limit = n * 1000;
  assert.match(app.mouserQuota(app.view()).textContent, new RegExp(`${n > 1 ? "every budget together, " : ""}checked .*: ${format.full(used)} of ${format.full(limit)} used since Mon 1 AM\\. At this pace about ${format.compact(used / 0.375)}`));
});

for (const n of [1, 3]) test(`DigiKey now: ext answering, API answering or paused, with ${n} budget(s)`, () => {
  const budget = (used, inUse) => ({ used_today: used, limit: 1000, api_remaining: 1000 - used, paused_until: null, in_use: inUse });
  const state = (digikey, limits) => {
    const app = setup(payload({ health: { status: "healthy", distributor_quota: { digikey } },
      edays: [day("2026-11-23", { complete: false, partial_end: true, distributor_limits: { digikey: limits || {} } })] }));
    app.render();
    return app.el("tiles").children[8];
  };
  const spent = Array.from({ length: n }, (_, i) => budget(1000, i === n - 1));
  let tile = state({ used_today: 1000, limit: 1000, paused_until: "2026-11-24 00:00 UTC", resets_at: "2026-11-24 00:00 UTC", budgets: spent,
    ext: { active: true, paused_until: null, active_since: "2026-11-23 13:05 UTC" } },
  { held_back: { address_daily: 4 }, ext_held_back: { address_daily: 1 }, refusals: { refused: 2 }, ext_refusals: { refused: 2 } });
  assert.match(tile.textContent, /DigiKey nowext answeringSince 8:05 AM; API day spent, resets 7 PM\. Checked/);
  assert.match(tile.textContent, /Today, turned away: API 3, ext 1; refused: API 0, ext 2/);
  assert.equal(tile.querySelectorAll("li").length, n > 1 ? n : 0);
  const fresh = Array.from({ length: n }, (_, i) => budget(i ? 0 : 400, i === 0));
  tile = state({ used_today: 400, limit: 1000, paused_until: null, budgets: fresh, ext: { active: false, paused_until: null } });
  assert.match(tile.textContent, new RegExp(`API answering${format.full(n * 1000 - 400)} of the day's ${format.full(n * 1000)} requests left; resets 7 PM`));
  tile = state({ used_today: 10, limit: 1000, paused_until: "2026-11-23 15:10 UTC", budgets: fresh, ext: { active: false, paused_until: null } });
  assert.match(tile.textContent, /Paused.*Until 10:10 AM; ext not in use/);
  tile = state({ used_today: 10, limit: 1000, paused_until: "2026-11-23 15:10 UTC" });
  assert.match(tile.textContent, /API paused.*Until 10:10 AM\./);
});

test("server starts: the deploy's exact time, restarts tagged, counted since midnight", () => {
  const starts = [{ at: "2026-11-23T07:10:00Z", version: "0.10.11" }, { at: "2026-11-23T12:30:00Z", version: "0.10.12" }, { at: "2026-11-23T14:00:00Z", version: "0.10.12" }];
  const app = setup(payload({
    health: { status: "healthy", version: "0.10.12", snapshot: { data_as_of: "2026-11-23T06:52:00Z" } },
    versions: [{ version: "0.10.11", from: "2026-11-20T10:00:00Z", exact: false, to: "2026-11-23T12:30:00Z" },
      { version: "0.10.12", from: "2026-11-23T12:30:00Z", exact: true, to: null, calls: 2000, failed: 3, rejected: 5, turned_away: 0, latency: [10, 5, 1], approx: false }],
    catalog_changes: [{ before: "2026-11-23T06:00:00Z", at: "2026-11-23T08:00:00Z", data_as_of: "2026-11-23T06:52:00Z" }],
    edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true, restarts: 3, starts, starts_complete: true })],
  }));
  app.render();
  assert.match(app.el("board-status").textContent, /Server 0\.10\.12 since Mon 7:30 AM/);
  const today = app.el("events").querySelectorAll("li").find((li) => /Nov 23/.test(li.textContent)).textContent;
  assert.match(today, /◆0\.10\.12 went live 7:30 AM/);
  assert.match(today, /↻2:10 AM restart, catalog update/);
  assert.match(today, /↻9:00 AM restart(?!,)/);
  assert.match(app.el("capacity").textContent, /Server restarts since midnight3/);
  // the version scorecard
  const card = app.el("events").querySelector(".scorecard").textContent;
  assert.match(card, /0\.10\.12Mon 7:30 AM, running/);
  assert.match(card, /3 h2,0001\.550250 ms/); // calls, failed per 1,000, rejected, turned away, 95% within
});

test("without listed starts a deploy is placed between the dashboard's checks", () => {
  const app = setup(payload({
    health: { status: "healthy", version: "0.10.11" }, problems_since: "2026-11-23T11:00:00Z", problems_version: "0.10.11",
    version_since: { version: "0.10.11", since: "2026-11-23T11:00:00Z", first_seen: "2026-11-23T12:00:00Z", configured: false },
    versions: [{ version: "0.10.10", from: "2026-11-21T10:00:00Z", exact: false, to: "2026-11-23T12:00:00Z" },
      { version: "0.10.11", from: "2026-11-23T12:00:00Z", exact: false, to: null }],
    edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true, restarts: 2 })],
  }));
  app.render();
  assert.match(app.el("board-status").textContent, /Server 0\.10\.11 started between Mon 6:00 AM and 7:00 AM/);
  assert.match(app.el("events").textContent, /◆0\.10\.11 went live between 6:00 AM and 7:00 AM/);
  assert.match(app.el("events").textContent, /↻2 restarts/);
  assert.match(app.el("capacity").textContent, /Server restarts since midnight2/);
});

test("services: resends, quiet error answers, 3xx as an error, saved answers and slot waits", () => {
  const app = setup(payload({ health: { status: "healthy", distributor_stored: { answers: 21714 } }, edays: [day("2026-11-23", {
    complete: false, partial_end: true,
    upstream: { jlcpcb: { sent: 100, retries: 3, cached: 0, waited: 12 }, digikey: { sent: 11 } },
    upstream_status: { jlcpcb: { "2xx": 100 }, digikey: { "2xx": 10, "3xx": 1 } },
    distributors: { mouser: { sent: 545, cached: 546, retries: 2, rate_limited: 0 }, digikey: { sent: 10, cached: 4, ext_sent: 0 } },
    parts_asked: { mouser: { total: 9069 }, digikey: { total: 14 } },
    distributor_apps: { mouser_get_part: { alpha: { calls: 10, rate_limited: 3 } } },
  })] }));
  app.render();
  const text = app.el("upstreams").textContent;
  assert.equal(app.el("upstreams").querySelectorAll("th")[2].textContent, "Resent");
  assert.equal(dkRow(app, "jlcpcb").children[2].textContent, "3");
  assert.match(dkRow(app, "digikey").textContent, /1 of 11: 3xx answer; no lookup failed/);
  assert.match(text, /Requests sent to Mouser545/);
  assert.match(text, /Part numbers asked9,069/);
  assert.match(text, /Lookups answered wholly from saved answers546 \(at least 50% of lookups\)/);
  assert.match(text, /Answered from saved answers4 \(29% of part numbers asked\)/);
  assert.match(text, /The server keeps 21,714 saved Mouser and DigiKey answers/);
  assert.match(text, /AppMouserTurned awayalpha103/); // turned away, per app
  assert.match(app.el("capacity").textContent, /Requests that waited for a free request slotJLCPCB parts search 12/);
  assert.doesNotMatch(text, /cache\b|Held back|rejected our request|Answered from our/);
  const quiet = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, upstream: { jlcpcb: { sent: 5, retries: 0 } } })] }));
  quiet.render();
  assert.ok(!quiet.el("upstreams").querySelectorAll("th").some((th) => th.textContent === "Resent"));
});

test("headline tiles: biggest app by tool calls, sessions without a per-session ratio", () => {
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, apps: { alpha: 2, beta: 30, gamma: 5 },
    tool_apps: { jlc_search: { alpha: { calls: 20, ok: 20 }, beta: { calls: 4, ok: 4 } } } })] }));
  app.render();
  const tiles = app.el("tiles").textContent;
  assert.match(tiles, /Biggest appalpha83% of tool calls; 2 sessions/);
  assert.match(tiles, /Sessions started37one each time an app connects/);
  assert.doesNotMatch(tiles, /tool calls a session/);
  // apps that connected without calling a tool are one row
  const rows = app.el("clients").querySelectorAll("tr");
  assert.ok(rows.some((tr) => tr.textContent.startsWith("1 app that called no tool5")));
  assert.ok(!rows.some((tr) => tr.children[0]?.textContent === "gamma"));
});

test("the header shows the health time only when it differs from the update time", () => {
  const same = setup(payload());
  same.render();
  assert.doesNotMatch(same.el("board-status").textContent, /Health values from/);
  const older = setup(payload({ health_at: "2026-11-23T14:00:00Z" }));
  older.render();
  assert.match(older.el("board-status").textContent, /Health values from Nov 23, 9:00 AM/);
});

test("limits: datasheet links not found, the AI platform list's age, stats not kept", () => {
  const app = setup(payload({ kept_across_restarts: false,
    health: { status: "healthy", platform_ranges: { anthropic: 2, openai: 289, openai_list_created: "2026-11-06T18:26:55.215535" } },
    edays: [day("2026-11-23", { complete: false, partial_end: true, datasheet_links: { visits: 631, not_found: 7, refused: 0, failed: 0 } })] }));
  app.render();
  const text = app.el("capacity").textContent;
  assert.match(text, /Datasheet links opened631; 7 not found/);
  assert.match(text, /Anthropic 2, OpenAI 289; OpenAI's list from Nov 6 \(16 days old\)/);
  assert.match(text, /Stats kept across restartsNo/);
  assert.match(app.el("attention").textContent, /The server's stats aren't kept across restarts/);
});

test("DigiKey refusals say the 403 and the pause, not the cause twice", () => {
  const app = setup(payload({ edays: [day("2026-11-23", whole({ distributor_limits: { digikey: { refusals: { refused: 7 } } } },
    { distributors: { digikey: { sent: 20, cached: 0 } } }))] }));
  const [item] = app.attentionItems(app.view(), app.scope(app.view()));
  assert.equal(item.what, "DigiKey refused 7 requests (403); each refusal paused lookups for 10 minutes.");
  app.render();
  assert.match(app.el("upstreams").textContent, /DigiKey refused us7: refused \(403\), paused 10 minutes/);
});

// ---------------------------------------------------------------- review fixes: dismissals over time

const liveNotices = (app) => app.el("attention").querySelectorAll("li").filter((li) => !li.parentElement.classList.contains("dismissed"));

test("a dismissal hides what happened before it: the next day's events come back, the dismissed day's don't", async () => {
  const p = { current: payload({ edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true, ...refusals(852) })] }) };
  const app = setup(p.current);
  backend(app, p);
  await app.load();
  liveNotices(app)[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  assert.equal(liveNotices(app).length, 0);
  // the next day: 10 new refusals today
  const at2 = "2026-11-24T15:00:00Z";
  p.current = payload({ generated_at: at2, as_of: at2, health_at: at2, last_fetch: { ok: true, at: at2 }, edays: [day("2026-11-22"),
    day("2026-11-23", refusals(852)), day("2026-11-24", { complete: false, partial_end: true, ...refusals(10) })] });
  app.setNow(at2);
  await app.load();
  assert.match(liveNotices(app)[0].textContent, /^10 requests turned away/);
  // yesterday's 852 were all there when it was dismissed: still hidden there
  app.setRange("yesterday");
  assert.equal(liveNotices(app).length, 0);
  // a range holding both days shows it again, for the new ones
  assert.ok(app.context.newSinceDismissed("per_ip_refusals", app.dismissed.get("per_ip_refusals"), app.context.buildView({ ...p.current }, "today")) === 10);
});

test("a dismissal made on a longer range counts from the data's own day, not from the range's count", async () => {
  const days = ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21", "2026-11-22"].map((d) => day(d, refusals(100)));
  const p = { current: payload({ edays: [...days, day("2026-11-23", { complete: false, partial_end: true, ...refusals(5) })] }) };
  const app = setup(p.current);
  backend(app, p);
  app.state.range = "7d";
  await app.load();
  assert.match(liveNotices(app)[0].textContent, /^700 requests/);
  liveNotices(app)[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  assert.equal(app.dismissed.get("per_ip_refusals").count, 5); // today's 5 were already there
  assert.equal(app.dismissed.get("per_ip_refusals").day, "2026-11-23");
  app.setRange("today");
  assert.equal(liveNotices(app).length, 0);
  p.current = payload({ edays: [...days, day("2026-11-23", { complete: false, partial_end: true, ...refusals(7) })] });
  await app.load();
  assert.match(liveNotices(app)[0].textContent, /^7 requests/); // 2 more since: back, with the range's count
});

test("restoring a notice, or hiding an emptied dismissed list, keeps the keyboard focus on the page", async () => {
  const p = { current: payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, ...refusals(5) })] }) };
  const app = setup(p.current);
  backend(app, p);
  await app.load();
  liveNotices(app)[0].querySelector("button.dismiss").dispatch("click");
  await tick();
  app.el("show-dismissed").dispatch("click");
  const restore = app.el("attention").querySelector("ul.dismissed").querySelector("button.dismiss");
  restore.focus();
  restore.dispatch("click");
  await tick();
  assert.equal(document.activeElement.id, "notice-per_ip_refusals");
  assert.equal(document.activeElement.textContent, "Dismiss");
  app.el("show-dismissed").dispatch("click"); // "Hide dismissed": with nothing dismissed, the button goes
  assert.equal(app.el("show-dismissed"), null);
  assert.equal(document.activeElement.id, "attention-head");
});

// ---------------------------------------------------------------- review fixes: addresses, paths, rollbacks

test("addresses are unknown on a day that began on an older server", () => {
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, partial_end: true, restarts: 3,
    starts: [{ at: "2026-11-23T14:00:00Z", version: "0.10.12" }], starts_complete: false,
    per_ip_refusals: { total: 51, everyone_else: 51 }, addresses: { rate_limited: 1, cap_reached: 0, blocked_tried: 0 } })] }));
  app.render();
  assert.match(app.el("attention").querySelector("li").textContent, /^51 requests turned away/);
  assert.doesNotMatch(app.el("capacity").textContent, /from 1 address/);
});

test("ext's part of a cause never goes past the cause", () => {
  const app = setup(payload({ health: { status: "healthy" }, edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true,
    distributor_limits: { digikey: { held_back: { address_daily: 200 }, ext_held_back: { address_daily: 202 } } } })] }));
  app.render();
  assert.match(app.el("tiles").children[8].textContent, /turned away: API 0, ext 200/);
  const item = app.attentionItems(app.view(), app.scope(app.view())).find((it) => it.key === "held_back:digikey:address_daily");
  assert.equal(item.count, 200);
  assert.match(item.detail, /All through ext\./);
});

test("a start after a rollback is a deploy, even when the start before it ran the same version", () => {
  const starts = [{ at: "2026-11-23T06:00:00Z", version: "0.10.12" }, { at: "2026-11-23T13:00:00Z", version: "0.10.12" }];
  const app = setup(payload({ health: { status: "healthy", version: "0.10.12" },
    versions: [{ version: "0.10.11", from: "2026-11-20T10:00:00Z", exact: false, to: "2026-11-23T06:00:00Z" },
      { version: "0.10.12", from: "2026-11-23T06:00:00Z", exact: true, to: "2026-11-23T10:00:30Z" },
      { version: "0.10.11", from: "2026-11-23T10:00:30Z", after: "2026-11-23T09:00:30Z", exact: false, to: "2026-11-23T13:00:00Z" },
      { version: "0.10.12", from: "2026-11-23T13:00:00Z", exact: true, to: null }],
    edays: [day("2026-11-22"), day("2026-11-23", { complete: false, partial_end: true, restarts: 3, starts, starts_complete: false })] }));
  app.render();
  const today = app.el("events").querySelectorAll("li").find((li) => /Nov 23/.test(li.textContent)).textContent;
  assert.match(today, /◆0\.10\.12 went live 1:00 AM/);
  assert.match(today, /◆0\.10\.11 went live between 4:00 AM and 5:00 AM/);
  assert.match(today, /◆0\.10\.12 went live 8:00 AM/);
  assert.match(today, /↻1 more restart, times not kept/);
});

test("a pause of the whole pool pauses every budget, and in use is the server's word", () => {
  const budgets = [0, 1, 2, 3].map((i) => ({ used_today: i === 3 ? 0 : 1000, limit: 1000, api_remaining: null,
    paused_until: i === 1 ? "2026-11-23 17:00 UTC" : null, in_use: i === 3 }));
  const app = setup(payload({ health: { status: "healthy", distributor_quota: { mouser: {
    used_today: 0, limit: 1000, paused_until: "2026-11-23 16:00 UTC", resets_at: "2026-11-24 06:00 UTC", budgets } } } }));
  app.render();
  const rows = app.el("tiles").children[7].querySelectorAll("li");
  assert.match(rows[0].textContent, /paused until 11:00 AM$/);
  assert.match(rows[1].textContent, /paused until 12:00 PM$/); // its own pause runs later
  assert.match(rows[3].textContent, /in use, paused until 11:00 AM$/);
  assert.equal(rows[3].dataset.state, "in-use");
  app.setNow("2026-11-23T16:30:00Z");
  app.render();
  const later = app.el("tiles").children[7].querySelectorAll("li");
  assert.match(later[0].textContent, /spent$/);
  assert.match(later[3].textContent, /in use$/);
});

// ---------------------------------------------------------------- Traffic: which tools failed, by hour

function problemsDay(hourProblems, extra = {}) {
  const failed = Array(24).fill(0), refused = Array(24).fill(0);
  failed[8] = 12;
  refused[8] = 4;
  return day("2026-11-23", { complete: false, partial_end: true, failed_hours: failed, refused_hours: refused,
    tools: { jlc_search: { calls: 24, ok: 22, bad_request: 2 }, cse_search: { calls: 7, failed: 7 }, cse_get_kicad: { calls: 5, failed: 5 } },
    per_ip_refusals: { total: 4, everyone_else: 4 }, hour_problems: hourProblems, ...extra });
}
const hourEntry = (extra = {}) => ({ from: "2026-11-23T13:00:30Z", to: "2026-11-23T14:00:30Z",
  failed: { cse_search: { cse_lookup_failed: 7 }, cse_get_kicad: { cse_invalid_zip: 3, cse_download_network: 2 } },
  rejected: { jlc_search: { "arg:limit:int_parsing": 2 } }, ...extra });

/** The tooltip of the problems chart at one hour, reached with the arrow keys. */
function problemsTip(app, hour) {
  const chart = app.el("traffic").querySelectorAll(".chart").find((c) => /tools that failed/.test(c.getAttribute("aria-label")));
  chart.onkeydown({ key: "ArrowRight", preventDefault() {} });
  for (let i = 23; i > hour; i--) chart.onkeydown({ key: "ArrowLeft", preventDefault() {} });
  return app.el("tooltip");
}

test("the problems tooltip says which tools failed and why, and the rejected arguments", () => {
  const hours = Array(24).fill(null);
  hours[8] = hourEntry();
  const app = setup(payload({ edays: [day("2026-11-22"), problemsDay(hours, { addresses: { rate_limited: 1, cap_reached: 0, blocked_tried: 0 }, starts: [], starts_complete: true })] }));
  app.render();
  const tip = problemsTip(app, 8);
  const lines = tip.children.map((c) => c.textContent);
  assert.deepEqual([...lines], ["Mon, Nov 23, 8:00 AM to 9:00 AM EST", "4Turned away", "from 1 address", "12Failed",
    "cse_search 7 · SamacSys search failed", "cse_get_kicad 3 · SamacSys sent a broken file",
    "cse_get_kicad 2 · SamacSys download lost its connection", "2Rejected arguments", "jlc_search 2 · \"limit\" wasn't a whole number"]);
  assert.equal(tip.querySelectorAll(".tt-sub").length, 5);
  // the table view says it too
  assert.match(app.el("traffic").querySelector(".table-view").textContent, /failed: cse_search 7, cse_get_kicad 5; rejected: jlc_search 2/);
});

test("a breakdown over a missed check says it covers several hours; more lines than fit say how many", () => {
  const hours = Array(24).fill(null);
  const span = hourEntry({ from: "2026-11-23T11:00:30Z", to: "2026-11-23T14:00:30Z",
    failed: { a_tool: { exception: 5 }, b_tool: { exception: 4 }, c_tool: { exception: 2 }, d_tool: { exception: 1 } } });
  hours[6] = hours[7] = hours[8] = span;
  const app = setup(payload({ edays: [day("2026-11-22"), problemsDay(hours)] }));
  app.render();
  const text = problemsTip(app, 8).textContent;
  assert.match(text, /a_tool 5 · Server error \(a bug in our code\)b_tool 4 · Server error \(a bug in our code\)c_tool 2 · Server error \(a bug in our code\)\+1 more/);
  assert.match(text, /by tool over 6 AM to 9 AM: a check was missed/);
});

test("a day rebuilt from daily totals shows totals only", () => {
  const app = setup(payload({ edays: [day("2026-11-22"), problemsDay(null)] }));
  app.render();
  const text = problemsTip(app, 8).textContent;
  assert.match(text, /12Failedno breakdown by tool for this day: rebuilt from daily totals/);
  assert.doesNotMatch(text, /Rejected arguments|cse_search/);
});

test("a multi-day chart shows each day's own breakdown", () => {
  const busy = { tools: { cse_search: { calls: 9, failed: 9 } }, reasons: { cse_search: { cse_lookup_failed: 9 } },
    bad_request_reasons: { jlc_search: { too_long: 3 } } };
  const days = ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20", "2026-11-21", "2026-11-22"].map((d) => day(d));
  days[6] = day("2026-11-22", { ...busy, tools: { ...busy.tools, jlc_search: { calls: 24, ok: 21, bad_request: 3 } } });
  const app = setup(payload({ edays: [...days.slice(0, 6), day("2026-11-15"), days[6], day("2026-11-23", { complete: false, partial_end: true })].sort((a, b) => (a.date < b.date ? -1 : 1)) }));
  app.state.range = "all"; // eight days: one column a day
  app.render();
  const chart = app.el("traffic").querySelectorAll(".chart").find((c) => /tools that failed/.test(c.getAttribute("aria-label")));
  chart.onkeydown({ key: "ArrowRight", preventDefault() {} });
  assert.match(app.el("tooltip").textContent, /9Failedcse_search 9 · SamacSys search failed3Rejected argumentsjlc_search 3 · Query too long/);
});

test("a tap shows the breakdown and keeps it after the finger lifts", () => {
  const hours = Array(24).fill(null);
  hours[8] = hourEntry();
  const app = setup(payload({ edays: [day("2026-11-22"), problemsDay(hours)] }));
  app.render();
  const chart = app.el("traffic").querySelectorAll(".chart").find((c) => /tools that failed/.test(c.getAttribute("aria-label")));
  const hit = chart.querySelector("svg").children.at(-1);
  // the double's chart is 600 wide: plot from 46 to 592, 24 columns of 22.75
  hit.dispatch("pointerdown", { pointerType: "touch", clientX: 46 + 22.75 * 8.5, clientY: 50 });
  hit.dispatch("pointerleave", { pointerType: "touch" });
  assert.equal(app.el("tooltip").dataset.show, "true");
  assert.match(app.el("tooltip").textContent, /cse_search 7/);
  assert.equal(document.activeElement, chart);
  hit.dispatch("pointerleave", { pointerType: "mouse" });
  assert.equal(app.el("tooltip").dataset.show, "false");
});

test("a second tap moves the highlight: only the column shown is lit", () => {
  setup();
  const c = new Element("div");
  document.body.append(c);
  charts.columns(c, { points: [0, 1, 2, 3].map((i) => ({ title: `h${i}` })), series: [{ label: "Failed", color: "#f00", values: [1, 2, 3, 4] }] });
  const svg = c.children[0], hit = svg.children.at(-1);
  for (const x of [60, 400]) {
    hit.dispatch("pointerdown", { pointerType: "touch", clientX: x, clientY: 50 });
    hit.dispatch("pointerleave", { pointerType: "touch" });
  }
  const lit = svg.querySelectorAll("*").filter((e) => e !== hit && e.style.filter);
  assert.equal(lit.length, 1);
  assert.equal(document.getElementById("tooltip").querySelector(".tt-title").textContent, "h2");
});
