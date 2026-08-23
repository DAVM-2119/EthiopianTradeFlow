# TradeFlow

**TradeFlow** — Intelligent Logistics & Freight Matching Platform for Landlocked Ethiopia (Djibouti Port → Modjo Dry Port → regional hubs).

## Repository
- **GitHub**: [DAVM-2119/EthiopianTradeFlow](https://github.com/DAVM-2119/EthiopianTradeFlow.git)
- **Primary Branch**: `main`

---

## Architecture Stack
- **Backend Framework**: Python 3.13 / Django / Django REST Framework
- **Authentication**: JWT (`djangorestframework-simplejwt`) with Token Blacklisting
- **Database**: PostgreSQL with PostGIS extension (GeoDjango spatial engine)
- **Caching & Broker**: Redis
- **Task Queue**: Celery & Celery Beat
- **Real-Time Communication**: Django Channels (WebSockets)
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Filtering & Search**: `django-filter`
- **Test Framework**: Pytest (`pytest-django`)

---

## Domain Architecture (Phases 3–9)

### User Identity & Profiles (`apps.accounts` & `apps.profiles`)
- **`User`**: Custom email-authenticated identity model inheriting `BaseModel` (UUIDv4).
- **Role Profiles**: `ShipperProfile`, `TransporterProfile`, `DriverProfile`, `FreightForwarderProfile`, `CustomsStaffProfile` linked 1-to-1 with `User`.
- **`GET/PATCH /api/v1/profiles/me/`**: Retrieve and update role-specific business profile.
- **`GET/POST /api/v1/profiles/transporter/drivers/`**: Transporter driver fleet management.

### Fleet Management (`apps.fleet`)
- **`Vehicle`**: Transporter fleet vehicle model (`registration_number`, `vehicle_type`, `capacity`, `capacity_unit`, `fuel_type`, `model`, `manufacturer`, `year`, `status`). Enforces database check constraint `capacity > 0`.
- **`VehicleDocument`**: Vehicle document metadata for insurance, roadworthiness certificate, and registration.
- **`GET/POST /api/v1/vehicles/`**: Transporter vehicle list & create endpoint.
- **`GET/PATCH/DELETE /api/v1/vehicles/<uuid:id>/`**: Transporter vehicle detail & deactivation endpoint.

### Marketplace Onboarding & Verification (`apps.verification`)
- **`Verification`**: User onboarding state model (`PENDING`, `VERIFIED`, `SUSPENDED`, `REJECTED`).
- **`VerificationHistory`**: Append-only audit trail capturing previous status, new status, acting administrator, timestamp, and required reasons.
- **`GET /api/v1/verification/me/`**: Retrieve current user verification state.
- **`POST /api/v1/verification/me/submit/`**: Self-service user verification submission.
- **`GET /api/v1/admin/verifications/`**: Admin pending verification queue.
- **`POST /api/v1/admin/verifications/<uuid:id>/approve/`**: Admin verification approval.

### Load Management & Search Engine (`apps.marketplace`)
- **`Load`**: Freight load entity (`shipper`, `title`, `origin_city`, `destination_city`, `cargo_type`, `weight`, `volume`, `pickup_window_start`, `pickup_window_end`, `delivery_window_start`, `delivery_window_end`, `status`: `DRAFT`/`POSTED`/`BOOKED`/`CANCELLED`). Enforces `weight > 0` and `volume > 0` check constraints.
- **`GET/POST /api/v1/loads/`**: List/search posted loads with multi-field filtering or create new load.
- **`GET/PATCH /api/v1/loads/<uuid:id>/`**: Retrieve or update load (Owner restricted).
- **`POST /api/v1/loads/<uuid:id>/post/`**: Transition load state `DRAFT` → `POSTED`.
- **`POST /api/v1/loads/<uuid:id>/cancel/`**: Transition load state → `CANCELLED`.

### Bidding & Booking System (`apps.marketplace`)
- **`Bid`**: Transporter bid entity (`load`, `transporter`, `amount`, `currency`, `proposed_pickup_date`, `estimated_delivery_date`, `message`, `status`: `ACTIVE`/`WITHDRAWN`/`ACCEPTED`/`REJECTED`/`EXPIRED`, `expires_at`, `accepted_at`, `withdrawn_at`). Enforces `amount > 0` check constraint and unique active bid per transporter per load.
- **`POST/GET /api/v1/loads/<uuid:load_id>/bids/`**: Verified transporter place bid / Load owner list bids.
- **`GET/PATCH /api/v1/bids/<uuid:id>/`**: Retrieve or update active bid.
- **`POST /api/v1/bids/<uuid:id>/withdraw/`**: Withdraw active bid (`ACTIVE` → `WITHDRAWN`).
- **`POST /api/v1/bids/<uuid:id>/accept/`**: Accept bid & book load (`ACTIVE` → `ACCEPTED`, `Load` → `BOOKED`, competing active bids → `REJECTED`). Uses `transaction.atomic()` with `select_for_update()` row locking.
- **`GET /api/v1/my-bids/`**: List bids placed by authenticated transporter.

### Freight Matching Engine (`apps.matching`)
- **`MatchRecommendation`**: Deterministic candidate recommendation entity (`load`, `transporter`, `rank`, `total_score`, `cost_score`, `reliability_score`, `fuel_efficiency_score`, `proximity_score`, `availability_score`, `explanation`, `algorithm_version`, `generated_at`, `is_active`).
- **Weighted Scoring Algorithm v1**: Total score = $0.30 \times \text{Cost} + 0.25 \times \text{Reliability} + 0.15 \times \text{Fuel} + 0.20 \times \text{Proximity} + 0.10 \times \text{Availability}$.
- **`POST /api/v1/loads/<uuid:load_id>/matches/`**: Generate or regenerate ranked recommendations shortlist for a posted load.
- **`GET /api/v1/loads/<uuid:load_id>/matches/`**: Retrieve active recommendation shortlist (Load owner / Admin).
- **`GET /api/v1/matches/<uuid:id>/`**: Retrieve recommendation detail with score breakdown (Load owner / Transporter / Admin).

---

## Verification Commands

Run the full automated test suite and system checks:
```bash
cd backend

# Verify Django configuration
pipenv run python manage.py check

# Check for unapplied migrations
pipenv run python manage.py makemigrations --check

# Execute database migrations
pipenv run python manage.py migrate

# Run complete pytest suite against PostgreSQL/PostGIS test database
pipenv run pytest

# Start development server
pipenv run python manage.py runserver
```

### Health Check Endpoint
`GET /api/v1/health/` verifies Django, PostgreSQL, PostGIS, and Redis status.
