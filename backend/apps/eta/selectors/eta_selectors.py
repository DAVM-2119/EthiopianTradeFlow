from apps.eta.models import ETAPrediction

def get_latest_eta_prediction(shipment_id):
    """
    Retrieves the most recent ETA prediction for a shipment.
    """
    return ETAPrediction.objects.filter(shipment_id=shipment_id).order_by('-predicted_at').first()


def get_eta_prediction_history(shipment_id):
    """
    Retrieves historical list of ETA predictions for a shipment.
    """
    return ETAPrediction.objects.filter(shipment_id=shipment_id).order_by('-predicted_at')
