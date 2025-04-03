import sqlite3
import datetime

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect("library.db")

def find_item(conn):
    """Search for an item by title or author."""
    search = input("Enter title or author to search for: ")
    cur = conn.cursor()
    cur.execute("""
        SELECT ISBN, title, author, itemType 
        FROM Item 
        WHERE title LIKE ? OR author LIKE ?
    """, ('%' + search + '%', '%' + search + '%'))
    results = cur.fetchall()
    if results:
        print("Items found:")
        for row in results:
            print(f"ISBN: {row[0]}, Title: {row[1]}, Author: {row[2]}, Type: {row[3]}")
    else:
        print("No items found.")

def borrow_item(conn):
    """
    Borrow an item from the library.
    
    Inserts a new Activity record and marks the Inventory record as unavailable.
    """
    member_id = input("Enter your member ID: ")
    copy_id = input("Enter the copy ID you want to borrow: ")
    borrow_date = datetime.date.today().isoformat()
    due_date = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()
    cur = conn.cursor()
    try:
        # Insert new loan record. The returnDate is set to NULL until the item is returned.
        cur.execute("""
            INSERT INTO Activity (copyID, memberID, borrowDate, dueDate, returnDate)
            VALUES (?, ?, ?, ?, NULL)
        """, (copy_id, member_id, borrow_date, due_date))
        # Update Inventory to mark the copy as unavailable.
        cur.execute("UPDATE Inventory SET Available = 0 WHERE copyID = ?", (copy_id,))
        conn.commit()
        print(f"Item borrowed successfully. Due date is {due_date}")
    except Exception as e:
        print("Error borrowing item:", e)

def return_item(conn):
    """
    Return a borrowed item.
    
    Updates the Activity record with the return date and marks the Inventory record as available.
    Note: Fine history is maintained in the Fine table. When an overdue fine exists,
    its record is updated (not deleted) via triggers when the item is returned. A paymentDate
    set from NULL indicates that the fine has been paid.
    """
    loan_id = input("Enter your loan ID: ")
    return_date = datetime.date.today().isoformat()
    cur = conn.cursor()
    try:
        # Update the Activity record to record the return date.
        cur.execute("UPDATE Activity SET returnDate = ? WHERE loanID = ?", (return_date, loan_id))
        # Retrieve the associated copyID.
        cur.execute("SELECT copyID FROM Activity WHERE loanID = ?", (loan_id,))
        result = cur.fetchone()
        if result:
            copy_id = result[0]
            # Mark the item as available in the Inventory.
            cur.execute("UPDATE Inventory SET Available = 1 WHERE copyID = ?", (copy_id,))
        conn.commit()
        print("Item returned successfully. Fine history is preserved for record purposes.")
    except Exception as e:
        print("Error returning item:", e)

