from django.contrib.auth import login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Avg
from .forms import (
    CustomUserCreationForm,
    ChangeUserRoleForm,
    ConferenceForm,
    PaperForm,
    ReviewForm,
    RoleChangeRequestForm,
    ConferenceRequestForm,
)
from conference.models import Conference, Request, Paper, Review


def get_back_url(request, default_url):
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return referer
    return default_url


User = get_user_model()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = "conferences:home"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class ConferenceListView(ListView):
    model = Conference
    template_name = "conference/conference/conference_list.html"
    context_object_name = "conferences"
    ordering = ["starts_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ConferenceDetailView(LoginRequiredMixin, DetailView):
    model = Conference
    template_name = "conference/conference/conference_detail.html"
    context_object_name = "conference"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = reverse("conferences:conference_list")
        return context

    def post(self, request, *args, **kwargs):
        conference = self.get_object()
        conference.participants.add(request.user)
        return redirect("conferences:conference_detail", pk=conference.pk)


class CreateConferenceView(
    LoginRequiredMixin, UserPassesTestMixin, CreateView
):
    model = Conference
    form_class = ConferenceForm
    template_name = "conference/conference/conference_form.html"
    success_url = reverse_lazy("conferences:conference_list")

    def test_func(self):
        return self.request.user.is_admin


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "conference/user/user_list.html"
    context_object_name = "users"

    def test_func(self):
        return self.request.user.is_admin

    def get_queryset(self):
        role_filter = self.request.GET.get("role")
        if role_filter:
            return User.objects.filter(role=role_filter).exclude(
                role=User.Role.ADMIN
            )
        return User.objects.exclude(role=User.Role.ADMIN)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_filter"] = self.request.GET.get("role")
        context["roles"] = User.Role
        return context


class ChangeRoleView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = ChangeUserRoleForm
    template_name = "conference/user/change_role.html"
    success_url = reverse_lazy("conferences:user_list")

    def test_func(self):
        return self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_obj"] = self.get_object()
        return context


class RequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Request
    template_name = "conference/request/request_list.html"
    context_object_name = "requests"
    ordering = ["-created_at"]

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_moderator

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_moderator:
            return qs.exclude(
                type=Request.Type.ROLE_CHANGE,
                role_requested=Request.Role.MODERATOR,
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_status"] = Request.Status
        context["request_type"] = Request.Type
        return context


class RequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Request
    context_object_name = "req"

    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_moderator

    def get_template_names(self):
        if self.get_object().type == Request.Type.ROLE_CHANGE:
            return ["conference/request/request_detail_role.html"]
        return ["conference/request/request_detail_conference.html"]

    def post(self, request, *args, **kwargs):
        req = self.get_object()
        action = request.POST.get("action")

        if req.type == Request.Type.CONFERENCE_CREATE:
            if action == "approve":
                Conference.objects.create(
                    title=req.conference_title,
                    description=req.conference_description,
                    starts_at=req.starts_at,
                    ends_at=req.ends_at,
                    speaker=req.speaker,
                )
                req.status = Request.Status.APPROVED
            elif action == "reject":
                req.status = Request.Status.REJECTED
            req.save()
            return redirect("conferences:request_list")

        if req.type == Request.Type.ROLE_CHANGE:
            if action == "approve":
                req.user.role = req.role_requested
                req.user.save()
                req.status = Request.Status.APPROVED
            elif action == "reject":
                req.status = Request.Status.REJECTED
            req.save()
            return redirect("conferences:request_list")

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_status"] = Request.Status

        req = self.get_object()
        if req.type == Request.Type.CONFERENCE_CREATE:
            context["form"] = ConferenceRequestForm(instance=req)
        return context


class RoleChangeRequestCreateView(LoginRequiredMixin, CreateView):
    model = Request
    form_class = RoleChangeRequestForm
    template_name = "conference/request/request_role_change.html"
    success_url = reverse_lazy("conferences:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = Request.Type.ROLE_CHANGE
        return super().form_valid(form)


class ConferenceRequestCreateView(
    LoginRequiredMixin, UserPassesTestMixin, CreateView
):
    model = Request
    form_class = ConferenceRequestForm
    template_name = "conference/request/request_conference.html"
    success_url = reverse_lazy("conferences:home")

    def test_func(self):
        return self.request.user.is_speaker

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.speaker = self.request.user
        form.instance.type = Request.Type.CONFERENCE_CREATE
        return super().form_valid(form)


class PaperListView(LoginRequiredMixin, ListView):
    model = Paper
    template_name = "conference/paper/paper_list.html"
    context_object_name = "papers"

    def get_queryset(self):
        qs = Paper.objects.select_related(
            "author", "conference"
        ).prefetch_related("reviews")
        conference_id = self.kwargs.get("conference_id")
        if conference_id:
            qs = qs.filter(conference_id=conference_id)
        else:
            qs = qs.filter(author=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conference_id = self.kwargs.get("conference_id")
        context["conference"] = (
            get_object_or_404(Conference, pk=conference_id)
            if conference_id
            else None
        )

        papers_with_rating = []
        for paper in context["papers"]:
            reviews = paper.reviews.all()
            avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0
            user_has_reviewed = reviews.filter(
                reviewer=self.request.user
            ).exists()
            papers_with_rating.append(
                {
                    "paper": paper,
                    "average_rating": avg_rating,
                    "user_has_reviewed": user_has_reviewed,
                }
            )
        context["papers_with_rating"] = papers_with_rating
        return context


class PaperDetailView(LoginRequiredMixin, DetailView):
    model = Paper
    template_name = "conference/paper/paper_detail.html"
    context_object_name = "paper"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper = self.get_object()

        context["author"] = paper.author
        context["conference"] = paper.conference
        context["abstract"] = paper.abstract
        context["file_url"] = paper.file.url if paper.file else None

        reviews = Review.objects.filter(paper=paper).select_related("reviewer")
        context["reviews"] = reviews
        context["avg_rating"] = (
            reviews.aggregate(Avg("rating"))["rating__avg"] or 0
        )

        return context


class PaperCreateView(LoginRequiredMixin, CreateView):
    model = Paper
    form_class = PaperForm
    template_name = "conference/paper/paper_form.html"

    def form_valid(self, form):
        conference = get_object_or_404(
            Conference, id=self.kwargs["conference_id"]
        )
        form.instance.author = self.request.user
        form.instance.conference = conference
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "conferences:conference_detail", args=[self.object.conference.id]
        )


class PaperUpdateView(LoginRequiredMixin, UpdateView):
    model = Paper
    form_class = PaperForm
    template_name = "conference/paper/paper_form.html"

    def get_queryset(self):
        return Paper.objects.filter(author=self.request.user)

    def get_success_url(self):
        return "conferences:paper_detail", (self.object.pk,)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "conference/review/review_form.html"

    def form_valid(self, form):
        paper = get_object_or_404(Paper, pk=self.kwargs["paper_id"])
        form.instance.reviewer = self.request.user
        form.instance.paper = paper
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("conferences:paper_detail", args=[self.object.paper.pk])


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "conference/review/review_form.html"

    def test_func(self):
        return self.get_object().reviewer == self.request.user

    def get_success_url(self):
        return "conferences:paper_detail", (self.object.paper.pk,)


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = "conference/review/review_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        paper_id = self.kwargs.get("paper_id")
        if paper_id:
            return Review.objects.filter(paper_id=paper_id).select_related(
                "paper", "reviewer"
            )
        return Review.objects.filter(
            reviewer=self.request.user
        ).select_related("paper")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper_id = self.kwargs.get("paper_id")
        if paper_id:
            context["paper"] = get_object_or_404(Paper, pk=paper_id)
            context["conference"] = context["paper"].conference
        else:
            context["paper"] = None
            context["conference"] = None
        return context


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = "conference/review/review_detail.html"
    context_object_name = "review"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = self.get_object()
        context["paper"] = review.paper
        context["conference"] = (
            review.paper.conference if review.paper.conference else None
        )
        return context
