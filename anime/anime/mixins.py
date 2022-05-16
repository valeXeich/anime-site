from django.urls import reverse_lazy
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin

from .models import Comment
from .forms import CommentForm
from .utils import top_views, get_comments, get_random


class ProfileContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_anime'] = get_random()
        return context


class CustomContextMixin(ProfileContextMixin, ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profile'] = self.request.user.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        return context


class CommentMixin(FormMixin):
    form_class = CommentForm

    def get_success_url(self):
        return reverse_lazy('anime:anime_detail', kwargs={'slug': self.get_object().url})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.anime = self.get_object()
        self.object.save()
        return super().form_valid(form)

    def get_comments_for_anime(self):
        return Comment.objects.filter(anime=self.get_object()).select_related('author')

