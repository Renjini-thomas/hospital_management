import random
from datetime import date
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.db.models import Sum, Q
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import  login as auth_login , authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .forms import Doctor_form, Department_form, Patient_form,CustomUserCreationForm,Appoinmentrequestform,Medicalrecord_form,BillingForm
# from . import models
from .models import Patient, Department, Doctors, Staff, Appointment, Room, Billing, CustomUser,MedicalRecord


# Create your views here.

def home(request):
    return render(request,'index.html')

def newbase(request):
    return render(request,'base.html')

def main(request):
    return render(request,"main.html")

# def login(request):
#     return render(request,"login.html")
#
# def register(request):
#     return render(request,"manage_appointments.html")
@login_required
def doctors_dash(request):
    if request.user.role == 'Doctor':
        try:
            # Try to access the doctor profile linked to the user
            doct = Doctors.objects.get(user=request.user)
            return render(request, "doctors_dash.html", {'doct': doct})
        except Doctors.DoesNotExist:
            # Handle the case where the doctor profile doesn't exist
            return redirect('home')  # Or show an appropriate message
    else:
        return redirect('home')

@login_required
def patient_dash(request):
    return render(request,"patient_dashboard.html")

# def staff_dash(request):
#     return render(request,"staff_dashboard.html")
# admin dashboard
@login_required
def admin_dash(request):
    return render(request,"admin_dashboard.html")
def admin_overview(request):
    t_patient = Patient.objects.count()
    t_doctors = Doctors.objects.count()
    today_appoinments = Appointment.objects.filter(appointment_date=now().date()).count()
    available_rooms = Room.objects.filter(status = "Available").count()
    pending_bills = Billing.objects.filter(payment_status="Pending").count()
    total_revenue = Billing.objects.filter(payment_status="Paid").aggregate(total_amount=Sum("total_amount"))['total_amount'] or 0



    context = {'t_patient':t_patient,
               't_doctors':t_doctors,
               'today_appoinments':today_appoinments,
               'available_rooms':available_rooms,
               'pending_bills':pending_bills,
               'total_revenue':total_revenue

    }

    return render(request,"admin_overview.html",context)
# doctor functionalities
@login_required
def doctor_list(request):
    doctors = Doctors.objects.all()
    return render(request,"doctor_list.html",{"doctors":doctors})
@login_required
def add_doctors(request):
    if request.user.role != 'Admin':
        messages.error(request,'Only admin can add doctors')
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = Doctor_form(request.POST)
        if form.is_valid():
            doctor = form.save(commit=False)
            temp_password = get_random_string(10)
            user = CustomUser.objects.create_user(
                username = doctor.email,
                email = doctor.email,
                password = temp_password,
                role='Doctor'
            )
            doctor.user=user
            doctor.save()

            request.session['new_doctor_credentials'] = {
                'name': f"{doctor.first_name} {doctor.last_name}",
                'username': doctor.email,
                'password': temp_password
            }

            subject = "your doctor account credentials"
            message = (
                f"Hello Dr. {doctor.first_name},\n\n"
                f"Your account has been created. Please log in using the following credentials:\n"
                f"Username: {doctor.email}\n"
                f"Password: {temp_password}\n\n"
                f"Kindly change your password after logging in.\n\n"
                f"Best regards,\nAdmin"
            )
            send_mail(subject,message,'renjini2539thomas@gmail.com',[doctor.email])
            messages.success(request,f'Doctor {doctor.first_name} {doctor.last_name} has been added successfully')


            return redirect('doctor_list')
    else:
        form = Doctor_form()
    return render(request,"add_doctors.html",{'form':form})
