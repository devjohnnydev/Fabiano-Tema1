#!/usr/bin/env python
"""
Script para popular o banco de dados com dados iniciais.
Execute após setup_database.py

Uso:
    python seed_data.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from subscriptions.models import Plan


def create_plans():
    """Cria os planos de assinatura padrão."""
    
    plans_data = [
        {
            'name': 'Gratuito',
            'price_monthly': 0.00,
            'price_annual': 0.00,
            'icon_name': 'star_outline',
        },
        {
            'name': 'Starter',
            'price_monthly': 29.90,
            'price_annual': 299.00,
            'icon_name': 'rocket_launch',
        },
        {
            'name': 'Pro',
            'price_monthly': 79.90,
            'price_annual': 799.00,
            'icon_name': 'workspace_premium',
        },
        {
            'name': 'Enterprise',
            'price_monthly': 199.90,
            'price_annual': 1999.00,
            'icon_name': 'corporate_fare',
        },
    ]
    
    print("\n" + "="*60)
    print("   CRIANDO PLANOS DE ASSINATURA")
    print("="*60 + "\n")
    
    created_count = 0
    updated_count = 0
    
    for plan_data in plans_data:
        plan, created = Plan.objects.update_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        
        if created:
            print(f"  ✓ Plano '{plan.name}' criado - R$ {plan.price_monthly}/mês")
            created_count += 1
        else:
            print(f"  ↻ Plano '{plan.name}' atualizado - R$ {plan.price_monthly}/mês")
            updated_count += 1
    
    print(f"\n  Total: {created_count} criados, {updated_count} atualizados")
    return True


def main():
    print("\n" + "="*60)
    print("   SEED DE DADOS INICIAIS")
    print("="*60)
    
    try:
        create_plans()
        
        print("\n" + "="*60)
        print("   SEED CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\nDados criados:")
        print("  - 4 planos de assinatura (Gratuito, Starter, Pro, Enterprise)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular dados: {e}")
        print("   Certifique-se de que as migrações foram aplicadas.")
        print("   Execute: python setup_database.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
