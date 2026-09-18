from gmail.email_service import *


service = get_gmail_service()

message_ids = get_latest_message_ids(
    service,
    max_results=5
)

emails =[
    get_email_by_id(service, message_id)
    for message_id in message_ids
]

for email in emails:
    print("=" * 80)
    print("ID:", email.id)
    print("FROM:", email.sender)
    print("SUBJECT:", email.subject)
    print("DATE:", email.date)

    print("\nBODY:")
    print(email.body[:1500])

    if email.attachments:
        print("\nATTACHMENTS:")

        for attachment in email.attachments:
            print(
                f"- {attachment.filename} "
                f"({attachment.mime_type})"
            )

    print()