from django.views.generic import ListView
from .models import Anime, Genre, Directors, Studio
from .mixins import CustomContextMixin


class FilterList:

    def get_genre(self):
        return Genre.objects.all()

    def get_directors(self):
        return Directors.objects.all()

    def get_studio(self):
        return Studio.objects.all()

    def get_year(self):
        return Anime.objects.all().values('year__year').order_by('-year__year').distinct('year__year')

    def get_status(self):
        return Anime.objects.all().order_by('-status').distinct('status')

    def get_age_rating(self):
        return Anime.objects.all().order_by('age_rating').distinct('age_rating')

    def get_season(self):
        return Anime.objects.all().order_by('season').distinct('season')

    def get_type(self):
        return Anime.objects.all().order_by('type').distinct('type')


class FilterForAnime(CustomContextMixin, FilterList, ListView):
    model = Anime
    template_name = 'filter.html'
    context_object_name = 'anime_filter'

    def get_queryset(self):
        queryset = Anime.objects.all().prefetch_related('comments', 'views')
        if 'genre' in self.request.GET:
            queryset = queryset.filter(genre__in=self.request.GET.getlist('genre'))

        if 'directors' in self.request.GET:
            queryset = queryset.filter(directors__in=self.request.GET.getlist('directors'))

        if 'studio' in self.request.GET:
            queryset = queryset.filter(studio__in=self.request.GET.getlist('studio'))

        if 'year' in self.request.GET:
            queryset = queryset.filter(year__year__in=self.request.GET.getlist('year'))

        if 'status' in self.request.GET:
            queryset = queryset.filter(status__in=self.request.GET.getlist('status'))

        if 'age_rating' in self.request.GET:
            queryset = queryset.filter(age_rating__in=self.request.GET.getlist('age_rating'))

        if 'season' in self.request.GET:
            queryset = queryset.filter(season__in=self.request.GET.getlist('season'))

        if 'type' in self.request.GET:
            queryset = queryset.filter(type__in=self.request.GET.getlist('type'))
        return queryset


class FilterForGenre(CustomContextMixin, FilterList, ListView):
    model = Anime
    template_name = 'genre_filter.html'
    context_object_name = 'anime_filter'

    def get_queryset(self):
        queryset = Anime.objects.prefetch_related('comments', 'views').filter(genre__id=self.request.GET.get('get_genre'))

        if 'directors' in self.request.GET:
            queryset = queryset.filter(directors__in=self.request.GET.getlist('directors'))

        if 'studio' in self.request.GET:
            queryset = queryset.filter(studio__in=self.request.GET.getlist('studio'))

        if 'year' in self.request.GET:
            queryset = queryset.filter(year__year__in=self.request.GET.getlist('year'))

        if 'status' in self.request.GET:
            queryset = queryset.filter(status__in=self.request.GET.getlist('status'))

        if 'age_rating' in self.request.GET:
            queryset = queryset.filter(age_rating__in=self.request.GET.getlist('age_rating'))

        if 'season' in self.request.GET:
            queryset = queryset.filter(season__in=self.request.GET.getlist('season'))

        if 'type' in self.request.GET:
            queryset = queryset.filter(type__in=self.request.GET.getlist('type'))
        return queryset

    def get_context_data(self, *args, **kwargs):
        genre = Genre.objects.get(id=self.request.GET.get('get_genre'))
        context = super().get_context_data(*args, **kwargs)
        context['genre'] = genre
        return context



