import random
from django.db.models import Max
from .models import Anime, Comment


def get_random():
    max_id = Anime.objects.all().aggregate(max_id=Max('id'))['max_id']
    while True:
        pk = random.randint(1, max_id)
        anime = Anime.objects.filter(pk=pk).first()
        if anime:
            return anime


def get_comments():
    comments = Comment.objects.all().order_by('-created_date')
    comment_list = []
    for i in comments:
        for j in comments:
            if i.anime == j.anime:
                if i.anime not in comment_list:
                    comment_list.append(i.anime)
    return comment_list