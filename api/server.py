from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client
import os

app = Flask(__name__, template_folder="../templates")
CORS(app)

# ENV (set in Vercel)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────
# HOME
# ─────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

# ─────────────────────────────
# EVENTS
# ─────────────────────────────
@app.route("/api/events", methods=["GET"])
def get_events():
    res = supabase.table("Events").select("*").execute()

    events = []
    for r in res.data:
        events.append({
            "id": r["EventID"],
            "name": r["EventName"],
            "date": r["EventDate"],
            "location": r["Location"],
            "seats": r["TotalSeats"]
        })

    return jsonify(events)

# ─────────────────────────────
# USERS
# ─────────────────────────────
@app.route("/api/users", methods=["POST"])
def add_user():
    d = request.json

    res = supabase.table("Users").insert({
        "UserName": d["userName"],
        "Email": d.get("email"),
        "Phone": d.get("phone")
    }).execute()

    return jsonify({"message": "User created"})

# ─────────────────────────────
# BOOK TICKET (MAIN LOGIC)
# ─────────────────────────────
@app.route("/api/tickets", methods=["POST"])
def book_ticket():
    d = request.json

    # 1. check seat
    seat_check = supabase.table("EventTickets").select("*")\
        .eq("EventID", d["eventId"])\
        .eq("SeatNo", d["seatNo"]).execute()

    if seat_check.data:
        return jsonify({"error": "Seat already booked"}), 409

    # 2. insert ticket
    ticket = supabase.table("EventTickets").insert({
        "EventID": d["eventId"],
        "UserID": d["userId"],
        "CategoryID": d["categoryId"],
        "SeatNo": d["seatNo"],
        "PaymentStatus": "Paid"
    }).execute()

    return jsonify({"message": "Ticket booked"})

# ─────────────────────────────
# GET TICKETS
# ─────────────────────────────
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    res = supabase.table("EventTickets").select("*").execute()
    return jsonify(res.data)

# ─────────────────────────────
# BOOKED SEATS
# ─────────────────────────────
@app.route("/api/tickets/booked-seats/<int:eid>", methods=["GET"])
def booked_seats(eid):
    res = supabase.table("EventTickets").select("SeatNo")\
        .eq("EventID", eid).execute()

    seats = [r["SeatNo"] for r in res.data]
    return jsonify(seats)