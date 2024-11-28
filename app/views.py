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
from django.utils import timezone
from django.utils.decorators import method_decorator
import json
from datetime import date, datetime, timedelta
from django.template.loader import render_to_string
from .weather_api import get_weather_data
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.db.models import Sum


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

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):

        return super().dispatch(*args, **kwargs)
    def get(self, request, *args, **kwargs):
        form = CampoForm()
        return render(request, 'adicao_campo.html', {'form': form})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
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
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        # Carrega os dados da requisição
        data = json.loads(request.body)
        campo_ids = data.get('campo_ids', [])
        
        if not campo_ids:
            return JsonResponse({"status": "error", "message": "Nenhum campo selecionado."}, status=400)
        
        # Filtra os campos para garantir que sejam do agricultor logado
        campos = Campo.objects.filter(id__in=campo_ids, agricultor=request.user)

        # Exclui os eventos associados a cada campo
        for campo in campos:
            campo.eventos_relacionados.all().delete()  # Use the correct related_name

        # Conta os campos que foram excluídos
        deleted_count = campos.count()
        campos.delete()
        
        return JsonResponse({"status": "success", "deleted_count": deleted_count})

# Visualizar Campo
class VisualizarCampoView(LoginRequiredMixin, View):
    login_url = '/login/'  # Se o usuário não estiver autenticado, ele volta para o login.

    def get(self, request):
        context = {
            "campos": request.user.get_campos(),
            "current_page": "campos",   
            'options': get_fab_content('campos.html'),
        }
        return render(request, "campos.html", context)

    def Filtrar_campos(request):
        if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            nome = request.GET.get("nome", "").strip()
            sort = request.GET.get("sort", "az")  # Parâmetro de ordenação
            
            # Garante que os campos sejam relacionados ao usuário logado
            campos = request.user.get_campos()

            # Filtro por nome com case-insensitive usando `__icontains`
            if nome:
                campos = campos.filter(nome__icontains=nome)

            # Ordenação com base na opção selecionada
            if sort == "az":
                campos = campos.order_by("nome__lower")  # Ordenação case-insensitive
            elif sort == "za":
                campos = campos.order_by("-nome__lower")  # Ordenação reversa case-insensitive
            elif sort == "recent":
                campos = campos.order_by("-created_at")  # Ordenar por mais recente

            # Renderiza os campos filtrados no componente de lista
            if campos.exists():
                html = render(request, "components/lista_campos.html", {"campos": campos}).content.decode("utf-8")
            else:
                html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'

            return JsonResponse({"html": html})
        
        else:
            return JsonResponse({"error": "Invalid request"}, status=400)





# Selecionar quantidade de planta para adicionar

class SelecionarQuantidadeParaAdicionarPlantaView(LoginRequiredMixin, View):
    def get(self, request, campo_id, planta_id):
        campo = get_object_or_404(Campo, id=campo_id)
        planta = get_object_or_404(Planta, id=planta_id)
        context = {
            'campo': campo,
            'planta': planta,
            'plantas': Planta.objects.all(),
        }
        return render(request, 'adicionar_planta.html', context)
    
    def post(self, request, campo_id, planta_id):
        quantidade = request.POST.get('quantidade_plantada')
        return redirect('selecionar-subcampo', campo_id=campo_id, planta_id=planta_id, quantidade=quantidade )


class SelecionarSubcampoParaAdicionarPlantaView(LoginRequiredMixin, View):
    def get(self, request, campo_id, planta_id, quantidade):
        campo = get_object_or_404(Campo, id=campo_id)
        subcampo_no = {
            1: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=1),
            2: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=2),
            3: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=3),
            4: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=4),
        }
        context = {
            'subcampo_no': subcampo_no,
            'campo': campo,
            'planta_id': planta_id,
            'quantidade': quantidade,
        }
        return render(request, 'selecionar_subcampo.html', context)

    
class SelecionarSubcampoParaAdicionarPlantaView(LoginRequiredMixin, View):
    def get(self, request, campo_id, planta_id, quantidade):
        campo = get_object_or_404(Campo, id=campo_id)
        subcampo_no = {
            1: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=1),
            2: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=2),
            3: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=3),
            4: PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=4),
        }
        context = {
            'subcampo_no': subcampo_no,
            'campo': campo,
            'planta_id': planta_id,
            'quantidade': quantidade,
        }
        return render(request, 'selecionar_subcampo.html', context)

    def post(self, request, campo_id, planta_id, quantidade):
        subcampo = request.POST.get("subcampo")
        posicao = PlantaCultivada.objects.filter(campo_id=campo_id, subcampo=subcampo).count() + 1

        nova_planta = PlantaCultivada(
            planta=Planta.objects.get(id=planta_id),
            campo=Campo.objects.get(id=campo_id),
            quantidade_plantada=quantidade,
            subcampo=subcampo,
            posicao_subcampo=posicao,
        )
        nova_planta.save()
        return redirect('adicionar-planta-campo', campo_id=campo_id, planta_id=planta_id, quantidade=quantidade)


