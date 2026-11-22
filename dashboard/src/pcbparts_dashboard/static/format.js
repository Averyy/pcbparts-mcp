// Number, time and text helpers. All times shown in Eastern.
export const TZ = "America/New_York";
const nf = new Intl.NumberFormat("en-US");

export function full(n) {
  return n == null || Number.isNaN(n) ? "–" : nf.format(Math.round(n));
}

export function compact(n) {
  if (n == null || Number.isNaN(n)) return "–";
  const a = Math.abs(n);
  if (a < 10_000) return nf.format(Math.round(n));
  if (a < 1_000_000) return trimZero((n / 1000).toFixed(a < 100_000 ? 1 : 0)) + "K";
  return trimZero((n / 1_000_000).toFixed(1)) + "M";
}
const trimZero = (s) => s.replace(/\.0$/, "");

/** A share as text: "3 of 9" under 30, otherwise a percent with sensible precision. */
export function rate(num, den, { min = 30 } = {}) {
  if (!den) return "–";
  if (den < min) return `${full(num)} of ${full(den)}`;
  return percent(num / den);
}

export function percent(r) {
  if (r == null || Number.isNaN(r)) return "–";
  const p = r * 100;
  if (p === 0) return "0%";
  if (p < 0.1) return "<0.1%";
  if (p < 10) return trimZero(p.toFixed(1)) + "%";
  return Math.round(p) + "%";
}

export function ms(v) {
  if (v == null) return "–";
  if (v >= 1000) return trimZero((v / 1000).toFixed(1)) + " s";
  return `${v} ms`;
}

/** Percentile from bucket counts; returns the bucket's upper bound in ms, null for the open bucket, undefined when empty. */
export function percentile(counts, bounds, p) {
  if (!Array.isArray(counts)) return undefined;
  const total = counts.reduce((a, b) => a + (b || 0), 0);
  if (!total) return undefined;
  const target = Math.ceil(p * total);
  let cum = 0;
  for (let i = 0; i < counts.length; i++) {
    cum += counts[i] || 0;
    if (cum >= target) return i < bounds.length ? bounds[i] : null;
  }
  return null;
}

export function latencyText(counts, bounds, p) {
  const v = percentile(counts, bounds, p);
  if (v === undefined) return "–";
  return v == null ? ">" + ms(bounds[bounds.length - 1]) : "≤" + ms(v);
}

const fmtCache = new Map();
function fmt(opts) {
  const key = JSON.stringify(opts);
  if (!fmtCache.has(key)) fmtCache.set(key, new Intl.DateTimeFormat("en-US", { timeZone: TZ, ...opts }));
  return fmtCache.get(key);
}

