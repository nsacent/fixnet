from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("request-success/", views.request_success, name="request_success"),

    path("client/dashboard/", views.client_dashboard, name="client_dashboard"),
    path("technician/profile/edit/", views.edit_technician_profile, name="edit_technician_profile"),
    path("technician/dashboard/", views.technician_dashboard, name="technician_dashboard"),
    path("technicians/<int:technician_id>/",views.technician_profile_detail,name="technician_profile_detail"),

    path("technician/requests/<int:request_id>/accept/", views.accept_request, name="accept_request"),
    path("technician/requests/<int:request_id>/start/", views.start_request, name="start_request"),
    path("technician/requests/<int:request_id>/", views.technician_request_detail, name="technician_request_detail"),
    path("technician/requests/<int:request_id>/complete/", views.complete_request, name="complete_request"),
    path("technician/jobs/history/", views.technician_job_history,name="technician_job_history",),

    path("client/requests/<int:request_id>/review/", views.leave_review, name="leave_review"),
    path("client/requests/<int:request_id>/", views.client_request_detail, name="client_request_detail"),
    path("client/requests/<int:request_id>/payment-proof/", views.client_upload_payment_proof, name="client_upload_payment_proof"),
    path("client/requests/history/", views.client_request_history,name="client_request_history",),

    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"), 
    path("dashboard/admin/requests/<int:request_id>/assign/", views.admin_assign_request, name="admin_assign_request"),
    path("dashboard/admin/requests/<int:request_id>/", views.admin_request_detail, name="admin_request_detail"),
    path("dashboard/admin/requests/<int:request_id>/status/", views.admin_update_request_status, name="admin_update_request_status"),
    path("dashboard/admin/requests/<int:request_id>/notes/",views.admin_update_request_notes,name="admin_update_request_notes"),
    path("dashboard/admin/requests/<int:request_id>/price/", views.admin_update_final_price, name="admin_update_final_price"),
    path("dashboard/admin/requests/<int:request_id>/payment/", views.admin_update_payment, name="admin_update_payment"),
    path("dashboard/admin/requests/",views.admin_request_list,name="admin_request_list",),
    path("dashboard/admin/live-stats/",views.admin_live_stats,name="admin_live_stats",),

    path("client/requests/<int:request_id>/cancel/", views.client_cancel_request, name="client_cancel_request"),

    path("dashboard/admin/requests/<int:request_id>/cancel/", views.admin_cancel_request, name="admin_cancel_request"),

    path("dashboard/admin/requests/<int:request_id>/technician-payout/",views.admin_update_technician_payout,name="admin_update_technician_payout"),

    path("dashboard/admin/live-latest-requests/",views.admin_live_latest_requests,name="admin_live_latest_requests",),
    path(
        "dashboard/admin/live-pending-proofs/",
        views.admin_live_pending_proofs,
        name="admin_live_pending_proofs",
    ),
    path(
        "dashboard/admin/live-unpaid-payouts/",
        views.admin_live_unpaid_payouts,
        name="admin_live_unpaid_payouts",
    ),

    path(
        "dashboard/admin/reports/",
        views.admin_reports,
        name="admin_reports",
    ),

    path(
        "dashboard/admin/reports/export/",
        views.admin_reports_export_csv,
        name="admin_reports_export_csv",
    ),

    path(
        "dashboard/admin/reports/export-excel/",
        views.admin_reports_export_excel,
        name="admin_reports_export_excel",
    ),

    path(
        "dashboard/admin/reports/outstanding-balances/",
        views.admin_outstanding_balances_report,
        name="admin_outstanding_balances_report",
    ),
    
]