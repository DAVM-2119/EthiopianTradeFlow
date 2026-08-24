from django.core.management.base import BaseCommand
from ml.eta.train import train_eta_model

class Command(BaseCommand):
    help = "Trains and registers Scikit-Learn GradientBoostingRegressor model for ETA prediction."

    def add_arguments(self, parser):
        parser.add_argument('--model-version', type=str, default='eta-v1', help="Model version identifier.")

    def handle(self, *args, **options):
        version = options['model_version']
        self.stdout.write(self.style.NOTICE(f"Training ETA ML model version {version}..."))
        result = train_eta_model(version=version)
        metrics = result['metrics']
        self.stdout.write(self.style.SUCCESS(f"Successfully trained {version}! MAE={metrics['mae']} mins, R²={metrics['r2']}"))
