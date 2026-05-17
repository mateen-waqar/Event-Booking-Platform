from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
import os

# Load local .env file
load_dotenv()

# Dynamic template path (works on localhost + Vercel)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Works for both: Vercel (api/server.py) and localhost (python api/server.py or python server.py)
template_dir = os.path.join(BASE_DIR, "../templates")
if not os.path.exists(template_dir):
    template_dir = os.path.join(BASE_DIR, "templates")

# Flask app
app = Flask(__name__, template_folder=template_dir)
CORS(app)

# Environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Safety check
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
# STATS
# ─────────────────────────────
@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        total    = len(supabase.table("EventTickets").select("TicketID").execute().data)
        paid     = len(supabase.table("EventTickets").select("TicketID").eq("PaymentStatus", "Paid").execute().data)
        events   = len(supabase.table("Events").select("EventID").execute().data)
        waitlist = len(supabase.table("Waitlist").select("WaitlistID").execute().data)
        cats     = len(supabase.table("Categories").select("CategoryID").execute().data)

        pay_rows = supabase.table("Payments").select("Amount").execute().data
        revenue  = sum(float(r.get("Amount") or 0) for r in pay_rows)

        return jsonify({
            "total": total,
            "paid": paid,
            "events": events,
            "waitlist": waitlist,
            "categories": cats,
            "revenue": revenue
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# EVENTS
# ─────────────────────────────
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        res = supabase.table("Events") \
            .select("*, Venues(VenueName, City), Organizers(OrganizerName)") \
            .execute()
        events = []
        for r in res.data:
            venue = r.get("Venues") or {}
            org   = r.get("Organizers") or {}
            events.append({
                "id":        r.get("EventID"),
                "name":      r.get("EventName"),
                "date":      r.get("EventDate"),
                "venue":     venue.get("VenueName"),
                "city":      venue.get("City"),
                "location":  venue.get("VenueName"),
                "organizer": org.get("OrganizerName"),
                "seats":     r.get("TotalSeats"),
                "eventType": r.get("EventType")
            })
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events", methods=["POST"])
def add_event():
    try:
        d = request.json
        supabase.table("Events").insert({
            "EventName":   d["eventName"],
            "EventDate":   d.get("eventDate"),
            "EventType":   d.get("eventType"),
            "VenueID":     d.get("venueId"),
            "OrganizerID": d.get("organizerId"),
            "TotalSeats":  d.get("totalSeats")
        }).execute()
        return jsonify({"message": "Event created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events/<int:eid>", methods=["DELETE"])
def delete_event(eid):
    try:
        supabase.table("Events").delete().eq("EventID", eid).execute()
        return jsonify({"message": "Event deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# USERS
# ─────────────────────────────
@app.route("/api/users", methods=["GET"])
def get_users():
    try:
        res = supabase.table("Users").select("*").execute()
        users = []
        for r in res.data:
            users.append({
                "id":        r.get("UserID"),
                "name":      r.get("UserName"),
                "email":     r.get("Email"),
                "phone":     r.get("Phone"),
                "cnic":      r.get("CNIC"),
                "createdAt": r.get("CreatedAt")
            })
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users", methods=["POST"])
def add_user():
    try:
        d = request.json
        supabase.table("Users").insert({
            "UserName": d["userName"],
            "Email":    d.get("email"),
            "Phone":    d.get("phone"),
            "CNIC":     d.get("cnic")
        }).execute()
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# VENUES
# ─────────────────────────────
@app.route("/api/venues", methods=["GET"])
def get_venues():
    try:
        res = supabase.table("Venues").select("*").execute()
        venues = []
        for r in res.data:
            venues.append({
                "id":       r.get("VenueID"),
                "name":     r.get("VenueName"),
                "city":     r.get("City"),
                "address":  r.get("Address"),
                "capacity": r.get("Capacity")
            })
        return jsonify(venues)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/venues", methods=["POST"])
def add_venue():
    try:
        d = request.json
        supabase.table("Venues").insert({
            "VenueName": d["venueName"],
            "City":      d.get("city"),
            "Address":   d.get("address"),
            "Capacity":  d.get("capacity")
        }).execute()
        return jsonify({"message": "Venue created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/venues/<int:vid>", methods=["DELETE"])
def delete_venue(vid):
    try:
        supabase.table("Venues").delete().eq("VenueID", vid).execute()
        return jsonify({"message": "Venue deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# ORGANIZERS
# ─────────────────────────────
@app.route("/api/organizers", methods=["GET"])
def get_organizers():
    try:
        res = supabase.table("Organizers").select("*").execute()
        orgs = []
        for r in res.data:
            orgs.append({
                "id":           r.get("OrganizerID"),
                "name":         r.get("OrganizerName"),
                "email":        r.get("ContactEmail"),
                "phone":        r.get("Phone"),
                "organization": r.get("Organization")
            })
        return jsonify(orgs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/organizers", methods=["POST"])
def add_organizer():
    try:
        d = request.json
        supabase.table("Organizers").insert({
            "OrganizerName": d["organizerName"],
            "ContactEmail":  d.get("contactEmail"),
            "Phone":         d.get("phone"),
            "Organization":  d.get("organization")
        }).execute()
        return jsonify({"message": "Organizer created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/organizers/<int:oid>", methods=["DELETE"])
def delete_organizer(oid):
    try:
        supabase.table("Organizers").delete().eq("OrganizerID", oid).execute()
        return jsonify({"message": "Organizer deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# STAFF
# ─────────────────────────────
@app.route("/api/staff", methods=["GET"])
def get_staff():
    try:
        res = supabase.table("Staff").select("*").execute()
        staff = []
        for r in res.data:
            staff.append({
                "id":        r.get("StaffID"),
                "name":      r.get("StaffName"),
                "role":      r.get("Role"),
                "shiftTime": r.get("ShiftTime"),
                "phone":     r.get("Phone"),
                "email":     r.get("Email"),
                "hireDate":  r.get("HireDate")
            })
        return jsonify(staff)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/staff", methods=["POST"])
def add_staff():
    try:
        d = request.json
        supabase.table("Staff").insert({
            "StaffName": d["staffName"],
            "Role":      d.get("role"),
            "ShiftTime": d.get("shiftTime"),
            "Phone":     d.get("phone"),
            "Email":     d.get("email"),
            "HireDate":  d.get("hireDate")
        }).execute()
        return jsonify({"message": "Staff created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/staff/<int:sid>", methods=["DELETE"])
def delete_staff(sid):
    try:
        supabase.table("Staff").delete().eq("StaffID", sid).execute()
        return jsonify({"message": "Staff deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# CATEGORIES
# ─────────────────────────────
@app.route("/api/categories", methods=["GET"])
def get_categories():
    try:
        res = supabase.table("Categories").select("*").execute()
        cats = []
        for r in res.data:
            cats.append({
                "id":    r.get("CategoryID"),
                "name":  r.get("CategoryName"),
                "price": r.get("Price")
            })
        return jsonify(cats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["POST"])
def add_category():
    try:
        d = request.json
        supabase.table("Categories").insert({
            "CategoryName": d["categoryName"],
            "Price":        d.get("price")
        }).execute()
        return jsonify({"message": "Category created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories/<int:cid>", methods=["DELETE"])
def delete_category(cid):
    try:
        supabase.table("Categories").delete().eq("CategoryID", cid).execute()
        return jsonify({"message": "Category deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# DISCOUNTS
# ─────────────────────────────
@app.route("/api/discounts", methods=["GET"])
def get_discounts():
    try:
        res = supabase.table("Discounts").select("*").execute()
        discounts = []
        for r in res.data:
            discounts.append({
                "id":          r.get("DiscountID"),
                "code":        r.get("Code"),
                "description": r.get("Description"),
                "percentage":  r.get("Percentage"),
                "validFrom":   r.get("ValidFrom"),
                "validUntil":  r.get("ValidUntil"),
                "isActive":    bool(r.get("IsActive"))
            })
        return jsonify(discounts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/discounts", methods=["POST"])
def add_discount():
    try:
        d = request.json
        supabase.table("Discounts").insert({
            "Code":        d["code"],
            "Description": d.get("description"),
            "Percentage":  d.get("percentage"),
            "ValidFrom":   d.get("validFrom"),
            "ValidUntil":  d.get("validUntil"),
            "IsActive":    d.get("isActive", 1)
        }).execute()
        return jsonify({"message": "Discount created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/discounts/<int:did>", methods=["DELETE"])
def delete_discount(did):
    try:
        supabase.table("Discounts").delete().eq("DiscountID", did).execute()
        return jsonify({"message": "Discount deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# TICKETS
# ─────────────────────────────
@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    try:
        res = supabase.table("EventTickets") \
            .select("*, Events(EventName, EventDate, Venues(VenueName)), Users(UserName), Categories(CategoryName, Price), Staff(StaffName), Discounts(Code)") \
            .execute()
        tickets = []
        for r in res.data:
            ev   = r.get("Events")      or {}
            usr  = r.get("Users")       or {}
            cat  = r.get("Categories")  or {}
            stf  = r.get("Staff")       or {}
            disc = r.get("Discounts")   or {}
            venue = ev.get("Venues")    or {}
            tickets.append({
                "ticketId":  r.get("TicketID"),
                "event":     ev.get("EventName"),
                "eventDate": ev.get("EventDate"),
                "location":  venue.get("VenueName"),
                "user":      usr.get("UserName"),
                "category":  cat.get("CategoryName"),
                "price":     cat.get("Price", 0),
                "discount":  disc.get("Code"),
                "seat":      r.get("SeatNo"),
                "booked":    r.get("BookingDate"),
                "staff":     stf.get("StaffName"),
                "status":    r.get("PaymentStatus")
            })
        return jsonify(tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tickets", methods=["POST"])
def book_ticket():
    try:
        d = request.json

        # Check seat not already taken
        seat_check = supabase.table("EventTickets").select("*") \
            .eq("EventID", d["eventId"]) \
            .eq("SeatNo", d["seatNo"]).execute()
        if seat_check.data:
            return jsonify({"error": "Seat already booked"}), 409

        # Insert ticket
        result = supabase.table("EventTickets").insert({
            "EventID":       d["eventId"],
            "UserID":        d["userId"],
            "CategoryID":    d["categoryId"],
            "StaffID":       d.get("staffId"),
            "DiscountID":    d.get("discountId"),
            "SeatNo":        d["seatNo"],
            "PaymentStatus": "Paid"
        }).execute()

        ticket_id = result.data[0].get("TicketID") if result.data else None

        # Auto-create payment record
        if ticket_id:
            cat = supabase.table("Categories").select("Price") \
                .eq("CategoryID", d["categoryId"]).execute()
            price = cat.data[0].get("Price", 0) if cat.data else 0
            supabase.table("Payments").insert({
                "TicketID":       ticket_id,
                "Amount":         price,
                "PaymentMethod":  d.get("paymentMethod", "Cash"),
                "Status":         "Paid",
                "TransactionRef": d.get("transactionRef")
            }).execute()

        return jsonify({"message": "Ticket booked"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tickets/<int:tid>", methods=["PATCH"])
def update_ticket(tid):
    try:
        d = request.json
        supabase.table("EventTickets").update({
            "PaymentStatus": d.get("paymentStatus")
        }).eq("TicketID", tid).execute()
        return jsonify({"message": "Ticket updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tickets/<int:tid>", methods=["DELETE"])
def delete_ticket(tid):
    try:
        supabase.table("EventTickets").delete().eq("TicketID", tid).execute()
        return jsonify({"message": "Ticket deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tickets/booked-seats/<int:eid>", methods=["GET"])
def booked_seats(eid):
    try:
        res = supabase.table("EventTickets").select("SeatNo") \
            .eq("EventID", eid).execute()
        seats = [r["SeatNo"] for r in res.data]
        return jsonify(seats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# WAITLIST
# ─────────────────────────────
@app.route("/api/waitlist", methods=["GET"])
def get_waitlist():
    try:
        res = supabase.table("Waitlist") \
            .select("*, Events(EventName), Users(UserName), Categories(CategoryName)") \
            .execute()
        waitlist = []
        for r in res.data:
            ev  = r.get("Events")      or {}
            usr = r.get("Users")       or {}
            cat = r.get("Categories")  or {}
            waitlist.append({
                "waitlistId":  r.get("WaitlistID"),
                "event":       ev.get("EventName"),
                "user":        usr.get("UserName"),
                "category":    cat.get("CategoryName"),
                "requestDate": r.get("RequestDate"),
                "status":      r.get("Status")
            })
        return jsonify(waitlist)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/waitlist", methods=["POST"])
def add_waitlist():
    try:
        d = request.json
        supabase.table("Waitlist").insert({
            "EventID":     d["eventId"],
            "UserID":      d["userId"],
            "CategoryID":  d["categoryId"],
            "RequestDate": d.get("requestDate"),
            "Status":      d.get("status", "Waiting")
        }).execute()
        return jsonify({"message": "Added to waitlist"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/waitlist/<int:wid>", methods=["DELETE"])
def delete_waitlist(wid):
    try:
        supabase.table("Waitlist").delete().eq("WaitlistID", wid).execute()
        return jsonify({"message": "Removed from waitlist"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# PAYMENTS
# ─────────────────────────────
@app.route("/api/payments", methods=["GET"])
def get_payments():
    try:
        res = supabase.table("Payments") \
            .select("*, EventTickets(UserID, Users(UserName))") \
            .execute()
        payments = []
        for r in res.data:
            ticket = r.get("EventTickets") or {}
            usr    = ticket.get("Users")   or {}
            payments.append({
                "paymentId":       r.get("PaymentID"),
                "ticketId":        r.get("TicketID"),
                "user":            usr.get("UserName"),
                "amount":          r.get("Amount"),
                "method":          r.get("PaymentMethod"),
                "transactionDate": r.get("TransactionDate"),
                "transactionRef":  r.get("TransactionRef"),
                "status":          r.get("Status")
            })
        return jsonify(payments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────
# CANCELLATIONS
# ─────────────────────────────
@app.route("/api/cancellations", methods=["GET"])
def get_cancellations():
    try:
        res = supabase.table("Cancellations") \
            .select("*, EventTickets(UserID, EventID, Users(UserName), Events(EventName)), Staff(StaffName)") \
            .execute()
        cancellations = []
        for r in res.data:
            ticket = r.get("EventTickets") or {}
            usr    = ticket.get("Users")   or {}
            ev     = ticket.get("Events")  or {}
            stf    = r.get("Staff")        or {}
            cancellations.append({
                "cancellationId": r.get("CancellationID"),
                "ticketId":       r.get("TicketID"),
                "user":           usr.get("UserName"),
                "event":          ev.get("EventName"),
                "reason":         r.get("Reason"),
                "cancelDate":     r.get("CancelDate"),
                "refundStatus":   r.get("RefundStatus"),
                "refundAmount":   r.get("RefundAmount"),
                "processedBy":    stf.get("StaffName")
            })
        return jsonify(cancellations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cancellations", methods=["POST"])
def add_cancellation():
    try:
        d = request.json
        supabase.table("Cancellations").insert({
            "TicketID":     d["ticketId"],
            "Reason":       d.get("reason"),
            "CancelDate":   d.get("cancelDate"),
            "RefundStatus": d.get("refundStatus"),
            "RefundAmount": d.get("refundAmount", 0),
            "ProcessedBy":  d.get("processedBy")
        }).execute()
        return jsonify({"message": "Cancellation recorded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(debug=True)
    