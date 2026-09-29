"""A conservative verification sheet for saved synthetic eligibility responses."""

MISSING = "Not returned by eligibility source"


def build_verification_sheet(summary: dict, source_label: str) -> dict:
    """Display only observed values; never infer missing dental benefits."""
    has_error = bool(summary["errors"])
    dental = [] if has_error else summary["dental"]
    rows = [
        ("Payer", summary["payer"], "payer.name.organization"),
        ("Test subscriber", summary["subscriber_name"], "subscriber.name.person"),
        ("Member ID", summary["member_id"], "subscriber.memberId"),
        ("Dental Care response", "; ".join(item["status"] for item in dental) if dental else MISSING,
         "dental nonCovered entry" if dental else ""),
        ("Network for Dental Care", "; ".join(item["network"] for item in dental) if dental else MISSING,
         "dental nonCovered entry" if dental else ""),
        ("Dental source message", "; ".join(msg for item in dental for msg in item["messages"]) or MISSING,
         "dental nonCovered entry" if dental else ""),
    ]
    for name in (
        "Overall eligibility status",
        "Effective date",
        "Termination date",
        "Group / plan",
        "Annual maximum",
        "Maximum used",
        "Maximum remaining",
        "Dental deductible",
        "Dental deductible met",
        "Preventive / basic / major coverage",
        "Crown coverage and replacement frequency",
        "Waiting periods / downgrades",
        "Predetermination requirement",
        "Source verification timestamp",
    ):
        rows.append((name, MISSING, ""))

    return {
        "source": source_label,
        "test_only": True,
        "errors": summary["errors"],
        "rows": rows,
    }


def sheet_markdown(sheet: dict) -> str:
    def safe(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "# AgentVerify Pro — Synthetic Eligibility Sheet",
        "",
        f"Source: {sheet['source']}",
        "TEST/SYNTHETIC DATA ONLY. This is not a live patient verification.",
        "",
    ]
    if sheet["errors"]:
        lines.extend(["Source errors:", *[f"- {safe(e)}" for e in sheet["errors"]], ""])
    lines.extend(["| Field | Returned value | Source field |", "|---|---|---|"])
    lines.extend(
        f"| {safe(name)} | {safe(value)} | {safe(source)} |"
        for name, value, source in sheet["rows"]
    )
    lines.extend([
        "",
        "Missing values were not inferred. Dental Care status applies only to this source response.",
        "Confirm actual eligibility and benefits through an authorized payer workflow.",
    ])
    return "\n".join(lines) + "\n"
