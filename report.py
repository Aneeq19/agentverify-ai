"""Render one review model to both the UI and exports."""
from schemas import Review


def field_value(field):
    return field.value if field.value is not None else (
        "Source error — no conclusion" if field.status == "source_error"
        else "Not returned by eligibility source")


def review_rows(review: Review):
    return [{"Field": f.name, "Value": field_value(f), "Status": f.status,
             "Scope": f.scope, "Evidence": " | ".join(f.evidence)} for f in review.fields]


def render_report(review: Review) -> str:
    lines = [
        "AgentVerify AI — Fictional Dental Verification Review",
        "By Aneeq Jawed | Synthetic demo; not live patient verification.",
        f"Procedure: {review.case.procedure or 'Not supplied'}",
        f"Source: {review.source}", f"Source status: {review.source_status}",
        f"Review status: {review.review_status}",
        f"Missing prerequisites: {', '.join(review.missing_fields) or 'None'}",
        f"Provider: {review.provider}", f"AI status: {review.ai_status}", "",
    ]
    lines += ["Source error: " + error for error in review.source_errors]
    lines += [f"{f.name}: {field_value(f)} [{f.status}]"
              + (" | Evidence: " + "; ".join(f.evidence) if f.evidence else "")
              for f in review.fields]
    lines += ["", "FOLLOW-UP QUESTIONS"] + [f"- {q}" for q in review.questions]
    lines += ["", "WORKFLOW GUIDANCE (not case benefit evidence)"]
    for g in review.guidance:
        lines += [f"Source: {g.source_id} | version: {g.version}", g.text, ""]
    lines += ["Confirm actual eligibility and benefits through an authorized payer workflow."]
    return "\n".join(lines) + "\n"
