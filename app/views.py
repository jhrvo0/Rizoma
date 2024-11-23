from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada, Planta, Evento
from .forms import LoginForm, RegistrationForm, CampoForm, PlantaCultivadaForm, ProfileForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import date, datetime, timedelta
from django.template.loader import render_to_string
from .weather_api import get_weather_data


""" LOGIN / REGISTER / LOGOUT """

# Login
class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Email ou senha incorretos.')
        return render(request, self.template_name, {'form': form})

# Cadastrar
class CadastrarView(View):
    template_name = 'cadastrar.html'
    
    def get(self, request):
        form = RegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.set_password(form.cleaned_data['password']) 
            user.save()
            login(request, user, backend='app.backends.EmailBackend') # Yuri te amo ♥ / Yuri rainha Gabi nadinha
            messages.success(request, f'Bem-vindo, {user.username}!') 
            return redirect('home') 

        return render(request, self.template_name, {'form': form})

# Google login
def google_login(backend, user, response, request, *args, **kwargs):
    if (backend.name == 'google-oauth2'):
        email = response.get('email')

        try:
            user = Agricultor.objects.get(email=email)
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            login(request, user)
        except Agricultor.DoesNotExist:
            user = Agricultor(username=email, email=email)
            user.set_unusable_password()
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            user.save()
            login(request, user)

    return {'user': user}
    
# Logout
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Você foi desconectado com sucesso.')
        return redirect(reverse_lazy('login'))

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

# Criar Campo
class CriarCampoView(LoginRequiredMixin, View):
    template_name = 'campo.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = CampoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CampoForm(request.POST)
        if form.is_valid():
            campo = form.save()
            request.user.campos.add(campo)  # Adiciona um campo para um agricultor.
            response_data = {
                'status': 'success',
                'nome': campo.nome,
                'icone': campo.icon  # Pega o ícone da form.
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors})
        
# Deletar Campo
class DeletarCamposView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        campo_ids = data.get('campo_ids', [])
        
        if not campo_ids:
            return JsonResponse({"status": "error", "message": "Nenhum campo selecionado."}, status=400)
        
        campos = Campo.objects.filter(id__in=campo_ids, agricultor=request.user)
        deleted_count = campos.count()
        campos.delete()
        
        return JsonResponse({"status": "success", "deleted_count": deleted_count})
    
# Visualizar Campo
class VisualizarCampoView(LoginRequiredMixin, View):
    login_url = '/login/' # Se o usuário não estiver autenticado, ele volta pro login.
    
    def get(self, request):
        context = {
            "campos": request.user.get_campos(),
            "current_page" : "campos",
        }
        return render(request, "campos.html", context)
    
    def Filtrar_campos(request):
        if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            nome = request.GET.get("nome", "")
            sort = request.GET.get("sort", "az")  # Parâmetro de ordenação
            campos = campos.objects.all()
            if nome:
                campos = campos.filter(nome__icontains=nome)
                    # Ordenação com base na opção selecionada
            if sort == "az":
                campos = campos.order_by("nome")  # A-Z
            elif sort == "za":
                campos = campos.order_by("-nome")  # Z-A
            elif sort == "recent":
                campos = campos.order_by("-created_at")  # Mais recente
            if campos.exists():
                html = render(request, "components/lista_campos.html", {"campos": campos}).content.decode("utf-8")
            else:
                html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'
            return JsonResponse({"html": html})
        else:
            return JsonResponse({"error": "Invalid request"}, status=400)


