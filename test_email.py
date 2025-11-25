import os
import django
from dotenv import load_dotenv # <--- O PULO DO GATO

# 1. Carrega as variáveis do arquivo .env
# (Ele procura o arquivo .env na mesma pasta)
load_dotenv()

# 2. Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("--- DIAGNÓSTICO DE EMAIL ---")

# Debug: Mostra o que ele leu do .env (só pra garantir)
# NÃO mostra a senha por segurança, só o email e a porta
print(f"1. Usuário lido do .env: {settings.EMAIL_HOST_USER}")
print(f"2. Porta configurada: {settings.EMAIL_PORT}")
print(f"3. Backend ativo: {settings.EMAIL_BACKEND}")

print("\n--- TENTANDO ENVIAR AGORA ---")

try:
    send_mail(
        subject='Teste de Envio - Media Scope',
        message='Se chegou aqui, seu .env está funcionando perfeitamente! 🚀',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER], # Manda pra você mesmo
        fail_silently=False,
    )
    print("✅ SUCESSO ABSOLUTO! O email foi despachado.")
    print("👉 Verifique sua caixa de entrada (e o SPAM).")
except Exception as e:
    print("❌ FALHA NO ENVIO:")
    print(e)
    print("-" * 30)
    print("DICA: Se o erro for 'Username and Password not accepted', sua senha de app no .env pode estar errada ou não foi lida.")