from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from .forms import ProfileUpdateForm, RatingForm
from django.db.models import Q

from .models import (Anime,
                     Profile,
                     AnimeList,
                     WatchingNow,
                     WillWatch, Viewed,
                     Throw,
                     Favorite,
                     Ip,
                     Rating,
                     Video,
                     Comment,
                     Genre,
                     Directors,
                     Studio
                     )
from .mixins import ProfileMixin, AnimeListMixin, CommentMixin
from .filter import FilterList
from .utils import get_random, get_comments, top_views


User = get_user_model()


class TrendingView(ProfileMixin, AnimeListMixin, ListView):
    model = Anime
    queryset = Anime.objects.all().prefetch_related('anime_comments', 'views').annotate(
        views_cnt=Count('views'), comm_cnt=Count('anime_comments')).order_by('-views_cnt', '-comm_cnt', '-year')
    context_object_name = 'trending'
    paginate_by = 18
    template_name = 'anime/trending.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class PopularView(ProfileMixin, AnimeListMixin, ListView):
    model = Anime
    queryset = Anime.objects.all().prefetch_related('anime_comments', 'views').annotate(
        views_cnt=Count('views'), comm_cnt=Count('anime_comments')).order_by('-views_cnt', '-comm_cnt')
    context_object_name = 'popular'
    paginate_by = 18
    template_name = 'anime/popular.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class RecentView(ProfileMixin, AnimeListMixin, ListView):
    model = Anime
    queryset = Anime.objects.all().prefetch_related('anime_comments', 'views').order_by('-year')
    context_object_name = 'recent'
    paginate_by = 18
    template_name = 'anime/recent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AllAnimeView(ProfileMixin, AnimeListMixin, FilterList, ListView):
    model = Anime
    queryset = Anime.objects.all().prefetch_related('anime_comments', 'views')
    template_name = 'anime/anime_all.html'
    context_object_name = 'anime_all'
    paginate_by = 18

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['random_anime'] = get_random()
        context['last_comment'] = get_comments()[:4]
        return context


