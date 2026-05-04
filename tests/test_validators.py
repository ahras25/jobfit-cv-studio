import unittest

from core.validators import clean_text, detect_too_short_input, validate_inputs


class ValidatorTests(unittest.TestCase):
    def test_empty_input_rejected_when_sample_mode_is_false(self):
        errors = validate_inputs("", "", use_sample_data=False)

        self.assertIn("CV or resume text is required.", errors)
        self.assertIn("Job description text is required.", errors)

    def test_sample_mode_allows_empty_input(self):
        errors = validate_inputs("", "", use_sample_data=True)

        self.assertEqual(errors, [])

    def test_clean_text_trims_extra_spaces(self):
        cleaned = clean_text("  Hello     world  \n\n   Next    line  ")

        self.assertEqual(cleaned, "Hello world\n\nNext line")

    def test_detect_too_short_input_works(self):
        self.assertTrue(detect_too_short_input("short text"))
        long_text = " ".join(["experience"] * 40)
        self.assertFalse(detect_too_short_input(long_text))


if __name__ == "__main__":
    unittest.main()