def donate_item(conn):
    """
    Donate an item to the library.
    
    If the item does not exist in the catalog, prompts for additional details to add it.
    Then, adds a new record in Inventory with the source noted as 'Donated'.
    """
    isbn = input("Enter ISBN of the donated item: ")
    cur = conn.cursor()
    # Check if the item already exists in the catalog.
    cur.execute("SELECT * FROM Item WHERE ISBN = ?", (isbn,))
    item = cur.fetchone()
    if not item:
        print("Item not found in the catalog. Please provide additional details.")
        item_type = input("Enter item type (e.g., Print Book, Online Book, Magazine): ")
        title = input("Enter title: ")
        author = input("Enter author: ")
        publish_date = input("Enter publish date (YYYY-MM-DD): ")
        publisher = input("Enter publisher: ")
        cur.execute("""
            INSERT INTO Item (ISBN, itemType, title, author, publishDate, Publisher)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (isbn, item_type, title, author, publish_date, publisher))
    shelf_number = input("Enter shelf number: ")
    acquisition_date = datetime.date.today().isoformat()
    physical_condition = input("Enter physical condition: ")
    source = "Donated"
    try:
        cur.execute("""
            INSERT INTO Inventory (ISBN, Available, shelfNumber, acquisitionDate, physicalCondition, Source)
            VALUES (?, 1, ?, ?, ?, ?)
        """, (isbn, shelf_number, acquisition_date, physical_condition, source))
        conn.commit()
        print("Donation recorded successfully.")
    except Exception as e:
        print("Error recording donation:", e)

def find_event(conn):
    """Find an event in the library by event name or type."""
    search = input("Enter event name or type to search for: ")
    cur = conn.cursor()
    cur.execute("""
        SELECT EventID, eventName, eventType, startDate, startTime, roomNumber 
        FROM Event 
        WHERE eventName LIKE ? OR eventType LIKE ?
    """, ('%' + search + '%', '%' + search + '%'))
    results = cur.fetchall()
    if results:
        print("Events found:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Date: {row[3]}, Time: {row[4]}, Room: {row[5]}")
    else:
        print("No events found.")

def register_event(conn):
    """
    Register for an event.
    
    Checks if the reservedSeats is within the room's capacity, and if so, increments it.
    """
    event_id = input("Enter the Event ID you want to register for: ")
    cur = conn.cursor()
    try:
        cur.execute("SELECT reservedSeats, roomNumber FROM Event WHERE EventID = ?", (event_id,))
        result = cur.fetchone()
        if result:
            current_reserved, room_number = result
            cur.execute("SELECT maxCapacity FROM Room WHERE roomNumber = ?", (room_number,))
            room_capacity = cur.fetchone()[0]
            if current_reserved < room_capacity:
                new_reserved = current_reserved + 1
                cur.execute("UPDATE Event SET reservedSeats = ? WHERE EventID = ?", (new_reserved, event_id))
                conn.commit()
                print("Successfully registered for the event.")
            else:
                print("Sorry, the event is fully booked.")
        else:
            print("Event not found.")
    except Exception as e:
        print("Error registering for event:", e)

def volunteer(conn):
    """
    Volunteer for the library.
    
    Adds a new Personnel record with Position set to 'Volunteer'.
    """
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    start_date = datetime.date.today().isoformat()
    salary = 0.0  # Volunteers do not receive a salary.
    room_number = input("Enter the room number where you'll volunteer (e.g., R001 for front desk): ")
    position = "Volunteer"
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Personnel (Position, startDate, salary, roomNumber)
            VALUES (?, ?, ?, ?)
        """, (position, start_date, salary, room_number))
        conn.commit()
        print("Thank you for volunteering!")
    except Exception as e:
        print("Error signing up as a volunteer:", e)

def ask_for_help(conn):
    """
    Ask for help from a librarian.
    
    Looks up a librarian assigned to room R001 (front desk) and provides instructions.
    """
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT personnelID, Position 
            FROM Personnel 
            WHERE Position LIKE '%Librarian%' AND roomNumber = 'R001' 
            LIMIT 1
        """)
        librarian = cur.fetchone()
        if librarian:
            print("A librarian is available to help you. Please go to room R001.")
        else:
            print("No librarian is currently available. Please try again later.")
    except Exception as e:
        print("Error finding a librarian:", e)

def main():
    """Main menu loop for the library application."""
    conn = connect_db()
    while True:
        print("\nLibrary Database Application")
        print("1. Find an item")
        print("2. Borrow an item")
        print("3. Return an item")
        print("4. Donate an item")
        print("5. Find an event")
        print("6. Register for an event")
        print("7. Volunteer for the library")
        print("8. Ask for help from a librarian")
        print("9. Exit")
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            find_item(conn)
        elif choice == '2':
            borrow_item(conn)
        elif choice == '3':
            return_item(conn)
        elif choice == '4':
            donate_item(conn)
        elif choice == '5':
            find_event(conn)
        elif choice == '6':
            register_event(conn)
        elif choice == '7':
            volunteer(conn)
        elif choice == '8':
            ask_for_help(conn)
        elif choice == '9':
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please try again.")
    
    conn.close()

if __name__ == "__main__":
    main()
