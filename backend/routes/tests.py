from fastapi import APIRouter

from services.issue_analyzer import load_tests

router = APIRouter(tags=["tests"])


@router.get("/tests")
async def get_tests() -> dict:
    tests = load_tests()
    return {"total": len(tests), "tests": tests}
