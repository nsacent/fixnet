from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    register_client,
    register_technician,
)


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/client/", register_client, name="register_client"),
    path("register/technician/", register_technician, name="register_technician"),
]