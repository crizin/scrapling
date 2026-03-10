from fastapi import APIRouter

from app.schemas.request import DynamicRequest
from app.schemas.response import ScrapeResponse
from app.services.scraper import fetch_dynamic

router = APIRouter()


@router.post("/dynamic", response_model=ScrapeResponse)
async def dynamic(req: DynamicRequest) -> ScrapeResponse:
    return await fetch_dynamic(req)
