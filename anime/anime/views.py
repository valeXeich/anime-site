from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Anime, Profile, AnimeList, WatchingNow, WillWatch, Viewed, Throw, Favorite
from .mixins import ProfileMixin, AnimeListMixin


class AnimeListView(ListView):
    model = Anime
    queryset = Anime.objects.all()
    context_object_name = 'anime_list'
    template_name = 'anime/anime_list.html'


class AnimeDetailView(AnimeListMixin, DetailView):
    model = Anime
    queryset = Anime.objects.all()
    slug_field = 'url'
    context_object_name = 'anime_detail'
    template_name = 'anime/anime_detail.html'


class ProfileView(ProfileMixin, AnimeListMixin, DetailView):
    model = Profile
    queryset = Profile.objects.all()
    template_name = 'profile/profile.html'


class AddToWatchingNow(AnimeListMixin, View):

    def get(self, request, *args, **kwargs):
        anime_slug = kwargs.get('slug')
        anime = Anime.objects.get(url=anime_slug)
        try:
            will_watch = WillWatch.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        watching_now, created = WatchingNow.objects.get_or_create(
            user=request.user,
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
        try:
            watching_now = WatchingNow.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        will_watch, created = WillWatch.objects.get_or_create(
            user=request.user,
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
        try:
            watching_now = WatchingNow.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            will_watch = WillWatch.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            throw = Throw.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.throw.remove(throw)
            throw.delete()
        except Throw.DoesNotExist:
            None
        viewed, created = Viewed.objects.get_or_create(
            user=request.user,
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
        try:
            watching_now = WatchingNow.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.watching_now.remove(watching_now)
            watching_now.delete()
        except WatchingNow.DoesNotExist:
            None
        try:
            will_watch = WillWatch.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.will_watch.remove(will_watch)
            will_watch.delete()
        except WillWatch.DoesNotExist:
            None
        try:
            viewed = Viewed.objects.get(user=request.user, anime=anime, anime_list=self.anime_list)
            self.anime_list.viewed.remove(viewed)
            viewed.delete()
        except Viewed.DoesNotExist:
            None
        throw, created = Throw.objects.get_or_create(
            user=request.user,
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
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            anime=anime,
            anime_list=self.anime_list
        )
        if created:
            self.anime_list.favorite.add(favorite)
        else:
            self.anime_list.favorite.remove(favorite)
            favorite.delete()
        return redirect('anime:anime_detail', slug=anime_slug)


class ProfileWatchingNowView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all()
    template_name = 'profile/profile_watching_now.html'
    context_object_name = 'anime_watching'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.user)
        return context


class ProfileWillWatchView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all()
    template_name = 'profile/profile_willwatch.html'
    context_object_name = 'anime_will_watch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.user)
        return context


class ProfileViewedView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all()
    template_name = 'profile/profile_viewed.html'
    context_object_name = 'anime_viewed'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.user)
        return context


class ProfileThrowView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all()
    template_name = 'profile/profile_throw.html'
    context_object_name = 'anime_throw'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.user)
        return context


class ProfileFavoriteView(ProfileMixin, AnimeListMixin, DetailView):
    model = AnimeList
    queryset = AnimeList.objects.all()
    template_name = 'profile/profile_favorite.html'
    context_object_name = 'anime_favorite'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.user)
        return context





