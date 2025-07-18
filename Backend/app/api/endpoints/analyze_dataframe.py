from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
from llama_index.core.query_engine import PandasQueryEngine
from llama_index.llms.openai import OpenAI
import os

router = APIRouter()

@router.post("/analyze_dataframe/")
async def analyze_dataframe(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    file_location = f"temp_data/{file.filename}"
    os.makedirs("temp_data", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(file_location)
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    query_engine = PandasQueryEngine(df, llm=llm)
    response = query_engine.query(question)

    os.remove(file_location)
    return {"answer": str(response)}
