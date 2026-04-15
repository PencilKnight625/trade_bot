"""
client.py
---------
Handles ALL communication with the Binance Futures Testnet API.

How Binance auth works:
  1. Every request needs your API key in a header.
  2. Account requests (like placing orders) also need a HMAC-SHA256
     signature computed from the params + your secret key.
"""

import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 10


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json",
        })
        logger.debug("BinanceClient initialised. Base URL: %s", BASE_URL)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamp + HMAC-SHA256 signature to params."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, signed: bool = True) -> Dict:
        if params is None:
            params = {}
        if signed:
            params = self._sign(params)

        url = BASE_URL + endpoint
        logger.debug("→ %s %s | params: %s", method, url, params)

        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            elif method == "POST":
                response = self.session.post(url, params=params, timeout=REQUEST_TIMEOUT)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=REQUEST_TIMEOUT)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.debug("← %s | status: %s | body: %s", url, response.status_code, response.text[:500])
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Request timed out after %s seconds: %s", REQUEST_TIMEOUT, url)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error reaching %s: %s", url, exc)
            raise
        except requests.exceptions.HTTPError as exc:
            try:
                error_body = exc.response.json()
                logger.error("Binance API error %s: code=%s msg=%s",
                             exc.response.status_code,
                             error_body.get("code"),
                             error_body.get("msg"))
            except Exception:
                logger.error("HTTP error: %s", exc)
            raise

    def place_order(self, symbol: str, side: str, order_type: str,
                    quantity: float, price: Optional[float] = None,
                    time_in_force: str = "GTC") -> Dict:
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        logger.info("Placing %s %s order | symbol=%s qty=%s price=%s",
                    side, order_type, symbol, quantity, price or "MARKET")
        return self._request("POST", "/fapi/v1/order", params=params)

    def get_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("GET", "/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        return self._request("DELETE", "/fapi/v1/order", {"symbol": symbol, "orderId": order_id})