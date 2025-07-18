from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any
import json
from openai import OpenAI
import tempfile
import os
import uuid
from ...brain.analyzer import EnhancedDataAnalyzer
from ...brain.prompt_generator import OptimizedPromptGenerator, TokenTracker
from dataclasses import dataclass

# Initialize OpenAI client
client = OpenAI()

router = APIRouter()
analyzer = EnhancedDataAnalyzer()
prompt_generator = OptimizedPromptGenerator()
token_tracker = TokenTracker()

@dataclass
class AnalysisRequest:
    analysis_type: str
    sql_query: str = None
    chart_type: str = "bar"
    group_by: str = None
    aggregation: str = "sum"
    time_column: str = None
    value_columns: list = None
    output_format: str = "HTML"
    filters: dict = None

def create_analysis_request(llm_decision: Dict[str, Any]) -> AnalysisRequest:
    """Convert LLM decision to analysis request"""
    # Map short codes to full names
    analysis_map = {
        'ts': 'time_series', 'corr': 'correlation', 'piv': 'pivot',
        'dist': 'distribution', 'comp': 'comparison', 'out': 'outlier', 'stat': 'statistical'
    }
    
    chart_map = {
        'L': 'line', 'B': 'bar', 'P': 'pie', 'S': 'scatter', 
        'H': 'histogram', 'X': 'box', 'M': 'heatmap'
    }
    
    analysis_type = analysis_map.get(llm_decision.get('analysis_type', 'piv'), 'pivot')
    chart_type = chart_map.get(llm_decision.get('chart_type', 'B'), 'bar')
    
    return AnalysisRequest(
        analysis_type=analysis_type,
        chart_type=chart_type,
        group_by=llm_decision.get('group_by') if llm_decision.get('group_by') != 'null' else None,
        aggregation=llm_decision.get('agg', llm_decision.get('aggregation', 'sum')),
        time_column=llm_decision.get('time_col', llm_decision.get('time_column')) if llm_decision.get('time_col') != 'null' else None,
        value_columns=llm_decision.get('value_cols', llm_decision.get('value_columns', [])),
        output_format="HTML",
        filters=llm_decision.get('filters')
    )

