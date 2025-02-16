from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Doctors, Department,Patient,CustomUser,Appointment,MedicalRecord,Billing

class Doctor_form(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = ['first_name','last_name','gender','specialty','contact_number','email','years_of_experience']

class Department_form(forms.ModelForm):
    head_of_department = forms.ModelChoiceField(
        queryset=Doctors.objects.all(),
        required=False,
        empty_label="select head of department",
        label="Head of Department"
    )
    class Meta:
        model = Department
        fields = ['name','description','head_of_department']

class Patient_form(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name','last_name','gender','date_of_birth','address','contact_number','email','blood_group']
        widgets = {
            'date_of_birth':forms.DateInput(attrs={'type':'date'}),
        }


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea)
    contact_number = forms.CharField(max_length=15)
    email = forms.EmailField(required=True)
    blood_group = forms.ChoiceField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
                                             ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'gender', 'date_of_birth',
                  'address', 'contact_number', 'blood_group']

    def save(self, commit=True):
        user = super().save(commit=False)

        # Set the user status to inactive (needs admin approval)
        user.is_active = False  # The user will remain inactive until the admin approves
        user.save()

        # Create the Patient object using the form data
        patient = Patient(
            user=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            gender=self.cleaned_data['gender'],
            date_of_birth=self.cleaned_data['date_of_birth'],
            address=self.cleaned_data['address'],
            contact_number=self.cleaned_data['contact_number'],
            email=self.cleaned_data['email'],
            blood_group=self.cleaned_data['blood_group'],
            status='Pending',  # Set the status to 'Pending' for admin approval
        )
        patient.save()

        return user

#appoinments
class Appoinmentrequestform(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor','appointment_date','appointment_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter doctors to only show active ones
        self.fields['doctor'].queryset = Doctors.objects.filter(user__is_active=True)
        self.fields['doctor'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} - {obj.specialty}"
        # Set widget for appointment_date to use a date picker
        self.fields['appointment_date'].widget = forms.DateInput(attrs={'type': 'date'})
        # Set widget for appointment_time to use a time picker
        self.fields['appointment_time'].widget = forms.TimeInput(attrs={'type': 'time'})

class Medicalrecord_form(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['prescription','medications','treatment_plan','diagnosis']

class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['total_amount']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
        }