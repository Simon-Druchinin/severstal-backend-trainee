from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Warehouse metal coil app"
)

# routers = (
#     pages_router,
#     chat_router,
# )

# [app.include_router(router) for router in routers]
