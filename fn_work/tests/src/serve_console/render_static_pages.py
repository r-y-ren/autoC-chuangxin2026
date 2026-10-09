# render_static_pages 单测：报告列表/详情/帮助页（经 create_app 集成）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.serve_console.serve_console import create_app  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402


def test_reports_and_help(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    r = tmp_path / "runs" / "runA"
    r.mkdir(parents=True)
    (r / "report.md").write_text("# 测评报告\n\n## 失效电平表\n\n| 样式 | dB |\n|---|---|\n| cw | -5 |\n\n![per_vs_jsr](figs/per_vs_jsr.png)\n", encoding="utf-8")
    app = create_app()
    with TestClient(app) as c:
        lst = c.get("/reports")
        assert lst.status_code == 200 and "runA" in lst.text
        det = c.get("/reports/runA")
        assert det.status_code == 200 and "失效电平表" in det.text
        assert "/runs-media/runA/figs/per_vs_jsr.png" in det.text
        missing = c.get("/reports/nope")
        assert missing.status_code == 200 and "404" in missing.text
        help_ = c.get("/help")
        assert help_.status_code == 200 and "急停" in help_.text and "五步" in help_.text
