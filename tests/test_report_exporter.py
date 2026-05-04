import unittest

from core.report_exporter import export_markdown, export_text, filename_safe


class ReportExporterTests(unittest.TestCase):
    def sample_result(self):
        return {
            "match_score": 82,
            "summary": "Good fit with some gaps.",
            "strong_matches": ["python", "reporting"],
            "missing_keywords": ["sql"],
            "weak_areas": ["SQL is not visible."],
            "cv_bullet_rewrites": [
                {
                    "before": "Built reports.",
                    "after": "Built reporting workflows aligned to team needs.",
                    "reason": "More specific.",
                }
            ],
            "cover_letter": "Dear team, I am excited to apply.",
            "linkedin_message": "Hello, I am interested in the role.",
            "interview_questions": ["Tell me about reporting."],
            "application_checklist": ["Proofread the CV."],
            "warnings": [],
        }

    def test_markdown_export_includes_match_score(self):
        report = export_markdown(self.sample_result(), {"target_role": "Analyst"})

        self.assertIn("82/100", report)

    def test_text_export_includes_cover_letter(self):
        report = export_text(self.sample_result(), {"target_role": "Analyst"})

        self.assertIn("Dear team", report)

    def test_filename_safe_removes_unsafe_characters(self):
        safe = filename_safe("Product Analyst / Growth: EU?")

        self.assertEqual(safe, "Product-Analyst-Growth-EU")


if __name__ == "__main__":
    unittest.main()

