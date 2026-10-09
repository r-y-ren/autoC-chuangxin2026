# 内置 OFL 中文字体注册进 matplotlib（幂等）；内置优先、系统探测兜底（R13）
from __future__ import annotations

from pathlib import Path

_registered: str | None = None


def register_cjk_font() -> str:
    # 返回生效字体名；内置与系统皆无→RuntimeError（打包错误立即暴露）
    global _registered
    if _registered:
        return _registered
    import matplotlib
    from matplotlib import font_manager

    fonts_dir = Path(__file__).resolve().parent / "fonts"
    name = None
    for f in sorted([*fonts_dir.glob("*.otf"), *fonts_dir.glob("*.ttf")]):
        font_manager.fontManager.addfont(str(f))
        name = font_manager.FontProperties(fname=str(f)).get_name()
    if name is None:
        for cand in ("Noto Sans CJK SC", "Noto Sans SC", "Noto Sans CJK TC",
                     "WenQuanYi Zen Hei", "WenQuanYi Micro Hei", "Source Han Sans SC"):
            try:
                font_manager.findfont(font_manager.FontProperties(family=cand),
                                      fallback_to_default=False)
                name = cand
                break
            except Exception:  # noqa: BLE001
                continue
    if name is None:
        raise RuntimeError("无可用中文字体：请将 OFL 字体放入 src/shared/fonts/ "
                           "或安装 Noto Sans CJK / 文泉驿")
    matplotlib.rcParams["font.sans-serif"] = [name] + \
        list(matplotlib.rcParams.get("font.sans-serif", []))
    matplotlib.rcParams["axes.unicode_minus"] = False
    _registered = name
    return name
