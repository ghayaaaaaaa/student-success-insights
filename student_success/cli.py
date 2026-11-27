"""Read cohort rows and print aggregate-only summaries."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

REQUIRED_FIELDS = {"course", "score", "attendance_rate"}
DEMO_ROWS = (
    {"course": "algebra", "score": "82", "attendance_rate": "0.94"},
    {"course": "algebra", "score": "74", "attendance_rate": "0.88"},
    {"course": "algebra", "score": "91", "attendance_rate": "0.97"},
    {"course": "algebra", "score": "68", "attendance_rate": "0.79"},
    {"course": "algebra", "score": "86", "attendance_rate": "0.91"},
    {"course": "biology", "score": "77", "attendance_rate": "0.85"},
    {"course": "biology", "score": "62", "attendance_rate": "0.72"},
    {"course": "biology", "score": "88", "attendance_rate": "0.95"},
)


def summarize_rows(
    rows: Iterable[Mapping[str, str]],
    score_threshold: float = 60.0,
    attendance_threshold: float = 0.75,
) -> list[dict[str, float | int | str]]:
    """Return course aggregates without retaining identifiers or raw records."""
    if not 0 <= score_threshold <= 100:
        raise ValueError("Score threshold must be within 0-100.")
    if not 0 <= attendance_threshold <= 1:
        raise ValueError("Attendance threshold must be within 0-1.")
    groups: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        try:
            score = float(row["score"])
            attendance = float(row["attendance_rate"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric value on CSV row {row_number}.") from exc
        if not 0 <= score <= 100:
            raise ValueError(f"Score outside 0-100 on CSV row {row_number}.")
        if not 0 <= attendance <= 1:
            raise ValueError(f"Attendance rate outside 0-1 on CSV row {row_number}.")
        course = (row.get("course") or "").strip()
        if not course:
            raise ValueError(f"Missing course on CSV row {row_number}.")
        groups[course].append((score, attendance))

    results: list[dict[str, float | int | str]] = []
    for course, values in sorted(groups.items()):
        count = len(values)
        score_mean = sum(score for score, _ in values) / count
        attendance_mean = sum(attendance for _, attendance in values) / count
        below = sum(
            score < score_threshold or attendance < attendance_threshold
            for score, attendance in values
        )
        results.append(
            {
                "course": course,
                "count": count,
                "mean_score": score_mean,
                "mean_attendance": attendance_mean,
                "below_demo_thresholds": below,
                "small_group": count < 5,
            }
        )
    return results


def summarize_csv(
    input_path: Path,
    score_threshold: float,
    attendance_threshold: float,
) -> list[dict[str, float | int | str]]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_FIELDS - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
        return summarize_rows(reader, score_threshold, attendance_threshold)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize course data by course.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Path to a CSV file")
    source.add_argument("--demo", action="store_true", help="Use the synthetic in-source cohort")
    parser.add_argument("--score-threshold", type=float, default=60.0)
    parser.add_argument("--attendance-threshold", type=float, default=0.75)
    args = parser.parse_args()
    try:
        rows = DEMO_ROWS if args.demo else summarize_csv(
            args.input, args.score_threshold, args.attendance_threshold
        )
        summaries = (
            summarize_rows(rows, args.score_threshold, args.attendance_threshold)
            if args.demo
            else rows
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if not summaries:
        print("No cohort rows found.")
        return
    print("Course-level summary (descriptive only)")
    for row in summaries:
        note = " | SMALL GROUP" if row["small_group"] else ""
        print(
            f"{row['course']}: n={row['count']}, mean_score={row['mean_score']:.1f}, "
            f"mean_attendance={row['mean_attendance']:.0%}, "
            f"below_demo_thresholds={row['below_demo_thresholds']}{note}"
        )


if __name__ == "__main__":
    main()
