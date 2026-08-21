from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
import PIL.Image
import io
import os
import json

app = FastAPI(title="SatyaFin AI Vision Service")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class FinancialClaim(BaseModel):
    stock_symbol: str = Field(description="The stock ticker or name mentioned (e.g., RELIANCE, TCS). Use 'UNKNOWN' if none.")
    claimed_return_pct: float = Field(description="The percentage of return/profit claimed. E.g., for 50%, output 50.0")
    timeframe_days: int = Field(description="The time frame in days mentioned for the trade. E.g., '1 month' = 30.")
    mentioned_sebi_id: str = Field(description="Any SEBI registration ID found in the image. Use 'NONE' if not found.")

@app.post("/extract-claim")
async def extract_claim(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    try:
        contents = await file.read()
        image = PIL.Image.open(io.BytesIO(contents))
        
        # Using Gemini 3.7 Flash for fast, accurate vision extraction
        model = genai.GenerativeModel("gemini-3.7-flash")
        
        prompt = "Extract the financial claims, target stock, return percentage, timeframe, and SEBI ID from this finfluencer screenshot."
        
        response = model.generate_content(
            [prompt, image],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=FinancialClaim,
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "Member 3 AI Service is online!"}


