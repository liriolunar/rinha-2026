import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: load references, mcc_risk and normalization data on startup
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ready")
async def ready() -> Response:
    # TODO: return 200 when references are loaded, 503 otherwise
    return Response(status_code=200)


@app.post("/fraud-score")
async def fraud_score(request: Request) -> ORJSONResponse:
    # TODO:
    # 1. Parse request body
    # 2. Vectorize payload into 14-dim float32 vector
    # 3. Find k=5 nearest neighbors in reference dataset
    # 4. Calculate fraud_score = fraud_count / 5
    # 5. Return {approved: fraud_score < 0.6, fraud_score: score}
    return ORJSONResponse({"approved": True, "fraud_score": 0.0})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "9999"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        access_log=False,
    )
