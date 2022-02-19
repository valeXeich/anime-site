from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Anime, Profile


class AnimeListView(ListView):
    model = Anime
    queryset = Anime.objects.all()
    context_object_name = 'anime_list'
    template_name = 'anime/anime_list.html'


class AnimeDetailView(DetailView):
    model = Anime
    queryset = Anime.objects.all()
    slug_field = 'url'
    context_object_name = 'anime_detail'
    template_name = 'anime/anime_detail.html'


class ProfileView(DetailView):
    model = Profile
    queryset = Profile.objects.all()
    template_name = 'profile/profile.html'






