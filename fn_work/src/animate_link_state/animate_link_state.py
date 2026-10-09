# R12 [P1]：样本流驱动光带/波纹动画状态机（非阻塞，渲染器无关）
from __future__ import annotations

STYLE_WAVE = {  # 样式→波纹形态（渲染层按此映射画法）
    "cw": "rings", "sweep": "moving-arc", "chirp": "sawtooth-trail",
    "noise_bandlimited": "diffuse", "partial_band": "band-glow", "pulse": "flash",
}


def _level(per: float) -> str:
    if per >= 0.95:
        return "broken"
    if per >= 0.8:
        return "red"
    if per >= 0.4:
        return "yellow"
    return "green"


def animate_link_state(stream, canvas, *, style: str | None = None):
    # stream=样本迭代器（DutSample 或含 per/link 的 dict）；canvas=状态回调 state dict
    # 返回末态 {links:{link:level}, wave}
    links: dict[str, str] = {}
    wave = STYLE_WAVE.get(style or "", "none") if style else "none"
    for s in stream:
        per = float(getattr(s, "per", None) if hasattr(s, "per") else s.get("per", 0.0))
        link = str(getattr(s, "link", None) if hasattr(s, "link") else s.get("link", "?"))
        links[link] = _level(per)
        canvas({"links": dict(links), "wave": wave, "per": per})
    return {"links": links, "wave": wave}
