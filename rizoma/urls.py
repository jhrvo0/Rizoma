from django.contrib import admin
from django.urls import path, include
from app.views import HomeView, CalendarioView, LoginView, LogoutView, CadastrarView, VisualizarCampoView, CriarCampoView, EditarCampoView, AdicionarPlantaNoCampoView, DetalhesCampoView, LandingView, google_login, DeletarCampoView, DeletarPlantaView, ProfileView, CamposView, Filtrar_campos, atividades_por_data, pagatividades, ListaPlantasView, DetalhePlantaView, EditarPlantasNoCampoView
from app.views import ModalView

#WeatherView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/clearcache/', include('clearcache.urls')),

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

    path('campos/<int:id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    
    path('calendario/<int:evento_id>/', CalendarioView.as_view(), name='calendario-delete'),
    path('deletar-campo/<int:campo_id>/', DeletarCampoView.as_view(), name='deletar-campo'),
    path('deletar-planta/<int:planta_id>/', DeletarPlantaView.as_view(), name='deletar-planta'),
    path('filtrar-campos/', Filtrar_campos, name='Filtrar-campos'),
    path('perfil/', ProfileView.as_view(), name='perfil'),
    path('campos/', CamposView.as_view(), name='campos'),
    path('atividades/<str:data>/', atividades_por_data, name='atividades_por_data'),
    path('atividades/', pagatividades, name='atividades'),

    path('calendario/', CalendarioView.as_view(), name='calendario'),

    path('planta/<int:id>/', DetalhePlantaView.as_view(), name='detalhes-planta'),
    path('editar-planta/<int:campo_id>/<int:planta_cultivada_id>/', EditarPlantasNoCampoView.as_view(), name='editar-planta'),
    
    path('adicionar-planta/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    
    path('adicionar-planta/<int:campo_id>/<int:planta_id>/<int:quantidade>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),

    path('campo/<int:campo_id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    path('campo/<int:campo_id>/lista-plantas/', ListaPlantasView.as_view(), name='lista-plantas'),
    path('campo/<int:campo_id>/lista-plantas/<int:planta_id>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    path('campo/<int:campo_id>/lista-plantas/<int:planta_id>/adicionar-planta/<int:quantidade>/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    
    path('campo/<int:campo_id>/editar/', EditarCampoView.as_view(), name='edicao_campo'),

    path('modal/', ModalView.as_view(), name='modal'),

    #path('weather/', WeatherView.as_view(), name='weather'),
]