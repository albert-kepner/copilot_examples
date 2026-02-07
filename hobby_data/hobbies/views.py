from django.urls import reverse_lazy
from django.views import generic

from .models import Hobby


class HobbyListView(generic.ListView):
    model = Hobby
    template_name = "hobbies/hobby_list.html"


class HobbyDetailView(generic.DetailView):
    model = Hobby
    template_name = "hobbies/hobby_detail.html"


class HobbyCreateView(generic.CreateView):
    model = Hobby
    fields = ["name", "description", "category", "url", "notes"]
    template_name = "hobbies/hobby_form.html"
    success_url = reverse_lazy("hobby-list")


class HobbyUpdateView(generic.UpdateView):
    model = Hobby
    fields = ["name", "description", "category", "url", "notes"]
    template_name = "hobbies/hobby_form.html"
    success_url = reverse_lazy("hobby-list")


class HobbyDeleteView(generic.DeleteView):
    model = Hobby
    template_name = "hobbies/hobby_confirm_delete.html"
    success_url = reverse_lazy("hobby-list")