# Adicionar Planta
class AdicionarPlantaNoCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id, planta_id):
        campo = get_object_or_404(Campo, id=campo_id)
        planta = get_object_or_404(Planta, id=planta_id)
        form = PlantaCultivadaForm()
        
        context = {
            'form': form,
            'campo': campo,
            'planta': planta,
            'plantas': Planta.objects.all(),
        }
        
        return render(request, 'adicionar_planta.html', context)

    
    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        form = PlantaCultivadaForm(request.POST)
        if form.is_valid():
            planta_cultivada = form.save(commit=False)
            
            plantas_inimigas = planta_cultivada.planta.get_plantas_inimigas()
            campo_plantas = campo.plantas.all()
            
            if any(planta in plantas_inimigas for planta in campo_plantas):
                # Se houver plantas inimigas, exibir mensagem de confirmação
                response_data = {
                    'status': 'confirm',
                    'message': f'{planta_cultivada.planta.nome} é inimiga de outras plantas no campo. Deseja continuar?'
                }
                return JsonResponse(response_data)
            else:
                # Se não houver plantas inimigas, salvar normalmente
                planta_cultivada.campo = campo
                planta_cultivada.save()
                response_data = {
                    'status': 'success',
                    'nome': planta_cultivada.planta.nome,
                    'data_plantio': planta_cultivada.data_plantio,
                    'quantidade_plantada': planta_cultivada.quantidade_plantada,
                }
                return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors})



class DeletarPlantaView(LoginRequiredMixin, View):
    def post(self, request, planta_id):
        planta = get_object_or_404(PlantaCultivada, id=planta_id)
        campo_id = planta.campo.id
        planta.delete()
        messages.success(request, 'Planta deletada com sucesso.')
        return redirect('detalhes-campo', campo_id=campo_id)

class EditarPlantasNoCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id, planta_cultivada_id):
        campo = get_object_or_404(Campo, id=campo_id)
        planta_cultivada = get_object_or_404(PlantaCultivada, id=planta_cultivada_id, campo=campo)
        form = PlantaCultivadaForm(instance=planta_cultivada)
        context = {
            'form': form,
            'campo': campo,
            'planta_cultivada': planta_cultivada,
            'plantas': Planta.objects.all(),
        }
        return render(request, 'editar_planta.html', context)
    
    def post(self, request, campo_id, planta_cultivada_id):
        campo = get_object_or_404(Campo, id=campo_id)
        planta_cultivada = get_object_or_404(PlantaCultivada, id=planta_cultivada_id, campo=campo)

        form = PlantaCultivadaForm(request.POST, instance=planta_cultivada)

        if form.is_valid():
            planta_cultivada = form.save(commit=False)

            nova_planta = request.POST.get('nova_planta')
            if nova_planta:
                planta_cultivada.planta = get_object_or_404(Planta, id=nova_planta)

            nova_quantidade = request.POST.get('quantidade_plantada')
            if nova_quantidade:
                planta_cultivada.quantidade_plantada = nova_quantidade

            planta_cultivada.save()

            response_data = {
                'status': 'success',
                'nome': planta_cultivada.planta.nome,
                'data_plantio': planta_cultivada.data_plantio,
                'quantidade_plantada': planta_cultivada.quantidade_plantada,
            }
            return JsonResponse(response_data)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'errors': errors})
    

# Dá detalhes sobre o campo
class DetalhesCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        plantas_cultivadas = PlantaCultivada.objects.filter(campo=campo)
        context = {
            'campo': campo,
            'plantas_cultivadas': plantas_cultivadas,
            'plantas': Planta.objects.all(),
            'options': get_fab_content('detalhes-campo.html', campo_id=campo_id),
        }
        return render(request, 'detalhes_campo.html', context)


    
class EditarCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id, agricultor=request.user)
        context = {
            'campo': campo
        }
        return render(request, 'edicao_campo.html', context)

    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id, agricultor=request.user)
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao') 

        if nome:
            campo.nome = nome
        if descricao:
            campo.descricao = descricao

        campo.save()
        messages.success(request, 'O campo foi atualizado com sucesso.')
        return redirect('detalhes-campo', campo_id=campo.id)



""" Landing Route """

class LandingView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return redirect('login')

""" Home """

