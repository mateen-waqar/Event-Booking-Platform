from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pyodbc
import traceback

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
#  HOME ROUTE
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

# ─────────────────────────────────────────────
#  MS SQL SERVER CONNECTION  –  update these!
# ─────────────────────────────────────────────
SERVER   = "localhost"             # e.g. localhost\SQLEXPRESS  or  127.0.0.1
DATABASE = "TicketBookingDB"

# Use Windows Authentication (Trusted Connection)
CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# Connection to master database for initial setup
MASTER_CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE=master;"
    f"Trusted_Connection=yes;"
)


def get_conn():
    return pyodbc.connect(CONN_STR)


def get_master_conn():
    conn = pyodbc.connect(MASTER_CONN_STR, autocommit=True)
    return conn


# ─────────────────────────────────────────────
#  DATABASE INITIALISATION  (run once)
# ─────────────────────────────────────────────
def init_db():
    """Create database, tables and seed data if they don't exist."""
    # First create the database if it doesn't exist
    try:
        master_conn = get_master_conn()
        master_cur = master_conn.cursor()
        master_cur.execute(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{DATABASE}') CREATE DATABASE {DATABASE}")
        master_conn.commit()
        master_cur.close()
        master_conn.close()
        print("✅  Database created.")
    except Exception as e:
        print(f"⚠️  Could not create database: {e}")
    
    # Now connect to the actual database and create tables
    conn = get_conn()
    cur  = conn.cursor()

    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Categories')
    CREATE TABLE Categories (
        CategoryID   INT PRIMARY KEY IDENTITY(1,1),
        CategoryName VARCHAR(20)  NOT NULL,
        Price        DECIMAL(10,2) NOT NULL
    )""")

    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Events')
    CREATE TABLE Events (
        EventID      INT PRIMARY KEY IDENTITY(1,1),
        EventName    VARCHAR(100) NOT NULL,
        EventDate    DATE         NOT NULL,
        Location     VARCHAR(200) NOT NULL,
        TotalSeats   INT          NOT NULL DEFAULT 100
    )""")

    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Users')
    CREATE TABLE Users (
        UserID       INT PRIMARY KEY IDENTITY(1,1),
        UserName     VARCHAR(100) NOT NULL,
        Email        VARCHAR(150),
        Phone        VARCHAR(20),
        CreatedAt    DATETIME     DEFAULT GETDATE()
    )""")

    cur.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='EventTickets')
    CREATE TABLE EventTickets (
        TicketID      INT PRIMARY KEY IDENTITY(1001,1),
        EventID       INT NOT NULL,
        UserID        INT NOT NULL,
        CategoryID    INT NOT NULL,
        SeatNo        VARCHAR(10)  NOT NULL,
        BookingDate   DATE         NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        PaymentStatus VARCHAR(20)  NOT NULL DEFAULT 'Pending',
        FOREIGN KEY (EventID)    REFERENCES Events(EventID),
        FOREIGN KEY (UserID)     REFERENCES Users(UserID),
        FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
    )""")

    # Seed Categories
    cur.execute("IF NOT EXISTS (SELECT 1 FROM Categories) BEGIN "
                "INSERT INTO Categories(CategoryName,Price) VALUES "
                "('VIP',5000),('Regular',3000),('Economy',1500) END")

    # Seed Events
    cur.execute("IF NOT EXISTS (SELECT 1 FROM Events) BEGIN "
                "INSERT INTO Events(EventName,EventDate,Location,TotalSeats) VALUES "
                "('Rock Concert','2026-05-10','Lahore Arena',200),"
                "('Jazz Night','2026-05-20','Karachi Arts Centre',150),"
                "('Tech Seminar','2026-06-01','Islamabad Convention Centre',300),"
                "('Football Match','2026-06-15','National Stadium Karachi',500),"
                "('Classical Symphony','2026-07-04','Alhamra Hall Lahore',180) END")

    conn.commit()
    cur.close()
    conn.close()
    print("✅  Database initialised.")


# ══════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════
@app.route("/api/categories", methods=["GET"])
def get_categories():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT CategoryID, CategoryName, Price FROM Categories ORDER BY Price DESC")
    rows = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)


# ══════════════════════════════════════════════
#  EVENTS
# ══════════════════════════════════════════════
@app.route("/api/events", methods=["GET"])
def get_events():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT EventID, EventName, EventDate, Location, TotalSeats FROM Events ORDER BY EventDate")
    rows = [{"id": r[0], "name": r[1],
             "date": str(r[2]), "location": r[3], "seats": r[4]}
            for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/api/events", methods=["POST"])
def add_event():
    d = request.json
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO Events(EventName,EventDate,Location,TotalSeats) VALUES(?,?,?,?)",
        d["eventName"], d["eventDate"], d["location"], d.get("totalSeats", 100)
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Event created"}), 201

@app.route("/api/events/<int:eid>", methods=["DELETE"])
def delete_event(eid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM Events WHERE EventID=?", eid)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Deleted"})


