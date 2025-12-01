from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django_countries.fields import CountryField
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado unificado.
    """
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=150, verbose_name='Nome', null=True, blank=True)
    last_name = models.CharField(max_length=150, verbose_name='Sobrenome', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True)
    timezone = models.CharField(max_length=100, blank=True, default='UTC')

    email_digest = models.BooleanField(default=True, verbose_name="Resumo Semanal")
    security_alerts = models.BooleanField(default=True, verbose_name="Alertas de Segurança")
    marketing_emails = models.BooleanField(default=False, verbose_name="E-mails de Marketing")

    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    google_profile_picture = models.URLField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'users'

    def __str__(self) -> str:
        return str(self.email)

    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return str(self.email)
