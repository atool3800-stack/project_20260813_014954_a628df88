#!/usr/bin/env python3
"""
Risk Analysis for Daily Learner Data
====================================
Reads learner learning-behaviour data from `data/daily_learners.csv` and
computes a composite risk score for every learner.

A learner is flagged as HIGH RISK when their composite risk score is equal
to or above RISK_THRESHOLD. The script prints a statistical summary of the
day's cohort and the list of high-risk learners (sorted by risk score,
highest first) to standard output.

Fields expected in the CSV:
    learner_id, region, course_id, last_login_days,
    assignment_completion_rate, quiz_score_trend, attendance_rate

Usage:
    python scripts/risk_analysis.py [path_to_csv]
"""

import csv
import os
import sys

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DEFAULT_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "daily_learners.csv"
)

# A learner with risk_score >= RISK_THRESHOLD is considered high risk.
RISK_THRESHOLD = 0.50

# Weights used to combine the normalised risk factors into a single score.
W_LAST_LOGIN = 0.30      # how long since the learner last logged in
W_COMPLETION = 0.25      # inverse of assignment completion rate
W_QUIZ_TREND = 0.20      # how negative the quiz-score trend is
W_ATTENDANCE = 0.25      # inverse of attendance rate

# Reference ranges used to normalise each raw feature to [0, 1].
MAX_LAST_LOGIN_DAYS = 60.0
MAX_TREND_MAGNITUDE = 50.0   # quiz_score_trend is expressed in percentage points


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def clamp(value, low=0.0, high=1.0):
    """Clamp *value* into the [low, high] interval."""
    return max(low, min(high, value))


def compute_risk_score(row):
    """
    Compute a composite risk score in [0, 1] for a single learner row.

    All risk factors are oriented so that a HIGHER value means MORE risk:
      * more days since last login            -> more risk
      * lower assignment completion           -> more risk
      * more negative quiz-score trend        -> more risk
      * lower attendance                      -> more risk
    """
    last_login_days = max(0.0, float(row["last_login_days"]))
    completion_rate = clamp(float(row["assignment_completion_rate"]))
    quiz_trend = float(row["quiz_score_trend"])
    attendance_rate = clamp(float(row["attendance_rate"]))

    last_login_risk = clamp(last_login_days / MAX_LAST_LOGIN_DAYS)
    completion_risk = 1.0 - completion_rate
    # A negative trend (declining quiz scores) increases risk.
    quiz_trend_risk = clamp(-quiz_trend / MAX_TREND_MAGNITUDE)
    attendance_risk = 1.0 - attendance_rate

    score = (
        W_LAST_LOGIN * last_login_risk
        + W_COMPLETION * completion_risk
        + W_QUIZ_TREND * quiz_trend_risk
        + W_ATTENDANCE * attendance_risk
    )
    return clamp(score)


def load_learners(csv_path):
    """Load the learner records from *csv_path* into a list of dicts."""
    learners = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            learners.append(row)
    return learners


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    if not os.path.exists(csv_path):
        print(f"[ERROR] Data file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    learners = load_learners(csv_path)
    if not learners:
        print("[ERROR] No learner records found in the CSV file.", file=sys.stderr)
        sys.exit(1)

    # Annotate each learner with their risk score.
    for learner in learners:
        learner["risk_score"] = compute_risk_score(learner)

    high_risk = [l for l in learners if l["risk_score"] >= RISK_THRESHOLD]
    high_risk.sort(key=lambda l: l["risk_score"], reverse=True)

    # ----- Statistical summary -------------------------------------------- #
    total = len(learners)
    high_count = len(high_risk)
    avg_risk = sum(l["risk_score"] for l in learners) / total

    region_distribution = {}
    for l in high_risk:
        region_distribution[l["region"]] = region_distribution.get(l["region"], 0) + 1

    print("=" * 64)
    print("DAILY LEARNER RISK ANALYSIS")
    print("=" * 64)
    print(f"Data file           : {csv_path}")
    print(f"Total learners      : {total}")
    print(f"Risk threshold      : {RISK_THRESHOLD}")
    print(f"Average risk score  : {avg_risk:.4f}")
    print(f"High-risk learners  : {high_count}")
    print("-" * 64)
    print("High-risk distribution by region:")
    for region in sorted(region_distribution.keys()):
        print(f"  {region:>14s}: {region_distribution[region]}")
    print("=" * 64)

    # ----- High-risk learner list ------------------------------------------ #
    print("\nTOP HIGH-RISK LEARNERS (learner_id, region, course_id, risk_score)")
    print("-" * 64)
    for idx, l in enumerate(high_risk, start=1):
        print(f"{idx:>4d}. {l['learner_id']:<10s} {l['region']:<14s} "
              f"{l['course_id']:<10s} {l['risk_score']:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
