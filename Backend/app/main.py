from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from app.api.endpoints import analyze_tabular
import os

from app.api.endpoints.upload_file import router as upload_file_router
from app.api.endpoints.analyze_sql import router as analyze_sql_router
from app.api.endpoints.enhanced_analysis import router as enhanced_analysis_router
from app.api.endpoints.dashboard import router as dashboard_router
from app.api.endpoints.brain import router as brain_router
from app.core.error_handlers import register_error_handlers

load_dotenv()
print("OPENAI_API_KEY is set:", os.getenv("OPENAI_API_KEY") is not None)

app = FastAPI(
    title="AI Data Analyst API",
    description="Enterprise-grade autonomous analytics engine",
    version="1.0.0"
)

# Register error handlers
register_error_handlers(app)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Type", "Content-Length"]
)

# Create charts and reports directories if they don't exist
charts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "charts")
reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
os.makedirs(charts_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

# Mount static files for charts (to fix visualization serving)
app.mount("/charts", StaticFiles(directory=charts_dir), name="charts")

app.include_router(upload_file_router, prefix="/api")
app.include_router(analyze_sql_router, prefix="/api")
app.include_router(enhanced_analysis_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(brain_router, prefix="/api/brain")
app.include_router(analyze_tabular.router, prefix="/api")
