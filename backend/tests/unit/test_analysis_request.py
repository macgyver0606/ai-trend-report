import unittest

from pydantic import ValidationError

from app.models.analysis_request import AnalysisRequest


class AnalysisRequestValidationTests(unittest.TestCase):
    def test_valid_request_is_normalized(self):
        request = AnalysisRequest(
            keyword="  AI 반도체  ",
            industry="  반도체 ",
        )

        self.assertEqual(request.keyword, "AI 반도체")
        self.assertEqual(request.industry, "반도체")

    def test_blank_keyword_is_rejected(self):
        with self.assertRaises(ValidationError):
            AnalysisRequest(
                keyword="   ",
                industry="IT",
            )
