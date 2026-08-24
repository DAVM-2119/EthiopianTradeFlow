from django.core.management.base import BaseCommand
from ml.data.synthetic_data import generate_synthetic_corridor_dataset

class Command(BaseCommand):
    help = "Generates synthetic corridor trip data for ML model training and demonstration."

    def add_arguments(self, parser):
        parser.add_argument('--samples', type=int, default=5000, help="Number of synthetic samples to generate.")

    def handle(self, *args, **options):
        samples = options['samples']
        self.stdout.write(self.style.NOTICE(f"Generating {samples} synthetic corridor trip records..."))
        df = generate_synthetic_corridor_dataset(num_samples=samples)
        self.stdout.write(self.style.SUCCESS(f"Successfully generated dataset with shape {df.shape}."))
