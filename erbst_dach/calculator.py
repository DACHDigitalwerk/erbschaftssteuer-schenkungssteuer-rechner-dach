# -*- coding: utf-8 -*-
"""
Core Calculation Logic for Estate & Gift Tax (ErbStG, BAO, CH)
"""

import math
from typing import List
from .models import (
    CalculationInput,
    CalculationResult,
    DecadePlanResult,
    DecadePlanStep,
    RelationshipType,
    TaxClass,
    TransferType,
    Country,
)
from .tables import (
    PERSONAL_ALLOWANCES,
    RELATIONSHIP_TAX_CLASS,
    ERBSTG_TAX_BRACKETS,
    AT_BAO_RELATIVES_THRESHOLD,
    AT_BAO_OTHERS_THRESHOLD,
    CH_TAX_RATES,
)
from .validator import validate_input


def get_allowance(relationship: RelationshipType, country: Country = Country.DE) -> float:
    """Returns personal tax-free allowance in Euro according to § 16 ErbStG."""
    if country == Country.AT:
        return 0.0  # In Österreich gibt es keine Erbschaftssteuer, daher keine ErbStG-Freibeträge
    return PERSONAL_ALLOWANCES.get(relationship, 20000.0)


def get_tax_class(relationship: RelationshipType) -> TaxClass:
    """Determines Steuerklasse I, II, or III according to § 15 ErbStG."""
    return RELATIONSHIP_TAX_CLASS.get(relationship, TaxClass.CLASS_III)


def get_tax_rate(taxable_amount: float, tax_class: TaxClass) -> float:
    """
    Returns statutory tax rate percentage according to § 19 ErbStG table.
    """
    if taxable_amount <= 0:
        return 0.0

    idx = 1 if tax_class == TaxClass.CLASS_I else (2 if tax_class == TaxClass.CLASS_II else 3)
    for ceiling, r1, r2, r3 in ERBSTG_TAX_BRACKETS:
        if taxable_amount <= ceiling:
            rates = (r1, r2, r3)
            return rates[idx - 1]

    # Fallback to last bracket
    last = ERBSTG_TAX_BRACKETS[-1]
    return last[idx]


def round_down_100(amount: float) -> float:
    """
    Rounds down taxable estate to full 100 Euro according to § 10 Abs. 1 Satz 6 ErbStG.
    """
    if amount <= 0:
        return 0.0
    return math.floor(amount / 100.0) * 100.0


