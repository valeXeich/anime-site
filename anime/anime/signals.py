from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AnimeList, Profile


@receiver(post_save, sender=User)
def create_profile_and_anime_list(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(
            user=instance
        )
        anime_list = AnimeList.objects.create(
            owner=profile
        )

