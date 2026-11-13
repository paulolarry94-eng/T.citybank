"""Pack the portfolio report page into ONE HTML file that opens in any browser, with no platform, no network and no server.

    python3 research/portfolio/make_offline_report.py [--d3 path/to/d3.min.js] [--out research/results/portfolio/report/report_offline.html]

Inputs (all in research/results/portfolio/report/): index.html (the page) and the CSV files it reads. The page was written for a
dashboard runtime that supplies `dash` (data, calc, draw, params, colors) and d3; this file supplies a small stand-in for `dash`
(below) and inlines d3 v7.9.0 (ISC licence, text kept in the output). d3 is taken from --d3 or downloaded from jsDelivr, and its
sha256 must equal D3_SHA256, the build the page was tested with.
"""
import os, sys, json, glob, hashlib, argparse, urllib.request, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.abspath(os.path.join(HERE, "..", "results", "portfolio", "report"))
D3_URL = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"
D3_SHA256 = "f2094bbf6141b359722c4fe454eb6c4b0f0e42cc10cc7af921fc158fceb86539"
LIVE = "https://claude.ai/artifact/QRh9Gy181Wsd2pn7uYgx8K"
D3_LICENSE = """Copyright 2010-2023 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE."""

CSS = """
:root{color-scheme:light dark;--color-fg:#1f1e1d;--color-fg-muted:#6b6a68;--color-bg:#faf9f5;--color-panel:#ffffff;--color-border-line:#e6e4dd;
--color-ok:#2f7d4f;--color-warn:#b7791f;--color-bad:#c2412d;--cds-chart-muted:#bdbbb5;--cds-chart-status-critical:#c2412d;--cds-chart-grid:#ecebe6;
--cds-chart-axis:#c9c7c0;--cds-chart-reference:#9a9893;--cds-text-secondary:#6b6a68;--cds-surface-popover:#ffffff;--cds-border:#e6e4dd;--c0:#3b6fd8;--c1:#d9822b}
@media (prefers-color-scheme: dark){:root{--color-fg:#ecebe6;--color-fg-muted:#a3a19b;--color-bg:#1f1e1d;--color-panel:#2a2927;--color-border-line:#3a3936;
--color-ok:#5fbf84;--color-warn:#e0a84a;--color-bad:#ef7a63;--cds-chart-muted:#6b6965;--cds-chart-status-critical:#ef7a63;--cds-chart-grid:#353431;
--cds-chart-axis:#55534f;--cds-chart-reference:#7d7b76;--cds-text-secondary:#a3a19b;--cds-surface-popover:#33322f;--cds-border:#3a3936;--c0:#7aa2f7;--c1:#f0a35e}}
:root{--font-anthropic-sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--font-anthropic-serif:Georgia,"Times New Roman",serif;
--cds-font-size-caption:12px;--cds-font-size-body:15px;--cds-font-size-heading:19px;--cds-font-size-title:28px;--cds-font-weight-medium:600;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:12px;--cds-gap-lg:16px;--cds-gap-xl:28px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:16px;--cds-pad-xl:24px;--cds-radius:8px;
--cds-shadow-popover:0 4px 16px rgba(0,0,0,.18)}
*{box-sizing:border-box}
body{margin:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:15px;line-height:1.45}
#dash-root{max-width:1180px;margin:0 auto;padding:16px}
.dash-select{font:inherit;color:var(--color-fg);background-color:var(--color-panel);border:1px solid var(--color-border-line);border-radius:var(--cds-radius);padding:6px 10px}
.dash-skeleton{opacity:.5}
.ofl-banner{max-width:1180px;margin:0 auto;padding:10px 16px 0;font-size:12px;color:var(--color-fg-muted)}
.ofl-banner a{color:inherit}
"""

