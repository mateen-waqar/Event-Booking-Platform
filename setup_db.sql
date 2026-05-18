-- schema_fix.sql
-- VS Code PostgreSQL / Supabase Ready

BEGIN;

-- USERS
ALTER TABLE "Users"
ADD COLUMN IF NOT EXISTS "CNIC" TEXT UNIQUE;

-- EVENTS
ALTER TABLE "Events"
ADD COLUMN IF NOT EXISTS "EventType" TEXT,
ADD COLUMN IF NOT EXISTS "VenueID" BIGINT,
ADD COLUMN IF NOT EXISTS "OrganizerID" BIGINT;

ALTER TABLE "Events"
ALTER COLUMN "Location" DROP NOT NULL;

-- VENUES
ALTER TABLE "Venues"
ADD COLUMN IF NOT EXISTS "VenueName" TEXT,
ADD COLUMN IF NOT EXISTS "City" TEXT,
ADD COLUMN IF NOT EXISTS "Address" TEXT,
ADD COLUMN IF NOT EXISTS "Capacity" INT;

-- ORGANIZERS
ALTER TABLE "Organizers"
ADD COLUMN IF NOT EXISTS "OrganizerName" TEXT,
ADD COLUMN IF NOT EXISTS "ContactEmail" TEXT,
ADD COLUMN IF NOT EXISTS "Phone" TEXT,
ADD COLUMN IF NOT EXISTS "Organization" TEXT;

-- STAFF
ALTER TABLE "Staff"
ADD COLUMN IF NOT EXISTS "StaffName" TEXT,
ADD COLUMN IF NOT EXISTS "Role" TEXT,
ADD COLUMN IF NOT EXISTS "ShiftTime" TEXT,
ADD COLUMN IF NOT EXISTS "Phone" TEXT,
ADD COLUMN IF NOT EXISTS "Email" TEXT,
ADD COLUMN IF NOT EXISTS "HireDate" DATE;

-- CATEGORIES
ALTER TABLE "Categories"
ADD COLUMN IF NOT EXISTS "CategoryName" TEXT,
ADD COLUMN IF NOT EXISTS "Price" NUMERIC;

-- DISCOUNTS
ALTER TABLE "Discounts"
ADD COLUMN IF NOT EXISTS "Code" TEXT,
ADD COLUMN IF NOT EXISTS "Description" TEXT,
ADD COLUMN IF NOT EXISTS "Percentage" NUMERIC,
ADD COLUMN IF NOT EXISTS "ValidFrom" DATE,
ADD COLUMN IF NOT EXISTS "ValidUntil" DATE,
ADD COLUMN IF NOT EXISTS "IsActive" BOOLEAN DEFAULT TRUE;

-- EVENTTICKETS
ALTER TABLE "EventTickets"
ADD COLUMN IF NOT EXISTS "EventID" BIGINT,
ADD COLUMN IF NOT EXISTS "UserID" BIGINT,
ADD COLUMN IF NOT EXISTS "CategoryID" BIGINT,
ADD COLUMN IF NOT EXISTS "StaffID" BIGINT,
ADD COLUMN IF NOT EXISTS "DiscountID" BIGINT,
ADD COLUMN IF NOT EXISTS "SeatNo" TEXT,
ADD COLUMN IF NOT EXISTS "BookingDate" DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS "PaymentStatus" TEXT;

-- WAITLIST
ALTER TABLE "Waitlist"
ADD COLUMN IF NOT EXISTS "EventID" BIGINT,
ADD COLUMN IF NOT EXISTS "UserID" BIGINT,
ADD COLUMN IF NOT EXISTS "CategoryID" BIGINT,
ADD COLUMN IF NOT EXISTS "RequestDate" DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS "Status" TEXT;

