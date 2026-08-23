from apps.marketplace.models import Load

def get_load_by_id(load_id):
    return Load.objects.select_related('shipper').filter(id=load_id).first()


def get_shipper_loads(shipper_user):
    return Load.objects.select_related('shipper').filter(shipper=shipper_user).order_by('-created_at')


def search_loads(queryset=None):
    if queryset is None:
        queryset = Load.objects.select_related('shipper').all()
    return queryset.order_by('-created_at')
