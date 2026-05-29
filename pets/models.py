from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Vaccination(models.Model):
    name = models.CharField(max_length=100)
    certificate = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AnimalType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Pet(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(AnimalType, on_delete=models.CASCADE, related_name="pets")
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField(help_text="Age in months")
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="animals/", null=True, blank=True)
    is_available = models.BooleanField(default=True)
    owner = models.ForeignKey(
        "users.BreederShelterProfile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pets",
    )
    vaccination = models.ForeignKey(
        Vaccination, on_delete=models.SET_NULL, null=True, blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave empty if free (shelter animal)",
        validators=[MinValueValidator(0, message="Price cannot be negative.")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.breed})"

    @property
    def is_free(self):
        return self.price is None or self.price == 0

    @property
    def age_display(self):
        if self.age < 12:
            return f"{self.age} mo"
        years = self.age // 12
        months = self.age % 12
        if months:
            return f"{years}y {months}mo"
        return f"{years} yr{'s' if years > 1 else ''}"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]
    REQUEST_TYPE_CHOICES = [
        ("adopt", "Adopt"),
        ("reserve", "Reserve"),
        ("buy", "Buy"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="adoption_requests",
    )
    pet = models.ForeignKey(
        Pet, on_delete=models.CASCADE, related_name="adoption_requests"
    )
    request_type = models.CharField(
        max_length=10, choices=REQUEST_TYPE_CHOICES, default="adopt"
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} → {self.pet} ({self.request_type})"


class PurchaseAgreement(models.Model):
    adoption_request = models.OneToOneField(
        AdoptionRequest, on_delete=models.CASCADE, related_name="agreement"
    )
    buyer_full_name = models.CharField(max_length=200)
    buyer_address = models.TextField()
    buyer_phone = models.CharField(max_length=20)
    seller_full_name = models.CharField(max_length=200)
    agreed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0, message="Price cannot be negative.")],
    )
    terms = models.TextField(blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Agreement #{self.pk} — {self.buyer_full_name}"
