from django.db import migrations


NEW_CATEGORIES = {
    "Linh kiện PC": ("linh-kien-pc", "CPU, mainboard, nguồn, RAM, SSD và card đồ họa cho máy tính để bàn."),
    "Laptop": ("laptop", "Máy tính xách tay cho học tập, công việc và giải trí."),
    "PC văn phòng": ("pc-van-phong", "Máy tính bộ ổn định cho công việc và học tập."),
    "PC gaming": ("pc-gaming", "Máy tính bộ hiệu năng cao dành cho chơi game."),
    "Màn hình": ("man-hinh", "Màn hình máy tính cho công việc, sáng tạo và giải trí."),
    "Phụ kiện PC": ("phu-kien-pc", "Chuột, bàn phím, camera, tai nghe và micro."),
}
LEGACY_COMPONENTS = ("CPU", "Mainboard", "Nguồn (PSU)", "RAM", "SSD", "VGA")


def consolidate_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    db = schema_editor.connection.alias
    categories = Category.objects.using(db)
    for name, (slug, description) in NEW_CATEGORIES.items():
        categories.get_or_create(name=name, defaults={"slug": slug, "description": description})
    components = categories.get(name="Linh kiện PC")
    for old_name in LEGACY_COMPONENTS:
        old = categories.filter(name=old_name).first()
        if old:
            old.products.using(db).update(category_id=components.pk)
            old.delete(using=db)


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]
    operations = [migrations.RunPython(consolidate_categories, migrations.RunPython.noop)]
