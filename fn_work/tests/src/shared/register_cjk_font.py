# register_cjk_font 单测：注册生效+渲染中文零缺字告警
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.shared.register_cjk_font import register_cjk_font  # noqa: E402


def test_register_and_render_no_glyph_warning():
    name = register_cjk_font()
    assert name and ("CJK" in name or "SC" in name or "Noto" in name or "Wen" in name)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fig, ax = plt.subplots()
        ax.set_title("干扰电平曲线（误码率测试）")
        ax.set_xlabel("时间 ms"); ax.set_ylabel("吞吐/误码")
        fig.canvas.draw()
        plt.close(fig)
        glyph_warns = [x for x in w if "missing from font" in str(x.message)]
        assert not glyph_warns, [str(x.message) for x in glyph_warns[:2]]
    assert register_cjk_font() == name  # 幂等
