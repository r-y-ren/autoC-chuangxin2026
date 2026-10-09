# R1 顶层：按注入段逐样式合成→后端发射→SigMF 归档（责任文档：generate_jamming）
from __future__ import annotations

from pathlib import Path

from src.create_instrument_backend.create_instrument_backend import create_instrument_backend
from src.generate_jamming.synthesize_style import synthesize_style
from src.shared.write_sigmf import write_sigmf


def generate_jamming(spec, *, dry_run: bool = False, out_dir=None, backend: str = "b210"):
    # spec=InjectionSpec；dry_run 只产参数表；任何失败先停发再返回
    out_dir = Path(out_dir) if out_dir else Path("runs") / "gen"
    errors: list[str] = []
    param_table: list[dict] = []
    sigmf_paths: list[Path] = []
    style_metas: list[dict] = []

    try:
        jammer, _analyzer = create_instrument_backend(backend)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "dry_run": dry_run, "sigmf_paths": [], "style_meta": [],
                "errors": [f"后端不可用: {exc}"]}

    for style in (spec.styles if spec else []):
        params = dict(spec.params or {})
        params.update({"freq_hz": spec.freq_hz, "bandwidth_hz": spec.bandwidth_hz,
                       "duration_s": spec.step_duration_s})
        try:
            iq, meta = synthesize_style(style, params)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{style}: 合成失败 {exc}")
            continue
        row = {"style": style, "freq_hz": spec.freq_hz, "bandwidth_hz": spec.bandwidth_hz,
               "power_db": spec.power_start_db, "duration_s": spec.step_duration_s}
        param_table.append(row)
        style_metas.append(meta)

        if dry_run:
            continue
        try:
            jammer.set_style(style, params)
            jammer.set_power_db(spec.power_start_db)
            jammer.on()
            base = out_dir / f"{style}_{abs(hash(style)) % 10000}"
            ann = [{"style": style, "power_db": spec.power_start_db,
                    "t_start_s": 0.0, "t_end_s": spec.step_duration_s}]
            sigmf_paths.append(write_sigmf(base, iq, ann,
                                           sample_rate_sps=meta["sample_rate_sps"]))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{style}: 发射/归档失败 {exc}")
        finally:
            jammer.off()

    return {"ok": not errors, "dry_run": dry_run,
            "param_table": param_table, "sigmf_paths": sigmf_paths,
            "style_meta": style_metas, "errors": errors}
