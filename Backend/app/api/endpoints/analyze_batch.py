from fastapi import APIRouter, HTTPException, UploadFile
from app.models.schemas import BatchRequest, BatchFile
from app.agents.data_analyst import analyze_data, save_upload_file_to_disk
import os

router = APIRouter()

async def get_file_by_name(file_name: str) -> UploadFile:
    try:
        file_path = os.path.join("uploads", file_name)
        return UploadFile(filename=file_name, file=open(file_path, "rb"))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")

@router.post("/analyze-batch")
async def analyze_batch(batch: BatchRequest):
    try:
        results = []
        for item in batch.files:
            file = await get_file_by_name(item.file_name)
            file_path = save_upload_file_to_disk(file)
            analysis_result = analyze_data(file_path, item.query, item.analysis_type)
            results.append({
                "file_name": item.file_name,
                "insights": analysis_result.get("describe"),
                "visualizations": analysis_result.get("visualizations"),
                "recommendations": analysis_result.get("modeling")
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
