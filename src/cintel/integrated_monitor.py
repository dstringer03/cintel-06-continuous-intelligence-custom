"""Integrate signals, anomalies, rolling monitoring, and drift comparisons.

Author: Darrion Maurice Stringer
Date: 2026-11
"""

from pathlib import Path

import polars as pl

from cintel.utils_system import (
    compute_rolling_metrics,
    design_signals,
    load_system_metrics,
)


def main() -> None:
    """Generate monitoring evidence, assessment, and a chart."""
    root = Path.cwd()
    artifacts = root / "artifacts"
    images = root / "docs" / "images"
    artifacts.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)

    raw = load_system_metrics(root / "data" / "system_metrics.csv")
    required = ["requests", "errors", "total_latency_ms"]
    if not all(name in raw.columns for name in required):
        raise ValueError("Required columns are missing.")
    if any(raw[name].null_count() for name in required):
        raise ValueError("Missing measurements require review.")
    if raw.height < 40:
        raise ValueError("At least 40 observations are required.")
    if raw.filter(
        (pl.col("requests") <= 0)
        | (pl.col("errors") < 0)
        | (pl.col("errors") > pl.col("requests"))
        | (pl.col("total_latency_ms") < 0)
    ).height:
        raise ValueError("Invalid measurements require review.")

    # CSV order is assumed to represent observation order.
    signals = design_signals(raw)
    signals = compute_rolling_metrics(signals, window_size=5)
    signals = signals.with_row_index("observation", offset=1).with_columns(
        pl.col("error_rate").rolling_mean(5).alias("rolling_error_rate_5"),
        pl.col("avg_latency_ms").rolling_mean(5).alias("rolling_latency_ms_5"),
        ((pl.col("error_rate") > 0.05) | (pl.col("avg_latency_ms") > 40.0)).alias(
            "anomaly"
        ),
    )

    baseline = signals.head(20)
    recent = signals.tail(20)
    baseline_error = baseline["error_rate"].mean()
    baseline_latency = baseline["avg_latency_ms"].mean()
    recent_error = recent["error_rate"].mean()
    recent_latency = recent["avg_latency_ms"].mean()

    # Illustrative drift limits: 1 percentage point and 5 milliseconds.
    error_change = recent_error - baseline_error
    latency_change = recent_latency - baseline_latency
    error_drift = abs(error_change) > 0.01
    latency_drift = abs(latency_change) > 5.0
    worsening_drift = error_change > 0.01 or latency_change > 5.0
    latest = signals.row(-1, named=True)

    degraded = (
        recent_error > 0.05
        or recent_latency > 40.0
        or latest["rolling_error_rate_5"] > 0.05
        or latest["rolling_latency_ms_5"] > 40.0
        or worsening_drift
    )

    assessment = pl.DataFrame(
        {
            "baseline_error_rate_pct": [100 * baseline_error],
            "recent_error_rate_pct": [100 * recent_error],
            "error_change_percentage_points": [100 * error_change],
            "baseline_latency_ms": [baseline_latency],
            "recent_latency_ms": [recent_latency],
            "latency_change_ms": [latency_change],
            "error_drift": [error_drift],
            "latency_drift": [latency_drift],
            "worsening_drift": [worsening_drift],
            "total_anomalies": [signals.filter(pl.col("anomaly")).height],
            "recent_anomalies": [recent.filter(pl.col("anomaly")).height],
            "system_state": ["DEGRADED" if degraded else "STABLE"],
        }
    )

    signals.write_csv(artifacts / "integrated_signals.csv")
    signals.filter(pl.col("anomaly")).write_csv(artifacts / "integrated_anomalies.csv")
    assessment.write_csv(artifacts / "integrated_assessment.csv")

    # Show every observation so summary averages cannot hide the middle.
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420">',
        '<rect width="900" height="420" fill="white"/>',
        '<g font-family="Arial" fill="#172033">',
        '<text x="30" y="35" font-size="23">Integrated Reliability Monitoring</text>',
        '<text x="30" y="65" font-size="14">Error rate (%): gray observations; blue trailing window of 5</text>',
    ]
    maximum = max(6.0, signals["error_rate"].max() * 110)
    for tick in range(int(maximum) + 1):
        y = 320 - tick / maximum * 220
        svg.append(f'<path d="M70 {y:.2f} H830" stroke="#e5e7eb"/>')
        svg.append(f'<text x="30" y="{y + 4:.2f}" font-size="13">{tick}%</text>')

    for column, color in (
        ("error_rate", "#9ca3af"),
        ("rolling_error_rate_5", "#2563eb"),
    ):
        points = []
        for index, value in enumerate(signals[column].to_list()):
            if value is not None:
                x = 70 + index / (signals.height - 1) * 760
                y = 320 - value * 100 / maximum * 220
                points.append(f"{x:.2f},{y:.2f}")
        coordinates = " ".join(points)
        svg.append(
            f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="2"/>'
        )

    y = 320 - 5 / maximum * 220
    svg.append(f'<path d="M70 {y:.2f} H830" stroke="#dc2626" stroke-dasharray="6 4"/>')
    for number in (1, 20, 40, 60):
        x = 70 + (number - 1) / (signals.height - 1) * 760
        svg.append(f'<text x="{x:.2f}" y="345" font-size="13">{number}</text>')
    svg.extend(
        [
            '<text x="330" y="375" font-size="14">Observation order (no timestamps)</text>',
            '<text x="70" y="405" font-size="13">Dashed red: illustrative 5% error threshold. Baseline: 1–20; recent: 41–60.</text>',
            "</g></svg>",
        ]
    )
    (images / "integrated-monitoring.svg").write_text(
        "\n".join(svg) + "\n", encoding="utf-8"
    )

    print(assessment)
    print("Saved integrated signals, anomalies, assessment, and chart.")


if __name__ == "__main__":
    main()
