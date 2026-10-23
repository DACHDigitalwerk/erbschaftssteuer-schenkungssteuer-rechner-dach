# -*- coding: utf-8 -*-
"""
Statutory Tax Tables & Allowances for Estate & Gift Tax (ErbStG, BAO, CH)
"""

from typing import Dict, Tuple, List
from .models import RelationshipType, TaxClass, TransferType


# § 16 ErbStG Freibeträge (in Euro)
PERSONAL_ALLOWANCES: Dict[RelationshipType, float] = {
    RelationshipType.SPOUSE: 500000.0,
    RelationshipType.CHILD: 400000.0,
    RelationshipType.GRANDCHILD: 200000.0,
    RelationshipType.PARENT_INHERITANCE: 100000.0,
    RelationshipType.PARENT_GIFT: 20000.0,
    RelationshipType.SIBLING: 20000.0,
    RelationshipType.OTHER: 20000.0,
}

# Zuordnung Verwandtschaft zu Steuerklasse (§ 15 ErbStG)
RELATIONSHIP_TAX_CLASS: Dict[RelationshipType, TaxClass] = {
    RelationshipType.SPOUSE: TaxClass.CLASS_I,
    RelationshipType.CHILD: TaxClass.CLASS_I,
    RelationshipType.GRANDCHILD: TaxClass.CLASS_I,
    RelationshipType.PARENT_INHERITANCE: TaxClass.CLASS_I,
    RelationshipType.PARENT_GIFT: TaxClass.CLASS_II,
    RelationshipType.SIBLING: TaxClass.CLASS_II,
    RelationshipType.OTHER: TaxClass.CLASS_III,
}

# § 17 ErbStG Maximaler Versorgungsfreibetrag für Ehegatten (in Euro)
MAX_SPOUSE_PENSION_ALLOWANCE: float = 256000.0

# § 17 Abs. 2 ErbStG Versorgungsfreibeträge für Kinder nach Alter
CHILD_PENSION_ALLOWANCE_BY_AGE: List[Tuple[int, float]] = [
    (5, 52000.0),    # bis vollendetes 5. Lebensjahr
    (10, 41000.0),   # 6 bis 10 Jahre
    (15, 30700.0),   # 11 bis 15 Jahre
    (20, 20500.0),   # 16 bis 20 Jahre
    (27, 10300.0),   # 21 bis 27 Jahre
]

# § 19 ErbStG Steuersatztabelle
# Format: (Obergrenze steuerpflichtiger Erwerb in Euro, Satz Klasse I %, Satz Klasse II %, Satz Klasse III %)
# Beträge über 26.000.000 fallen in die letzte Stufe (float("inf"))
ERBSTG_TAX_BRACKETS: List[Tuple[float, float, float, float]] = [
    (75000.0, 7.0, 15.0, 30.0),
    (300000.0, 11.0, 20.0, 30.0),
    (600000.0, 15.0, 25.0, 30.0),
    (6000000.0, 19.0, 30.0, 30.0),
    (13000000.0, 23.0, 35.0, 50.0),
    (26000000.0, 27.0, 40.0, 50.0),
    (float("inf"), 30.0, 43.0, 50.0),
]

# Österreich BAO § 121a Schwellenwerte für Schenkungsmeldung (in Euro)
AT_BAO_RELATIVES_THRESHOLD: float = 50000.0    # Angehörige innerhalb 1 Jahres
AT_BAO_OTHERS_THRESHOLD: float = 15000.0       # Dritte innerhalb 5 Jahren

# Schweizer Durchschnittssteuersätze nach Verwandtschaft (zur Modellierung)
CH_TAX_RATES: Dict[RelationshipType, float] = {
    RelationshipType.SPOUSE: 0.0,              # In allen 26 Kantonen 0 %
    RelationshipType.CHILD: 0.0,               # In 24 von 26 Kantonen 0 %
    RelationshipType.GRANDCHILD: 0.0,          # In den meisten Kantonen 0 %
    RelationshipType.PARENT_INHERITANCE: 5.0,  # Je nach Kanton 0-10 %
    RelationshipType.PARENT_GIFT: 7.0,         # Je nach Kanton 0-15 %
    RelationshipType.SIBLING: 12.0,            # Je nach Kanton 6-25 %
    RelationshipType.OTHER: 25.0,              # Je nach Kanton 20-49,5 %
}
