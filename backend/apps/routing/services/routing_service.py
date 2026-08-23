from decimal import Decimal
from django.db import transaction
from apps.shipments.models import Shipment
from apps.routing.models import Route, RouteLeg, RouteStatusChoices
from apps.routing.providers import OSRMRoutingProvider
from apps.routing.optimizers import WeightedRouteOptimizer
from apps.core.exceptions import NotFoundException, ValidationException

def calculate_and_save_routes(*, shipment_id, provider=None, optimizer=None):
    """
    Calculates candidate routes, evaluates them using weighted optimization,
    persists candidate Route and RouteLeg models, and sets the top-ranked candidate as ROUTE_ACTIVE.
    """
    shipment = Shipment.objects.select_related('load').filter(id=shipment_id).first()
    if not shipment:
        raise NotFoundException("Shipment not found.")

    if provider is None:
        provider = OSRMRoutingProvider()
    if optimizer is None:
        optimizer = WeightedRouteOptimizer()

    candidates = provider.calculate_candidate_routes(
        origin_city=shipment.load.origin_city,
        destination_city=shipment.load.destination_city
    )

    if not candidates:
        raise ValidationException("No candidate routes could be generated for this corridor.")

    evaluated = optimizer.evaluate_candidates(candidates)
    best_candidate, best_score = evaluated[0]

    created_routes = []
    with transaction.atomic():
        # Deactivate existing active routes for this shipment
        Route.objects.filter(shipment=shipment, status=RouteStatusChoices.ROUTE_ACTIVE).update(
            status=RouteStatusChoices.INACTIVE,
            is_recommended=False
        )

        for candidate, score in evaluated:
            is_recommended = (candidate == best_candidate)
            status = RouteStatusChoices.ROUTE_ACTIVE if is_recommended else RouteStatusChoices.INACTIVE

            route = Route.objects.create(
                shipment=shipment,
                provider=candidate.provider,
                provider_route_id=candidate.provider_route_id,
                origin_city=candidate.origin_city,
                destination_city=candidate.destination_city,
                distance_km=Decimal(str(candidate.distance_km)),
                duration_minutes=candidate.duration_minutes,
                estimated_fuel_liters=Decimal(str(candidate.estimated_fuel_liters)),
                estimated_fuel_cost=Decimal(str(candidate.estimated_fuel_cost)),
                risk_score=Decimal(str(candidate.risk_score)),
                optimization_score=Decimal(str(score)),
                status=status,
                is_recommended=is_recommended,
                geometry_json=candidate.geometry_json
            )

            for leg in candidate.legs:
                RouteLeg.objects.create(
                    route=route,
                    sequence=leg.sequence,
                    start_point=leg.start_point,
                    end_point=leg.end_point,
                    distance_km=Decimal(str(leg.distance_km)),
                    duration_minutes=leg.duration_minutes,
                    estimated_fuel_liters=Decimal(str(leg.estimated_fuel_liters)),
                    security_risk_score=Decimal(str(leg.security_risk_score))
                )

            created_routes.append(route)

    # Return top recommended route
    return next(r for r in created_routes if r.is_recommended)


def propose_reroute(*, route_id, new_risk_score=None):
    """
    FR-05.3 Proposes a reroute based on route condition changes or security incidents.
    Creates a new route proposal in REROUTE_PROPOSED status without altering active route.
    """
    route = Route.objects.filter(id=route_id).first()
    if not route:
        raise NotFoundException("Route not found.")

    risk = Decimal(str(new_risk_score)) if new_risk_score is not None else Decimal('0.30')
    opt_score = float(route.optimization_score) * 1.10

    proposed = Route.objects.create(
        shipment=route.shipment,
        provider=route.provider,
        provider_route_id=f"{route.provider_route_id}-reroute",
        origin_city=route.origin_city,
        destination_city=route.destination_city,
        distance_km=route.distance_km,
        duration_minutes=route.duration_minutes,
        estimated_fuel_liters=route.estimated_fuel_liters,
        estimated_fuel_cost=route.estimated_fuel_cost,
        risk_score=risk,
        optimization_score=Decimal(str(round(opt_score, 4))),
        status=RouteStatusChoices.REROUTE_PROPOSED,
        is_recommended=False,
        geometry_json=route.geometry_json
    )

    return proposed


def confirm_reroute(*, route_id, accept=True):
    """
    FR-05.3 Confirms or rejects a reroute proposal.
    Active route is updated only upon explicit driver/dispatcher confirmation.
    """
    proposed_route = Route.objects.filter(id=route_id).first()
    if not proposed_route:
        raise NotFoundException("Proposed route not found.")

    if proposed_route.status != RouteStatusChoices.REROUTE_PROPOSED:
        raise ValidationException("Route is not in REROUTE_PROPOSED status.")

    with transaction.atomic():
        if accept:
            # Deactivate current active route
            Route.objects.filter(
                shipment=proposed_route.shipment,
                status=RouteStatusChoices.ROUTE_ACTIVE
            ).update(status=RouteStatusChoices.INACTIVE, is_recommended=False)

            proposed_route.status = RouteStatusChoices.ROUTE_ACTIVE
            proposed_route.is_recommended = True
            proposed_route.save(update_fields=['status', 'is_recommended', 'updated_at'])
        else:
            proposed_route.status = RouteStatusChoices.REROUTE_REJECTED
            proposed_route.save(update_fields=['status', 'updated_at'])

    return proposed_route
