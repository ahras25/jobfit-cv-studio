import unittest

from core.prompt_builder import build_system_prompt, build_user_prompt


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_contains_no_instruction_to_fabricate_experience(self):
        prompt = build_system_prompt()

        self.assertIn("Do not fabricate experience", prompt)

    def test_prompt_includes_target_language(self):
        prompt = build_user_prompt(
            "CV text",
            "Job text",
            {
                "target_role": "Product Analyst",
                "output_language": "Turkish",
                "tone": "confident",
                "detail_level": "short",
            },
        )

        self.assertIn("Target language: Turkish", prompt)

    def test_prompt_asks_for_json_only(self):
        self.assertIn("Return JSON only", build_system_prompt())
        self.assertIn(
            "Return JSON only",
            build_user_prompt("CV", "Job", {"output_language": "English"}),
        )


if __name__ == "__main__":
    unittest.main()

