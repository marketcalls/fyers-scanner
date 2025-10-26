"""
Scheduler for automatic daily token cleanup at 3:00 AM IST
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from database import SessionLocal, User
from logger import logger
import pytz


class TokenCleanupScheduler:
    """
    Scheduler to automatically clear Fyers access tokens at 3:00 AM IST daily
    This ensures users re-authenticate every day since Fyers tokens expire after 24 hours
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ist_timezone = pytz.timezone('Asia/Kolkata')

    def clear_all_tokens(self):
        """
        Clear all user access tokens from the database
        This forces users to re-authenticate when they next access the app
        """
        db: Session = SessionLocal()
        try:
            # Update all users to clear their access tokens
            updated_count = db.query(User).update({"access_token": None})
            db.commit()

            logger.info(f"[Token Cleanup] Cleared access tokens for {updated_count} users at 3:00 AM IST")
            logger.info(f"[Token Cleanup] Users will need to re-authenticate on next login")

        except Exception as e:
            logger.error(f"[Token Cleanup] Error clearing tokens: {str(e)}")
            db.rollback()
        finally:
            db.close()

    def start(self):
        """
        Start the scheduler with daily token cleanup at 3:00 AM IST
        """
        # Schedule the task to run at 3:00 AM IST every day
        trigger = CronTrigger(
            hour=3,
            minute=0,
            second=0,
            timezone=self.ist_timezone
        )

        self.scheduler.add_job(
            self.clear_all_tokens,
            trigger=trigger,
            id='daily_token_cleanup',
            name='Clear Fyers access tokens at 3:00 AM IST',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("[Scheduler] Started daily token cleanup scheduler - will run at 3:00 AM IST")

    def shutdown(self):
        """
        Gracefully shutdown the scheduler
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("[Scheduler] Scheduler shut down successfully")


# Global scheduler instance
scheduler_instance = TokenCleanupScheduler()
