from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.chat import router as insights_router
from routes.issues import router as issues_router
from routes.tests import router as tests_router

app = FastAPI(
    title="Clinical Intelligence Assistant API",
    version="2.0.0",
    description=(
        "Decision-intelligence backend for clinical product analysts working on EHR workflows, "
        "requirement validation, testing outcomes, and release decisions."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "Clinical Intelligence Assistant backend is running"}


app.include_router(issues_router)
app.include_router(tests_router)
app.include_router(insights_router)
