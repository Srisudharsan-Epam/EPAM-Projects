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

# Test Input List
<img width="529" height="484" alt="image" src="https://github.com/user-attachments/assets/fe806e1d-5b91-45a7-8da6-d5d8c743735d" />

# Output contains only:

```text
decision
reason
