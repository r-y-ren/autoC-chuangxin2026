# resume_from 单测：半程/完成/损坏三分支
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.execute_scenario.plan_steps import Step  # noqa: E402
from src.execute_scenario.resume_from import resume_from  # noqa: E402


def _plan():
    return [Step(index=i, style="cw", power_db=p, duration_s=1)
            for i, p in enumerate(range(-5, 16, 5))]


def _write_steps(d: Path, n: int):
    recs = [{"style": "cw", "power_db": p, "t_start_ms": 0, "t_end_ms": 1,
             "failed": False, "failure_kind": ""} for p in range(-5, 16, 5)][:n]
    (d / "steps.jsonl").write_text(
        "\n".join(json.dumps(r) for r in recs), encoding="utf-8")


def test_half(tmp_path):
    _write_steps(tmp_path, 2)
    start, done, finished = resume_from(tmp_path, _plan())
    assert start == 2 and len(done) == 2 and finished is False


def test_finished(tmp_path):
    _write_steps(tmp_path, 5)
    start, done, finished = resume_from(tmp_path, _plan())
    assert finished is True and start == 5


def test_corrupt(tmp_path):
    (tmp_path / "steps.jsonl").write_text("{broken", encoding="utf-8")
    start, done, finished = resume_from(tmp_path, _plan())
    assert (start, done, finished) == (0, [], False)
