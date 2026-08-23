from apps.routing.models import Route, RouteStatusChoices

def get_active_route_for_shipment(shipment_id):
    """
    Retrieves currently active route for a shipment.
    """
    return Route.objects.filter(
        shipment_id=shipment_id,
        status=RouteStatusChoices.ROUTE_ACTIVE
    ).first()


def get_routes_for_shipment(shipment_id):
    """
    Retrieves all route candidates and active routes for a shipment.
    """
    return Route.objects.filter(shipment_id=shipment_id).order_by('optimization_score', '-created_at')


def get_route_by_id(route_id):
    """
    Retrieves route by UUID primary key.
    """
    return Route.objects.filter(id=route_id).first()
