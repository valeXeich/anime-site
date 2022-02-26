from django.contrib.auth import get_user_model
from django.views import View

from .models import Profile, AnimeList

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
