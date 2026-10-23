# -*- coding: utf-8 -*-
import pytest
from erbst_dach.models import (
    CalculationInput,
    RelationshipType,
    TransferType,
    TaxClass,
    Country,
)
from erbst_dach.calculator import (
    calculate_estate_tax,
    get_allowance,
    get_tax_class,
    get_tax_rate,
    round_down_100,
    simulate_decade_gifting,
)
from erbst_dach.validator import ValidationError, validate_input


def test_allowance_values():
    assert get_allowance(RelationshipType.SPOUSE) == 500000.0
    assert get_allowance(RelationshipType.CHILD) == 400000.0
    assert get_allowance(RelationshipType.GRANDCHILD) == 200000.0
    assert get_allowance(RelationshipType.PARENT_INHERITANCE) == 100000.0
    assert get_allowance(RelationshipType.PARENT_GIFT) == 20000.0
    assert get_allowance(RelationshipType.SIBLING) == 20000.0
    assert get_allowance(RelationshipType.OTHER) == 20000.0


def test_tax_class_assignment():
    assert get_tax_class(RelationshipType.SPOUSE) == TaxClass.CLASS_I
    assert get_tax_class(RelationshipType.CHILD) == TaxClass.CLASS_I
    assert get_tax_class(RelationshipType.GRANDCHILD) == TaxClass.CLASS_I
    assert get_tax_class(RelationshipType.PARENT_INHERITANCE) == TaxClass.CLASS_I
    assert get_tax_class(RelationshipType.PARENT_GIFT) == TaxClass.CLASS_II
    assert get_tax_class(RelationshipType.SIBLING) == TaxClass.CLASS_II
    assert get_tax_class(RelationshipType.OTHER) == TaxClass.CLASS_III


def test_tax_rate_class_1():
    assert get_tax_rate(50000, TaxClass.CLASS_I) == 7.0
    assert get_tax_rate(75000, TaxClass.CLASS_I) == 7.0
    assert get_tax_rate(75001, TaxClass.CLASS_I) == 11.0
    assert get_tax_rate(300000, TaxClass.CLASS_I) == 11.0
    assert get_tax_rate(600000, TaxClass.CLASS_I) == 15.0
    assert get_tax_rate(6000000, TaxClass.CLASS_I) == 19.0
    assert get_tax_rate(13000000, TaxClass.CLASS_I) == 23.0
    assert get_tax_rate(26000000, TaxClass.CLASS_I) == 27.0
    assert get_tax_rate(30000000, TaxClass.CLASS_I) == 30.0


def test_tax_rate_class_2():
    assert get_tax_rate(50000, TaxClass.CLASS_II) == 15.0
    assert get_tax_rate(300000, TaxClass.CLASS_II) == 20.0
    assert get_tax_rate(600000, TaxClass.CLASS_II) == 25.0
    assert get_tax_rate(6000000, TaxClass.CLASS_II) == 30.0
    assert get_tax_rate(13000000, TaxClass.CLASS_II) == 35.0
    assert get_tax_rate(26000000, TaxClass.CLASS_II) == 40.0
    assert get_tax_rate(30000000, TaxClass.CLASS_II) == 43.0


def test_tax_rate_class_3():
    assert get_tax_rate(50000, TaxClass.CLASS_III) == 30.0
    assert get_tax_rate(6000000, TaxClass.CLASS_III) == 30.0
    assert get_tax_rate(7000000, TaxClass.CLASS_III) == 50.0


def test_round_down_100():
    assert round_down_100(155.99) == 100.0
    assert round_down_100(100.0) == 100.0
    assert round_down_100(99.99) == 0.0
    assert round_down_100(0.0) == 0.0


def test_inheritance_under_allowance():
    # Kind erbt 350.000 € (Freibetrag 400.000 €) -> Steuer 0 €
    inp = CalculationInput(
        gross_amount=350000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
    )
    res = calculate_estate_tax(inp)
    assert res.net_tax_payable == 0.0
    assert res.taxable_amount == 0.0
    assert res.net_beneficiary_receives == 350000.0


