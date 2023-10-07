from fastapi import FastAPI

from src.coil.router import router as coil_router


app = FastAPI(
    title="Warehouse metal coil app",
)

routers = (
    coil_router,
)

[app.include_router(router) for router in routers]
