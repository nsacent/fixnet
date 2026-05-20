from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("request-success/", views.request_success, name="request_success"),

    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("technician/profile/edit/", views.edit_technician_profile, name="edit_technician_profile"),
    path("technician/dashboard/", views.technician_dashboard, name="technician_dashboard"),

    path("technician/requests/<int:request_id>/accept/", views.accept_request, name="accept_request"),
    path("technician/requests/<int:request_id>/start/", views.start_request, name="start_request"),
    path("technician/requests/<int:request_id>/", views.technician_request_detail, name="technician_request_detail"),
    path("technician/requests/<int:request_id>/complete/", views.complete_request, name="complete_request"),

    path("client/requests/<int:request_id>/review/", views.leave_review, name="leave_review"),
    path("client/requests/<int:request_id>/", views.client_request_detail, name="client_request_detail"),

    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"), 
    path("dashboard/admin/requests/<int:request_id>/assign/", views.admin_assign_request, name="admin_assign_request"),
    path("dashboard/admin/requests/<int:request_id>/", views.admin_request_detail, name="admin_request_detail"),
    path("dashboard/admin/requests/<int:request_id>/status/", views.admin_update_request_status, name="admin_update_request_status"),
    path("dashboard/admin/requests/<int:request_id>/notes/",views.admin_update_request_notes,name="admin_update_request_notes"),
]