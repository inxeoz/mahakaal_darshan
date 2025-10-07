# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from functools import wraps
from typing import Optional, Any, Callable, Dict

def _ensure_role(role_name: str) -> Callable:
    """
    Decorator to ensure the current session user has the specified role.
    If not, returns a consistent error dict.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = frappe.session.user
            roles = frappe.get_roles(user)
            if role_name not in roles:
                return {"error": "permission_denied", "message": "You do not have role to access this"}
            return fn(*args, **kwargs)
        return wrapper
    return decorator
