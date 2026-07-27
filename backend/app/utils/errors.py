"""API에서 공통으로 사용하는 안전한 오류 응답입니다."""

from typing import NoReturn

from fastapi import HTTPException, status


def raise_upstream_service_error(error: RuntimeError) -> NoReturn:
    """외부 데이터·AI 서비스 오류를 동일한 API 응답으로 변환한다."""

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error),
    ) from error
