import random
from django.db.models import Max, Count
from .models import Anime, Comment, WatchingNow, WillWatch, Throw, Viewed


def get_random():
    max_id = Anime.objects.all().aggregate(max_id=Max('id'))['max_id']
    while True:
        pk = random.randint(1, max_id)
        anime = Anime.objects.filter(pk=pk).first()
        if anime:
            return anime


def get_comments():
    comments = Comment.objects.all().select_related('anime').prefetch_related('anime__views').order_by('-created_date')
    comment_list = []
    for comment_i in comments:
        for comment_j in comments:
            if comment_i.anime == comment_j.anime:
                if comment_i.anime not in comment_list:
                    comment_list.append(comment_i.anime)
    return comment_list


def top_views():
    top_views = Anime.objects.all().prefetch_related('views').annotate(views_cnt=Count('views')).order_by('-views_cnt')
    return top_views

def add_anime_to_list(profile, anime, model_name, anime_list):
    model_list = [WatchingNow, WillWatch, Viewed, Throw]
    fields_list = [anime_list.watching_now, anime_list.will_watch, anime_list.viewed, anime_list.throw]
    field = None
    current_model = None
    for model in model_list:
        if model_name == model.__name__:
            current_model = model
            model_list.remove(model)
    for anime_list_field in fields_list:
        if model_name == anime_list_field.model.__name__:
            field = anime_list_field
    for model in model_list:
        try:
            object = model.objects.get(user=profile, anime=anime, anime_list=anime_list)
            object.delete()
        except model.DoesNotExist:
            print('Object DoesNotExist')
    obj, created = current_model.objects.get_or_create(
        user=profile,
        anime=anime,
        anime_list=anime_list
    )
    if created:
        field.add(obj)
    else:
        field.remove(obj)
        obj.delete()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_trending_anime():
    queryset = Anime.objects.prefetch_related('comments', 'views').\
        annotate(views_cnt=Count('views'), comm_cnt=Count('comments')).\
        order_by('-views_cnt', '-comm_cnt', '-year')
    return queryset

def get_popular_anime():
    queryset = Anime.objects.prefetch_related('comments', 'views').\
        annotate(views_cnt=Count('views'), comm_cnt=Count('comments')).\
        order_by('-views_cnt', '-comm_cnt')
    return queryset

def get_recent_anime():
    queryset = Anime.objects.prefetch_related('comments', 'views').order_by('-year')
    return queryset




