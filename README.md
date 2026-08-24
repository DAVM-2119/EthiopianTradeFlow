# TradeFlow

**TradeFlow** — Intelligent Logistics & Freight Matching Platform for Landlocked Ethiopia (Djibouti Port → Modjo Dry Port → regional hubs).

## Repository
- **GitHub**: [DAVM-2119/EthiopianTradeFlow](https://github.com/DAVM-2119/EthiopianTradeFlow.git)
- **Primary Branch**: `main`

---

## Architecture Stack
- **Mobile App**: React Native / Expo / TanStack Query v5 / Axios / AsyncStorage
- **Web App**: React 18 / Vite / Tailwind CSS / React Router v6 / Axios / TanStack Query v5
- **Backend Framework**: Python 3.13 / Django / Django REST Framework
- **Authentication**: JWT (`djangorestframework-simplejwt`) with Token Blacklisting
- **Real-Time WebSockets**: Django Channels (`channels`, `channels-redis`, `daphne`)
- **Asynchronous Task Queue**: Celery & Redis (`celery`, `redis`)
- **Database**: PostgreSQL with PostGIS extension (GeoDjango spatial engine)
- **Caching & Broker**: Redis
- **ML & Optimization Engine**: Scikit-Learn `GradientBoostingRegressor`, Pandas, NumPy, Joblib, Google OR-Tools constraint solver

---

## ML & Advanced Optimization Engine (`backend/ml/`)
- **Scikit-Learn GradientBoostingRegressor**: Corridor travel duration prediction model trained on remaining distance, cargo weight, vehicle type, hour of day, day of week, incident count, risk level, and average speed.
- **Safe Fallback Architecture**: `ETAService` checks active `MLETAPredictor` and gracefully falls back to `RuleBasedETAPredictor` on missing model file, invalid inputs, or inference exception.
- **Model Registry & Versioning**: Thread-safe registry (`ModelRegistry`) tracking versioned `.joblib` models and `.json` metadata artifacts with auto-discovery.
- **Synthetic Corridor Data Generator**: Development data generator (`generate_synthetic_corridor_dataset`) producing 5,000 corridor freight movements for training and evaluation.
- **Advanced Multi-Criteria Matcher**: Composite ranking model (`AdvancedMatcher`) scoring transporter bids based on price, on-time delivery rate, cancellation history, and corridor experience.
- **Google OR-Tools Route Optimizer**: Vehicle routing solver (`AdvancedRouteOptimizer`) computing optimal multi-checkpoint itineraries under capacity and risk constraints.

---

## React Native Driver Mobile Application (`mobile/`)
- **Driver Authentication**: Driver JWT login, token refresh interceptor, and secure session restoration.
- **Assigned Shipments Grid**: One-handed, glance-based driver screen rendering assigned freight, status pills (`BOOKED`, `ASSIGNED`, `IN_TRANSIT`, `CUSTOMS_PROCESSING`, `DELIVERED`), and highway routes.
- **Real-Time GPS Telemetry**: Continuous location telemetry stream (`latitude`, `longitude`, `speed`, `heading`, `timestamp`) along the Djibouti-Modjo N1 highway corridor.
- **Offline Synchronization Queue Engine**: Persistent client queue (`AsyncStorage`) capturing offline actions with UUID v4 idempotency keys, automatically synchronizing via `POST /api/v1/sync/events/batch/` upon reconnection.
- **Waypoint Check-in & Incident Reporting**: One-tap incident reporting modal (`ACCIDENT`, `CHECKPOINT_DELAY`, `FUEL_UNAVAILABLE`, `ROAD_PROBLEM`, `SECURITY_INCIDENT`).
- **Risk & Security Alerts**: Live highway risk advisories and checkpoint updates.
- **Digital Proof of Delivery (POD)**: Recipient signature text, full name, photo proof, timestamp, and location snapshot.

---

## Complete React Web Application Suite (`frontend/`)
- **Shipments & Live Tracking (`/shipments`, `/shipments/:id`, `/tracking/:id`)**
- **Customs & Digital Declaration (`/customs`)**
- **Analytics & Efficiency (`/analytics/fuel`, `/analytics/performance`)**
- **Payments, Settlements & Disputes (`/payments`, `/payments/:id`, `/payments/disputes`)**
- **Bidding & Booking Engine (`/bids`, `/bids/:id`)**
- **Marketplace & Freight Listings (`/loads`, `/marketplace`)**
- **Role-Aware Dashboard & Metrics Engine (`/dashboard`)**

---

## Verification & Execution Commands

### ML Model Training & Evaluation Commands (`backend/`)
```bash
cd backend

# Generate synthetic development dataset (5,000 corridor trips)
pipenv run python manage.py generate_ml_demo_data

# Train and register Scikit-Learn GradientBoostingRegressor model
pipenv run python manage.py train_eta_model --model-version eta-v1

# Benchmark active ML model vs rule-based baseline
pipenv run python manage.py evaluate_eta_model
```

### Driver Mobile Application (`mobile/`)
```bash
cd mobile

# Run unit tests for mobile offline queue engine
npm test

# Start Expo development server
npm start
```

### Web Application (`frontend/`)
```bash
cd frontend
npm run build
```

### Backend Application & Comprehensive Testing (`backend/`)
```bash
cd backend

# Run complete backend pytest suite (155 tests passed)
pipenv run pytest

# Execute Phase 26 performance & latency benchmark (P50: 16.42ms, P95: 34.40ms)
pipenv run pytest locust/run_load_test.py -s
```

---

## Phase 26 — Comprehensive Testing & Performance Framework
- **155 Backend Test Modules (100% Pass Rate)**: Complete coverage across accounts, marketplace, matching, bidding, shipments, tracking, customs, risk, routing, payments, verification, ML ETA, offline sync, and state machine.
- **Full End-to-End Business Integration**: Multi-actor simulation (`test_shipper_to_delivery_flow.py`) validating load creation ➔ bidding ➔ driver assignment ➔ live telemetry ➔ ML/Rule ETA ➔ customs declaration ➔ digital proof of delivery.
- **Shipment State Machine Enforcement**: Enforces strict lifecycle transitions (`test_state_machine.py`) and rejects invalid state jumps.
- **RBAC Matrix & Object-Level Permissions**: Multi-role security validation (`test_rbac_matrix.py`) across 6 platform roles (`SHIPPER`, `TRANSPORTER`, `DRIVER`, `FREIGHT_FORWARDER`, `CUSTOMS_STAFF`, `ADMIN`).
- **Offline Sync & Idempotency Recovery**: Mobile batch sync verification (`test_sync_resilience.py`) with client UUID v4 idempotency key duplicate event suppression.
- **WebSocket Channels Broadcast**: Real-time position tracking (`test_tracking_websocket_integration.py`) with JWT handshake auth and multi-subscriber room fanout.
- **ORM N+1 Query Elimination**: Query profiling (`test_query_performance.py`) enforcing sub-10 query count bounds on list views.
- **Locust Load Benchmarking**: Load suite (`backend/locust/locustfile.py`, `run_load_test.py`) proving sub-35ms P95 percentiles under load.

### Primary API Endpoints
- `POST /api/v1/auth/login/` — JWT authentication.
- `GET /api/v1/shipments/` — Assigned shipments listing.
- `POST /api/v1/tracking/events/` — GPS telemetry ingest.
- `POST /api/v1/sync/events/batch/` — Offline batch synchronization.
- `POST /api/v1/incidents/` — Incident report API.
- `POST /api/v1/shipments/{id}/proof-of-delivery/` — Proof of delivery capture.
