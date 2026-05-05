-- ═══════════════════════════════════════════════════════
--   TicketVault DB · ERD MATCHED VERSION (11 TABLES)
-- ═══════════════════════════════════════════════════════

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TicketBookingDB')
    CREATE DATABASE TicketBookingDB;

USE TicketBookingDB;

-- ═══════════════════════════════════════════════════════
-- ORGANIZERS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Organizers (
    OrganizerID INT IDENTITY PRIMARY KEY,
    OrganizerName VARCHAR(100),
    ContactEmail VARCHAR(100),
    Phone VARCHAR(15),
    Organization VARCHAR(100)
);

-- ═══════════════════════════════════════════════════════
-- VENUES
-- ═══════════════════════════════════════════════════════
CREATE TABLE Venues (
    VenueID INT IDENTITY PRIMARY KEY,
    VenueName VARCHAR(100),
    City VARCHAR(50),
    Address VARCHAR(150),
    Capacity INT CHECK (Capacity > 0)
);

-- ═══════════════════════════════════════════════════════
-- USERS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Users (
    UserID INT IDENTITY PRIMARY KEY,
    UserName VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15),
    CNIC VARCHAR(15) UNIQUE,
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- ═══════════════════════════════════════════════════════
-- STAFF
-- ═══════════════════════════════════════════════════════
CREATE TABLE Staff (
    StaffID INT IDENTITY PRIMARY KEY,
    StaffName VARCHAR(100),
    Role VARCHAR(50),
    ShiftTime VARCHAR(50),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    HireDate DATE
);

-- ═══════════════════════════════════════════════════════
-- EVENTS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Events (
    EventID INT IDENTITY PRIMARY KEY,
    EventName VARCHAR(100),
    EventDate DATE,
    VenueID INT,
    OrganizerID INT,
    TotalSeats INT CHECK (TotalSeats > 0),
    EventType VARCHAR(50),

    FOREIGN KEY (VenueID) REFERENCES Venues(VenueID),
    FOREIGN KEY (OrganizerID) REFERENCES Organizers(OrganizerID)
);

-- ═══════════════════════════════════════════════════════
-- CATEGORIES
-- ═══════════════════════════════════════════════════════
CREATE TABLE Categories (
    CategoryID INT IDENTITY PRIMARY KEY,
    CategoryName VARCHAR(50),
    Price DECIMAL(10,2)
);

-- ═══════════════════════════════════════════════════════
-- DISCOUNTS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Discounts (
    DiscountID INT IDENTITY PRIMARY KEY,
    Code VARCHAR(20),
    Description VARCHAR(100),
    Percentage DECIMAL(5,2),
    ValidFrom DATE,
    ValidUntil DATE,
    IsActive BIT,

    CHECK (ValidUntil >= ValidFrom)
);

