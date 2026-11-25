# EPAM-Projects

# Portfolio Trade Order Compliance & Execution Checker

A Python-based compliance and execution-readiness checker for proposed portfolio trades.

The application evaluates each proposed trade against portfolio-level reference data supplied by the user in a JSON file. Portfolio reference data is **not hardcoded** in the application.

For every trade, the application returns only:

- `decision`
- `reason`

The checker is designed to identify trades that can be approved automatically, trades that must be rejected, and trades that require manual approval before execution.

---

## Features

- Accepts proposed trades from a CSV file.
- Accepts portfolio reference data from a user-provided JSON file.
- Evaluates trades using six ordered compliance rules.
- Stops processing a trade when an earlier rule produces a final decision.
- Checks cash availability for buy orders.
- Checks current holdings for sell orders.
- Checks restricted securities.
- Checks maximum position concentration.
- Supports exact-boundary behavior.
- Returns only `decision` and `reason`.
- Handles invalid input and malformed reference data with clear error messages.
- Can optionally save results to CSV or Excel format, if output-file support is enabled in the script.

---

## How the Application Works

The application requires two input files:

1. A CSV file containing proposed trades.
2. A JSON file containing reference data for each portfolio.

The workflow is:

```text
Read trades CSV
        |
Read portfolio reference JSON
        |
Validate reference data
        |
Process each trade
        |
Look up the trade's portfolio
        |
Apply compliance rules in order
        |
Return decision and reason
        |
Optionally save results to CSV or XLSX
```

Each trade is evaluated independently using the portfolio state supplied in the reference JSON.

---

## Compliance Decisions

Each trade receives one of the following decisions:

| Decision | Meaning |
|---|---|
| `Approved` | The trade passed all applicable compliance and execution-readiness checks. |
| `Rejected` | The trade failed a mandatory validation or compliance rule. |
| `Needs Manual Sign-off` | The trade exceeded the maximum position concentration and requires manual approval. |

---

## Compliance Rules

The rules are evaluated in the exact order shown below.

The checker stops evaluating a trade when a rule produces a final decision. For example, an invalid trade does not continue to the concentration check.

---

### Step 1: Validate Trade Data

The following conditions must be satisfied:

- `quantity` must be a positive number.
- `price` must be a positive number.
- `action` must be `Buy` or `Sell`.

If any validation fails:

```text
Decision: Rejected
Reason: Invalid trade data.
```

---

### Step 2: Restricted Security Check

The application checks whether the trade's `security_id` appears in the portfolio's `restricted_securities` list.

If the security is restricted:

```text
Decision: Rejected
Reason: Security is restricted for this portfolio.
```

---

### Step 3: Sell Check

This rule applies only to `Sell` orders.

The portfolio must currently hold at least the requested quantity of the security.

The following comparison is used:

```text
current holding quantity >= requested sell quantity
```

Holding exactly the requested quantity is sufficient.

If the portfolio holds less than the requested quantity:

```text
Decision: Rejected
Reason: Insufficient holdings to sell.
```

---

### Step 4: Buy Affordability Check

This rule applies only to `Buy` orders.

The cost of the buy order is calculated as:

```text
buy cost = quantity × price
```

The order is affordable when:

```text
buy cost <= cash_balance
```

A buy order costing exactly the available cash is affordable.

If the order cost exceeds the available cash:

```text
Decision: Rejected
Reason: Insufficient cash for this buy order.
```

---

### Step 5: Buy Position-Concentration Check

This rule applies only to `Buy` orders.

The checker calculates the portfolio's position concentration after the proposed trade.

#### Post-trade cash

```text
post_trade_cash =
    cash_balance - (quantity × price)
```

#### Post-trade quantity of the traded security

```text
post_trade_quantity =
    existing quantity of this security + buy quantity
```

If the security is not currently held, its existing quantity is treated as zero.

#### Post-trade value of the traded security

```text
post_trade_value_of_this_security =
    post_trade_quantity × trade price
```

