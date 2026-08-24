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

## Complete React Web Application Suite (`frontend/`)
- **Shipments & Live Tracking (`/shipments`, `/shipments/:id`, `/tracking/:id`)**:
  - Role-aware shipment management grid (`ShipmentsPage.jsx`).
  - Milestone lifecycle progression bar (`ShipmentTimeline.jsx`) tracking statuses (`BOOKED`, `ASSIGNED`, `PICKUP_READY`, `IN_TRANSIT`, `CUSTOMS_PROCESSING`, `CUSTOMS_CLEARED`, `DELIVERED`, `COMPLETED`).
  - Interactive GPS live corridor map (`ShipmentMap.jsx`) & real-time WebSocket telemetry stream (`useShipmentTracking.js`).
  - AI predictive ETA card (`ETAInfoCard.jsx`).
- **Customs & Digital Declaration (`/customs`)**:
  - Declaration management for Commercial Invoices, Packing Lists, Bills of Lading, and Certificates of Origin.
  - Document upload modal (`DocumentUploadForm.jsx`) with multipart upload support.
- **Analytics & Efficiency (`/analytics/fuel`, `/analytics/performance`)**:
  - Fuel consumption trends and AI eco-driving recommendations.
  - Transporter performance dashboard benchmarking on-time delivery rates, incident rates, and platinum verification tier.
- **Payments, Settlements & Disputes (`/payments`, `/payments/:id`, `/payments/disputes`)**:
  - Escrow payment management, automated platform commission calculations, and transporter payouts.
  - Dispute resolution claims portal.
- **Bidding & Booking Engine (`/bids`, `/bids/:id`)**:
  - Transporter bidding portal, bid comparison matrix (`BidComparison.jsx`), and acceptance confirmation modal.
- **Marketplace & Freight Listings (`/loads`, `/marketplace`)**:
  - Load creation, publishing, search, filtering, and detail management.
- **Role-Aware Dashboard & Metrics Engine (`/dashboard`)**:
  - Aggregated metrics for Shippers, Transporters, Drivers, Freight Forwarders, Customs Staff, and Admins.

---

## Verification & Execution Commands

### Frontend Application (`frontend/`)
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev

# Execute production build
npm run build
```

### Backend Application (`backend/`)
```bash
cd backend

# Verify Django configuration
pipenv run python manage.py check

# Execute database migrations
pipenv run python manage.py migrate

# Run complete pytest suite against PostgreSQL/PostGIS test database
pipenv run pytest

# Start development ASGI server
pipenv run python manage.py runserver
```

### Primary API Endpoints
- `GET /api/v1/health/` — System health check.
- `GET /api/v1/dashboard/summary/` — Role-aware metrics dashboard.
- `GET /api/v1/loads/` — Load marketplace API.
- `GET /api/v1/shipments/` — Shipment lifecycle API.
- `GET /api/v1/shipments/{id}/tracking/` — Live tracking telemetry history.
- `GET /api/v1/shipments/{id}/customs/documents/` — Customs declaration documents.
- `GET /api/v1/analytics/fuel/trends/` — Fuel consumption analytics.
- `GET /api/v1/analytics/transporter/performance/` — Transporter performance metrics.
- `GET /api/v1/payments/` — Payment escrow ledger.
- `GET /api/v1/payments/disputes/` — Disputes portal API.
