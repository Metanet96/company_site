from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from core import models, forms
from core.forms import SignUpForm, PasswordForm

from django.core.exceptions import ValidationError



def index(request):
    company = models.Companye.objects.all()
    if request.user.is_authenticated:
        return render(request, 'core/pages/index.html', {'company': company})
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def company(request):
    company = models.Companye.objects.all()
    if request.user.is_authenticated:
        return render(request, 'core/pages/company.html', {'company': company})
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def branch(request):
    branch = models.Branch.objects.filter(is_deleted=False)
    if request.user.is_authenticated:
        return render(request, 'core/pages/branch.html', {'branch': branch})
    else:
        return redirect('core:auth_sign_in')


# ****************************************************************************

def branch_create(request):
    form = forms.BranchForm
    if request.user.is_authenticated:
        if request.POST:
            form = forms.BranchForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Branch successfully added')
                return redirect('core:branch')
            else:
                messages.warning(request, 'Something was wrong, please try again')
                return redirect(request, 'core/pages/branch_create.html')
    else:
        return redirect('core:auth_sign_in')

    return render(request, 'core/pages/branch_create.html', {
        'form': form,
    })


# ****************************************************************************

def branch_update(request, pk):
    if not models.Branch.objects.filter(is_deleted=False).filter(pk=pk).exists():
        raise Http404
    branch = models.Branch.objects.filter(is_deleted=False).get(pk=pk)
    form = forms.BranchForm
    if request.user.is_authenticated:
        if request.POST:
            form = forms.BranchForm(request.POST, instance=branch)
            if form.is_valid():
                form.save()
                messages.success(request, 'Branch successfully updated')
                return redirect('core:branch')
            else:
                messages.warning(request, 'Something was wrong, please try again')
                return redirect('core:branch_update', branch.pk)
    else:
        return redirect('core:auth_sign_in')

    return render(request, 'core/pages/branch_update.html', {
        'branch': branch,
        'form': form,
    })


# ****************************************************************************

