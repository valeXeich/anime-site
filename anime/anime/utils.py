import random
from django.db.models import Max
from .models import Anime


def get_random():
    max_id = Anime.objects.all().aggregate(max_id=Max('id'))['max_id']
    while True:
        pk = random.randint(1, max_id)
        anime = Anime.objects.filter(pk=pk).first()
        if anime:
            return anime