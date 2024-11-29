
from django.contrib import admin
from django.urls import path, include
from app.views import HomeView, CalendarioView, LoginView, LogoutView, CadastrarView, VisualizarCampoView, CriarCampoView, EditarCampoView, AdicionarPlantaNoCampoView, DetalhesCampoView, LandingView, google_login, DeletarCamposView, DeletarPlantaView, Filtrar_campos, ListaPlantasView, DetalhePlantaView, EditarPlantasNoCampoView, pagatividades
from app.views import SelecionarQuantidadeParaAdicionarPlantaView, SelecionarSubcampoParaAdicionarPlantaView

# Funções
from app.views import AtividadesView, get_atividades_por_data, get_atividades_do_dia

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('admin/', admin.site.urls),
    path('admin/clearcache/', include('clearcache.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/', LoginView.as_view(), name='login'),
    path('social-login/', google_login, name='social_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('cadastrar/', CadastrarView.as_view(), name='cadastrar'),
    path('home/', HomeView.as_view(), name="home"),

    path('home/', HomeView.as_view(), name='home'),
    
    path('atividades/', pagatividades, name='atividades'),
    
    path('novo-campo/', CriarCampoView.as_view(), name='novo-campo'),

    path('calendario/<int:evento_id>/', CalendarioView.as_view(), name='calendario-delete'),
    path('deletar-planta/<int:planta_id>/', DeletarPlantaView.as_view(), name='deletar-planta'),
    path('filtrar-campos/', Filtrar_campos, name='Filtrar-campos'),

    path('calendario/', CalendarioView.as_view(), name='calendario'),

    path('planta/<int:id>/', DetalhePlantaView.as_view(), name='detalhe-planta'),

    path('editar-planta/<int:campo_id>/<int:planta_cultivada_id>/', EditarPlantasNoCampoView.as_view(), name='editar-planta'),
    path('adicionar-planta/', AdicionarPlantaNoCampoView.as_view(), name='adicionar-planta'),
    

    path('campos/', VisualizarCampoView.as_view(), name='campos'),
    path('campo/<int:campo_id>/', DetalhesCampoView.as_view(), name='detalhes-campo'),
    path('campo/<int:campo_id>/lista-plantas/', ListaPlantasView.as_view(), name='lista-plantas'),
    path('campo/<int:campo_id>/lista-plantas/<int:planta_id>/', SelecionarQuantidadeParaAdicionarPlantaView.as_view(), name='adicionar-planta'),
    path('campo/<int:campo_id>/lista-plantas/<int:planta_id>/adicionar-planta/<int:quantidade>/', SelecionarSubcampoParaAdicionarPlantaView.as_view(), name='selecionar-subcampo'),
    path('campo/<int:campo_id>/lista-plantas/<int:planta_id>/adicionar-planta/<int:quantidade>/', SelecionarSubcampoParaAdicionarPlantaView.as_view(), name='adicionar-planta-campo'),    
    path('campo/<int:campo_id>/editar/', EditarCampoView.as_view(), name='edicao_campo'),
    path('criar-campo/', CriarCampoView.as_view(), name='criar-campo'),

    path('deletar-campos/', DeletarCamposView.as_view(), name='deletar-campos'),
    path('editar-campo/<int:campo_id>/', EditarCampoView.as_view(), name='editar-campo'),
]
