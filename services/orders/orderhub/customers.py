"""Customer operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .errors import Conflict, NotFound, ValidationFailed
from .models import Customer


def create_customer(session: Session, email: str, name: str, country: str) -> Customer:
    email = email.strip()
    if "@" not in email:
        raise ValidationFailed("email is not valid")
    if len(country) != 2:
        raise ValidationFailed("country must be an ISO 3166-1 alpha-2 code")
    existing = session.scalar(select(Customer).where(func.lower(Customer.email) == email.lower()))
    if existing is not None:
        raise Conflict("a customer with this email already exists")
    customer = Customer(email=email, name=name.strip(), country=country.upper())
    session.add(customer)
    session.commit()
    return customer


def get_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFound(f"customer {customer_id} not found")
    return customer


def update_customer(session: Session, customer_id: int, name: str | None = None,
                    email: str | None = None) -> Customer:
    customer = get_customer(session, customer_id)
    if name is not None:
        customer.name = name.strip()
    if email is not None:
        customer.email = email.strip()
    session.commit()
    return customer
