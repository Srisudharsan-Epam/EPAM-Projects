from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class Trade:
    portfolio_id: str
    security_id: str
    action: str
    quantity: int | float | Decimal
    price: int | float | Decimal
    security_type: str


@dataclass(frozen=True)
class Holding:
    security_id: str
    quantity: int | float | Decimal
    market_price: int | float | Decimal


@dataclass(frozen=True)
class Portfolio:
    cash_balance: int | float | Decimal
    restricted_securities: frozenset[str]
    max_position_pct: int | float | Decimal
    current_holdings: tuple[Holding, ...]


def _decimal(value: int | float | Decimal) -> Decimal:
    """Convert supported numeric input to Decimal without float arithmetic."""
    if isinstance(value, bool):
        raise InvalidOperation
    if isinstance(value, float) and not isfinite(value):
        raise InvalidOperation
    result = Decimal(str(value))
    if not result.is_finite():
        raise InvalidOperation
    return result


def check_trade(
    trade: Trade,
    portfolios: Mapping[str, Portfolio],
) -> dict[str, str]:
    def result(decision: str, reason: str) -> dict[str, str]:
        return {"decision": decision, "reason": reason}

    try:
        quantity = _decimal(trade.quantity)
        price = _decimal(trade.price)
        if quantity <= 0 or price <= 0 or trade.action not in {"Buy", "Sell"}:
            return result("Rejected", "Invalid trade data.")
    except (InvalidOperation, ValueError, TypeError):
        return result("Rejected", "Invalid trade data.")

    portfolio = portfolios.get(trade.portfolio_id)
    if portfolio is None:
        return result("Rejected", "Portfolio not found.")

    if trade.security_id in portfolio.restricted_securities:
        return result(
            "Rejected",
            "Security is restricted for this portfolio.",
        )

    matching_holdings = [
        holding
        for holding in portfolio.current_holdings
        if holding.security_id == trade.security_id
    ]

    if trade.action == "Sell":
        held_quantity = sum(
            (_decimal(holding.quantity) for holding in matching_holdings),
            Decimal("0"),
        )
        if held_quantity < quantity:
            return result("Rejected", "Insufficient holdings to sell.")
        return result("Approved", "Trade passed compliance checks.")

    cost = quantity * price
    cash_balance = _decimal(portfolio.cash_balance)
    if cost > cash_balance:
        return result("Rejected", "Insufficient cash for this buy order.")

    existing_quantity = sum(
        (_decimal(holding.quantity) for holding in matching_holdings),
        Decimal("0"),
    )
    other_holdings_value = sum(
        (
            _decimal(holding.quantity) * _decimal(holding.market_price)
            for holding in portfolio.current_holdings
            if holding.security_id != trade.security_id
        ),
        Decimal("0"),
    )

    post_trade_cash = cash_balance - cost
    post_trade_quantity = existing_quantity + quantity
    post_trade_security_value = post_trade_quantity * price
    total_value_after = (
        post_trade_cash + post_trade_security_value + other_holdings_value
    )
    position_pct = post_trade_security_value / total_value_after

    if position_pct > _decimal(portfolio.max_position_pct):
        return result(
            "Needs Manual Sign-off",
            "Exceeds maximum position concentration — requires approval.",
        )

    return result("Approved", "Trade passed compliance checks.")
