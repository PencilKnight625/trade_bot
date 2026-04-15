import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

from bot.logging_config import setup_logging
from bot.validators import validate_all
from bot.client import BinanceClient
from bot.orders import place_order


def build_parser():
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            "Binance Futures Testnet Trading Bot\n"
            "Places MARKET or LIMIT orders on USDT-M Futures testnet.\n\n"
            "Set API keys in a .env file:\n"
            "  BINANCE_API_KEY=your_key\n"
            "  BINANCE_API_SECRET=your_secret"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 100000\n"
        ),
    )
    parser.add_argument("--symbol",    required=True, help="Trading pair e.g. BTCUSDT")
    parser.add_argument("--side",      required=True, choices=["BUY","SELL","buy","sell"], help="BUY or SELL")
    parser.add_argument("--type",      dest="order_type", required=True,
                        choices=["MARKET","LIMIT","market","limit"], help="MARKET or LIMIT")
    parser.add_argument("--quantity",  required=True, help="Amount to trade e.g. 0.01")
    parser.add_argument("--price",     default=None,  help="Limit price (LIMIT orders only)")
    parser.add_argument("--api-key",   default=None,  help="Binance API key (overrides .env)")
    parser.add_argument("--api-secret",default=None,  help="Binance API secret (overrides .env)")
    parser.add_argument("--log-file",  default="trading_bot.log", help="Log file path")
    return parser


def get_api_credentials(args):
    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")

    if not api_key:
        print("API key not found!\n"
              "   Add to .env:  BINANCE_API_KEY=your_key\n"
              "   Or pass:      --api-key your_key\n")
        sys.exit(1)
    if not api_secret:
        print("API secret not found!\n"
              "   Add to .env:  BINANCE_API_SECRET=your_secret\n"
              "   Or pass:      --api-secret your_secret\n")
        sys.exit(1)

    return api_key, api_secret


def main():
    parser = build_parser()
    args   = parser.parse_args()

    logger = setup_logging(log_file=args.log_file)
    logger.info("Trading bot started")

    api_key, api_secret = get_api_credentials(args)

    try:
        params = validate_all(
            symbol=args.symbol, side=args.side,
            order_type=args.order_type, quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        print(f"Input error: {exc}\n")
        logger.error("Validation failed: %s", exc)
        sys.exit(1)

    logger.info("Validation passed: %s", params)

    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        place_order(client=client, **params)
    except Exception as exc:
        logger.error("Bot exiting due to error: %s", exc)
        sys.exit(1)

    logger.info("Trading bot finished successfully")


if __name__ == "__main__":
    main()