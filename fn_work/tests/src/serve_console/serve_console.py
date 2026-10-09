# serve_console 单测：selftest 四点 + 页面可达
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.serve_console.serve_console import create_app  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


def test_health_scenarios_page():
    app = create_app()
    with TestClient(app) as c:
        assert c.get("/api/health").json()["ok"]
        assert len(c.get("/api/scenarios").json()["scenarios"]) >= 4
        html = c.get("/").text
        assert "急" in html and ("ws" in html.lower() or "websocket" in html.lower())


def test_estop_changes_state():
    app = create_app()
    with TestClient(app) as c:
        before = c.get("/api/health").json()["state"]
        r = c.post("/api/estop").json()["state"]
        assert before == "armed" and r.startswith("fired")


# ---- 演进轮二集成（R17/R18） ----


def test_r17_devices_endpoint():
    app = create_app()
    with TestClient(app) as c:
        devs = c.get("/api/devices").json()["devices"]
        assert len(devs) >= 6
        assert any(e["id"] == "b210" for e in devs)
        assert all(set(e) >= {"id", "name", "status", "detail", "ts"} for e in devs)


def test_r18_theme_and_status_bar_all_pages():
    app = create_app()
    with TestClient(app) as c:
        for path in ("/", "/reports", "/help"):
            html = c.get(path).text
            assert "device-bar" in html, path          # 状态栏挂载
            assert "--accent" in html, path            # 统一主题变量
            assert "dev-chips" in html, path
        home = c.get("/").text
        assert "急 停" in home and "btn-danger" in home  # 急停危险色醒目
        assert "报告中心" in home and "帮助" in home


def test_r18_page_js_syntax():
    import shutil
    import subprocess
    if not shutil.which("node"):
        import pytest
        pytest.skip("node 不可用，JS 语法断言转 selfcheck 承载")
    from src.serve_console.serve_console import _PAGE
    js = _PAGE.split("<script>")[-1].split("</script>")[0]
    res = subprocess.run(["node", "--check", "--input-type=module"],
                         input=js, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr[:300]


# ---- 演进轮三集成（R19/R20） ----


def test_r20_preview_matches_model():
    from src.shared.per_response_model import per_response_model
    app = create_app()
    with TestClient(app) as c:
        d = c.get("/api/preview?power_db=5&fail_power_db=10").json()
    assert d["per"] == per_response_model(5.0, 10.0)      # 预览=实测口径
    assert any(pt["per"] > 0 for pt in d["curve"]) and len(d["curve"]) >= 10


def test_r20_four_components_dom():
    app = create_app()
    with TestClient(app) as c:
        html = c.get("/").text
    # 真元素断言（含标签属性），防 JS 字符串假阳性
    assert '<canvas id="kpi-chart"' in html
    assert '<canvas id="preview-chart"' in html
    assert '<input id="power-slider"' in html
    assert 'id="timeline"' in html and "<div id=\"timeline\"" in html.replace("'", '"').replace('"""', '"')
    assert 'id="progress-card"' in html


def test_r19_ws_end_to_end_run(monkeypatch):
    # 端到端：/api/run 国标卡（高速）→ WS 3s 内 ≥5 条 kpi 且 per 非常数
    import time
    monkeypatch.setenv("LINKBENCH_SPEED", "80")
    app = create_app()
    with TestClient(app) as c:
        c.post("/api/run", json={"scenario": "gb42590_noise"})
        t0 = time.monotonic()
        kpis, t5 = [], None
        with c.websocket_connect("/ws") as ws:
            while time.monotonic() - t0 < 3.2 and (t5 is None or len(kpis) < 40):
                m = ws.receive_json()
                if m.get("type") == "kpi":
                    kpis.append(m)
                    if len(kpis) == 5:
                        t5 = time.monotonic() - t0
    assert len(kpis) >= 5 and t5 is not None and t5 <= 3.0   # R19：3s 内 ≥5 条
    assert len({m["per"] for m in kpis}) > 1                 # 全序列非常数
