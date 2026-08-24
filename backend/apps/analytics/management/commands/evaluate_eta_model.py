from django.core.management.base import BaseCommand
from ml.eta.evaluate import evaluate_eta_model

class Command(BaseCommand):
    help = "Evaluates current active ML model vs deterministic rule-based benchmark."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Evaluating active ETA ML model benchmark..."))
        result = evaluate_eta_model()
        if 'error' in result:
            self.stdout.write(self.style.ERROR(result['error']))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ML MAE: {result['ml_mae_minutes']} mins | Rule MAE: {result['rule_based_mae_minutes']} mins | Improvement: {result['mae_improvement_pct']}%"
                )
            )