RUNTIME = r"""
(function () {
  var DATA = __DATA__, sets = {}, calcs = {}, draws = {}, onDatas = [], params = {env: '3.6'}, pending = null;
  Object.keys(DATA).forEach(function (k) { sets[k] = d3.csvParse(DATA[k]); });
  function data(id) {
    if (sets[id]) return {status: 'ok', data: sets[id], meta: {}};
    if (calcs[id]) { var c = calcs[id]; return {status: 'ok', data: c.fn.apply(null, c.inputs.map(function (i) { return data(i).data; }))}; }
    return {status: 'missing', data: []};
  }
  function runDraws() {
    onDatas.forEach(function (f) { try { f(); } catch (e) { console.error('onData', e); } });
    Object.keys(draws).forEach(function (name) {
      document.querySelectorAll('[data-draw="' + name + '"]').forEach(function (el) {
        if (el.closest('[hidden]')) return;
        try { draws[name](el); } catch (e) { console.error(name, e); }
      });
    });
  }
  window.dash = {
    data: data, calc: function (id, o) { calcs[id] = o; }, onData: function (f) { onDatas.push(f); },
    draw: function (n, f) { if (f) draws[n] = f; else runDraws(); },
    colors: ['var(--c0)', 'var(--c1)'], params: function () { return params; },
    setParams: function (p) { Object.assign(params, p); runDraws(); }, resetParams: function () { params = {env: '3.6'}; runDraws(); },
    refresh: function () {}, setLink: function () {}, loader: function () {}, __run: runDraws
  };
  window.addEventListener('resize', function () { clearTimeout(pending); pending = setTimeout(runDraws, 120); });
})();
"""


def get_d3(path=None):
    if path:
        raw = open(path, "rb").read()
    else:
        raw = urllib.request.urlopen(D3_URL, timeout=60).read()
    if hashlib.sha256(raw).hexdigest() != D3_SHA256:
        raise SystemExit("d3 build differs from the one the page was tested with (D3_SHA256); pass --d3 with d3@7.9.0 dist/d3.min.js")
    return raw.decode("utf-8")


def build(report_dir=REPORT, d3_js=None, built=None):
    page = open(os.path.join(report_dir, "index.html"), encoding="utf-8").read()
    csvs = {os.path.basename(f)[:-4]: open(f, encoding="utf-8").read() for f in sorted(glob.glob(os.path.join(report_dir, "*.csv")))}
    esc = lambda s: s.replace("</", "<\\/").replace("<!--", "<\\!--")        # nothing inside a script may close it or open a comment
    built = built or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    parts = [
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<title>Timeless 10 + v2: portfolio backtest report (offline copy)</title><style>" + CSS + "</style>",
        "<!-- d3 v7.9.0 (https://d3js.org) is inlined below.\n" + D3_LICENSE + "\n-->",
        "<script>" + esc(d3_js) + "</script>",
        "<script>" + esc(RUNTIME.replace("__DATA__", json.dumps(csvs))) + "</script></head><body>",
        f"<div class=\"ofl-banner\">Offline copy, built {built} by research/portfolio/make_offline_report.py from research/results/portfolio/report/. "
        f"The figures are fixed backtest output. Live version (private to the owner's account): <a href=\"{LIVE}\">{LIVE}</a></div>",
        "<noscript><p style=\"padding:16px\">This report draws its charts with JavaScript; please enable it.</p></noscript>",
        "<div id=\"dash-root\"></div>",
        "<script>(function(){var root=document.getElementById('dash-root');root.innerHTML=" + esc(json.dumps(page)) + ";"
        "Array.prototype.forEach.call(root.querySelectorAll('script'),function(s){var n=document.createElement('script');n.textContent=s.textContent;s.replaceWith(n);});"
        "dash.__run();})();</script></body></html>\n"]
    return "\n".join(parts)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--d3"); ap.add_argument("--out", default=os.path.join(REPORT, "report_offline.html"))
    a = ap.parse_args()
    html = build(d3_js=get_d3(a.d3))
    open(a.out, "w", encoding="utf-8").write(html)
    print(f"wrote {os.path.relpath(a.out, os.getcwd())} ({len(html) / 1024:.0f} KB)")
