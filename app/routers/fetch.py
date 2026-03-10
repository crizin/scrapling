from fastapi import APIRouter

from app.schemas.request import FetchRequest
from app.schemas.response import ScrapeResponse
from app.services.scraper import fetch_static

router = APIRouter()


@router.post("/fetch", response_model=ScrapeResponse)
async def fetch(req: FetchRequest) -> ScrapeResponse:
    return await fetch_static(req)
