from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import AnimeListView, AnimeDetailView, ProfileView

app_name = 'anime'

urlpatterns = [
    path('', AnimeListView.as_view(), name='anime_list'),
    path('anime/<slug:slug>', AnimeDetailView.as_view(), name='anime_detail'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)