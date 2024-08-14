from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Heath"], responses={404: {"description": "Not found"}})
async def health():
    return {"Status": "Running"}