The trade price is used as the current market price for the traded security.

#### Value of all other holdings

```text
value_of_other_holdings =
    sum(quantity × market_price)
    for every other security in current_holdings
```

Each other holding uses its own stored `market_price`.

#### Total portfolio value after the trade

```text
total_portfolio_value_after =
    post_trade_cash
    + post_trade_value_of_this_security
    + value_of_other_holdings
```

#### Position concentration

```text
position_pct =
    post_trade_value_of_this_security
    / total_portfolio_value_after
```

If the resulting position percentage strictly exceeds `max_position_pct`:

```text
Decision: Needs Manual Sign-off
Reason: Exceeds maximum position concentration — requires approval.
```

A position exactly equal to `max_position_pct` passes the concentration check.

---

### Step 6: Approval

If the trade passes all applicable rules:

```text
Decision: Approved
Reason: Approved.
```

---

## Important Comparison Rules

The checker uses strict comparisons where required:

| Scenario | Result |
|---|---|
| Sell quantity equals current holding | Passes |
| Buy cost equals available cash | Passes |
| Position percentage equals maximum position percentage | Passes |
| Buy cost exceeds available cash | Rejected |
| Sell quantity exceeds current holding | Rejected |
| Position percentage exceeds maximum position percentage | Needs Manual Sign-off |

---

## Input File 1: Proposed Trades CSV

The proposed trades file must be a CSV file with the following columns:

| Column | Required | Description |
|---|---:|---|
| `portfolio_id` | Yes | Identifier of the portfolio receiving the trade |
| `security_id` | Yes | Identifier of the security |
| `action` | Yes | Must be `Buy` or `Sell` |
| `quantity` | Yes | Number of units to buy or sell |
| `price` | Yes | Proposed execution price |
| `security_type` | Yes | Security type, such as `Equity`, `Bond`, or `ETF` |

### Trades CSV Example

<img width="529" height="484" alt="image" src="https://github.com/user-attachments/assets/fe806e1d-5b91-45a7-8da6-d5d8c743735d" />


## Input File 2: Portfolio Reference JSON

Portfolio reference data is supplied by the user through a JSON file.

The JSON file must contain one object for each `portfolio_id`.

Each portfolio object must include:

- `cash_balance`
- `restricted_securities`
- `max_position_pct`
- `current_holdings`

### JSON Schema

```json
{
  "<portfolio_id>": {
    "cash_balance": 0.0,
    "restricted_securities": [
      "<security_id>"
    ],
    "max_position_pct": 0.0,
    "current_holdings": [
      {
        "security_id": "<security_id>",
        "quantity": 0.0,
        "market_price": 0.0
      }
    ]
  }
}
```

### Reference Data Fields

| Field | Type | Description |
|---|---|---|
| `portfolio_id` | JSON object key | Unique portfolio identifier |
| `cash_balance` | Number | Available cash before the trade |
| `restricted_securities` | Array of strings | Securities that cannot be traded |
| `max_position_pct` | Number | Maximum position concentration as a decimal |
| `current_holdings` | Array | Existing portfolio holdings |
| `current_holdings[].security_id` | String | Security identifier |
| `current_holdings[].quantity` | Number | Existing quantity held |
| `current_holdings[].market_price` | Number | Market price used to value the holding |

Position percentages must be supplied as decimals:

```text
0.40 = 40%
0.50 = 50%
0.75 = 75%
```

---

## Complete Portfolio Reference JSON Example

Save the following content as `portfolio_reference.json`:

