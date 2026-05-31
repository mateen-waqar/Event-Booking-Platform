<div align="center">

# 🎟️ TicketVault

### A full-stack event ticketing & booking management platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-event--booking--platform--amber.vercel.app-0070f3?style=flat-square)](https://event-booking-platform-amber.vercel.app)
[![Python](https://img.shields.io/badge/Backend-Python%20%2F%20Flask-3572A5?style=flat-square)](https://flask.palletsprojects.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?style=flat-square)](https://supabase.com/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=flat-square)](https://vercel.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)

[🌐 Live Demo](https://event-booking-platform-amber.vercel.app) · [🐛 Report Bug](../../issues) · [✨ Request Feature](../../issues)

---

### 🔐 Demo Credentials

> Use these to log in on the live demo:

| Field | Value |
|---|---|
| **Username** | `maty` |
| **Password** | `test1234` |

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Project Structure](#project-structure)

---

## 🌟 Overview

**TicketVault** is a production-ready event booking platform that handles end-to-end ticket management — from event creation and seat allocation to payments, waitlists, and cancellations. It is deployed live on **Vercel** with a **Supabase** PostgreSQL backend.

The platform supports multiple stakeholders: **organizers** who create events, **staff** who process bookings, and **users** who reserve seats. Built-in business logic handles overbooking prevention and automatic waitlist promotion.

> 🔐 **To try the live demo**, use username `maty` and password `test1234`.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎪 **Event Management** | Create, view, and delete events with venue and organizer linkage |
| 🪑 **Seat Booking** | Real-time seat availability checks with conflict prevention |
| 👥 **User Management** | Register users with CNIC-based deduplication |
| 💳 **Payments** | Auto-generated payment records per ticket with method tracking |
| ⏳ **Waitlist** | Join waitlists; auto-promoted to booked when a seat opens |
| ❌ **Cancellations** | Cancel tickets with refund tracking and staff attribution |
| 🏷️ **Discounts** | Apply discount codes with validity periods and percentages |
| 📊 **Dashboard Stats** | Live revenue, ticket counts, and event summaries |
| 🏢 **Venue & Organizer CRUD** | Full management of venues and organizers |

---

## 🛠️ Tech Stack

**Backend**
- [Python 3](https://www.python.org/) + [Flask](https://flask.palletsprojects.com/) — REST API server
- [Flask-CORS](https://flask-cors.readthedocs.io/) — Cross-origin resource sharing
- [Supabase Python SDK](https://supabase.com/docs/reference/python/) — Database client

**Database**
- [Supabase](https://supabase.com/) (PostgreSQL) — Hosted relational database
- Stored procedures, triggers, and constraints for data integrity

**Frontend**
- Vanilla HTML/CSS/JavaScript — Lightweight, dependency-free UI

**Deployment**
- [Vercel](https://vercel.com/) — Serverless deployment for the full stack

---

## 🗄️ Database Schema

The database consists of **11 tables** with full relational integrity:

```
Organizers ──┐
             ├──► Events ──► EventTickets ──► Payments
Venues ───────┘         │               └──► Cancellations
                        └──► Waitlist
Users ──────────────────────► EventTickets
                              EventTickets ◄── Categories
                              EventTickets ◄── Staff
                              EventTickets ◄── Discounts
```

| Table | Purpose |
|---|---|
| `Users` | Registered customers (unique Email + CNIC) |
| `Events` | Events with venue, organizer, date, and seat count |
| `Venues` | Physical locations with city and capacity |
| `Organizers` | Event organizers with contact info |
| `Staff` | Staff members who process bookings |
| `Categories` | Ticket tiers (e.g. VIP, General) with prices |
| `Discounts` | Promo codes with percentage off and validity dates |
| `EventTickets` | Core booking record linking all entities |
| `Payments` | One payment per ticket, auto-created on booking |
| `Waitlist` | Queue for sold-out events |
| `Cancellations` | Cancellation records with refund tracking |

**Key database features:**
- `UNIQUE (EventID, SeatNo)` — prevents double-booking of the same seat
- `trg_BlockOverbooking` trigger — rolls back any insert exceeding `TotalSeats`
- `trg_WaitlistAuto` trigger — auto-promotes first waitlisted user on cancellation
- `BookTicket` stored procedure — atomic seat booking with payment creation

---

## 📡 API Reference

All endpoints are prefixed with `/api/`.

### Stats
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/stats` | Dashboard summary (tickets, revenue, events) |

### Events
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/events` | List all events with venue and organizer |
| `POST` | `/api/events` | Create a new event |
| `DELETE` | `/api/events/<id>` | Delete an event |

### Users
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users` | List all users |
| `POST` | `/api/users` | Register a new user |

### Tickets
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tickets` | List all tickets |
| `POST` | `/api/tickets` | Book a ticket (auto-creates payment) |
| `PATCH` | `/api/tickets/<id>` | Update payment status |
| `DELETE` | `/api/tickets/<id>` | Delete a ticket |
| `GET` | `/api/tickets/booked-seats/<event_id>` | Get booked seat numbers for an event |

### Venues, Organizers, Staff, Categories, Discounts
Each supports standard `GET`, `POST`, and `DELETE` (where applicable) at their respective `/api/<resource>` endpoints.

### Waitlist
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/waitlist` | List all waitlist entries |
| `POST` | `/api/waitlist` | Add user to waitlist |
| `DELETE` | `/api/waitlist/<id>` | Remove from waitlist |

### Payments & Cancellations
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/payments` | List all payments |
| `GET` | `/api/cancellations` | List all cancellations |
| `POST` | `/api/cancellations` | Record a cancellation with refund info |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A [Supabase](https://supabase.com/) project with the schema applied

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ticketvault.git
   cd ticketvault
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the database**

   Run `setup_db.sql` in your Supabase SQL editor to create all 11 tables, stored procedures, and triggers.

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-or-service-role-key
   ```

5. **Run the development server**
   ```bash
   python server.py
   ```

   The app will be available at `http://localhost:5000`.

---

## 🔐 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL | ✅ |
| `SUPABASE_KEY` | Your Supabase anon or service role key | ✅ |

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

---

## ☁️ Deployment

This project is deployed on **Vercel**.

### Deploy your own

1. Push the repo to GitHub.
2. Import the project in [Vercel](https://vercel.com/new).
3. Add `SUPABASE_URL` and `SUPABASE_KEY` under **Settings → Environment Variables**.
4. Vercel auto-detects the Flask app via `vercel.json` or the WSGI entrypoint and deploys.

**Live URL:** [event-booking-platform-amber.vercel.app](https://event-booking-platform-amber.vercel.app)

---

## 📁 Project Structure

```
TICKET VAULT/
├── api/
│   └── server.py          # Flask application & all API routes
├── templates/
│   └── index.html         # Frontend UI
├── .env                   # Local environment variables (not committed)
├── .env.local             # Local overrides (not committed)
├── .gitignore             # Git ignore rules
├── DB Project ERD.pdf     # Entity Relationship Diagram
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── setup_db.sql           # Full database schema (11 tables, triggers, procedures)
└── vercel.json            # Vercel deployment configuration
```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<div align="center">

Made with ❤️ · [⭐ Star this repo](../../stargazers) if you found it helpful!

</div>
