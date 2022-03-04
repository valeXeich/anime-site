from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .filter import FilterForAnime, FilterForGenre
from .views import (
    AnimeListView,
    AnimeDetailView,
    ProfileView,
    AddToWatchingNow,
    AddToWillWatch,
    AddToThrow,
    AddToViewed,
    AddToFavorite,
    ProfileWillWatchView,
    ProfileViewedView,
    ProfileThrowView,
    ProfileFavoriteView,
    UpdateProfileView,
    AddStarRating,
    DisplayVideo,
    DeleteCommentView,
    GenreListView,
    GenreDetailView,
    Search,
    TrendingView,
    PopularView,
    RecentView,
    AllAnimeView
)
from django.contrib.auth.views import LogoutView

app_name = 'anime'

urlpatterns = [
    path('', AnimeListView.as_view(), name='anime_list'),
    path('exit/', LogoutView.as_view(next_page='anime:anime_list'), name='exit'),
    path('anime/trending', TrendingView.as_view(), name='anime_trending'),
    path('anime/popular', PopularView.as_view(), name='anime_popular'),
    path('anime/recent', RecentView.as_view(), name='anime_recent'),
    path('anime/all', AllAnimeView.as_view(), name='anime_all'),
    path('anime/all/filter', FilterForAnime.as_view(), name='anime_filter'),
    path('anime/genre/filter', FilterForGenre.as_view(), name='anime_filter_genre'),
    path('anime/<slug:slug>', AnimeDetailView.as_view(), name='anime_detail'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/update', UpdateProfileView.as_view(), name='profile_update'),
    path('add-rating/', AddStarRating.as_view(), name='add_rating'),
    path('anime/video/<slug:slug>', DisplayVideo.as_view(), name='anime_video'),
    # AnimeList
    path('profile/<int:pk>/will_watching', ProfileWillWatchView.as_view(), name='will_watching'),
    path('profile/<int:pk>/viewed', ProfileViewedView.as_view(), name='viewed'),
    path('profile/<int:pk>/throw', ProfileThrowView.as_view(), name='throw'),
    path('profile/<int:pk>/favorite', ProfileFavoriteView.as_view(), name='favorite'),
    # Add AnimeList
    path('add-to-watching/<slug:slug>', AddToWatchingNow.as_view(), name='add_to_watching'),
    path('add-to-will-watching/<slug:slug>', AddToWillWatch.as_view(), name='add_to_will_watching'),
    path('add-to-viewed/<slug:slug>', AddToViewed.as_view(), name='add_to_viewed'),
    path('add-to-throw/<slug:slug>', AddToThrow.as_view(), name='add_to_throw'),
    path('add-to-favorite/<slug:slug>', AddToFavorite.as_view(), name='add_to_favorite'),

    path('anime/genres/', GenreListView.as_view(), name='genre_list'),
    path('anime/genres/<slug:slug>', GenreDetailView.as_view(), name='genre_detail'),
    path('comment/delete/<slug:slug>/<int:pk>', DeleteCommentView.as_view(), name='delete_comment'),

    path('search/', Search.as_view(), name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)