export const parseIso = (s) => (s ? new Date(s) : null);
export const timeET = (d) => fmt({ hour: "numeric", minute: "2-digit" }).format(d);
export const hourET = (d) => fmt({ hour: "numeric" }).format(d).replace(":00", "");
export const dateET = (d) => fmt({ month: "short", day: "numeric" }).format(d);
export const weekdayDateET = (d) => fmt({ weekday: "short", month: "short", day: "numeric" }).format(d);
export const dateTimeET = (d) => fmt({ month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(d);

export function tzAbbr(d) {
  const part = fmt({ timeZoneName: "short" }).formatToParts(d).find((p) => p.type === "timeZoneName");
  return part ? part.value : "ET";
}

/** Eastern calendar parts for a Date: {y, m, d, h, key:"YYYY-MM-DD"}. */
export function partsET(d) {
  const o = {};
  for (const p of fmt({ year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" }).formatToParts(d)) o[p.type] = p.value;
  return { y: +o.year, m: +o.month, d: +o.day, h: +o.hour % 24, key: `${o.year}-${o.month}-${o.day}` };
}

/** "Nov 21" (or "Sat, Nov 21") for a YYYY-MM-DD calendar date, read as written (not shifted). */
export function dayLabel(date, { weekday = false, long = false } = {}) {
  const d = new Date(date + "T12:00:00Z");
  return new Intl.DateTimeFormat("en-US", { timeZone: "UTC", month: "short", day: "numeric", ...(weekday ? { weekday: long ? "long" : "short" } : {}) }).format(d);
}

/** Epoch ms of midnight Eastern starting the YYYY-MM-DD date (05:00 UTC in winter, 04:00 in summer). */
export function etMidnight(date) {
  const [y, m, d] = date.split("-").map(Number);
  for (const off of [5, 4]) {
    const t = Date.UTC(y, m - 1, d, off);
    const p = partsET(new Date(t));
    if (p.key === date && p.h === 0) return t;
  }
  return Date.UTC(y, m - 1, d, 5);
}

/** "Sat 1:00 PM" for a moment, Eastern. */
export const dayTimeET = (d) => fmt({ weekday: "short", hour: "numeric", minute: "2-digit" }).format(d);
/** "Sat 7 PM" for a moment on the hour, Eastern. */
export const dayHourET = (d) => `${fmt({ weekday: "short" }).format(d)} ${hourET(d)}`;

/**
 * The server's own day (its Mouser and DigiKey budgets, per-address allowances) runs midnight to
 * midnight UTC: 7 PM to 7 PM Eastern in winter, 8 PM in summer. The day holding `now`: [start, end).
 */
export function serverDay(now) {
  const start = new Date(now);
  start.setUTCHours(0, 0, 0, 0);
  return { start, end: new Date(start.getTime() + 86400_000) };
}
/** "7 PM": the Eastern hour the server's day ends at, on the day holding `now`. */
export const resetHour = (now) => hourET(serverDay(now).end);

export function ago(from, now) {
  const s = Math.max(0, Math.round((now - from) / 1000));
  if (s < 90) return "just now";
  const m = Math.round(s / 60);
  if (m < 90) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 36) return `${h} h ago`;
  return `${Math.round(h / 24)} days ago`;
}

export function addDays(date, n) {
  const d = new Date(date + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

export const utcDate = (d) => d.toISOString().slice(0, 10);

/** Signed change between two values. kind "count" gives a percent, "rate" gives points. */
export function delta(cur, prev, { upIsGood = true, kind = "count", flat = 0.02 } = {}) {
  if (cur == null || prev == null) return null;
  if (kind === "rate") {
    const pts = (cur - prev) * 100;
    const text = (pts >= 0 ? "+" : "−") + trimZero(Math.abs(pts).toFixed(Math.abs(pts) < 1 ? 2 : 1)) + " pts";
    const tone = Math.abs(pts) < 0.05 ? "neutral" : (pts > 0) === upIsGood ? "good" : "bad";
    return { text, tone, arrow: pts > 0 ? "▲" : pts < 0 ? "▼" : "" };
  }
  if (prev === 0) return cur === 0 ? { text: "no change", tone: "neutral", arrow: "" } : { text: "new", tone: "neutral", arrow: "" };
  const r = (cur - prev) / prev;
  // past ten times the old value a percent stops meaning anything ("+1721%"): say "18×"
  const text = r >= 9 ? `${Math.round(cur / prev)}×` : (r >= 0 ? "+" : "−") + percent(Math.abs(r)).replace("<0.1%", "0.1%");
  const tone = Math.abs(r) < flat ? "neutral" : (r > 0) === upIsGood ? "good" : "bad";
  return { text, tone, arrow: r > 0 ? "▲" : r < 0 ? "▼" : "" };
}

/** Build an element: h("td", {class: "x", text: "y"}, ...children). Text always goes through textContent. */
export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "text") el.textContent = v;
    else if (k === "class") el.className = v;
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "dataset") Object.assign(el.dataset, v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

export const SVGNS = "http://www.w3.org/2000/svg";
export function s(tag, attrs = {}, ...children) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "text") el.textContent = v;
    else el.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c) el.append(c);
  return el;
}
