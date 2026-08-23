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

## Frontend Web Application & Role Dashboard (`frontend/`)
- **Role-Aware Dashboard & Metrics Engine (`GET /api/v1/dashboard/summary/`)**: Real-time aggregated metric cards, charts, and activity feeds for each role:
  - **Shipper Dashboard (`ShipperDashboard.jsx`)**: Active loads, in-transit cargo, pending bids, completed shipments, monthly throughput bar charts, freight status distribution.
  - **Transporter Dashboard (`TransporterDashboard.jsx`)**: Available freight listings, active shipments, fleet vehicle count, confirmed payout earnings (ETB), on-time delivery rate, revenue trend charts.
  - **Driver Dashboard (`DriverDashboard.jsx`)**: Assigned route, completed trips, active corridor safety alerts, live GPS location status (15s interval).
  - **Freight Forwarder Dashboard (`FreightForwarderDashboard.jsx`)**: Managed freight throughput, customs clearance pipeline, corridor movement speed.
  - **Customs Staff Dashboard (`CustomsStaffDashboard.jsx`)**: Pending declaration review queue, approved/rejected customs document statistics, total intake.
  - **Admin Dashboard (`AdminDashboard.jsx`)**: Platform user growth, pending verification queue, global active shipments, financial dispute logs.
- **JWT Authentication & Profile Engine**: Secure login, registration, token refresh queue, token blacklisting logout, profile updates (`PATCH /api/v1/auth/me/`), and password updates (`POST /api/v1/auth/password/change/`).

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

### Health Check & Dashboard Summary Endpoints
- `GET /api/v1/health/` — Verifies Django, PostgreSQL, PostGIS, and Redis connection status.
- `GET /api/v1/dashboard/summary/` — Returns role-specific aggregated metric cards, charts, and activity feeds.
