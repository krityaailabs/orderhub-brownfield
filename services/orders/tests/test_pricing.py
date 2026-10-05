import pytest

from orderhub import pricing


def test_line_total_multiplies_price_by_quantity():
    assert pricing.line_total(249, 4) == 996


def test_line_total_rejects_zero_quantity():
    with pytest.raises(ValueError):
        pricing.line_total(249, 0)


def test_subtotal_sums_lines():
    assert pricing.subtotal([(1000, 2), (250, 3)]) == 2750


def test_discount_on_round_amount():
    assert pricing.apply_percentage_discount(2000, 10) == 1800


def test_zero_percent_discount_keeps_amount():
    assert pricing.apply_percentage_discount(1999, 0) == 1999


def test_discount_above_limit_is_rejected():
    with pytest.raises(ValueError):
        pricing.apply_percentage_discount(1000, 95)


@pytest.mark.parametrize("minor,expected", [(1999, "19.99 USD"), (5, "0.05 USD"), (-250, "-2.50 USD")])
def test_format_money(minor, expected):
    assert pricing.format_money(minor, "USD") == expected
