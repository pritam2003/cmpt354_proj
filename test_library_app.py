import unittest
from io import StringIO
import sys
import sqlite3
import datetime

# Import your functions from the library_app.py file.
from library_app import (
    connect_db,
    find_item,
    borrow_item,
    return_item,
    donate_item,
    find_event,
    register_event,
    volunteer,
    ask_for_help
)

class TestLibraryApp(unittest.TestCase):
    def setUp(self):
        """Set up an in-memory SQLite database with the minimal schema and sample data."""
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.create_schema()
        self.populate_data()

    def tearDown(self):
        """Close the database connection."""
        self.conn.close()

    def create_schema(self):
        """Creates the necessary tables for testing."""
        self.conn.executescript("""
            CREATE TABLE Item (
                ISBN TEXT PRIMARY KEY,
                itemType TEXT,
                title TEXT,
                author TEXT,
                publishDate DATE,
                Publisher TEXT
            );
            CREATE TABLE Member (
                memberID INTEGER PRIMARY KEY,
                firstName TEXT,
                lastName TEXT,
                DOB DATE
            );
            CREATE TABLE Room (
                roomNumber TEXT PRIMARY KEY,
                maxCapacity INTEGER
            );
            CREATE TABLE Personnel (
                personnelID INTEGER PRIMARY KEY,
                Position TEXT,
                startDate DATE,
                salary REAL,
                roomNumber TEXT,
                FOREIGN KEY (roomNumber) REFERENCES Room(roomNumber)
            );
            CREATE TABLE Inventory (
                copyID INTEGER PRIMARY KEY,
                ISBN TEXT,
                Available BOOLEAN,
                shelfNumber TEXT,
                acquisitionDate DATE,
                physicalCondition TEXT,
                Source TEXT,
                FOREIGN KEY (ISBN) REFERENCES Item(ISBN)
            );
            CREATE TABLE Activity (
                loanID INTEGER PRIMARY KEY,
                copyID INTEGER,
                memberID INTEGER,
                borrowDate DATE,
                dueDate DATE,
                returnDate DATE,
                FOREIGN KEY (copyID) REFERENCES Inventory(copyID),
                FOREIGN KEY (memberID) REFERENCES Member(memberID)
            );
            CREATE TABLE Fine (
                loanID INTEGER PRIMARY KEY,
                amount REAL,
                paymentDate DATE,
                FOREIGN KEY (loanID) REFERENCES Activity(loanID)
            );
            CREATE TABLE Event (
                EventID INTEGER PRIMARY KEY,
                startDate DATE,
                endDate DATE,
                startTime TIME,
                endTime TIME,
                reservedSeats INTEGER,
                roomNumber TEXT,
                eventName TEXT,
                eventType TEXT,
                personnelID INTEGER,
                FOREIGN KEY (roomNumber) REFERENCES Room(roomNumber),
                FOREIGN KEY (personnelID) REFERENCES Personnel(personnelID)
            );
        """)
        self.conn.commit()

    def populate_data(self):
        """Insert sample records used by several tests."""
        # Insert one item.
        self.conn.execute("""
            INSERT INTO Item VALUES ('9783161484100', 'Print Book', 'The Great Gatsby',
            'F. Scott Fitzgerald', '1925-04-10', 'Scribner')
        """)
        # Insert one member.
        self.conn.execute("INSERT INTO Member VALUES (1, 'Alice', 'Smith', '1985-05-15')")
        # Insert one room with capacity 30.
        self.conn.execute("INSERT INTO Room VALUES ('R001', 30)")
        # Insert one personnel (a librarian at R001).
        self.conn.execute("INSERT INTO Personnel VALUES (1, 'Librarian', '2010-06-01', 45000, 'R001')")
        # Insert one inventory record for the item.
        self.conn.execute("INSERT INTO Inventory VALUES (1, '9783161484100', 1, 'A1', '2020-01-10', 'Good', 'Amazon')")
        # Insert one event (reservedSeats initially 10).
        self.conn.execute("""
            INSERT INTO Event VALUES (1, '2023-11-01', '2023-11-01', '18:00', '20:00', 10, 'R001', 
            'Book Club Meeting', 'Book Club', 1)
        """)
        self.conn.commit()

    def test_1_find_item(self):
        """Test finding an item by title/author."""
        test_input = "Gatsby\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        find_item(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        self.assertIn("The Great Gatsby", output.getvalue())

    def test_2_borrow_item(self):
        """
        Test borrowing an item.
        First, borrow the available copy; then try to borrow the same copy again as an edge case.
        The second attempt should not create a new Activity record.
        """
        # Normal borrowing: member 1 borrows copy 1.
        test_input = "1\n1\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        borrow_item(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Activity WHERE copyID = 1 AND memberID = 1")
        activity = cur.fetchone()
        self.assertIsNotNone(activity, "Activity record should be created when borrowing an item.")
        cur.execute("SELECT Available FROM Inventory WHERE copyID = 1")
        available = cur.fetchone()[0]
        self.assertEqual(available, 0, "Inventory record should mark the item as not available.")

        # Edge case: Attempt to borrow the same copy again by member 2.
        test_input = "2\n1\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        borrow_item(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        # Expect that no additional Activity record is created for copyID 1.
        cur.execute("SELECT COUNT(*) FROM Activity WHERE copyID = 1")
        count = cur.fetchone()[0]
        self.assertEqual(count, 1, "Edge case: Should not allow borrowing of an unavailable item.")

    def test_3_return_item(self):
        """Test returning an item: update loan with return date and mark inventory available."""
        # Insert an active loan record.
        self.conn.execute("""
            INSERT INTO Activity (loanID, copyID, memberID, borrowDate, dueDate, returnDate)
            VALUES (1, 1, 1, '2023-01-01', '2023-01-15', NULL)
        """)
        self.conn.execute("UPDATE Inventory SET Available = 0 WHERE copyID = 1")
        self.conn.commit()

        test_input = "1\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        return_item(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

        cur = self.conn.cursor()
        cur.execute("SELECT returnDate FROM Activity WHERE loanID = 1")
        return_date = cur.fetchone()[0]
        self.assertIsNotNone(return_date, "Return date should be set after returning an item.")
        cur.execute("SELECT Available FROM Inventory WHERE copyID = 1")
        available = cur.fetchone()[0]
        self.assertEqual(available, 1, "Inventory record should mark the item as available after return.")

    def test_4_donate_item(self):
        """
        Test donating an item.
        For a new ISBN, the function should insert into Item and create a corresponding Inventory record.
        """
        test_input = (
            "9789999999999\n"  # New ISBN
            "Print Book\n"
            "Test Book\n"
            "Test Author\n"
            "2023-01-01\n"
            "Test Publisher\n"
            "S1\n"
            "Good\n"
        )
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        donate_item(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Item WHERE ISBN = '9789999999999'")
        item = cur.fetchone()
        self.assertIsNotNone(item, "Donated item should be added to the Item table.")
        cur.execute("SELECT * FROM Inventory WHERE ISBN = '9789999999999'")
        inventory = cur.fetchone()
        self.assertIsNotNone(inventory, "An inventory record should be created for the donated item.")

    def test_5_find_event(self):
        """Test finding an event by searching for event name or type."""
        test_input = "Book Club\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        find_event(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        self.assertIn("Book Club Meeting", output.getvalue())

    def test_6_register_event(self):
        """
        Test event registration.
        First, a normal registration should increment reservedSeats.
        Then, as an edge case, simulate a full event (reservedSeats equals room capacity) and verify the error message.
        """
        # Normal registration:
        test_input = "1\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        register_event(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

        cur = self.conn.cursor()
        cur.execute("SELECT reservedSeats FROM Event WHERE EventID = 1")
        reserved = cur.fetchone()[0]
        self.assertEqual(reserved, 11, "Reserved seats should increment by 1 upon registration.")

        # Edge case: Set reservedSeats equal to room capacity.
        cur.execute("UPDATE Event SET reservedSeats = 30 WHERE EventID = 1")
        self.conn.commit()
        test_input = "1\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        register_event(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        self.assertIn("fully booked", output.getvalue(), "Should indicate the event is fully booked when at capacity.")

    def test_7_volunteer(self):
        """Test volunteer signup by adding a Personnel record with Position 'Volunteer'."""
        test_input = "Test\nUser\nR001\n"
        sys.stdin = StringIO(test_input)
        output = StringIO()
        sys.stdout = output
        volunteer(self.conn)
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM Personnel WHERE Position = 'Volunteer' AND roomNumber = 'R001'")
        record = cur.fetchone()
        self.assertIsNotNone(record, "Volunteer record should be added to the Personnel table.")

    def test_8_ask_for_help(self):
        """Test asking for help: should locate a librarian in room R001."""
        output = StringIO()
        sys.stdout = output
        ask_for_help(self.conn)
        sys.stdout = sys.__stdout__
        self.assertIn("R001", output.getvalue(), "Output should indicate a librarian in room R001 is available.")

# Custom TestResult class to print messages after each test.
class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        test_num = self._get_test_number(test)
        print(f"Test {test_num} passed")
    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_num = self._get_test_number(test)
        print(f"Test {test_num} failed due to: {self._exc_info_to_string(err, test)}")
    def addError(self, test, err):
        super().addError(test, err)
        test_num = self._get_test_number(test)
        print(f"Test {test_num} failed due to: {self._exc_info_to_string(err, test)}")
    def _get_test_number(self, test):
        # Expecting test method names like test_1_find_item, test_2_borrow_item, etc.
        test_id = test.id()
        test_method = test_id.split('.')[-1]
        if test_method.startswith("test_"):
            parts = test_method.split('_')
            if len(parts) > 1:
                return parts[1]  # returns the number part
        return test_method

if __name__ == '__main__':
    # Load tests and run with our custom result class.
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLibraryApp)
    runner = unittest.TextTestRunner(resultclass=CustomTestResult, verbosity=2)
    result = runner.run(suite)
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.failures) - len(result.errors)
    if result.wasSuccessful():
        print("All tests passed")
    else:
        # Build lists of test method names that passed and failed.
        passed_ids = []
        failed_ids = []
        for test in suite:
            test_id = test.id().split('.')[-1]
            found_failure = any(test_id in f[0].id() for f in result.failures)
            found_error = any(test_id in e[0].id() for e in result.errors)
            if found_failure or found_error:
                failed_ids.append(test_id)
            else:
                passed_ids.append(test_id)
        percent = (len(passed_ids) / total_tests) * 100
        print(f"{percent:.0f}% tests passed, tests passed- {', '.join(passed_ids)} and failed - {', '.join(failed_ids)}")
