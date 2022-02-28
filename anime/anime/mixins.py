from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin

from .models import Profile, AnimeList, Comment, Anime
from .forms import CommentForm

User = get_user_model()


class ProfileMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            profile = Profile.objects.filter(user=user).first()
            if not profile:
                profile = Profile.objects.create(user=user)
        if request.user.is_authenticated:
            self.user = user
            self.profile = profile
        return super().dispatch(request, *args, **kwargs)


class AnimeListMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            profile = Profile.objects.get(user=user)
            anime_list = AnimeList.objects.filter(owner=profile).first()
            if not anime_list:
                anime_list = AnimeList.objects.create(owner=profile)
        self.anime_list = anime_list
        return super().dispatch(request, *args, **kwargs)


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
        anime = Anime.objects.get(pk=self.get_object().pk)
        anime.number_of_comments += 1
        anime.save()
        return super().form_valid(form)

    def get_comments_for_anime(self):
        return Comment.objects.filter(anime=self.get_object())
