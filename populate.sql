---------------------------------------------------------
-- Insert Data into Item Table
---------------------------------------------------------
INSERT INTO Item (ISBN, itemType, title, author, publishDate, Publisher) VALUES
  ('9783161484100', 'Print Book', 'The Great Gatsby', 'F. Scott Fitzgerald', '1925-04-10', 'Scribner'),
  ('9780140449136', 'Print Book', 'The Odyssey', 'Homer', '1999-11-01', 'Penguin Classics'),
  ('9780307277671', 'Online Book', 'The Road', 'Cormac McCarthy', '2006-09-26', 'Vintage'),
  ('9780679783272', 'Print Book', 'Pride and Prejudice', 'Jane Austen', '2000-10-10', 'Modern Library'),
  ('9780525566151', 'Magazine', 'Time', 'Various', '2020-07-01', 'Time Inc.'),
  ('9780061120084', 'Print Book', 'To Kill a Mockingbird', 'Harper Lee', '1960-07-11', 'J.B. Lippincott & Co.'),
  ('9780307465351', 'Scientific Journal', 'Nature Research', 'Nature Publishing', '2021-03-15', 'Nature'),
  ('9780131103627', 'CD', 'Abbey Road', 'The Beatles', '1969-09-26', 'Apple Records'),
  ('9780316769488', 'Record', 'Rumours', 'Fleetwood Mac', '1977-02-04', 'Warner Bros.'),
  ('9780743273565', 'Online Book', '1984', 'George Orwell', '1949-06-08', 'Secker & Warburg');

---------------------------------------------------------
-- Insert Data into Member Table
---------------------------------------------------------
INSERT INTO Member (memberID, firstName, lastName, DOB) VALUES
  (1, 'Alice', 'Smith', '1985-05-15'),
  (2, 'Bob', 'Johnson', '1990-03-22'),
  (3, 'Charlie', 'Williams', '1978-11-30'),
  (4, 'Diana', 'Brown', '2000-01-10'),
  (5, 'Edward', 'Jones', '1988-07-08'),
  (6, 'Fiona', 'Garcia', '1995-09-17'),
  (7, 'George', 'Miller', '1980-12-25'),
  (8, 'Hannah', 'Davis', '1992-04-05'),
  (9, 'Ian', 'Rodriguez', '1975-06-20'),
  (10, 'Jenny', 'Martinez', '1983-08-30');

---------------------------------------------------------
-- Insert Data into Room Table
---------------------------------------------------------
INSERT INTO Room (roomNumber, maxCapacity) VALUES
  ('R001', 30),
  ('R002', 50),
  ('R003', 20),
  ('R004', 40),
  ('R005', 25),
  ('R006', 35),
  ('R007', 15),
  ('R008', 45),
  ('R009', 60),
  ('R010', 55);

---------------------------------------------------------
-- Insert Data into Personnel Table
---------------------------------------------------------
INSERT INTO Personnel (personnelID, Position, startDate, salary, roomNumber) VALUES
  (1, 'Librarian', '2010-06-01', 45000, 'R001'),
  (2, 'Volunteer', '2022-01-15', 0, 'R002'),
  (3, 'Assistant Librarian', '2015-09-10', 35000, 'R003'),
  (4, 'Manager', '2008-03-12', 55000, 'R004'),
  (5, 'Volunteer', '2021-07-05', 0, 'R005'),
  (6, 'Archivist', '2018-11-20', 40000, 'R006'),
  (7, 'IT Support', '2019-04-15', 42000, 'R007'),
  (8, 'Volunteer', '2020-08-01', 0, 'R008'),
  (9, 'Librarian', '2012-05-22', 47000, 'R009'),
  (10, 'Volunteer', '2023-01-01', 0, 'R010');

---------------------------------------------------------
-- Insert Data into Inventory Table
---------------------------------------------------------
INSERT INTO Inventory (copyID, ISBN, Available, shelfNumber, acquisitionDate, physicalCondition, Source) VALUES
  (1, '9783161484100', 1, 'A1', '2020-01-10', 'Good', 'Amazon'),
  (2, '9780140449136', 1, 'A2', '2019-03-15', 'Excellent', 'Donated'),
  (3, '9780307277671', 0, 'B1', '2021-06-20', 'Fair', 'Amazon'),
  (4, '9780679783272', 1, 'B2', '2018-08-30', 'Good', 'Donated'),
  (5, '9780525566151', 1, 'C1', '2022-05-12', 'New', 'Amazon'),
  (6, '9780061120084', 0, 'C2', '2017-11-05', 'Worn', 'Donated'),
  (7, '9780307465351', 1, 'D1', '2023-02-20', 'Excellent', 'Amazon'),
  (8, '9780131103627', 1, 'D2', '2020-09-15', 'Good', 'Donated'),
  (9, '9780316769488', 1, 'E1', '2016-04-18', 'Fair', 'Amazon'),
  (10, '9780743273565', 0, 'E2', '2015-12-30', 'Good', 'Donated');

