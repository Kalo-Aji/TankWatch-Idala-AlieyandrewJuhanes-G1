from django.urls import path

from dashboard.features.admin_console.overview.views import CustomAdminHomeView

urlpatterns = [
    path("", CustomAdminHomeView.as_view(), name="home"),
]
