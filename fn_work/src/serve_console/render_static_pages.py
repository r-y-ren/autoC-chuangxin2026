# 操控台静态页：统一深色驾驶舱样式 + 设备状态条 + /reports 与 /help（R13+R18）
from __future__ import annotations

from pathlib import Path

_CSS = '<style>\n:root{--bg:#0d1220;--panel:#141c2e;--border:#243352;--text:#dbe4f0;--muted:#8fa3c0;\n--accent:#4da3ff;--ok:#2ecc71;--warn:#f1c40f;--danger:#e74c3c;--mono:ui-monospace,monospace}\nbody{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif}\na{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}\n.panel{background:var(--panel);border:1px solid var(--border);border-radius:12px;\npadding:16px 18px;margin:12px auto;max-width:960px;box-shadow:0 4px 14px rgba(0,0,0,.25)}\nh1{font-size:1.35em;margin:.2em 0}h2{font-size:1.1em;color:var(--accent)}\n.btn{border:1px solid var(--border);background:#1b2740;color:var(--text);padding:9px 16px;\nborder-radius:10px;cursor:pointer;font-size:.95em;margin:4px}\n.btn:hover{border-color:var(--accent)}\n.btn-primary{background:var(--accent);border-color:var(--accent);color:#08122a;font-weight:600}\n.btn-danger{background:var(--danger);border-color:var(--danger);color:#fff;font-weight:700}\n.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--border);\nborder-radius:999px;padding:4px 12px;margin:3px;font-size:.82em;background:#101a2e}\n.dot{width:9px;height:9px;border-radius:50%;display:inline-block}\n.dot.ok{background:var(--ok)}.dot.missing{background:var(--danger)}\n.dot.pending_manual{background:var(--warn)}.dot.manual_ok{background:var(--ok)}\n.badge{background:var(--danger);color:#fff;border-radius:999px;padding:1px 8px;font-size:.75em}\ntable{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:.86em}\nth,td{padding:6px 10px;border-bottom:1px solid var(--border);text-align:left}\ntr:nth-child(even) td{background:#101a2e}\npre{background:#0a0f18;padding:10px;border-radius:10px;overflow:auto;font-family:var(--mono);font-size:.85em}\nimg{max-width:100%;border-radius:8px;border:1px solid var(--border)}\ndetails summary{cursor:pointer;color:var(--muted)}\ncode{font-family:var(--mono);background:#0a0f18;padding:1px 6px;border-radius:6px}\n</style>'
STATUS_BAR_HTML = '<div class="panel" id="device-bar" style="max-width:960px">\n<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">\n<b>设备状态</b><span id="dev-badge"></span>\n<button class="btn" onclick="lbDev(true)">刷新</button>\n</div>\n<div id="dev-chips" style="margin-top:8px">探测中…</div>\n<details style="margin-top:8px"><summary>明细与人工确认（屏蔽箱/天线几何/供电 Hub）</summary>\n<div id="dev-detail"></div></details>\n</div>\n<script>\nasync function lbDev(manual){try{\nconst r=await fetch(\'/api/devices\');const d=await r.json();const devs=d.devices||[];\nconst saved=JSON.parse(localStorage.getItem(\'lb_manual\')||\'{}\');\nconst chips=document.getElementById(\'dev-chips\');const det=document.getElementById(\'dev-detail\');\nif(chips)chips.innerHTML=devs.map(e=>{\nconst st=(e.status===\'pending_manual\'&&saved[e.id])?\'manual_ok\':e.status;\nreturn \'<span class="chip"><span class="dot \'+st+\'"></span>\'+e.name+\'</span>\';}).join(\'\');\nconst miss=devs.filter(e=>e.status===\'missing\').length;\nconst bg=document.getElementById(\'dev-badge\');\nif(bg)bg.innerHTML=miss?\'<span class="badge">缺 \'+miss+\' 件</span>\':\'<span class="badge" style="background:#2ecc71">齐</span>\';\nif(det)det.innerHTML=\'<table><tr><th>设备</th><th>状态</th><th>说明</th></tr>\'+\ndevs.map(e=>{\nconst man=e.status===\'pending_manual\';\nconst st=(man&&saved[e.id])?\'manual_ok\':e.status;\nconst tick=man?\' <label><input type="checkbox" \'+(saved[e.id]?\'checked\':\'\')+\n\' onchange="lbTick(\\\'\'+e.id+\'\\\',this.checked)"> 已确认</label>\':\'\';\nreturn \'<tr><td>\'+e.name+\'</td><td><span class="dot \'+st+\'"></span> \'+st+tick+\n\'</td><td>\'+e.detail+\'</td></tr>\';}).join(\'\')+\'</table>\';\n}catch(e){const c=document.getElementById(\'dev-chips\');\nif(c)c.textContent=\'状态探测失败：\'+e;}if(manual)return;}\nfunction lbTick(id,v){const s=JSON.parse(localStorage.getItem(\'lb_manual\')||\'{}\');\ns[id]=v;localStorage.setItem(\'lb_manual\',JSON.stringify(s));lbDev();}\nsetInterval(function(){lbDev();},5000);lbDev();\n</script>'
HELP_HTML = '<h1>快速上手（五步）</h1>\n<ol>\n<li>看上方<b>设备状态</b>条：绿灯就绪、红灯缺件、黄灯待办（屏蔽箱等物理件勾“已确认”）</li>\n<li>在主页"场景卡片"点一张卡（比如"国标·噪声干扰"）</li>\n<li>点<b>开始</b>——实时数据区滚动链路表现</li>\n<li>跑完到<a href="/reports">报告中心</a>点开运行，看曲线和失效电平表</li>\n<li>任何时候点红色<b>急停</b>——干扰立即停止</li>\n</ol>\n<p style="color:#8fa3c0">提示：历史测试可在报告中心对比；所有数字来自当次实测，可复现。当前为合成数据模式（未接硬件时全链路可演示）。</p>'