@login_required
def edit_doctor(request,pk):
    doctor = get_object_or_404(Doctors, pk =pk)
    if request.method == "POST":
        form = Doctor_form(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = Doctor_form(instance=doctor)
    return render(request,"edit_doctor.html",{'form':form,'doctor':doctor})
@login_required
def doctor_credentials(request):
    cred = request.session.pop('new_doctor_credentials',None)
    if not cred:
        messages.error(request,'no new doctor credentiloas found')
        return redirect('doctor_list')
    return render(request,'doctor_cred.html',{'cred':cred})
@login_required
def delete_doctor(request,pk):
    doctor = get_object_or_404(Doctors,pk=pk)
    doctor.delete()
    return redirect('doctor_list')

# department management
@login_required
def department_list(request):
    dep = Department.objects.all()
    return render(request,"department_list.html",{'dep':dep})
@login_required
def add_department(request):
    if request.method == 'POST':
        form = Department_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form = Department_form()
    return render(request,'add_department.html',{'form':form})
@login_required
def edit_department(request,pk):
    dep = get_object_or_404(Department,pk=pk)
    doctors = Doctors.objects.all()
    if request.method == 'POST':
        form = Department_form(request.POST,instance=dep)
        if form.is_valid():
            form.save()
            return redirect('department_list')
    else:
        form =Department_form(instance=dep)
    return render(request,'edit_department.html',{'form':form,'dep':dep,'doctors':doctors})
@login_required
def delete_department(request,pk):
    dep = get_object_or_404(Department,pk=pk)
    dep.delete()
    return redirect('department_list')
@login_required
def dep_head_allo(request):
    if request.method == 'POST':
        for dep in Department.objects.all():
            doctor_id = request.POST.get(f'head_{dep.department_id}')
            if doctor_id:
                doctor = Doctors.objects.get(pk = doctor_id)
                dep.head_of_department = doctor
                dep.save()
        messages.success(request,'heads of department successfully changed')
        return redirect('department_list')
    departments = Department.objects.all()
    doctors = Doctors.objects.all()
    return render(request, "allocate_heads.html", {'departments': departments, 'doctors': doctors})
# patient management
@login_required
def patient_reg_dash(request):
    pending_patients = Patient.objects.filter(status='Pending')
    print(pending_patients)
    return render(request,'patient_reg_dash.html',{'pending_patients':pending_patients})



@login_required
def approve_patient(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id = patient_id)
        patient.user.is_active = True
        patient.status='Approved'
        patient.user.save()
        patient.save()

        subject = 'Your registration has been approved'
        message = f'hello {patient.first_name},your registration has been approved by the admin you can log into the system.'
        send_mail(subject,message,'renjini2539thomas@gmail.com',[patient.user.email])

        messages.success(request,f'{patient.first_name} {patient.last_name} has been approved')
    except Patient.DoesNotExist:
        messages.error(request,'patient not found')
    return redirect('patient_reg_dash')

@login_required
def reject_patient(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        patient.user.is_active = False
        patient.status = 'Rejected'
        patient.user.save()
        patient.save()

        subject = 'Your registration has been rejected'
        message = f'hello {patient.first_name},your registration has been rejected by the admin you can log into the system.'
        send_mail(subject, message, 'renjini2539thomas@gmail.com', [patient.user.email])

        messages.success(request, f'{patient.first_name} {patient.last_name} has been rejected')
    except Patient.DoesNotExist:
        messages.error(request, 'patient not found')
    return redirect('patient_reg_dash')
@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request,"patient_list.html",{"patients":patients})

@login_required
def add_patient(request):
    if request.method == 'POST':
        form = Patient_form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = Patient_form()
    return render(request,'add_patient.html',{'form':form})
@login_required
def edit_patient(request,pk):
    patient = get_object_or_404(Patient,pk=pk)
    if request.method == "POST":
        form = Patient_form(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = Patient_form(instance=patient)
    return render(request,"edit_patient.html",{'form':form,'patient':patient})

#registartion views

#admin registartion

def select_role(request):
    return render(request,'select_role.html')


def register(request, role):
    # Check if the role is valid
    if role not in ['Patient', 'Doctor', 'Admin']:
        messages.error(request, "Invalid registration role.")
        return redirect('select_role')  # Redirect to role selection page if invalid

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the user and create the Patient object (for Patient role)
            user = form.save()

            # Send email to admin about the new registration (for Patient role)
            if role == 'Patient':
                subject = "New Patient Registration Pending Approval"
                message = f"New patient {user.first_name} {user.last_name} has registered and is awaiting approval."
                send_mail(subject, message, 'renjini2539thomas@gmail.com', ['admin@hospital.com'])

            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')  # Redirect to login page or another page

    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form, 'role': role})  # Pass role to the template


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)

                # Allow superusers to access the Django admin panel
                if user.is_superuser:
                    return redirect('/admin/')

                    # Role-based redirection for regular users
                elif user.role == 'Admin':
                    return redirect('admin_dash')
                elif user.role == 'Doctor':
                    return redirect('doctors_dash')
                elif user.role == 'Patient':
                    return redirect('patient_dash')

            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')
