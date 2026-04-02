from django.db import models
from django.contrib.auth.models import User


# ---------------- APARTMENT MODEL ----------------
class Apartment(models.Model):

    TYPE_CHOICES = [
        ("Studio", "Studio"),
        ("1BHK", "1BHK"),
        ("2BHK", "2BHK"),
        ("3BHK", "3BHK"),
    ]

    number = models.CharField(max_length=20)
    building = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    apartment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    rooms = models.IntegerField()

    rent = models.DecimalField(max_digits=8, decimal_places=2)

    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.building} - {self.number}"


# ---------------- TENANT MODEL ----------------
class Tenant(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    lease_start = models.DateField()

    lease_end = models.DateField()

    def __str__(self):
        return self.user.username


# ---------------- PAYMENT MODEL ----------------
class Payment(models.Model):

    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Failed", "Failed"),
    ]

    METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("Online", "Online"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    date = models.DateField(auto_now_add=True)

    method = models.CharField(max_length=50, choices=METHOD_CHOICES)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


# ---------------- MAINTENANCE MODEL ----------------
class MaintenanceRequest(models.Model):

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)

    issue_type = models.CharField(max_length=100)

    description = models.TextField()

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    cost = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    completion_date = models.DateField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.apartment} - {self.issue_type}"


# ---------------- COMPLAINT MODEL ----------------
class Complaint(models.Model):

    CATEGORY_CHOICES = [
        ("Electrical", "Electrical"),
        ("Maintenance", "Maintenance"),
        ("Noise", "Noise"),
        ("Billing", "Billing"),
        ("Neighbour", "Neighbour"),
        ("Other", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Resolved", "Resolved"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    message = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    reply = models.TextField(blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.category}"


# ---------------- PROFILE MODEL ----------------
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20, blank=True)

    photo = models.ImageField(
        upload_to="profile_photos/",
        default="profile_photos/default.png",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username