from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import HomeView, CalendarioView, LoginView, LogoutView, CadastrarView, VisualizarCampoView, CriarCampoView, AdicionarPlantaNoCampoView, DetalhesCampoView, LandingView, google_login, DeletarCampoView, DeletarPlantaView, ProfileView, CamposView, Filtrar_campos

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

    # Campo URLs
    path('campos/', VisualizarCampoView.as_view(), name='campos'),
    path('novo-campo/', CriarCampoView.as_view(), name='novo-campo'),
    path('campos/<int:campo_id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    path('adicionar-planta/<int:campo_id>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    path('campos/<int:id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    path('calendario/', CalendarioView.as_view(), name='calendario'),
    path('calendario/<int:evento_id>/', CalendarioView.as_view(), name='calendario-delete'),
    path('deletar-campo/<int:campo_id>/', DeletarCampoView.as_view(), name='deletar-campo'),
    path('deletar-planta/<int:planta_id>/', DeletarPlantaView.as_view(), name='deletar-planta'),
    path('filtrar-campos/', Filtrar_campos, name='Filtrar-campos'),
    path('perfil/', ProfileView.as_view(), name='perfil'),
    path('campos/', CamposView.as_view(), name='campos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)