class AnimeListView(ProfileMixin, AnimeListMixin, ListView):
    model = Anime
    template_name = 'anime/anime_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = self.profile
        context['popular'] = Anime.objects.all().prefetch_related('anime_comments', 'views').annotate(
            views_cnt=Count('views'), comm_cnt=Count('anime_comments')).order_by('-views_cnt', '-comm_cnt')[:6]
        context['trending'] = Anime.objects.all().prefetch_related('anime_comments', 'views').annotate(
            views_cnt=Count('views'), comm_cnt=Count('anime_comments')).order_by('-views_cnt', '-comm_cnt', '-year')[:6]
        context['recent'] = Anime.objects.all().prefetch_related('anime_comments', 'views').order_by('-year')[:6]
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class UpdateProfileView(ProfileMixin, AnimeListMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profile/profile_update.html'

    def get_success_url(self, **kwargs):
        return reverse('anime:profile_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['random_anime'] = get_random()
        return context


class AnimeDetailView(ProfileMixin, AnimeListMixin, CommentMixin, DetailView):
    model = Anime
    queryset = Anime.objects.all().select_related('studio')
    slug_field = 'url'
    context_object_name = 'anime_detail'
    template_name = 'anime/anime_detail.html'

    def dispatch(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        ip = get_client_ip(request)
        views_ip, created = Ip.objects.get_or_create(ip=ip)
        anime.views.add(views_ip)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        anime = kwargs.get('object')
        genre = anime.genre.all()
        similar_anime = Anime.objects.filter(genre__in=genre).exclude(
            id=anime.id).distinct().prefetch_related('views')[:4]
        context = super().get_context_data(*args, **kwargs)
        context['profile'] = self.profile
        context['comments'] = self.get_comments_for_anime()
        context['similar_anime'] = similar_anime
        context['star_form'] = RatingForm()
        context['random_anime'] = get_random()
        context['video'] = Video.objects.filter(anime=anime)
        context['cacl_rating'] = Rating.objects.filter(anime=anime).aggregate(Avg('star')).get('star__avg')
        try:
            anime_list = AnimeList.objects.get(owner=self.profile)
            try:
                context['watching_now'] = anime_list.watching_now.get(anime=anime)
            except WatchingNow.DoesNotExist:
                None
            try:
                context['will_watch'] = anime_list.will_watch.get(anime=anime)
            except WillWatch.DoesNotExist:
                None
            try:
                context['throw'] = anime_list.throw.get(anime=anime)
            except Throw.DoesNotExist:
                None
            try:
                context['viewed'] = anime_list.viewed.get(anime=anime)
            except Viewed.DoesNotExist:
                None
            try:
                context['favorite'] = anime_list.favorite.get(anime=anime)
            except Favorite.DoesNotExist:
                None
        except AnimeList.DoesNotExist:
            None
        return context


class DisplayVideo(ProfileMixin, AnimeListMixin, DetailView):
    model = Video
    template_name = 'anime/anime_video.html'
    slug_field = 'url'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        anime = kwargs.get('object')
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['random_anime'] = get_random()
        return context


class ProfileView(ProfileMixin, AnimeListMixin, DetailView):
    model = Profile
    queryset = Profile.objects.all().select_related('user')
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['watching'] = AnimeList.objects.prefetch_related('watching_now').get(owner=self.get_object())
        context['random_anime'] = get_random()
        return context


class AddToWatchingNow(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        profile = Profile.objects.get(user=request.user)
        try:
            will_watch = WillWatch.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        watching_now, created = WatchingNow.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.watching_now.add(watching_now)
        else:
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class AddToWillWatch(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        profile = Profile.objects.get(user=request.user)
        try:
            watching_now = WatchingNow.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        will_watch, created = WillWatch.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.will_watch.add(will_watch)
        else:
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class AddToViewed(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        profile = Profile.objects.get(user=request.user)
        try:
            watching_now = WatchingNow.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            will_watch = WillWatch.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        viewed, created = Viewed.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.viewed.add(viewed)
        else:
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class AddToThrow(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        profile = Profile.objects.get(user=request.user)
        try:
            watching_now = WatchingNow.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            will_watch = WillWatch.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=profile, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        throw, created = Throw.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.throw.add(throw)
        else:
            self.anime_list.throw.remove(throw)
            throw.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class AddToFavorite(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        profile = Profile.objects.get(user=request.user)
        favorite, created = Favorite.objects.get_or_create(
            user=profile,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.favorite.add(favorite)
        else:
            self.anime_list.favorite.remove(favorite)
            favorite.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class ProfileWillWatchView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all().prefetch_related('will_watch')
    template_name = 'profile/profile_willwatch.html'
    context_object_name = 'anime_will_watch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = kwargs.get('object').owner.user
        context['profile'] = Profile.objects.select_related('user').get(user=user)
        context['random_anime'] = get_random()
        return context


class ProfileViewedView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all().prefetch_related('viewed')
    template_name = 'profile/profile_viewed.html'
    context_object_name = 'anime_viewed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = kwargs.get('object').owner.user
        context['profile'] = Profile.objects.select_related('user').get(user=user)
        context['random_anime'] = get_random()
        return context


class ProfileThrowView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all().prefetch_related('throw')
    template_name = 'profile/profile_throw.html'
    context_object_name = 'anime_throw'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = kwargs.get('object').owner.user
        context['profile'] = Profile.objects.select_related('user').get(user=user)
        context['random_anime'] = get_random()
        return context


class ProfileFavoriteView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all().prefetch_related('favorite')
    template_name = 'profile/profile_favorite.html'
    context_object_name = 'anime_favorite'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = kwargs.get('object').owner.user
        context['profile'] = Profile.objects.select_related('user').get(user=user)
        context['random_anime'] = get_random()
        return context


class AddStarRating(View):

    def post(self, request):
        form = RatingForm(request.POST)
        prof = Profile.objects.get(user=request.user)
        if form.is_valid():
            Rating.objects.update_or_create(
                profile=prof,
                anime_id=int(request.POST.get('anime')),
                defaults={'star_id': int(request.POST.get('star'))}
            )
            anime = Anime.objects.get(id=int(request.POST.get('anime')))
            rating = Rating.objects.get(anime=anime, profile=prof)
            anime.rating.add(rating)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)


class DeleteCommentView(View):

    def get(self, request, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        comment = Comment.objects.get(id=kwargs.get('pk'))
        anime.anime_comments.remove(comment)
        comment.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class GenreListView(ProfileMixin, AnimeListMixin, ListView):
    model = Genre
    queryset = Genre.objects.all()
    context_object_name = 'genres'
    template_name = 'anime/genre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['random_anime'] = get_random()
        return context

class GenreDetailView(ProfileMixin, FilterList, AnimeListMixin, DetailView, MultipleObjectMixin):
    model = Genre
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/genre_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('anime_comments', 'views').filter(genre=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['profile'] = self.profile
        context['genre'] = self.get_object()
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class DirectorsDetailView(ProfileMixin, AnimeListMixin, DetailView, MultipleObjectMixin):
    model = Directors
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/directors_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('anime_comments', 'views').filter(directors=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['profile'] = self.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class StudioDetailView(ProfileMixin, AnimeListMixin, DetailView, MultipleObjectMixin):
    model = Studio
    paginate_by = 18
    slug_field = 'url'
    template_name = 'anime/studio_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Anime.objects.prefetch_related('anime_comments', 'views').filter(studio=self.get_object())
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['profile'] = self.profile
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        context['random_anime'] = get_random()
        return context


class Search(ProfileMixin, AnimeListMixin, ListView):
    model = Anime
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        anime = Anime.objects.prefetch_related('anime_comments', 'views').filter(
            Q(title__icontains=self.request.GET.get('q')) | Q(second_title__icontains=self.request.GET.get('q')))
        context = super().get_context_data(**kwargs)
        context['search_request'] = self.request.GET.get('q')
        context['q'] = anime
        context['profile'] = self.profile
        context['random_anime'] = get_random()
        context['top_views'] = top_views()[:5]
        context['last_comment'] = get_comments()[:4]
        return context

