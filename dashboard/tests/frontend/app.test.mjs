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
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems })] }));
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
    const app = setup(payload({ edays: [day("2026-11-23", { complete: false,
      upstream_status: problems.upstream_status, problems })] }));
    app.render();
    const items = app.attentionItems(app.view(), app.scope(app.view()));
    const warning = items.find((it) => it.what.startsWith("Mouser:"));
    if (warnings) {
      assert.equal(warning.what, `Mouser: ${warnings} of ${10 + errors} requests got an error answer.`);
      assert.match(warning.detail, new RegExp(`rejected our request ${warnings}`));
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
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false,
    upstream_status: problems.upstream_status, problems })] }));
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  const errors = items.filter((it) => it.what.startsWith("Mouser:"));
  assert.equal(errors.length, 1);
  assert.equal(errors[0].what, `Mouser: ${bad} of 9 requests got an error answer.`);
  assert.match(errors[0].detail, new RegExp(`rejected our request ${st["4xx"]}`));
  if (otherStatus === 503) assert.match(errors[0].detail, /server error or no answer 3/);
  assert.equal(items.filter((it) => /daily limit/.test(it.what)).length, 1);
  assert.equal(items.filter((it) => /Mouser refused 3 of our requests/.test(it.what)).length, minute ? 1 : 0);
  assert.equal(app.view().problems.upstream_status.mouser["429"], st["429"]);
});

for (const [daily, counted429, errors4xx, errors5xx, expected] of [
  [3, 3, 0, 0, 0], [3, 3, 3, 0, 3], [3, 3, 0, 3, 3],
  [5, 3, 5, 0, 5], [3, 6, 3, 0, 3], [3, 0, 6, 0, 6],
]) test(`Mouser excludes only 429: ${daily} daily, ${counted429} at 429, ${errors4xx} at 4xx, ${errors5xx} at 5xx`, () => {
  const problems = { distributor_limits: { mouser: { refusals: { daily } } },
    upstream_status: { mouser: { "429": counted429, "4xx": errors4xx, "5xx": errors5xx } } };
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems })] }));
  const warning = app.attentionItems(app.view(), app.scope(app.view())).find((it) => it.what.startsWith("Mouser:"));
  if (expected) assert.equal(warning.what, `Mouser: ${expected} of ${counted429 + errors4xx + errors5xx} requests got an error answer.`);
  else assert.equal(warning, undefined);
});

test("DigiKey 429 outcomes still contribute to HTTP warnings", () => {
  const problems = { upstream_status: { digikey: { "429": 3 } } };
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems })] }));
  assert.ok(app.attentionItems(app.view(), app.scope(app.view())).some((it) => it.what === "DigiKey API: 3 of 3 requests got an error answer."));
});

test("DigiKey HTTP warnings say plain DigiKey over unsplit days and count DigiKey's retries", () => {
  const status = { digikey: { "2xx": 10, "5xx": 6 } };
  const warning = (distributors) => {
    const problems = { upstream_status: status, distributors };
    const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems, distributors })] }));
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
  assert.match(text, /Sent to DigiKey30/);
  assert.match(text, /Through the API18/);
  assert.match(text, /Through ext12/);
  assert.match(text, /Requests each API lookup took, on average2\.0/); // the API's 36 requests over its 18 lookups
  assert.doesNotMatch(text, /counted apart/);
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  assert.ok(items.some((it) => it.what === "DigiKey ext: 3 of 14 requests got an error answer."));
  assert.ok(!items.some((it) => it.what.startsWith("DigiKey API:")));
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
  assert.match(text, /Sent to DigiKey110/);
  assert.match(text, /Through the API \(from Nov 22\)18/);
  assert.match(text, /Through ext \(from Nov 22\)12/);
  // the older days' requests and lookups both include ext's; the split day's API ones go together
  assert.match(text, /Requests each one took, on average1\.0/); // not "API lookup": older days are unsplit

  app.state.range = "yesterday"; // the split day alone: no older figure, no note
  app.render();
  text = app.el("upstreams").textContent;
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey API");
  assert.match(text, /Through the API18/);
  assert.match(text, /Requests each API lookup took, on average1\.0/);
  assert.doesNotMatch(text, /counted apart|\(from /);

  const before = setup(payload({ edays: [day("2026-11-22", old), day("2026-11-23", { complete: false, partial_end: true })] }));
  before.state.range = "yesterday"; // only older days: exactly as before the split existed
  before.render();
  text = before.el("upstreams").textContent;
  assert.equal(dkRow(before, "digikey").children[0].textContent, "DigiKey");
  assert.equal(dkRow(before, "digikey_ext"), null);
  assert.match(text, /Sent to DigiKey40/);
  assert.match(text, /Requests each one took, on average1\.0/);
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
  assert.match(text, /Sent to DigiKey300/);
  assert.match(text, /Requests each one took, on average1\.0/); // 200 + 100 requests for 300 lookups
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
  assert.match(text, new RegExp(`Sent to DigiKey${older * 40 + 330}`));
  assert.equal(dkRow(app, "digikey").children[0].textContent, "DigiKey");
  assert.equal(dkRow(app, "digikey").children[1].textContent, String(older * 40 + 218));
  assert.equal(dkRow(app, "digikey_ext").children[1].textContent, "112");
  // older days 40/40, the deploy day (200 + 100)/300, the split day 18/18: 1.0, where adding the range's
  // requests and dividing by all but the split day's ext lookups gave less than one, so no figure
  assert.match(text, /Requests each one took, on average1\.0/);
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
  assert.match(text, /Sent to DigiKey20/);
  assert.match(text, /Requests each one took, on average1\.0/);
  assert.doesNotMatch(text, /Through the|ext/);
});

