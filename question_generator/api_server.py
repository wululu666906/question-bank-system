import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from search_module import search_web
from crawler_module import fetch_and_clean_url
from extractor_module import extract_relevant_chunks
from llm_generator import generate_questions_initial, evaluate_and_refine
import httpx
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="External Question Generator API for Dify")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    topic: str

@app.post("/api/generate_questions")
def generate_questions_api(req: QuestionRequest):
    topic = req.topic
    logger.info(f"API called for topic: '{topic}'")
    
    # 1. Search
    search_results = search_web(topic, max_results=3)
    if not search_results:
        raise HTTPException(status_code=404, detail="No search results found.")

    # 2. Crawl
    combined_raw_text = ""
    for idx, result in enumerate(search_results):
        url = result.get('href')
        if not url:
            continue
        content = fetch_and_clean_url(url)
        if content:
            combined_raw_text += f"\n--- 来源 {idx+1}: {url} ---\n{content}\n"

    if not combined_raw_text.strip():
        raise HTTPException(status_code=400, detail="Failed to extract text from URLs.")

    # 3. Extract
    relevant_context = extract_relevant_chunks(combined_raw_text, topic, max_chars=4000)
    
    # 4. Generate
    initial_questions = generate_questions_initial(context=relevant_context, topic=topic)
    if "error" in initial_questions:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {initial_questions['error']}")

    # 5. Evaluate and Refine
    final_result = evaluate_and_refine(initial_questions, context=relevant_context, topic=topic)
    
    return {
        "status": "success",
        "topic": topic,
        "evaluation_score": final_result.get("evaluation", {}).get("score", None),
        "was_refined": final_result.get("refined", False),
        "questions": final_result.get("final_questions", {})
    }

@app.post("/api/dify/v1/workflows/run")
async def dify_proxy(request: Request):
    """
    Proxy request to Dify API, injecting the API key securely.
    Supports streaming responses.
    """
    dify_url = "https://api.dify.ai/v1/workflows/run"
    dify_api_key = os.getenv("DIFY_API_KEY")
    
    if not dify_api_key:
        raise HTTPException(status_code=500, detail="DIFY_API_KEY not configured in backend.")

    # Get the request body
    body = await request.json()
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {dify_api_key}",
        "Content-Type": "application/json"
    }

    async def generate():
        async with httpx.AsyncClient(timeout=600.0) as client:
            async with client.stream("POST", dify_url, json=body, headers=headers) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    raise HTTPException(status_code=response.status_code, detail=error_detail.decode())
                
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # Default runs on 0.0.0.0:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
