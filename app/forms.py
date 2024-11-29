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
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md border-2 border-[#999] bg-[#fff] focus:outline-none focus:ring-2',
            'placeholder': 'Digite sua senha'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 rounded-md border-2 border-[#999] bg-[#fff] focus:outline-none focus:ring-2',
            'placeholder': 'Confirme sua senha'
        })
    )

    class Meta:
        model = Agricultor
        fields = ['username', 'email', 'password'] # Campos de registro

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md border-2 border-[#999999] bg-[#ffffff]',
            'placeholder': 'Digite seu nome de usuário'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'w-full px-4 py-2 rounded-md border-2 border-[#999999] bg-[#ffffff]',
            'placeholder': 'Digite seu e-mail'
        })

     
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "As senhas não coincidem. Por favor, tente novamente."
            )
    

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
        fields = ['nome', 'icon']
        labels = {
            'nome': 'Nome do Campo',
            'icon': 'Escolha um Ícone',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do Campo', 'class': 'form-control'}),
            'icon': forms.Select(choices=[
                ('bi-house-fill', 'Casa'),
                ('bi-tree-fill', 'Árvore'),
                ('bi-cloud-fill', 'Nuvem'),
                ('bi-flower1', 'Flor'),
            ], attrs={'class': 'form-control'}),
        }

class PlantaCultivadaForm(forms.ModelForm):
    class Meta:
        model = PlantaCultivada
        fields = ['planta', 'data_plantio', 'quantidade_plantada']

        labels = {
            'planta': 'Planta',
            'data_plantio': 'Data do Plantio',
            'quantidade_plantada': 'Quantidade Plantada',
        }

        widgets = {
            'planta': forms.Select(attrs={'class': 'form-control'}),
            'data_plantio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantidade_plantada': forms.NumberInput(attrs={'placeholder': 'Quantidade', 'class': 'form-control'}),
        }
