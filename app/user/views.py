from django.conf import settings
from django.db.models import Count, Prefetch
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpRequest

from .models import User
from item.models import Item, Comment
from item.views import ItemList


class HomeDetail(TemplateView):
    model = User
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["myitems"] = Item.objects.filter(author=self.request.user).order_by(
            "-created_at"
        )

        return context


class UserDetail(DetailView):
    model = User
    context_object_name = "items"
    template_name = "user/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Item.objects.filter(author=self.object.id)
        likes = Item.objects.filter(likes__author=self.object.id)
        context["items"] = items
        context["likes"] = likes

        return context


class UserUpdate(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "user/update.html"
    fields = ("bio",)
    success_url = reverse_lazy("home")

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(id=self.request.user.id)


def AvatarUpload(request, pk):
    if request.method == "POST":
        avatar = request.FILES["avatar"]
        user = User.objects.get(pk=pk)
        user.avatar = avatar
        user.save(update_fields=["avatar"])

        return JsonResponse({"url": user.avatar.url})
