# -*- coding: utf-8 -*-
"""
Command-Line Interface for DACH Estate & Gift Tax Calculator (dach-erbst)
"""

import argparse
import json
import sys
from typing import Any, Dict

from .models import (
    CalculationInput,
    RelationshipType,
    TransferType,
    Country,
)
from .calculator import calculate_estate_tax, simulate_decade_gifting


def format_currency(val: float) -> str:
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="dach-erbst",
        description="DACH Erbschaftssteuer-, Schenkungssteuer- & Freibetrags-Rechner 2026 (ErbStG, BAO & CH Kantone)",
        epilog="Entwickelt von DACH Digitalwerk • https://dachdigitalwerk.github.io/erbschaftssteuer-schenkungssteuer-rechner/",
    )

    parser.add_argument(
        "amount",
        type=float,
        nargs="?",
        default=None,
        help="Brutto-Nachlasswert oder Schenkungswert in Euro",
    )
    parser.add_argument(
        "-a", "--amount-flag",
        dest="amount_alt",
        type=float,
        default=None,
        help="Alternativer Parameter fuer Vermoegenswert in Euro",
    )
    parser.add_argument(
        "-r", "--relationship",
        choices=["spouse", "child", "grandchild", "parent_erbfall", "parent_schenkung", "sibling", "other"],
        default="child",
        help="Verwandtschaftsgrad (spouse=Ehegatte, child=Kind, grandchild=Enkel, etc.)",
    )
    parser.add_argument(
        "-t", "--type",
        choices=["erbfall", "schenkung"],
        default="erbfall",
        help="Uebertragungsart (erbfall = Erbschaft, schenkung = Schenkung unter Lebenden)",
    )
    parser.add_argument(
        "-c", "--country",
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Rechtsraum: DE (Deutschland ErbStG), AT (Oesterreich 0 Prozent + BAO), CH (Schweiz Kantone)",
    )
    parser.add_argument(
        "--prior-gifts",
        type=float,
        default=0.0,
        help="Vorerwerbe innerhalb der letzten 10 Jahre nach Paragraph 14 ErbStG in Euro",
    )
    parser.add_argument(
        "--pension-allowance",
        type=float,
        default=0.0,
        help="Besonderer Versorgungsfreibetrag nach Paragraph 17 ErbStG (nur Erbfall) in Euro",
    )
    parser.add_argument(
        "--family-home",
        type=float,
        default=0.0,
        help="Wert des steuerbefreiten Familienheims nach Paragraph 13 ErbStG in Euro",
    )
    parser.add_argument(
        "--estate-liabilities",
        type=float,
        default=0.0,
        help="Nachlassverbindlichkeiten / Schulden / Bestattungskosten in Euro",
    )
    parser.add_argument(
        "--simulate-decades",
        action="store_true",
        help="Simuliert eine gestaffelte Kettenschenkung ueber 10 bis 20 Jahre im Vergleich zur Sofortuebertragung",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe als maschinenlesbares JSON-Format",
    )

    return parser.parse_args(args)


