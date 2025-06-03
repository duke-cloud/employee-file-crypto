from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class EncryptedFile(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)


    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     null=True,        # allow null in DB
    #     blank=True        # allow empty in forms
    # )
      original_file = models.FileField(upload_to='original/')
      encrypted_file = models.FileField(upload_to='encrypted/', null=True, blank=True)
      decrypted_file = models.FileField(upload_to='decrypted/', null=True, blank=True)
      uploaded_at = models.DateTimeField(auto_now_add=True)
      

      def __str__(self):
        return f"{self.original_file.name} uploaded by {self.user.username}"








class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    email      = models.EmailField(unique=True)
    position   = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)  # fixed
    date_joined = models.DateField(auto_now_add=True)
    manager    = models.ForeignKey(
        'self', on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
