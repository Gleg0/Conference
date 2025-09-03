from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path
from conference import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

app_name = "conferences"

urlpatterns = [
    # Home
    path(
        "",
        TemplateView.as_view(template_name="conference/home.html"),
        name="home",
    ),
    # Auth
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    # Conferences
    path(
        "conferences/",
        views.ConferenceListView.as_view(),
        name="conference_list",
    ),
    path(
        "conferences/<int:pk>/",
        views.ConferenceDetailView.as_view(),
        name="conference_detail",
    ),
    path(
        "conferences/create/",
        views.CreateConferenceView.as_view(),
        name="conference_create",
    ),
    # Users
    path("users/", views.UserListView.as_view(), name="user_list"),
    path(
        "users/<int:pk>/change-role/",
        views.ChangeRoleView.as_view(),
        name="change_user_role",
    ),
    # Requests
    path("requests/", views.RequestListView.as_view(), name="request_list"),
    path(
        "requests/<int:pk>/",
        views.RequestDetailView.as_view(),
        name="request_detail",
    ),
    path(
        "requests/role/create/",
        views.RoleChangeRequestCreateView.as_view(),
        name="request_role_create",
    ),
    path(
        "requests/conference/create/",
        views.ConferenceRequestCreateView.as_view(),
        name="request_conference_create",
    ),
    # Papers
    path("papers/", views.PaperListView.as_view(), name="paper_user_list"),
    path(
        "conferences/<int:conference_id>/papers/",
        views.PaperListView.as_view(),
        name="conference_paper_list",
    ),
    path(
        "papers/<int:pk>/",
        views.PaperDetailView.as_view(),
        name="paper_detail",
    ),
    path(
        "papers/<int:conference_id>/create/",
        views.PaperCreateView.as_view(),
        name="paper_create",
    ),
    path(
        "papers/<int:pk>/edit/",
        views.PaperUpdateView.as_view(),
        name="paper_edit",
    ),
    # Reviews
    path("reviews/", views.ReviewListView.as_view(), name="review_user_list"),
    path(
        "papers/<int:paper_id>/reviews/",
        views.ReviewListView.as_view(),
        name="paper_review_list",
    ),
    path(
        "reviews/<int:pk>/",
        views.ReviewDetailView.as_view(),
        name="review_detail",
    ),
    path(
        "papers/<int:paper_id>/review/add/",
        views.ReviewCreateView.as_view(),
        name="review_create",
    ),
    path(
        "reviews/<int:pk>/edit/",
        views.ReviewUpdateView.as_view(),
        name="review_edit",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
