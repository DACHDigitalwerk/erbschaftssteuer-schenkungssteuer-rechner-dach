# -*- coding: utf-8 -*-
"""
DACH Erbschaftssteuer- & Schenkungssteuer-Rechner 2026 (ErbStG, BAO & CH Kantone)
================================================================================

Open-Source Python Core Engine für die rechtssichere Modellberechnung von
Erbschaften, Schenkungen, persönlichen Freibeträgen (§ 16 ErbStG),
Versorgungsfreibeträgen (§ 17 ErbStG), Zehnjahresfristen (§ 14 ErbStG),
Kettenschenkungen sowie DACH-Länderspezifika (Österreich § 121a BAO, Schweiz Kantone).

Entwickelt von DACH Digitalwerk (https://dachdigitalwerk.github.io).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__license__ = "MIT"

from .models import (
    RelationshipType,
    TaxClass,
    TransferType,
    Country,
    CalculationInput,
    CalculationResult,
    DecadePlanResult,
)
from .calculator import (
    calculate_estate_tax,
    simulate_decade_gifting,
    get_allowance,
    get_tax_rate,
)
from .validator import validate_input

__all__ = [
    "RelationshipType",
    "TaxClass",
    "TransferType",
    "Country",
    "CalculationInput",
    "CalculationResult",
    "DecadePlanResult",
    "calculate_estate_tax",
    "simulate_decade_gifting",
    "get_allowance",
    "get_tax_rate",
    "validate_input",
]