```json
{
  "POR001": {
    "cash_balance": 10000.0,
    "restricted_securities": [
      "XYZCORP"
    ],
    "max_position_pct": 0.4,
    "current_holdings": [
      {
        "security_id": "AAPL",
        "quantity": 50,
        "market_price": 150.0
      },
      {
        "security_id": "TCS",
        "quantity": 50,
        "market_price": 100.0
      },
      {
        "security_id": "INFY",
        "quantity": 20,
        "market_price": 80.0
      }
    ]
  },
  "POR002": {
    "cash_balance": 10000.0,
    "restricted_securities": [],
    "max_position_pct": 0.5,
    "current_holdings": [
      {
        "security_id": "MSFT",
        "quantity": 20,
        "market_price": 300.0
      },
      {
        "security_id": "AMZN",
        "quantity": 10,
        "market_price": 150.0
      }
    ]
  },
  "POR003": {
    "cash_balance": 15000.0,
    "restricted_securities": [
      "BADCO"
    ],
    "max_position_pct": 0.5,
    "current_holdings": [
      {
        "security_id": "RELIANCE",
        "quantity": 30,
        "market_price": 250.0
      },
      {
        "security_id": "INFY",
        "quantity": 20,
        "market_price": 80.0
      },
      {
        "security_id": "TCS",
        "quantity": 10,
        "market_price": 100.0
      }
    ]
  },
  "POR004": {
    "cash_balance": 50000.0,
    "restricted_securities": [],
    "max_position_pct": 0.4,
    "current_holdings": [
      {
        "security_id": "AAPL",
        "quantity": 100,
        "market_price": 150.0
      },
      {
        "security_id": "GOOGL",
        "quantity": 20,
        "market_price": 2000.0
      }
    ]
  },
  "POR005": {
    "cash_balance": 25000.0,
    "restricted_securities": [],
    "max_position_pct": 0.6,
    "current_holdings": [
      {
        "security_id": "BOND01",
        "quantity": 100,
        "market_price": 100.0
      },
      {
        "security_id": "ETF01",
        "quantity": 50,
        "market_price": 200.0
      }
    ]
  }
}
```

The portfolio reference data is supplied by the user and can be replaced without changing the compliance rules.

---

## Project Structure

```text
portfolio-trade-compliance-checker/
├── compliance_checker.py
├── trades_test.csv
├── compliance_results.csv
├── README.md
└── .venv/
```

### File Descriptions

| File | Description |
|---|---|
| `compliance_checker.py` | Main Python application and compliance rule engine |
| `trades_test.csv` | Proposed trade input file |
| `portfolio_reference.json` | User-supplied portfolio reference data |
| `compliance_results.csv` | Optional CSV output |
| `README.md` | Project documentation |
| `.venv/` | Local Python virtual environment |

The output files are created only when the script is configured to save them or an output path is supplied.

---

## Requirements

- Python 3.9 or later
- `pandas`
- `openpyxl` if Excel output is supported or required

The core decision logic does not require a database, web service, or external API.

---

## Setup in Visual Studio Code

### 1. Clone the Repository

```bash
git clone <repository-url>
cd portfolio-trade-compliance-checker
```

Replace `<repository-url>` with the actual GitHub repository URL.

### 2. Open the Project in VS Code

```bash
code .
```

You can also open the folder directly from Visual Studio Code:

```text
File → Open Folder
```

### 3. Install the Python Extension

In Visual Studio Code:

1. Open the Extensions panel.
2. Search for `Python`.
3. Install the Python extension published by Microsoft.

### 4. Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell prevents script execution, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Alternatively, update the execution policy for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

#### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal should show:

```text
(.venv)
```

### 5. Select the Python Interpreter

In VS Code:

1. Open the Command Palette.
2. Select `Python: Select Interpreter`.
3. Select the interpreter located inside `.venv`.

Typical interpreter paths are:

```text
Windows:     .venv\Scripts\python.exe
macOS/Linux: .venv/bin/python
```

---

## Installation

Activate the virtual environment and install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install pandas openpyxl
```

On systems where Python is invoked with `python3`:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pandas openpyxl
```

Verify the installation:

```bash
python -c "import pandas, openpyxl; print('Dependencies installed successfully')"
```

If the application does not generate Excel output, `openpyxl` may not be required.

---

## Command-Line Usage

The application accepts:

1. The proposed trades CSV path.
2. The portfolio reference JSON path.
3. An optional output path.

