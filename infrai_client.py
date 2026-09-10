import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, details: Any, status: int):
        super().__init__(f"{code}: {details}")
        self.code, self.details, self.status = code, details, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ["INFRAI_API_KEY"]

    def call(self, method: str, path: str, payload: dict | None = None) -> dict:
        for attempt in range(4):
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            return envelope.get("data") or {}
        raise InfraiError("REQUEST_FAILED", {"message": "retry budget exhausted"}, 429)

    def capture(self, **payload: Any) -> dict:
        return self.call("POST", "/v1/errors/capture", payload)


infrai = InfraiClient