-- ═══════════════════════════════════════════════════════
-- EVENT TICKETS
-- ═══════════════════════════════════════════════════════
CREATE TABLE EventTickets (
    TicketID INT IDENTITY PRIMARY KEY,
    EventID INT,
    UserID INT,
    CategoryID INT,
    StaffID INT,
    DiscountID INT,
    SeatNo VARCHAR(10),
    BookingDate DATE DEFAULT GETDATE(),
    PaymentStatus VARCHAR(20),

    FOREIGN KEY (EventID) REFERENCES Events(EventID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    FOREIGN KEY (DiscountID) REFERENCES Discounts(DiscountID),

    CONSTRAINT UQ_Seat UNIQUE (EventID, SeatNo)
);

-- ═══════════════════════════════════════════════════════
-- WAITLIST
-- ═══════════════════════════════════════════════════════
CREATE TABLE Waitlist (
    WaitlistID INT IDENTITY PRIMARY KEY,
    EventID INT,
    UserID INT,
    CategoryID INT,
    RequestDate DATE DEFAULT GETDATE(),
    Status VARCHAR(20),

    FOREIGN KEY (EventID) REFERENCES Events(EventID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),

    CHECK (Status IN ('Waiting','Confirmed','Cancelled'))
);

-- ═══════════════════════════════════════════════════════
-- PAYMENTS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Payments (
    PaymentID INT IDENTITY PRIMARY KEY,
    TicketID INT UNIQUE,
    Amount DECIMAL(10,2),
    PaymentMethod VARCHAR(20),
    TransactionDate DATETIME DEFAULT GETDATE(),
    Status VARCHAR(20),
    TransactionRef VARCHAR(50),

    FOREIGN KEY (TicketID) REFERENCES EventTickets(TicketID)
);

-- ═══════════════════════════════════════════════════════
-- CANCELLATIONS
-- ═══════════════════════════════════════════════════════
CREATE TABLE Cancellations (
    CancellationID INT IDENTITY PRIMARY KEY,
    TicketID INT,
    Reason VARCHAR(100),
    CancelDate DATE DEFAULT GETDATE(),
    RefundStatus VARCHAR(20),
    RefundAmount DECIMAL(10,2),
    ProcessedBy INT,

    FOREIGN KEY (TicketID) REFERENCES EventTickets(TicketID),
    FOREIGN KEY (ProcessedBy) REFERENCES Staff(StaffID)
);

-- ═══════════════════════════════════════════════════════
-- STORED PROCEDURE (UPDATED)
-- ═══════════════════════════════════════════════════════
GO
CREATE PROCEDURE BookTicket
    @UserID INT,
    @EventID INT,
    @CategoryID INT,
    @SeatNo VARCHAR(10),
    @PaymentMethod VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @Price DECIMAL(10,2);
    DECLARE @TicketID INT;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Seat check
        IF EXISTS (SELECT 1 FROM EventTickets WHERE EventID=@EventID AND SeatNo=@SeatNo)
        BEGIN
            RAISERROR('Seat already booked',16,1);
            ROLLBACK; RETURN;
        END

        -- Get price from category
        SELECT @Price = Price FROM Categories WHERE CategoryID=@CategoryID;

        -- Insert ticket
        INSERT INTO EventTickets(EventID,UserID,CategoryID,SeatNo,PaymentStatus)
        VALUES(@EventID,@UserID,@CategoryID,@SeatNo,'Paid');

        SET @TicketID = SCOPE_IDENTITY();

        -- Payment
        INSERT INTO Payments(TicketID,Amount,PaymentMethod,Status)
        VALUES(@TicketID,@Price,@PaymentMethod,'Paid');

        COMMIT;
    END TRY
    BEGIN CATCH
        ROLLBACK;
        PRINT ERROR_MESSAGE();
    END CATCH
END;
GO

-- ═══════════════════════════════════════════════════════
-- TRIGGER: BLOCK OVERBOOKING
-- ═══════════════════════════════════════════════════════
GO
CREATE TRIGGER trg_BlockOverbooking
ON EventTickets
AFTER INSERT
AS
BEGIN
    DECLARE @EventID INT;
    SELECT @EventID = EventID FROM inserted;

    DECLARE @Total INT = (SELECT TotalSeats FROM Events WHERE EventID=@EventID);
    DECLARE @Count INT = (SELECT COUNT(*) FROM EventTickets WHERE EventID=@EventID);

    IF @Count > @Total
    BEGIN
        RAISERROR('Event full!',16,1);
        ROLLBACK TRANSACTION;
    END
END;
GO

-- ═══════════════════════════════════════════════════════
-- TRIGGER: WAITLIST AUTO MOVE
-- ═══════════════════════════════════════════════════════
GO
CREATE TRIGGER trg_WaitlistAuto
ON EventTickets
AFTER DELETE
AS
BEGIN
    DECLARE @EventID INT;
    DECLARE @UserID INT;
    DECLARE @CategoryID INT;

    SELECT @EventID = EventID FROM deleted;

    IF (SELECT COUNT(*) FROM EventTickets WHERE EventID=@EventID)
       < (SELECT TotalSeats FROM Events WHERE EventID=@EventID)
    BEGIN
        SELECT TOP 1 @UserID=UserID,@CategoryID=CategoryID
        FROM Waitlist
        WHERE EventID=@EventID AND Status='Waiting'
        ORDER BY WaitlistID;

        IF @UserID IS NOT NULL
        BEGIN
            INSERT INTO EventTickets(EventID,UserID,CategoryID,SeatNo,PaymentStatus)
            VALUES(@EventID,@UserID,@CategoryID,CONCAT('WL',@UserID),'Pending');

            UPDATE Waitlist
            SET Status='Confirmed'
            WHERE UserID=@UserID AND EventID=@EventID;
        END
    END
END;
GO