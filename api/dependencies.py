from functools import lru_cache
from gmail.email_service import get_gmail_service

def provide_gmail_service():
    return get_gmail_service()
