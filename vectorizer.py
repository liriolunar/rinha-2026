from datetime import datetime

import numpy as np
from numpy.typing import NDArray

SENTINEL_NO_LAST_TX: float = -1.0

_MCC_RISK: dict[str, float] = {
    "5411": 0.15,
    "5812": 0.30,
    "5912": 0.20,
    "5944": 0.45,
    "7801": 0.80,
    "7802": 0.75,
    "7995": 0.85,
    "4511": 0.35,
    "5311": 0.25,
    "5999": 0.50,
}

_INV_MAX_AMOUNT = np.float32(1.0 / 10000)
_INV_MAX_INSTALLMENTS = np.float32(1.0 / 12)
_INV_AMOUNT_VS_AVG_RATIO = np.float32(1.0 / 10)
_INV_MAX_KM = np.float32(1.0 / 1000)
_INV_MAX_TX_COUNT_24H = np.float32(1.0 / 20)
_INV_MAX_MERCHANT_AVG_AMOUNT = np.float32(1.0 / 10000)
_INV_HOURS_IN_DAY = np.float32(1.0 / 23)
_INV_DAYS_IN_WEEK = np.float32(1.0 / 6)
_INV_SECONDS = np.float32(1.0 / 86400.0)


def vectorize(body: dict) -> NDArray[np.float32]:
    """Turn a raw API payload into a 14-dim float32 vector."""
    tx = body["transaction"]
    customer = body["customer"]
    merchant = body["merchant"]
    terminal = body["terminal"]
    last_tx = body.get("last_transaction")

    amount = tx["amount"]
    installments = tx["installments"]
    avg_amount = customer["avg_amount"]
    requested_at = tx["requested_at"]

    km_from_home = terminal["km_from_home"]
    tx_count_24h = customer["tx_count_24h"]
    is_online = 1.0 if terminal["is_online"] else 0.0
    card_present = 1.0 if terminal["card_present"] else 0.0

    known_merchants = customer["known_merchants"]
    unknown_merchant = 0.0 if merchant["id"] in known_merchants else 1.0

    mcc = merchant["mcc"]
    mcc_risk_val = _MCC_RISK.get(mcc, 0.5)

    merchant_avg_amount = merchant["avg_amount"]

    vec = np.empty(14, dtype=np.float32)
    vec[0] = np.clip(amount * _INV_MAX_AMOUNT, 0.0, 1.0)
    vec[1] = np.clip(installments * _INV_MAX_INSTALLMENTS, 0.0, 1.0)
    vec[2] = np.clip((amount / avg_amount) * _INV_AMOUNT_VS_AVG_RATIO, 0.0, 1.0)

    dt = datetime.fromisoformat(requested_at)
    vec[3] = dt.hour * _INV_HOURS_IN_DAY
    vec[4] = dt.weekday() * _INV_DAYS_IN_WEEK

    if last_tx is None:
        vec[5] = SENTINEL_NO_LAST_TX
        vec[6] = SENTINEL_NO_LAST_TX
    else:
        t1 = datetime.fromisoformat(requested_at)
        t2 = datetime.fromisoformat(last_tx["timestamp"])
        seconds_since_last = (t1 - t2).total_seconds()
        km_from_last = last_tx["km_from_current"]
        vec[5] = np.clip(seconds_since_last * _INV_SECONDS, 0.0, 1.0)
        vec[6] = np.clip(km_from_last * _INV_MAX_KM, 0.0, 1.0)

    vec[7] = np.clip(km_from_home * _INV_MAX_KM, 0.0, 1.0)
    vec[8] = np.clip(tx_count_24h * _INV_MAX_TX_COUNT_24H, 0.0, 1.0)
    vec[9] = is_online
    vec[10] = card_present
    vec[11] = unknown_merchant
    vec[12] = mcc_risk_val
    vec[13] = np.clip(merchant_avg_amount * _INV_MAX_MERCHANT_AVG_AMOUNT, 0.0, 1.0)

    return vec
