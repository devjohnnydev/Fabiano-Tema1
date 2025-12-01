# Em accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from .forms import SignUpForm, SignInForm, ProfileForm, NotificationForm
from django.contrib.auth import views as auth_views

# --- 1. LOGIN VIEW (Substitui o AuthView / handle_signin) ---
def login_view(request):
    # Se já estiver logado, manda pro dashboard
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == 'POST':
        # Pega os dados (compatível com seu form SignInForm)
        email = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirecionamento inteligente (se veio de um link ?next=...)
            next_url = request.GET.get('next', 'dashboard_home')
            messages.success(request, f'Bem-vindo de volta, {user.get_full_name()}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou senha incorretos.')
    
    # Se for GET ou Erro, mostra a tela de login
    # Passamos active_tab='signin' para o CSS saber qual aba abrir
    context = {
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'active_tab': 'signin' 
    }
    return render(request, 'accounts/auth.html', context)


# --- 2. REGISTER VIEW (Substitui o AuthView / handle_signup) ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Login automático após cadastro
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
            return redirect('dashboard_home')
        else:
            # Mostra erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = SignUpForm()

    context = {
        'signup_form': form,
        'signin_form': SignInForm(),
        'active_tab': 'signup' # Abre na aba de cadastro
    }
    return render(request, 'accounts/auth.html', context)


# --- 3. LOGOUT VIEW ---
def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da conta.")
    return redirect('home') # Manda pra Landing Page


# --- 4. SETTINGS VIEW (Mantida e Ajustada) ---
@login_required
def settings_view(request):
    user = request.user
    active_tab = 'profile' # Aba padrão
    
    # Verifica se o usuário tem senha (para login social)
    if user.has_usable_password():
        PasswordFormClass = PasswordChangeForm
    else:
        PasswordFormClass = SetPasswordForm

    # Inicializa forms
    profile_form = ProfileForm(instance=user)
    notification_form = NotificationForm(instance=user)
    password_form = PasswordFormClass(user)
    
    google_connected = user.social_auth.filter(provider='google-oauth2').exists()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # --- PERFIL ---
        if action == 'update_profile':
            active_tab = 'profile'
            profile_form = ProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso!')
                return redirect('settings')

        # --- SENHA ---
        elif action == 'change_password':
            active_tab = 'security'
            password_form = PasswordFormClass(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) # Mantém logado
                messages.success(request, 'Sua senha foi atualizada!')
                return redirect('settings')
            else:
                messages.error(request, 'Erro na senha. Verifique os campos.')

        # --- NOTIFICAÇÕES ---
        elif action == 'update_notifications':
            active_tab = 'notifications'
            notification_form = NotificationForm(request.POST, instance=user)
            if notification_form.is_valid():
                notification_form.save()
                messages.success(request, 'Preferências salvas!')
                return redirect('settings')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'notification_form': notification_form,
        'google_connected': google_connected,
        'active_tab': active_tab,
        'has_password': user.has_usable_password()
    }
    return render(request, 'accounts/settings.html', context)


# --- 5. DELETE ACCOUNT ---
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.info(request, 'Sua conta foi excluída permanentemente.')
        return redirect('login')
    return redirect('settings')


# --- 6. DISCONNECT GOOGLE ---
@login_required
def disconnect_google_view(request):
    if request.method == 'POST':
        user = request.user
        
        if not user.has_usable_password():
            messages.error(request, 'Para desconectar o Google, defina uma senha na aba Segurança primeiro.')
            return redirect('settings')

        try:
            google_account = user.social_auth.get(provider='google-oauth2')
            google_account.delete()
            messages.success(request, 'Conta do Google desconectada.')
        except:
            messages.error(request, 'Nenhuma conta Google encontrada.')
            
    return redirect('settings')

# Em accounts/views.py (No final)

class DebugPasswordResetView(auth_views.PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        print(f"\n--- 🕵️‍♂️ DEBUG ESPIONAGEM ---")
        print(f"1. Email digitado: {email}")
        
        # Busca usuários com esse email
        users = list(form.get_users(email))
        print(f"2. Usuários encontrados no banco: {len(users)}")
        
        if users:
            user = users[0]
            print(f"3. Usuário: {user.email}")
            print(f"4. Tem senha utilizável? {user.has_usable_password()}")
            print(f"5. Está ativo? {user.is_active}")
            
            if not user.has_usable_password():
                print("🚨 PROBLEMA ENCONTRADO: Este usuário não tem senha (login social?) então o Django IGNORA o envio.")
        else:
            print("🚨 PROBLEMA: Nenhum usuário encontrado com esse email!")
            
        print("------------------------------\n")
        return super().form_valid(form)