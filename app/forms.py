from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Agricultor, Campo, PlantaCultivada
from app.models import Agricultor

class CustomAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Email'}),
        label="Email"
    )

    class Meta:
        model = Agricultor
        fields = ('email', 'password')

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Agricultor
        fields = ['username', 'email', 'password']  # Inclua todos os campos necessários

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Define a senha
        if commit:
            user.save()
        return user
    

class LoginForm(forms.Form):

    email = forms.EmailField(
        label='Email',
        max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Digite seu email', 'class': 'form-control'})
    )

    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha', 'class': 'form-control'})
    )

class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nome']
        labels = {
            'nome': 'Nome do Campo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do Campo', 'class': 'form-control'}),
        }

class PlantaCultivadaForm(forms.ModelForm):
    class Meta:
        model = PlantaCultivada
        fields = ['planta', 'data_plantio', 'quantidade_plantada', 'percentual_perda']

        labels = {
            'planta': 'Planta',
            'data_plantio': 'Data do Plantio',
            'quantidade_plantada': 'Quantidade Plantada',
            'percentual_perda': 'Percentual de Perda',
        }

        widgets = {
            'planta': forms.Select(attrs={'class': 'form-control'}),
            'data_plantio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantidade_plantada': forms.NumberInput(attrs={'placeholder': 'Quantidade', 'class': 'form-control'}),
            'percentual_perda': forms.NumberInput(attrs={'placeholder': 'Percentual de Perda', 'class': 'form-control'}),
        }
