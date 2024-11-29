from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from .models import Agricultor, Campo, PlantaCultivada, Planta
from .forms import LoginForm, RegistrationForm, CampoForm, PlantaCultivadaForm
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
import json
from datetime import datetime
from django.template.loader import render_to_string
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
                campos = campos.order_by("nome__lor")  # Ordenação case-insensitive
            elif sort == "za":
                campos = campos.order_by("-nome__lor")  # Ordenação reversa case-insensitive
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
        context = {
            'current_page': 'home',
            'options': get_fab_content('home.html'),
        }
        return render(request, 'home.html', context)
            
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
