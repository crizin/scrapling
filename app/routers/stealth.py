from fastapi import APIRouter

from app.schemas.request import StealthRequest
from app.schemas.response import ScrapeResponse
from app.services.scraper import fetch_stealth

router = APIRouter()


@router.post("/stealth", response_model=ScrapeResponse)
async def stealth(req: StealthRequest) -> ScrapeResponse:
    return await fetch_stealth(req)
