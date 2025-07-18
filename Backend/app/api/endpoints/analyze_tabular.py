from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.openai import OpenAI
import pandas as pd
import io
import json
import logging

from app.core.exceptions import (
    DataAnalysisError,
    FileValidationError,
    QueryProcessingError
)
from app.utils.file_validator import validate_dataframe_content, validate_upload_file

router = APIRouter()
logger = logging.getLogger(__name__)

def parse_tabular_file(file: UploadFile) -> pd.DataFrame:
    """Parse uploaded tabular file (CSV, Excel, JSON) into a pandas DataFrame."""
    logger.info(f"Parsing file: {file.filename}")
    
    try:
        # Read file content
        content = file.file.read()
        
        # Determine file type and parse accordingly
        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            except UnicodeDecodeError:
                # Try different encoding
                df = pd.read_csv(io.StringIO(content.decode('latin-1')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.json'):
            # Try to parse as JSON
            json_data = json.loads(content.decode('utf-8'))
            # Handle different JSON structures
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                df = pd.DataFrame([json_data])
            else:
                raise DataAnalysisError("Unsupported JSON format: expected list of objects or single object")
        else:
            raise FileValidationError(f"Unsupported file format: {file.filename}. Supported formats: CSV, Excel (.xlsx, .xls), JSON")
        
        # Reset file pointer for potential reuse
        file.file.seek(0)
        
        # Validate the parsed dataframe
        validate_dataframe_content(df)
        
        logger.info(f"Successfully parsed file: {file.filename}, shape: {df.shape}, columns: {list(df.columns)}")
        
        return df
        
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        raise DataAnalysisError(f"Failed to parse {file.filename}: {str(e)}")
    except json.JSONDecodeError as e:
        raise DataAnalysisError(f"Invalid JSON format in {file.filename}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error parsing file {file.filename}: {str(e)}")
        raise DataAnalysisError(f"Failed to parse file {file.filename}: {str(e)}")

@router.post("/analyze/")
async def analyze_data(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    """Analyze tabular data with natural language questions."""
    logger.info(f"Tabular analysis endpoint called - File: {file.filename}, Question: {question}")
    
    try:
        # Validate the uploaded file
        validate_upload_file(file)
        
        # Validate question input
        if not question or not question.strip():
            raise QueryProcessingError("Question cannot be empty")
        
        if len(question.strip()) < 3:
            raise QueryProcessingError("Question must be at least 3 characters long")
        
        # Parse the uploaded file
        df = parse_tabular_file(file)
        
        # Initialize LLM and query engine
        try:
            llm = OpenAI(model="gpt-3.5-turbo")
            query_engine = PandasQueryEngine(df=df, llm=llm)
        except Exception as e:
            logger.error(f"Failed to initialize query engine: {str(e)}")
            raise DataAnalysisError(f"Failed to initialize analysis engine: {str(e)}")
        
        # Query the data
        try:
            response = query_engine.query(question)
        except Exception as e:
            logger.error(f"Query execution failed for question '{question}': {str(e)}")
            raise QueryProcessingError(f"Failed to process query: {str(e)}")
        
        logger.info(f"Successfully analyzed {file.filename} with question: {question}")
        
        return {
            "success": True,
            "answer": str(response),
            "filename": file.filename,
            "question": question,
            "data_shape": df.shape,
            "columns": list(df.columns)
        }
        
    except (FileValidationError, DataAnalysisError, QueryProcessingError) as e:
        logger.error(f"Analysis error for file {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in analyze_data for file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")