-- PAYMENTS
ALTER TABLE "Payments"
ADD COLUMN IF NOT EXISTS "TicketID" BIGINT,
ADD COLUMN IF NOT EXISTS "Amount" NUMERIC,
ADD COLUMN IF NOT EXISTS "PaymentMethod" TEXT,
ADD COLUMN IF NOT EXISTS "TransactionDate" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS "Status" TEXT,
ADD COLUMN IF NOT EXISTS "TransactionRef" TEXT;

-- CANCELLATIONS
ALTER TABLE "Cancellations"
ADD COLUMN IF NOT EXISTS "TicketID" BIGINT,
ADD COLUMN IF NOT EXISTS "Reason" TEXT,
ADD COLUMN IF NOT EXISTS "CancelDate" DATE DEFAULT CURRENT_DATE,
ADD COLUMN IF NOT EXISTS "RefundStatus" TEXT,
ADD COLUMN IF NOT EXISTS "RefundAmount" NUMERIC,
ADD COLUMN IF NOT EXISTS "ProcessedBy" BIGINT;

-- FOREIGN KEYS
DO $$
BEGIN

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_events_venue'
) THEN
ALTER TABLE "Events"
ADD CONSTRAINT fk_events_venue
FOREIGN KEY ("VenueID") REFERENCES "Venues"("VenueID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_events_organizer'
) THEN
ALTER TABLE "Events"
ADD CONSTRAINT fk_events_organizer
FOREIGN KEY ("OrganizerID") REFERENCES "Organizers"("OrganizerID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_tickets_event'
) THEN
ALTER TABLE "EventTickets"
ADD CONSTRAINT fk_tickets_event
FOREIGN KEY ("EventID") REFERENCES "Events"("EventID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_tickets_user'
) THEN
ALTER TABLE "EventTickets"
ADD CONSTRAINT fk_tickets_user
FOREIGN KEY ("UserID") REFERENCES "Users"("UserID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_tickets_category'
) THEN
ALTER TABLE "EventTickets"
ADD CONSTRAINT fk_tickets_category
FOREIGN KEY ("CategoryID") REFERENCES "Categories"("CategoryID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_tickets_staff'
) THEN
ALTER TABLE "EventTickets"
ADD CONSTRAINT fk_tickets_staff
FOREIGN KEY ("StaffID") REFERENCES "Staff"("StaffID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_tickets_discount'
) THEN
ALTER TABLE "EventTickets"
ADD CONSTRAINT fk_tickets_discount
FOREIGN KEY ("DiscountID") REFERENCES "Discounts"("DiscountID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_payments_ticket'
) THEN
ALTER TABLE "Payments"
ADD CONSTRAINT fk_payments_ticket
FOREIGN KEY ("TicketID") REFERENCES "EventTickets"("TicketID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_cancellations_ticket'
) THEN
ALTER TABLE "Cancellations"
ADD CONSTRAINT fk_cancellations_ticket
FOREIGN KEY ("TicketID") REFERENCES "EventTickets"("TicketID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_cancellations_staff'
) THEN
ALTER TABLE "Cancellations"
ADD CONSTRAINT fk_cancellations_staff
FOREIGN KEY ("ProcessedBy") REFERENCES "Staff"("StaffID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_waitlist_event'
) THEN
ALTER TABLE "Waitlist"
ADD CONSTRAINT fk_waitlist_event
FOREIGN KEY ("EventID") REFERENCES "Events"("EventID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_waitlist_user'
) THEN
ALTER TABLE "Waitlist"
ADD CONSTRAINT fk_waitlist_user
FOREIGN KEY ("UserID") REFERENCES "Users"("UserID");
END IF;

IF NOT EXISTS (
SELECT 1 FROM information_schema.table_constraints
WHERE constraint_name = 'fk_waitlist_category'
) THEN
ALTER TABLE "Waitlist"
ADD CONSTRAINT fk_waitlist_category
FOREIGN KEY ("CategoryID") REFERENCES "Categories"("CategoryID");
END IF;

END $$;

NOTIFY pgrst, 'reload schema';

COMMIT;