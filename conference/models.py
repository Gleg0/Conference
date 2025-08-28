from django.contrib.auth.models import AbstractUser
from django.db import models

from config import settings


class User(AbstractUser):
    role = models.CharField(max_length=15, default="USER")

class Conference(models.Model):
    title = models.CharField(max_length=63)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    speaker = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="conferences_as_speaker"
    )
    participants = models.ManyToManyField(
        User,
        related_name="conference_participation",
        blank=True
    )

    def __str__(self):
        return self.title

class Paper(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="papers")
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="papers")
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="papers/", null=True, blank=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.paper.title}"

    class Meta:
        unique_together = ("paper", "reviewer")

class Request(models.Model):
    ROLE_CHOICES = [
        ("SPEAKER", "Speaker"),
        ("MODERATOR", "Moderator"),
    ]
    TYPE_CHOICES = [
        ("ROLE_CHANGE", "Role Change"),
        ("CONFERENCE_CREATE", "Conference Create"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    role_requested = models.CharField(max_length=15, choices=ROLE_CHOICES, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    conference_title = models.CharField(max_length=63, null=True, blank=True)
    conference_description = models.TextField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    speaker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="conference_requests")
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("APPROVED", "Approved"), ("REJECTED", "Rejected")],
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} request by {self.user.username}"
