#!/usr/bin/env python3
"""
Enhanced Analysis API Endpoints
Provides comprehensive report generation with progress tracking and multiple data source support
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import pandas as pd
import json
import asyncio
from datetime import datetime
import os
import logging

from app.core.enhanced_report_generator import (
    EnhancedReportGenerator, 
    ProgressUpdate, 
    DataSourceConnector,
    MagicQuestionProcessor,
    ReportStatus
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Global storage for progress tracking (in production, use Redis or database)
progress_store = {}

class ReportRequest(BaseModel):
    question: str
    analysis_type: str = "comprehensive"
    custom_sheets: Optional[List[Dict]] = []
    
class DatabaseConnectionRequest(BaseModel):
    connection_string: str
    query: str
    question: str = "Analyze this data"
    
class APIConnectionRequest(BaseModel):
    api_url: str
    headers: Optional[Dict[str, str]] = {}
    question: str = "Analyze this data"

def store_progress(session_id: str, progress: ProgressUpdate):
    """Store progress update for session"""
    progress_store[session_id] = {
        'status': progress.status.value,
        'percentage': progress.percentage,
        'message': progress.message,
        'current_step': progress.current_step,
        'total_steps': progress.total_steps,
        'current_step_number': progress.current_step_number,
        'timestamp': datetime.now().isoformat()
    }

@router.post("/generate-enhanced-report/")
async def generate_enhanced_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    question: str = Form("Provide comprehensive analysis of this data"),
    analysis_type: str = Form("comprehensive"),
    custom_sheets: str = Form("[]")
):
    """
    Generate comprehensive Excel report with multiple sheets and interactive features
    
    Features:
    - Interactive Dashboard with visualizations
    - Pivot Tables and Analysis
    - Clean structured data
    - Custom analysis sheets
    - Progress tracking
    """
    try:
        # Generate unique session ID
        session_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file.filename)}"
        
        # Initialize report generator
        generator = EnhancedReportGenerator()
        
        # Set up progress callback
        def progress_callback(progress: ProgressUpdate):
            store_progress(session_id, progress)
            logger.info(f"Session {session_id}: {progress.percentage:.1f}% - {progress.message}")
        
        generator.set_progress_callback(progress_callback)
        
        # Parse custom sheets
        try:
            custom_sheets_list = json.loads(custom_sheets) if custom_sheets else []
        except json.JSONDecodeError:
            custom_sheets_list = []
        
        # Process the uploaded file
        file_content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        
        try:
            dataframe = await DataSourceConnector.process_file_upload(file_content, file_extension)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
        
        # Process the question using Magic Question Processor
        magic_processor = MagicQuestionProcessor()
        analysis_config = await magic_processor.process_question(question, dataframe)
        
        # Merge custom sheets from question processing
        if analysis_config.get('custom_sheets'):
            custom_sheets_list.extend(analysis_config['custom_sheets'])
        
        # Start background task for report generation
        background_tasks.add_task(
            generate_report_background,
            generator,
            dataframe,
            question,
            custom_sheets_list,
            analysis_type,
            session_id
        )
        
        return JSONResponse({
            "session_id": session_id,
            "message": "Report generation started",
            "status": "initializing",
            "progress_endpoint": f"/api/report-progress/{session_id}",
            "download_endpoint": f"/api/download-report/{session_id}"
        })
        
    except Exception as e:
        logger.error(f"Error starting report generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def generate_report_background(
    generator: EnhancedReportGenerator,
    dataframe: pd.DataFrame,
    question: str,
    custom_sheets: List[Dict],
    analysis_type: str,
    session_id: str
):
    """Background task for report generation"""
    try:
        # Generate the comprehensive report
        report_filename, analysis_summary = await generator.generate_comprehensive_report(
            data=dataframe,
            question=question,
            custom_sheets=custom_sheets,
            analysis_type=analysis_type
        )
        
        # Store final result
        progress_store[session_id].update({
            'report_filename': report_filename,
            'analysis_summary': analysis_summary,
            'completed': True
        })
        
    except Exception as e:
        logger.error(f"Error in background report generation: {str(e)}")
        progress_store[session_id].update({
            'status': ReportStatus.ERROR.value,
            'error': str(e),
            'completed': True
        })

@router.get("/report-progress/{session_id}")
async def get_report_progress(session_id: str):
    """Get progress of report generation"""
    if session_id not in progress_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress_data = progress_store[session_id]
    
    return JSONResponse({
        "session_id": session_id,
        "status": progress_data.get('status', 'unknown'),
        "percentage": progress_data.get('percentage', 0),
        "message": progress_data.get('message', ''),
        "current_step": progress_data.get('current_step', ''),
        "current_step_number": progress_data.get('current_step_number', 0),
        "total_steps": progress_data.get('total_steps', 6),
        "completed": progress_data.get('completed', False),
        "error": progress_data.get('error'),
        "timestamp": progress_data.get('timestamp')
    })

@router.get("/download-report/{session_id}")
async def download_report(session_id: str):
    """Download the generated report"""
    if session_id not in progress_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress_data = progress_store[session_id]
    
    if not progress_data.get('completed'):
        raise HTTPException(status_code=202, detail="Report still generating")
    
    if progress_data.get('error'):
        raise HTTPException(status_code=500, detail=progress_data['error'])
    
    report_filename = progress_data.get('report_filename')
    if not report_filename or not os.path.exists(report_filename):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Extract just the filename for the download
    filename = os.path.basename(report_filename)
    
    return FileResponse(
        path=report_filename,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.post("/analyze-database/")
async def analyze_database(request: DatabaseConnectionRequest, background_tasks: BackgroundTasks):
    """Connect to database and generate analysis report"""
    try:
        # Generate session ID
        session_id = f"db_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        generator = EnhancedReportGenerator()
        magic_processor = MagicQuestionProcessor()
        
        def progress_callback(progress: ProgressUpdate):
            store_progress(session_id, progress)
        
        generator.set_progress_callback(progress_callback)
        
        # Connect to database and fetch data
        try:
            dataframe = await DataSourceConnector.connect_to_database(
                request.connection_string, 
                request.query
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Database connection error: {str(e)}")
        
        # Process question and generate analysis config
        analysis_config = await magic_processor.process_question(request.question, dataframe)
        
        # Start background report generation
        background_tasks.add_task(
            generate_report_background,
            generator,
            dataframe,
            request.question,
            analysis_config.get('custom_sheets', []),
            "comprehensive",
            session_id
        )
        
        return JSONResponse({
            "session_id": session_id,
            "message": "Database analysis started",
            "data_shape": dataframe.shape,
            "columns": list(dataframe.columns),
            "progress_endpoint": f"/api/report-progress/{session_id}",
            "download_endpoint": f"/api/download-report/{session_id}"
        })
        
    except Exception as e:
        logger.error(f"Database analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-api/")
async def analyze_api_data(request: APIConnectionRequest, background_tasks: BackgroundTasks):
    """Connect to API and generate analysis report"""
    try:
        # Generate session ID
        session_id = f"api_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        generator = EnhancedReportGenerator()
        magic_processor = MagicQuestionProcessor()
        
        def progress_callback(progress: ProgressUpdate):
            store_progress(session_id, progress)
        
        generator.set_progress_callback(progress_callback)
        
        # Connect to API and fetch data
        try:
            dataframe = await DataSourceConnector.connect_to_api(
                request.api_url, 
                request.headers
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"API connection error: {str(e)}")
        
        # Process question and generate analysis config
        analysis_config = await magic_processor.process_question(request.question, dataframe)
        
        # Start background report generation
        background_tasks.add_task(
            generate_report_background,
            generator,
            dataframe,
            request.question,
            analysis_config.get('custom_sheets', []),
            "comprehensive",
            session_id
        )
        
        return JSONResponse({
            "session_id": session_id,
            "message": "API data analysis started",
            "data_shape": dataframe.shape,
            "columns": list(dataframe.columns),
            "progress_endpoint": f"/api/report-progress/{session_id}",
            "download_endpoint": f"/api/download-report/{session_id}"
        })
        
    except Exception as e:
        logger.error(f"API analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/magic-question/")
async def magic_question_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    question: str = Form(...),
):
    """
    Magic question processing - automatically determines what analysis to perform
    based on the user's natural language question
    """
    try:
        session_id = f"magic_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(question)}"
        
        # Process file
        file_content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()
        dataframe = await DataSourceConnector.process_file_upload(file_content, file_extension)
        
        # Initialize magic processor
        magic_processor = MagicQuestionProcessor()
        analysis_config = await magic_processor.process_question(question, dataframe)
        
        # Initialize report generator
        generator = EnhancedReportGenerator()
        
        def progress_callback(progress: ProgressUpdate):
            store_progress(session_id, progress)
        
        generator.set_progress_callback(progress_callback)
        
        # Start background generation with magic-derived configuration
        background_tasks.add_task(
            generate_report_background,
            generator,
            dataframe,
            question,
            analysis_config.get('custom_sheets', []),
            analysis_config.get('type', 'comprehensive'),
            session_id
        )
        
        return JSONResponse({
            "session_id": session_id,
            "message": f"Magic analysis started for question: '{question}'",
            "detected_analysis": analysis_config,
            "data_info": {
                "shape": dataframe.shape,
                "columns": list(dataframe.columns)
            },
            "progress_endpoint": f"/api/report-progress/{session_id}",
            "download_endpoint": f"/api/download-report/{session_id}"
        })
        
    except Exception as e:
        logger.error(f"Magic question analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/")
async def list_active_sessions():
    """List all active report generation sessions"""
    return JSONResponse({
        "active_sessions": list(progress_store.keys()),
        "total_count": len(progress_store)
    })

@router.delete("/session/{session_id}")
async def cleanup_session(session_id: str):
    """Clean up session data and remove temporary files"""
    if session_id in progress_store:
        # Clean up report file if it exists
        progress_data = progress_store[session_id]
        report_filename = progress_data.get('report_filename')
        if report_filename and os.path.exists(report_filename):
            try:
                os.remove(report_filename)
            except Exception as e:
                logger.warning(f"Could not remove file {report_filename}: {e}")
        
        # Remove from progress store
        del progress_store[session_id]
        
        return JSONResponse({"message": f"Session {session_id} cleaned up successfully"})
    else:
        raise HTTPException(status_code=404, detail="Session not found")
