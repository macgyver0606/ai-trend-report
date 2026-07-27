import unittest

from fastapi import HTTPException, status

from app.utils.errors import raise_upstream_service_error


class ApiErrorTests(unittest.TestCase):
    def test_upstream_error_is_returned_as_bad_gateway(self):
        with self.assertRaises(HTTPException) as context:
            raise_upstream_service_error(RuntimeError("외부 서비스 오류"))

        self.assertEqual(context.exception.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(context.exception.detail, "외부 서비스 오류")
