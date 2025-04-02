-- Enable foreign key enforcement in SQLite.
PRAGMA foreign_keys = ON;

---------------------------------------------------------
-- Table Definitions
---------------------------------------------------------

-- Item table: one row per distinct book/item.
CREATE TABLE Item (
    ISBN TEXT PRIMARY KEY,          -- Unique identifier for each item
    itemType TEXT,                  -- Type of item (print book, online book, magazine, etc.)
    title TEXT,                     -- Title of the item
    author TEXT,                    -- Author of the item (note: this could be extended for multiple authors)
    publishDate DATE,               -- Publication date of the item
    Publisher TEXT                  -- Publisher of the item
);

-- Member table: records for library members.
CREATE TABLE Member (
    memberID INTEGER PRIMARY KEY,   -- Unique identifier for each member
    firstName TEXT,                 -- Member's first name
    lastName TEXT,                  -- Member's last name
    DOB DATE                       -- Date of birth
);

-- Room table: defines library rooms for events and work areas.
CREATE TABLE Room (
    roomNumber TEXT PRIMARY KEY,    -- Unique room identifier
    maxCapacity INTEGER CHECK (maxCapacity > 0)  -- Maximum capacity, must be a positive number
);

-- Personnel table: records for library employees and volunteers.
CREATE TABLE Personnel (
    personnelID INTEGER PRIMARY KEY,  -- Unique identifier for each personnel record
    Position TEXT,                    -- Job position (e.g., librarian, volunteer)
    startDate DATE,                   -- Date when the personnel started
    salary REAL,                      -- Salary information
    roomNumber TEXT,                  -- Room where the personnel is assigned
    FOREIGN KEY (roomNumber) REFERENCES Room(roomNumber)
);

-- Inventory table: tracks individual copies of items.
CREATE TABLE Inventory (
    copyID INTEGER PRIMARY KEY,       -- Unique identifier for each copy of an item
    ISBN TEXT,                        -- Foreign key to the Item table
    Available BOOLEAN,                -- Availability status (true if available)
    shelfNumber TEXT,                 -- Shelf location in the library
    acquisitionDate DATE,             -- Date the copy was acquired
    physicalCondition TEXT,           -- Condition of the copy (e.g., new, good, worn)
    Source TEXT,                      -- Source of acquisition (e.g., 'Amazon', 'Donated')
    FOREIGN KEY (ISBN) REFERENCES Item(ISBN)
);

-- Activity table: records borrowing (loans) history.
CREATE TABLE Activity (
    loanID INTEGER PRIMARY KEY,       -- Unique identifier for each loan record
    copyID INTEGER,                   -- Foreign key to Inventory (the specific copy being loaned)
    memberID INTEGER,                 -- Foreign key to Member (who is borrowing)
    borrowDate DATE,                  -- Date when the item was borrowed
    dueDate DATE,                     -- Due date for returning the item
    returnDate DATE,                  -- Date when the item was returned (NULL if not yet returned)
    FOREIGN KEY (copyID) REFERENCES Inventory(copyID),
    FOREIGN KEY (memberID) REFERENCES Member(memberID),
    CHECK (returnDate IS NULL OR returnDate >= borrowDate)  -- Ensure return date is not before borrow date
);

-- Fine table: each loan can have at most one associated fine.
CREATE TABLE Fine (
    loanID INTEGER PRIMARY KEY,       -- Loan ID acts as both the primary key and foreign key (one fine per loan)
    amount REAL,                      -- Fine amount
    paymentDate DATE,                 -- Date when the fine was paid (NULL if not yet paid)
    FOREIGN KEY (loanID) REFERENCES Activity(loanID)
);