#class AdicionarPlantaView(LoginRequiredMixin, View):


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
        total_quantidade_plantada = plantas_cultivadas.aggregate(total=Sum('quantidade_plantada'))['total'] or 0

        subcampo_no = {
            1: plantas_cultivadas.filter(subcampo=1),
            2: plantas_cultivadas.filter(subcampo=2),
            3: plantas_cultivadas.filter(subcampo=3),
            4: plantas_cultivadas.filter(subcampo=4),
        }

        tipos_plantas = plantas_cultivadas.values('planta').distinct().count()

        context = {
            'campo': campo,
            'subcampo_no': subcampo_no,
            'plantas_cultivadas': plantas_cultivadas,
            'plantas': Planta.objects.all(),
            'options': get_fab_content('detalhes-campo.html', campo_id=campo_id),
            'tipos_plantas': tipos_plantas,
            'qtd_plantas': total_quantidade_plantada,
            'current_page': "campos",
            'campo_id': campo_id,
        }
        return render(request, 'detalhes_campo.html', context)
        

class EditarCampoView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id, agricultor=request.user)
        form = CampoForm(instance=campo)  # Create form with the existing campo data
        context = {
            'campo': campo,
            'form': form,  # Pass the form to the template
        }
        return render(request, 'edicao_campo.html', context)

    def post(self, request, campo_id):
        campo = get_object_or_404(Campo, id=campo_id, agricultor=request.user)
        form = CampoForm(request.POST, instance=campo)  # Bind form with POST data

        if form.is_valid():  # Validate the form
            form.save()  # Save the updated campo
            return JsonResponse({'success': True, 'message': 'Campo editado com sucesso'})
        else:
            return JsonResponse({'success': False, 'message': 'Erro ao editar o campo', 'errors': form.errors})
        
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
        current_date = timezone.now().date()
        atividades = HomeView.get_atividades_por_data(request.user, current_date)
        context = {
            'current_date': current_date.strftime('%Y-%m-%d'),
            'current_page': 'home',
            'options': get_fab_content('home.html'),
            'qtd_atividades': atividades.count(),
            'hoje': current_date  # Add today's date to the context
        }
        return render(request, 'home.html', context)

    @staticmethod
    def get_atividades_por_data(user, data):
        return Evento.objects.filter(
            data_inicio__lte=data,
            data_fim__gte=data,
            campos__agricultor=user
        )

def get_atividades_por_data(request, data):
    data = datetime.strptime(data, '%Y-%m-%d').date()
    atividades = HomeView.get_atividades_por_data(request.user, data)
    context = {
        'atividades_hoje': atividades, 
        'qtd_atividades': atividades.count(),
        'hoje': timezone.now().date()
    }
    html = render_to_string('components/home/tarefas_do_dia.html', context)
    return JsonResponse({'html': html})


""" Calendário """

class CalendarioView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        terrenos = list(request.user.campos.all())
        terreno_id = request.GET.get('terreno_id')
        cores = ["#FF0000", "#FD7E14", "#FFC107", "#28A745", "#007BFF", "#8A2BE2", "#FF5733", "#17A2B8", "#DA70D6", "#FFFF00"]

        if terrenos:
            if terreno_id:
                terreno_atual = get_object_or_404(Campo, id=terreno_id, agricultor=request.user)
            else:
                terreno_atual = terrenos[0]
            
            terreno_index = terrenos.index(terreno_atual) if terreno_atual in terrenos else 0
            terreno_anterior = terrenos[terreno_index - 1] if terreno_index > 0 else terrenos[-1]
            terreno_proximo = terrenos[terreno_index + 1] if terreno_index < len(terrenos) - 1 else terrenos[0]
            
            eventos = []
            if hasattr(terreno_atual, 'eventos') and terreno_atual.eventos is not None:
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

        moon = weather_data["moon_phase"]
        translated_moon = "moon"

        if moon == "New Moon":
            translated_moon = "Lua Nova"
        elif moon == "Waxing Crescent":
            translated_moon = "Crescente"
        elif moon == "First Quarter":
            translated_moon = "Quarto Crescente"
        elif moon == "Waxing Gibbous":
            translated_moon = "Gibosa Crescente"
        elif moon == "Full Moon":
            translated_moon = "Lua Cheia"
        elif moon == "Waning Gibbous":
            translated_moon = "Gibosa Minguante"
        elif moon == "Last Quarter" or moon == "Third Quarter":
            translated_moon = "Quarto Minguante"
        elif moon == "Waning Crescent":
            translated_moon = "Minguante"
        else:
            translated_moon = "Fase lunar desconhecida"
        
        if weather_data:
            weather_context = {
                "city": weather_data["city"],
                "temperature": weather_data["temperature"],
                "condition": weather_data["condition"],
                "icon": weather_data["icon"],
                "moon_phase": translated_moon
            }
        else:
            weather_context = {
                "city": "N/A",
                "temperature": "N/A",
                "condition": "N/A",
                "icon": "N/A",
                "moon_phase": "N/A"
            }

        context = {
            "eventos": json.dumps(eventos),
            "terreno_atual": terreno_atual,
            "terreno_anterior": terreno_anterior,
            "terreno_proximo": terreno_proximo,
            "terrenos": terrenos,
            "current_page": "calendario",
            "cores": cores,
            **weather_context
        }

        return render(request, 'calendario.html', context)

    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        data = json.loads(request.body)
        nome = data.get('nome', 'Tarefa')
        descricao = data.get('descricao')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim', data_inicio)
        cor = data.get('cor', '#FF5733')
        campo_id = data.get('campos')[0]
        
        try:
            campo = Campo.objects.get(id=campo_id)
            evento = Evento.objects.create(
                nome=nome,
                descricao=descricao,
                data_inicio=data_inicio,
                data_fim=data_fim,
                cor=cor,
                campos=campo,
            )
            return JsonResponse({'status': 'success', 'evento_id': evento.id})
        
        except Campo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Campo não encontrado'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    
        
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
    
