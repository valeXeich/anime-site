from django.contrib.auth import get_user_model
from django.forms import ModelForm, TextInput, Select, FileInput, Textarea, ModelChoiceField, RadioSelect
from .models import Profile, Rating, RatingStar, Comment


User = get_user_model()

class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['description', 'date_birth', 'sex', 'avatar',]
        labels = {
            'description': 'Описание',
            'date_birth': 'Дата рождения',
            'sex': 'Пол',
            'avatar': 'Аватар'
        }
        widgets = {
            'description': Textarea(attrs={'placeholder': 'Описание', 'rows': 4, 'id': 'description'}),
            'date_birth': TextInput(attrs={'type': 'date'}),
            'sex': Select(attrs={'class': 'form-select form-select-sm'}),
            'avatar': FileInput(attrs={'type': 'file'}),
        }


class RatingForm(ModelForm):

    star = ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ['star', ]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
