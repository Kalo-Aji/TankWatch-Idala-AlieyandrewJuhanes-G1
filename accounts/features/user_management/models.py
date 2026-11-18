from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        OPERATOR = "OPERATOR", "Operator"
        MEMBER = "MEMBER", "Member"
        STUDENT = "STUDENT", "Student / Member"

    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    contact_number = models.CharField(
        max_length=25,
        blank=True,
        default="",
        verbose_name="Contact Number",
    )
    course = models.CharField(max_length=100, blank=True)

    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_operator(self):
        return self.role == self.Role.OPERATOR

    def is_member(self):
        return self.role in (self.Role.MEMBER, self.Role.STUDENT)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != self.Role.ADMIN:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
