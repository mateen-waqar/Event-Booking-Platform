from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client
import os

# IMPORTANT: correct template path for Vercel
app = Flask(__name__, template_folder="../templates")
CORS(app)

# ENV VARIABLES (from Vercel)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Safety check (prevents crash)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase ENV variables missing")

# Supabase client
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
    try:
        res = supabase.table("Events").select("*").execute()

        events = []
        for r in res.data:
            events.append({
                "id": r.get("EventID"),
                "name": r.get("EventName"),
                "date": r.get("EventDate"),
                "location": r.get("Location"),
                "seats": r.get("TotalSeats")
            })

        return jsonify(events)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────
# USERS
# ─────────────────────────────
@app.route("/api/users", methods=["POST"])
def add_user():
    try:
        d = request.json

        supabase.table("Users").insert({
            "UserName": d["userName"],
            "Email": d.get("email"),
            "Phone": d.get("phone")
        }).execute()

        return jsonify({"message": "User created"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────
# BOOK TICKET
# ─────────────────────────────
@app.route("/api/tickets", methods=["POST"])
def book_ticket():
    try:
        d = request.json

        # Check seat
        seat_check = supabase.table("EventTickets").select("*") \
            .eq("EventID", d["eventId"]) \
            .eq("SeatNo", d["seatNo"]).execute()

        if seat_check.data:
            return jsonify({"error": "Seat already booked"}), 409

        # Insert ticket
        supabase.table("EventTickets").insert({
            "EventID": d["eventId"],
            "UserID": d["userId"],
            "CategoryID": d["categoryId"],
            "SeatNo": d["seatNo"],
            "PaymentStatus": "Paid"
        }).execute()

        return jsonify({"message": "Ticket booked"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────
# GET TICKETS
# ─────────────────────────────
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    try:
        res = supabase.table("EventTickets").select("*").execute()
        return jsonify(res.data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────
# BOOKED SEATS
# ─────────────────────────────
@app.route("/api/tickets/booked-seats/<int:eid>", methods=["GET"])
def booked_seats(eid):
    try:
        res = supabase.table("EventTickets").select("SeatNo") \
            .eq("EventID", eid).execute()

        seats = [r["SeatNo"] for r in res.data]
        return jsonify(seats)

    except Exception as e:
        return jsonify({"error": str(e)}), 500