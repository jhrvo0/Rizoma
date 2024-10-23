from django.contrib import admin
from django.urls import include, path
from app.views import (
    CadastrarView, LoginView, LogoutView, LandingView, google_login, 
    VisualizarCampoView, CriarCampoView, HomeView, DetalhesCampoView, 
    AdicionarPlantaNoCampoView, DeletarPlantaView, DeletarCampoView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/', LoginView.as_view(), name='login'),
    path('social-login/', google_login, name='social_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('cadastrar/', CadastrarView.as_view(), name='cadastrar'),

    # Landing and Home
    path('', LandingView.as_view(), name='landing'),
    path('home/', HomeView.as_view(), name="home"),

    # Campo URLs
    path('campos/', VisualizarCampoView.as_view(), name='campos'),
    path('novo-campo/', CriarCampoView.as_view(), name='novo-campo'),
    path('campos/<int:campo_id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    path('adicionar-planta/<int:campo_id>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    path('deletar-planta/<int:planta_id>/', DeletarPlantaView.as_view(), name='deletar-planta'),
    path('deletar-campo/<int:campo_id>/', DeletarCampoView.as_view(), name='deletar-campo'),
]