---------------------------------------------------------
-- Insert Data into Activity Table
---------------------------------------------------------
-- Each row represents a loan; the returnDate is set to a date after dueDate to simulate overdue loans.
INSERT INTO Activity (loanID, copyID, memberID, borrowDate, dueDate, returnDate) VALUES
  (1, 1, 1, '2023-01-01', '2023-01-15', '2023-01-20'),
  (2, 2, 2, '2023-02-01', '2023-02-15', '2023-02-18'),
  (3, 3, 3, '2023-03-01', '2023-03-15', '2023-03-16'),
  (4, 4, 4, '2023-04-01', '2023-04-15', '2023-04-20'),
  (5, 5, 5, '2023-05-01', '2023-05-15', '2023-05-17'),
  (6, 6, 6, '2023-06-01', '2023-06-15', '2023-06-25'),
  (7, 7, 7, '2023-07-01', '2023-07-15', '2023-07-15'),
  (8, 8, 8, '2023-08-01', '2023-08-15', '2023-08-20'),
  (9, 9, 9, '2023-09-01', '2023-09-15', '2023-09-18'),
  (10, 10, 10, '2023-10-01', '2023-10-15', '2023-10-16');

---------------------------------------------------------
-- Insert Data into Fine Table
---------------------------------------------------------
-- The fine amount is calculated as (returnDate - dueDate) in days (rate: 1 per day).
-- PaymentDate is NULL if the fine hasn't been paid; otherwise, it shows when payment occurred.
INSERT INTO Fine (loanID, amount, paymentDate) VALUES
  (1, 5.0, NULL),      -- Overdue by 5 days
  (2, 3.0, '2023-02-20'),  -- Overdue by 3 days and paid
  (3, 1.0, NULL),      -- Overdue by 1 day
  (4, 5.0, '2023-04-25'),  -- Overdue by 5 days and paid
  (5, 2.0, NULL),      -- Overdue by 2 days
  (6, 10.0, NULL),     -- Overdue by 10 days
  (7, 0.0, '2023-07-16'),  -- Returned on time (no fine)
  (8, 5.0, NULL),      -- Overdue by 5 days
  (9, 3.0, '2023-09-20'),  -- Overdue by 3 days and paid
  (10, 1.0, NULL);     -- Overdue by 1 day

---------------------------------------------------------
-- Insert Data into Event Table
---------------------------------------------------------
-- Each event is scheduled in a room, and reservedSeats are set within the room's capacity.
INSERT INTO Event (EventID, startDate, endDate, startTime, endTime, reservedSeats, roomNumber, eventName, eventType, personnelID) VALUES
  (1, '2023-11-01', '2023-11-01', '18:00', '20:00', 25, 'R002', 'Book Club Meeting', 'Book Club', 1),
  (2, '2023-11-05', '2023-11-05', '19:00', '21:00', 30, 'R004', 'Film Screening', 'Film', 4),
  (3, '2023-11-10', '2023-11-10', '17:00', '19:00', 20, 'R003', 'Art Show', 'Art', 2),
  (4, '2023-11-15', '2023-11-15', '16:00', '18:00', 15, 'R007', 'Science Talk', 'Lecture', 3),
  (5, '2023-11-20', '2023-11-20', '15:00', '17:00', 40, 'R009', 'Historical Discussion', 'Discussion', 9),
  (6, '2023-11-25', '2023-11-25', '14:00', '16:00', 10, 'R005', 'Local Authors Meetup', 'Meetup', 5),
  (7, '2023-11-30', '2023-11-30', '13:00', '15:00', 20, 'R006', 'Poetry Reading', 'Literary', 6),
  (8, '2023-12-05', '2023-12-05', '12:00', '14:00', 35, 'R010', 'New Book Launch', 'Launch', 10),
  (9, '2023-12-10', '2023-12-10', '11:00', '13:00', 45, 'R008', 'Community Forum', 'Forum', 8),
  (10, '2023-12-15', '2023-12-15', '10:00', '12:00', 50, 'R009', 'Literature Workshop', 'Workshop', 7);
