from email_service import (
    get_gmail_service,
    get_latest_message_ids
)


service = get_gmail_service()

message_ids = get_latest_message_ids(
    service,
    max_results=5
)

print(message_ids)