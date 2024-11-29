from django.contrib.auth.models import AbstractUser, BaseUserManager
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
    icone = models.CharField(max_length=50, blank=True, null=True)

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
    icon = models.CharField(max_length=50, default='bi-house-fill') # Ícone do campo
    plantas_cultivadas = models.ManyToManyField('Planta', through='PlantaCultivada')

    def __str__(self):
        return self.nome

    def get_plantas_cultivadas(self):
        return self.plantas_cultivadas.all()


# Quando planta se relaciona com campo, temos PlantaCultivada, com outros campos importantes:
class PlantaCultivada(models.Model):
    planta = models.ForeignKey(Planta, on_delete=models.CASCADE)
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE)
    data_plantio = models.DateField(blank=True, null=True)
    quantidade_plantada = models.IntegerField(blank=True, null=True)
    percentual_perda = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.planta} plantada no {self.campo} em {self.data_plantio}"

    def estimativa_de_colheita(self):
        """Retorna um número representando a quantidade de dias restantes para colher."""
        dias_cultivo = self.planta.get_dias_de_cultivo()
        return self.data_plantio + models.timedelta(days=dias_cultivo)

    def get_data_de_plantio(self):
        """Retorna a data de plantio."""
        return self.data_plantio


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# Para permitir o login com o e-mail, precisamos de um usuário customizado, que é esse:
class Agricultor(AbstractUser):
    username = models.CharField(max_length=100, unique=False)
    email = models.EmailField(unique=True)
    campos = models.ManyToManyField('Campo')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_campos(self):
        return self.campos.all()
    
