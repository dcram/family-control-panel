from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.children import router as children_router

app = FastAPI(title="Family Control Panel", version="0.1.0")

app.include_router(router=auth_router, prefix="/api/v1")
app.include_router(router=children_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
