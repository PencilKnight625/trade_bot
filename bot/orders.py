"""
orders.py
---------
Order placement logic + output formatting.

  client.py  → HOW to talk to Binance (HTTP)
  orders.py  → WHAT to send and HOW to display results
  cli.py     → WHAT the user typed
"""

import logging
from typing import Optional
from .client import BinanceClient

logger = logging.getLogger("trading_bot.orders")


def print_order_summary(symbol, side, order_type, quantity, price):
    print("\n" + "=" * 50)
    print("       📋  ORDER REQUEST SUMMARY")
    print("=" * 50)
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Order Type : {order_type}")
    print(f"  Quantity   : {quantity}")
    print(f"  Price      : {price if price else '(market price)'}")
    print("=" * 50)


def print_order_response(response: dict):
    print("\n" + "=" * 50)
    print("       ✅  ORDER RESPONSE")
    print("=" * 50)
    print(f"  Order ID     : {response.get('orderId', 'N/A')}")
    print(f"  Symbol       : {response.get('symbol', 'N/A')}")
    print(f"  Status       : {response.get('status', 'N/A')}")
    print(f"  Side         : {response.get('side', 'N/A')}")
    print(f"  Type         : {response.get('type', 'N/A')}")
    print(f"  Orig Qty     : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
    avg_price = response.get("avgPrice", "0")
    print(f"  Avg Price    : {avg_price if float(avg_price) > 0 else '(not filled yet)'}")
    print(f"  Time in Force: {response.get('timeInForce', 'N/A')}")
    print("=" * 50)


def place_order(client: BinanceClient, symbol: str, side: str,
                order_type: str, quantity: float, price: Optional[float] = None) -> dict:
    print_order_summary(symbol, side, order_type, quantity, price)
    logger.info("Submitting order: symbol=%s side=%s type=%s qty=%s price=%s",
                symbol, side, order_type, quantity, price)
    try:
        response = client.place_order(
            symbol=symbol, side=side, order_type=order_type,
            quantity=quantity, price=price,
        )
        logger.debug("Raw order response: %s", response)
        print_order_response(response)
        print("\n  🎉  Order placed successfully!\n")
        logger.info("Order placed successfully: orderId=%s status=%s",
                    response.get("orderId"), response.get("status"))
        return response
    except Exception as exc:
        print(f"\n  ❌  Order failed: {exc}\n")
        logger.error("Order placement failed: %s", exc, exc_info=True)
        raise