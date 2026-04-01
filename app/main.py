import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.ui_routes import router as ui_router
from app.scheduler import scheduler_loop
import os

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler_task = asyncio.create_task(scheduler_loop())
    yield
    # Shutdown
    scheduler_task.cancel()

app = FastAPI(title="DropCatcher", lifespan=lifespan)

# Mount static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")

# Include UI routes
app.include_router(ui_router)
