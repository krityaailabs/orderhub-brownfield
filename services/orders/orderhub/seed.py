"""Load the synthetic seed data into a database.

Usage: python -m orderhub.seed   (uses ORDERHUB_DATABASE_URL)
"""

import json
from pathlib import Path

from .config import load_settings
from .db import Base, make_engine, make_session_factory
from .models import Customer, DiscountCode, Product

DATA = Path(__file__).resolve().parents[3] / "data" / "seed.json"


def load(session, data_path: Path = DATA) -> dict:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    for c in data["customers"]:
        session.add(Customer(**c))
    for p in data["products"]:
        session.add(Product(**p))
    for d in data["discount_codes"]:
        session.add(DiscountCode(**d))
    session.commit()
    return {k: len(v) for k, v in data.items()}


def main() -> None:
    settings = load_settings()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    with make_session_factory(engine)() as session:
        counts = load(session)
    print("seeded:", counts)


if __name__ == "__main__":
    main()
