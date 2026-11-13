/* Build Room Website Design Studio — the tweak bar.
   Injected by tweakbar.py between its start and end markers (tweakbar.py remove takes it out).
   It only changes CSS variables on :root and data- attributes on <html> (the page token contract), so
   whatever the member lands on can be locked exactly. Nothing leaves the browser: "Save this look"
   shows the settings to copy or download, and keeps them in this browser when it can. */
(function () {
  "use strict";
  var cfgEl = document.getElementById("bt-config");
  if (!cfgEl) return;
  var cfg = JSON.parse(cfgEl.textContent);
  var root = document.documentElement;
  var KEY = "bt-presets:" + location.pathname;
  var COLOR_KEYS = ["bg", "surface", "ink", "muted", "accent", "accent_ink", "line"];
  var VAR_OF = {}; COLOR_KEYS.forEach(function (k) { VAR_OF[k] = "--c-" + k.replace("_", "-"); });
  var SHADOWS = { none: "none", soft: "0 1px 2px rgba(0,0,0,.08), 0 4px 12px rgba(0,0,0,.06)",
                  deep: "0 2px 4px rgba(0,0,0,.12), 0 16px 40px rgba(0,0,0,.18)" };
  var MOTION = { off: "0", gentle: "1", lively: "1.6" };
  var supportedVars = cfg.supported.vars, supportedAttrs = cfg.supported.attrs;
  function has(v) { return supportedVars.indexOf(v) >= 0; }
  function hasAttr(a) { return Object.prototype.hasOwnProperty.call(supportedAttrs, a); }

  // ---------------------------------------------------------------- colour maths (WCAG 2.2)
  var cv = document.createElement("canvas").getContext("2d");
  function toHex(v) { if (!v) return null; cv.fillStyle = "#000"; cv.fillStyle = v.trim(); var s = cv.fillStyle;
    return /^#[0-9a-f]{6}$/i.test(s) ? s.toLowerCase() : null; }
  function lum(h) { var c = [1, 3, 5].map(function (i) { var x = parseInt(h.substr(i, 2), 16) / 255;
    return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function getVar(n) { return getComputedStyle(root).getPropertyValue(n).trim(); }

  // ---------------------------------------------------------------- state
  var initial = { vars: Object.assign({}, cfg.initial.vars), attrs: Object.assign({}, cfg.initial.attrs) };
  var current = { vars: Object.assign({}, initial.vars), attrs: Object.assign({}, initial.attrs), palette: "", fonts: "" };
  function setVar(n, v) { current.vars[n] = String(v); root.style.setProperty(n, String(v)); }
  function setAttr(n, v) { current.attrs[n] = v; root.setAttribute(n, v); }
  var loadedFonts = {};
  function loadFonts(pair) { if (!pair.preview_css || loadedFonts[pair.name]) return; loadedFonts[pair.name] = 1;
    var l = document.createElement("link"); l.rel = "stylesheet"; l.href = pair.preview_css; document.head.appendChild(l); }
  function fam(f) { return '"' + f.family + '", ' + f.fallback; }

  // ---------------------------------------------------------------- the controls
  var C = [];
  function add(c) { C.push(c); }
  if (cfg.palettes.length && COLOR_KEYS.some(function (k) { return has(VAR_OF[k]); }))
    add({ id: "palette", group: "Look", label: "Colour palette", type: "select", level: "starter",
      options: cfg.palettes.map(function (p) { return p.name; }),
      apply: function (v) { var p = cfg.palettes.filter(function (x) { return x.name === v; })[0]; if (!p) return;
        current.palette = v; COLOR_KEYS.forEach(function (k) { if (p[k]) setVar(VAR_OF[k], p[k]); }); } });
  if (cfg.fonts.length && (has("--font-head") || has("--font-body")))
    add({ id: "fonts", group: "Look", label: "Font pairing", type: "select", level: "starter",
      options: cfg.fonts.map(function (p) { return p.name; }),
      apply: function (v) { var p = cfg.fonts.filter(function (x) { return x.name === v; })[0]; if (!p) return;
        current.fonts = v; loadFonts(p); setVar("--font-head", fam(p.head)); setVar("--font-body", fam(p.body)); } });
  function range(id, group, label, v, min, max, step, unit, level) {
    if (!has(v)) return;
    add({ id: id, group: group, label: label, type: "range", level: level, min: min, max: max, step: step, unit: unit,
      apply: function (x) { setVar(v, x + unit); } });
  }
  range("size", "Type", "Text size", "--size-base", cfg.min_px, 26, 1, "px", "starter");
  range("weight", "Type", "Heading weight", "--w-head", 400, 900, 100, "", "starter");
  range("scale", "Type", "Heading size steps", "--scale", 1.1, 1.5, 0.025, "", "advanced");
  range("leading", "Type", "Line spacing", "--leading", 1.35, 1.9, 0.05, "", "advanced");
  range("measure", "Type", "Line length", "--measure", 45, 85, 1, "ch", "advanced");
  range("radius", "Shape", "Corner roundness", "--radius", 0, 28, 1, "px", "starter");
  range("space", "Shape", "Spacing", "--space", 4, 14, 1, "px", "starter");
  if (has("--shadow")) add({ id: "shadow", group: "Shape", label: "Shadow depth", type: "select", level: "starter",
    options: ["none", "soft", "deep"], apply: function (x) { setVar("--shadow", SHADOWS[x]); } });
  if (has("--motion")) add({ id: "motion", group: "Motion & mode", label: "Motion", type: "select", level: "starter",
    options: ["off", "gentle", "lively"], apply: function (x) { setVar("--motion", MOTION[x]); } });
  var ATTR_LABELS = { "data-buttons": ["Shape", "Buttons", "starter"], "data-photo": ["Layout", "Photo treatment", "starter"],
    "data-hero": ["Layout", "Top of the page", "starter"], "data-texture": ["Layout", "Background", "starter"],
    "data-density": ["Layout", "Density", "advanced"], "data-theme": ["Motion & mode", "Light or dark", "starter"],
    "data-eyebrows": ["Generic tells", "Small labels over headings", "advanced"],
    "data-head-italic": ["Generic tells", "Italic last word in the headline", "advanced"] };
  Object.keys(ATTR_LABELS).forEach(function (a) {
    if (!hasAttr(a)) return; var L = ATTR_LABELS[a];
    add({ id: a, group: L[0], label: L[1], type: "select", level: L[2], options: supportedAttrs[a],
      apply: function (x) { setAttr(a, x);
        if (a !== "data-theme") return;
        // Dark mode comes from the page's own [data-theme="dark"] block: take the light palette off while it shows.
        if (x === "dark") COLOR_KEYS.forEach(function (k) { root.style.removeProperty(VAR_OF[k]); });
        else COLOR_KEYS.forEach(function (k) { var v = current.vars[VAR_OF[k]]; if (v) root.style.setProperty(VAR_OF[k], v); }); } });
  });
  COLOR_KEYS.forEach(function (k) {
    if (!has(VAR_OF[k])) return;
    add({ id: "c-" + k, group: "Colours one by one", label: { bg: "Page", surface: "Panels", ink: "Text", muted: "Quiet text",
      accent: "Accent", accent_ink: "Text on accent", line: "Lines" }[k], type: "color", level: "advanced",
      apply: function (x) { current.palette = "custom"; setVar(VAR_OF[k], x); } });
  });

  // ---------------------------------------------------------------- the panel
  var open = document.createElement("button");
  open.type = "button"; open.id = "bt-open"; open.textContent = "Tweaks"; open.setAttribute("aria-controls", "bt-panel");
  var panel = document.createElement("aside");
  panel.id = "bt-panel"; panel.setAttribute("aria-label", "Tweaks"); panel.hidden = true;
  var starterCount = C.filter(function (c) { return c.level === "starter"; }).length;
  panel.innerHTML = '<div class="bt-head"><strong>Tweaks</strong><span class="bt-count"></span>' +
    '<button type="button" class="bt-close" aria-label="Close tweaks">×</button></div>' +
    '<div class="bt-row"><button type="button" data-act="shuffle">Shuffle</button><button type="button" data-act="reset">Reset</button>' +
    '<button type="button" data-act="adv" aria-pressed="false">Show advanced</button></div>' +
    '<div class="bt-warn" role="status" aria-live="polite"></div><div class="bt-body"></div>' +
    '<div class="bt-save"><label>Name this look <input type="text" class="bt-name" maxlength="40" placeholder="Look 1"></label>' +
    '<button type="button" data-act="save">Save this look</button>' +
    '<div class="bt-out" hidden><p>Copy these settings into the chat, or download them:</p><textarea readonly rows="6"></textarea>' +
    '<div class="bt-row"><button type="button" data-act="copy">Copy</button><button type="button" data-act="download">Download</button></div></div></div>';
  document.body.appendChild(open); document.body.appendChild(panel);
  var body = panel.querySelector(".bt-body"), warn = panel.querySelector(".bt-warn");
  var showAdv = cfg.level === "advanced";
  var inputs = {};
  var groups = {};
  C.forEach(function (c) {
    var g = groups[c.group];
    if (!g) { g = document.createElement("fieldset"); g.className = "bt-group"; g.innerHTML = "<legend>" + c.group + "</legend>";
      body.appendChild(g); groups[c.group] = g; }
    var wrap = document.createElement("label"); wrap.className = "bt-ctl bt-" + c.level;
    var span = document.createElement("span"); span.textContent = c.label; wrap.appendChild(span);
    var el;
    if (c.type === "select") { el = document.createElement("select");
      c.options.forEach(function (o) { var op = document.createElement("option"); op.value = op.textContent = o; el.appendChild(op); }); }
    else if (c.type === "range") { el = document.createElement("input"); el.type = "range"; el.min = c.min; el.max = c.max; el.step = c.step; }
    else { el = document.createElement("input"); el.type = "color"; }
    el.addEventListener("input", function () { c.apply(el.value); refresh(); });
    wrap.appendChild(el); g.appendChild(wrap); inputs[c.id] = { c: c, el: el };
  });
  function syncInputs() {
    C.forEach(function (c) { var el = inputs[c.id].el, v;
      if (c.id === "palette") v = current.palette; else if (c.id === "fonts") v = current.fonts;
      else if (c.type === "range") { var name = { size: "--size-base", weight: "--w-head", scale: "--scale", leading: "--leading",
        measure: "--measure", radius: "--radius", space: "--space" }[c.id]; v = parseFloat(getVar(name)); }
      else if (c.type === "color") v = toHex(getVar(VAR_OF[c.id.slice(2)])) || "#000000";
      else if (c.id === "shadow") { var s = getVar("--shadow"); v = Object.keys(SHADOWS).filter(function (k) { return SHADOWS[k] === s; })[0] || "soft"; }
      else if (c.id === "motion") { var m = getVar("--motion"); v = Object.keys(MOTION).filter(function (k) { return MOTION[k] === m; })[0] || "gentle"; }
      else v = root.getAttribute(c.id) || c.options[0];
      if (v !== undefined && v !== "" && !(typeof v === "number" && isNaN(v))) el.value = v; });
  }
  function levels() {
    panel.querySelectorAll(".bt-advanced").forEach(function (n) { n.hidden = !showAdv; });
    panel.querySelectorAll(".bt-group").forEach(function (g) {
      g.hidden = !Array.prototype.some.call(g.querySelectorAll(".bt-ctl"), function (n) { return !n.hidden; }); });
    var b = panel.querySelector('[data-act="adv"]'); b.setAttribute("aria-pressed", String(showAdv));
    b.textContent = showAdv ? "Fewer controls" : "Show advanced";
    panel.querySelector(".bt-count").textContent = (showAdv ? C.length : starterCount) + " controls";
  }
  function refresh() {
    var msgs = [];
    var c = {}; COLOR_KEYS.forEach(function (k) { c[k] = toHex(getVar(VAR_OF[k])); });
    [["ink", "bg", 4.5, "Text"], ["muted", "bg", 4.5, "Quiet text"], ["accent_ink", "accent", 4.5, "Button text"],
     ["accent", "bg", 3, "Accent against the page"]].forEach(function (p) {
      if (c[p[0]] && c[p[1]]) { var r = ratio(c[p[0]], c[p[1]]);
        if (r < p[2]) msgs.push(p[3] + " contrast is " + r.toFixed(1) + ":1 (needs " + p[2] + ":1)"); } });
    var px = parseFloat(getVar("--size-base"));
    if (px && px < cfg.min_px) msgs.push("Text is " + px + "px; your readers need " + cfg.min_px + "px or more");
    if (root.getAttribute("data-eyebrows") === "on") msgs.push("Small labels over headings: a generic tell");
    if (root.getAttribute("data-head-italic") === "on") msgs.push("Italic last word: a generic tell");
    if (root.getAttribute("data-buttons") === "pill") msgs.push("Pill buttons everywhere: a generic tell");
    warn.textContent = msgs.length ? "Check: " + msgs.join(" · ") : "Readable: contrast and size pass.";
    warn.className = "bt-warn" + (msgs.length ? " bt-bad" : "");
  }
  function pick(a) { return a[Math.floor(Math.random() * a.length)]; }
  function apply(id, v) { if (inputs[id]) inputs[id].c.apply(v); }
  function shuffle() {
    if (inputs.palette) apply("palette", pick(cfg.palettes).name);
    if (inputs.fonts) apply("fonts", pick(cfg.fonts).name);
    if (inputs.radius) apply("radius", pick([0, 2, 4, 6, 10, 14]));
    if (inputs.space) apply("space", pick([6, 8, 10, 12]));
    if (inputs.weight) apply("weight", pick([500, 600, 700, 800]));
    if (inputs.size) apply("size", Math.max(cfg.min_px, pick([cfg.min_px, cfg.min_px + 1, cfg.min_px + 2])));
    if (inputs.shadow) apply("shadow", pick(["none", "soft", "deep"]));
    ["data-hero", "data-photo", "data-texture", "data-density"].forEach(function (a) { if (inputs[a]) apply(a, pick(supportedAttrs[a])); });
    if (inputs["data-buttons"]) apply("data-buttons", pick(["solid", "outline"]));
    syncInputs(); refresh();
  }
  function reset() {
    Object.keys(current.vars).forEach(function (n) { root.style.removeProperty(n); });
    current = { vars: Object.assign({}, initial.vars), attrs: Object.assign({}, initial.attrs), palette: "", fonts: "" };
    Object.keys(initial.attrs).forEach(function (a) { root.setAttribute(a, initial.attrs[a]); });
    syncInputs(); refresh();
  }
  function snapshot(name) {
    var theme = root.getAttribute("data-theme");
    if (theme === "dark") { root.setAttribute("data-theme", "light");
      COLOR_KEYS.forEach(function (k) { var v = current.vars[VAR_OF[k]]; if (v) root.style.setProperty(VAR_OF[k], v); }); }
    var vars = {}; supportedVars.forEach(function (n) { var v = getVar(n); if (v) vars[n] = v; });
    if (theme === "dark") { root.setAttribute("data-theme", "dark"); COLOR_KEYS.forEach(function (k) { root.style.removeProperty(VAR_OF[k]); }); }
    var attrs = {}; Object.keys(supportedAttrs).forEach(function (a) { var v = root.getAttribute(a); if (v) attrs[a] = v; });
    if (theme) attrs["data-theme"] = "light";
    return { name: name, palette: current.palette, fonts: current.fonts, vars: vars, attrs: attrs, saved: new Date().toISOString() };
  }
  function stored() { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
  function save() {
    var nm = panel.querySelector(".bt-name").value.trim() || ("Look " + (stored().length + 1));
    var list = stored().filter(function (p) { return p.name !== nm; }); list.push(snapshot(nm));
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* private window: the text box still has it */ }
    var out = panel.querySelector(".bt-out"); out.hidden = false;
    out.querySelector("textarea").value = JSON.stringify({ schema: "buildroom-tweaks-export/1", page: document.title, presets: list }, null, 2);
  }
  panel.addEventListener("click", function (e) {
    var act = e.target.getAttribute && e.target.getAttribute("data-act"); if (!act) return;
    if (act === "shuffle") shuffle(); if (act === "reset") reset();
    if (act === "adv") { showAdv = !showAdv; levels(); }
    if (act === "save") save();
    if (act === "copy") { var t = panel.querySelector("textarea"); t.select();
      try { navigator.clipboard.writeText(t.value); } catch (er) { document.execCommand && document.execCommand("copy"); }
      e.target.textContent = "Copied"; }
    if (act === "download") { var blob = new Blob([panel.querySelector("textarea").value], { type: "application/json" });
      var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "tweaks-export.json";
      document.body.appendChild(a); a.click(); a.remove(); }
  });
  function toggle(show) { panel.hidden = !show; open.setAttribute("aria-expanded", String(show)); if (show) panel.querySelector("select,input,button").focus(); }
  open.addEventListener("click", function () { toggle(panel.hidden); });
  panel.querySelector(".bt-close").addEventListener("click", function () { toggle(false); open.focus(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !panel.hidden) { toggle(false); open.focus(); } });
  levels(); syncInputs(); refresh();
  if (cfg.open) toggle(true);
  window.buildroomTweaks = { controls: C.length, starter: starterCount, snapshot: snapshot, shuffle: shuffle, reset: reset };
})();
