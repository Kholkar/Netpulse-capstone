from fastapi import FastAPI

from app.routes.devices import router

app = FastAPI(
    title="NetPulse",
    description="Network device monitoring API with in-memory or MySQL storage",
)
app.include_router(router)