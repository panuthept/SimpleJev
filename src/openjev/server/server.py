from fastapi import FastAPI
from openjev.backends import get_backend


def create_app(config: dict) -> FastAPI:
    app = FastAPI()
    print(f"Creating FastAPI app with configuration: {config}")
    app.state.timeout = config.get("timeout")
    app.state.backend = get_backend(
        config["backend"],
        backend_base_url=config.get("backend_base_url"),
        backend_api_key=config.get("backend_api_key"),
    )

    # ------------------------------------------------------------------
    # Inference routers (hooks fire on these)
    # Registered under both "" and "/v1" so the proxy works regardless
    # of whether the client sets base_url="http://host:port" or
    # base_url="http://host:port/v1".
    # ------------------------------------------------------------------
    from .routes.systemone import router as systemone_router
    from .routes.decisions import router as decisions_router
    from .routes.decision import router as decision_router

    app.include_router(systemone_router)
    app.include_router(decisions_router)
    app.include_router(decision_router)

    app.include_router(systemone_router, prefix="/v1")
    app.include_router(decisions_router, prefix="/v1")
    app.include_router(decision_router, prefix="/alpha")

    return app