class HomeView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        current_date = date.today()
        atividades_hoje = self.get_atividades_por_data(request.user, current_date)
        
        context = {
            'atividades_hoje': atividades_hoje,
            'current_date': current_date.strftime('%Y-%m-%d'),  # Formatar a data corretamente
            'current_page': 'home',  # adiciona o clima ao contexto
            'options': get_fab_content('home.html')
        }
        return render(request, 'home.html', context)
    
    def get_atividades_por_data(self, user, data):
        return Evento.objects.filter(data_inicio__lte=data, data_fim__gte=data, campos__agricultor=user)

def atividades_por_data(request, data):
    data = datetime.strptime(data, '%Y-%m-%d').date()
    atividades = HomeView().get_atividades_por_data(request.user, data)
    html = render_to_string('components/atividades_lista.html', {'atividades_hoje': atividades})
    return JsonResponse({'html': html})

""" Calendário """

class CalendarioView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        terrenos = list(request.user.campos.all())
        terreno_id = request.GET.get('terreno_id')

        if terrenos:
            if (terreno_id):
                terreno_atual = get_object_or_404(Campo, id=terreno_id, agricultor=request.user)
            else:
                terreno_atual = terrenos[0]
            
            terreno_index = terrenos.index(terreno_atual) if terreno_atual in terrenos else 0
            terreno_anterior = terrenos[terreno_index - 1] if terreno_index > 0 else terrenos[-1]
            terreno_proximo = terrenos[terreno_index + 1] if terreno_index < len(terrenos) - 1 else terrenos[0]
            
            eventos = list(terreno_atual.eventos.values())
            for evento in eventos:
                evento['data_inicio'] = evento['data_inicio'].strftime('%Y-%m-%d')
                if evento['data_fim']:
                    evento['data_fim'] = evento['data_fim'].strftime('%Y-%m-%d')
        else:
            terreno_atual = "Nenhum campo foi registrado ainda"
            terreno_anterior = None
            terreno_proximo = None
            eventos = []

        weather_data = get_weather_data('Carpina')
        if weather_data:
            context = {
                "eventos": json.dumps(eventos),
                "terreno_atual": terreno_atual,
                "terreno_anterior": terreno_anterior,
                "terreno_proximo": terreno_proximo,
                "terrenos": terrenos,
                "current_page": "calendario",
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "condition": weather_data["condition"],
                "icon": weather_data["icon"],
                "moon_phase": weather_data["moon_phase"]
            }
        else:
            context = {
                "eventos": json.dumps(eventos),
                "terreno_atual": terreno_atual,
                "terreno_anterior": terreno_anterior,
                "terreno_proximo": terreno_proximo,
                "terrenos": terrenos,
                "current_page": "calendario",
                "city": "N/A",
                "temperature": "N/A",
                "condition": "N/A",
                "icon": "N/A",
                "moon_phase": "N/A"
            }
        return render(request, 'calendario.html', context)

    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            descricao = data.get('descricao')
            data_inicio = data.get('data_inicio')
            data_fim = data.get('data_fim')
            campo_ids = data.get('campos', [])
            cor = data.get('cor', '#FF5733')

            evento = Evento.objects.create(
                descricao=descricao,
                data_inicio=data_inicio,
                data_fim=data_fim,
                cor=cor
            )

            campos = Campo.objects.filter(id__in=campo_ids)
            evento.campos.set(campos)
            return JsonResponse({"status": "success", "evento_id": evento.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    @method_decorator(csrf_exempt)
    def delete(self, request, evento_id):
        try:
            evento = get_object_or_404(Evento, id=evento_id)
            single_day = request.GET.get('single_day') == 'true'
            date = request.GET.get('date')
            if single_day and date:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                
                if evento.data_inicio == evento.data_fim:
                    evento.delete()
                elif evento.data_inicio == date_obj:
                    evento.data_inicio = date_obj + timedelta(days=1)
                    evento.save()
                elif evento.data_fim == date_obj:
                    evento.data_fim = date_obj - timedelta(days=1)
                    evento.save()
                else:
                    # Criar um novo evento para os dias após o dia excluído
                    novo_evento_apos = Evento.objects.create(
                        descricao=evento.descricao,
                        data_inicio=date_obj + timedelta(days=1),
                        data_fim=evento.data_fim,
                        cor=evento.cor
                    )
                    novo_evento_apos.campos.set(evento.campos.all())
                    
                    # Criar um novo evento para os dias antes do dia excluído
                    novo_evento_antes = Evento.objects.create(
                        descricao=evento.descricao,
                        data_inicio=evento.data_inicio,
                        data_fim=date_obj - timedelta(days=1),
                        cor=evento.cor
                    )
                    novo_evento_antes.campos.set(evento.campos.all())
                    
                    # Excluir o evento original
                    evento.delete()
            else:
                evento.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
        
class ProfileView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        user = request.user
        form = ProfileForm(instance=user)
        context = {
            'form': form,
            'nome': user.username,
            'email': user.email,
            'quantidade_campos': user.campos.count(),
        }
        return render(request, 'perfil.html', context)
    def post(self, request):
        user = request.user
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('perfil')
        context = {
            'form': form,
            'nome': user.username,
            'email': user.email,
            'quantidade_campos': user.campos.count(),
        }
        return render(request, 'perfil.html', context)
    

class CamposView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):

        campos = []  
        context = {
            'campos': campos,
        }
        return render(request, 'campos.html', context)
    
def Filtrar_campos(request):
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        nome = request.GET.get("nome", "")
        tipo = request.GET.get("tipo", "")
        sort = request.GET.get("sort", "az")
        
        campos = request.user.get_campos()

        if nome:
            campos = campos.filter(nome__icontains=nome)
        
        if sort == "az":
            campos = campos.order_by("nome")
        elif sort == "za":
            campos = campos.order_by("-nome")
        elif sort == "recent":
            campos = campos.order_by("-created_at")

        if campos.exists():
            html = render_to_string("components/lista_campos.html", {"campos": campos}, request=request)
        else:
            html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'

        return JsonResponse({"html": html})
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)

