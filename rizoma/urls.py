from django.contrib import admin
from django.urls import include, path
from app.views import CadastrarView, LoginView, LogoutView, LandingView, google_login

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('cadastrar/', CadastrarView.as_view(), name='cadastrar'),
    path('accounts/', include('allauth.urls')),
    path('social-login/', google_login, name='social_login'),
]