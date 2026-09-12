import asyncio


class NotificationService:
    async def send_complaint_notification(
        self,
        student_email: str,
        complaint_id: int,
        title: str
    ) -> bool:
        try:
            # Simulate an external notification service
            await asyncio.wait_for(
                self._send_notification(
                    student_email,
                    complaint_id,
                    title
                ),
                timeout=5.0
            )

            return True

        except asyncio.TimeoutError:
            print("Notification service timed out")
            return False

        except Exception as e:
            print(f"Notification service failed: {e}")
            return False

    async def _send_notification(
        self,
        student_email: str,
        complaint_id: int,
        title: str
    ):
        # Temporary mock notification
        print(
            f"Notification sent to {student_email}: "
            f"Complaint #{complaint_id} - {title}"
        )


notification_service = NotificationService()