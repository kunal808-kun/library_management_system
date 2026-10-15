# Banking Management System

## About
A console-based Banking Management System developed using Python and Oracle SQL.

## Features
- Create bank accounts
- View all accounts
- Check account balances
- Deposit money
- Withdraw money
- Transfer money between accounts
- View transaction history

## Technologies Used
- Python
- Oracle Database
- python-oracledb

## Database
The application uses two tables:
- `bank_accounts` — stores account details and balances.
- `bank_transactions` — stores transaction records.

An Oracle sequence generates transaction IDs.

## Installation
1. Install Python and configure Oracle Database.
2. Install the dependency using `python -m pip install oracledb`.
3. Configure your Oracle connection settings and credentials.
4. Run `python banking_management.py`.