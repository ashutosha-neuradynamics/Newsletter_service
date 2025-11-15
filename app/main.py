from fastapi import FastAPI
from app.routers import topics, subscribers, subscriptions, content

app = FastAPI(title="Newsletter Service", version="1.0.0")

app.include_router(topics.router)
app.include_router(subscribers.router)
app.include_router(subscriptions.router)
app.include_router(content.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

