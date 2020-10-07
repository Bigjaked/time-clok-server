from fastapi import FastAPI
from web_server.extensions import token_manager, password_hasher, login_manager
from web_server.database import DB
from web_server.routes import auth, clok, job, user


def create_app(config) -> FastAPI:
    cfg = config()
    DB.init_app(cfg)
    token_manager.init_app(cfg)
    password_hasher.init_app(cfg)

    tags_metadata = [
        {"name": "Users", "description": "API endpoints that manage user",},
        {
            "name": "Clock",
            "description": "API endpoints that manage and return clock information",
        },
        {
            "name": "Jobs",
            "description": "API endpoints that manage and return Job information",
        },
        {
            "name": "Auth",
            "description": "API endpoints that manage authentication and tokens",
        },
    ]

    app = FastAPI(
        openapi_tags=tags_metadata,
        title="Time Clok Server",
        description="This is an api server for the python timeclok app",
        version="0.2.0",
    )

    app.include_router(auth.api, prefix="/auth", tags=["Auth"])
    app.include_router(clok.api, prefix="/api/v1/clok", tags=["Clock"])
    app.include_router(job.api, prefix="/api/v1/job", tags=["Jobs"])
    app.include_router(user.api, prefix="/api/v1/user", tags=["Users"])

    return app
