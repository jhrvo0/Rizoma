from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

# O model de uma planta em nosso código.
class Planta(models.Model):
    FASES_DA_LUA = [
        ('nova', 'Lua Nova'),
        ('crescente', 'Lua Crescente'),
        ('cheia', 'Lua Cheia'),
        ('minguante', 'Lua Minguante'),
    ]
    
    nome = models.CharField(max_length=100)
    dias_de_cultivo = models.IntegerField()
    plantas_amigas = models.ManyToManyField('self', symmetrical=True)
    plantas_inimigas = models.ManyToManyField('self', symmetrical=True)
    fase_da_lua = models.CharField(max_length=10, choices=FASES_DA_LUA)
    inicio_de_temporada = models.DateField()
    fim_de_temporada = models.DateField()

    def __str__(self):
        return self.nome

    def get_plantas_amigas(self):
        return list(self.plantas_amigas.all())

    def get_plantas_inimigas(self):
        return list(self.plantas_inimigas.all())

    def get_dias_de_cultivo(self):
        return self.dias_de_cultivo

# A representação de um campo em nosso código:
class Campo(models.Model):
    nome = models.CharField(max_length=100)
    plantas_cultivadas = models.ManyToManyField('Planta', through='PlantaCultivada')

    def __str__(self):
        return self.nome

    def get_plantas_cultivadas(self):
        return list(self.plantas_cultivadas.all())


# Quando planta se relaciona com campo, temos PlantaCultivada, com outros campos importantes:
class PlantaCultivada(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    data_plantio = models.DateField()
    quantidade_plantada = models.IntegerField()
    percentual_perda = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.planta} plantada no {self.campo} em {self.data_plantio}"

    def estimativa_de_colheita(self):
        """Retorna um número representando a quantidade de dias restantes para colher."""
        dias_cultivo = self.planta.get_dias_de_cultivo()
        return self.data_plantio + models.timedelta(days=dias_cultivo)

    def get_data_de_plantio(self):
        """Retorna a data de plantio."""
        return self.data_plantio


# Para permitir o login com o e-mail, precisamos de um usuário customizado, que é esse:
class Agricultor(AbstractUser):
    username = models.CharField(max_length = 100, unique=False)
    email = models.EmailField(unique=True)
    campos = models.ManyToManyField('Campo')

    USERNAME_FIELD = 'email'  # Usar o email para autenticação
    REQUIRED_FIELDS = []  # Aqui você pode definir outros campos obrigatórios, se necessário

    def __str__(self):
        return self.username

    def listar_campos(self):
        return self.campos.all()