def Filtrar_campos(request):
    if request.method == "GET" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        nome = request.GET.get("nome", "").strip().upper()  # Converter o nome para maiúsculas
        sort = request.GET.get("sort", "az")  # Parâmetro de ordenação
        
        campos = request.user.get_campos()

        if nome:
      
            campos = campos.filter(nome__icontains=nome)

        if sort == "az":
            campos = sorted(campos, key=lambda campo: campo.nome.upper())  
        elif sort == "za":
            campos = sorted(campos, key=lambda campo: campo.nome.upper(), reverse=True)  
        elif sort == "recent":
            campos = campos.order_by("-created_at") 

        if campos:
            html = render_to_string("components/lista_campos.html", {"campos": campos}, request=request)
        else:
            html = '<div class="p-4 rounded-lg text-center"><p class="text-gray-600 font-semibold">Nenhum campo encontrado.</p></div>'

        return JsonResponse({"html": html})
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


class ListaPlantasView(LoginRequiredMixin, View):
    login_url = '/login/'
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

    # Adicione uma location aqui e chame essa função na view da location. 
    # Veja a view de home para um exemplo.
    # - icon é o ícone (bootstrap icons) que vai aparecer na opção.
    # - link é o redirect.
    # - name é a opção que aparece escrita.

    options = []
    if location == 'home.html':
        options = [
            {"icon": "/app/images/clientes.svg", "link": "home", "name": "Clientes"},
            {"icon": "/app/images/plantio.svg", "link": "home", "name": "Novo plantio"},
            {"icon": "/app/images/campo.svg", "link": "home", "name": "Novo campo"},
            {"icon": "/app/images/tarefa.svg", "link": "home", "name": "Nova tarefa"},
        ]
    elif location == 'detalhes-campo.html' and campo_id is not None:
        options = [
            {"icon": "/app/images/plantio.svg", "link": 'lista-plantas', 'args': [campo_id], "name": "Adicionar Planta"},
        ]
    elif location == 'campos.html':
        options = [
            {"icon": "/app/images/campo.svg", "link": "criar-campo", "name": "Criar Campo"},
        ]
    else:
        options= [ 
            {"icon": "bi-house-fill", "link": "", "name": "DEBUG: PASSOU NOME ERRADO PARA get_fab_content"},
        ]
    return options

class AtividadesView(LoginRequiredMixin, View):    
    def get(self, request):
        campos = request.user.campos.all()
        eventos = Evento.objects.filter(campos__in=campos)
        context = {
            'atividades': eventos,
            'count': eventos.count()
        }
        return render(request, "atividades.html", context)

    @staticmethod
    def get_atividades_do_dia(user, data):
        return Evento.objects.filter(
            data_inicio__lte=data,
            data_fim__gte=data,
            campos__agricultor=user
        )

def get_atividades_do_dia(request, data):
    data = datetime.strptime(data, '%Y-%m-%d').date()
    atividades = AtividadesView.get_atividades_do_dia(request.user, data)
    context = {
        'atividades_hoje': atividades, 
        'qtd_atividades': atividades.count(),
        'hoje': timezone.now().date()
    }
    html = render_to_string('components/atividades_lista.html', context)
    return JsonResponse({'html': html})


#def pagatividades(request):
#    eventos = Evento.objects.all()  # Obtenha todos os eventos
#    terrenos = Campo.objects.all()  # Obtenha todos os terrenos
#    return render(request, 'atividades.html', {'eventos': eventos, 'terrenos': terrenos})