# -*- coding: utf-8 -*-
"""
Quickstart Example for erbst_dach
"""

from erbst_dach import (
    CalculationInput,
    RelationshipType,
    TransferType,
    Country,
    calculate_estate_tax,
    simulate_decade_gifting,
)


def main():
    print("=== Beispiel 1: Erbschaft an ein Kind (600.000 €) ===")
    inp1 = CalculationInput(
        gross_amount=600000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
        country=Country.DE,
    )
    res1 = calculate_estate_tax(inp1)
    print(f"Bruttoerwerb:           {res1.gross_amount:,.2f} €")
    print(f"Persönlicher Freibetrag: -{res1.personal_allowance:,.2f} €")
    print(f"Steuerpflichtig:        {res1.taxable_amount:,.2f} €")
    print(f"Steuersatz:             {res1.tax_rate_percent:.1f} %")
    print(f"Zu zahlende Steuer:     {res1.net_tax_payable:,.2f} €")
    print(f"Netto-Auszahlung:       {res1.net_beneficiary_receives:,.2f} €\n")

    print("=== Beispiel 2: Kettenschenkung & Dekadenplanung (1.200.000 €) ===")
    plan = simulate_decade_gifting(1200000.0, RelationshipType.CHILD)
    print(f"Einmalige Übertragung heute:  Steuer = {plan.lump_sum_tax:,.2f} €")
    print(f"Gestaffelt über 20 Jahre:     Steuer = {plan.decade_plan_tax:,.2f} €")
    print(f"Steuerersparnis:              {plan.tax_saved:,.2f} € ({plan.savings_percent:.1f} %)")
    for step in plan.steps:
        print(f"  • {step.year_label:26} Tranche: {step.amount_transferred:,.2f} € -> Steuer: {step.tax_paid:,.2f} €")


if __name__ == "__main__":
    main()
