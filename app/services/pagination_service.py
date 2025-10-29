"""
Pagination Service
Owner: Ryan
Description: Provides pagination utilities for API responses.
"""

"""
Pagination Service
Owner: Ryan
Description: Provides pagination utilities for API responses.
"""

from math import ceil
from flask import request

def paginate_query(query, page=None, per_page=None):
    """
    Return paginated SQLAlchemy query results.

    Args:
        query (BaseQuery): SQLAlchemy query object
        page (int): Current page number (default from query params)
        per_page (int): Results per page (default from query params)

    Returns:
        dict: {
            "items": list of objects,
            "meta": pagination metadata
        }
    """
    # Read pagination parameters from request if not provided
    page = page or int(request.args.get("page", 1))
    per_page = per_page or int(request.args.get("per_page", 10))

    pagination_obj = query.paginate(page=page, per_page=per_page, error_out=False)
    meta = get_pagination_meta(pagination_obj)

    return {
        "items": pagination_obj.items,
        "meta": meta
    }


def get_pagination_meta(pagination_obj):
    """
    Return metadata for pagination (page, total, per_page).

    Args:
        pagination_obj (Pagination): SQLAlchemy pagination object
    Returns:
        dict: pagination metadata
    """
    return {
        "page": pagination_obj.page,
        "per_page": pagination_obj.per_page,
        "total_items": pagination_obj.total,
        "total_pages": ceil(pagination_obj.total / pagination_obj.per_page) if pagination_obj.per_page else 1,
        "has_next": pagination_obj.has_next,
        "has_prev": pagination_obj.has_prev,
        "next_page": pagination_obj.next_num if pagination_obj.has_next else None,
        "prev_page": pagination_obj.prev_num if pagination_obj.has_prev else None,
    }


def paginate_response(query, page=1, per_page=10):
    """
    Convenience function that combines pagination and metadata.

    Args:
        query: SQLAlchemy query object
        page: Page number (default: 1)
        per_page: Items per page (default: 10)

    Returns:
        Tuple of (items, metadata)
    """
    pagination = paginate_query(query, page, per_page)
    metadata = get_pagination_meta(pagination)
    return pagination.items, metadata
