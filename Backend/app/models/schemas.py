from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalysisRequest(BaseModel):
    query: str
    analysis_type: str = "descriptive"

class AnalysisResponse(BaseModel):
    insights: str
    visualization: Dict[str, Any]  # Can be Plotly JSON, base64 image, etc.
    recommendations: List[str]

# Batch processing models
class BatchFile(BaseModel):
    file_name: str
    query: str
    analysis_type: str = "descriptive"

class BatchRequest(BaseModel):
    files: List[BatchFile]