def pagatividades(request):
    eventos = Evento.objects.all()  # Obtenha todos os eventos
    return render(request, 'atividades.html', {'eventos': eventos})


class ListaPlantasView(LoginRequiredMixin, View):
    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id)
        context = {
            'campo': campo,
            'plantas': Planta.objects.all(),
        }
        return render(request, 'lista_plantas.html', context)


class DetalhePlantaView(LoginRequiredMixin, View):
    def get(self, request, id):
        context={
            'planta': Planta.objects.get(id=id),
        }
        return render(request, 'perfil_planta.html', context)


class BuscaPlantaView(LoginRequiredMixin, View):
    def get(self, request, query):
        plantas = Planta.objects.filter(nome__icontains=query)
        context = {
            'plantas': plantas
        }
        return render(request, 'lista_campos.html', context)


def get_fab_content(location, campo_id=None):

    # Adicione uma location aqui e chame essa função na view da location. Veja home para um exemplo.
    # - icon é o ícone (bootstrap icons) que vai aparecer na opção.
    # - link é o redirect.
    # - name é a opção que aparece escrita.

    options = []
    if location == 'home.html':
        options = [
            {"icon": "bi-house-fill", "link": "home", "name": "Clientes"},
            {"icon": "bi-house-fill", "link": "home", "name": "Novo plantio"},
            {"icon": "bi-house-fill", "link": "home", "name": "Novo campo"}
        ]
    elif location == 'detalhes-campo.html' and campo_id is not None:
        options = [
            {"icon": "bi-house-fill", "link": 'lista-plantas', 'args': [campo_id], "name": "Adicionar Planta"},
        ]
    return options

        


class ModalView(View):
    def get(self, request):
        context = {
            'message': 'test',
        }
        return render(request, "components/component_modal.html", context)