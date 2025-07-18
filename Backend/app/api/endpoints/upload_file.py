from fastapi import APIRouter, UploadFile, File, Form
from app.utils.file_validator import validate_upload_file
from app.core.exceptions import ValidationError
import os

router = APIRouter()

@router.post("/upload/")
async def upload_file_info(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    # Validate the uploaded file
    validate_upload_file(file)
    
    # Read file content
    content = await file.read()
    
    # Optional: Save file to uploads directory
    upload_dir = "Backend/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    # Handle existing files by removing them first
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            # If we can't remove it, create a new filename
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(file.filename)
            file_path = os.path.join(upload_dir, f"{name}_{timestamp}{ext}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": file.filename, 
        "size": len(content), 
        "question": question,
        "file_path": file_path,
        "message": "File uploaded and validated successfully"
    }
