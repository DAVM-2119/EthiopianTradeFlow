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

## Frontend Web Application (`frontend/`)
- **Bidding & Booking Engine (`/bids`, `/bids/:id`, `/loads/:id`)**:
  - **Transporter Bidding Portal**: Rate bid creation, updating, and withdrawal (`ACTIVE`, `WITHDRAWN`). Form validation with React Hook Form + Zod.
  - **Transporter Bids Dashboard (`MyBidsPage.jsx`)**: Comprehensive list of submitted bids with status filters (`All`, `Active`, `Accepted`, `Rejected`, `Withdrawn`).
  - **Shipper Bid Evaluation Matrix (`BidComparison.jsx`)**: Side-by-side bid comparison matrix highlighting rate offers, proposed pickup/delivery dates, and transporter reliability badges.
  - **Booking Acceptance Modal (`AcceptBidModal.jsx`)**: Confirms rate bid acceptance, transitioning bid status to `ACCEPTED` and load status to `BOOKED` while rejecting competing bids (`POST /api/v1/bids/{id}/accept/`).
- **Marketplace & Load Management (`/loads`, `/marketplace`)**:
  - Freight discovery, search, multi-field filter toolbar, load creation, editing, and publishing.
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
- `GET /api/v1/loads/` — Load list & marketplace search.
- `GET /api/v1/loads/{id}/bids/` — List bids submitted for a freight load.
- `POST /api/v1/loads/{id}/bids/` — Submit a new transporter rate bid.
- `GET /api/v1/my-bids/` — List transporter's submitted bids.
- `GET /api/v1/bids/{id}/` — Retrieve single bid details.
- `PATCH /api/v1/bids/{id}/` — Update an active bid rate or schedule.
- `POST /api/v1/bids/{id}/withdraw/` — Withdraw an active bid offer.
- `POST /api/v1/bids/{id}/accept/` — Accept bid & transition load to `BOOKED`.
