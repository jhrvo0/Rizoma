from django.contrib import admin
from django.urls import include, path
from app.views import CadastrarView, LoginView, LogoutView, LandingView, google_login, VisualizarCampoView, CriarCampoView, HomeView

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('home/', HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('cadastrar/', CadastrarView.as_view(), name='cadastrar'),
    path('accounts/', include('allauth.urls')),
    path('social-login/', google_login, name='social_login'),
    path('campos/', VisualizarCampoView.as_view(), name='campos'),
    path('novo-campo/', CriarCampoView.as_view(), name='novo-campo'),
]