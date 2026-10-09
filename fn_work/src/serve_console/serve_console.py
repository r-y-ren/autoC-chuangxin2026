# R10 顶层：Web 操控台——REST+WS+静态单页（急停硬通道+selftest 自检）（责任文档：serve_console）
from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.testclient import TestClient

from src.shared.estop import EstopManager

from src.serve_console.render_static_pages import STATUS_BAR_HTML, _CSS

_PAGE = _CSS + """<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8"><title>无人机链路抗干扰测评台</title></head><body>
<header class="panel" style="max-width:960px"><h1>无人机链路抗干扰测评台</h1>
<span id="st">state: -</span></header>
""" + STATUS_BAR_HTML + """
<section class="panel" id="dashboard"><h2>结果仪表盘</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px">
<div id="card-latest" class="panel" style="margin:0">加载中…</div>
<div id="card-model" class="panel" style="margin:0">加载中…</div>
<div id="card-capability" class="panel" style="margin:0">加载中…</div>
</div>
<div id="card-history" class="panel" style="margin:10px 0 0">加载中…</div>
</section>
<section class="panel"><h2>场景卡片</h2><div id="cards">加载中…</div>
<button class="btn btn-primary" onclick="api('/api/run','POST',{scenario:current})">开始</button>
<button class="btn" onclick="api('/api/stop','POST',{})">停止</button>
<button class="btn btn-danger" id="estop" onclick="api('/api/estop','POST',{})">急 停</button>
<span style="margin-left:10px"><a href="/reports">报告中心</a> · <a href="/help">帮助</a></span></section>
<section class="panel"><h2>运行进度</h2><div id="progress-card" style="font-family:ui-monospace,monospace">待机</div></section>\n''<section class="panel"><h2>实时双曲线（丢包率 / 相对吞吐）</h2><canvas id="kpi-chart" width="900" height="220" style="width:100%;background:#0a0f18;border-radius:8px"></canvas><div id="chart-tip" style="color:#8fa3c0;font-size:.85em">悬停曲线读数值</div></section>\n''<section class="panel"><h2>功率预览（拖滑杆）</h2><input id="power-slider" type="range" min="-20" max="40" value="0" step="5" style="width:70%"><span id="preview-read" style="font-family:ui-monospace,monospace;margin-left:10px"></span><canvas id="preview-chart" width="900" height="120" style="width:100%;background:#0a0f18;border-radius:8px;margin-top:6px"></canvas></section>\n''<section class="panel"><h2>事件时间线</h2><div id="timeline" style="max-height:180px;overflow:auto"></div></section>\n'
'<section class="panel"><h2>实时数据</h2><div id="log" style="white-space:pre-wrap;font-family:ui-monospace,monospace;font-size:12px;max-height:220px;overflow:auto"></div></section>
<section class="panel"><h2>历史运行</h2><div id="runs">-</div></section>
<script>
let current=null;
const NL=String.fromCharCode(10);
const hist={per:[],thr:[]};
function api(p,m,b){return fetch(p,{method:m||'GET',headers:{'Content-Type':'application/json'},body:b?JSON.stringify(b):null}).then(r=>r.json())}
function drawChart(){const c=document.getElementById('kpi-chart');if(!c)return;const g=c.getContext('2d');
g.clearRect(0,0,c.width,c.height);g.strokeStyle='#243352';g.beginPath();g.moveTo(40,10);g.lineTo(40,c.height-24);g.lineTo(c.width-10,c.height-24);g.stroke();
function line(arr,color){if(arr.length<2)return;g.strokeStyle=color;g.beginPath();
arr.forEach((v,i)=>{const x=40+(c.width-50)*i/Math.max(arr.length-1,1);const y=10+(c.height-34)*(1-v);i?g.lineTo(x,y):g.moveTo(x,y)});g.stroke()}
line(hist.per,'#e74c3c');line(hist.thr,'#2ecc71');g.fillStyle='#8fa3c0';g.fillText('1.0',6,16);g.fillText('0.0',6,c.height-28)}
function drawPreview(curve){const c=document.getElementById('preview-chart');if(!c||!curve)return;const g=c.getContext('2d');
g.clearRect(0,0,c.width,c.height);g.strokeStyle='#243352';g.beginPath();g.moveTo(40,8);g.lineTo(40,c.height-20);g.lineTo(c.width-10,c.height-20);g.stroke();
g.strokeStyle='#4da3ff';g.beginPath();curve.forEach((pt,i)=>{const x=40+(c.width-50)*i/Math.max(curve.length-1,1);const y=8+(c.height-28)*(1-pt.per);i?g.lineTo(x,y):g.moveTo(x,y)});g.stroke()}
function pushTimeline(m){const tl=document.getElementById('timeline');if(!tl)return;const d=document.createElement('div');
const label=(m.type==='injection'?'注入 '+(m.style||'')+' @'+(m.power_db??'')+'dB':m.type==='fail'?'失效 @'+(m.power_db??'')+'dB':m.type==='gap'?'断连':m.type);
d.textContent=label;d.style.cssText='padding:3px 8px;margin:2px 0;background:#1b2740;border-left:3px solid '+(m.type==='fail'?'#e74c3c':m.type==='injection'?'#4da3ff':'#f1c40f')+';border-radius:6px;transition:background .8s';
d.style.background='#3a2b12';setTimeout(()=>{d.style.background='#1b2740'},800);tl.prepend(d);while(tl.children.length>60)tl.removeChild(tl.lastChild)}
function onFrame(m){if(m.type==='kpi'){hist.per.push(m.per);hist.thr.push(1-m.per);if(hist.per.length>240){hist.per.shift();hist.thr.shift()}drawChart();
const lg=document.getElementById('log');if(lg){lg.textContent+=(m.link||'')+' PER='+Number(m.per).toFixed(3)+NL;if(lg.scrollHeight>2000)lg.textContent=lg.textContent.slice(-1500);lg.scrollTop=lg.scrollHeight}
const pc=document.getElementById('progress-card');if(pc&&m.link)pc.dataset.last='最新 '+(m.link||'')+' PER='+(m.per||0).toFixed(3)}
else if(m.type==='progress'){const pc=document.getElementById('progress-card');if(pc)pc.textContent='第 '+m.index+'/'+m.total+' 步 · '+(m.style||'')+' · 功率 '+(m.power_db??'')+'dB · 已用 '+(m.elapsed_s??0)+'s'}
else if(m.type==='event'||m.type==='injection'||m.type==='fail'||m.type==='gap'){pushTimeline(m)}
else if(m.type==='idle'){const st=document.getElementById('st');if(st)st.textContent='state: idle'}}
(async()=>{const s=await api('/api/scenarios');const d=document.getElementById('cards');d.innerHTML='';
for(const n of s.scenarios){const b=document.createElement('button');b.className='btn';b.textContent=n;
b.onclick=()=>{current=n;document.querySelectorAll('#cards button').forEach(x=>x.style.borderColor='');b.style.borderColor='#4da3ff'};d.appendChild(b)}})();
(async()=>{const r=await api('/api/runs');document.getElementById('runs').textContent=JSON.stringify(r.runs)})();
const ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws');
ws.onmessage=e=>{try{onFrame(JSON.parse(e.data))}catch(err){}};
const slider=document.getElementById('power-slider');
if(slider){slider.oninput=()=>{api('/api/preview?power_db='+slider.value+'&fail_power_db=10').then(d=>{
const rd=document.getElementById('preview-read');if(rd)rd.textContent='预览 PER=' + d.per.toFixed(3) + '（该强度下链路丢包预估）';drawPreview(d.curve)})}}
const chart=document.getElementById('kpi-chart');
if(chart){chart.onmousemove=ev=>{const r=chart.getBoundingClientRect();const i=Math.round((ev.clientX-r.left)/r.width*Math.max(hist.per.length-1,0));
const tip=document.getElementById('chart-tip');if(tip&&hist.per[i]!==undefined)tip.textContent='样本'+i+': 丢包率='+hist.per[i].toFixed(3)+' 相对吞吐='+hist.thr[i].toFixed(3)}}
drawChart();
</script>
<script src="/dashboard.js"></script></body></html>"""



