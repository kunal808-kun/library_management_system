import oracledb
import os

# Change these details according to your Oracle setup
DB_USER = ""
DB_PASSWORD = ""
DB_DSN = "192.168.29.34:1521/orcl"
ORACLE_CLIENT_DIR = os.path.join(
    os.environ["LOCALAPPDATA"], "Oracle", "instantclient_19_32"
)

oracledb.init_oracle_client(lib_dir=ORACLE_CLIENT_DIR)


def get_connection():
    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )


def add_book():
    book_id = input("Enter Book ID: ")
    title = input("Enter Book Title: ")
    author = input("Enter Author Name: ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO books (book_id, title, author, available)
                    VALUES (:1, :2, :3, 'Y')
                    """,
                    [book_id, title, author]
                )
            conn.commit()

        print("Book added successfully.")

    except oracledb.IntegrityError:
        print("Book ID already exists.")
    except oracledb.Error as e:
        print("Database error:", e)


def view_books():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT book_id, title, author, available FROM books ORDER BY book_id"
                )
                rows = cursor.fetchall()

        if not rows:
            print("No books found.")
            return

        print("\n----- Library Books -----")
        for book_id, title, author, available in rows:
            status = "Available" if available == "Y" else "Borrowed"
            print(f"ID: {book_id} | Title: {title} | Author: {author} | Status: {status}")

    except oracledb.Error as e:
        print("Database error:", e)


def search_book():
    title = input("Enter title to search: ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT book_id, title, author, available
                    FROM books
                    WHERE LOWER(title) LIKE :1
                    ORDER BY book_id
                    """,
                    ["%" + title.lower() + "%"]
                )
                rows = cursor.fetchall()

        if not rows:
            print("No matching book found.")
            return

        for book_id, title, author, available in rows:
            status = "Available" if available == "Y" else "Borrowed"
            print(f"ID: {book_id} | Title: {title} | Author: {author} | Status: {status}")

    except oracledb.Error as e:
        print("Database error:", e)


def borrow_book():
    book_id = input("Enter Book ID to borrow: ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT available FROM books WHERE book_id = :1",
                    [book_id]
                )
                row = cursor.fetchone()

                if row is None:
                    print("Book not found.")
                    return

                if row[0] == "N":
                    print("This book is already borrowed.")
                    return

                cursor.execute(
                    "UPDATE books SET available = 'N' WHERE book_id = :1",
                    [book_id]
                )

            conn.commit()

        print("Book borrowed successfully.")

    except oracledb.Error as e:
        print("Database error:", e)


def return_book():
    book_id = input("Enter Book ID to return: ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT available FROM books WHERE book_id = :1",
                    [book_id]
                )
                row = cursor.fetchone()

                if row is None:
                    print("Book not found.")
                    return

                if row[0] == "Y":
                    print("This book was not borrowed.")
                    return

                cursor.execute(
                    "UPDATE books SET available = 'Y' WHERE book_id = :1",
                    [book_id]
                )

            conn.commit()

        print("Book returned successfully.")

    except oracledb.Error as e:
        print("Database error:", e)


def delete_book():
    book_id = input("Enter Book ID to delete: ")

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM books WHERE book_id = :1",
                    [book_id]
                )

                if cursor.rowcount == 0:
                    print("Book not found.")
                else:
                    print("Book deleted successfully.")

            conn.commit()

    except oracledb.Error as e:
        print("Database error:", e)


def main():
    while True:
        print("\n===== Library Management System =====")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Search Book")
        print("4. Borrow Book")
        print("5. Return Book")
        print("6. Delete Book")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            view_books()
        elif choice == "3":
            search_book()
        elif choice == "4":
            borrow_book()
        elif choice == "5":
            return_book()
        elif choice == "6":
            delete_book()
        elif choice == "7":
            print("Exiting Library Management System.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()