test("mixed Mouser refusals split daily info from warnings and keep held-back lookups visible", () => {
  const problems = { distributor_limits: {
    mouser: { refusals: { daily: 7, minute: 2, refused: 1 }, held_back: { distributor_daily: 4 } },
    digikey: { refusals: { daily: 5 } },
  } };
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems })] }));
  app.render();
  const items = app.attentionItems(app.view(), app.scope(app.view()));
  assert.equal(items.length, 4);
  assert.ok(items.slice(0, -1).every((it) => it.level === "warning"));
  assert.equal(items.at(-1).level, "info");
  assert.match(items.at(-1).what, /Mouser refused 7 requests for its daily limit/);
  const warning = items.find((it) => it.level === "warning" && it.what.startsWith("Mouser refused"));
  assert.match(warning.what, /refused 3 of our requests/);
  assert.match(warning.detail, /per-minute limit 2, refused 1/);
  assert.doesNotMatch(warning.detail, /daily/);
  assert.ok(items.some((it) => /4 Mouser lookups turned away by limits/.test(it.what)));
  assert.match(app.el("tiles").textContent, /Turned away by limits4/);
  assert.equal(app.el("attention").querySelector(".clear"), null);
});

test("held-back labels keep address and DigiKey resets separate from Mouser's budget", () => {
  const distributors = { mouser: { sent: 0 }, digikey: { sent: 0 } };
  const problems = { distributor_limits: {
    mouser: { held_back: { daily_count: 2, address_daily: 1 } },
    digikey: { held_back: { daily_count: 1, address_blocked: 1 } },
  } };
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, distributors, problems })] }));
  app.render();
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
  const app = setup(payload({ problems_since: "2026-11-21T18:00:00Z", edays: [
    day("2026-11-20", { upstream: { jlcpcb: { sent: 50 } } }),
    day("2026-11-21", { ...usage(40), problems: { ...usage(2), start: "2026-11-21T18:00:00Z" } }),
    day("2026-11-22", { ...usage(50), problems: usage(3) }),
    day("2026-11-23", { ...usage(60), complete: false, problems: usage(60) }),
  ] }));
  app.state.range = "all";
  app.render();
  const view = app.view("all"), items = app.attentionItems(view, app.scope(view));
  assert.equal(items.length, 1);
  assert.equal(items[0].what, "Mouser: 20 of 200 requests got an error answer.");
  assert.match(items[0].detail, /5 were retries\.$/);
  const row = app.el("upstreams").querySelector("td[title=\"mouser\"]").parentElement;
  assert.equal(row.children[0].textContent, "Mouser");
  assert.equal(row.children[1].textContent, "200");
  assert.match(row.textContent, /20 of 200/);
  assert.match(app.el("upstreams").textContent, /Mouser since Sat 1:00 PM/);
});

for (const retries of [undefined, null, 0, 1]) test(`Mouser error text handles retries=${retries}`, () => {
  const problems = { upstream_status: { mouser: { "5xx": 5 } },
    ...(retries === undefined ? {} : { distributors: { mouser: { retries } } }) };
  const app = setup(payload({ edays: [day("2026-11-23", { complete: false, problems })] }));
  app.render();
  const [item] = app.attentionItems(app.view(), app.scope(app.view()));
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
