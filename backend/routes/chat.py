from fastapi import APIRouter
from pydantic import BaseModel

from services.agent_service import run_agent_query

router = APIRouter(tags=["agent"])


class AgentQueryRequest(BaseModel):
    question: str


@router.post("/agent/query")
async def agent_query(body: AgentQueryRequest) -> dict:
    return run_agent_query(body.question)
