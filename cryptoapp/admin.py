




# cryptoapp/admin.py

from django.contrib import admin
from django.contrib.auth.models import User  # <— corrected import
from .models import EncryptedFile, Employee,Department



#admin.site.register(Employee)
admin.site.register(Department)





@admin.register(EncryptedFile)
class EncryptedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'original_file', 'encrypted_file', 'decrypted_file', 'uploaded_at')
    list_filter  = ('user',)
    search_fields = ('original_file', 'user__username')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'position', 'department', 'manager')
    list_filter  = ('department',)
    search_fields = ('first_name', 'last_name', 'email')
