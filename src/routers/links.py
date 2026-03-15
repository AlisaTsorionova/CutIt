from fastapi import APIRouter, Depends, HTTPException, Query, responses
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils import generate_short_code, normalize_url
from src.db import get_db
from datetime import datetime, timezone
from src import models
from src.config import BASE_URL
from sqlalchemy import select, delete, update
from src.auth import current_user, optional_current_user

router = APIRouter(tags=["links"])


@router.post(
    "/links/shorten",
    summary="Создать короткую ссылку",
)
async def create_short_link(
    original_url: str,
    custom_alias: str = None,
    expires_at: datetime = Query(
        None,
        description="Дата истечения в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС / ГГГГ-ММ-ДД",
        example="2026-12-31 23:59:59",
    ),
    session: AsyncSession = Depends(get_db),
    user: models.User = Depends(optional_current_user),
):
    if custom_alias:
        # проверяем, не дублируется ли алиас
        result = await session.execute(
            select(models.Link).where(models.Link.short_code == custom_alias)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=400, detail=f"Алиас '{custom_alias}' уже занят"
            )

        short_code = custom_alias
    else:
        while True:
            # проверяем, что случайно не повторилось(вряд ли)
            short_code = generate_short_code()
            result = await session.execute(
                select(models.Link).where(models.Link.short_code == short_code)
            )
            exists = result.scalar_one_or_none()

            if not exists:
                break

    link = models.Link(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
        owner_id=user.id if user else None,
    )

    session.add(link)
    await session.commit()
    await session.refresh(link)

    return {
        "short_url": f"https://{BASE_URL}/{short_code}",
        "original_url": original_url,
        "expires_at": expires_at,
        "custom_alias": custom_alias,
        "owner_id": link.owner_id,
    }


@router.get("/links/search")
async def search_links(original_url: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(models.Link).where(models.Link.original_url == original_url)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(404, "URL не найден")

    if not link.short_code:
        raise HTTPException(404, "Произошла ошибка, короткой ссылки не существует")

    return {
        "short_code": link.short_code,
        "original_url": link.original_url,
        "created_at": link.created_at,
    }


@router.get("/links/{short_code}")
async def redirect(
    short_code: str,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(models.Link).where(models.Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(404, "Ссылка не найдена")

    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(410, "Срок действия истек")

    link.clicks += 1
    link.last_used = datetime.now(timezone.utc)
    await session.commit()

    return responses.RedirectResponse(link.original_url)


@router.get("/links/{short_code}/stats")
async def get_link_stats(short_code: str, session: AsyncSession = Depends(get_db)):

    result = await session.execute(
        select(models.Link).where(models.Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(404, "Ссылка не найдена")

    return {
        "original_url": link.original_url,
        "short_code": link.short_code,
        "clicks": link.clicks,
        "created_at": link.created_at,
        "last_used": link.last_used,
        "expires_at": link.expires_at,
    }


@router.put("/links/{short_code}")
async def update_link(
    short_code: str,
    new_short_code: str,
    session: AsyncSession = Depends(get_db),
    user: models.User = Depends(current_user),
):
    result = await session.execute(
        select(models.Link).where(models.Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(404, "Ссылка не найдена")

    if link.owner_id != user.id:
        raise HTTPException(403, "Ссылка недоступна")

    result = await session.execute(
        select(models.Link).where(models.Link.short_code == new_short_code)
    )
    exists = result.scalar_one_or_none()

    if exists:
        raise HTTPException(400, f"Код '{new_short_code}' уже используется")

    link.short_code = new_short_code
    await session.commit()

    return {
        "message": "Короткая ссылка обновлена",
        "old_code": short_code,
        "new_code": new_short_code,
        "new_url": f"https://{BASE_URL}/{new_short_code}",
    }


@router.delete("/links/{short_code}")
async def delete_link(
    short_code: str,
    session: AsyncSession = Depends(get_db),
    user: models.User = Depends(current_user),
):

    result = await session.execute(
        select(models.Link).where(models.Link.short_code == short_code)
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(404, "Такой ссылки нет, возможно, она уже удалена")

    if link.owner_id != user.id:
        raise HTTPException(403, "Операция недоступна")

    await session.delete(link)
    await session.commit()

    return {"message": "Ссылка удалена"}
