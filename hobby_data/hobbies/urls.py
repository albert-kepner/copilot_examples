from django.urls import path

from . import views

urlpatterns = [
    path("", views.HobbyListView.as_view(), name="hobby-list"),
    path("hobby/add/", views.HobbyCreateView.as_view(), name="hobby-add"),
    path("hobby/<int:pk>/", views.HobbyDetailView.as_view(), name="hobby-detail"),
    path("hobby/<int:pk>/edit/", views.HobbyUpdateView.as_view(), name="hobby-edit"),
    path("hobby/<int:pk>/delete/", views.HobbyDeleteView.as_view(), name="hobby-delete"),
    path(
        "hobby/<int:hobby_pk>/details/add/",
        views.HobbyDetailCreateView.as_view(),
        name="hobby-detail-add",
    ),
    path(
        "hobby/<int:hobby_pk>/details/<int:pk>/edit/",
        views.HobbyDetailUpdateView.as_view(),
        name="hobby-detail-edit",
    ),
    path(
        "hobby/<int:hobby_pk>/details/<int:pk>/delete/",
        views.HobbyDetailDeleteView.as_view(),
        name="hobby-detail-delete",
    ),
]
