from django.urls import path
from .admin_views import (
    CustomAdminHomeView,
    CustomAdminSystemView,
    CustomAdminTankFleetView,
    CustomAdminUserCreateView,
    CustomAdminUserDeleteView,
    CustomAdminUserListView,
    CustomAdminUserToggleStatusView,
    CustomAdminUserUpdateView,
)

app_name = "custom_admin"

urlpatterns = [
    path("", CustomAdminHomeView.as_view(), name="home"),
    path("users/", CustomAdminUserListView.as_view(), name="user_list"),
    path("users/create/", CustomAdminUserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", CustomAdminUserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/toggle-status/", CustomAdminUserToggleStatusView.as_view(), name="user_toggle_status"),
    path("users/<int:pk>/delete/", CustomAdminUserDeleteView.as_view(), name="user_delete"),
    path("tanks/", CustomAdminTankFleetView.as_view(), name="tanks"),
    path("system/", CustomAdminSystemView.as_view(), name="system"),
]