#appointment management by patient

def is_appointment_avail(doctor, appointment_time,appointment_date):
    # Check if there are any appointments for the doctor at the given time
    existing_appointments = Appointment.objects.filter(doctor=doctor, appointment_time=appointment_time,appointment_date=appointment_date)
    if existing_appointments.exists():
        print(f"Appointment already exists for Dr. {doctor} at {appointment_time} on {appointment_date}.")
        return False
    else:
        print(f"Appointment slot is available for Dr. {doctor} at {appointment_time} on {appointment_date}.")
        return True


@login_required
def appointment_request(request):
    if request.user.role == 'Patient':
        if request.method == 'POST':
            form = Appoinmentrequestform(request.POST)
            if form.is_valid():
                appointment_time = form.cleaned_data['appointment_time']
                doctor = form.cleaned_data['doctor']
                appointment_date = form.cleaned_data['appointment_date']
                print(f"Checking availability for doctor {doctor} at {appointment_time} on {appointment_date}")

                # Check if the appointment slot is available
                if is_appointment_avail(doctor, appointment_time,appointment_date):
                    print("Slot is available. Proceeding with the appointment.")
                    # Save the appointment with the patient attached
                    appointment = form.save(commit=False)
                    appointment.patient = request.user.patient  # Ensure patient is correctly assigned
                    appointment.request_status = "Pending"
                    appointment.status = 'Scheduled'
                    appointment.save()

                    # Success message and redirect to the appointment status page
                    messages.success(request, 'Your appointment request has been submitted and is waiting for approval.')
                    return redirect('appointment_status')  # Ensure this URL name is correct
                else:
                    print("time slot is already booked")
                    messages.error(request, "This time slot is already taken. Please choose another time.")
            else:
                print(f"form is not valid:{form.errors}")
        else:
            form = Appoinmentrequestform()  # Initialize the form for GET requests

        return render(request, 'appointment_request.html', {'form': form})

    else:
        return redirect('home')  # Redirect non-patients to home page if they're not allowed to access this view


@login_required
def patient_all_appointments(request):
    if request.user.role == 'Patient':
        patient = request.user.patient
        appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')

        # Attach medical records to appointments
        for appointment in appointments:
            appointment.medical_record = MedicalRecord.objects.filter(appointment=appointment).first()

        return render(request, 'patient_all_appointments.html', {'appointments': appointments})
    else:
        return redirect('patient_dash')


@login_required
def patient_medical_record_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, patient=request.user.patient)

    medical_record = MedicalRecord.objects.filter(appointment=appointment).first()


    return render(request, 'patient_medical_record_detail.html', {
        'appointment': appointment,
        'medical_record': medical_record
    })


@login_required
def delete_appointment(request, appointment_id):
    # Fetch the appointment object by its ID
    appointment = get_object_or_404(Appointment, pk=appointment_id)

    # Check if the logged-in user is the one who created the appointment (patient)
    if appointment.patient == request.user.patient:
        if appointment.request_status == 'Pending':
            # Delete the appointment if it's in 'Pending' status
            appointment.delete()

            messages.success(request, 'Your appointment request has been deleted successfully.')
        else:
            messages.error(request, 'You can only delete appointments that are pending approval.')
    else:
        messages.error(request, 'You are not authorized to delete this appointment.')

    return redirect('appointment_status')
@login_required
def appointment_status(request):
    if request.user.role == 'Patient':
        try:
            appointment = Appointment.objects.filter(patient = request.user.patient).latest('created_at')
            return render(request,'appointment_status.html',{'appointment':appointment})
        except Appointment.DoesNotExist:
            messages.error(request,'you have no appointment requests')
            return redirect('patient_dash')
    else:
        return redirect('home')
