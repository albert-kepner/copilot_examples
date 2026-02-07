from django.urls import path

from . import views

urlpatterns = [
    path("", views.HobbyListView.as_view(), name="hobby-list"),
    path("hobby/add/", views.HobbyCreateView.as_view(), name="hobby-add"),
    path("hobby/<int:pk>/", views.HobbyDetailView.as_view(), name="hobby-detail"),
    path("hobby/<int:pk>/edit/", views.HobbyUpdateView.as_view(), name="hobby-edit"),
    path("hobby/<int:pk>/delete/", views.HobbyDeleteView.as_view(), name="hobby-delete"),
]
