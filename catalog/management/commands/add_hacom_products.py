from django.core.management.base import BaseCommand

from catalog.hacom_products import fill_seed_product_images, import_hacom_products


class Command(BaseCommand):
    help = "Add or update the curated HACOM product snapshot."

    def handle(self, *args, **options):
        count = import_hacom_products()
        image_count = fill_seed_product_images()
        self.stdout.write(self.style.SUCCESS(
            f"Imported or updated {count} HACOM products; added images to {image_count} demo products."
        ))
