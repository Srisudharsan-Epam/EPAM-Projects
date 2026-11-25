import pandas as pd
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
PORTFOLIO_REFERENCE_DATA: Dict[str, dict] = {
    "POR001": {
        "cash_balance": 10000.0,
        "restricted_securities": ["XYZCORP"],
        "max_position_pct": 0.40,
        "current_holdings": [
            ("AAPL", 50, 150.0),
            ("TCS", 50, 310.0),
            ("INFY", 0, 1500.0),
        ],
    },
    "POR002": {
        "cash_balance": 10000.0,   
        "restricted_securities": ["TCS"],
        "max_position_pct": 1.00,  
        "current_holdings": [],
    },
    "POR003": {
        "cash_balance": 100000.0,
        "restricted_securities": ["BADCO"],
        "max_position_pct": 0.50,
        "current_holdings": [
            ("TCS", 10, 300.0),
            ("INFY", 20, 1500.0),
            ("RELIANCE", 30, 2400.0),   
        ],
    },
    "POR004": {
        "cash_balance": 50000.0,
        "restricted_securities": [],
        "max_position_pct": 0.40,
        "current_holdings": [
            ("GOOGL", 0, 2000.0),
            ("AAPL", 0, 150.0),
        ],
    },
    "POR005": {
        "cash_balance": 20000.0,
        "restricted_securities": [],
        "max_position_pct": 0.40,
        "current_holdings": [
            ("AAPL", 0, 150.0),
            ("TCS", 0, 250.0),
            ("PENNY1", 0, 10.0),
        ],
    },
}

@dataclass
class Decision:
    decision: str
    reason: str

csv_path = "trades_test.csv"
APPROVED = "Approved"
REJECTED = "Rejected"
MANUAL = "Needs Manual Sign-off"

def evaluate_trade(trade: dict, portfolio: Optional[dict]) -> Decision:
    
    quantity = trade.get("quantity")
    price = trade.get("price")
    action = trade.get("action")
    security_id = trade.get("security_id")

    quantity_ok = isinstance(quantity, (int, float)) and not isinstance(quantity, bool) and quantity > 0
    price_ok = isinstance(price, (int, float)) and not isinstance(price, bool) and price > 0
    action_ok = action in ("Buy", "Sell")
    if not (quantity_ok and price_ok and action_ok):
        return Decision(REJECTED, "Invalid trade data.")

    if portfolio is None:
        return Decision(REJECTED, "Invalid trade data.")

    if security_id in portfolio.get("restricted_securities", []):
        return Decision(REJECTED, "Security is restricted for this portfolio.")

    holdings: List[Tuple[str, float, float]] = portfolio.get("current_holdings", [])
    held_qty = sum(q for (sid, q, _) in holdings if sid == security_id)

    if action == "Sell":
        if held_qty < quantity:
            return Decision(REJECTED, "Insufficient holdings to sell.")
        return Decision(APPROVED, "Trade passes all compliance checks.")

    trade_cost = quantity * price
    cash_balance = portfolio.get("cash_balance", 0.0)

    if trade_cost > cash_balance:
        return Decision(REJECTED, "Insufficient cash for this buy order.")

    post_trade_cash = cash_balance - trade_cost
    post_trade_quantity = held_qty + quantity
    post_trade_value_of_this_security = post_trade_quantity * price
    value_of_other_holdings = sum(
        q * mp for (sid, q, mp) in holdings if sid != security_id
    )
    total_portfolio_value_after = (
        post_trade_cash + post_trade_value_of_this_security + value_of_other_holdings
    )

    if total_portfolio_value_after <= 0:
        position_pct = float("inf")
    else:
        position_pct = post_trade_value_of_this_security / total_portfolio_value_after

    max_position_pct = portfolio.get("max_position_pct", 1.0)
    if position_pct > max_position_pct:
        return Decision(MANUAL, "Exceeds maximum position concentration — requires approval.")

    return Decision(APPROVED, "Trade passes all compliance checks.")


def run_detailed(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    results = []
    for _, row in df.iterrows():
        trade = row.to_dict()
        portfolio = PORTFOLIO_REFERENCE_DATA.get(trade["portfolio_id"])
        outcome = evaluate_trade(trade, portfolio)
        results.append({**trade, "decision": outcome.decision, "reason": outcome.reason})
    return pd.DataFrame(results)

def run(csv_path: str) -> pd.DataFrame:
   
    detailed = run_detailed(csv_path)
    return detailed[["decision", "reason"]]

if __name__ == "__main__":
    out_df = run("trades_test.csv")
    with pd.option_context("display.max_rows", None, "display.width", 160):
        print(out_df.to_string(index=False))