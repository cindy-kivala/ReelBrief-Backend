"""
Pagination Service
Owner: Ryan
Description: Provides pagination utilities for API responses.
"""

def paginate_query(query, page=1, per_page=10):
    """
    Return paginated results from a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (default: 1)
        per_page: Items per page (default: 10)
    
    Returns:
        Pagination object with items and metadata
    """
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:  # Max limit to prevent abuse
        per_page = 100
    
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_pagination_meta(pagination_obj):
    """
    Return metadata for pagination (page, total, per_page).
    
    Args:
        pagination_obj: Flask-SQLAlchemy pagination object
    
    Returns:
        Dictionary with pagination metadata
    """
    return {
        'page': pagination_obj.page,
        'per_page': pagination_obj.per_page,
        'total_items': pagination_obj.total,
        'total_pages': pagination_obj.pages,
        'has_next': pagination_obj.has_next,
        'has_prev': pagination_obj.has_prev,
        'next_page': pagination_obj.next_num if pagination_obj.has_next else None,
        'prev_page': pagination_obj.prev_num if pagination_obj.has_prev else None
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