// Small SVG charts: stacked columns with an optional comparison line, multi-line, sparkline.
// Marks follow the dataviz specs: <=24px columns with 4px rounded data ends, 2px lines,
// hairline grid, 2px surface gaps, a crosshair tooltip, keyboard stepping.
import { compact, full, h, s } from "./format.js";

const tip = () => document.getElementById("tooltip");

export function showTip(x, y, title, rows) {
  const el = tip();
  el.replaceChildren();
  if (title) el.append(h("div", { class: "tt-title", text: title }));
  for (const r of rows) {
    const key = r.color ? h("i", { class: "tt-key", style: { background: r.color } }) : h("i");
    el.append(h("div", { class: "tt-row" }, key, h("b", { text: r.value }), h("span", { text: r.label })));
  }
  el.dataset.show = "true";
  const pad = 14, w = el.offsetWidth, ht = el.offsetHeight;
  let left = x + pad, top = y + pad;
  if (left + w > innerWidth - 8) left = x - w - pad;
  if (top + ht > innerHeight - 8) top = y - ht - pad;
  el.style.left = Math.max(8, left) + "px";
  el.style.top = Math.max(8, top) + "px";
}
export function hideTip() { tip().dataset.show = "false"; }

/** Axis top and tick step: round steps (1, 2, 2.5, 5 x 10^k, whole numbers), about four gridlines. */
function niceScale(v) {
  if (!(v > 0)) return { max: 4, step: 1 };
  const raw = v / 4;
  const p = 10 ** Math.floor(Math.log10(raw));
  // 2.5 only from 25 up: a step of 2.5 puts gridlines at 2.5 and 7.5, which the axis labels as 3 and 8
  let step = (p >= 10 ? [1, 2, 2.5, 5, 10] : [1, 2, 5, 10]).map((m) => m * p).find((x) => x >= raw);
  if (step < 1) step = 1;
  return { max: step * Math.ceil(v / step), step };
}

function topRounded(x, y, w, hgt, r) {
  r = Math.max(0, Math.min(r, w / 2, hgt));
  return `M${x},${y + hgt}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + hgt}Z`;
}

function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

/**
 * Stacked columns. points: [{title, tick, partial}], series: [{label, color, values}],
 * compare: {label, color, values} drawn as a line, markers: [{index, label}].
 */
