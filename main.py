from gmail.email_service import *
from ai.email_analyzer import analyze_email , analyze_emails
from services.inbox_service import *

def main():
    service = get_gmail_service()

    ids = get_latest_message_ids(
        service,
        max_results=5,
    )

    emails = [
        get_email_by_id(
            service,
            message_id,
        )
        for message_id in ids
    ]

    analyzed_emails = analyze_emails(
        emails
    )

    analyzed_emails = sort_by_priority(
        analyzed_emails
    )

    summary = build_inbox_summary(
        analyzed_emails
    )

    print("\nINBOX SUMMARY")
    print("=" * 80)

    print(
        summary.model_dump_json(
            indent=2
        )
    )

    print("\nEMAILS")
    print("=" * 80)

    for item in analyzed_emails:

        email = item.email
        analysis = item.analysis

        print(
            f"[{analysis.priority.upper()}] "
            f"{email.subject}"
        )

        print(
            f"From: {email.sender}"
        )

        print(
            f"Category: "
            f"{analysis.category}"
        )

        print(
            f"Summary: "
            f"{analysis.summary}"
        )

        if analysis.action_required:
            print("Actions:")

            for action in analysis.action_items:
                print(
                    f"  - {action}"
                )

        print()


if __name__ == "__main__":
    main()