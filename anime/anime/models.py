from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=250)
    url = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('anime:genre_detail', kwargs={'slug': self.url})


class Directors(models.Model):
    name = models.CharField('Режиссер', max_length=250)
    url = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('anime:directors_detail', kwargs={'slug': self.url})


class Studio(models.Model):
    name = models.CharField('Студия', max_length=250)
    url = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('anime:studio_detail', kwargs={'slug': self.url})


class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip


class Anime(models.Model):
    STATUS_ANIME = (
        ('released', 'Вышел'),
        ('ongoing', 'Онгоинг'),
        ('announcement', 'Анонс'),
    )

    AGE_RATING = (
        ('six', '6+'),
        ('thirteen', '13+'),
        ('sixteen', '16+'),
        ('eighteen', '18+'),
    )

    SEASON_ANIME = (
        ('autumn', 'Осень'),
        ('winter', 'Зима'),
        ('spring', 'Весна'),
        ('summer', 'Лето'),
    )

    TYPE_ANIME = (
        ('series', 'Сериал'),
        ('feature_film', 'Полнометражный фильм'),
        ('short_film', 'Короткометражный фильм'),
        ('ova', 'OVA'),
        ('special', 'Special'),
        ('ona', 'ONA'),
    )

    title = models.CharField('Название', max_length=250)
    second_title = models.CharField('Другое название', max_length=250, blank=True, null=True)
    poster = models.ImageField('Постер', upload_to='anime_poster/')
    genre = models.ManyToManyField(Genre, verbose_name='Жанры')
    directors = models.ManyToManyField(Directors, verbose_name='Режиссеры')
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, verbose_name='Студия')
    description = models.TextField('Описание')
    year = models.DateField('Год выпуска')
    total_series = models.PositiveIntegerField('Кол-во серий')
    status = models.CharField('Статус', max_length=200, choices=STATUS_ANIME)
    age_rating = models.CharField('Возрастной рейтинг', max_length=200, choices=AGE_RATING)
    season = models.CharField('Сезон', max_length=200, choices=SEASON_ANIME)
    type = models.CharField('Тип', max_length=200, choices=TYPE_ANIME)
    views = models.ManyToManyField(Ip, verbose_name='Просмотры', related_name='anime_views', blank=True)
    url = models.SlugField(unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('anime:anime_detail', kwargs={'slug': self.url})

    def get_anime_comments(self):
        return self.comments.select_related('author', 'author__profile').all()

    def get_video(self):
        return self.related_series.all()

    def avg_rating(self):
        return self.anime_rating.aggregate(Avg('star')).get('star__avg')


class Profile(models.Model):
    SEX_CHOICES = (
        ('man', 'Мужской'),
        ('female', 'Женский'),
    )

    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    date_birth = models.DateField('Дата рождения', blank=True, null=True)
    description = models.TextField('Описание', blank=True, null=True)
    sex = models.CharField('Пол', max_length=200, choices=SEX_CHOICES, blank=True, null=True)
    avatar = models.ImageField('Аватар', default='user_avatar/default_avatar.png', upload_to='user_avatar/', blank=True, null=True)

    def __str__(self):
        return 'Профиль: {}'.format(self.user)


class AnimeList(models.Model):
    owner = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE, verbose_name='Владелец списка')
    watching_now = models.ManyToManyField('WatchingNow', verbose_name='Смотрю', blank=True)
    will_watch = models.ManyToManyField('WillWatch', verbose_name='Буду смотреть', blank=True)
    viewed = models.ManyToManyField('Viewed', verbose_name='Просмотрено', blank=True)
    throw = models.ManyToManyField('Throw', verbose_name='Брошено', blank=True)
    favorite = models.ManyToManyField('Favorite', verbose_name='Любимые', blank=True)

    def __str__(self):
        return 'Владелец списка: {}'.format(self.owner)


class WatchingNow(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watching')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, blank=True, null=True, related_name='watching')
    anime_list = models.ForeignKey(AnimeList, on_delete=models.CASCADE)

    def __str__(self):
        return 'Аниме: {}'.format(self.anime)


class WillWatch(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='will_watch')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, blank=True, null=True, related_name='will_watch')
    anime_list = models.ForeignKey(AnimeList, on_delete=models.CASCADE)

    def __str__(self):
        return 'Аниме: {}'.format(self.anime)


class Viewed(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='viewed')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, blank=True, null=True, related_name='viewed')
    anime_list = models.ForeignKey(AnimeList, on_delete=models.CASCADE, related_name='related_viewed')

    def __str__(self):
        return 'Аниме: {}'.format(self.anime)


class Throw(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='throw')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, blank=True, null=True, related_name='throw')
    anime_list = models.ForeignKey(AnimeList, on_delete=models.CASCADE, related_name='related_throw')

    def __str__(self):
        return 'Аниме: {}'.format(self.anime)


class Favorite(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='favorite')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, blank=True, null=True, related_name='favorite')
    anime_list = models.ForeignKey(AnimeList, on_delete=models.CASCADE, related_name='related_favorite')

    def __str__(self):
        return 'Аниме: {}'.format(self.anime)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='comments', null=True)
    text = models.TextField('Текст', max_length=500)
    created_date = models.DateTimeField('Дата создания', auto_now=True)

    def __str__(self):
        return 'Комментарий: {}'.format(self.anime)

    def get_absolute_url(self):
        return reverse('anime:delete_comment', kwargs={'pk': self.pk})


class RatingStar(models.Model):
    value = models.SmallIntegerField('Значение', default=0)

    class Meta:
        ordering = ['-value']

    def __str__(self):
        return f'{self.value}'


class Rating(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Профиль', related_name='rating')
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name='Звезды')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name='Аниме', related_name='anime_rating')

    def __str__(self):
        return '{}, Звезда: {}, Аниме: {}'.format(self.profile, self.star, self.anime)


class Video(models.Model):
    name = models.CharField(max_length=100)
    video = models.FileField(upload_to='video/')
    thumb = models.FileField(upload_to='thumb/')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='related_series')
    url = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('anime:anime_video', kwargs={'series': self.anime.url, 'slug': self.url})


class AnimeShot(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name='Аниме', related_name='anime_shots')
    shot = models.ImageField('Момент', upload_to='anime_shots/')

    def __str__(self):
        return 'Кадр: {}'.format(self.anime.title)

