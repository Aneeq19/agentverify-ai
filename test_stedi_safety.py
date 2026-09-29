"""Safety checks for the synthetic Stedi adapter and report."""
import unittest

from stedi_parser import parse_stedi_response
from verification_sheet import MISSING, build_verification_sheet, sheet_markdown


def rows(sheet):
    return {field: value for field, value, _ in sheet["rows"]}


class StediSafetyTests(unittest.TestCase):
    def test_missing_benefits_are_not_inferred(self):
        sheet = build_verification_sheet(parse_stedi_response({"payer": {}}), "test")
        self.assertEqual(rows(sheet)["Annual maximum"], MISSING)
        self.assertEqual(rows(sheet)["Dental deductible"], MISSING)
        self.assertEqual(rows(sheet)["Dental Care response"], MISSING)

    def test_medical_deductibles_do_not_become_dental(self):
        response = {
            "benefits": {
                "deductible": [
                    {"service": {"definition": "Hospital - Outpatient"}, "amount": 250}
                ]
            }
        }
        sheet = build_verification_sheet(parse_stedi_response(response), "test")
        self.assertEqual(rows(sheet)["Dental deductible"], MISSING)
        self.assertEqual(rows(sheet)["Dental Care response"], MISSING)
        self.assertNotIn("Hospital", sheet_markdown(sheet))

    def test_source_error_suppresses_dental_result(self):
        response = {
            "errors": [{"description": "Subscriber not found"}],
            "benefits": {
                "nonCovered": [
                    {"service": {"value": "35", "definition": "Dental Care"}}
                ]
            },
        }
        sheet = build_verification_sheet(parse_stedi_response(response), "test")
        self.assertEqual(rows(sheet)["Dental Care response"], MISSING)
        self.assertIn("Subscriber not found", sheet_markdown(sheet))

    def test_dental_response_does_not_imply_overall_eligibility(self):
        response = {
            "benefits": {
                "nonCovered": [{
                    "service": {"value": "35", "definition": "Dental Care"},
                    "network": {"indicator": "IN_NETWORK"},
                    "messages": ["VIEW CONTRACT FOR COVERAGE DETAILS"],
                }]
            }
        }
        sheet = build_verification_sheet(parse_stedi_response(response), "test")
        self.assertEqual(rows(sheet)["Dental Care response"], "NON_COVERED")
        self.assertEqual(rows(sheet)["Overall eligibility status"], MISSING)
        self.assertEqual(rows(sheet)["Crown coverage and replacement frequency"], MISSING)

    def test_malformed_response_fails_closed(self):
        with self.assertRaises(TypeError):
            parse_stedi_response([])
        with self.assertRaises(TypeError):
            parse_stedi_response({"payer": ["unexpected"]})


if __name__ == "__main__":
    unittest.main()