@router.post("/analyze-smart")
async def smart_analysis(
    file: UploadFile = File(...),
    query: str = Form(...)
):
    """Smart analysis using AI brain system"""
    import time
    start_time = time.time()
    performance_metrics = {}
    
    try:
        # 1. Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # 2. Read and process data
        df = analyzer.read_file(tmp_file_path)
        metadata = analyzer.extract_metadata(df)
        
        # 3. Generate optimized prompt
        prompt = prompt_generator.generate_smart_prompt(
            metadata.__dict__, 
            query
        )
        
        # 4. Get LLM recommendation (using GPT-4.1)
        openai_response = client.chat.completions.create(
            model="gpt-4o",  # GPT-4.1 (faster and more efficient)
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,  # Reduced for faster response
            temperature=0.0  # Deterministic output for consistent results
        )
        
        # 5. Parse LLM response
        response_content = openai_response.choices[0].message.content
        
        # Extract JSON from response if it contains other text
        if '```json' in response_content:
            json_start = response_content.find('```json') + 7
            json_end = response_content.find('```', json_start)
            response_content = response_content[json_start:json_end]
        elif '{' in response_content:
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            response_content = response_content[json_start:json_end]
        
        try:
            llm_decision = json.loads(response_content)
        except json.JSONDecodeError as e:
            # Fallback to basic analysis if JSON parsing fails
            llm_decision = {
                'analysis_type': 'piv',
                'chart_type': 'B',
                'group_by': None,
                'aggregation': 'sum',
                'time_col': None,
                'value_cols': []
            }
        
        # 6. Execute analysis
        analysis_request = create_analysis_request(llm_decision)
        result = analyzer.execute_analysis(df, analysis_request)

        # 7. Generate (and store) Enhanced Excel Dashboard for download
        try:
            from app.utils.enhanced_excel_generator import create_excel_with_dashboards_and_charts
            session_id = f"brain_{uuid.uuid4().hex}"
            reports_dir = os.path.abspath("reports")
            os.makedirs(reports_dir, exist_ok=True)
            excel_filepath = os.path.join(reports_dir, f"enhanced_dashboard_{session_id}.xlsx")
            excel_bytes = create_excel_with_dashboards_and_charts(df, result, query, session_id)
            with open(excel_filepath, "wb") as f:
                f.write(excel_bytes.read())
        except Exception as excel_error:
            # If Excel generation fails, still continue with the analysis
            print(f"Enhanced Excel generation failed: {excel_error}")
            # Fallback to basic Excel generation
            try:
                from app.utils.excel_generator import create_excel_with_pivots_and_charts
                session_id = f"brain_{uuid.uuid4().hex}"
                excel_filepath = os.path.join(reports_dir, f"basic_report_{session_id}.xlsx")
                excel_bytes = create_excel_with_pivots_and_charts(df, result, query, session_id)
                with open(excel_filepath, "wb") as f:
                    f.write(excel_bytes.read())
            except Exception as fallback_error:
                print(f"Fallback Excel generation also failed: {fallback_error}")
                session_id = f"brain_{uuid.uuid4().hex}"
                excel_filepath = None

        # 8. Store the excel file path in a simple session store (in memory)
        global progress_store
        if 'progress_store' not in globals():
            progress_store = {}
        progress_store[session_id] = {
            'report_filename': excel_filepath,
            'completed': True
        }

        # 9. Track token usage
        token_usage = token_tracker.track_request(
            prompt, 
            openai_response.choices[0].message.content
        )
        
        # 10. Clean up temporary file
        os.unlink(tmp_file_path)
        
        # Add session_id to result for frontend compatibility
        if isinstance(result, dict):
            result['session_id'] = session_id
            
            # Handle multiple chart filenames (backwards compatibility)
            if 'chart_filenames' in result and isinstance(result['chart_filenames'], list):
                result['chart_filename'] = result['chart_filenames'][0] if result['chart_filenames'] else None
        
        return {
            "success": True,
            "analysis_result": result,
            "llm_decision": llm_decision,
            "token_usage": token_usage,
            "metadata": {k: v for k, v in metadata.__dict__.items() if k != 'sample_stats'},
            "query": query,
            "session_id": session_id
        }
        
    except Exception as e:
        # Clean up temporary file on error
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        # Log the full error for debugging
        import traceback
        error_details = f"Error in brain analysis: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
        print(error_details)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/brain-stats")
async def get_brain_stats():
    """Get AI brain usage statistics"""
    return token_tracker.get_usage_stats()

@router.get("/chart/{chart_filename}")
async def get_chart(chart_filename: str):
    """Serve chart files with proper headers"""
    from fastapi.responses import HTMLResponse
    import os
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    charts_dir = os.path.join(project_root, "charts")
    charts_dir = os.path.abspath(charts_dir)
    chart_path = os.path.join(charts_dir, chart_filename)
    
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found")
    
    # Read the HTML content
    with open(chart_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HTMLResponse(
        content=html_content,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
            "X-Frame-Options": "ALLOWALL",
            "Content-Security-Policy": "frame-ancestors 'self' http://localhost:3000"
        }
    )

@router.get("/download-report/{session_id}")
async def download_brain_report(session_id: str):
    """Download the generated brain analysis report"""
    global progress_store
    
    if 'progress_store' not in globals() or session_id not in progress_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = progress_store[session_id]
    
    if not session_data.get('completed'):
        raise HTTPException(status_code=202, detail="Report still generating")
    
    if session_data.get('error'):
        raise HTTPException(status_code=500, detail=session_data['error'])
    
    report_filename = session_data.get('report_filename')
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

