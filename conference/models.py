from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MODERATOR = "MODERATOR", "Moderator"
        SPEAKER = "SPEAKER", "Speaker"
        USER = "USER", "User"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_speaker(self):
        return self.role == self.Role.SPEAKER

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class Conference(models.Model):
    title = models.CharField(max_length=63)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    speaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conferences_as_speaker"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conference_participation",
        blank=True
    )

    def __str__(self):
        return self.title


class Paper(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="papers"
    )
    conference = models.ForeignKey(
        Conference,
        on_delete=models.CASCADE,
        related_name="papers"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="papers/", null=True, blank=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.paper.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["paper", "reviewer"], name="unique_review_per_paper")
        ]


class Request(models.Model):
    class Role(models.TextChoices):
        SPEAKER = "SPEAKER", "Speaker"
        MODERATOR = "MODERATOR", "Moderator"

    class Type(models.TextChoices):
        ROLE_CHANGE = "ROLE_CHANGE", "Role Change"
        CONFERENCE_CREATE = "CONFERENCE_CREATE", "Conference Create"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests"
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices
    )
    role_requested = models.CharField(
        max_length=15,
        choices=Role.choices,
        null=True,
        blank=True
    )
    reason = models.TextField(null=True, blank=True)
    conference_title = models.CharField(max_length=63, null=True, blank=True)
    conference_description = models.TextField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    speaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conference_requests"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} request by {self.user.username}"