### Basic Usage

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json
```

### Usage with an Output File

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json compliance_results.csv
```

### Usage with Excel Output

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json compliance_results.xlsx
```

On macOS/Linux, use `python3` if required:

```bash
python3 compliance_checker.py trades_test.csv portfolio_reference.json compliance_results.csv
```

### General Command Format

```text
python compliance_checker.py <trades_csv> <reference_json> [output_path]
```

Where:

| Argument | Required | Description |
|---|---:|---|
| `<trades_csv>` | Yes | Path to the proposed trades CSV file |
| `<reference_json>` | Yes | Path to the user-supplied portfolio reference JSON file |
| `[output_path]` | No | Optional path for CSV or XLSX output |

### Example Using Absolute Paths

```bash
python compliance_checker.py \
  "data/trades_test.csv" \
  "data/portfolio_reference.json" \
  "output/compliance_results.xlsx"
```

On Windows PowerShell:

```powershell
python compliance_checker.py `
  "data\trades_test.csv" `
  "data\portfolio_reference.json" `
  "output\compliance_results.xlsx"
```

---

## Output Format

The user-facing output contains only two fields:

```text
decision
reason
```

The output does not include the original trade columns unless the implementation explicitly provides a separate detailed or traceability output.

### Example Output

```text
decision,reason
Approved,Approved.
Rejected,Insufficient holdings to sell.
Rejected,Security is restricted for this portfolio.
Needs Manual Sign-off,Exceeds maximum position concentration — requires approval.
```

Results are returned in the same order as the input trades.

---

## CSV and XLSX Output

If an output path is supplied, the file format is determined by its extension.

### CSV Output

Example:

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json compliance_results.csv
```

The resulting CSV contains:

```csv
decision,reason
Approved,Approved.
Rejected,Insufficient cash for this buy order.
Needs Manual Sign-off,Exceeds maximum position concentration — requires approval.
```

### Excel Output

Example:

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json compliance_results.xlsx
```

The resulting workbook contains the decision and reason output in an Excel-compatible format.

Excel output requires:

```bash
python -m pip install openpyxl
```

If the current implementation does not include output-file support, the application will print the results to the console instead. In that case, CSV/XLSX generation must be added or enabled in the script.

---

## Sample Input

### `trades_test.csv`

```csv
portfolio_id,security_id,action,quantity,price,security_type
POR001,AAPL,Buy,20,150,Equity
POR001,TCS,Sell,60,100,Equity
POR002,GOOGL,Buy,5,2000,Equity
POR003,BADCO,Buy,10,100,Equity
POR004,AAPL,Buy,300,150,Equity
POR005,BOND01,Buy,10,100,Bond
```

### `portfolio_reference.json`

```json
{
  "POR001": {
    "cash_balance": 10000.0,
    "restricted_securities": [
      "XYZCORP"
    ],
    "max_position_pct": 0.4,
    "current_holdings": [
      {
        "security_id": "AAPL",
        "quantity": 50,
        "market_price": 150.0
      },
      {
        "security_id": "TCS",
        "quantity": 50,
        "market_price": 100.0
      }
    ]
  },
  "POR002": {
    "cash_balance": 10000.0,
    "restricted_securities": [],
    "max_position_pct": 0.5,
    "current_holdings": [
      {
        "security_id": "MSFT",
        "quantity": 20,
        "market_price": 300.0
      }
    ]
  },
  "POR003": {
    "cash_balance": 15000.0,
    "restricted_securities": [
      "BADCO"
    ],
    "max_position_pct": 0.5,
    "current_holdings": [
      {
        "security_id": "RELIANCE",
        "quantity": 30,
        "market_price": 250.0
      },
      {
        "security_id": "INFY",
        "quantity": 20,
        "market_price": 80.0
      }
    ]
  },
  "POR004": {
    "cash_balance": 50000.0,
    "restricted_securities": [],
    "max_position_pct": 0.4,
    "current_holdings": [
      {
        "security_id": "AAPL",
        "quantity": 100,
        "market_price": 150.0
      }
    ]
  },
  "POR005": {
    "cash_balance": 25000.0,
    "restricted_securities": [],
    "max_position_pct": 0.6,
    "current_holdings": [
      {
        "security_id": "BOND01",
        "quantity": 100,
        "market_price": 100.0
      }
    ]
  }
}
```

