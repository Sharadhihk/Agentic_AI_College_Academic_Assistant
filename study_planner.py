"""Study planner: build, modify and recalculate schedules."""
import copy
from collections import defaultdict
from datetime import date, datetime, timedelta

UNIT = 0.5  # smallest block of study time (hours)

# profile = {
#   "subjects": [{"name": "Maths", "exam_date": "2026-11-20", "difficulty": 4}],
#   "daily_hours": 4,
#   "day_overrides": {"2026-10-10": 2}      # optional: different hours for one date
# }


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _allocate(total_hours: float, weights: dict) -> dict:
    """Split hours across subjects by weight, in UNIT blocks (largest remainder method)."""
    slots = int(round(total_hours / UNIT))
    total_w = sum(weights.values())
    raw = {k: slots * w / total_w for k, w in weights.items()}
    base = {k: int(v) for k, v in raw.items()}
    left = slots - sum(base.values())
    for k in sorted(raw, key=lambda k: raw[k] - base[k], reverse=True)[:left]:
        base[k] += 1
    return {k: v * UNIT for k, v in base.items() if v > 0}


def build_plan(profile: dict, today: date | None = None):
    """Return (plan, warnings). plan = list of {date, subject, hours, type}."""
    today = today or date.today()
    warnings, valid = [], []
    for s in profile.get("subjects", []):
        try:
            ed = parse_date(s["exam_date"])
        except (ValueError, KeyError):
            warnings.append(f"{s.get('name', '?')}: invalid exam date, skipped.")
            continue
        if ed <= today:
            warnings.append(f"{s['name']}: exam date {ed} is not in the future, skipped.")
            continue
        valid.append((s, ed))

    plan = []
    if not valid:
        return plan, warnings

    last_exam = max(ed for _, ed in valid)
    d = today
    while d < last_exam:
        hours = profile.get("day_overrides", {}).get(d.isoformat(), profile["daily_hours"])
        weights, kinds = {}, {}
        for s, ed in valid:
            days_left = (ed - d).days
            if days_left >= 1:
                w = s.get("difficulty", 3) / days_left      # harder + closer exam = more time
                kinds[s["name"]] = "study"
                if days_left == 1:                          # day before exam = revision
                    w *= 2
                    kinds[s["name"]] = "revision"
                weights[s["name"]] = w
        if weights and hours > 0:
            for name, h in _allocate(hours, weights).items():
                plan.append({"date": d.isoformat(), "subject": name,
                             "hours": h, "type": kinds[name]})
        d += timedelta(days=1)

    # feasibility hints
    for s, ed in valid:
        days_left = (ed - today).days
        if days_left < 3:
            warnings.append(f"{s['name']}: only {days_left} day(s) left, the plan is very tight.")
    return plan, warnings


def apply_changes(profile: dict, changes: list[dict]):
    """Apply edits to the profile. Returns (new_profile, notes)."""
    p = copy.deepcopy(profile)
    p.setdefault("day_overrides", {})
    notes = []

    def find(name):
        return next((s for s in p["subjects"] if s["name"].lower() == str(name).lower()), None)

    for c in changes:
        act = c.get("action")
        try:
            if act == "set_exam_date":
                s = find(c["subject"]); parse_date(c["date"])
                if not s:
                    notes.append(f"Subject '{c['subject']}' not found."); continue
                notes.append(f"{s['name']} exam: {s['exam_date']} -> {c['date']}")
                s["exam_date"] = c["date"]
            elif act == "set_daily_hours":
                notes.append(f"Daily hours: {p['daily_hours']} -> {c['hours']}")
                p["daily_hours"] = float(c["hours"])
            elif act == "set_day_hours":
                parse_date(c["date"])
                p["day_overrides"][c["date"]] = float(c["hours"])
                notes.append(f"{c['date']} limited to {c['hours']}h")
            elif act == "add_subject":
                parse_date(c["date"])
                if find(c["subject"]):
                    notes.append(f"'{c['subject']}' already exists."); continue
                p["subjects"].append({"name": c["subject"], "exam_date": c["date"],
                                      "difficulty": int(c.get("difficulty", 3))})
                notes.append(f"Added {c['subject']} (exam {c['date']})")
            elif act == "remove_subject":
                s = find(c["subject"])
                if not s:
                    notes.append(f"Subject '{c['subject']}' not found."); continue
                p["subjects"].remove(s)
                notes.append(f"Removed {s['name']}")
            elif act == "set_difficulty":
                s = find(c["subject"])
                if not s:
                    notes.append(f"Subject '{c['subject']}' not found."); continue
                s["difficulty"] = max(1, min(5, int(c["difficulty"])))
                notes.append(f"{s['name']} difficulty set to {s['difficulty']}")
            else:
                notes.append(f"Unknown change: {c}")
        except (KeyError, ValueError) as e:
            notes.append(f"Could not apply {c}: {e}")
    return p, notes


def format_plan(plan: list[dict], warnings: list[str] | None = None, max_days: int = 14) -> str:
    if not plan:
        return "No study plan could be generated.\n" + "\n".join(warnings or [])
    by_day = defaultdict(list)
    totals = defaultdict(float)
    for e in plan:
        tag = " (revision)" if e["type"] == "revision" else ""
        by_day[e["date"]].append(f"{e['subject']} {e['hours']}h{tag}")
        totals[e["subject"]] += e["hours"]

    lines = ["**Study plan**"]
    for i, day in enumerate(sorted(by_day)):
        if i >= max_days:
            lines.append(f"... and {len(by_day) - max_days} more days")
            break
        lines.append(f"- {parse_date(day):%a %d %b}: " + ", ".join(by_day[day]))
    lines.append("\n**Total hours per subject**")
    lines += [f"- {k}: {v:g}h" for k, v in totals.items()]
    if warnings:
        lines.append("\n**Warnings**")
        lines += [f"- {w}" for w in warnings]
    return "\n".join(lines)