def branch_delete(request, pk):
    if not models.Branch.objects.filter(is_deleted=False).filter(pk=pk).exists():
        raise Http404
    if request.user.is_authenticated:
        branch = models.Branch.objects.filter(is_deleted=False).get(pk=pk)
        staffs_count = models.Staff.objects.filter(branch_id=branch.pk).count()
        if not staffs_count:
            messages.info(request, 'Deleted')
            branch.is_deleted = True
            branch.save()
        else:
            messages.warning(request, 'You can not  deleted this branch')
        return redirect('core:branch')
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def staff(request):
    branches = models.Branch.objects.all()

    if request.user.is_authenticated:
        return render(request, 'core/pages/staff.html', {'branches': branches})
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************
''
def employee(request):
    employees = models.Employee.objects.filter(is_deleted=False)
    if request.user.is_authenticated:
        return render(request, 'core/pages/employee.html', {
            'employees': employees,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def employee_delete(request,pk):
    if not models.Employee.objects.filter(is_deleted=False).filter(pk=pk).exists():
        raise Http404
    if request.user.is_authenticated:
        employee = models.Employee.objects.filter(is_deleted=False).get(pk=pk)
        employee.is_deleted = True
        employee.save()
        messages.info(request,'Employee deleted')
        return redirect('core:employee')
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def employee_create(request):
    gender = models.Gender.objects.all()
    staff = models.Staff.objects.all()
    staff_type = models.StaffType.objects.all()
    form = forms.EmployeeForm
    if request.user.is_authenticated:
        if request.POST:
            form = forms.EmployeeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Employee successfully added')
                return redirect('core:employee')
            else:
                messages.warning(request,'Something was wrong, please try again')
                return redirect(request, 'core/pages/employee_create.html')
        return render(request,'core/pages/employee_create.html',{
            'gender' : gender,
            'staff' : staff,
            'staff_type' : staff_type,
            'form': form,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def employee_update(request,pk):
    if not models.Employee.objects.filter(is_deleted=False).filter(pk=pk).exists():
        raise Http404
    employee = models.Employee.objects.filter(is_deleted=False).get(pk=pk)
    gender = models.Gender.objects.all()
    staff = models.Staff.objects.all()
    staff_type = models.StaffType.objects.all()
    form = forms.EmployeeForm
    if request.user.is_authenticated:
        if request.POST:
            form = forms.EmployeeForm(request.POST, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Employee information successfully updated')
                return redirect('core:employee')
            else:
                messages.warning(request, 'Something was wrong, please try again')
                return redirect('core:employee_update', employee.pk)
    else:
        return redirect('core:auth_sign_in')

    return render(request, 'core/pages/employee_update.html', {
        'gender': gender,
        'staff': staff,
        'staff_type' : staff_type,
        'form': form,
        'pk': pk,
        'employee' : employee,
    })


# ****************************************************************************

def search_results(request):
    if request.user.is_authenticated:
        if ('q' in request.GET):
            query_string = request.GET.get('q')

            search = models.Employee.objects.filter(
                Q(name__icontains=query_string) | Q(surname__icontains=query_string) |Q(staff__name__icontains=query_string))
            counts = search.count()

            if search:
                return render(request, 'core/pages/search_results.html', {
                    'query_string': query_string,
                    'search': search,
                    'counts': counts,
                })
            else:
                messages.warning(request, "Nothing found")
                return render(request, 'core/pages/search_results.html', {
                    'query_string': query_string,
                    'search': search,
                    'counts': counts,
                })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def auth_sign_in(request):
    if request.user.is_authenticated:
        referrer = request.META.get('HTTP_REFERER')
        if not referrer:
            referrer = 'core:index'
        messages.warning(request, 'You already authenticated in system')
        return redirect(referrer)

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('core:index')
        else:
            messages.warning(request, 'Credentials not valid')
            return redirect('core:auth_sign_in')

    return render(request, 'core/pages/auth/sign_in.html')


# ****************************************************************************

def auth_sign_up(request):
    form = SignUpForm(request.POST)

    if request.user.is_authenticated:
        referrer = request.META.get('HTTP_REFERER')
        if not referrer:
            referrer = 'core:index'
        messages.warning(request, 'You already authenticated in system')
        return redirect(referrer)

    if request.method == 'POST':
        email = request.POST.get('email')
        if not models.Employee.objects.filter(email=email).exists():
            messages.warning(request, 'Email is not listed')
            return redirect('core:auth_sign_up')

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, 'You are successfully registered')
            return redirect('core:index')
        else:
            messages.warning(request, 'Something was wrong please try again')

    form = SignUpForm()

    return render(request, 'core/pages/auth/sign_up.html', {'form': form})


# ****************************************************************************

def auth_sign_out(request):
    if request.user.is_anonymous:
        return redirect('core:auth_sign_in')

    logout(request)

    return redirect('core:auth_sign_in')

# ****************************************************************************

def users(request):
    if request.user.is_authenticated:
        users = models.User.objects.all()
        return render(request,'core/pages/users/users.html',{'users': users})
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def password_update(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                login(request, request.user)
                messages.success(request, 'Password successfully changed')
                return redirect('core:users')
        else:
            form = PasswordForm(user=request.user)

        for field in form.fields.values():
            field.help_text = None
    else:
        return redirect('core:auth_sign_in')

    return render(request, 'core/pages/users/password_update.html', {
        'form': form
    })

# ****************************************************************************

def user_delete(request,pk):
    if request.user.is_authenticated:
        if not models.User.objects.filter(pk=pk).exists():
            raise Http404
        models.User.objects.get(pk=pk).delete()
        return redirect('core:auth_sign_in')
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def inbox(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/inbox.html', {
            'message': message,
        'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def inbox_read(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=True).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/inbox.html', {
            'message': message,
        'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def inbox_unread(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/inbox.html', {
            'message': message,
        'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def inbox_detail(request, pk):
    if request.user.is_authenticated:
        if not models.Message.objects.filter(pk=pk).exists():
            raise Http404
        message = models.Message.objects.get(pk=pk)
        message.is_read = True
        message.save()

        message = models.Message.objects.get(pk=pk)
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        if request.POST:
            post_copy = request.POST.copy()
            post_copy['is_send'] = True

        return render(request, 'core/pages/message/inbox_detail.html', {
            'pk': pk,
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def reply (request,pk):
    if not models.Message.objects.filter(pk=pk).exists():
        raise Http404
    form = forms.MessageForm
    message = models.Message.objects.get(pk=pk)

    if request.user.is_authenticated:
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        if request.POST:
            from_user = message.to_id.pk
            to_id = message.from_user.pk
            subject = message.subject
            status = request.POST.get('status')
            is_send = False
            if status == 'send':
                is_send = True
            post_copy = request.POST.copy()
            post_copy['is_send'] = is_send
            post_copy['from_user'] = from_user
            post_copy['to_id'] = to_id
            post_copy['subject'] = subject
            form = forms.MessageForm(post_copy)

            if form.is_valid():
                form.save()
                if is_send:
                    messages.success(request, 'You successfully reply the message')
                else:
                    messages.success(request,'You reply added to drafts')
                return redirect('core:inbox')
            else:
                return redirect('core:inbox')
        return render(request, 'core/pages/message/reply.html', {
            'pk': pk,
            'form': form,
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def sent(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(from_user=request.user).filter(is_send=True).\
            filter(is_deleted=False).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True). \
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/sent.html', {
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def sent_detail(request, pk):
    if not models.Message.objects.filter(pk=pk).exists():
        raise Http404
    message = models.Message.objects.get(pk=pk)

    if request.user.is_authenticated:
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True). \
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/sent_detail.html', {
            'pk': pk,
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def drafts(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(from_user=request.user).filter(is_send=False).\
            filter( is_deleted=False).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/drafts.html', {
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')


# ****************************************************************************

def drafts_detail(request,pk):
    if not models.Message.objects.filter(pk=pk).exists():
        raise Http404
    form = forms.MessageForm
    message = models.Message.objects.get(pk=pk)
    users = models.User.objects.exclude(pk=request.user.pk)

    if request.user.is_authenticated:
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        if request.POST:
            from_user = message.from_user.pk
            status = request.POST.get('status')
            is_send = False
            if status == 'send':
                is_send = True
            post_copy = request.POST.copy()
            post_copy['is_send'] = is_send
            post_copy['from_user'] = from_user

            form = forms.MessageForm(post_copy, request.POST, instance=message)
            if form.is_valid():
                form.save()
                if is_send:
                    messages.success(request,'You successfully send the draft message')
                else:
                    messages.success(request,'You draft message successfully updated')
                return redirect('core:drafts')

        return render(request, 'core/pages/message/drafts_detail.html', {
            'pk' : pk,
            'form' : form,
            'message': message,
            'users' : users,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ***************************************************************************

def trash(request):
    if request.user.is_authenticated:
        message = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=True).order_by('-id')
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/trash.html', {
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************

def trash_detail (request,pk):
    if not models.Message.objects.filter(pk=pk).exists():
        raise Http404
    message = models.Message.objects.get(pk=pk)

    if request.user.is_authenticated:
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        return render(request, 'core/pages/message/trash_detail.html', {
            'pk': pk,
            'message': message,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')


# ****************************************************************************

def compose(request):
    form = forms.MessageForm

    if request.user.is_authenticated:
        users = models.User.objects.exclude(pk=request.user.pk)
        inbox_count = models.Message.objects.filter(to_id=request.user).filter(is_send=True).\
            filter(is_deleted=False).filter(is_read=False).count()
        if request.POST:
            from_user = request.user.pk
            status = request.POST.get('status')
            is_send = False
            if status == "send":
                is_send = True
            post_copy = request.POST.copy()
            post_copy['is_send'] = is_send
            post_copy['from_user'] = from_user
            form = forms.MessageForm(post_copy)

            if form.is_valid():
                form.save()
                if is_send:
                   messages.success(request, "You successfully send message")
                else:
                    messages.success(request, "You message added to draft")
                return redirect('core:compose')
            else:
                return redirect('core:compose')
        return render(request, 'core/pages/message/compose.html', {
            'users': users,
            'form': form,
            'inbox_count' : inbox_count,
        })
    else:
        return redirect('core:auth_sign_in')

# ****************************************************************************