from django.contrib.auth import get_user_model
from django.forms import ModelForm, TextInput, Select, FileInput
from .models import Profile


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
            'description': TextInput(),
            'date_birth': TextInput(attrs={'type': 'date'}),
            'sex': Select(),
            'avatar': FileInput(),
        }

