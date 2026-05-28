from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class BreederShelterProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="organization_profile"
    )
    name = models.CharField(max_length=100)
    city = models.ForeignKey(
        "pets.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_shelter = models.BooleanField(
        default=False,
        help_text="Check if this is a shelter (animals are free). Uncheck for breeders."
    )

    def __str__(self):
        kind = "Shelter" if self.is_shelter else "Breeder"
        return f"{self.name} ({kind})"

    @property
    def kind_label(self):
        return "Shelter" if self.is_shelter else "Breeder"
