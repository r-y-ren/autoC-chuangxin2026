# bridge_to_sitl 单测：时间线产出+模拟模式如实标注
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.bridge_to_sitl.bridge_to_sitl import bridge_to_sitl  # noqa: E402


def test_timeline_from_steps(tmp_path):
    (tmp_path / "steps.jsonl").write_text("\n".join(json.dumps(s) for s in [
        {"style": "cw", "power_db": 5, "t_start_ms": 0, "t_end_ms": 900,
         "failed": False},
        {"style": "cw", "power_db": 10, "t_start_ms": 900, "t_end_ms": 1800,
         "failed": True}]), encoding="utf-8")
    res = bridge_to_sitl(str(tmp_path))
    assert res["steps"] == 2
    rec = json.loads(Path(res["log"]).read_text(encoding="utf-8"))
    assert rec["mode"] in ("simulated", "pymavlink")
    assert rec["timeline"][1]["per_target"] == 1.0
    if rec["mode"] == "simulated":
        assert "模拟" in rec["note"] or "计划" in rec["note"]