def create_app():
    from src.shared.runtime_feed import RuntimeFeed
    app = FastAPI(title="linkbench console")
    estop = EstopManager()  # 操控台与运行场景共享的硬急停通道
    feed = RuntimeFeed()
    app.state.feed = feed
    state = {"run_thread": None, "last_result": None, "feed": feed}

    @app.get("/api/health")
    def health():
        return {"ok": True, "state": estop.state}

    @app.get("/api/devices")
    def devices():
        from src.serve_console.probe_device_status import probe_device_status
        return {"devices": probe_device_status()}

    @app.get("/api/scenarios")
    def scenarios():
        d = Path(__file__).resolve().parents[2] / "scenarios"
        names = sorted(p.stem for p in d.glob("*.yaml")) if d.exists() else []
        return {"scenarios": names}

    @app.post("/api/run")
    def run(payload: dict):
        from src.execute_scenario.execute_scenario import execute_scenario
        name = str(payload.get("scenario", "smoke_loop"))
        d = Path(__file__).resolve().parents[2] / "scenarios"
        card = d / (name + ".yaml")

        def _work():
            try:
                state["last_result"] = execute_scenario(card, estop=estop,
                                                        feed=state["feed"])
            except Exception as exc:  # noqa: BLE001
                estop.fire("ui-run 异常: %s" % exc)

        th = threading.Thread(target=_work, daemon=True)
        state["run_thread"] = th
        th.start()
        return {"started": name}

    @app.post("/api/stop")
    def stop():
        estop.fire("ui-stop")
        return {"state": estop.state}

    @app.post("/api/estop")
    def estop_ep():
        estop.fire("ui-estop")
        return {"state": estop.state}

    @app.get("/api/preview")
    def preview(power_db: float = 0.0, fail_power_db: float = 10.0,
                base_per: float = 0.0):
        from src.shared.per_response_model import per_response_model
        curve = [{"power_db": x,
                  "per": per_response_model(x, fail_power_db, base_per)}
                 for x in range(-20, 41, 5)]
        return {"per": per_response_model(power_db, fail_power_db, base_per),
                "curve": curve, "power_db": power_db}

    @app.get("/api/dashboard")
    def dashboard():
        from src.serve_console.collect_dashboard import collect_dashboard
        return collect_dashboard()

    @app.post("/api/seed_demo")
    def seed_demo():
        if state.get("seeding"):
            return {"started": False, "reason": "演示数据生成中"}
        from src.run_demo.run_demo import run_demo

        def _seed():
            state["seeding"] = True
            try:
                state["last_result"] = run_demo(quick=True)
            except Exception as exc:  # noqa: BLE001
                estop.fire("seed_demo 异常: %s" % exc)
            finally:
                state["seeding"] = False
        import threading as _th
        _th.Thread(target=_seed, daemon=True).start()
        return {"started": True}

    @app.get("/api/runs")
    def runs():
        d = Path("runs")
        return {"runs": sorted(p.name for p in d.iterdir()) if d.exists() else []}

    @app.get("/api/runs/{name}/report")
    def run_report(name: str):
        p = Path("runs") / name / "report.md"
        if not p.exists():
            return {"error": "no report", "name": name}
        return {"name": name, "report": p.read_text(encoding="utf-8")}

    @app.post("/api/demo")
    def demo():
        from src.run_demo.run_demo import run_demo

        def _work():
            state["last_result"] = run_demo(quick=True)
        threading.Thread(target=_work, daemon=True).start()
        return {"started": True}

    @app.get("/dashboard.js")
    def dashboard_js():
        from fastapi.responses import FileResponse
        return FileResponse(Path(__file__).resolve().parent / "static" / "dashboard.js",
                            media_type="application/javascript")

    @app.get("/", response_class=HTMLResponse)
    def page():
        return _PAGE

    # [改造←R13] 报告中心/帮助页 + runs 媒体目录（演进轮一增量挂载）
    from starlette.staticfiles import StaticFiles
    _runs = Path("runs")
    app.mount("/runs-media", StaticFiles(directory=str(_runs), check_dir=False),
              name="runsmedia")
    from src.serve_console.render_static_pages import render_static_pages
    render_static_pages(app)

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        from src.serve_console.ws_stream_feed import ws_stream_feed
        await ws.accept()
        await ws_stream_feed(ws, state["feed"])

    return app