### Sample Result

```text
decision,reason
Approved,Approved.
Rejected,Insufficient holdings to sell.
Approved,Approved.
Rejected,Security is restricted for this portfolio.
Needs Manual Sign-off,Exceeds maximum position concentration — requires approval.
Approved,Approved.
```

---

## Validation and Error Handling

The application validates both input files before processing trades.

### Missing Trades CSV

If the trades CSV cannot be found, the application reports a file error rather than silently continuing.

Example:

```text
Error: Trades file not found: trades_test.csv
```

### Missing Reference JSON

If the reference JSON cannot be found:

```text
Error: Reference data file not found: portfolio_reference.json
```

### Invalid JSON

If the reference file is not valid JSON:

```text
Error: Reference data file contains invalid JSON.
```

### Missing Portfolio Fields

Each portfolio must contain:

- `cash_balance`
- `restricted_securities`
- `max_position_pct`
- `current_holdings`

If a required field is missing, the application should report which portfolio and field caused the problem.

Example:

```text
Error: Portfolio POR001 is missing required field: max_position_pct
```

### Invalid Cash Balance

`cash_balance` must be numeric and must not be negative.

Example:

```text
Error: Portfolio POR001 has an invalid cash_balance.
```

### Invalid Maximum Position Percentage

`max_position_pct` must be numeric and should normally be between `0` and `1`.

Examples:

```text
0.40 = 40%
0.75 = 75%
1.00 = 100%
```

Example error:

```text
Error: Portfolio POR001 has an invalid max_position_pct. Expected a value between 0 and 1.
```

### Invalid Holdings

Each holding must contain:

- `security_id`
- `quantity`
- `market_price`

Holding quantities must not be negative, and market prices must be positive.

Example:

```text
Error: Portfolio POR001 has an invalid holding for security AAPL.
```

### Unknown Portfolio

If a trade references a portfolio that does not exist in the reference JSON, the application should return a rejected result for that trade rather than attempting to process it without portfolio data.

Example:

```text
Decision: Rejected
Reason: Unknown portfolio - no reference data supplied.
```

### Invalid Trade Data

Invalid trade values produce:

```text
Decision: Rejected
Reason: Invalid trade data.
```

This includes:

- Missing or invalid quantity
- Zero or negative quantity
- Missing or invalid price
- Zero or negative price
- An action other than `Buy` or `Sell`

---

## Testing

### Run the Application Against Test Data

```bash
python compliance_checker.py trades_test.csv portfolio_reference.json
```

### Test Scenarios

The test data should cover:

- Valid buy orders
- Valid sell orders
- Invalid quantities
- Invalid prices
- Invalid actions
- Restricted securities
- Sell orders with insufficient holdings
- Sell orders equal to current holdings
- Buy orders exceeding available cash
- Buy orders equal to available cash
- Buy orders within the concentration limit
- Buy orders exceeding the concentration limit
- Position concentration exactly equal to the maximum
- Unknown portfolio identifiers
- Missing or malformed reference data
- Buy and sell orders for different security types

### Expected Rule Coverage

| Scenario | Expected Result |
|---|---|
| Invalid trade data | `Rejected` |
| Restricted security | `Rejected` |
| Insufficient sell holdings | `Rejected` |
| Exact sell holding quantity | Continues to later applicable rules |
| Insufficient cash | `Rejected` |
| Exact cash balance | Continues to concentration check |
| Concentration exceeds maximum | `Needs Manual Sign-off` |
| Concentration equals maximum | `Approved`, assuming all other checks pass |
| All checks pass | `Approved` |


