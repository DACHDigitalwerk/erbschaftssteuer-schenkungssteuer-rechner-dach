# -*- coding: utf-8 -*-
"""
Data Models for Estate and Gift Tax Calculations (ErbStG, BAO, CH)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class RelationshipType(str, Enum):
    SPOUSE = "spouse"                    # Ehegatten, Lebenspartner (Kl. I, 500k)
    CHILD = "child"                      # Kinder, Stiefkinder (Kl. I, 400k)
    GRANDCHILD = "grandchild"            # Enkel (Kl. I, 200k)
    PARENT_INHERITANCE = "parent_erbfall" # Eltern bei Erwerb von Todes wegen (Kl. I, 100k)
    PARENT_GIFT = "parent_schenkung"     # Eltern bei Schenkung (Kl. II, 20k)
    SIBLING = "sibling"                  # Geschwister, Nichten, Neffen (Kl. II, 20k)
    OTHER = "other"                      # Dritte, Lebensgefährten (Kl. III, 20k)


class TaxClass(str, Enum):
    CLASS_I = "I"
    CLASS_II = "II"
    CLASS_III = "III"


class TransferType(str, Enum):
    INHERITANCE = "inheritance"  # Erbfall
    GIFT = "gift"                # Schenkung


class Country(str, Enum):
    DE = "DE"  # Deutschland (ErbStG)
    AT = "AT"  # Österreich (0% Steuer + § 121a BAO Meldepflicht)
    CH = "CH"  # Schweiz (Kantonale Regelungen, direkte Linie meist 0%)


@dataclass
class CalculationInput:
    """Input parameters for estate/gift tax calculation."""
    gross_amount: float
    relationship: RelationshipType = RelationshipType.CHILD
    transfer_type: TransferType = TransferType.INHERITANCE
    country: Country = Country.DE
    prior_gifts_10y: float = 0.0          # Vorerwerbe innerhalb 10 Jahren (§ 14 ErbStG)
    pension_allowance: float = 0.0        # Versorgungsfreibetrag (§ 17 ErbStG, nur Erbfall)
    family_home_exempt: bool = False      # Steuerbefreiung Familienheim (§ 13 Abs. 1 Nr. 4b/c)
    family_home_value: float = 0.0        # Wert des Familienheims (wird abgezogen bei Befreiung)
    estate_liabilities: float = 0.0       # Nachlassverbindlichkeiten / Schulden


@dataclass
class CalculationResult:
    """Detailed calculation outcome."""
    country: Country
    transfer_type: TransferType
    relationship: RelationshipType
    tax_class: TaxClass
    gross_amount: float
    estate_liabilities: float
    net_transfer: float
    family_home_deduction: float
    personal_allowance: float             # § 16 ErbStG
    pension_allowance: float              # § 17 ErbStG
    prior_gifts_10y: float
    taxable_amount: float                 # Nach Freibeträgen & Abrundung auf volle 100 €
    tax_rate_percent: float               # Steuersatz nach § 19 ErbStG
    tax_amount: float                     # Steuerfestsetzung
    prior_tax_credit: float               # Fiktive Steuer auf Vorerwerbe gem. § 14 ErbStG
    net_tax_payable: float                # Tatsächlich zu zahlende Steuer
    effective_tax_rate: float             # Effektiver Steuersatz in Prozent auf Bruttoerwerb
    net_beneficiary_receives: float       # Auszahlungsbetrag nach Steuern
    reporting_required: bool = False      # Meldepflicht (z.B. § 121a BAO AT oder § 30 ErbStG DE)
    reporting_notice: str = ""            # Gesetzliche Hinweistexte & Fristen
    disclaimer: str = ""


@dataclass
class DecadePlanStep:
    year_label: str
    amount_transferred: float
    allowance_used: float
    taxable_portion: float
    tax_paid: float
    remaining_balance: float


@dataclass
class DecadePlanResult:
    """Simulation of phased gifting over 10-20 years vs. lump sum."""
    total_wealth: float
    relationship: RelationshipType
    lump_sum_tax: float
    decade_plan_tax: float
    tax_saved: float
    savings_percent: float
    steps: List[DecadePlanStep] = field(default_factory=list)
