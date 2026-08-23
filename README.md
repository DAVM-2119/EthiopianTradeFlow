# TradeFlow

**TradeFlow** — Intelligent Logistics & Freight Matching Platform for Landlocked Ethiopia (Djibouti Port → Modjo Dry Port → regional hubs).

## Repository
- **GitHub**: [DAVM-2119/EthiopianTradeFlow](https://github.com/DAVM-2119/EthiopianTradeFlow.git)
- **Primary Branch**: `main`

---

## Architecture Stack
- **Backend Framework**: Python 3.13 / Django / Django REST Framework
- **Authentication**: JWT (`djangorestframework-simplejwt`) with Token Blacklisting
- **Real-Time WebSockets**: Django Channels (`channels`, `channels-redis`, `daphne`)
- **Database**: PostgreSQL with PostGIS extension (GeoDjango spatial engine)
- **Caching & Broker**: Redis
- **Task Queue**: Celery & Celery Beat
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Filtering & Search**: `django-filter`
- **Test Framework**: Pytest (`pytest-django`, `pytest-asyncio`)

---

## Domain Architecture (Phases 3–17)

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
- **`POST /api/v1/bids/<uuid:id>/accept/`**: Accept bid & book load (`ACTIVE` → `ACCEPTED`, `Load` → `BOOKED`, competing active bids → `REJECTED`, automatic `Shipment` creation in `BOOKED` state). Uses `transaction.atomic()` with `select_for_update()` row locking.
- **`GET /api/v1/my-bids/`**: List bids placed by authenticated transporter.

### Freight Matching Engine (`apps.matching`)
- **`MatchRecommendation`**: Deterministic candidate recommendation entity (`load`, `transporter`, `rank`, `total_score`, `cost_score`, `reliability_score`, `fuel_efficiency_score`, `proximity_score`, `availability_score`, `explanation`, `algorithm_version`, `generated_at`, `is_active`).
- **Weighted Scoring Algorithm v1**: Total score = $0.30 \times \text{Cost} + 0.25 \times \text{Reliability} + 0.15 \times \text{Fuel} + 0.20 \times \text{Proximity} + 0.10 \times \text{Availability}$.
- **`POST /api/v1/loads/<uuid:load_id>/matches/`**: Generate or regenerate ranked recommendations shortlist for a posted load.
- **`GET /api/v1/loads/<uuid:load_id>/matches/`**: Retrieve active recommendation shortlist (Load owner / Admin).
- **`GET /api/v1/matches/<uuid:id>/`**: Retrieve recommendation detail with score breakdown (Load owner / Transporter / Admin).

### Shipment Lifecycle (`apps.shipments`)
- **`Shipment`**: Shipment entity created upon bid acceptance (`load`, `bid`, `shipper`, `transporter`, `vehicle`, `driver`, `status`: `BOOKED`/`ASSIGNED`/`PICKUP_READY`/`IN_TRANSIT`/`CUSTOMS_PROCESSING`/`CUSTOMS_CLEARED`/`DELIVERED`/`COMPLETED`/`CANCELLED`/`FAILED`/`DISPUTED`, operational timestamps).
- **`ShipmentEvent`**: Append-only lifecycle event audit log (`shipment`, `event_type`, `previous_status`, `new_status`, `description`, `created_by`).
- **`ProofOfDelivery`**: Delivery confirmation record (`shipment`, `receiver_name`, `delivery_timestamp`, `signature_reference`, `photo_reference`, `notes`, `submitted_by`).
- **`GET /api/v1/shipments/`**: List role-filtered shipments (Shipper, Transporter, Driver, Admin).
- **`GET /api/v1/shipments/<uuid:id>/`**: Retrieve shipment detail.
- **`POST /api/v1/shipments/<uuid:id>/assign/`**: Assign fleet vehicle and driver.
- **`POST /api/v1/shipments/<uuid:id>/transition/`**: Execute controlled lifecycle state transition.
- **`POST /api/v1/shipments/<uuid:id>/cancel/`**: Cancel pre-delivery shipment.
- **`GET /api/v1/shipments/<uuid:id>/events/`**: Retrieve shipment lifecycle audit trail.
- **`POST/GET /api/v1/shipments/<uuid:id>/proof-of-delivery/`**: Record or view proof of delivery.
- **`POST /api/v1/shipments/<uuid:id>/complete/`**: Complete shipment (Requires DELIVERED status + Proof of Delivery).

### Real-Time GPS Tracking & WebSockets (`apps.tracking`)
- **`TrackingEvent`**: Spatial GPS position update entity (`event_id` unique key, `shipment`, `driver`, `location` PostGIS `PointField` SRID 4326, `latitude`, `longitude`, `speed`, `heading`, `recorded_at`, `received_at`).
- **`POST /api/v1/tracking/events/`**: Ingest GPS position update from device/driver. Enforces assigned driver verification, trackable shipment status checks, coordinate boundaries, duplicate event prevention, broadcasts position update upon `transaction.on_commit`, and recalculates ETA.
- **`GET /api/v1/shipments/<uuid:shipment_id>/tracking/`**: Retrieve historical GPS position updates list for a shipment.
- **`GET /api/v1/shipments/<uuid:shipment_id>/tracking/latest/`**: Retrieve latest recorded GPS position update for a shipment.
- **`WS /ws/v1/shipments/<uuid:shipment_id>/tracking/?token=<jwt>`**: Real-time WebSocket connection endpoint. Joins `shipment_<shipment_id>` channel group via Redis channel layer. Authenticates via JWT and enforces object-level participant security (`Shipper`, `Transporter`, `Driver`, `Admin`). Broadcasts `tracking.position_updated` JSON events in real time.

### Offline Synchronization Engine (`apps.synchronization`)
- **`OfflineSyncEvent`**: Offline driver action record (`client_event_id` unique UUID key, `user`, `device_id`, `event_type`: `WAYPOINT_CHECKIN`/`INCIDENT_REPORT`/`TRACKING_EVENT`, `entity_type`, `entity_id`, `payload`, `client_created_at`, `client_updated_at`, `server_received_at`, `status`: `PENDING`/`SYNCING`/`SYNCED`/`FAILED`/`CONFLICT`, `attempt_count`, `last_attempt_at`, `synced_at`, `error_code`, `error_message`, `server_entity_id`).
- **Idempotency**: Guarantees one logical client event = one server-side domain execution. Duplicate submissions return the existing `SYNCED` record without duplicate side-effects.
- **Conflict Resolution**: Timestamp comparison against server state. Stale/superseded offline events are set to `status="CONFLICT"` with `error_code="STALE_TIMESTAMP"`.
- **Transaction Safety**: Domain processing occurs in `transaction.atomic()`. Synced tracking events trigger `transaction.on_commit` broadcasting updates to Phase 12 WebSocket clients and recalculating ETA.
- **`POST /api/v1/sync/events/`**: Submit single queued offline event.
- **`POST /api/v1/sync/events/batch/`**: Submit batch of queued offline events returning per-event status results.
- **`GET /api/v1/sync/events/<uuid:client_event_id>/`**: Retrieve offline sync event status by client UUID.
- **`POST /api/v1/sync/events/<uuid:client_event_id>/retry/`**: Retry a failed offline sync event.
- **`GET /api/v1/sync/status/`**: Retrieve user sync status summary.

### ETA Prediction Engine (`apps.eta`)
- **`ETAPrediction`**: Persisted predicted arrival record (`shipment`, `predicted_at`, `estimated_arrival`, `remaining_distance_km`, `expected_speed_kmh`, `delay_minutes`, `prediction_method`: `RULE_BASED`, `algorithm_version`: `eta-v1`, `confidence`: `0.85`).
- **Predictor Abstraction**: `BaseETAPredictor` interface and `RuleBasedETAPredictor` baseline algorithm calculating remaining geodesic Haversine corridor distance, expected travel speeds, and incident delays. Formatted for future ML model substitution (Phase 25).
- **`GET /api/v1/shipments/<uuid:shipment_id>/eta/`**: Retrieve latest ETA prediction for a shipment.
- **`GET /api/v1/shipments/<uuid:shipment_id>/eta/history/`**: Retrieve historical predictions list for a shipment.

### Dynamic Pricing Engine (`apps.pricing`)
- **`PriceQuote`**: Persisted spot price quote entity (`load`, `shipment`, `base_price`, `demand_multiplier`, `fuel_multiplier`, `congestion_multiplier`, `calculated_price`, `final_price`, `currency`, `pricing_method`: `RULE_BASED`, `algorithm_version`: `pricing-v1`, `valid_from`, `valid_until`, `divergence_warning`, `divergence_notes`).
- **`ContractRate`**: Locked contract rate agreement for shippers (`shipper`, `transporter`, `origin_city`, `destination_city`, `agreed_rate`, `currency`, `valid_from`, `valid_until`, `is_active`, `divergence_threshold_percent`). Flags spot rate divergence warnings if spot price deviates significantly from agreed contract rate (FR-04.2).
- **`PricingAudit`**: Input/output JSON snapshot record for complete calculation auditability (FR-04.3).
- **`GET /api/v1/loads/<uuid:load_id>/pricing/`**: Retrieve current spot price quote.
- **`POST /api/v1/loads/<uuid:load_id>/pricing/calculate/`**: Recalculate spot price quote.
- **`GET /api/v1/loads/<uuid:load_id>/pricing/history/`**: Retrieve pricing audit & quote history.
- **`GET/POST /api/v1/pricing/contracts/`**: List or create locked shipper contract rates.

### Route Optimization & Routing Engine (`apps.routing`)
- **`Route`**: Candidate and active route entity (`shipment`, `provider`: `OSRM`/`GeodesicCorridor`, `provider_route_id`, `origin_city`, `destination_city`, `distance_km`, `duration_minutes`, `estimated_fuel_liters`, `estimated_fuel_cost`, `risk_score`, `optimization_score`, `status`: `ROUTE_ACTIVE`/`REROUTE_PROPOSED`/`REROUTE_ACCEPTED`/`REROUTE_REJECTED`/`INACTIVE`, `is_recommended`, `geometry_json`).
- **`RouteLeg`**: Sequenced route waypoint component (`route`, `sequence`, `start_point`, `end_point`, `distance_km`, `duration_minutes`, `estimated_fuel_liters`, `road_condition`, `security_risk_score`).
- **Pluggable Architecture**: `BaseRoutingProvider` & `OSRMRoutingProvider` querying `OSRM_BASE_URL` (environment configurable, with geodesic fallback); `BaseRouteOptimizer` & `WeightedRouteOptimizer` computing normalized multi-attribute cost scores (Distance 0.25, Time 0.25, Fuel 0.30, Risk 0.20; lower score = superior route).
- **Rerouting Workflow**: Proposes alternative routes in `REROUTE_PROPOSED` status without altering active routes until driver/dispatcher explicitly confirms (`confirm_reroute(accept=True)`).
- **`POST /api/v1/shipments/<uuid:shipment_id>/routes/calculate/`**: Calculate candidate routes and select best route.
- **`GET /api/v1/shipments/<uuid:shipment_id>/routes/`**: List candidate and active routes for a shipment.
- **`GET /api/v1/routes/<uuid:route_id>/`**: Retrieve route detail and legs.
- **`POST /api/v1/routes/<uuid:route_id>/reroute/`**: Propose or confirm/reject route modification.

### Customs Documentation & Clearance Engine (`apps.customs`)
- **`CustomsDocument`**: Digital customs document entity (`shipment`, `document_type`: `COMMERCIAL_INVOICE`/`PACKING_LIST`/`BILL_OF_LADING`/`CERTIFICATE_OF_ORIGIN`, `file`, `original_filename`, `file_size`, `mime_type`, `document_number`, `issue_date`, `declared_value`, `quantity`, `uploaded_by`, `clearance_status`: `DRAFT`/`SUBMITTED`/`UNDER_REVIEW`/`CLEARED`/`REJECTED`, `validation_status`: `PENDING`/`PASSED`/`FAILED`, `rejection_reason`, timestamps).
- **Automated Validation Engine**: `DocumentValidator` (file size 10MB limit, allowed extensions `.pdf`, `.jpg`, `.png`, MIME sanitization); `ConsistencyValidator` (completeness check for 4 required document types, commercial invoice vs packing list quantity verification, declared financial value validation).
- **Clearance Workflow & Permissions**: Shipper and Freight Forwarder document upload and submission (`DRAFT` $\rightarrow$ `SUBMITTED`); Customs Staff (`CUSTOMS_STAFF`) and Admin review workflow (`UNDER_REVIEW` $\rightarrow$ `CLEARED` / `REJECTED` with audit rejection reason).
- **External Customs Integration Boundary**: `BaseCustomsProvider` interface and `MockCustomsProvider` implementation representing Ethiopian Customs Commission integration boundary.
- **`POST /api/v1/shipments/<uuid:shipment_id>/customs/documents/`**: Upload customs document file & metadata.
- **`GET /api/v1/shipments/<uuid:shipment_id>/customs/documents/`**: List all customs documents for a shipment.
- **`GET /api/v1/customs/documents/<uuid:document_id>/`**: Retrieve document detail.
- **`POST /api/v1/shipments/<uuid:shipment_id>/customs/validate/`**: Run automated document completeness and consistency checks.
- **`POST /api/v1/shipments/<uuid:shipment_id>/customs/submit/`**: Submit shipment documents for customs clearance (`SUBMITTED`).
- **`POST /api/v1/shipments/<uuid:shipment_id>/customs/status/`**: Update clearance review status (`UNDER_REVIEW`, `CLEARED`, `REJECTED` - Customs Staff / Admin).

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

# Start development ASGI server
pipenv run python manage.py runserver
```

### Health Check Endpoint
`GET /api/v1/health/` verifies Django, PostgreSQL, PostGIS, and Redis status.
