from django.urls import path
from . import views

urlpatterns = [
    # Вход
    path('', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Для поставщиков
    path('supplier/<int:supplier_id>/', views.supplier_form, name='supplier_form'),
    path('success/', views.success, name='success'),
    # Работа с токенами
    path('get_supplier_token/<int:supplier_id>/', views.get_supplier_token, name='get_supplier_token'),
    path('supplier_form/<int:supplier_id>/<uuid:token>/', views.supplier_form, name='supplier_form'),

    # Итоговые таблицы
    path('product_supplier_table/', views.product_supplier_table, name='product_supplier_table'),
    path('prices/', views.price_list, name='price_list'),

    # Category
    path('category_list/', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    
    # Supplier
    path('add_supplier/', views.add_supplier, name='add_supplier'),  
    path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
    path('supplier_list/', views.supplier_list, name='supplier_list'),
    path('toggle_supplier_visibility/<int:supplier_id>/', views.toggle_supplier_visibility, name='toggle_supplier_visibility'),
    
    # Product
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product_list/', views.product_list, name='product_list'),
    
    # Excel
    path('upload/', views.upload_excel, name='upload_excel'),
    path("export-prices/", views.export_prices_to_excel, name="export_prices"),
    path('export/', views.export_to_excel, name='export_to_excel'),

    path('product-supplier-table/', views.product_supplier_table, name='product_supplier_table'),
    
    path('best-prices-by-category/', views.best_prices_by_category, name='best_prices_by_category'),
    path('price-history/<int:product_id>/', views.price_history_view, name='price_history'),

]
