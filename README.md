# TradeFlow

**TradeFlow** — Intelligent Logistics & Freight Matching Platform for Landlocked Ethiopia (Djibouti Port → Modjo Dry Port → regional hubs).

## Repository
- **GitHub**: [DAVM-2119/EthiopianTradeFlow](https://github.com/DAVM-2119/EthiopianTradeFlow.git)
- **Primary Branch**: `main`

---

## Architecture Stack
- **Frontend Framework**: React 18 / Vite / Tailwind CSS / React Router v6 / Axios / TanStack Query v5 / React Hook Form / Zod
- **Backend Framework**: Python 3.13 / Django / Django REST Framework
- **Authentication**: JWT (`djangorestframework-simplejwt`) with Token Blacklisting
- **Real-Time WebSockets**: Django Channels (`channels`, `channels-redis`, `daphne`)
- **Asynchronous Task Queue**: Celery & Redis (`celery`, `redis`)
- **Database**: PostgreSQL with PostGIS extension (GeoDjango spatial engine)
- **Caching & Broker**: Redis
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Filtering & Search**: `django-filter`
- **Test Framework**: Pytest (`pytest-django`, `pytest-asyncio`)

---

## Frontend Web Application & Marketplace (`frontend/`)
- **Marketplace & Load Management (`/loads`, `/marketplace`)**:
  - **Freight Discovery (`LoadsPage.jsx`)**: Search, filter by origin/destination, cargo type, and status (`DRAFT`, `POSTED`, `BOOKED`, `CANCELLED`). Tabs for Available Marketplace Freight vs My Posted Loads.
  - **Load Creation (`CreateLoadPage.jsx`)**: Form with React Hook Form + Zod validation submitting to `POST /api/v1/loads/`.
  - **Load Details & Lifecycle (`LoadDetailsPage.jsx`)**: Displays complete cargo specifications, route info, shipper identity, publish action (`POST /api/v1/loads/{id}/post/`), and cancel action (`POST /api/v1/loads/{id}/cancel/`).
  - **Load Editing (`EditLoadPage.jsx`)**: Modifies draft or posted load details via `PATCH /api/v1/loads/{id}/`.
- **Role-Aware Dashboard & Metrics Engine (`GET /api/v1/dashboard/summary/`)**: Real-time aggregated metrics for Shippers, Transporters, Drivers, Freight Forwarders, Customs Staff, and Admins.
- **JWT Authentication & Profile Engine**: Secure authentication, profile management, and password updates.

---

## Verification & Execution Commands

### Frontend Application (`frontend/`)
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server (proxies /api to http://127.0.0.1:8000)
npm run dev

# Execute production build
npm run build
```

### Backend Application (`backend/`)
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

# Start development ASGI server
pipenv run python manage.py runserver
```

### Key API Endpoints
- `GET /api/v1/health/` — System health check.
- `GET /api/v1/dashboard/summary/` — Role-aware dashboard metrics.
- `GET /api/v1/loads/` — Load list & marketplace search (`origin_city`, `destination_city`, `cargo_type`, `status`, `my_loads`).
- `POST /api/v1/loads/` — Post a new load.
- `GET /api/v1/loads/{id}/` — Retrieve load details.
- `PATCH /api/v1/loads/{id}/` — Update load specs.
- `POST /api/v1/loads/{id}/post/` — Transition status to `POSTED`.
- `POST /api/v1/loads/{id}/cancel/` — Transition status to `CANCELLED`.
