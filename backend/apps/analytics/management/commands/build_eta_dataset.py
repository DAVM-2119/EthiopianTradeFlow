from django.core.management.base import BaseCommand
from ml.data.dataset_builders import build_eta_training_dataset

class Command(BaseCommand):
    help = "Builds and exports the ETA training dataset CSV."

    def add_arguments(self, parser):
        parser.add_argument('--samples', type=int, default=5000, help="Number of synthetic samples to include.")

    def handle(self, *args, **options):
        samples = options['samples']
        self.stdout.write(self.style.NOTICE(f"Building ETA training dataset with {samples} samples..."))
        df = build_eta_training_dataset(num_synthetic_samples=samples)
        self.stdout.write(self.style.SUCCESS(f"Dataset built successfully with {len(df)} records."))
