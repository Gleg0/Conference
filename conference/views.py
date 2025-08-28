from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg

from conference.forms import (
    CustomUserCreationForm,
    ConferenceForm,
    ChangeUserRoleForm,
    RoleChangeRequestForm,
    ConferenceRequestForm,
    PaperForm,
    ReviewForm
)
from conference.models import (
    Conference,
    Paper,
    Review,
    User,
    Request
)

User = get_user_model()

def is_admin(user):
    return user.role == "ADMIN"

def is_speaker(user):
    return user.role == "SPEAKER"

def is_moderator(user):
    return user.is_authenticated and user.role == "MODERATOR"

def home(request):
    return render(request, "conference/home.html")

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("conferences:home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "conference/user/login.html", {"form": form})

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            login(request, user)
            return redirect("conferences:home")
    else:
        form = CustomUserCreationForm()
    return render(request, "conference/user/signup.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("conferences:home")

def conference_list(request):
    conferences = Conference.objects.all().order_by("starts_at")
    return render(request, "conference/conference/conferences.html", {"conferences": conferences})

@login_required
def conference_detail(request, pk):
    conference = get_object_or_404(Conference, pk=pk)

    if request.method == "POST":
        conference.participants.add(request.user)
        return redirect("conferences:conference_detail", pk=pk)

    return render(request, "conference/conference/conference_detail.html", {"conference": conference})

@login_required
@user_passes_test(is_admin)
def create_conference(request):
    if request.method == "POST":
        form = ConferenceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("conferences:conferences")
    else:
        form = ConferenceForm()
    return render(request, "conference/conference/create_conference.html", {"form": form})

@login_required
@user_passes_test(is_admin)
def user_list(request):
    role_filter = request.GET.get("role")
    if role_filter:
        users = User.objects.filter(role=role_filter)
    else:
        users = User.objects.exclude(role__in=["ADMIN"])
    return render(request, "conference/user/user_list.html", {"users": users, "role_filter": role_filter})

@login_required
@user_passes_test(is_admin)
def change_role(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = ChangeUserRoleForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect("conferences:user_list")
    else:
        form = ChangeUserRoleForm(instance=user_obj)
    return render(request, "conference/user/change_role.html", {"form": form, "user_obj": user_obj})

@login_required
@user_passes_test(is_moderator)
def moderator_user_list(request):
    role_filter = request.GET.get("role")

    users = User.objects.exclude(role__in=["ADMIN", "MODERATOR"])

    if role_filter in ["USER", "SPEAKER"]:
        users = users.filter(role=role_filter)

    return render(request, "conference/user/moderator_user_list.html", {"users": users, "role_filter": role_filter})

@login_required
@user_passes_test(is_moderator)
def moderator_change_role(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.role == "USER":
        user.role = "SPEAKER"
    elif user.role == "SPEAKER":
        user.role = "USER"

    user.save()
    return redirect("conferences:moderator_user_list")

@login_required
def request_role_change(request):
    if request.method == "POST":
        form = RoleChangeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Request submitted successfully!")
            return redirect("conferences:home")
    else:
        form = RoleChangeRequestForm(user=request.user)
    return render(request, "conference/request/request_role_change.html", {"form": form})

@login_required
@user_passes_test(is_speaker)
def request_conference(request):
    if request.method == "POST":
        form = ConferenceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.speaker = request.user
            req.save()
            return redirect("conferences:home")
    else:
        form = ConferenceRequestForm()
    return render(request, "conference/request/request_conference.html", {"form": form})

@login_required
@user_passes_test(lambda u: is_moderator(u) or is_admin(u))
def request_list(request):
    if is_moderator(request.user):
        requests = Request.objects.exclude(
            type="ROLE_CHANGE", role_requested="MODERATOR"
        ).order_by("-created_at")
    else:
        requests = Request.objects.all().order_by("-created_at")
    return render(request, "conference/request/request_list.html", {"requests": requests})

@login_required
@user_passes_test(lambda u: is_moderator(u) or is_admin(u))
def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if req.type == "CONFERENCE_CREATE":
        from .forms import ConferenceRequestForm

        if req.status == "PENDING":
            if request.method == "POST":
                action = request.POST.get("action")

                if action == "approve":
                    form = ConferenceRequestForm(request.POST, instance=req)
                    if form.is_valid():
                        Conference.objects.create(
                            title=form.cleaned_data['conference_title'],
                            description=form.cleaned_data['conference_description'],
                            starts_at=form.cleaned_data['starts_at'],
                            ends_at=form.cleaned_data['ends_at'],
                            speaker=req.user
                        )
                        req.status = "APPROVED"
                        req.save()
                        return redirect("conferences:request_list")

                elif action == "reject":
                    req.status = "REJECTED"
                    req.save()
                    return redirect("conferences:request_list")

            else:
                form = ConferenceRequestForm(instance=req)

            return render(
                request,
                "conference/request/request_detail_conference.html",
                {"req": req, "form": form}
            )

        return render(
            request,
            "conference/request/request_detail_conference.html",
            {"req": req, "form": None}
        )

    if req.type == "ROLE_CHANGE":
        if req.role_requested == "MODERATOR" and not is_admin(request.user):
            return redirect("conferences:request_list")

        if req.status == "PENDING":
            if request.method == "POST":
                action = request.POST.get("action")
                if action == "approve":
                    if req.role_requested == "MODERATOR" and not is_admin(request.user):
                        return redirect("conferences:request_list")
                    req.user.role = req.role_requested
                    req.user.save()
                    req.status = "APPROVED"
                elif action == "reject":
                    req.status = "REJECTED"
                req.save()
                return redirect("conferences:request_list")

            return render(request, "conference/request/request_detail_role.html", {"req": req})

        return render(request, "conference/request/request_detail_role.html", {"req": req})

    return None

@login_required
def submit_paper(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)

    if request.user not in conference.participants.all():
        messages.error(request, "You must be registered for this conference to submit a paper.")
        return redirect("conferences:conference_detail", pk=conference.id)

    if request.method == "POST":
        form = PaperForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.author = request.user
            paper.conference = conference
            paper.save()
            messages.success(request, "Your paper has been submitted successfully.")
            return redirect("conferences:conference_detail", pk=conference.id)
    else:
        form = PaperForm()

    return render(
        request,
        "conference/paper/submit_paper.html",
        {"conference": conference, "form": form}
    )

@login_required
def conference_papers(request, conference_id):
    conference = get_object_or_404(Conference, id=conference_id)
    papers = conference.papers.all().select_related("author").prefetch_related("reviews")

    papers_with_rating = []
    for paper in papers:
        avg_rating = paper.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        user_has_reviewed = paper.reviews.filter(reviewer=request.user).exists()
        papers_with_rating.append({
            "paper": paper,
            "average_rating": avg_rating,
            "user_has_reviewed": user_has_reviewed
        })

    return render(request, "conference/paper/conference_papers.html", {
        "conference": conference,
        "papers_with_rating": papers_with_rating
    })

@login_required
def my_all_papers(request):
    papers = Paper.objects.filter(author=request.user).select_related("conference")
    return render(request, "conference/paper/my_all_papers.html", {
        "papers": papers
    })

@login_required
def add_review(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)

    if request.user == paper.author:
        return redirect("conferences:conference_papers", conference_id=paper.conference.id)

    existing_review = paper.reviews.filter(reviewer=request.user).first()
    if existing_review:
        return redirect("conferences:paper_reviews", paper_id=paper.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.paper = paper
            review.reviewer = request.user
            review.save()
            return redirect("conferences:paper_reviews", paper_id=paper.id)
    else:
        form = ReviewForm()

    return render(request, "conference/review/add_review.html", {"form": form, "paper": paper})

@login_required
def paper_reviews(request, paper_id):
    paper = get_object_or_404(Paper, id=paper_id)
    reviews = paper.reviews.select_related("reviewer")

    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    user_has_reviewed = reviews.filter(reviewer=request.user).exists()

    return render(request, "conference/review/paper_reviews.html", {
        "paper": paper,
        "reviews": reviews,
        "average_rating": average_rating,
        "user_has_reviewed": user_has_reviewed,
    })

@login_required
def my_all_reviews(request):
    reviews = request.user.reviews.select_related("paper", "paper__conference")

    return render(request, "conference/review/my_all_reviews.html", {
        "reviews": reviews
    })