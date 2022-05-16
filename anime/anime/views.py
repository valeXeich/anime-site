from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from .forms import ProfileUpdateForm, RatingForm
from django.db.models import Q

from .models import (
    Anime,
    Profile,
    AnimeList,
    Favorite,
    Ip,
    Rating,
    Video,
    Comment,
    Genre,
    Directors,
    Studio
)
from .mixins import CommentMixin, CustomContextMixin, ProfileContextMixin
from .filter import FilterList
from .utils import add_anime_to_list, get_client_ip, get_trending_anime, get_popular_anime, get_recent_anime

User = get_user_model()


class TrendingView(CustomContextMixin, ListView):
    model = Anime
    context_object_name = 'trending'
    paginate_by = 18
    template_name = 'anime/trending.html'

    def get_queryset(self):
        queryset = get_trending_anime()
        return queryset


class PopularView(CustomContextMixin, ListView):
    model = Anime
    context_object_name = 'popular'
    paginate_by = 18
    template_name = 'anime/popular.html'

    def get_queryset(self):
        queryset = get_popular_anime()
        return queryset


class RecentView(CustomContextMixin, ListView):
    model = Anime
    queryset = Anime.objects.prefetch_related('comments', 'views').order_by('-year')
    context_object_name = 'recent'
    paginate_by = 18
    template_name = 'anime/recent.html'


class AllAnimeView(FilterList, CustomContextMixin, ListView):
    model = Anime
    queryset = Anime.objects.prefetch_related('comments', 'views')
    template_name = 'anime/anime_all.html'
    context_object_name = 'anime_all'
    paginate_by = 18


class AnimeListView(CustomContextMixin, ListView):
    model = Anime
    template_name = 'anime/anime_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['popular'] = get_popular_anime()[:6]
        context['trending'] = get_trending_anime()[:6]
        context['recent'] = get_recent_anime()[:6]
        return context


class UpdateProfileView(LoginRequiredMixin, UserPassesTestMixin, CustomContextMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile/profile_update.html'

    def test_func(self):
        profile = self.get_object()
        return profile == self.request.user.profile

    def get_success_url(self, **kwargs):
        return reverse('anime:profile_detail', kwargs={'pk': self.object.pk})


class AnimeDetailView(CustomContextMixin, CommentMixin, DetailView):
    model = Anime
    queryset = Anime.objects.select_related('studio')
    slug_field = 'url'
    context_object_name = 'anime_detail'
    template_name = 'anime/anime_detail.html'

    def dispatch(self, request, *args, **kwargs):
        anime = self.get_object()
        ip = get_client_ip(request)
        views_ip, created = Ip.objects.get_or_create(ip=ip)
        anime.views.add(views_ip)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        anime = self.get_object()
        genre = anime.genre.all()
        similar_anime = Anime.objects.prefetch_related('views').filter(genre__in=genre).exclude(
            id=anime.id).distinct()[:4]
        context = super().get_context_data(*args, **kwargs)
        context['similar_anime'] = similar_anime
        context['star_form'] = RatingForm()
        return context


class DisplayVideo(CustomContextMixin, DetailView):
    model = Video
    template_name = 'anime/anime_video.html'
    slug_field = 'url'
    context_object_name = 'video'


class AddToList(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        anime_id = request.POST.get('anime_id')
        model_name = request.POST.get('model_name')
        profile = self.request.user.profile
        anime = Anime.objects.get(id=anime_id)
        anime_list = AnimeList.objects.get(owner=profile)
        add_anime_to_list(profile, anime, model_name, anime_list)
        return redirect('anime:anime_detail', slug=anime.url)


class AddToFavorite(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        anime_id = request.POST.get('anime_id')
        anime = Anime.objects.get(id=anime_id)
        anime_list = AnimeList.objects.get(owner=profile)
        favorite, created = Favorite.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=anime_list
        )
        if created:
            anime_list.favorite.add(favorite)
        else:
            anime_list.favorite.remove(favorite)
            favorite.delete()
        return redirect('anime:anime_detail', slug=anime.url)


class ProfileView(ProfileContextMixin, DetailView):
    queryset = Profile.objects.prefetch_related('watching', 'watching__anime').select_related('user')
    template_name = 'profile/profile.html'


class ProfileWillWatchView(ProfileContextMixin, DetailView):
    queryset = Profile.objects.prefetch_related('will_watch', 'will_watch__anime').select_related('user')
    template_name = 'profile/profile_willwatch.html'
    context_object_name = 'profile'


class ProfileViewedView(ProfileContextMixin, DetailView):
    queryset = Profile.objects.prefetch_related('viewed', 'viewed__anime').select_related('user')
    template_name = 'profile/profile_viewed.html'
    context_object_name = 'profile'


class ProfileThrowView(ProfileContextMixin, DetailView):
    queryset = Profile.objects.prefetch_related('throw', 'throw__anime').select_related('user')
    template_name = 'profile/profile_throw.html'
    context_object_name = 'profile'


class ProfileFavoriteView(ProfileContextMixin, DetailView):
    queryset = Profile.objects.prefetch_related('favorite', 'favorite__anime').select_related('user')
    template_name = 'profile/profile_favorite.html'
    context_object_name = 'profile'


class AddStarRating(LoginRequiredMixin, View):

    def post(self, request):
        form = RatingForm(request.POST)
        prof = Profile.objects.get(user=request.user)
        if form.is_valid():
            Rating.objects.update_or_create(
                profile=prof,
                anime_id=int(request.POST.get('anime')),
                defaults={'star_id': int(request.POST.get('star'))}
            )
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        comment_id = self.request.POST.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        return comment.author == self.request.user

    def post(self, request, *args, **kwargs):
        anime_id = request.POST.get('anime_id')
        comment_id = request.POST.get('comment_id')
        anime = Anime.objects.get(id=anime_id)
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return redirect('anime:anime_detail', slug=anime.url)


class GenreListView(CustomContextMixin, ListView):
    model = Genre
    queryset = Genre.objects.all()
    context_object_name = 'genres'
    template_name = 'anime/genre.html'


class GenreDetailView(CustomContextMixin, FilterList, DetailView, MultipleObjectMixin):
    model = Genre
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/genre_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('comments', 'views').filter(genre=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['genre'] = self.get_object()
        return context


class DirectorsDetailView(CustomContextMixin, DetailView, MultipleObjectMixin):
    model = Directors
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/directors_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('comments', 'views').filter(directors=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class StudioDetailView(CustomContextMixin, DetailView, MultipleObjectMixin):
    model = Studio
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/studio_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('comments', 'views').filter(studio=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class Search(CustomContextMixin, ListView):
    model = Anime
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        anime = Anime.objects.prefetch_related('comments', 'views').filter(
            Q(title__icontains=self.request.GET.get('q')) | Q(second_title__icontains=self.request.GET.get('q')))
        context = super().get_context_data(**kwargs)
        context['search_request'] = self.request.GET.get('q')
        context['q'] = anime
        return context


