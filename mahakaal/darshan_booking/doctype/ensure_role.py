# Copyright (c) 2025, inx and contributors
# For license information, please see license.txt

import frappe
from functools import wraps
from typing import Optional, Any, Callable, Dict



def _ensure_role(*role_names: str) -> Callable:
    """
    Decorator to ensure the current session user has at least one of the specified roles.
    Usage:
        @_ensure_role("Approver Role")
        @_ensure_role("Approver Role", "Admin Role")
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = frappe.session.user
            user_roles = frappe.get_roles(user)

            if not any(role in user_roles for role in role_names):
                return {
                    "error": "permission_denied",
                    "message": f"You must have one of these roles: {', '.join(role_names)}"
                }

            return fn(*args, **kwargs)
        return wrapper
    return decorator

