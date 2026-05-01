import gzip
import os

import numpy as np
import orjson
from socketify import App

from vectorizer import vectorize

app = App()

_THRESHOLD = 0.6
_ready = False
_vectors = np.empty((0, 14), dtype=np.float32)
_ref_norms = np.empty(0, dtype=np.float32)
_labels = np.empty(0, dtype=bool)


@app.on_start
async def startup():
    global _ready, _vectors, _ref_norms, _labels

    with gzip.open("resources/references.json.gz", "rb") as f:
        refs = orjson.loads(f.read())

    _vectors = np.array([r["vector"] for r in refs], dtype=np.float32)
    _ref_norms = np.sum(_vectors**2, axis=1)
    _labels = np.array([r["label"] == "fraud" for r in refs], dtype=bool)
    _ready = True


@app.on_shutdown
async def shutdown():
    pass


def ready(res, req):
    if _ready:
        res.write_status(200).end("OK")
    else:
        res.write_status(503).end("NOT_READY")


async def fraud_score(res, req):
    data = await res.get_data()
    payload = orjson.loads(data.getvalue())
    vec = vectorize(payload)

    query_norm = np.dot(vec, vec)
    distances = _ref_norms + query_norm - 2.0 * _vectors.dot(vec)

    nearest_idx = np.argpartition(distances, 5)[:5]
    fraud_count = np.count_nonzero(_labels[nearest_idx])
    fraud_score = fraud_count / 5.0

    res.write_header(b"Content-Type", b"application/json")
    res.end(orjson.dumps({"approved": bool(fraud_score < _THRESHOLD), "fraud_score": float(fraud_score)}))


app.get("/ready", ready)
app.post("/fraud-score", fraud_score)

if __name__ == "__main__":
    app.listen(int(os.getenv("PORT", "9999")))
    app.run()
