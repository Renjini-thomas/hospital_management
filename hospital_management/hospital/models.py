from decimal import Decimal

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Doctor', 'Doctor'),
        ('Patient', 'Patient')
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Patient', editable=False)  # Prevent manual editing

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'Admin'  # Ensure superusers are always Admin
        elif not self.pk:  # Only set role on creation
            self.role = self.role or 'Patient'  # Default role as Patient
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Patient(models.Model):
    PATIENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    date_of_birth = models.DateField()
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, null=True, blank=True)
    status = models.CharField(max_length = 10,choices=PATIENT_STATUS_CHOICES,default = 'Pending')
    blood_group = models.CharField(max_length=5, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Doctors(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    specialty = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    years_of_experience = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.user:  # Only create a new user if it doesn't exist
            if not CustomUser.objects.filter(email=self.email).exists():  # Check if email exists
                temp_password = make_password(get_random_string(12))  # Secure password
                user = CustomUser.objects.create_user(
                    username=self.email,
                    email=self.email,
                    password=temp_password,
                    role='Doctor'
                )
                self.user = user  # Link user to doctor
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Appointment(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])
    request_status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.appointment_id} for {self.patient.first_name} with Dr. {self.doctor.first_name}"
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    head_of_department = models.ForeignKey(Doctors, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=[('General', 'General'), ('Private', 'Private'), ('ICU', 'ICU')])
    status = models.CharField(max_length=20, choices=[('Available', 'Available'), ('Occupied', 'Occupied')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MedicalRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    prescription = models.TextField(null=True, blank=True)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    medications = models.TextField()  # Use ManyToMany if needed
    visit_date = models.DateField()
    medical_report = models.FileField(upload_to='medical_reports/', null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Draft', 'Draft'), ('Finalized', 'Finalized')],
        default='Draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record {self.record_id} - {self.patient.first_name} {self.patient.last_name} ({self.visit_date})"

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    position = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

class Billing(models.Model):
    billing_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,null=True,blank=True)
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE,null=True,blank=True)  # Link doctor
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE,null=True,blank=True)  # Link to appointment
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Doctor sets the charge
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    billing_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Partially Paid', 'Partially Paid'), ('Paid', 'Paid')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_amount is not None:
            # Ensure amount_paid is treated as Decimal
            self.amount_paid = Decimal(str(self.amount_paid))
            self.amount_due = self.total_amount - self.amount_paid

            if self.amount_due <= 0:
                self.payment_status = 'Paid'
            elif self.amount_due < self.total_amount:
                self.payment_status = 'Partially Paid'
            else:
                self.payment_status = 'Pending'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill {self.billing_id} - {self.patient.first_name} {self.patient.last_name} - {self.payment_status}"


