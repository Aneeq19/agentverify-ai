"""Authored fictional fixtures, never presented as a payer response."""
from copy import deepcopy

BASE_CASE = dict(patient_name="John Demo", dob="01/01/1995",
                 member_id="DEMO123", group_number="GRP001", procedure="Crown",
                 notes="Fictional crown preparation case.")


def record(field, value, scope="dental"):
    return dict(field=field, value=value, scope=scope)


BENEFITS = {"schema": "agentverify-demo-v1", "errors": [], "benefits": [
    record("Overall eligibility", "Active", "overall"),
    record("Dental coverage", "Reported for dental services; procedure review required"),
    record("Network", "IN_NETWORK"),
    record("Annual maximum", "$1,500 (fictional calendar-year benefit)"),
    record("Major coverage", "50% (fictional example)"),
]}
CASES = {
    "Incomplete crown case": {
        "case": {**BASE_CASE, "member_id": ""},
        "raw": None, "format": "demo", "source": "No benefit source supplied"},
    "Synthetic dental benefits": {
        "case": BASE_CASE, "raw": BENEFITS, "format": "demo",
        "source": "Authored fictional dental benefits fixture"},
    "Medical-only response": {
        "case": BASE_CASE, "format": "demo",
        "source": "Authored fictional medical-only fixture",
        "raw": {"schema": "agentverify-demo-v1", "errors": [], "benefits": [
            record("Overall eligibility", "Active", "overall"),
            record("Dental deductible", "$250", "medical")]}},
    "Source error": {
        "case": BASE_CASE, "format": "demo",
        "source": "Authored fictional source-error fixture",
        "raw": {**BENEFITS, "errors": ["Synthetic source failure: subscriber not found"]}},
    "Conflicting annual maximum": {
        "case": BASE_CASE, "format": "demo",
        "source": "Authored fictional conflict fixture",
        "raw": {**BENEFITS, "benefits": BENEFITS["benefits"] + [
            record("Annual maximum", "$2,000 (fictional calendar-year benefit)")]}},
}


def load_demo(name):
    return deepcopy(CASES[name])
