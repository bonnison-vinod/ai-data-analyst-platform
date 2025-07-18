from fastapi import APIRouter

router = APIRouter()

@router.get("/analyze_sql/")
async def analyze_sql():
    return {"message": "SQL analysis endpoint is working."}