#appointment management by admin
def manage_appointments(request):
    appointment = Appointment.objects.filter(request_status='Pending')
    return render(request,'manage_appointments.html',{'appointment':appointment})

@login_required
def admin_appointment_dashboard(request):
    if request.user.role == 'Admin':
        appointments = Appointment.objects.filter(request_status__in=['Pending','Approved'])
        return render(request,'admin_app_dash.html',{'appointments':appointments})
    else:
        return redirect('home')


@login_required
def approve_appointments(request,appointment_id):
    if request.user.role == 'Admin':
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            # Change request status to approved
            appointment.request_status = 'Approved'
            # Mark the status as 'Scheduled'
            appointment.status = 'Scheduled'  # Appointment is officially scheduled now
            appointment.save()

            messages.success(request, 'Appointment has been approved and scheduled.')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')

        return redirect('admin_appointment_dashboard')
    else:
        return redirect('home')

@login_required
def reject_appointments(request,appointment_id):
    if request.user.role == 'Admin':
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            # Change request status to approved
            appointment.request_status = 'Rejected'
            # Mark the status as 'Scheduled'
            appointment.status = 'Cancelled'  # Appointment is officially scheduled now
            appointment.save()

            messages.success(request, 'Appointment has been Rejected.')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found.')

        return redirect('admin_appointment_dashboard')
    else:
        return redirect('home')

# def patient_status(request):
#     appointment = Appointment.objects.filter(patient = request.user.patient).latest('created_at')
#     return render(request,'appointment_status.html',{'appointment':appointment})
#doctor appointment management
@login_required
def doctor_appointment_dashboard(request):
    if request.user.role == 'Doctor':
        # Fetch appointments assigned to the logged-in user
        medical_records = MedicalRecord.objects.filter(doctor__user=request.user)
        appointments = Appointment.objects.filter(doctor__user=request.user, status__in=['Scheduled','Completed'])
        return render(request, 'doctor_app_dash.html', {'appointments': appointments,'medical_records':medical_records})
    else:
        return redirect('home')


@login_required
def complete_appointment(request, appointment_id):
    if request.user.role == 'Doctor':
        try:
            # Fetch the appointment assigned to the logged-in doctor
            appointment = Appointment.objects.get(appointment_id=appointment_id, doctor__user=request.user)
            # Mark the appointment as completed
            appointment.status = 'Completed'
            appointment.save()

            messages.success(request, 'Appointment has been marked as completed.')
        except Appointment.DoesNotExist:
            messages.error(request, 'Appointment not found or you do not have permission to complete this appointment.')

        return redirect('doctor_appointment_dashboard')
    else:
        return redirect('home')


# def doctor_appointments_details(request):
#     doctor = request.user.doctor  # Assuming the logged-in user has a linked doctor profile
#     today = date.today()
#
#     # Get today's appointments
#     today_appointments = Appointment.objects.filter(doctor=doctor, appointment_date=today, status='Scheduled')
#
#     # Get upcoming appointments (appointments scheduled after today)
#     upcoming_appointments = Appointment.objects.filter(doctor=doctor, appointment_date__gt=today, status='Scheduled')
#
#     # Get completed appointments
#     completed_appointments = Appointment.objects.filter(doctor=doctor, status='Completed')
#
#     return render(request, 'doctor_appointments_details.html', {
#         'today_appointments': today_appointments,
#         'upcoming_appointments': upcoming_appointments,
#         'completed_appointments': completed_appointments,
#     })

#medical records
@login_required
def doctor_medical_records(request):
    """View for doctors to see and add medical records for their assigned patients."""
    doctor = get_object_or_404(Doctors, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor, status='Completed')
    medical_records = MedicalRecord.objects.filter(doctor=doctor)

    return render(request, 'doctor_medical_records.html', {
        'appointments': appointments,
        'medical_records': medical_records
    })

