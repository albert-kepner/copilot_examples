from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic

from .models import Hobby, HobbyDetail


class HobbyListView(generic.ListView):
    model = Hobby
    template_name = "hobbies/hobby_list.html"


class HobbyDetailView(generic.DetailView):
    model = Hobby
    template_name = "hobbies/hobby_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["details"] = self.object.details.all()
        return context


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


class HobbyDetailParentMixin:
    hobby_kwarg = "hobby_pk"

    def get_hobby(self) -> Hobby:
        if not hasattr(self, "_hobby"):
            self._hobby = get_object_or_404(Hobby, pk=self.kwargs[self.hobby_kwarg])
        return self._hobby

    def get_queryset(self):
        return HobbyDetail.objects.filter(hobby=self.get_hobby())

    def get_success_url(self):
        return reverse("hobby-detail", kwargs={"pk": self.get_hobby().pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hobby"] = self.get_hobby()
        return context


class HobbyDetailCreateView(HobbyDetailParentMixin, generic.CreateView):
    model = HobbyDetail
    fields = ["name", "description", "category", "url", "notes"]
    template_name = "hobbies/hobby_detail_form.html"

    def form_valid(self, form):
        form.instance.hobby = self.get_hobby()
        return super().form_valid(form)


class HobbyDetailUpdateView(HobbyDetailParentMixin, generic.UpdateView):
    model = HobbyDetail
    fields = ["name", "description", "category", "url", "notes"]
    template_name = "hobbies/hobby_detail_form.html"


class HobbyDetailDeleteView(HobbyDetailParentMixin, generic.DeleteView):
    model = HobbyDetail
    template_name = "hobbies/hobby_detail_confirm_delete.html"
