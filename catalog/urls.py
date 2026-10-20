from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("compare/", views.compare_products, name="compare"),
    path("pc-builder/", views.pc_builder, name="pc_builder"),
    path("category/<slug:slug>/", views.product_list, name="category"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("products/<slug:slug>/review/", views.review_submit, name="review_submit"),
]
