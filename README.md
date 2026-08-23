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
- **Role-Aware Navigation System**: Centralized configuration (`src/config/navigation.js`) providing tailored sidebar views for `SHIPPER`, `TRANSPORTER`, `DRIVER`, `FREIGHT_FORWARDER`, `CUSTOMS_STAFF`, and `ADMIN`.
- **Responsive Layout & Sidebar**: Desktop collapsible sidebar (`w-64` / `w-16`) and mobile drawer overlay with smooth transitions (`Sidebar.jsx`).
- **Navbar & Breadcrumbs**: Real-time location breadcrumb trail (`Breadcrumbs.jsx`), live online/offline network connection monitoring (`Navbar.jsx`), and user profile dropdown (`UserMenu.jsx`).
- **Application State Engine**: Reusable data states (`EmptyState.jsx`) and offline corridor cache mode notifications (`OfflineState.jsx`).

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

### Health Check Endpoint
`GET /api/v1/health/` verifies Django, PostgreSQL, PostGIS, and Redis status.
