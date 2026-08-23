from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from apps.core.responses import success_response
from apps.core.exceptions import NotFoundException, PermissionDeniedException
from apps.marketplace.models import Load
from apps.pricing.selectors import get_latest_price_quote, get_price_quote_history
from apps.pricing.services import calculate_and_save_price_quote
from apps.pricing.serializers import PriceQuoteSerializer, ContractRateSerializer
from apps.pricing.models import ContractRate

def verify_load_pricing_access(user, load_id):
    load = Load.objects.filter(id=load_id).first()
    if not load:
        raise NotFoundException("Load not found.")
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return load
    if load.shipper == user:
        return load
    # Transporters can view quotes for posted/booked loads
    if getattr(user, 'role', '') == 'TRANSPORTER':
        return load
    raise PermissionDeniedException("You are not authorized to view pricing for this load.")


class LoadPricingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, load_id):
        load = verify_load_pricing_access(request.user, load_id)
        quote = get_latest_price_quote(load.id)
        if not quote:
            quote = calculate_and_save_price_quote(load_id=load.id)

        serializer = PriceQuoteSerializer(quote)
        return success_response(data=serializer.data)


class LoadPricingCalculateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, load_id):
        load = verify_load_pricing_access(request.user, load_id)
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'ADMIN' or load.shipper == request.user):
            raise PermissionDeniedException("Only the load owner or admin can recalculate spot price quotes.")

        quote = calculate_and_save_price_quote(load_id=load.id)
        serializer = PriceQuoteSerializer(quote)
        return success_response(data=serializer.data, message="Price quote recalculated successfully.", status_code=status.HTTP_201_CREATED)


class LoadPricingHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, load_id):
        load = verify_load_pricing_access(request.user, load_id)
        history = get_price_quote_history(load.id)
        serializer = PriceQuoteSerializer(history, many=True)
        return success_response(data=serializer.data)


class ContractRateListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContractRateSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
            return ContractRate.objects.all()
        return ContractRate.objects.filter(shipper=user)

    def perform_create(self, serializer):
        serializer.save(shipper=self.request.user)
