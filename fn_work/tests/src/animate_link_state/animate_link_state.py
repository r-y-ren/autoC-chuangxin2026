# animate_link_state 单测：分级状态机+波纹映射全覆盖
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.animate_link_state.animate_link_state import STYLE_WAVE, animate_link_state  # noqa: E402
from src.shared.load_scenario import KNOWN_STYLES  # noqa: E402


def _stream(pers):
    return [{"link": "wifi", "per": p} for p in pers]


def test_levels_and_callback():
    seen = []
    final = animate_link_state(_stream([0.0, 0.5, 0.85, 0.99]),
                               lambda st: seen.append(st), style="cw")
    assert final["links"]["wifi"] == "broken"
    assert [s["links"]["wifi"] for s in seen] == ["green", "yellow", "red", "broken"]
    assert seen[0]["wave"] == "rings"


def test_wave_table_covers_six_styles():
    assert set(STYLE_WAVE) == set(KNOWN_STYLES)