def test_inheritance_over_allowance_child():
    # Kind erbt 600.000 € -> Freibetrag 400.000 € -> Steuerpflichtig 200.000 €
    # Satz Steuerklasse I bei 200.000 € ist 11 % -> Steuer 22.000 €
    inp = CalculationInput(
        gross_amount=600000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
    )
    res = calculate_estate_tax(inp)
    assert res.taxable_amount == 200000.0
    assert res.tax_rate_percent == 11.0
    assert res.net_tax_payable == 22000.0
    assert res.net_beneficiary_receives == 578000.0


def test_spouse_with_pension_allowance():
    # Ehegatte erbt 800.000 €, Freibetrag 500.000 € + Versorgungsfreibetrag 256.000 € = 756.000 €
    # Steuerpflichtig: 44.000 € (abgerundet 44.000 €), Satz 7 % = 3.080 €
    inp = CalculationInput(
        gross_amount=800000.0,
        relationship=RelationshipType.SPOUSE,
        transfer_type=TransferType.INHERITANCE,
        pension_allowance=256000.0,
    )
    res = calculate_estate_tax(inp)
    assert res.taxable_amount == 44000.0
    assert res.tax_rate_percent == 7.0
    assert res.net_tax_payable == 3080.0


def test_family_home_exemption():
    # Kind erbt Familienheim im Wert von 500.000 € + Barvermögen 300.000 € = 800.000 €
    # Familienheim steuerfrei -> Verbleiben 300.000 € -> unter Freibetrag 400.000 € -> 0 € Steuer
    inp = CalculationInput(
        gross_amount=800000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
        family_home_exempt=True,
        family_home_value=500000.0,
    )
    res = calculate_estate_tax(inp)
    assert res.family_home_deduction == 500000.0
    assert res.taxable_amount == 0.0
    assert res.net_tax_payable == 0.0


def test_estate_liabilities_deduction():
    # Nachlass 500.000 €, Verbindlichkeiten 150.000 € -> Netto 350.000 € (unter Kind-Freibetrag 400k)
    inp = CalculationInput(
        gross_amount=500000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
        estate_liabilities=150000.0,
    )
    res = calculate_estate_tax(inp)
    assert res.net_transfer == 350000.0
    assert res.net_tax_payable == 0.0


def test_parent_inheritance_vs_gift():
    # Eltern im Erbfall: Steuerklasse I, Freibetrag 100.000 €
    inp_erbfall = CalculationInput(
        gross_amount=150000.0,
        relationship=RelationshipType.PARENT_INHERITANCE,
        transfer_type=TransferType.INHERITANCE,
    )
    res_erbfall = calculate_estate_tax(inp_erbfall)
    assert res_erbfall.tax_class == TaxClass.CLASS_I
    assert res_erbfall.personal_allowance == 100000.0
    assert res_erbfall.taxable_amount == 50000.0
    assert res_erbfall.tax_rate_percent == 7.0
    assert res_erbfall.net_tax_payable == 3500.0

    # Eltern bei Schenkung: Steuerklasse II, Freibetrag 20.000 €
    inp_schenkung = CalculationInput(
        gross_amount=150000.0,
        relationship=RelationshipType.PARENT_GIFT,
        transfer_type=TransferType.GIFT,
    )
    res_schenkung = calculate_estate_tax(inp_schenkung)
    assert res_schenkung.tax_class == TaxClass.CLASS_II
    assert res_schenkung.personal_allowance == 20000.0
    assert res_schenkung.taxable_amount == 130000.0
    assert res_schenkung.tax_rate_percent == 20.0
    assert res_schenkung.net_tax_payable == 26000.0


def test_prior_gifts_10_years():
    # Vorerwerb 300.000 € (vor 4 Jahren) + Neuerwerb 300.000 € = 600.000 € (Kind)
    # Zusammen: 600.000 € - 400.000 € = 200.000 € taxable -> 11 % = 22.000 €
    # Vorerwerb isoliert: 300.000 € < 400.000 € -> 0 € Steuer
    # Zu zahlen: 22.000 € - 0 € = 22.000 €
    inp = CalculationInput(
        gross_amount=300000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.GIFT,
        prior_gifts_10y=300000.0,
    )
    res = calculate_estate_tax(inp)
    assert res.prior_gifts_10y == 300000.0
    assert res.taxable_amount == 200000.0
    assert res.tax_rate_percent == 11.0
    assert res.net_tax_payable == 22000.0


