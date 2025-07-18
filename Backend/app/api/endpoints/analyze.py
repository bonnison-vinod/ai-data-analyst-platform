import sys
print(sys.path)
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.data_analyst import analyze_data, save_upload_file_to_disk
from app.utils.storytelling import generate_story_from_analysis
from app.utils.excel_generator import create_excel_with_pivots_and_charts
from app.utils.data_cleaning import clean_data
from app.utils.file_validator import validate_file, FileType
from app.core.exceptions import (
    FileValidationError,
    DataProcessingError,
    AnalysisError,
    InvalidParameterError
)
from fastapi.responses import StreamingResponse
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze")
async def analyze_endpoint(
    file: UploadFile = File(...),
    query: str = Form(None),
    analysis_type: str = Form("descriptive"),
    target_column: str = Form(None)
):
    """
    Analyze the uploaded file, clean the data, generate insights, visualizations, modeling, and a plain-English story.
    """
    # Validate file type
    try:
        validate_file(file, FileType.CSV)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Save file to disk
        file_path = save_upload_file_to_disk(file)
        
        # Read and clean data
        df = pd.read_csv(file_path)  # or pd.read_excel(file_path)
        # Example: specify columns to drop, numeric/text columns, or skip rows as needed
        # drop_columns = ['unnecessary_col1', 'unnecessary_col2']
        # numeric_cols = ['price', 'mileage']
        # text_cols = ['make', 'model']
        # df = clean_data(df, drop_columns=drop_columns, numeric_cols=numeric_cols, text_cols=text_cols, skip_rows=0)
        df = clean_data(df)  # Use defaults if you don't have special requirements
        
        # Analyze data (includes cleaning)
        analysis_result = analyze_data(file_path, target_column)  # If your analyze_data expects a file_path
        # If analyze_data expects a DataFrame, use:
        # analysis_result = analyze_data(df, target_column)
        
        # Generate story from analysis
        story = generate_story_from_analysis(analysis_result)
        
        return {
            "insights": analysis_result.get("describe"),
            "visualizations": analysis_result.get("visualizations"),
            "modeling": analysis_result.get("modeling"),
            "story": story
        }
    except DataProcessingError as e:
        raise HTTPException(status_code=422, detail="Data Processing Error: " + str(e))
    except AnalysisError as e:
        raise HTTPException(status_code=422, detail="Analysis Error: " + str(e))
    except InvalidParameterError as e:
        raise HTTPException(status_code=400, detail="Invalid Parameter: " + str(e))
    except Exception as e:
        logger.error("Unexpected Error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/analyze-excel")
async def analyze_excel(file: UploadFile = File(...)):
    # Validate file type
    try:
        validate_file(file, FileType.EXCEL)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        file_path = save_upload_file_to_disk(file)
        df = pd.read_csv(file_path)  # or pd.read_excel(file_path)
        df = clean_data(df)
        analysis_result = analyze_data(file_path)
        story = generate_story_from_analysis(analysis_result)
        excel_bytes = create_excel_with_pivots_and_charts(df, story)
        return StreamingResponse(
            excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=analysis.xlsx"}
        )
    except DataProcessingError as e:
        raise HTTPException(status_code=422, detail="Data Processing Error: " + str(e))
    except AnalysisError as e:
        raise HTTPException(status_code=422, detail="Analysis Error: " + str(e))
    except InvalidParameterError as e:
        raise HTTPException(status_code=400, detail="Invalid Parameter: " + str(e))
    except Exception as e:
        logger.error("Unexpected Error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