def serve_console(*, host: str = "0.0.0.0", port: int = 8000, selftest: bool = False):
    # selftest：四点无头自检（服务构建/健康/急停生效/WS 心跳）→返回退出码
    app = create_app()
    if selftest:
        with TestClient(app) as c:
            h = c.get("/api/health")
            assert h.status_code == 200 and h.json()["ok"]
            sc = c.get("/api/scenarios")
            assert sc.status_code == 200 and len(sc.json()["scenarios"]) >= 1
            e = c.post("/api/estop")
            assert e.status_code == 200 and e.json()["state"].startswith("fired")
            with c.websocket_connect("/ws") as ws:
                msg = ws.receive_json()
                assert "type" in msg   # typed 帧（kpi/event/progress/idle）
            dv = c.get("/api/devices").json()["devices"]
            assert len(dv) >= 6 and any(e["id"] == "b210" for e in dv)
            assert all(e["status"] in ("ok", "missing", "pending_manual", "manual_ok")
                       for e in dv)
            for path in ("/", "/reports", "/help"):
                html = c.get(path).text
                assert "device-bar" in html and "--accent" in html, path
            import subprocess
            import shutil as _sh
            if _sh.which("node"):
                js = _PAGE.split("<script>")[-1].split("</script>")[0]
                r = subprocess.run(["node", "--check", "--input-type=module"],
                                   input=js, capture_output=True, text=True)
                assert r.returncode == 0, "主页 JS 语法错误：%s" % r.stderr[:200]
        print("SELFTEST OK: health/scenarios/estop/ws/devices/页面结构(+JS语法) 全过")
        return 0
    import uvicorn
    uvicorn.run(app, host=host, port=port)
    return 0
