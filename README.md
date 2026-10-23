# DACH Erbschaftssteuer-, Schenkungssteuer- & Freibetrags-Rechner 2026 (ErbStG, BAO & CH Kantone)

[![CI Tests](https://github.com/DACHDigitalwerk/erbschaftssteuer-schenkungssteuer-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/erbschaftssteuer-schenkungssteuer-rechner-dach/actions)
[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/erbst-dach/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DACH Region](https://img.shields.io/badge/DACH-DE%20%E2%80%A2%20AT%20%E2%80%A2%20CH-emerald.svg)](https://dachdigitalwerk.github.io/)

**Produktionsreife Open-Source Python Engine & CLI** zur finanzmathematischen und rechtskonformen Modellberechnung von **Erbschaften, Schenkungen, persönlichen Freibeträgen (§ 16 ErbStG), Versorgungsfreibeträgen (§ 17 ErbStG), 10-Jahres-Vorerwerben (§ 14 ErbStG), Kettenschenkungen** sowie **DACH-Länderspezifika (Österreich § 121a BAO Schenkungsmeldegesetz & Schweizer Kantonaltarife)**.

> 🌐 **Interaktive Web-Applikation & DIN-A4 PDF-Export:**  
> Nutzen Sie das kostenlose Browser-Tool ohne Installation oder Registrierung unter:  
> **👉 [https://dachdigitalwerk.github.io/erbschaftssteuer-schenkungssteuer-rechner/](https://dachdigitalwerk.github.io/erbschaftssteuer-schenkungssteuer-rechner/)**

---

## 📚 Fach-Ratgeber & Hintergrundwissen

* 📖 [Erbschaftssteuer berechnen Formel & Freibeträge 2026](https://dachdigitalwerk.github.io/erbschaftssteuer-berechnen-formel-freibetraege-2026.html)
* 📖 [Schenkungssteuer 10-Jahres-Frist & Kettenschenkung legal nutzen](https://dachdigitalwerk.github.io/schenkungssteuer-10-jahres-frist-kettenschenkung.html)
* 📖 [Erbschaftssteuer Österreich & Schweiz im DACH-Vergleich: § 121a BAO & Kantonstarife](https://dachdigitalwerk.github.io/erbschaftssteuer-oesterreich-schweiz-vergleich-schenkungsmeldung.html)

---

## 🚀 Features & Rechtskonformität

* ✅ **Gesetzliche Freibeträge (§ 16 ErbStG):**
  * Ehegatten & eingetragene Lebenspartner: **500.000 €**
  * Kinder & Stiefkinder: **400.000 €** (je Elternteil!)
  * Enkelkinder: **200.000 €**
  * Eltern im Erbfall: **100.000 €** (Steuerklasse I) / bei Schenkung **20.000 €** (Steuerklasse II)
  * Geschwister, Nichten, Neffen: **20.000 €** (Steuerklasse II)
  * Nicht-Verwandte / Dritte: **20.000 €** (Steuerklasse III)
* ✅ **Besonderer Versorgungsfreibetrag (§ 17 ErbStG):** Bis zu **256.000 €** für Ehegatten sowie bis zu **52.000 €** für Kinder im Erbfall.
* ✅ **Familienheim-Befreiung (§ 13 Abs. 1 Nr. 4b/c ErbStG):** Vollständige Steuerfreistellung der selbstgenutzten Wohnimmobilie.
* ✅ **Zusammenrechnung früherer Erwerbe (§ 14 ErbStG):** Fiktive Gesamterwerbsberechnung und Verrechnung der Vorerwerbssteuer bei Schenkungen innerhalb von 10 Jahren.
* ✅ **10-Jahres-Kettenschenkungs-Simulator:** Berechnet die konkrete Steuerersparnis bei gestaffelter Vermögensübertragung über Dekaden hinweg.
* ✅ **DACH-Spezifika:**
  * **Österreich (AT):** 0 % Steuer, automatische Prüfung der **Schenkungsmeldepflicht gem. § 121a BAO** (50.000 € Angehörige, 15.000 € Dritte) und Warnung vor dem Strafrahmen gem. § 49a FinStrG.
  * **Schweiz (CH):** Föderales Kantonsmodell (Ehegatten und direkte Nachkommen in den meisten Kantonen 0 %).
* ✅ **BGH Smartlaw-Konformität:** Rein deterministische Algorithmen ohne unzulässige Rechtsberatung gem. § 2 RDG / § 5 StBerG.

---

## 📦 Installation

```bash
pip install erbst-dach
```

Oder direkt aus dem Repository:

```bash
git clone https://github.com/DACHDigitalwerk/erbschaftssteuer-schenkungssteuer-rechner-dach.git
cd erbschaftssteuer-schenkungssteuer-rechner-dach
pip install -e .
```

---

## 💻 CLI-Nutzung (`dach-erbst`)

Die CLI bietet intuitive Parameter für alle Erbfall- und Schenkungskonstellationen:

### 1. Einfache Erbschaft an ein Kind (600.000 €)

```bash
dach-erbst 600000 -r child
```

**Ausgabe:**
```text
====================================================================
  DACH ERBSCHAFTS- & SCHENKUNGSSTEUER-RECHNER 2026
  Rechtskonforme Modellberechnung (ErbStG, BAO, CH Kantone)
====================================================================
 Land:                      DE
 Vorgangsart:               Erbfall
 Verwandtschaft:            child (Steuerklasse I)
 Bruttoerwerb:              600.000,00 €
 Persoenlicher Freibetrag:  -400.000,00 €
--------------------------------------------------------------------
 Steuerpflichtiger Erwerb:  200.000,00 €
 Steuersatz (§ 19 ErbStG):  11.0 %
 ZU ZAHLENDE STEUER:        22.000,00 €
 Effektive Steuerbelastung: 3.67 %
 Netto nach Steuern:        578.000,00 €
====================================================================
```

### 2. 10-Jahres-Kettenschenkungs-Simulation (1.200.000 €)

```bash
dach-erbst 1200000 -r child --simulate-decades
```

**Ergebnis:**
```text
--------------------------------------------------------------------
  10-JAHRES-KETTENSCHENKUNGS-SIMULATOR (§ 14 ErbStG)
--------------------------------------------------------------------
 Einmalübertragung (Sofort): Steuer 152.000,00 €
 Gestaffelt über 10-20 J.:   Steuer 0,00 €
 STEUERERSPARNIS:            152.000,00 € (100.0 % gespart!)
  • Heute (Tranche 1)          Tranche: 400.000,00 €   Steuer: 0,00 €
  • Nach 10 Jahren (Tranche 2) Tranche: 400.000,00 €   Steuer: 0,00 €
  • Nach 20 Jahren (Tranche 3) Tranche: 400.000,00 €   Steuer: 0,00 €
--------------------------------------------------------------------
```

### 3. Österreichische Schenkungsmeldung (§ 121a BAO)

```bash
dach-erbst 80000 -c AT -t schenkung -r child --json
```

---

## 🐍 Python API

```python
from erbst_dach import (
    CalculationInput,
    RelationshipType,
    TransferType,
    Country,
    calculate_estate_tax,
    simulate_decade_gifting,
)

# 1. Erbschaftssteuer berechnen
params = CalculationInput(
    gross_amount=800000.0,
    relationship=RelationshipType.SPOUSE,
    transfer_type=TransferType.INHERITANCE,
    pension_allowance=256000.0,
    country=Country.DE,
)
result = calculate_estate_tax(params)
print(f"Steuerpflichtig: {result.taxable_amount:,.2f} €")
print(f"Zu zahlende Steuer: {result.net_tax_payable:,.2f} €")

# 2. Dekadensimulation
plan = simulate_decade_gifting(1200000.0, RelationshipType.CHILD)
print(f"Steuerersparnis: {plan.tax_saved:,.2f} €")
```

---

## 🧪 Unit Tests

Das Projekt verfügt über 35 automatisierte Unit Tests:

```bash
pytest tests/ -v
```

---

## ⚖️ Rechtlicher Hinweis & Haftungsausschluss

Dieses Software-Paket stellt eine **rein technische Hilfsberechnung und unverbindliche finanzmathematische Modellierung** dar. Es ersetzt ausdrücklich **keine Rechts- oder Steuerberatung** im Sinne des Rechtsdienstleistungsgesetzes (§ 2 RDG) oder Steuerberatungsgesetzes (§ 5 StBerG). 

Gemäß der Grundsatzentscheidung des Bundesgerichtshofs (BGH, Urteil vom 09.09.2021 – I ZR 226/20, „Smartlaw“) ist die Bereitstellung algorithmenbasierter Generatoren und Berechnungstools zulässig. Für verbindliche steuerliche Beurteilungen konsultieren Sie bitte einen zugelassenen Steuerberater oder Fachanwalt für Erbrecht.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe die [LICENSE](LICENSE) Datei für Details.
Publiziert durch **[DACH Digitalwerk](https://dachdigitalwerk.github.io/)**.
