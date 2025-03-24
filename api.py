from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from utils import analyze_company_news, text_to_hindi_speech
from fastapi.middleware.cors import CORSMiddleware
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze_company")
async def analyze_company(company_name: str):
    try:
        results = analyze_company_news(company_name)
        if results:
            summary_text = ""
            for article in results["articles"]:
                summary_text += f"{article['title']}. {article['summary']} "

            audio_bytes = text_to_hindi_speech(summary_text)

            if audio_bytes:
                results["audio_base64"] = base64.b64encode(audio_bytes).decode("utf-8")
            else:
                results["audio_base64"] = None
            return JSONResponse(content=results)
        else:
            raise HTTPException(status_code=404, detail="No news articles found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))