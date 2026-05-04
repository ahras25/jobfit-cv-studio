import unittest

from core.analyzer import (
    analyze_locally,
    calculate_basic_match_score,
    create_demo_result,
    extract_keywords,
)
from core.schemas import RESULT_FIELDS


class AnalyzerTests(unittest.TestCase):
    def test_keyword_extraction_works(self):
        keywords = extract_keywords("Python SQL Python onboarding CRM reporting")

        self.assertIn("python", keywords)
        self.assertIn("sql", keywords)

    def test_basic_match_score_is_between_zero_and_one_hundred(self):
        score = calculate_basic_match_score(
            "Python SQL customer onboarding reporting",
            "Python SQL CRM onboarding automation reporting",
        )

        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_missing_keywords_are_found(self):
        result = analyze_locally(
            "Python reporting",
            "Python SQL CRM onboarding reporting",
            {"target_role": "Operations Analyst"},
        )

        self.assertIn("sql", result["missing_keywords"])
        self.assertIn("crm", result["missing_keywords"])

    def test_demo_result_has_all_required_schema_fields(self):
        result = create_demo_result(
            "Customer onboarding CRM reporting and support operations experience. "
            "Created documentation and improved weekly metrics tracking.",
            "Need customer onboarding CRM reporting SQL documentation and renewal analysis.",
            {
                "target_role": "Customer Success Operations Specialist",
                "output_language": "English",
                "tone": "professional",
                "detail_level": "balanced",
            },
        )

        self.assertEqual(set(RESULT_FIELDS), set(result.keys()))


if __name__ == "__main__":
    unittest.main()

