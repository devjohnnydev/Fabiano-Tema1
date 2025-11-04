from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """
    Gerenciador customizado para criar usuários e superusuários
    """
    
    # --- INÍCIO DA MUDANÇA (create_user) ---
    # Tornamos o método flexível aceitando **extra_fields
    # O social-django vai chamar: create_user(email='email@google.com')
    # O createsuperuser vai chamar: create_user(email='...', password='...', first_name='...', ...)
    
    def create_user(self, email, password=None, **extra_fields): # <-- MUDANÇA
        if not email:
            raise ValueError('O usuário deve ter um email')
        
        email = self.normalize_email(email)
        
        # Passa os campos extras para o modelo
        user = self.model(email=email, **extra_fields) # <-- MUDANÇA
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    # --- FIM DA MUDANÇA (create_user) ---
    
    
    # --- INÍCIO DA MUDANÇA (create_superuser) ---
    # Ajustamos para usar o novo create_user
    
    def create_superuser(self, email, first_name, last_name, password):
        
        # Define os campos que serão passados como **extra_fields
        extra_fields = {                          # <-- MUDANÇA
            'first_name': first_name,
            'last_name': last_name,
            'is_staff': True,
            'is_superuser': True
        }

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Chama o create_user flexível
        return self.create_user(email, password, **extra_fields) # <-- MUDANÇA
    # --- FIM DA MUDANÇA (create_superuser) ---


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado
    Campos: id (automático), email, first_name, last_name, senha (criptografada)
    """
    # Campos principais
    email = models.EmailField(unique=True, verbose_name='Email')
    
    # --- INÍCIO DA MUDANÇA (Campos) ---
    # Permitimos que sejam nulos, pois o social-django
    # cria o usuário primeiro e preenche os nomes DEPOIS.
    first_name = models.CharField(max_length=150, verbose_name='Nome', null=True, blank=True) # <-- MUDANÇA
    last_name = models.CharField(max_length=150, verbose_name='Sobrenome', null=True, blank=True) # <-- MUDANÇA
    # --- FIM DA MUDANÇA (Campos) ---
    
    # Campos de controle
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Campos para Google OAuth (opcional)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    # Define email como campo de login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Isso afeta apenas o 'createsuperuser'
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"