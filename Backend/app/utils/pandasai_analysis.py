import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from dotenv import load_dotenv
import os

print("Script started.")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debug: Hide API key
print("API Key:", "***hidden***" if OPENAI_API_KEY else "Not set")

df = pd.read_csv("vehicle_price.csv")
print("Data loaded:")
print(df.head())

llm = OpenAI(api_token=OPENAI_API_KEY)
sdf = SmartDataframe(df, config={"llm": llm})

result = sdf.chat("What is the average price by make?")
print("Result:")
print(result)