def calculate_estate_tax(params: CalculationInput) -> CalculationResult:
    """
    Main calculation engine. Computes estate or gift tax for Germany, Austria, or Switzerland.
    """
    warnings = validate_input(params)

    # Nachlassverbindlichkeiten abziehen
    net_transfer = max(0.0, params.gross_amount - params.estate_liabilities)

    # Steuerbefreiung Familienheim § 13 Abs. 1 Nr. 4b/c
    family_home_deduction = 0.0
    if params.family_home_exempt and params.relationship in (
        RelationshipType.SPOUSE,
        RelationshipType.CHILD,
        RelationshipType.GRANDCHILD,
    ):
        family_home_deduction = min(params.family_home_value, net_transfer)

    # Verbleibender Erwerb vor Freibeträgen
    subtotal_after_home = max(0.0, net_transfer - family_home_deduction)

    # Freibeträge ermitteln
    personal_allowance = get_allowance(params.relationship, params.country)
    tax_class = get_tax_class(params.relationship)

    # Versorgungsfreibetrag § 17 (nur Erbfall)
    pension_allowance = 0.0
    if params.transfer_type == TransferType.INHERITANCE:
        pension_allowance = params.pension_allowance

    disclaimer = (
        "Rechtlicher Hinweis: Rein technisches Berechnungstool gem. § 2 RDG / § 5 StBerG. "
        "Keine Steuerberatung. Gemäß BGH-Urteil (Az. I ZR 226/20 - Smartlaw) ist die rein algorithmenbasierte "
        "Generierung rechtlicher und steuerlicher Berechnungen zulässig. Verbindliche Auskünfte erteilt das Finanzamt oder ein Steuerberater."
    )

    # 1. ÖSTERREICH (AT)
    if params.country == Country.AT:
        is_relative = params.relationship in (
            RelationshipType.SPOUSE,
            RelationshipType.CHILD,
            RelationshipType.GRANDCHILD,
            RelationshipType.PARENT_INHERITANCE,
            RelationshipType.PARENT_GIFT,
            RelationshipType.SIBLING,
        )
        threshold = AT_BAO_RELATIVES_THRESHOLD if is_relative else AT_BAO_OTHERS_THRESHOLD
        reporting_required = (params.transfer_type == TransferType.GIFT and net_transfer > threshold)
        
        notice = "Österreich erhebt 0 % Erbschafts- und Schenkungssteuer (seit 01.08.2008 aufgehoben)."
        if reporting_required:
            notice += f" ACHTUNG: Schenkung übersteigt {threshold:,.0f} €. Elektronische Schenkungsmeldung binnen 3 Monaten via FinanzOnline gem. § 121a BAO zwingend erforderlich (Strafrahmen bis 10 % gem. § 49a FinStrG)."
        elif params.transfer_type == TransferType.GIFT:
            notice += f" Betrag liegt unter der Schenkungsmeldegrenze von {threshold:,.0f} €."

        return CalculationResult(
            country=Country.AT,
            transfer_type=params.transfer_type,
            relationship=params.relationship,
            tax_class=tax_class,
            gross_amount=params.gross_amount,
            estate_liabilities=params.estate_liabilities,
            net_transfer=net_transfer,
            family_home_deduction=family_home_deduction,
            personal_allowance=0.0,
            pension_allowance=0.0,
            prior_gifts_10y=params.prior_gifts_10y,
            taxable_amount=0.0,
            tax_rate_percent=0.0,
            tax_amount=0.0,
            prior_tax_credit=0.0,
            net_tax_payable=0.0,
            effective_tax_rate=0.0,
            net_beneficiary_receives=net_transfer,
            reporting_required=reporting_required,
            reporting_notice=notice,
            disclaimer=disclaimer,
        )

    # 2. SCHWEIZ (CH)
    if params.country == Country.CH:
        ch_rate = CH_TAX_RATES.get(params.relationship, 0.0)
        allowance_ch = 10000.0 if ch_rate > 0 else 0.0
        taxable_ch = max(0.0, net_transfer - allowance_ch)
        tax_ch = round(taxable_ch * (ch_rate / 100.0), 2)
        eff_rate = (tax_ch / params.gross_amount * 100.0) if params.gross_amount > 0 else 0.0

        notice = f"Schweiz: Kantonale Besteuerung (Richtwert ca. {ch_rate:.1f} %). Ehegatten und direkte Nachkommen in den meisten Kantonen steuerbefreit. Deklaration im Rahmen der regulären Steuererklärung."

        return CalculationResult(
            country=Country.CH,
            transfer_type=params.transfer_type,
            relationship=params.relationship,
            tax_class=tax_class,
            gross_amount=params.gross_amount,
            estate_liabilities=params.estate_liabilities,
            net_transfer=net_transfer,
            family_home_deduction=family_home_deduction,
            personal_allowance=allowance_ch,
            pension_allowance=0.0,
            prior_gifts_10y=params.prior_gifts_10y,
            taxable_amount=taxable_ch,
            tax_rate_percent=ch_rate,
            tax_amount=tax_ch,
            prior_tax_credit=0.0,
            net_tax_payable=tax_ch,
            effective_tax_rate=round(eff_rate, 2),
            net_beneficiary_receives=round(net_transfer - tax_ch, 2),
            reporting_required=True,
            reporting_notice=notice,
            disclaimer=disclaimer,
        )

    # 3. DEUTSCHLAND (DE - ErbStG)
    total_deductions = family_home_deduction + personal_allowance + pension_allowance

    if params.prior_gifts_10y > 0:
        # § 14 ErbStG Zusammenrechnung
        combined_wealth = net_transfer + params.prior_gifts_10y
        taxable_combined_raw = max(0.0, combined_wealth - total_deductions)
        taxable_combined = round_down_100(taxable_combined_raw)
        rate_combined = get_tax_rate(taxable_combined, tax_class)
        tax_combined = round(taxable_combined * (rate_combined / 100.0), 2)

        # Fiktive Steuer auf Vorerwerbe
        taxable_prior_raw = max(0.0, params.prior_gifts_10y - personal_allowance)
        taxable_prior = round_down_100(taxable_prior_raw)
        rate_prior = get_tax_rate(taxable_prior, tax_class)
        tax_prior = round(taxable_prior * (rate_prior / 100.0), 2)

        tax_payable = round(max(0.0, tax_combined - tax_prior), 2)
        taxable_amount = taxable_combined
        tax_rate_percent = rate_combined
        tax_amount = tax_combined
        prior_tax_credit = tax_prior
    else:
        taxable_raw = max(0.0, subtotal_after_home - personal_allowance - pension_allowance)
        taxable_amount = round_down_100(taxable_raw)
        tax_rate_percent = get_tax_rate(taxable_amount, tax_class) if taxable_amount > 0 else 0.0
        tax_amount = round(taxable_amount * (tax_rate_percent / 100.0), 2)
        prior_tax_credit = 0.0
        tax_payable = tax_amount

    effective_rate = (tax_payable / params.gross_amount * 100.0) if params.gross_amount > 0 else 0.0
    net_receives = round(max(0.0, net_transfer - tax_payable), 2)

    notice_de = "Meldepflicht nach § 30 ErbStG: Jeder der Erbschaftsteuer unterliegende Erwerb ist dem zuständigen Finanzamt innerhalb von 3 Monaten nach Kenntnis schriftlich anzuzeigen."

    return CalculationResult(
        country=Country.DE,
        transfer_type=params.transfer_type,
        relationship=params.relationship,
        tax_class=tax_class,
        gross_amount=params.gross_amount,
        estate_liabilities=params.estate_liabilities,
        net_transfer=net_transfer,
        family_home_deduction=family_home_deduction,
        personal_allowance=personal_allowance,
        pension_allowance=pension_allowance,
        prior_gifts_10y=params.prior_gifts_10y,
        taxable_amount=taxable_amount,
        tax_rate_percent=tax_rate_percent,
        tax_amount=tax_amount,
        prior_tax_credit=prior_tax_credit,
        net_tax_payable=tax_payable,
        effective_tax_rate=round(effective_rate, 2),
        net_beneficiary_receives=net_receives,
        reporting_required=True,
        reporting_notice=notice_de,
        disclaimer=disclaimer,
    )


