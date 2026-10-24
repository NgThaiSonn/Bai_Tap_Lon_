from django.db import migrations


def fix_cpu_products(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    products = Product.objects.filter(
        category__slug="linh-kien-pc",
        component_kind="ram",
    )
    for product in products.iterator():
        specs = product.specifications if isinstance(product.specifications, dict) else {}
        normalized_keys = {str(key).casefold() for key in specs}
        if "socket" in normalized_keys and "chipset" not in normalized_keys:
            Product.objects.filter(pk=product.pk).update(component_kind="cpu")


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_product_component_kind"),
    ]

    operations = [
        migrations.RunPython(fix_cpu_products, migrations.RunPython.noop),
    ]