@login_required
def add_medical_record(request, appointment_id):
    """Allow doctors to add a medical record for a patient after an appointment."""
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, doctor__user=request.user)

    if request.method == 'POST':
        form = Medicalrecord_form(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            medical_record.patient = appointment.patient
            medical_record.doctor = appointment.doctor
            medical_record.appointment = appointment
            medical_record.visit_date = appointment.appointment_date
            medical_record.save()
            messages.success(request, "Medical record added successfully.")
            return redirect('doctor_appointment_dashboard')
    else:
        form = Medicalrecord_form()

    return render(request, 'add_medical_record.html', {'form': form, 'appointment': appointment})


@login_required
def view_medical_record(request, appointment_id):

    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, doctor__user=request.user)

    record = get_object_or_404(MedicalRecord, patient=appointment.patient, doctor__user=request.user)

    return render(request, 'view_medical_record.html', {
        'appointment': appointment,
        'record': record
    })

@login_required
def patient_medical_records(request):
    """View for patients to see their own medical records."""
    medical_records = MedicalRecord.objects.filter(patient=request.user.patient)
    return render(request, 'patient_medical_records.html', {'medical_records': medical_records})

def doctor_list_for_pat(request):
    doctors = Doctors.objects.all()
    deps = Department.objects.all()
    return render(request,"doctor_list_for_pat.html",{'doctors':doctors,'deps':deps})

OTP_STORAGE = {}
def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email = email).first()

        if user:
            otp = random.randint(100000,999999)
            OTP_STORAGE[email] = otp
            send_mail(
                "password reset OTP",
                f"your otp for password reset : {otp}",
                "renjini2539thomas@gmail.com",
                [email],
            )
            request.session['reset_email']=email
            messages.success(request,'OTP sent to your email.')
            return redirect('verify_otp')
        else:
            messages.error(request,'no user found with this email')
    return render(request,"send_otp.html")
def verify_otp(request):
    if request.method == "POST":
        email = request.session.get('reset_email')
        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("password")

        if email in OTP_STORAGE and OTP_STORAGE[email] == int(entered_otp):
            user = CustomUser.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            del OTP_STORAGE[email]

            messages.success(request,"password reset successfully")
            return redirect('login')
        else:
            messages.error(request,"invalid OTP")

    return render(request,'verify_otp.html')

@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id, doctor__user=request.user)
    if request.method == "POST":
        form = BillingForm(request.POST)
        if form.is_valid():
            total_amount = Decimal(str(form.cleaned_data['total_amount']))

            # Create the bill if it doesn't exist
            bill, created = Billing.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'patient': appointment.patient,
                    'total_amount': total_amount,
                    'payment_status': 'Pending'
                }
            )
            if not created:
                bill.total_amount = total_amount  # Update the amount if bill exists
                bill.save()

            # Mark appointment as completed
            appointment.status = 'Completed'
            appointment.save()

            messages.success(request, "Appointment completed and bill created successfully.")
            return redirect('doctor_appointment_dashboard')

    else:
        form = BillingForm()

    return render(request, 'enter_bill.html', {'form': form, 'appointment': appointment})

@login_required
def mark_as_paid(request, billing_id):
    bill = get_object_or_404(Billing , billing_id = billing_id)

    if request.user.role == "Admin":
        bill.payment_status = "Paid"
        bill.amount_paid = bill.total_amount
        bill.amount_due = 0.0
        bill.save()
        messages.success(request, "Bill marked as Paid.")

    return redirect('admin_appointment_dashboard')

@login_required
def view_bill(request, billing_id):
    bill = get_object_or_404(Billing, billing_id=billing_id)
    return render(request, 'view_bill.html', {'bill': bill})

# @login_required
# def patient_bills(request):
#     # Ensure only patients can view their own bills
#     if not hasattr(request.user, 'patient'):
#         messages.error(request, "Access denied.")
#         return redirect('home')  # Redirect if not a patient
#
#     # Get all bills for the logged-in patient along with their appointment details
#     bills = Billing.objects.filter(patient=request.user.patient).select_related('appointment')
#
#     return render(request, 'patient_bills.html', {'bills': bills})

@login_required
def view_bill_pat(request, billing_id):
    bill = get_object_or_404(Billing, billing_id=billing_id)

    # Ensure only the patient who owns the bill can access it
    if request.user.role == "Patient" and bill.patient.user != request.user:
        messages.error(request, "You are not authorized to view this bill.")
        return redirect('home')

    return render(request, 'view_bill_pat.html', {'bill': bill})
