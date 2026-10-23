# -*- coding: utf-8 -*-
import json
import pytest
from erbst_dach.cli import main, parse_args


def test_parse_args_defaults():
    args = parse_args(["500000"])
    assert args.amount == 500000.0
    assert args.relationship == "child"
    assert args.type == "erbfall"
    assert args.country == "DE"
    assert args.prior_gifts == 0.0
    assert args.estate_liabilities == 0.0
    assert args.simulate_decades is False
    assert args.json is False


def test_cli_stdout_basic(capsys):
    main(["600000", "-r", "child"])
    captured = capsys.readouterr()
    assert "DACH ERBSCHAFTS- & SCHENKUNGSSTEUER-RECHNER 2026" in captured.out
    assert "Steuerpflichtiger Erwerb:  200.000,00 €" in captured.out
    assert "ZU ZAHLENDE STEUER:        22.000,00 €" in captured.out


def test_cli_stdout_alt_amount_flag(capsys):
    main(["-a", "400000", "-r", "child"])
    captured = capsys.readouterr()
    assert "ZU ZAHLENDE STEUER:        0,00 €" in captured.out


def test_cli_json_output(capsys):
    main(["600000", "-r", "child", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "DE"
    assert data["relationship"] == "child"
    assert data["gross_amount"] == 600000.0
    assert data["personal_allowance"] == 400000.0
    assert data["taxable_amount"] == 200000.0
    assert data["net_tax_payable"] == 22000.0
    assert data["net_beneficiary_receives"] == 578000.0


def test_cli_simulate_decades_json(capsys):
    main(["1200000", "-r", "child", "--simulate-decades", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "decade_simulation" in data
    assert data["decade_simulation"]["tax_saved"] == 152000.0
    assert len(data["decade_simulation"]["steps"]) == 3


def test_cli_simulate_decades_text(capsys):
    main(["1200000", "-r", "child", "--simulate-decades"])
    captured = capsys.readouterr()
    assert "10-JAHRES-KETTENSCHENKUNGS-SIMULATOR" in captured.out
    assert "STEUERERSPARNIS:" in captured.out


def test_cli_austria(capsys):
    main(["100000", "-c", "AT", "-t", "schenkung", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "AT"
    assert data["net_tax_payable"] == 0.0
    assert data["reporting_required"] is True


def test_cli_switzerland(capsys):
    main(["500000", "-c", "CH", "-r", "spouse", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "CH"
    assert data["net_tax_payable"] == 0.0


def test_cli_with_prior_gifts(capsys):
    main(["300000", "-r", "child", "--prior-gifts", "300000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["prior_gifts_10y"] == 300000.0
    assert data["net_tax_payable"] == 22000.0


def test_cli_with_family_home(capsys):
    main(["800000", "-r", "child", "--family-home", "500000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["family_home_deduction"] == 500000.0
    assert data["net_tax_payable"] == 0.0


def test_cli_with_liabilities(capsys):
    main(["500000", "-r", "child", "--estate-liabilities", "150000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["estate_liabilities"] == 150000.0
    assert data["net_transfer"] == 350000.0
    assert data["net_tax_payable"] == 0.0


def test_cli_missing_amount_exits():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
