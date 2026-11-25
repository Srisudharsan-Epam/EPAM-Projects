# EPAM-Projects
# Portfolio Trade Order Compliance & Execution Checker
A Python-based rule engine that evaluates proposed portfolio trades before execution. Each trade is checked against portfolio cash, holdings, restricted securities, and position-concentration limits. The checker returns a clear compliance decision and reason for every trade.

Overview
Portfolio rebalancing systems may generate buy and sell orders automatically, but proposed trades should be validated before they are submitted for execution.

The Portfolio Trade Order Compliance & Execution Checker processes proposed trades and evaluates them in a defined sequence:

Invalid trade data is rejected.
Restricted securities are rejected.
Sell orders are checked against current holdings.
Buy orders are checked against available cash.
Buy orders exceeding the maximum position concentration require manual approval.
Trades passing all checks are approved.
The application returns only:

decision
reason
This makes the result suitable for downstream processing, review screens, or integration with an order-management workflow.

Decisions
Each trade receives one of the following decisions:

Decision	Meaning
Approved	The trade passed all applicable compliance and execution-readiness checks.
Rejected	The trade failed a mandatory validation or compliance rule.
Needs Manual Sign-off	The trade exceeded the permitted position concentration and requires approval.
Compliance Rules
Rules are evaluated in the exact order below. The checker stops evaluating a trade as soon as a rule produces a final rejection or manual-review decision.

Step 1: Validate trade data
The following conditions must be satisfied:

quantity must be a positive number.
price must be a positive number.
action must be either Buy or Sell.
If any condition fails:

Decision: Rejected
Reason: Invalid trade data.
Step 2: Restricted security check
If security_id appears in the portfolio's restricted_securities list:

Decision: Rejected
Reason: Security is restricted for this portfolio.
Step 3: Sell check
For a Sell order, the portfolio must hold at least the requested quantity of the security.

Holding exactly the requested quantity is sufficient.

If the current holding is less than the requested sell quantity:

Decision: Rejected
Reason: Insufficient holdings to sell.
Step 4: Buy affordability check
For a Buy order, the total cost is calculated as:

quantity × price
The order is affordable when its cost is less than or equal to the portfolio's cash_balance.

If the cost exceeds available cash:

Decision: Rejected
Reason: Insufficient cash for this buy order.
Step 5: Buy position-concentration check
This check applies only to Buy orders.

The checker calculates:

post_trade_cash = cash_balance - (quantity × price)
post_trade_quantity =
    existing quantity of this security + quantity
post_trade_value_of_this_security =
    post_trade_quantity × price
The value of all other holdings is calculated using each holding's own stored market price:

value_of_other_holdings =
    sum(quantity × market_price for every other security)
The total portfolio value after the trade is:

total_portfolio_value_after =
    post_trade_cash
    + post_trade_value_of_this_security
    + value_of_other_holdings
The resulting position percentage is:

position_pct =
    post_trade_value_of_this_security
    / total_portfolio_value_after
If position_pct strictly exceeds max_position_pct:

Decision: Needs Manual Sign-off
Reason: Exceeds maximum position concentration — requires approval.
A position exactly equal to the maximum permitted percentage passes this check.

Step 6: Approval
If the trade passes all applicable checks:

Decision: Approved
Reason: Approved.
Input Data
Proposed trades
The proposed trade input is provided as a CSV file, for example:

portfolio_id,security_id,action,quantity,price,security_type
POR001,AAPL,Buy,20,150,Equity
POR001,TCS,Sell,50,100,Equity
POR002,GOOGL,Buy,5,2000,Equity
Each trade contains:

Field	Description
portfolio_id	Identifier of the portfolio receiving the trade
security_id	Identifier of the security
action	Buy or Sell
quantity	Number of units to buy or sell
price	Proposed trade price
security_type	Security classification such as Equity, Bond, or ETF
The security_type field is accepted as part of the trade input. The rules described by this project do not apply different logic based on security type.

Portfolio reference data
Each portfolio_id must have corresponding reference data containing:

{
    "cash_balance": 10000,
    "restricted_securities": ["RESTRICTED_SECURITY"],
    "max_position_pct": 0.40,
    "current_holdings": [
        ("AAPL", 50, 150.00),
        ("TCS", 100, 100.00)
    ]
}
The reference data includes:

Field	Description
cash_balance	Cash available before the proposed trade
restricted_securities	Securities that cannot be traded by the portfolio
max_position_pct	Maximum permitted portfolio concentration for a single security
current_holdings	Existing holdings represented as (security_id, quantity, market_price)
Each holding's own market_price is used when valuing the other holdings during the concentration calculation.

The provided trade CSV contains proposed trades. Portfolio reference data is maintained separately because it is portfolio-level information rather than trade-level information.

Output
The user-facing output contains only two columns:

decision
reason
Example:

| decision              | reason                                      |
|-----------------------|--------------------------------------------|
| Approved              | Approved.                                  |
| Rejected              | Insufficient cash for this buy order.      |
| Needs Manual Sign-off | Exceeds maximum position concentration — requires approval. |
The output remains in the same order as the input trades.

Project Structure
A typical project structure is:

portfolio-trade-compliance-checker/
├── compliance_checker.py
├── trades_test.csv
├── compliance_results.xlsx
├── README.md
└── .venv/
Files
File	Description
compliance_checker.py	Main Python implementation and compliance rule engine
trades_test.csv	Proposed trade test data
compliance_results.xlsx	Optional Excel output generated from the test run
README.md	Project documentation
.venv/	Local Python virtual environment
The portfolio reference data may be defined in compliance_checker.py for demonstration purposes. In a production application, it should normally be retrieved from a portfolio-management system, database, or reference-data service.

Requirements
Python 3
pandas for CSV reading and tabular processing
openpyxl if Excel workbook generation is enabled
The compliance decision logic itself does not require an external database or web service.