# ══════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════
@app.route("/api/users", methods=["GET"])
def get_users():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT UserID, UserName, Email, Phone FROM Users ORDER BY UserID")
    rows = [{"id": r[0], "name": r[1], "email": r[2] or "", "phone": r[3] or ""}
            for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/api/users", methods=["POST"])
def add_user():
    d = request.json
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        "INSERT INTO Users(UserName,Email,Phone) VALUES(?,?,?)",
        d["userName"], d.get("email", ""), d.get("phone", "")
    )
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "User created"}), 201


# ══════════════════════════════════════════════
#  TICKETS  (main table – most queries here)
# ══════════════════════════════════════════════
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT t.TicketID, e.EventName, u.UserName, c.CategoryName,
               c.Price, t.SeatNo, t.BookingDate, e.EventDate,
               e.Location, t.PaymentStatus
        FROM EventTickets t
        JOIN Events      e ON t.EventID    = e.EventID
        JOIN Users       u ON t.UserID     = u.UserID
        JOIN Categories  c ON t.CategoryID = c.CategoryID
        ORDER BY t.TicketID DESC
    """)
    cols = ["ticketId","event","user","category","price",
            "seat","booked","eventDate","location","status"]
    rows = []
    for r in cur.fetchall():
        row = dict(zip(cols, r))
        row["price"]     = float(row["price"])
        row["booked"]    = str(row["booked"])
        row["eventDate"] = str(row["eventDate"])
        rows.append(row)
    cur.close(); conn.close()
    return jsonify(rows)

@app.route("/api/tickets", methods=["POST"])
def book_ticket():
    d = request.json
    try:
        conn = get_conn(); cur = conn.cursor()

        # Resolve or create user
        cur.execute("SELECT UserID FROM Users WHERE UserName=?", d["userName"])
        row = cur.fetchone()
        if row:
            uid = row[0]
        else:
            cur.execute("INSERT INTO Users(UserName,Email,Phone) OUTPUT INSERTED.UserID "
                        "VALUES(?,?,?)", d["userName"], d.get("email",""), d.get("phone",""))
            uid = cur.fetchone()[0]

        # Check seat not already taken for this event
        cur.execute("SELECT 1 FROM EventTickets WHERE EventID=? AND SeatNo=?",
                    d["eventId"], d["seatNo"])
        if cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "Seat already booked"}), 409

        cur.execute(
            "INSERT INTO EventTickets(EventID,UserID,CategoryID,SeatNo,BookingDate,PaymentStatus) "
            "VALUES(?,?,?,?,?,?)",
            d["eventId"], uid, d["categoryId"], d["seatNo"],
            d.get("bookingDate", "2026-04-28"), d.get("paymentStatus", "Pending")
        )
        conn.commit(); cur.close(); conn.close()
        return jsonify({"message": "Ticket booked!"}), 201
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Booking failed"}), 500

@app.route("/api/tickets/<int:tid>", methods=["PATCH"])
def update_payment(tid):
    d = request.json
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE EventTickets SET PaymentStatus=? WHERE TicketID=?",
                d["paymentStatus"], tid)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Updated"})

@app.route("/api/tickets/<int:tid>", methods=["DELETE"])
def delete_ticket(tid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM EventTickets WHERE TicketID=?", tid)
    conn.commit(); cur.close(); conn.close()
    return jsonify({"message": "Deleted"})

# Booked seats for a specific event (seat-map)
@app.route("/api/tickets/booked-seats/<int:eid>", methods=["GET"])
def booked_seats(eid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT SeatNo FROM EventTickets WHERE EventID=?", eid)
    seats = [r[0] for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(seats)

# Stats summary
@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM EventTickets")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM EventTickets WHERE PaymentStatus='Paid'")
    paid = cur.fetchone()[0]
    cur.execute("SELECT ISNULL(SUM(c.Price),0) FROM EventTickets t "
                "JOIN Categories c ON t.CategoryID=c.CategoryID WHERE t.PaymentStatus='Paid'")
    revenue = float(cur.fetchone()[0])
    cur.execute("SELECT COUNT(*) FROM Events")
    events = cur.fetchone()[0]
    cur.close(); conn.close()
    return jsonify({"total": total, "paid": paid, "revenue": revenue, "events": events})


# ══════════════════════════════════════════════
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
