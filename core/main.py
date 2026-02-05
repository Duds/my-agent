from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.router import ModelRouter, Intent
from core.security import SecurityValidator
from core.adapters_local import OllamaAdapter
from core.adapters_remote import RemoteAdapter
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Secure Personal Agentic Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Real Adapters
local_model = OllamaAdapter(model_name="llama3:latest")
security_validator = SecurityValidator(judge_adapter=local_model)

# Real or Mocked Clients based on ENV
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_api_key:
    anthropic_client = RemoteAdapter(
        model_name="claude-3-sonnet-20240229",
        api_key=anthropic_api_key,
        base_url="https://api.anthropic.com/v1/messages"
    )
else:
    anthropic_client = RemoteAdapter(model_name="claude-skeleton", api_key="none", base_url="anthropic")

router = ModelRouter(local_client=local_model, remote_clients={
    "anthropic": anthropic_client,
    "moonshot": RemoteAdapter(model_name="kimi-skeleton", api_key="none", base_url="moonshot")
}, security_validator=security_validator)

class UserQuery(BaseModel):
    text: str

@app.post("/query")
async def handle_query(query: UserQuery):
    routing_info = await router.route_request(query.text)
    return {
        "status": "success",
        "routing": {
            "intent": routing_info["intent"],
            "adapter": routing_info["adapter"],
            "requires_privacy": routing_info["requires_privacy"]
        },
        "answer": routing_info["answer"],
        "security": routing_info["security"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Secure Personal Agentic Platform"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
