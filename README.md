# TradeFlow

**TradeFlow** — Intelligent Logistics & Freight Matching Platform for Landlocked Ethiopia (Djibouti Port → Modjo Dry Port → regional hubs).

## Repository
- **GitHub**: [DAVM-2119/EthiopianTradeFlow](https://github.com/DAVM-2119/EthiopianTradeFlow.git)
- **Primary Branch**: `main`

---

## Architecture Stack
- **Backend Framework**: Python 3.13 / Django / Django REST Framework
- **Database**: PostgreSQL with PostGIS extension (GeoDjango spatial engine)
- **Caching & Broker**: Redis
- **Task Queue**: Celery & Celery Beat
- **Real-Time Communication**: Django Channels (WebSockets)
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Filtering & Search**: `django-filter`
- **Test Framework**: Pytest (`pytest-django`)

---

## Identity & Custom User Model (Phase 3)

The custom user model lives in `backend/apps/accounts/`:
- **`User`**: Custom user model inheriting `AbstractBaseUser`, `PermissionsMixin`, and `BaseModel` (UUIDv4 primary key).
- **Email Authentication**: `USERNAME_FIELD = "email"`, unique, normalized email addresses (no username field).
- **Role System**: Centralized `RoleChoices` (`SHIPPER`, `TRANSPORTER`, `DRIVER`, `FREIGHT_FORWARDER`, `CUSTOMS_STAFF`, `ADMIN`).
- **Account Status**: Independent `StatusChoices` (`ACTIVE`, `INACTIVE`, `SUSPENDED`, `PENDING`).
- **Verification Flag**: Independent `is_verified` identity verification status.
- **User Manager**: `UserManager` providing email normalization, secure password hashing (`set_password`), and superuser validation.
- **Admin**: Custom `UserAdmin` registered in Django admin with search and role/status/verification filters.

---

## Core Infrastructure (Phase 2) Architecture

The core reusable infrastructure lives in `backend/apps/core/`:
- **`BaseModel`**: Abstract base model providing auto-generated UUIDv4 primary keys (`id`), indexed `created_at`, and `updated_at` timestamps for all future domain models.
- **`AuditLog`**: Decoupled system audit logging tracking action types (`CREATE`, `UPDATE`, `DELETE`, `VERIFY`, `REJECT`), `actor_id`, target `resource_type` and `resource_id`, and structured `metadata` JSON.
- **Exceptions**: Centralized `TradeFlowException` base class and subclasses (`ValidationException`, `NotFoundException`, `PermissionDeniedException`, `ConflictException`) handled by `custom_exception_handler` for unified JSON error payloads.
- **Standard Responses**: `success_response` and `error_response` helpers producing consistent API response formats.
- **Pagination**: `StandardResultsSetPagination` (default page size 20, max 100).
- **Filtering**: Global `DEFAULT_FILTER_BACKENDS` configured (`DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`).
- **Permissions**: Reusable `IsStaffUser`, `ReadOnly`, and `IsOwnerOrReadOnly` permission classes.

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
