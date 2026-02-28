import math

import pytest
from pydantic import ValidationError

from app.shared.schemas import ErrorResponse, PaginatedResponse, PaginationParams


def test_pagination_params_defaults() -> None:
    params = PaginationParams()
    assert params.page == 1
    assert params.page_size == 20


def test_pagination_params_offset_calculation() -> None:
    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20


def test_pagination_params_rejects_page_zero() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(page=0)


def test_pagination_params_rejects_page_size_over_100() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(page_size=101)


def test_paginated_response_structure() -> None:
    response: PaginatedResponse[str] = PaginatedResponse(
        items=["a", "b", "c"],
        total=25,
        page=2,
        page_size=10,
    )
    assert response.items == ["a", "b", "c"]
    assert response.total == 25
    assert response.page == 2
    assert response.page_size == 10


def test_paginated_response_total_pages_rounds_up() -> None:
    response: PaginatedResponse[int] = PaginatedResponse(
        items=[1, 2, 3],
        total=25,
        page=1,
        page_size=10,
    )
    assert response.total_pages == math.ceil(25 / 10)  # 3


def test_error_response_structure() -> None:
    err = ErrorResponse(error="Not found", type="not_found")
    assert err.error == "Not found"
    assert err.type == "not_found"
    assert err.detail is None


def test_error_response_with_detail() -> None:
    err = ErrorResponse(
        error="Invalid input",
        type="validation_error",
        detail="Field 'name' is required",
    )
    assert err.detail == "Field 'name' is required"