export function columns(container, { points, series, compare, markers = [], height = 220, yFormat = compact, ariaLabel, extraRows, tooltipValue = full }) {
  if (ariaLabel && !container.id) container.id = "chart-" + encodeURIComponent(ariaLabel);
  container.replaceChildren();
  container.classList.add("chart");
  const W = Math.max(280, container.clientWidth || 600);
  const m = { l: 46, r: 8, t: markers.length ? 18 : 8, b: 24 };
  const pw = W - m.l - m.r, ph = height - m.t - m.b;
  const n = points.length;
  const stackTop = points.map((_, i) => series.reduce((a, sr) => a + (sr.values[i] || 0), 0));
  const { max: yMax, step } = niceScale(Math.max(...stackTop, ...(compare ? compare.values.map((v) => v || 0) : [0]), 1));
  const y = (v) => m.t + ph - (v / yMax) * ph;
  const band = pw / n;
  const bw = band >= 6 ? Math.min(24, band * 0.7) : Math.max(1, band - 1);
  const cx = (i) => m.l + band * i + band / 2;
  const surface = cssVar("--card") || "#0D1F16";

  const svg = s("svg", { viewBox: `0 0 ${W} ${height}`, width: W, height, role: "img", "aria-label": ariaLabel || "" });
  const grid = s("g", { class: "grid" });
  const axis = s("g", { class: "axis" });
  for (let v = 0; v <= yMax + 1e-9; v += step) {
    const k = v, yy = Math.round(y(v)) + 0.5;
    if (k > 0) grid.append(s("line", { x1: m.l, x2: W - m.r, y1: yy, y2: yy }));
    axis.append(s("text", { x: m.l - 8, y: yy + 4, "text-anchor": "end", text: yFormat(v) }));
  }
  svg.append(grid);
  svg.append(s("line", { class: "baseline", x1: m.l, x2: W - m.r, y1: m.t + ph + 0.5, y2: m.t + ph + 0.5 }));

  // x ticks, skipping any that would crowd the previous one
  let lastX = -Infinity;
  points.forEach((p, i) => {
    if (!p.tick) return;
    const x = cx(i);
    if (x - lastX < 46) return;
    lastX = x;
    axis.append(s("text", { x, y: height - 6, "text-anchor": "middle", text: p.tick }));
  });
  svg.append(axis);

  const cols = s("g");
  const colEls = [];
  points.forEach((p, i) => {
    const g = s("g", { class: p.partial ? "partial" : null });
    let base = 0;
    const stackIdx = series.map((sr, k) => [k, sr.values[i] || 0]).filter(([, v]) => v > 0);
    stackIdx.forEach(([k, v], j) => {
      const y0 = y(base), y1 = y(base + v);
      let top = y1, hgt = y0 - y1;
      if (j > 0 && hgt > 2) hgt -= 2; // surface gap between stacked segments
      if (hgt < 0.5) hgt = 0.5, top = y0 - 0.5;
      const isTop = j === stackIdx.length - 1;
      const x = cx(i) - bw / 2;
      g.append(isTop
        ? s("path", { d: topRounded(x, top, bw, hgt, bw >= 8 ? 4 : bw / 3), fill: series[k].color })
        : s("rect", { x, y: top, width: bw, height: hgt, fill: series[k].color }));
      base += v;
    });
    cols.append(g);
    colEls.push(g);
  });
  svg.append(cols);

  if (compare) {
    let d = "";
    compare.values.forEach((v, i) => {
      if (v == null) { d += " "; return; }
      const cmd = d === "" || d.endsWith(" ") ? "M" : "L";
      d += `${cmd}${cx(i).toFixed(1)},${y(v).toFixed(1)}`;
    });
    svg.append(s("path", { d: d.trim(), fill: "none", stroke: compare.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round", opacity: 0.9 }));
  }

  for (const mk of markers) {
    const x = Math.round(cx(mk.index)) + 0.5;
    svg.append(s("g", { class: "marker" },
      s("line", { x1: x, x2: x, y1: m.t - 4, y2: m.t + ph }),
      s("text", { x: x + 4, y: m.t - 6, text: mk.label })));
  }

  const cross = s("line", { class: "crosshair", y1: m.t, y2: m.t + ph, opacity: 0 });
  svg.append(cross);
  const hit = s("rect", { x: m.l, y: 0, width: pw, height, fill: "transparent" });
  svg.append(hit);
  container.append(svg);

  let current = -1;
  const show = (i, clientX, clientY) => {
    if (i < 0 || i >= n || i === current) return;
    if (current >= 0) colEls[current].style.filter = "";
    colEls[i].style.filter = "brightness(1.25)";
    current = i;
    const x = Math.round(cx(i)) + 0.5;
    cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("opacity", 1);
    const rows = [];
    for (const sr of [...series].reverse()) {
      const v = sr.values[i];
      if (v == null && series.length > 1) continue;
      rows.push({ color: sr.color, value: v == null ? "–" : tooltipValue(v), label: sr.label });
    }
    if (compare) rows.push({ color: compare.color, value: compare.values[i] == null ? "–" : tooltipValue(compare.values[i]), label: compare.label });
    if (extraRows) rows.push(...extraRows(i));
    if (clientX == null) {
      const r = svg.getBoundingClientRect();
      clientX = r.left + (x / W) * r.width;
      clientY = r.top + (y(stackTop[i]) / height) * r.height;
    }
    showTip(clientX, clientY, points[i].title, rows);
  };
  const clear = () => {
    if (current >= 0) colEls[current].style.filter = "";
    current = -1; cross.setAttribute("opacity", 0); hideTip();
  };
  hit.addEventListener("pointermove", (e) => {
    const r = svg.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * W;
    show(Math.floor((x - m.l) / band), e.clientX, e.clientY);
  });
  hit.addEventListener("pointerleave", clear);
  container.tabIndex = 0;
  container.setAttribute("aria-label", (ariaLabel || "Chart") + ". Use the arrow keys to read values.");
  container.onkeydown = (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      show(Math.max(0, Math.min(n - 1, (current < 0 ? n - 1 : current + (e.key === "ArrowRight" ? 1 : -1)))));
    } else if (e.key === "Escape") clear();
  };
  container.onblur = clear;
}

/** Multi-series lines over the same x points. */
export function lines(container, { points, series, height = 200, yFormat = compact, ariaLabel }) {
  if (ariaLabel && !container.id) container.id = "chart-" + encodeURIComponent(ariaLabel);
  container.replaceChildren();
  container.classList.add("chart");
  const W = Math.max(280, container.clientWidth || 600);
  const m = { l: 46, r: 12, t: 10, b: 24 };
  const pw = W - m.l - m.r, ph = height - m.t - m.b;
  const n = points.length;
  const { max: yMax, step } = niceScale(Math.max(1, ...series.flatMap((sr) => sr.values.map((v) => v || 0))));
  const y = (v) => m.t + ph - (v / yMax) * ph;
  const x = (i) => (n === 1 ? m.l + pw / 2 : m.l + (pw * i) / (n - 1));
  const surface = cssVar("--card") || "#0D1F16";
  const svg = s("svg", { viewBox: `0 0 ${W} ${height}`, width: W, height, role: "img", "aria-label": ariaLabel || "" });
  const grid = s("g", { class: "grid" }), axis = s("g", { class: "axis" });
  for (let v = 0; v <= yMax + 1e-9; v += step) {
    const k = v, yy = Math.round(y(v)) + 0.5;
    if (k > 0) grid.append(s("line", { x1: m.l, x2: W - m.r, y1: yy, y2: yy }));
    axis.append(s("text", { x: m.l - 8, y: yy + 4, "text-anchor": "end", text: yFormat(v) }));
  }
  let lastX = -Infinity;
  points.forEach((p, i) => {
    if (!p.tick) return;
    if (x(i) - lastX < 46) return;
    lastX = x(i);
    axis.append(s("text", { x: x(i), y: height - 6, "text-anchor": "middle", text: p.tick }));
  });
  svg.append(grid, s("line", { class: "baseline", x1: m.l, x2: W - m.r, y1: m.t + ph + 0.5, y2: m.t + ph + 0.5 }), axis);
  for (const sr of series) {
    // a day without a record breaks the line: joining its neighbours would draw values nobody stored
    let d = "";
    sr.values.forEach((v, i) => {
      if (v == null) { d += " "; return; }
      d += `${d === "" || d.endsWith(" ") ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)}`;
      // a lone point between gaps has no segment to show it: a zero-length one draws as a dot
      if (sr.values[i - 1] == null && sr.values[i + 1] == null) d += "h0";
    });
    svg.append(s("path", { d: d.trim(), fill: "none", stroke: sr.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
    const last = sr.values.length - 1;
    if (sr.values[last] != null) svg.append(s("circle", { cx: x(last), cy: y(sr.values[last]), r: 4, fill: sr.color, stroke: surface, "stroke-width": 2 }));
  }
  const cross = s("line", { class: "crosshair", y1: m.t, y2: m.t + ph, opacity: 0 });
  const hit = s("rect", { x: m.l - 6, y: 0, width: pw + 12, height, fill: "transparent" });
  svg.append(cross, hit);
  container.append(svg);
  let current = -1;
  const show = (i, cxp, cyp) => {
    if (i < 0 || i >= n || i === current) return;
    current = i;
    const xx = Math.round(x(i)) + 0.5;
    cross.setAttribute("x1", xx); cross.setAttribute("x2", xx); cross.setAttribute("opacity", 1);
    const rows = series.map((sr) => ({ color: sr.color, value: sr.values[i] == null ? "–" : full(sr.values[i]), label: sr.label, v: sr.values[i] || 0 }))
      .sort((a, b) => b.v - a.v);
    if (cxp == null) { const r = svg.getBoundingClientRect(); cxp = r.left + (xx / W) * r.width; cyp = r.top + r.height / 3; }
    showTip(cxp, cyp, points[i].title, rows);
  };
  const clear = () => { current = -1; cross.setAttribute("opacity", 0); hideTip(); };
  hit.addEventListener("pointermove", (e) => {
    const r = svg.getBoundingClientRect();
    const px = ((e.clientX - r.left) / r.width) * W;
    show(n === 1 ? 0 : Math.round(((px - m.l) / pw) * (n - 1)), e.clientX, e.clientY);
  });
  hit.addEventListener("pointerleave", clear);
  container.tabIndex = 0;
  container.setAttribute("aria-label", (ariaLabel || "Chart") + ". Use the arrow keys to read values.");
  container.onkeydown = (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      show(Math.max(0, Math.min(n - 1, current < 0 ? n - 1 : current + (e.key === "ArrowRight" ? 1 : -1))));
    } else if (e.key === "Escape") clear();
  };
  container.onblur = clear;
}

/** Word-sized trend: de-emphasis line, the range's own point in copper. */
export function sparkline(values, { width = 160, height = 26, accentLast = true, partialLast = false } = {}) {
  const vals = values.map((v) => (typeof v === "number" ? v : null));
  const max = Math.max(1, ...vals.filter((v) => v != null));
  const n = vals.length;
  const x = (i) => 2 + ((width - 6) * i) / Math.max(1, n - 1);
  const y = (v) => height - 3 - (v / max) * (height - 7);
  let d = "";
  vals.forEach((v, i) => { if (v == null) { d += " "; return; } d += `${d === "" || d.endsWith(" ") ? "M" : "L"}${x(i).toFixed(1)},${y(v).toFixed(1)}`; });
  const svg = s("svg", { viewBox: `0 0 ${width} ${height}`, width: "100%", height, preserveAspectRatio: "none", "aria-hidden": "true", class: "spark-svg" });
  if (vals.filter((v) => v != null).length < 2) return svg; // one day is a dot, not a trend
  svg.append(s("path", { d: d.trim(), fill: "none", stroke: cssVar("--silk-dim"), "stroke-width": 1.5, "stroke-linejoin": "round", opacity: 0.7, "vector-effect": "non-scaling-stroke" }));
  const last = vals[n - 1];
  if (accentLast && last != null) {
    // The svg stretches to its box (preserveAspectRatio none), which would squash a circle into an
    // ellipse. A zero-length stroke with round caps keeps its width in screen pixels, so it stays round.
    const dot = (width, color) => s("path", {
      d: `M${x(n - 1).toFixed(1)},${y(last).toFixed(1)}h0`, fill: "none", stroke: color, "stroke-width": width,
      "stroke-linecap": "round", "vector-effect": "non-scaling-stroke",
    });
    svg.append(dot(7.5, cssVar("--copper")));
    if (partialLast) svg.append(dot(4.5, cssVar("--card"))); // hollow: the day isn't over
  }
  return svg;
}

/** A thin segmented bar: one whole split into parts, no text (the figures sit beside it). */
export function segBar(parts, { width } = {}) {
  const total = parts.reduce((a, p) => a + (p.value || 0), 0);
  const el = h("div", { class: "seg", style: width ? { width } : null, role: "img", "aria-label": parts.filter((p) => p.value).map((p) => `${p.label} ${full(p.value)}`).join(", ") });
  if (!total) return el;
  for (const p of parts) {
    if (!p.value) continue;
    el.append(h("i", { style: { flex: `${p.value} 0 0`, background: p.color }, title: `${p.label}: ${full(p.value)}` }));
  }
  return el;
}

export function legend(items) {
  return h("ul", { class: "legend" }, items.map((it) => h("li", {}, h("i", { class: it.line ? "ln" : "sw", style: { background: it.color } }), it.label)));
}
