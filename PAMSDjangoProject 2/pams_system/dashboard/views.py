from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash, login, logout
from django.db.models import Sum
from datetime import date, timedelta
from calendar import month_abbr

from .models import Payment, Complaint, Profile, MaintenanceRequest, Tenant


# DASHBOARD
@login_required
def home(request):

    tenant = Tenant.objects.filter(user=request.user).first()
    apartment = tenant.apartment if tenant else None

    complaint_count = Complaint.objects.filter(
        user=request.user
    ).count()

    payments = Payment.objects.filter(
        user=request.user
    ).order_by("-date")[:5]

    paid_this_month = Payment.objects.filter(
        user=request.user,
        status="Paid",
        date__month=date.today().month,
        date__year=date.today().year
    ).exists()

    rent_due = apartment.rent if apartment and not paid_this_month else 0

    next_due = date(date.today().year, date.today().month, 30)

    lease_days_left = 0

    if tenant and tenant.lease_end:
        lease_days_left = (tenant.lease_end - date.today()).days

    rent_status = "Paid" if paid_this_month else "Pending"

    monthly_amounts = []
    months = []

    for m in range(1, 13):

        total = Payment.objects.filter(
            user=request.user,
            status="Paid",
            date__month=m,
            date__year=date.today().year
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        monthly_amounts.append(float(total))
        months.append(month_abbr[m])


    neighbour_names = []
    neighbour_payments = []

    if apartment:

        neighbours = Tenant.objects.filter(
            apartment__building=apartment.building
        ).exclude(user=request.user)[:5]

        for n in neighbours:

            total = Payment.objects.filter(
                user=n.user
            ).aggregate(Sum("amount"))["amount__sum"] or 0

            neighbour_names.append(
                f"Apt {n.apartment.number}" if n.apartment else "Unknown"
            )

            neighbour_payments.append(float(total))


    tenant_total = Payment.objects.filter(
        user=request.user
    ).aggregate(Sum("amount"))["amount__sum"] or 0


    if not neighbour_names:

        building_total = Payment.objects.filter(
            user__tenant__apartment__building=apartment.building if apartment else None
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        neighbour_names = ["Building Average"]
        neighbour_payments = [float(building_total)]


    tenant_payment_total = [float(tenant_total)] * len(neighbour_names)


    maintenance_requested = MaintenanceRequest.objects.filter(
        user=request.user,
        status="Pending"
    ).count()

    maintenance_progress = MaintenanceRequest.objects.filter(
        user=request.user,
        status="In Progress"
    ).count()

    maintenance_completed = MaintenanceRequest.objects.filter(
        user=request.user,
        status="Completed"
    ).count()


    maintenance_count = maintenance_requested + maintenance_progress


    maintenance_high = MaintenanceRequest.objects.filter(
        user=request.user,
        priority="High"
    ).exclude(status="Completed").count()

    maintenance_medium = MaintenanceRequest.objects.filter(
        user=request.user,
        priority="Medium"
    ).exclude(status="Completed").count()

    maintenance_low = MaintenanceRequest.objects.filter(
        user=request.user,
        priority="Low"
    ).exclude(status="Completed").count()


    notifications = []

    if rent_due > 0:
        notifications.append(f"Rent of £{rent_due} is due this month")

    if lease_days_left > 0 and lease_days_left <= 30:
        notifications.append(f"Lease ending in {lease_days_left} days")

    if maintenance_progress > 0:
        notifications.append(f"{maintenance_progress} maintenance request(s) in progress")

    pending_complaints = Complaint.objects.filter(
        user=request.user,
        status="Pending"
    ).count()

    if pending_complaints > 0:
        notifications.append(f"{pending_complaints} complaint(s) awaiting response")

    upcoming = MaintenanceRequest.objects.filter(
        user=request.user,
        status="In Progress",
        completion_date__gte=date.today(),
        completion_date__lte=date.today() + timedelta(days=7)
    )

    for m in upcoming:
        notifications.append(f"Maintenance expected by {m.completion_date}")


    context = {

        "tenant": tenant,
        "apartment": apartment,

        "complaint_count": complaint_count,

        "payments": payments,

        "rent_due": rent_due,
        "next_due": next_due,

        "monthly_amounts": monthly_amounts,
        "months": months,

        "neighbour_names": neighbour_names,
        "neighbour_payments": neighbour_payments,
        "tenant_payment_total": tenant_payment_total,

        "maintenance_requested": maintenance_requested,
        "maintenance_progress": maintenance_progress,
        "maintenance_completed": maintenance_completed,

        "maintenance_count": maintenance_count,

        "maintenance_high": maintenance_high,
        "maintenance_medium": maintenance_medium,
        "maintenance_low": maintenance_low,

        "lease_days_left": lease_days_left,
        "rent_status": rent_status,

        "notifications": notifications
    }

    return render(request, "home.html", context)


# PAYMENT HISTORY
@login_required
def history(request):

    payments = Payment.objects.filter(
        user=request.user
    ).order_by("-date")

    monthly_amounts = []
    months = []

    for m in range(1, 13):

        total = Payment.objects.filter(
            user=request.user,
            status="Paid",
            date__month=m,
            date__year=date.today().year
        ).aggregate(Sum("amount"))["amount__sum"] or 0

        monthly_amounts.append(float(total))
        months.append(month_abbr[m])

    return render(request, 'history.html', {
        'payments': payments,
        'months': months,
        'monthly_amounts': monthly_amounts
    })


# RENT
@login_required
def rent(request):

    tenant = Tenant.objects.filter(user=request.user).first()

    rent_amount = tenant.apartment.rent if tenant and tenant.apartment else 450

    if request.method == "POST":

        method = request.POST.get("method")
        amount = request.POST.get("amount")

        Payment.objects.create(

            user=request.user,
            amount=amount,
            method=method,
            status="Paid"

        )

        messages.success(request, "Payment successful")

        return redirect("history")

    return render(request, 'rent.html', {
        'rent_amount': rent_amount
    })


# MAINTENANCE
@login_required
def maintenance(request):

    tenant = Tenant.objects.filter(user=request.user).first()

    if request.method == "POST":

        if not tenant or not tenant.apartment:

            messages.error(request, "No apartment assigned yet")

            return redirect("maintenance")

        MaintenanceRequest.objects.create(

            user=request.user,
            apartment=tenant.apartment,
            issue_type=request.POST.get("issue_type"),
            description=request.POST.get("description"),
            priority=request.POST.get("priority"),
            status="Pending"

        )

        messages.success(request, "Request submitted successfully")

        return redirect("maintenance")

    requests = MaintenanceRequest.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "maintenance.html", {
        "requests": requests
    })


# COMPLAINTS
@login_required
def complaints(request):

    tenant = Tenant.objects.filter(user=request.user).first()

    if request.method == "POST":

        if not tenant or not tenant.apartment:

            messages.error(request, "No apartment assigned yet")

            return redirect("complaints")

        Complaint.objects.create(

            user=request.user,
            apartment=tenant.apartment,
            category=request.POST.get("category"),
            priority=request.POST.get("priority"),
            message=request.POST.get("message"),
            status="Pending"

        )

        messages.success(request, "Complaint submitted successfully")

        return redirect("complaints")

    complaints = Complaint.objects.filter(
        user=request.user
    ).order_by("-date")

    return render(request, "complaints.html", {
        "complaints": complaints
    })

def complaint_list(request):

    complaints = Complaint.objects.filter(user=request.user).order_by("-date")

    return render(request, "complaint_list.html", {
        "complaints": complaints
    })
# PROFILE
@login_required
def profile(request):

    profile = request.user.profile

    tenant = Tenant.objects.filter(user=request.user).first()

    return render(request, 'profile.html', {
        'profile': profile,
        'tenant': tenant
    })


# EDIT PROFILE
@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == 'POST':

        user = request.user

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        profile.phone = request.POST.get('phone')

        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']

        user.save()
        profile.save()

        messages.success(request, "Profile updated")

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'profile': profile
    })


# CHANGE PASSWORD
@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Password changed")

            return redirect("profile")

    else:

        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {
        "form": form
    })


# LOGIN
def user_login(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            login(request, form.get_user())

            return redirect("home")

    else:

        form = AuthenticationForm()

    return render(request, "login.html", {
        "form": form
    })


# RECEIPT
@login_required
def download_receipt(request, payment_id):

    payment = Payment.objects.get(id=payment_id)

    content = f"""

PAYMENT RECEIPT

Date: {payment.date}
Amount: £{payment.amount}
Method: {payment.method}
Status: {payment.status}

"""

    response = HttpResponse(content, content_type='text/plain')

    response['Content-Disposition'] = f'attachment; filename=receipt_{payment.id}.txt'

    return response


# LOGOUT
def user_logout(request):

    logout(request)

    return redirect("login")


# REGISTER
def register(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created")

            return redirect("login")

    else:

        form = UserCreationForm()

    return render(request, "register.html", {
        "form": form
    })