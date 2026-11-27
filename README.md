# Student Cohort Insights

A small Python CLI that summarizes a synthetic course cohort without printing student-level records. It reports aggregate score and attendance measures and counts rows below configurable demonstration thresholds.

## Run

Use Python 3.11 or newer from this directory:

```bash
python -m student_success --demo
python -m student_success --input path/to/cohort.csv --score-threshold 60 --attendance-threshold 0.75
```

The CSV requires `course`, `score`, and `attendance_rate` columns.

## Features

- Validates numeric ranges and required fields.
- Produces course-level summaries only.
- Marks small groups in the output so averages are not mistaken for stable estimates.
- Uses only Python's standard library; the demo cohort is generated from constants in the source.

## Data and limitations

The demonstration records are synthetic. The tool is descriptive; it does not predict student outcomes, identify individual students, or recommend educational decisions. Do not use it for student eligibility, grading, placement, intervention, or other high-impact decisions. Use anonymized or synthetic data only.

This is an AI-assisted portfolio demonstration inspired by a student-performance project theme in a folder supplied by Ghaya. No original records, notebook outputs, model weights, or source datasets are included. No model was trained and no measured result is claimed. No open-source license is included.
