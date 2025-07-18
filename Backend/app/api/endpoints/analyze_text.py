# app/api/endpoints/analyze_text.py

from fastapi import APIRouter, UploadFile, File, Form
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
import os

router = APIRouter()

@router.post("/analyze_text/")
async def analyze_text(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    # Save uploaded file temporarily
    file_location = f"temp_data/{file.filename}"
    os.makedirs("temp_data", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Load and index document
    documents = SimpleDirectoryReader("temp_data/").load_data()
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(llm=llm)

    # Query
    response = query_engine.query(question)

    # Clean up temp file
    os.remove(file_location)

    return {"answer": str(response)}
