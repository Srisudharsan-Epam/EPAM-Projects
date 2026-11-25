# EPAM-Projects
# Portfolio Trade Order Compliance & Execution Checker

A Python-based rule engine that evaluates proposed portfolio trades before execution. Each trade is checked against portfolio cash, current holdings, restricted securities, and position-concentration limits.

The application returns a clear decision and reason for every trade.

## Overview

Portfolio rebalancing systems may generate buy and sell orders automatically, but proposed trades should be validated before submission for execution.

The checker processes each proposed trade and evaluates it in a defined order:

1. Validate the trade data.
2. Check whether the security is restricted.
3. Verify sufficient holdings for sell orders.
4. Verify sufficient cash for buy orders.
5. Check position concentration for buy orders.
6. Approve the trade if all applicable checks pass.

portfolio_id	security_id	action	quantity	price	security_type
POR001	AAPL	Buy	20	150	Equity
POR001	AAPL	Buy	60	150	Equity
POR001	TCS	Sell	50	310	Equity
POR001	TCS	Sell	60	310	Equity
POR001	XYZCORP	Buy	10	50	Equity
POR001	AAPL	Buy	400	150	Equity
POR001	AAPL	Buy	-10	150	Equity
POR001	INFY	Buy	10	1500	Equity
POR002	GOOGL	Buy	5	2000	Equity
POR003	BADCO	Buy	10	100	Equity
POR003	TCS	Buy	5	300	Equity
POR003	INFY	Buy	50	1500	Equity
POR003	RELIANCE	Sell	30	2400	Equity
POR003	RELIANCE	Sell	31	2400	Equity
POR004	GOOGL	Buy	10	2000	Equity
POR004	AAPL	Buy	300	150	Equity
POR005	PENNY1	Buy	5	10	Equity
POR005	AAPL	Buy	33	150	Equity
POR005	AAPL	Buy	34	150	Equity
POR005	TCS	Buy	20	250	Equity
<img width="529" height="484" alt="image" src="https://github.com/user-attachments/assets/fe806e1d-5b91-45a7-8da6-d5d8c743735d" />

The user-facing output contains only:

```text
decision
reason
