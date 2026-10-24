from django.contrib import admin

from .filters import filter_products
from .models import Category, Product, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


class ComponentKindFilter(admin.SimpleListFilter):
    title = "Nhóm linh kiện"
    parameter_name = "component_kind"
    kinds = Product.COMPONENT_KIND_CHOICES

    def lookups(self, request, model_admin):
        selected_category = request.GET.get("category__id__exact")
        if selected_category:
            slug = Category.objects.filter(pk=selected_category).values_list("slug", flat=True).first()
            if slug and slug != "linh-kien-pc":
                return ()

        base = model_admin.get_queryset(request)
        options = []
        for kind, label in self.kinds:
            count = filter_products(base, {"category": "linh-kien-pc", "kind": kind}).count()
            if count:
                options.append((kind, f"{label} ({count})"))
        return options

    def queryset(self, request, queryset):
        if self.value():
            return filter_products(
                queryset,
                {"category": "linh-kien-pc", "kind": self.value()},
            )
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "get_component_kind_display", "brand", "price", "stock", "is_active")
    list_filter = ("category", ComponentKindFilter, "brand", "is_active")
    search_fields = ("name", "brand")
    list_editable = ("price", "stock", "is_active")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)