def test_austria_zero_tax_and_bao_reporting():
    # AT: Immer 0 % Steuer
    inp = CalculationInput(
        gross_amount=80000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.GIFT,
        country=Country.AT,
    )
    res = calculate_estate_tax(inp)
    assert res.net_tax_payable == 0.0
    assert res.tax_rate_percent == 0.0
    assert res.reporting_required is True  # > 50.000 € Angehörigengrenze
    assert "§ 121a BAO" in res.reporting_notice


def test_austria_below_bao_threshold():
    inp = CalculationInput(
        gross_amount=30000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.GIFT,
        country=Country.AT,
    )
    res = calculate_estate_tax(inp)
    assert res.net_tax_payable == 0.0
    assert res.reporting_required is False


def test_switzerland_spouse_exempt():
    inp = CalculationInput(
        gross_amount=1000000.0,
        relationship=RelationshipType.SPOUSE,
        transfer_type=TransferType.INHERITANCE,
        country=Country.CH,
    )
    res = calculate_estate_tax(inp)
    assert res.net_tax_payable == 0.0
    assert res.tax_rate_percent == 0.0


def test_switzerland_third_party():
    inp = CalculationInput(
        gross_amount=100000.0,
        relationship=RelationshipType.OTHER,
        transfer_type=TransferType.INHERITANCE,
        country=Country.CH,
    )
    res = calculate_estate_tax(inp)
    assert res.net_tax_payable > 0.0
    assert res.tax_rate_percent == 25.0


def test_simulate_decade_gifting_savings():
    # 1.200.000 € an Kind:
    # Sofort: 1.2M - 400k = 800k taxable -> 19 % = 152.000 € Steuer
    # Gestaffelt über 3 x 400k (heute, nach 10 J., nach 20 J.): Jedes Mal 400k Freibetrag -> 0 € Steuer!
    # Ersparnis: 152.000 € (100 %)
    dec = simulate_decade_gifting(1200000.0, RelationshipType.CHILD)
    assert dec.lump_sum_tax == 152000.0
    assert dec.decade_plan_tax == 0.0
    assert dec.tax_saved == 152000.0
    assert dec.savings_percent == 100.0
    assert len(dec.steps) == 3


def test_validation_negative_gross():
    inp = CalculationInput(gross_amount=-500.0)
    with pytest.raises(ValidationError):
        calculate_estate_tax(inp)


def test_validation_negative_liabilities():
    inp = CalculationInput(gross_amount=50000.0, estate_liabilities=-100.0)
    with pytest.raises(ValidationError):
        calculate_estate_tax(inp)


def test_validation_warnings():
    # Versorgungsfreibetrag bei Schenkung -> Warning
    inp = CalculationInput(
        gross_amount=100000.0,
        transfer_type=TransferType.GIFT,
        pension_allowance=50000.0,
    )
    warnings = validate_input(inp)
    assert any("Versorgungsfreibetrag" in w for w in warnings)


def test_third_party_tax_rates_and_class():
    # Nicht-Verwandter (Kl. III), 50.000 €
    # Freibetrag: 20.000 € -> steuerpflichtig 30.000 €
    # Satz: 30 % -> Steuer 9.000 €
    inp = CalculationInput(
        gross_amount=50000.0,
        relationship=RelationshipType.OTHER,
        transfer_type=TransferType.INHERITANCE,
    )
    res = calculate_estate_tax(inp)
    assert res.tax_class == TaxClass.CLASS_III
    assert res.personal_allowance == 20000.0
    assert res.taxable_amount == 30000.0
    assert res.tax_rate_percent == 30.0
    assert res.net_tax_payable == 9000.0


def test_high_net_worth_bracket():
    # 30.000.000 € Erbe an Kind: Freibetrag 400k -> 29.600.000 € steuerpflichtig
    # Über 26 Mio €: Höchstsatz 30 %
    inp = CalculationInput(
        gross_amount=30000000.0,
        relationship=RelationshipType.CHILD,
        transfer_type=TransferType.INHERITANCE,
    )
    res = calculate_estate_tax(inp)
    assert res.taxable_amount == 29600000.0
    assert res.tax_rate_percent == 30.0
    assert res.net_tax_payable == 8880000.0
