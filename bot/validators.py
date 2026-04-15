"""
validators.py
-------------
All input validation lives here.
Each function raises ValueError with a clear message if input is bad,
or returns the cleaned value if everything is fine.
"""

from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty. Example: BTCUSDT")
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}'. Use only letters and numbers, e.g. BTCUSDT.")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}")
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number, e.g. 0.01")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. You entered: {qty}")
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    order_type = order_type.upper()

    if order_type == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders. Use --price <value>.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid price '{price}'. Must be a positive number, e.g. 30000.5")
        if p <= 0:
            raise ValueError(f"Price must be greater than 0. You entered: {p}")
        return p

    if price is not None:
        raise ValueError("Price should NOT be provided for MARKET orders. Remove --price from your command.")
    return None


def validate_all(symbol, side, order_type, quantity, price=None) -> dict:
    """Validate all fields at once and return a clean dict."""
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, order_type),
    }