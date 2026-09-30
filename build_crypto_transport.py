#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_json(path: Path):
    raw = path.read_bytes()
    return json.loads(raw), raw

def require(d, path):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise SystemExit(f"Missing required field: {path}")
        cur = cur[part]
    return cur

def trade_setup_min(ts):
    ts = ts or {}
    keys = [
        "available","setup_status","side","signal_time_utc","signal_age_1h_bars",
        "entry","stop_loss","t1","t2","t3","t4","t5",
        "t1_hit","t2_hit","t3_hit","t4_hit","t5_hit",
        "stop_loss_hit_after_entry","stop_hit_time_utc","tp5_completion_time_utc"
    ]
    return {k: ts.get(k) for k in keys}

def sniper_min(s):
    s = s or {}
    return {
        "status": s.get("status"),
        "signal": s.get("signal"),
        "bias": s.get("bias"),
        "bull_pct": s.get("bull_pct"),
        "bear_pct": s.get("bear_pct"),
        "current_closed_1h_bar_utc": s.get("current_closed_1h_bar_utc"),
        "current_closed_1h_bar_close_utc": s.get("current_closed_1h_bar_close_utc"),
        "trade_setup": trade_setup_min(s.get("trade_setup")),
    }

def sniper15_min(s):
    s = s or {}
    keys = [
        "status","current_state","directional_state","execution_timing_state",
        "bias","bull_pct","bear_pct","closed_bar_timestamp","closed_bar_close_utc",
        "exchange","instrument","same_exchange","closed_candles_only"
    ]
    return {k: s.get(k) for k in keys}

def joat_min(j):
    j = j or {}
    d = j.get("dashboard") or {}
    tr = j.get("trend") or {}
    rs = j.get("recent_strong_trigger") or {}
    sig = j.get("signals") or {}
    return {
        "status": j.get("status"),
        "current_closed_1h_bar_utc": j.get("current_closed_1h_bar_utc"),
        "trend": {"value": tr.get("value"), "alignment": tr.get("alignment")},
        "dashboard": {
            "strength": d.get("strength"),
            "compression": d.get("compression"),
            "acceleration": d.get("acceleration"),
            "volume_ratio": d.get("volume_ratio"),
            "mtf": d.get("mtf"),
        },
        "signals": {
            k: sig.get(k) for k in [
                "bull_cross","bear_cross","vol_confirmed_bull","vol_confirmed_bear",
                "compression_breakout","is_accelerating","mtf_aligned","is_compressed"
            ]
        },
        "recent_strong_trigger": {
            k: rs.get(k) for k in [
                "status","side","trigger_time_utc","age_1h_bars","freshness","display",
                "strength_pct","strength_status","volume_ratio","mtf_alignment_pct",
                "mtf_aligned","trend"
            ]
        },
    }

def dq_min(d):
    d = d or {}
    return {k: d.get(k) for k in [
        "same_exchange_all_timeframes","required_timeframes_pass",
        "current_cycle_1h_covered","latest_1h_start_utc","latest_1h_close_utc"
    ]}

def market_context_asset(a):
    return {
        "ticker": a.get("ticker"),
        "name": a.get("name"),
        "market": a.get("market"),
        "timeframe_states": a.get("timeframe_states"),
        "sniper": sniper_min(a.get("sniper")),
        "sniper_15m": sniper15_min(a.get("sniper_15m")),
        "joat": joat_min(a.get("joat")),
        "trend_4h": a.get("trend_4h"),
        "data_quality": dq_min(a.get("data_quality")),
    }

def build_4h_core(data, raw, source_path, role):
    for f in [
        "generated_at_utc","generated_at_europe_bucharest","pipeline_version",
        "current_hour_cycle.expected_latest_1h_close_utc",
        "current_hour_cycle.expected_latest_15m_close_utc",
        "current_hour_cycle.analysis_ready_assets",
        "current_hour_cycle.current_cycle_coverage_count",
        "current_hour_cycle.complete",
        "status.data_pipeline",
        "action_report.top_5_buy_with_trend",
        "action_report.top_5_sell_with_trend",
        "trend_engine_summary"
    ]:
        require(data, f)

    assets = data.get("assets") or []
    context = [market_context_asset(a) for a in assets if a.get("ticker") in {"BTC","ETH"}]

    return {
        "artifact_schema_version": "CRYPTO_4H_REPORT_CORE_V1",
        "artifact_role": role,
        "transport_projection_only": True,
        "methodology_impact": "NONE",
        "source_path": source_path,
        "source_sha256": sha256_bytes(raw),
        "source_size_bytes": len(raw),
        "generated_at_utc": data.get("generated_at_utc"),
        "generated_at_europe_bucharest": data.get("generated_at_europe_bucharest"),
        "pipeline_version": data.get("pipeline_version"),
        "report_mode": data.get("report_mode"),
        "reference_timezone": data.get("reference_timezone"),
        "current_hour_cycle": data.get("current_hour_cycle"),
        "universe": data.get("universe"),
        "status": data.get("status"),
        "provider_policy": data.get("provider_policy"),
        "action_report": data.get("action_report"),
        "trend_engine_summary": data.get("trend_engine_summary"),
        "market_context_assets": context,
    }

