from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from apps.shipments.models import Shipment

@database_sync_to_async
def is_user_authorized_for_shipment(user, shipment_id):
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return True

    shipment = Shipment.objects.filter(id=shipment_id).first()
    if not shipment:
        return False

    return (
        shipment.shipper_id == user.id or
        shipment.transporter_id == user.id or
        shipment.driver_id == user.id
    )


class TrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time shipment GPS tracking.
    Endpoint: /ws/v1/shipments/<shipment_id>/tracking/
    Subscribes connected authorized client to channel group: shipment_<shipment_id>
    """
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.shipment_id = self.scope['url_route']['kwargs'].get('shipment_id')
        if not self.shipment_id:
            await self.close(code=4000)
            return

        authorized = await is_user_authorized_for_shipment(self.user, self.shipment_id)
        if not authorized:
            await self.close(code=4003)
            return

        self.group_name = f"shipment_{self.shipment_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def tracking_position_updated(self, event):
        """
        Handler for 'tracking.position_updated' broadcast events.
        """
        await self.send_json(event)
