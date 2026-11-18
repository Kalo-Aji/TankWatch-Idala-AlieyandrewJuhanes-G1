from django.urls import path

from dashboard.features.admin_console.user_management.views import (
    CustomAdminUserCreateView,
    CustomAdminUserDeleteView,
    CustomAdminUserListView,
    CustomAdminTankLevelView,
    CustomAdminUserToggleStatusView,
    CustomAdminUserUpdateView,
)

urlpatterns = [
    path("users/", CustomAdminUserListView.as_view(), name="user_list"),
    path("users/create/", CustomAdminUserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", CustomAdminUserUpdateView.as_view(), name="user_edit"),
    path(
        "users/<int:pk>/toggle-status/",
        CustomAdminUserToggleStatusView.as_view(),
        name="user_toggle_status",
    ),
    path(
        "users/<int:pk>/delete/",
        CustomAdminUserDeleteView.as_view(),
        name="user_delete",
    ),
    path(
        "users/<int:pk>/tank-level/",
        CustomAdminTankLevelView.as_view(),
        name="user_tank_level",
    ),
]
