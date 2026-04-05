from fastapi import APIRouter

from services.issue_analyzer import load_issues

router = APIRouter(tags=["issues"])


@router.get("/issues")
async def get_issues() -> dict:
    issues = load_issues()
    return {"total": len(issues), "issues": issues}
