# Em accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View
# (O login_required e CustomUser não são mais usados aqui, mas pode deixar)
from django.contrib.auth.decorators import login_required 
from .forms import SignUpForm, SignInForm
from .models import CustomUser

class AuthView(View):
    """
    View principal que gerencia login e registro
    """
    def get(self, request):
        # Se já estiver logado, redireciona para dashboard
        if request.user.is_authenticated:
            # [CONSERTO 1: O NOME DA URL MUDOU]
            return redirect('dashboard_home') 
        
        signup_form = SignUpForm()
        signin_form = SignInForm()
        
        context = {
            'signup_form': signup_form,
            'signin_form': signin_form,
        }
        return render(request, 'accounts/auth.html', context)
    
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'signup':
            return self.handle_signup(request)
        elif action == 'signin':
            return self.handle_signin(request)
        
        # [CONSERTO 2: O NOME DA URL MUDOU]
        return redirect('login')
    
    def handle_signup(self, request):
        """
        Processa o registro de novo usuário
        """
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            # Cria o usuário (senha já é criptografada automaticamente)
            user = form.save()
            
            # Faz login automático após registro
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Mensagem de sucesso
            messages.success(
                request, 
                f'Bem-vindo, {user.get_full_name()}! Sua conta foi criada com sucesso.'
            )
            return redirect('dashboard_home') # <-- Este já estava certo!
        else:
            # Mostra erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            
            signin_form = SignInForm()
            context = {
                'signup_form': form,
                'signin_form': signin_form,
                'active_tab': 'signup'
            }
            return render(request, 'accounts/auth.html', context)
    
    def handle_signin(self, request):
        """
        Processa o login do usuário
        """
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autentica o usuário
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Login bem-sucedido
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.get_full_name()}!')
            return redirect('dashboard_home') # <-- Este também já estava certo!
        else:
            # Credenciais inválidas
            messages.error(request, 'Email ou senha incorretos. Tente novamente.')
            
            signup_form = SignUpForm()
            signin_form = SignInForm()
            context = {
                'signup_form': signup_form,
                'signin_form': signin_form,
                'active_tab': 'signin'
            }
            return render(request, 'accounts/auth.html', context)

# 
# [FUNÇÕES FANTASMAS 'logout_view' e 'dashboard_view' APAGADAS]
#