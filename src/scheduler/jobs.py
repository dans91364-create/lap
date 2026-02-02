"""Scheduler jobs for automated data collection."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from config.settings import settings, get_collection_times
from src.services.coleta_service import ColetaService

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)


async def collect_all_municipios_job():
    """Job to collect biddings for all municipalities."""
    logger.info("Starting scheduled collection for all municipalities")
    try:
        service = ColetaService()
        stats = await service.collect_all_municipios(years=2)
        logger.info(f"Collection completed: {stats}")
    except Exception as e:
        logger.error(f"Error in collection job: {e}")


def setup_scheduler():
    """Setup scheduler jobs."""
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled")
        return
    
    logger.info("Setting up scheduler")
    
    # Get collection times from settings
    collection_times = get_collection_times()
    
    # Add job for each collection time
    for time_str in collection_times:
        try:
            hour, minute = time_str.split(':')
            scheduler.add_job(
                collect_all_municipios_job,
                CronTrigger(hour=int(hour), minute=int(minute)),
                id=f'collect_municipios_{time_str}',
                name=f'Collect municipalities at {time_str}',
                replace_existing=True
            )
            logger.info(f"Scheduled collection job for {time_str}")
        except Exception as e:
            logger.error(f"Error scheduling job for {time_str}: {e}")
    
    return scheduler


def start_scheduler():
    """Start the scheduler."""
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler is disabled")
        return None
    
    try:
        scheduler.start()
        logger.info("Scheduler started successfully")
        return scheduler
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        return None


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
