from django.urls import path
from .views import create_paste, create_paste_ui, fetch_paste, health_check, view_paste_html

urlpatterns = [
    path("api/healthz", health_check),
    path("api/pastes", create_paste),
    path("api/pastes/<uuid:id>", fetch_paste),
    path("p/<uuid:id>", view_paste_html),
    path("", create_paste_ui),



]

