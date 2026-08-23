from apps.fleet.models import Vehicle, VehicleStatusChoices
from apps.profiles.models import TransporterProfile
from apps.fleet.serializers import VehicleSerializer

def create_vehicle(user, data):
    transporter, _ = TransporterProfile.objects.get_or_create(user=user)
    serializer = VehicleSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.save(transporter=transporter)


def update_vehicle(vehicle, data):
    serializer = VehicleSerializer(vehicle, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


def deactivate_vehicle(vehicle):
    vehicle.status = VehicleStatusChoices.INACTIVE
    vehicle.save()
    return vehicle
