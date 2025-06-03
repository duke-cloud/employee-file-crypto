from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import FileUploadForm
from .models import EncryptedFile
from .utils import encrypt_file, decrypt_file
from django.contrib import messages
from .models import Employee, EncryptedFile
from django.db.models import Count, Avg, Q
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File

from django.contrib.auth import login
#from .forms import UserRegisterForm
from .forms import RegisterForm,UserForm
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from cryptography.fernet import Fernet
from .forms import EmployeeForm,EncryptedFileForm
from django.views.decorators.http import require_POST

from django.template.loader import render_to_string
from django.http import JsonResponse
from .decorators import role_required


cipher = settings.FERNET_CIPHER
# Create your views here.


# In production, generate once and store securely!
# Load your Fernet cipher from settings or env
FERNET_KEY = b'your-32-byte-base64-encoded-key-here='
#cipher = Fernet(FERNET_KEY)




def home(request):
    return render(request, 'cryptoapp/home.html')




@login_required
@role_required('Admin')
def admin_dashboard(request):
    # --- POST: encrypt/decrypt via AJAX ---
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        action  = request.POST.get('action')
        file_obj = EncryptedFile.objects.get(pk=file_id)

        if action == 'encrypt' and not file_obj.encrypted_file:
            with file_obj.original_file.open('rb') as f:
                data = f.read()
            encrypted_data = cipher.encrypt(data)
            name = os.path.basename(file_obj.original_file.name) + '.enc'
            file_obj.encrypted_file.save(name, ContentFile(encrypted_data))
            file_obj.save()
            messages.success(request, f'Encrypted "{file_obj.original_file.name}".')

        elif action == 'decrypt' and file_obj.encrypted_file and not file_obj.decrypted_file:
            with file_obj.encrypted_file.open('rb') as f:
                enc_data = f.read()
            decrypted_data = cipher.decrypt(enc_data)
            name = os.path.basename(file_obj.original_file.name) + '.dec'
            file_obj.decrypted_file.save(name, ContentFile(decrypted_data))
            file_obj.save()
            messages.success(request, f'Decrypted "{file_obj.original_file.name}".')

        else:
            messages.warning(request, "Action not applicable.")

        return JsonResponse({
            'success':       True,
            'file_id':       file_id,
            'encrypted_url': file_obj.encrypted_file.url if file_obj.encrypted_file else None,
            'decrypted_url': file_obj.decrypted_file.url if file_obj.decrypted_file else None,
        })

    # --- GET: search & filter ---
    search_query  = request.GET.get('q', '')
    filter_status = request.GET.get('status', '')
    files = EncryptedFile.objects.select_related('user').order_by('-uploaded_at')

    if search_query:
        files = files.filter(
            Q(original_file__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if filter_status == 'encrypted':
        files = files.exclude(encrypted_file='')
    elif filter_status == 'decrypted':
        files = files.exclude(decrypted_file='')
    elif filter_status == 'original':
        files = files.filter(encrypted_file='')

    users = User.objects.all()

    
       



    emp_by_dept = (
        Employee.objects
        .values('department')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    total_files       = EncryptedFile.objects.count()
    num_encrypted     = EncryptedFile.objects.exclude(encrypted_file='').count()
    num_decrypted     = EncryptedFile.objects.exclude(decrypted_file='').count()
    num_original_only = total_files - num_encrypted

    # Flags for empty data
    has_emp_data  = bool(emp_by_dept)
    has_file_data = total_files > 0


# === Analytics ===
    total_employees = Employee.objects.count()
    total_files     = EncryptedFile.objects.count()#UploadedFile.objects.count()

    # average files per user (only users who have uploaded at least one)
    avg_files_per_user = (
        EncryptedFile.objects
        .values('user')
        .annotate(cnt=Count('id'))
        .aggregate(avg=Avg('cnt'))['avg'] or 0
    )

    # top 3 uploaders
    top_uploaders = (
        EncryptedFile.objects
        .values('user__username')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:3]
    )

    # recent 5 uploads
    recent_uploads = (
        EncryptedFile.objects
        .select_related('user')
        .order_by('-uploaded_at')[:5]
    )
# Get file status stats from the EncryptedFile model
    file_stats = {
        'Original': EncryptedFile.objects.filter(original_file__isnull=False).count(),
        'Encrypted': EncryptedFile.objects.filter(encrypted_file__isnull=False).count(),
        'Decrypted': EncryptedFile.objects.filter(decrypted_file__isnull=False).count(),
    }

   
    context = {
        'users':         users,
        'files':         files,
        'search_query':  search_query,
        'filter_status': filter_status,
        'emp_labels':    [e['department'] for e in emp_by_dept],
        'emp_counts':    [e['count']      for e in emp_by_dept],
        'file_stats': {
            'Original':  num_original_only,
            'Encrypted': num_encrypted,
            'Decrypted': num_decrypted,
        },
        'has_emp_data':  has_emp_data,
        'has_file_data': has_file_data,
        'total_employees': total_employees,
        'total_files': total_files,
        'avg_files_per_user': round(avg_files_per_user, 2),
        'top_uploaders': top_uploaders,
        'recent_uploads': recent_uploads,
        'file_labels': list(file_stats.keys()),
        'file_data': list(file_stats.values()),
         
    }

    return render(request, 'admin_dashboard.html', context)





@login_required
@role_required('Employee', 'Admin')
def upload_file(request):
    if request.method == 'POST':
        form = EncryptedFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.user = request.user
            file_obj.save()

            # Encrypt the file after saving
            if file_obj.original_file:
                encrypted_path = encrypt_file(file_obj.original_file.path)
                file_obj.encrypted_file.name = encrypted_path
                file_obj.save()

            messages.success(request, 'File uploaded and encrypted successfully.')
            return redirect('file_detail', file_id=file_obj.id)  # ✅ Correct object reference
    else:
        form = EncryptedFileForm()
    
    return render(request, 'upload.html', {'form': form})













@login_required
@role_required('Employee','Admin')
def file_list(request):
    files = EncryptedFile.objects.filter(user=request.user)
    return render(request, 'cryptoapp/my_files.html', {'files': files})





@login_required
@role_required('Employee','Admin')
def my_files(request):
    if request.method == 'POST':
        if 'action' in request.POST:
            file_id = request.POST.get('file_id')
            action = request.POST.get('action')
            file = get_object_or_404(EncryptedFile, id=file_id, user=request.user)

            if action == 'encrypt' and not file.encrypted_file:
                encrypt_file(file)
            elif action == 'decrypt' and file.encrypted_file and not file.decrypted_file:
                decrypt_file(file)

            return redirect('my_files')

        else:
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.save(commit=False)
                uploaded_file.user = request.user
                uploaded_file.save()
                return redirect('my_files')
    else:
        form = FileUploadForm()

    files = EncryptedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'my_files.html', {'form': form, 'files': files})







@login_required
@role_required('Employee', 'Admin')
def file_detail(request, file_id):
    file_obj = get_object_or_404(EncryptedFile, id=file_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'encrypt':
            encrypted_path = encrypt_file(file_obj.original_file.path)
            file_obj.encrypted_file.name = encrypted_path
            file_obj.save()
            messages.success(request, 'File encrypted successfully.')

        elif action == 'decrypt':
            decrypted_path = decrypt_file(file_obj.encrypted_file.path)
            file_obj.decrypted_file.name = decrypted_path
            file_obj.save()
            messages.success(request, 'File decrypted successfully.')

        return redirect('file_detail', file_id=file_obj.id)

    return render(request, 'file_detail.html', {'file': file_obj})





@login_required
@role_required('Employee','Admin')
def file_list(request):
    files = EncryptedFile.objects.filter(user=request.user)
    return render(request, 'file_list.html', {'files': files})



def register(request):
    if request.user.is_authenticated:
        return redirect('file_list')  # redirect logged-in users

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # optionally log them in directly
            return redirect('file_list')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


def is_admin(user):
    return user.groups.filter(name='Admin').exists()





@login_required
@user_passes_test(is_admin)
@role_required('Admin')
def employee_list(request):
    emps = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': emps})




@staff_member_required
def employee_detail(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': emp})




@login_required
@role_required('Admin')
def employee_update(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated.")
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=emp)
    return render(request, 'employees/employee_form.html', {'form': form})





@login_required
@user_passes_test(is_admin)
def employee_create(request):
    if request.method == 'POST':
        #user_form = UserForm(request.POST)
        emp_form = EmployeeForm(request.POST)

        if  emp_form.is_valid():
            emp = emp_form.save(commit=False)
            emp.save()


        return redirect('employee_list')  # You need to define this view
    else:
        # user_form = UserForm()
        emp_form = EmployeeForm()

        return render(request, 'employees/employee_create.html', {
        # 'user_form': user_form,
        'emp_form': emp_form
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name='Admin').exists())
def employee_delete(request, pk):
    if request.method == 'POST':
        try:
            emp = Employee.objects.get(pk=pk)
            emp.delete()
            return JsonResponse({'success': True})
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not found'})
    return JsonResponse({'success': False, 'error': 'Invalid method'})




def upload_list(request):
    files = EncryptedFile.objects.filter(user=request.user)
    return render(request, 'uploads/upload_list.html', {'files': files})

