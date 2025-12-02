#!/usr/bin/env python
"""
Script para criação automática de tabelas no PostgreSQL do Railway.
Execute este script após configurar o DATABASE_URL no Railway.

Uso:
    python setup_database.py
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n{'='*60}")
    print(f">>> {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        print(f"ERRO: {result.stderr}")
        return False
    
    print(f"✓ {description} - Concluído!")
    return True


def main():
    print("\n" + "="*60)
    print("   SETUP DO BANCO DE DADOS - RAILWAY")
    print("="*60)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("\n⚠️  AVISO: DATABASE_URL não encontrada!")
        print("   No Railway, esta variável é configurada automaticamente")
        print("   quando você adiciona um banco PostgreSQL ao projeto.")
        print("\n   Para desenvolvimento local, configure a variável no arquivo .env")
        print("-"*60)
    else:
        print(f"\n✓ DATABASE_URL encontrada!")
        if 'railway' in database_url:
            print("  → Conectando ao banco Railway...")
        elif 'localhost' in database_url or '127.0.0.1' in database_url:
            print("  → Conectando ao banco local...")
        else:
            print("  → Conectando ao banco remoto...")
    
    print("\n")
    
    steps = [
        ("python manage.py migrate --run-syncdb", "Aplicando migrações do banco de dados"),
        ("python manage.py createcachetable", "Criando tabela de cache"),
        ("python manage.py collectstatic --noinput", "Coletando arquivos estáticos"),
    ]
    
    success_count = 0
    for command, description in steps:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n❌ Falha em: {description}")
            print("   Verifique se DATABASE_URL está configurada corretamente.")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("   SETUP CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print(f"\n✓ {success_count}/{len(steps)} etapas completadas")
    print("\nTabelas criadas:")
    print("  - accounts_customuser (usuários)")
    print("  - analytics_profile (perfis)")
    print("  - subscriptions_plan (planos)")
    print("  - subscriptions_subscription (assinaturas)")
    print("  - subscriptions_payment (pagamentos)")
    print("  - social_auth_* (autenticação Google)")
    print("  - django_cache (cache)")
    print("  - django_session (sessões)")
    print("  - auth_* (permissões)")
    print("\n" + "="*60)
    print("   PRÓXIMOS PASSOS:")
    print("="*60)
    print("\n1. Para criar um superusuário (admin):")
    print("   python manage.py createsuperuser")
    print("\n2. Para criar planos de assinatura iniciais:")
    print("   python manage.py shell")
    print("   >>> from subscriptions.models import Plan")
    print("   >>> Plan.objects.create(name='Free', price=0, ...)")
    print("\n3. Para rodar o servidor:")
    print("   gunicorn config.wsgi --bind 0.0.0.0:$PORT")
    print("\n")


if __name__ == "__main__":
    main()