def main(args=None):
    parsed = parse_args(args)

    amt = parsed.amount if parsed.amount is not None else parsed.amount_alt
    if amt is None:
        print("Fehler: Bitte geben Sie einen Vermoegenswert an (z. B. 'dach-erbst 600000').", file=sys.stderr)
        sys.exit(1)

    rel_map = {
        "spouse": RelationshipType.SPOUSE,
        "child": RelationshipType.CHILD,
        "grandchild": RelationshipType.GRANDCHILD,
        "parent_erbfall": RelationshipType.PARENT_INHERITANCE,
        "parent_schenkung": RelationshipType.PARENT_GIFT,
        "sibling": RelationshipType.SIBLING,
        "other": RelationshipType.OTHER,
    }
    relationship = rel_map.get(parsed.relationship, RelationshipType.CHILD)

    tt_map = {
        "erbfall": TransferType.INHERITANCE,
        "schenkung": TransferType.GIFT,
    }
    transfer_type = tt_map.get(parsed.type, TransferType.INHERITANCE)

    c_map = {
        "DE": Country.DE,
        "AT": Country.AT,
        "CH": Country.CH,
    }
    country = c_map.get(parsed.country, Country.DE)

    calc_input = CalculationInput(
        gross_amount=amt,
        relationship=relationship,
        transfer_type=transfer_type,
        country=country,
        prior_gifts_10y=parsed.prior_gifts,
        pension_allowance=parsed.pension_allowance,
        family_home_exempt=(parsed.family_home > 0),
        family_home_value=parsed.family_home,
        estate_liabilities=parsed.estate_liabilities,
    )

    result = calculate_estate_tax(calc_input)

    if parsed.json:
        data: Dict[str, Any] = {
            "country": result.country.value,
            "transfer_type": result.transfer_type.value,
            "relationship": result.relationship.value,
            "tax_class": result.tax_class.value,
            "gross_amount": result.gross_amount,
            "estate_liabilities": result.estate_liabilities,
            "net_transfer": result.net_transfer,
            "family_home_deduction": result.family_home_deduction,
            "personal_allowance": result.personal_allowance,
            "pension_allowance": result.pension_allowance,
            "prior_gifts_10y": result.prior_gifts_10y,
            "taxable_amount": result.taxable_amount,
            "tax_rate_percent": result.tax_rate_percent,
            "tax_amount": result.tax_amount,
            "prior_tax_credit": result.prior_tax_credit,
            "net_tax_payable": result.net_tax_payable,
            "effective_tax_rate": result.effective_tax_rate,
            "net_beneficiary_receives": result.net_beneficiary_receives,
            "reporting_required": result.reporting_required,
            "reporting_notice": result.reporting_notice,
            "disclaimer": result.disclaimer,
        }
        if parsed.simulate_decades:
            dec = simulate_decade_gifting(amt, relationship)
            data["decade_simulation"] = {
                "lump_sum_tax": dec.lump_sum_tax,
                "decade_plan_tax": dec.decade_plan_tax,
                "tax_saved": dec.tax_saved,
                "savings_percent": dec.savings_percent,
                "steps": [
                    {
                        "label": s.year_label,
                        "transferred": s.amount_transferred,
                        "tax_paid": s.tax_paid,
                        "remaining": s.remaining_balance,
                    }
                    for s in dec.steps
                ],
            }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Text UI Output
    print("\n" + "=" * 68)
    print("  DACH ERBSCHAFTS- & SCHENKUNGSSTEUER-RECHNER 2026")
    print("  Rechtskonforme Modellberechnung (ErbStG, BAO, CH Kantone)")
    print("=" * 68)

    print(f" Land:                      {result.country.value}")
    print(f" Vorgangsart:               {result.transfer_type.value.capitalize()}")
    print(f" Verwandtschaft:            {result.relationship.value} (Steuerklasse {result.tax_class.value})")
    print(f" Bruttoerwerb:              {format_currency(result.gross_amount)}")
    if result.estate_liabilities > 0:
        print(f" Nachlassverbindlichkeiten: -{format_currency(result.estate_liabilities)}")
        print(f" Netto-Erwerb:              {format_currency(result.net_transfer)}")

    if result.family_home_deduction > 0:
        print(f" Familienheim (§ 13 ErbStG):-{format_currency(result.family_home_deduction)}")
    print(f" Persoenlicher Freibetrag:  -{format_currency(result.personal_allowance)}")
    if result.pension_allowance > 0:
        print(f" Versorgungsfreibetrag:     -{format_currency(result.pension_allowance)}")
    if result.prior_gifts_10y > 0:
        print(f" Vorerwerbe (10 Jahre § 14): {format_currency(result.prior_gifts_10y)}")

    print("-" * 68)
    print(f" Steuerpflichtiger Erwerb:  {format_currency(result.taxable_amount)}")
    print(f" Steuersatz (§ 19 ErbStG):  {result.tax_rate_percent:.1f} %")
    if result.prior_tax_credit > 0:
        print(f" Fiktive Steuer Vorerwerbe: -{format_currency(result.prior_tax_credit)}")
    print(f" ZU ZAHLENDE STEUER:        {format_currency(result.net_tax_payable)}")
    print(f" Effektive Steuerbelastung: {result.effective_tax_rate:.2f} %")
    print(f" Netto nach Steuern:        {format_currency(result.net_beneficiary_receives)}")
    print("=" * 68)

    if result.reporting_notice:
        print(f"\n[Meldepflicht]: {result.reporting_notice}")

    if parsed.simulate_decades:
        dec = simulate_decade_gifting(amt, relationship)
        print("\n" + "-" * 68)
        print("  10-JAHRES-KETTENSCHENKUNGS-SIMULATOR (§ 14 ErbStG)")
        print("-" * 68)
        print(f" Einmalübertragung (Sofort): Steuer {format_currency(dec.lump_sum_tax)}")
        print(f" Gestaffelt über 10-20 J.:   Steuer {format_currency(dec.decade_plan_tax)}")
        print(f" STEUERERSPARNIS:            {format_currency(dec.tax_saved)} ({dec.savings_percent:.1f} % gespart!)")
        for s in dec.steps:
            print(f"  • {s.year_label:26} Tranche: {format_currency(s.amount_transferred):14} Steuer: {format_currency(s.tax_paid)}")
        print("-" * 68)

    print("\n" + result.disclaimer + "\n")


if __name__ == "__main__":
    main()
