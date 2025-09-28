# app/utils/rate_limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from typing import Callable

def get_vendor_key(request: Request) -> str:
   
    if hasattr(request, '_json') and request._json:
        vendor_id = request._json.get('vendor_id')
        if vendor_id:
            return f"vendor:{vendor_id}"
    
    return get_remote_address(request)

limiter = Limiter(key_func=get_vendor_key)

def vendor_rate_limit(limit: str):
    return limiter.limit(limit)
