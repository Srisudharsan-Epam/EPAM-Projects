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

The user-facing output contains only:

```text
decision
reason
