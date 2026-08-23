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

## Authentication & RBAC (Phase 4)

Authentication routes live under `/api/v1/auth/`:
- **`POST /api/v1/auth/register/`**: User registration (email-based, default: `role=SHIPPER`, `status=PENDING`, `is_verified=False`; prevents privilege injection).
- **`POST /api/v1/auth/login/`**: Issue JWT access (default 30 min) and refresh tokens (default 7 days) and user details (generic error messages on failure).
- **`POST /api/v1/auth/token/refresh/`**: Refresh JWT access token.
- **`POST /api/v1/auth/logout/`**: Blacklist refresh token using SimpleJWT blacklist.
- **`GET /api/v1/auth/me/`**: Get authenticated user profile details.
- **`POST /api/v1/auth/password/change/`**: Change user password and invalidate refresh tokens.
- **`POST /api/v1/auth/password/reset/request/`**: Request password reset (generic email lookup).
- **`POST /api/v1/auth/password/reset/confirm/`**: Confirm password reset using reset token.

### Role-Based Access Control (RBAC) Permissions
Modular permission classes available in `apps.accounts.permissions`:
- **Role Permissions**: `IsAdmin`, `IsShipper`, `IsTransporter`, `IsDriver`, `IsFreightForwarder`, `IsCustomsStaff`, `HasAnyRole`.
- **Status Permissions**: `IsActiveAccount`, `IsNotSuspendedAccount`, `IsVerifiedAccount`.

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
