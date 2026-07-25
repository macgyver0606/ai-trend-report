import unittest
from datetime import date

from pydantic import ValidationError

from app.models.analysis_request import AnalysisRequest


class AnalysisRequestValidationTests(unittest.TestCase):
    def test_valid_request_is_normalized(self):
        request = AnalysisRequest(
            keyword="  AI 반도체  ",
            industry="  반도체 ",
            start_date=date(2026, 6, 25),
            end_date=date(2026, 7, 25),
        )

        self.assertEqual(request.keyword, "AI 반도체")
        self.assertEqual(request.industry, "반도체")

    def test_period_shorter_than_seven_days_is_rejected(self):
        with self.assertRaises(ValidationError):
            AnalysisRequest(
                keyword="AI",
                industry="IT",
                start_date=date(2026, 7, 20),
                end_date=date(2026, 7, 25),
            )

    def test_start_date_after_end_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            AnalysisRequest(
                keyword="AI",
                industry="IT",
                start_date=date(2026, 7, 25),
                end_date=date(2026, 7, 20),
            )
