from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User, Conference, Request, Paper, Review


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ConferenceForm(forms.ModelForm):
    class Meta:
        model = Conference
        fields = ["title", "description", "starts_at", "ends_at", "speaker"]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "speaker": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["speaker"].queryset = User.objects.filter(role="SPEAKER")

class ChangeUserRoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["role"]
        widgets = {
            "role": forms.Select(choices=[("USER", "User"), ("MODERATOR", "Moderator"), ("SPEAKER", "Speaker")], attrs={"class": "form-select"})
        }

class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["role_requested", "reason"]
        widgets = {
            "role_requested": forms.Select(attrs={"class": "form-select"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        req = super().save(commit=False)
        req.type = "ROLE_CHANGE"
        if self.user:
            req.user = self.user
        if commit:
            req.save()
        return req

class ConferenceRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ["conference_title", "conference_description", "starts_at", "ends_at"]
        widgets = {
            "conference_title": forms.TextInput(attrs={"class": "form-control"}),
            "conference_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def save(self, commit=True):
        req = super().save(commit=False)
        req.type = "CONFERENCE_CREATE"
        if commit:
            req.save()
        return req

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ["title", "abstract", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "abstract": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
