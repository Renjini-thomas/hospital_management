from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin

from .models import Patient, Doctors, Appointment, Room, MedicalRecord, Staff, CustomUser, Billing, Department

# Register your models here.
admin.site.register(Patient)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'specialty', 'contact_number', 'email', 'years_of_experience']
admin.site.register(Doctors,DoctorAdmin)
admin.site.register(Appointment)
admin.site.register(Room)
admin.site.register(MedicalRecord)
admin.site.register(Staff)
class CustomUserAdmin(UserAdmin):
    def delete_model(self, request, obj):
        # Delete all related log entries before deleting the user
        LogEntry.objects.filter(user_id=obj.id).delete()
        obj.delete()
admin.site.register(CustomUser)
admin.site.register(Billing)
admin.site.register(Department)