def rs_min(rti):
    rs = (rti or {}).get("relative_strength") or {}
    return {
        "status": rs.get("status"),
        "method": rs.get("method"),
        "vs_btc": rs.get("vs_btc"),
        "vs_eth": rs.get("vs_eth"),
    }

def early_asset(a):
    rti = a.get("report_technical_inputs") or {}
    d1 = ((rti.get("timeframes") or {}).get("1d") or {})
    execution = ((a.get("technical_engine") or {}).get("execution") or {})
    return {
        "rank": a.get("rank"),
        "id": a.get("id"),
        "name": a.get("name"),
        "ticker": a.get("ticker"),
        "exchange": a.get("exchange"),
        "instrument": a.get("instrument"),
        "market": a.get("market"),
        "timeframe_states": a.get("timeframe_states"),
        "sniper": sniper_min(a.get("sniper")),
        "sniper_15m": sniper15_min(a.get("sniper_15m")),
        "joat": joat_min(a.get("joat")),
        "trend_4h": a.get("trend_4h"),
        "early_ignition_metrics": {
            "rti_status": rti.get("status"),
            "rti_version": rti.get("version"),
            "frozen_at_utc": rti.get("frozen_at_utc"),
            "relative_strength": rs_min(rti),
            "volume_ratio20_1d": (d1.get("volume_participation") or {}).get("volume_ratio_20"),
            "change_24h_pct": (a.get("market") or {}).get("change_24h_pct"),
            "extension_atr": execution.get("extension_atr"),
        },
        "data_quality": dq_min(a.get("data_quality")),
    }

def build_early_core(data, raw, source_path):
    for f in [
        "generated_at_utc","generated_at_europe_bucharest","pipeline_version",
        "current_hour_cycle.expected_latest_1h_close_utc",
        "current_hour_cycle.expected_latest_15m_close_utc",
        "current_hour_cycle.analysis_ready_assets",
        "current_hour_cycle.current_cycle_coverage_count",
        "current_hour_cycle.current_15m_coverage_count",
        "current_hour_cycle.complete",
        "status.data_pipeline",
        "status.execution_15m",
        "trend_engine_summary.near_trigger_long",
        "assets"
    ]:
        require(data, f)

    te = data.get("trend_engine_summary") or {}
    te_keep = [
        "status","method_version","analysis_ready_assets","computed_assets","failed_assets",
        "qualifying_buy_count","qualifying_sell_count","watch_long_count","watch_short_count",
        "no_trade_count","near_trigger_long","near_trigger_short","ranking_rule","qualification_rule"
    ]

    return {
        "artifact_schema_version": "CRYPTO_EARLY_IGNITION_CORE_V1",
        "artifact_role": "EARLY_IGNITION_TRANSPORT_PROJECTION",
        "transport_projection_only": True,
        "methodology_impact": "NONE",
        "source_path": source_path,
        "source_sha256": sha256_bytes(raw),
        "source_size_bytes": len(raw),
        "generated_at_utc": data.get("generated_at_utc"),
        "generated_at_europe_bucharest": data.get("generated_at_europe_bucharest"),
        "pipeline_version": data.get("pipeline_version"),
        "report_mode": data.get("report_mode"),
        "reference_timezone": data.get("reference_timezone"),
        "current_hour_cycle": data.get("current_hour_cycle"),
        "universe": data.get("universe"),
        "status": data.get("status"),
        "provider_policy": data.get("provider_policy"),
        "trend_engine_summary": {k: te.get(k) for k in te_keep},
        "assets": [early_asset(a) for a in (data.get("assets") or [])],
    }

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--latest", default="crypto/latest_scan.json")
    p.add_argument("--previous", default="crypto/previous_4h_scan.json")
    p.add_argument("--out", default="public/crypto")
    args = p.parse_args()

    latest_path = Path(args.latest)
    previous_path = Path(args.previous)
    out = Path(args.out)

    latest, latest_raw = read_json(latest_path)
    previous, previous_raw = read_json(previous_path)

    current_core = build_4h_core(latest, latest_raw, str(latest_path), "CURRENT")
    previous_core = build_4h_core(previous, previous_raw, str(previous_path), "PREVIOUS_4H")
    early_core = build_early_core(latest, latest_raw, str(latest_path))

    write_json(out / "report_core.json", current_core)
    write_json(out / "previous_4h_report_core.json", previous_core)
    write_json(out / "early_ignition_core.json", early_core)

    status = {
        "artifact_schema_version": "CRYPTO_TRANSPORT_STATUS_V1",
        "methodology_impact": "NONE",
        "current_generated_at_utc": latest.get("generated_at_utc"),
        "current_pipeline_version": latest.get("pipeline_version"),
        "current_source_sha256": sha256_bytes(latest_raw),
        "previous_4h_generated_at_utc": previous.get("generated_at_utc"),
        "previous_4h_source_sha256": sha256_bytes(previous_raw),
        "outputs": [
            "crypto/report_core.json",
            "crypto/previous_4h_report_core.json",
            "crypto/early_ignition_core.json"
        ]
    }
    write_json(out / "transport_status.json", status)
    (out.parent / ".nojekyll").write_text("", encoding="utf-8")

if __name__ == "__main__":
    main()