-- Event table: records events hosted by the library.
CREATE TABLE Event (
    EventID INTEGER PRIMARY KEY,      -- Unique identifier for each event
    startDate DATE,                   -- Start date of the event
    endDate DATE,                     -- End date of the event
    startTime TIME,                   -- Start time of the event
    endTime TIME,                     -- End time of the event
    reservedSeats INTEGER,            -- Number of reserved seats for the event
    roomNumber TEXT,                  -- Foreign key to Room (location of the event)
    eventName TEXT,                   -- Name of the event
    eventType TEXT,                   -- Type of event (e.g., book club, art show)
    personnelID INTEGER,              -- Foreign key to Personnel (employee managing the event)
    FOREIGN KEY (roomNumber) REFERENCES Room(roomNumber),
    FOREIGN KEY (personnelID) REFERENCES Personnel(personnelID)
);

---------------------------------------------------------
-- Trigger Definitions
---------------------------------------------------------

-- Trigger to ensure that the number of reserved seats does not exceed the room's maximum capacity.
CREATE TRIGGER check_event_reservedSeats_insert
BEFORE INSERT ON Event
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.reservedSeats > (SELECT maxCapacity FROM Room WHERE roomNumber = NEW.roomNumber)
        THEN RAISE(ABORT, 'Reserved seats exceed room capacity')
    END;
END;

-- Same check for update operations on the Event table.
CREATE TRIGGER check_event_reservedSeats_update
BEFORE UPDATE ON Event
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.reservedSeats > (SELECT maxCapacity FROM Room WHERE roomNumber = NEW.roomNumber)
        THEN RAISE(ABORT, 'Reserved seats exceed room capacity')
    END;
END;

-- Trigger to adjust fines when a loan's returnDate is updated.
-- Fine is calculated as (number of overdue days) * 1 (rate per day)
CREATE TRIGGER adjust_fine_after_return
AFTER UPDATE OF returnDate ON Activity
FOR EACH ROW
WHEN NEW.returnDate IS NOT NULL
BEGIN
    -- If the item is returned late, insert or update the fine record.
    INSERT OR REPLACE INTO Fine (loanID, amount, paymentDate)
    SELECT NEW.loanID,
           (julianday(NEW.returnDate) - julianday(NEW.dueDate)) * 1.0,
           NULL
    WHERE julianday(NEW.returnDate) > julianday(NEW.dueDate);
    
    -- If the item is returned on time, delete any existing fine record.
    DELETE FROM Fine 
    WHERE NEW.returnDate IS NOT NULL 
      AND julianday(NEW.returnDate) <= julianday(NEW.dueDate)
      AND loanID = NEW.loanID;
END;

-- Trigger to insert a fine record for an open (not yet returned) but overdue loan.
CREATE TRIGGER insert_fine_for_overdue_loan
AFTER INSERT ON Activity
FOR EACH ROW
WHEN NEW.returnDate IS NULL AND date('now') > NEW.dueDate
BEGIN
    INSERT OR REPLACE INTO Fine (loanID, amount, paymentDate)
    SELECT NEW.loanID,
           (julianday(date('now')) - julianday(NEW.dueDate)) * 1.0,
           NULL;
END;

-- Trigger to update fine for an open, overdue loan if dueDate or borrowDate is modified.
CREATE TRIGGER update_fine_for_overdue_loan
AFTER UPDATE OF dueDate, borrowDate ON Activity
FOR EACH ROW
WHEN NEW.returnDate IS NULL AND date('now') > NEW.dueDate
BEGIN
    INSERT OR REPLACE INTO Fine (loanID, amount, paymentDate)
    SELECT NEW.loanID,
           (julianday(date('now')) - julianday(NEW.dueDate)) * 1.0,
           NULL;
END;

-- Trigger to remove the fine if a loan is no longer overdue.
CREATE TRIGGER remove_fine_for_non_overdue_loan
AFTER UPDATE OF dueDate, borrowDate, returnDate ON Activity
FOR EACH ROW
WHEN (NEW.returnDate IS NOT NULL AND julianday(NEW.returnDate) <= julianday(NEW.dueDate))
   OR (NEW.returnDate IS NULL AND date('now') <= NEW.dueDate)
BEGIN
    DELETE FROM Fine WHERE loanID = NEW.loanID;
END;
