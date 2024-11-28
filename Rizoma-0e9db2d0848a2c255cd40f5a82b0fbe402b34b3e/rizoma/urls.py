from django.contrib import admin
from django.urls import include, path
from app.views import CadastrarView, LoginView, LogoutView, LandingView, google_login, VisualizarCampoView, CriarCampoView, HomeView, DetalhesCampoView, AdicionarPlantaNoCampoView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('social_django.urls', namespace='social')),
    path('login/', LoginView.as_view(), name='login'),
    path('social-login/', google_login, name='social_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('cadastrar/', CadastrarView.as_view(), name='cadastrar'),

    path('', LandingView.as_view(), name='landing'),
    path('home/', HomeView.as_view(), name="home"),
    path('campos/', VisualizarCampoView.as_view(), name='campos'),
    path('novo-campo/', CriarCampoView.as_view(), name='novo-campo'),
    path('adicionar-planta/<int:campo_id>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    path('campos/<int:id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
]