from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import UserManager


class Aadhaar(models.Model):
    aadhaar_number = models.CharField(
        max_length=12, unique=True, null=False, blank=False
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    gender = models.CharField(max_length=10)
    age = models.PositiveIntegerField(null=False, blank=False)
    address = models.TextField()
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    mobile = models.CharField(max_length=14)
    is_eligible = models.BooleanField(default=False)
    has_registered = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
    eth_public_key = models.CharField(
        max_length=42, null=True, blank=True, db_collation="binary"
    )

    def clean(self):
        super().clean()
        # Clean and normalize the email
        if self.email:
            self.email = UserManager.normalize_email(self.email)
            try:
                validate_email(self.email)
            except ValidationError:
                raise ValidationError({"email": "Please enter a valid email address."})
        # Strip whitespace from the eth_public_key
        if self.eth_public_key:
            self.eth_public_key = self.eth_public_key.strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
