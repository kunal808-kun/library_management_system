import getpass
import os
import sys
from decimal import Decimal, InvalidOperation

import oracledb


DB_DSN = os.getenv("ORACLE_DSN", "192.168.29.34:1521/orcl")
ORACLE_CLIENT_DIR = os.path.join(
    os.environ["LOCALAPPDATA"], "Oracle", "instantclient_19_32"
)

oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)

_credentials = None


def get_connection():
    global _credentials
    if _credentials is None:
        user = os.getenv("ORACLE_USER") or input("Oracle username: ").strip()
        password = os.getenv("ORACLE_PASSWORD") or getpass.getpass(
            "Oracle password: "
        )
        _credentials = (user, password)
    user, password = _credentials
    return oracledb.connect(user=user, password=password, dsn=DB_DSN)


def initialize_database():
    statement = """
        CREATE TABLE bank_accounts (
            account_no VARCHAR2(20) PRIMARY KEY,
            account_holder VARCHAR2(100) NOT NULL,
            balance NUMBER(15, 2) DEFAULT 0 NOT NULL
                CHECK (balance >= 0)
        )
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(statement)
            except oracledb.DatabaseError as error:
                if error.args[0].code != 955:
                    raise
        connection.commit()


def read_amount(prompt, allow_zero=False):
    while True:
        try:
            amount = Decimal(input(prompt).strip())
            if not amount.is_finite() or amount < 0:
                raise InvalidOperation
            if amount == 0 and not allow_zero:
                raise InvalidOperation
            if amount.quantize(Decimal("0.01")) != amount:
                raise InvalidOperation
            return amount
        except (InvalidOperation, ValueError):
            requirement = "non-negative" if allow_zero else "positive"
            print(f"Enter a {requirement} amount with up to two decimal places.")


def create_account():
    account_no = input("Enter account number: ").strip()
    account_holder = input("Enter account holder name: ").strip()
    if not account_no or not account_holder:
        print("Account number and holder name are required.")
        return

    opening_balance = read_amount("Enter opening balance: ", allow_zero=True)
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO bank_accounts (account_no, account_holder, balance)
                    VALUES (:1, :2, :3)
                    """,
                    [account_no, account_holder, opening_balance],
                )
            connection.commit()
        print("Account created successfully.")
    except oracledb.IntegrityError:
        print("That account number already exists.")
    except oracledb.Error as error:
        print("Database error:", error)


def view_accounts():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT account_no, account_holder, balance
                    FROM bank_accounts
                    ORDER BY account_no
                    """
                )
                accounts = cursor.fetchall()

        if not accounts:
            print("No accounts found.")
            return

        print("\n----- Bank Accounts -----")
        for account_no, holder, balance in accounts:
            print(
                f"Account: {account_no} | Holder: {holder} "
                f"| Balance: {balance:,.2f}"
            )
    except oracledb.Error as error:
        print("Database error:", error)


def check_balance():
    account_no = input("Enter account number: ").strip()
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance FROM bank_accounts WHERE account_no = :1",
                    [account_no],
                )
                row = cursor.fetchone()

        if row is None:
            print("Account not found.")
        else:
            print(f"Current balance: {row[0]:,.2f}")
    except oracledb.Error as error:
        print("Database error:", error)


def change_balance(action, add_to_balance):
    account_no = input("Enter account number: ").strip()
    amount = read_amount(f"Enter {action.lower()} amount: ")
    operator = "+" if add_to_balance else "-"

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT balance FROM bank_accounts "
                    f"WHERE account_no = :1 FOR UPDATE",
                    [account_no],
                )
                row = cursor.fetchone()
                if row is None:
                    print("Account not found.")
                    return
                if not add_to_balance and row[0] < amount:
                    print("Insufficient funds.")
                    return

                cursor.execute(
                    f"UPDATE bank_accounts SET balance = balance {operator} :1 "
                    "WHERE account_no = :2",
                    [amount, account_no],
                )
            connection.commit()

        print(f"{action} completed successfully.")
    except oracledb.Error as error:
        print("Database error:", error)


def deposit():
    change_balance("Deposit", add_to_balance=True)


def withdraw():
    change_balance("Withdrawal", add_to_balance=False)


def main():
    try:
        initialize_database()
        print("Connected to Oracle. Banking accounts are ready.")
    except oracledb.Error as error:
        print("Could not initialize the banking database:", error)
        sys.exit(1)

    actions = {
        "1": create_account,
        "2": view_accounts,
        "3": check_balance,
        "4": deposit,
        "5": withdraw,
    }

    while True:
        print("\n===== Banking Management System =====")
        print("1. Create Account")
        print("2. View All Accounts")
        print("3. Check Balance")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "6":
            print("Exiting Banking Management System.")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Please try again.")
        else:
            action()


if __name__ == "__main__":
    main()
