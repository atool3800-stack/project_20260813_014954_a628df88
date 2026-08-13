# Daily Learner Risk Alert

This repository powers the **daily learner risk alert** workflow for our online
professional training company, which operates from our headquarters in Cape Town
(South Africa) and a branch office in Cairo (Egypt).

We generate a large volume of learner engagement data every day. The repository
consolidates that data and runs a repeatable risk analysis so that our learner
success team can proactively reach out to at-risk learners.

## Repository contents

- `data/daily_learners.csv` — Daily learner learning-behaviour records
  (`learner_id`, `region`, `course_id`, `last_login_days`,
  `assignment_completion_rate`, `quiz_score_trend`, `attendance_rate`).
- `scripts/risk_analysis.py` — Computes a composite risk score for every learner
  and flags high-risk learners along with a statistical summary.

## Usage

Run the daily risk analysis:

```bash
python scripts/risk_analysis.py
```

The script prints a statistical summary of the day's cohort together with the
list of high-risk learners, sorted by risk score (highest first).

## Daily workflow

1. Run `scripts/risk_analysis.py` against the latest `data/daily_learners.csv`.
2. Update the **每日风险预警** (Daily Risk Alert) section of this `README.md`
   with the date, the total number of high-risk learners, the regional
   distribution (South Africa / Egypt) and the Top 10 high-risk learners.
3. Commit and push the updated `README.md`.
4. If more than 20 learners are flagged as high risk, open a GitHub issue with
   the `risk-alert` label summarising the alert.
