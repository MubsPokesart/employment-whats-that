from typing import List
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    DeviceNotRegisteredError
)

from src.models import JobPosting, UserProfile

class NotificationService:
    """Handles push notification dispatch via Expo."""

    def __init__(self):
        self.client = PushClient()

    def dispatch(self, new_jobs: List[JobPosting], users: List[UserProfile]) -> None:
        """
        Send notifications to users based on their filters.

        Args:
            new_jobs: List of newly discovered jobs
            users: List of user profiles with filters
        """
        messages = []

        for user in users:
            # Find jobs matching this user's filters
            relevant_jobs = [
                job for job in new_jobs
                if user.filters.matches(job)
            ]

            if not relevant_jobs:
                continue

            try:
                if len(relevant_jobs) == 1:
                    # Single job notification (detailed)
                    job = relevant_jobs[0]
                    msg = PushMessage(
                        to=user.push_token,
                        title=f"New Job at {job.company}",
                        body=f"{job.role} in {job.location}",
                        data={"url": job.link, "job_id": job.id},
                        sound="default",
                        priority="high",
                    )
                else:
                    # Multiple jobs notification (summary)
                    companies = ", ".join(set(j.company for j in relevant_jobs[:3]))
                    remaining = len(relevant_jobs) - 3
                    suffix = f" +{remaining} more" if remaining > 0 else ""

                    msg = PushMessage(
                        to=user.push_token,
                        title=f"{len(relevant_jobs)} New Jobs Found",
                        body=f"{companies}{suffix}",
                        data={"count": len(relevant_jobs)},
                        sound="default",
                        priority="high",
                    )

                messages.append(msg)

            except Exception as e:
                print(f"Error building notification for {user.push_token}: {e}")

        # Send batch
        if not messages:
            print("No notifications to send")
            return

        try:
            responses = self.client.publish_multiple(messages)

            # Validate responses and handle errors
            for response in responses:
                try:
                    response.validate_response()
                except DeviceNotRegisteredError:
                    print(f"Invalid token (device unregistered): {response.push_message.to}")
                    # TODO: Mark user as inactive in database
                except PushServerError as e:
                    print(f"Push server error: {e.errors}")

        except Exception as e:
            print(f"Fatal error dispatching notifications: {e}")