def simulate_decade_gifting(total_wealth: float, relationship: RelationshipType) -> DecadePlanResult:
    """
    Simulates phased gifting exploiting the 10-year renewal period (§ 14 ErbStG)
    compared to a single lump-sum transfer.
    """
    allowance = get_allowance(relationship, Country.DE)
    tax_class = get_tax_class(relationship)

    # 1. Einmalübertragung
    lump_input = CalculationInput(
        gross_amount=total_wealth,
        relationship=relationship,
        transfer_type=TransferType.GIFT,
        country=Country.DE,
    )
    lump_res = calculate_estate_tax(lump_input)
    lump_tax = lump_res.net_tax_payable

    # 2. Gestaffelte Übertragung in 3 Tranchen (Heute, nach 10 Jahren, nach 20 Jahren)
    steps: List[DecadePlanStep] = []
    rem_balance = total_wealth
    total_decade_tax = 0.0

    labels = ["Heute (Tranche 1)", "Nach 10 Jahren (Tranche 2)", "Nach 20 Jahren (Tranche 3)"]

    for label in labels:
        if rem_balance <= 0:
            break
        transfer = min(rem_balance, allowance)
        # Wenn noch mehr übrig als 3 Tranchen Freibetrag, verteile Rest gleichmäßig
        if label == labels[-1] and rem_balance > allowance:
            transfer = rem_balance

        taxable = max(0.0, transfer - allowance)
        rate = get_tax_rate(taxable, tax_class)
        tax = taxable * (rate / 100.0)

        rem_balance = max(0.0, rem_balance - transfer)
        total_decade_tax += tax

        steps.append(
            DecadePlanStep(
                year_label=label,
                amount_transferred=transfer,
                allowance_used=min(transfer, allowance),
                taxable_portion=taxable,
                tax_paid=tax,
                remaining_balance=rem_balance,
            )
        )

    saved = max(0.0, lump_tax - total_decade_tax)
    saved_pct = (saved / lump_tax * 100.0) if lump_tax > 0 else 0.0

    return DecadePlanResult(
        total_wealth=total_wealth,
        relationship=relationship,
        lump_sum_tax=lump_tax,
        decade_plan_tax=total_decade_tax,
        tax_saved=saved,
        savings_percent=round(saved_pct, 2),
        steps=steps,
    )
