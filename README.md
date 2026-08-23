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

## Domain Architecture (Phases 3–6)

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
- **Eligibility Engine**: `is_vehicle_verification_eligible(vehicle)` and `is_marketplace_eligible(user)` validating document presence/expiry and verification state.
- **`GET /api/v1/verification/me/`**: Retrieve current user verification state.
- **`POST /api/v1/verification/me/submit/`**: Self-service user verification submission.
- **`GET /api/v1/admin/verifications/`**: Admin pending verification queue.
- **`POST /api/v1/admin/verifications/<uuid:id>/approve/`**: Admin verification approval.
- **`POST /api/v1/admin/verifications/<uuid:id>/suspend/`**: Admin verification suspension.

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
