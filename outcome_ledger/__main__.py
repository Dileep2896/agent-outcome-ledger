import argparse
import json

from fastapi.encoders import jsonable_encoder

from .seed import make_seed
from .service import build_ledger


def main():
    parser = argparse.ArgumentParser(description="Outcome Ledger weekly report")
    parser.add_argument("command", choices=["report"])
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()
    summary = build_ledger(make_seed()).summary()
    if args.json:
        print(json.dumps(jsonable_encoder(summary), indent=2))
    else:
        print(f"Outcome Ledger · week {summary['week']}")
        print(f"Spend: ${summary['totals']['spend']:.2f}")
        print(f"Attributed value: ${summary['totals']['attributed_value']:.2f}")
        print(f"Coverage: {summary['coverage']['naive']:.1%} → {summary['coverage']['engine']:.1%}")


if __name__ == "__main__":
    main()
