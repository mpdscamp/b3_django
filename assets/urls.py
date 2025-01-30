# assets/urls.py

from django.urls import path
from .views import (
    AssetListView, AssetCreateView, AssetDetailView, 
    update_tunnel_and_frequency, AssetDeleteView
)

urlpatterns = [
    path('', AssetListView.as_view(), name='asset_list'),
    path('create/', AssetCreateView.as_view(), name='asset_create'),
    path('<int:pk>/', AssetDetailView.as_view(), name='asset_detail'),
    path('<int:pk>/update-config/', update_tunnel_and_frequency, name='update_config'),
    path('<int:pk>/delete/', AssetDeleteView.as_view(), name='asset_delete'),
]