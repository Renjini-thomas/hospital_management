from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.home, name = 'home'),
    path('main/',views.main,name ="main"),
    path('newbase/',views.newbase,name ="newbase"),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('doctors_dash/',views.doctors_dash,name = "doctors_dash"),
    path('admin_dash/',views.admin_dash,name = "admin_dash"),
    path('admin_overview/',views.admin_overview,name = "admin_overview"),
    path('doctor_list/',views.doctor_list,name = 'doctor_list'),
    path('add_doctors/',views.add_doctors,name = 'add_doctors'),
    path('edit_doctor/<int:pk>/',views.edit_doctor,name = 'edit_doctor'),
    path('delete_doctor/<int:pk>/',views.delete_doctor,name = 'delete_doctor'),
    path('department_list/',views.department_list,name = 'department_list'),
    path('add_department/',views.add_department,name = 'add_department'),
    path('allocate_heads/',views.dep_head_allo,name = 'allocate_heads'),
    path('edit_department/<int:pk>/',views.edit_department,name = 'edit_department'),
    path('delete_department/<int:pk>/',views.delete_department,name = 'delete_department'),
    path('patient_list/',views.patient_list,name = 'patient_list'),
    path('add_patient/',views.add_patient,name = 'add_patient'),
    path('edit_patient/<int:pk>/',views.edit_patient,name = 'edit_patient'),



    path('patient_dash/',views.patient_dash,name = "patient_dash"),
    path('doctors_dash/',views.doctors_dash,name = "doctors_dash"),

    path('select_role/',views.select_role,name = 'select_role'),
    path('register/<str:role>/',views.register,name = 'register'),
    path('login/',views.login_view,name = 'login'),
    path('logout/',views.logout_view,name = 'logout'),

    path('patient_reg_dash/',views.patient_reg_dash,name = 'patient_reg_dash'),
    path('approve_patient/<int:patient_id>/',views.approve_patient,name = 'approve_patient'),
    path('reject_patient/<int:patient_id>/',views.reject_patient,name = 'reject_patient'),



    path('appointment_request/',views.appointment_request,name = 'appointment_request'),
    path('delete_app/<int:appointment_id>/',views.delete_appointment,name = 'delete_app'),
    path('manage_appointments/',views.manage_appointments,name = 'manage_appointments'),
    path('approve_appointments/<int:appointment_id>/',views.approve_appointments,name = 'approve_appointments'),
    path('reject_appointments/<int:appointment_id>/',views.reject_appointments,name = 'reject_appointments'),
    path('admin_appointment_dashboard/',views.admin_appointment_dashboard,name = 'admin_appointment_dashboard'),
    path('doctor_appointment_dashboard/',views.doctor_appointment_dashboard,name = 'doctor_appointment_dashboard'),
    path('appointment_status/',views.appointment_status,name = 'appointment_status'),
    # path('doctor_appointments_details/',views.doctor_appointments_details,name = 'doctor_appointments_details'),
    path('complete_appointment/<int:appointment_id>/',views.complete_appointment,name = 'complete_appointment'),
    path('doctor_credentials/',views.doctor_credentials,name = 'doctor_credentials'),
    path('doctor_medical_records/',views.doctor_medical_records,name = 'doctor_medical_records'),
    path('add_medical_record/<int:appointment_id>/',views.add_medical_record,name = 'add_medical_record'),
    path('patient_medical_records/',views.patient_medical_records,name = 'patient_medical_records'),
    path('view_medical_record/<int:appointment_id>/',views.view_medical_record,name = 'view_medical_record'),
    path('patient_medical_record_detail/<int:appointment_id>/', views.patient_medical_record_detail, name='patient_medical_record_detail'),

    path('patient_all_appointments/',views.patient_all_appointments,name = 'patient_all_appointments'),
    path('doctor_list_for_pat/',views.doctor_list_for_pat,name = 'doctor_list_for_pat'),
    path('verify_otp/',views.verify_otp,name = 'verify_otp'),
    path('send_otp/',views.send_otp,name = 'send_otp'),
    # path('patient_bills/',views.patient_bills,name = 'patient_bills'),
    path('complete_appointment/<int:appointment_id>/',views.complete_appointment,name = 'complete_appointment'),
    path('view_bill/<int:billing_id>/',views.view_bill,name = 'view_bill'),
    path('mark_as_paid/<int:billing_id>/',views.mark_as_paid,name = 'mark_as_paid'),
    path('view_bill_pat/<int:billing_id>/',views.view_bill_pat,name = 'view_bill_pat'),




]