from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from src.db import AsyncSessionLocal
from src import models
from src.config import CLEANUP_DAYS


async def delete_unused_links():
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=CLEANUP_DAYS)

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(models.Link).where(models.Link.last_used < cutoff_date)
        )
        old_links = result.scalars().all()

        if old_links:
            for link in old_links:
                await session.delete(link)

            await session.commit()
            print(f"Удалено {len(old_links)} старых ссылок")
        else:
            print("все ссылки актуальны")
