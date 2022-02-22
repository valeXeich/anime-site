from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.list import MultipleObjectMixin

from .models import Anime, Profile, Comment, Genre
from .mixins import CommentMixin


class AnimeListView(ListView):
    model = Anime
    queryset = Anime.objects.all()
    context_object_name = 'anime_list'
    template_name = 'anime/anime_list.html'


class AnimeDetailView(CommentMixin, DetailView):
    model = Anime
    queryset = Anime.objects.all()
    slug_field = 'url'
    context_object_name = 'anime_detail'
    template_name = 'anime/anime_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_comments_for_anime()
        return context


class ProfileView(DetailView):
    model = Profile
    queryset = Profile.objects.all()
    template_name = 'profile/profile.html'


class DeleteCommentView(DeleteView):
    model = Comment
    template_name = 'anime/anime_detail.html'

    def get_success_url(self):
        return reverse_lazy('anime:anime_detail', kwargs={'slug': self.get_object().anime.url})

    def post(self, request, *args, **kwargs):
        anime = Anime.objects.get(pk=self.get_object().anime.pk)
        anime.number_of_comments -= 1
        anime.save()
        return self.delete(request, *args, **kwargs)


class GenreListView(ListView):
    model = Genre
    queryset = Genre.objects.all()
    context_object_name = 'genres'
    template_name = 'anime/genre.html'


class GenreDetailView(DetailView, MultipleObjectMixin):
    model = Genre
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/genre_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.filter(genre=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context
