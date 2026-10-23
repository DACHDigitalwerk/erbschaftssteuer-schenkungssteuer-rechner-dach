# -*- coding: utf-8 -*-
"""
Input validation and legal compliance checks for Estate & Gift Tax
"""

from typing import List, Tuple
from .models import CalculationInput, RelationshipType, TransferType, Country


class ValidationError(ValueError):
    """Raised when input parameters fail legal or computational constraints."""
    pass


def validate_input(params: CalculationInput) -> List[str]:
    """
    Validates CalculationInput fields and returns a list of informative warnings/notices.
    Raises ValidationError if constraints are violated.
    """
    warnings: List[str] = []

    if params.gross_amount < 0:
        raise ValidationError(f"Bruttoerwerb muss >= 0 sein, erhalten: {params.gross_amount}")

    if params.prior_gifts_10y < 0:
        raise ValidationError(f"Vorerwerbe müssen >= 0 sein, erhalten: {params.prior_gifts_10y}")

    if params.pension_allowance < 0:
        raise ValidationError(f"Versorgungsfreibetrag muss >= 0 sein, erhalten: {params.pension_allowance}")

    if params.estate_liabilities < 0:
        raise ValidationError(f"Nachlassverbindlichkeiten müssen >= 0 sein, erhalten: {params.estate_liabilities}")

    if params.family_home_value < 0:
        raise ValidationError(f"Familienheim-Wert muss >= 0 sein, erhalten: {params.family_home_value}")

    # Logik-Regeln:
    # Versorgungsfreibetrag § 17 nur bei Erbfall
    if params.transfer_type == TransferType.GIFT and params.pension_allowance > 0:
        warnings.append(
            "Hinweis: Der besondere Versorgungsfreibetrag nach § 17 ErbStG gilt nur bei Erwerb von Todes wegen (Erbfall) und wird bei Schenkungen ignoriert."
        )

    # Familienheim-Befreiung § 13 Abs. 1 Nr. 4b/c nur für Ehegatten / Kinder
    if params.family_home_exempt:
        if params.relationship not in (RelationshipType.SPOUSE, RelationshipType.CHILD, RelationshipType.GRANDCHILD):
            warnings.append(
                "Achtung: Die Familienheim-Steuerbefreiung nach § 13 Abs. 1 Nr. 4b/c ErbStG steht nur Ehegatten, Lebenspartnern, Kindern und Enkeln zu."
            )

    # Vorerwerbe § 14 ErbStG Hinweis
    if params.prior_gifts_10y > 0 and params.country == Country.DE:
        warnings.append(
            "Hinweis: Gemäß § 14 ErbStG werden Vorerwerbe innerhalb von 10 Jahren dem aktuellen Erwerb hinzugerechnet (Zusammenrechnung)."
        )

    # Österreich BAO § 121a Meldepflicht-Check
    if params.country == Country.AT and params.transfer_type == TransferType.GIFT:
        is_relative = params.relationship in (
            RelationshipType.SPOUSE,
            RelationshipType.CHILD,
            RelationshipType.GRANDCHILD,
            RelationshipType.PARENT_INHERITANCE,
            RelationshipType.PARENT_GIFT,
            RelationshipType.SIBLING,
        )
        threshold = 50000.0 if is_relative else 15000.0
        if params.gross_amount > threshold:
            warnings.append(
                f"Achtung Österreich: Schenkung übersteigt den Freibetrag von {threshold:,.0f} € gem. § 121a BAO. Eine elektronische Schenkungsmeldung via FinanzOnline ist binnen 3 Monaten zwingend erforderlich (Strafrahmen bis 10 Prozent gem. § 49a FinStrG)."
            )

    return warnings
