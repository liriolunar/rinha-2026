import os

import orjson
from socketify import App

app = App()
app.json_serializer(orjson)


@app.on_start
async def startup():
    # TODO: load references, mcc_risk and normalization data on startup
    pass


@app.on_shutdown
async def shutdown():
    pass


def ready(res, req):
    # TODO: return 200 when references are loaded, 503 otherwise
    res.write_status(200).end()


async def fraud_score(res, req):
    # TODO:
    # 1. Parse request body
    # 2. Vectorize payload into 14-dim float32 vector
    # 3. Find k=5 nearest neighbors in reference dataset
    # 4. Calculate fraud_score = fraud_count / 5
    # 5. Return {approved: fraud_score < 0.6, fraud_score: score}
    body = await res.get_json()
    res.end({"approved": True, "fraud_score": 0.0})


app.get("/ready", ready)
app.post("/fraud-score", fraud_score)

if __name__ == "__main__":
    app.listen(int(os.getenv("PORT", "9999")))
    app.run()
