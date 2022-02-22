from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import AnimeListView, AnimeDetailView, ProfileView, DeleteCommentView, GenreListView, GenreDetailView

app_name = 'anime'

urlpatterns = [
    path('', AnimeListView.as_view(), name='anime_list'),
    path('anime/<slug:slug>', AnimeDetailView.as_view(), name='anime_detail'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile_detail'),

    path('anime/genres/', GenreListView.as_view(), name='genre_list'),
    path('anime/genres/<slug:slug>', GenreDetailView.as_view(), name='genre_detail'),

    path('comment/delete/<int:pk>', DeleteCommentView.as_view(), name='delete_comment')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)