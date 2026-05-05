-- ═══════════════════════════════════════════════════════
--   TicketVault Database Setup  ·  MS SQL Server
--   FA24-BSE-152  |  S.M. Mateen Ud Din
-- ═══════════════════════════════════════════════════════

-- 1. Create & use database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TicketBookingDB')
    CREATE DATABASE TicketBookingDB;
GO
USE TicketBookingDB;
GO

-- ─── TABLE 1 : Categories (fixed pricing tiers) ──────
CREATE TABLE Categories (
    CategoryID   INT           PRIMARY KEY IDENTITY(1,1),
    CategoryName VARCHAR(20)   NOT NULL,
    Price        DECIMAL(10,2) NOT NULL
);

-- ─── TABLE 2 : Events ────────────────────────────────
CREATE TABLE Events (
    EventID    INT          PRIMARY KEY IDENTITY(1,1),
    EventName  VARCHAR(100) NOT NULL,
    EventDate  DATE         NOT NULL,
    Location   VARCHAR(200) NOT NULL,
    TotalSeats INT          NOT NULL DEFAULT 100
);

-- ─── TABLE 3 : Users ─────────────────────────────────
CREATE TABLE Users (
    UserID    INT          PRIMARY KEY IDENTITY(1,1),
    UserName  VARCHAR(100) NOT NULL,
    Email     VARCHAR(150),
    Phone     VARCHAR(20),
    CreatedAt DATETIME     DEFAULT GETDATE()
);

-- ─── TABLE 4 : EventTickets (FK → all three tables) ──
CREATE TABLE EventTickets (
    TicketID      INT         PRIMARY KEY IDENTITY(1001,1),
    EventID       INT         NOT NULL,
    UserID        INT         NOT NULL,
    CategoryID    INT         NOT NULL,
    SeatNo        VARCHAR(10) NOT NULL,
    BookingDate   DATE        NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    PaymentStatus VARCHAR(20) NOT NULL DEFAULT 'Pending',
    CONSTRAINT FK_Ticket_Event    FOREIGN KEY (EventID)    REFERENCES Events(EventID),
    CONSTRAINT FK_Ticket_User     FOREIGN KEY (UserID)     REFERENCES Users(UserID),
    CONSTRAINT FK_Ticket_Category FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- ─── SEED DATA ────────────────────────────────────────

INSERT INTO Categories (CategoryName, Price) VALUES
('VIP',     5000.00),
('Regular', 3000.00),
('Economy', 1500.00);

INSERT INTO Events (EventName, EventDate, Location, TotalSeats) VALUES
('Rock Concert',          '2026-05-10', 'Lahore Arena',                   200),
('Jazz Night',            '2026-05-20', 'Karachi Arts Centre',            150),
('Tech Seminar',          '2026-06-01', 'Islamabad Convention Centre',    300),
('Football Match',        '2026-06-15', 'National Stadium Karachi',       500),
('Classical Symphony',    '2026-07-04', 'Alhamra Hall Lahore',            180);

INSERT INTO Users (UserName, Email, Phone) VALUES
('Ali Khan',    'ali@example.com',   '0311-1234567'),
('Sara Ahmed',  'sara@example.com',  '0321-7654321'),
('Usman Ali',   'usman@example.com', '0333-9988776'),
('Fatima Noor', 'fatima@example.com','0300-1122334');

INSERT INTO EventTickets (EventID, UserID, CategoryID, SeatNo, BookingDate, PaymentStatus) VALUES
(1, 1, 1, 'A1',  '2026-03-20', 'Paid'),
(1, 2, 2, 'C3',  '2026-03-21', 'Pending'),
(2, 3, 3, 'G5',  '2026-03-22', 'Paid'),
(3, 4, 1, 'A2',  '2026-03-23', 'Paid'),
(4, 1, 2, 'D7',  '2026-03-24', 'Pending');

-- ─── SAMPLE QUERIES (matches assignment PDF) ──────────

-- Q1: View all tickets with full details (JOIN across 4 tables)
SELECT
    t.TicketID,
    e.EventName,
    u.UserName,
    c.CategoryName,
    c.Price,
    t.SeatNo,
    t.BookingDate,
    e.EventDate,
    e.Location,
    t.PaymentStatus
FROM EventTickets t
JOIN Events     e ON t.EventID    = e.EventID
JOIN Users      u ON t.UserID     = u.UserID
JOIN Categories c ON t.CategoryID = c.CategoryID
ORDER BY t.TicketID;

-- Q2: Check booked seats for a specific event
SELECT SeatNo
FROM EventTickets t
JOIN Events e ON t.EventID = e.EventID
WHERE e.EventName = 'Rock Concert';

-- Q3: Filter Paid tickets only
SELECT t.TicketID, e.EventName, u.UserName, t.PaymentStatus
FROM EventTickets t
JOIN Events e ON t.EventID = e.EventID
JOIN Users  u ON t.UserID  = u.UserID
WHERE t.PaymentStatus = 'Paid';

-- Q4: Update payment status
UPDATE EventTickets
SET PaymentStatus = 'Paid'
WHERE TicketID = 1002;

-- Q5: Delete a ticket
DELETE FROM EventTickets WHERE TicketID = 1005;

-- Q6: Sort tickets by price descending
SELECT
    t.TicketID,
    e.EventName,
    u.UserName,
    c.CategoryName,
    c.Price
FROM EventTickets t
JOIN Events     e ON t.EventID    = e.EventID
JOIN Users      u ON t.UserID     = u.UserID
JOIN Categories c ON t.CategoryID = c.CategoryID
ORDER BY c.Price DESC;

-- Q7: Count tickets per event
SELECT e.EventName, COUNT(t.TicketID) AS TotalBookings
FROM Events e
LEFT JOIN EventTickets t ON e.EventID = t.EventID
GROUP BY e.EventName
ORDER BY TotalBookings DESC;

-- Q8: Total revenue (paid only)
SELECT SUM(c.Price) AS TotalRevenue
FROM EventTickets t
JOIN Categories c ON t.CategoryID = c.CategoryID
WHERE t.PaymentStatus = 'Paid';

-- Q9: Seats remaining per event
SELECT
    e.EventName,
    e.TotalSeats,
    COUNT(t.TicketID)              AS BookedSeats,
    e.TotalSeats - COUNT(t.TicketID) AS RemainingSeats
FROM Events e
LEFT JOIN EventTickets t ON e.EventID = t.EventID
GROUP BY e.EventName, e.TotalSeats;

-- Q10: Users with more than one booking
SELECT u.UserName, COUNT(t.TicketID) AS TotalBookings
FROM Users u
JOIN EventTickets t ON u.UserID = t.UserID
GROUP BY u.UserName
HAVING COUNT(t.TicketID) > 1;