def _md_to_html(text: str, run: str | None = None) -> str:
    out, table = [], []
    for ln in text.splitlines():
        if ln.startswith("|"):
            table.append(ln)
            continue
        if table:
            out.append("<table><tr><th>" + "</th><th>".join(
                c.strip() for c in table[0].strip("|").split("|"))
                + "</th></tr>" + "".join(
                "<tr><td>" + "</td><td>".join(c.strip() for c in row.strip("|").split("|"))
                + "</td></tr>" for row in table[2:]) + "</table>")
            table = []
        if ln.startswith("# "):
            out.append("<h1>" + ln[2:] + "</h1>")
        elif ln.startswith("## "):
            out.append("<h2>" + ln[3:] + "</h2>")
        elif ln.startswith("> "):
            out.append("<p style='color:#8fa3c0'>" + ln[2:] + "</p>")
        elif ln.startswith("![") and "](" in ln:
            alt = ln[2:ln.index("]")]
            src = ln[ln.index("](") + 2:-1]
            if run:
                src = "/runs-media/%s/%s" % (run, src)
            out.append("<p><img alt='%s' src='%s'></p>" % (alt, src))
        elif ln.strip():
            out.append("<p>" + ln + "</p>")
    if table:
        out.append("<pre>" + "\n".join(table) + "</pre>")
    return "\n".join(out)


def render_static_pages(app) -> None:
    # 在既有 app 上挂 /reports 与 /help（页顶同挂设备状态条）
    from fastapi.responses import HTMLResponse

    def page(body: str) -> str:
        return _CSS + STATUS_BAR_HTML + '<div class="panel">' + body + "</div>"

    @app.get("/reports", response_class=HTMLResponse)
    def reports_page():
        d = Path("runs")
        names = sorted((p.name for p in d.iterdir() if (p / "report.md").exists()),
                       reverse=True) if d.exists() else []
        rows = "".join('<tr><td><a href="/reports/%s">%s</a></td></tr>' % (n, n)
                       for n in names) or "<tr><td>（暂无历史测试）</td></tr>"
        return page('<h1>报告中心</h1><table><tr><th>运行</th></tr>' + rows + "</table>")

    @app.get("/reports/{name}", response_class=HTMLResponse)
    def report_detail(name: str):
        p = Path("runs") / name / "report.md"
        if not p.exists():
            return page('<h1>404</h1><p>没有这次运行：%s</p>'
                        '<p><a href="/reports">返回列表</a></p>' % name)
        return page('<p><a href="/reports">← 返回列表</a></p>'
                    + _md_to_html(p.read_text(encoding="utf-8"), run=name))

    @app.get("/help", response_class=HTMLResponse)
    def help_page():
        return page(HELP_HTML)
