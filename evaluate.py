import json
from pathlib import Path

from agent import (
    check_required_fields,
    build_payer_questions,
    search_knowledge_base,
)

EVAL_FILE = Path(__file__).parent / "eval_cases.json"


def load_cases():
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def check_required_fields_test(case):
    expected = case.get("expected_missing")

    if expected is None:
        return True, "Not required for this case"

    result = check_required_fields(case["data"]).lower()

    if not expected:
        passed = "all required fields are present" in result
        return passed, result

    passed = all(field.lower() in result for field in expected)
    return passed, result


def check_payer_questions_test(case):
    expected_keywords = case.get("expected_question_keywords")

    if not expected_keywords:
        return True, "Not required for this case"

    result = build_payer_questions(case["data"])

    passed = all(
        keyword.lower() in result.lower()
        for keyword in expected_keywords
    )

    return passed, result


def check_rag_test(case):
    keyword = case.get("rag_keyword")

    if not keyword:
        return True, "Not required for this case"

    data = case["data"]

    query = " ".join(
        [
            case.get("request", ""),
            data.get("procedure", ""),
            data.get("notes", ""),
        ]
    )

    result = search_knowledge_base(query)

    passed = keyword.lower() in result.lower()

    return passed, "knowledge_base.md used"


def check_safety_test(case):
    data = case["data"]

    query = " ".join(
        [
            case.get("request", ""),
            data.get("procedure", ""),
            data.get("notes", ""),
        ]
    )

    result = search_knowledge_base(query).lower()

    safety_phrases = [
        "confirm directly with payer",
        "confirmed directly with the payer",
        "confirm directly with the payer",
    ]

    passed = any(
        phrase in result
        for phrase in safety_phrases
    )

    return passed, "confirm directly with payer"


def evaluate_case(case):
    checks = {}

    required_pass, required_detail = check_required_fields_test(case)
    checks["required_fields"] = required_pass

    questions_pass, questions_detail = check_payer_questions_test(case)
    checks["payer_questions"] = questions_pass

    rag_pass, rag_detail = check_rag_test(case)
    checks["rag"] = rag_pass

    safety_pass, safety_detail = check_safety_test(case)
    checks["safety"] = safety_pass

    passed = all(checks.values())

    return {
        "passed": passed,
        "checks": checks,
        "details": {
            "required_fields": required_detail,
            "payer_questions": questions_detail,
            "rag": rag_detail,
            "safety": safety_detail,
        },
    }


def main():
    cases = load_cases()

    passed_count = 0

    print("\nAgentVerify AI v1.3 Evaluation")
    print("=" * 50)

    for case in cases:
        result = evaluate_case(case)

        status = "PASS" if result["passed"] else "FAIL"

        if result["passed"]:
            passed_count += 1

        print(
            f"\nTest {case['id']}: "
            f"{case['name']} — {status}"
        )

        for check_name, check_passed in result["checks"].items():
            symbol = "PASS" if check_passed else "FAIL"
            print(f"  {check_name}: {symbol}")

        if not result["passed"]:
            print("  Failure details:")

            for check_name, check_passed in result["checks"].items():
                if not check_passed:
                    detail = result["details"][check_name]
                    print(f"    {check_name}: {detail}")

    total = len(cases)
    percentage = round((passed_count / total) * 100)

    print("\n" + "=" * 50)
    print(
        f"FINAL RESULT: "
        f"{passed_count}/{total} PASS — {percentage}%"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()
    