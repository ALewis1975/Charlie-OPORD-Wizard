"""Tests for the Flask web application."""
import pytest

# app.py imports dotenv and opord modules — ensure they're importable
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app, _form_to_opord_data
from opord.generator import UNIT_NAME


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def minimal_form():
    return {
        "operation_name": "IRON HAWK",
        "classification": "UNCLASSIFIED // TRAINING USE ONLY",
        "dtg": "231500Z FEB 2025",
        "time_zone": "ZULU",
        "reference_maps": "",
        "insert_method": "Airborne (Static Line)",
        "dz_lz": "DZ FALCON",
        "enemy_composition": "OPFOR platoon",
        "enemy_disposition": "Defending",
        "enemy_strength": "~30",
        "enemy_recent_activity": "Patrol activity",
        "enemy_capabilities": "",
        "enemy_most_likely_coa": "",
        "enemy_most_dangerous_coa": "",
        "friendly_higher_hq_mission": "1-7 CAV attacks to seize OBJ BULLDOG.",
        "friendly_adjacent_units": "",
        "friendly_supporting_units": "",
        "attachments_detachments": "",
        "civil_considerations": "",
        "mission": (
            "C/1-7 CAV conducts an airborne assault on OBJ EAGLE NLT 231800Z FEB 25 "
            "to destroy OPFOR element."
        ),
        "commanders_intent": "Seize OBJ EAGLE.",
        "concept_of_operations": "Two phase operation.",
        "scheme_of_maneuver": "1PLT left, 2PLT right.",
        "scheme_of_fires": "Mortars in support.",
        "task_1st": "Assault OBJ EAGLE.",
        "task_2nd": "Secure flanks.",
        "task_3rd": "",
        "task_weapons": "",
        "task_headquarters": "",
        "coordinating_instructions": "H-Hour 231800Z.",
        "rules_of_engagement": "PID required.",
        "sustainment_logistics": "Basic load.",
        "sustainment_personnel": "See roster.",
        "sustainment_medical": "CASEVAC via UH-60.",
        "command_cp": "Grid 12ABC12345",
        "succession_of_command": "1PSG",
        "signal": "PACE plan IAW SOP.",
        "frequencies": "CMD: 46.250",
        "challenge_and_password": "RAVEN / TALON",
    }


class TestIndexRoute:
    def test_get_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_form(self, client):
        resp = client.get("/")
        assert b"<form" in resp.data

    def test_contains_unit_badge(self, client):
        resp = client.get("/")
        assert b"C/1-7 CAV" in resp.data

    def test_contains_five_paragraph_headings(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        for heading in ["Situation", "Mission", "Execution", "Sustainment", "Command"]:
            assert heading in html, f"Missing heading: {heading}"


class TestGenerateRoute:
    def test_post_returns_200(self, client, minimal_form):
        resp = client.post("/generate", data=minimal_form)
        assert resp.status_code == 200

    def test_result_contains_operation_name(self, client, minimal_form):
        resp = client.post("/generate", data=minimal_form)
        assert b"IRON HAWK" in resp.data

    def test_result_contains_mission(self, client, minimal_form):
        resp = client.post("/generate", data=minimal_form)
        assert b"airborne assault" in resp.data

    def test_result_contains_unit_name(self, client, minimal_form):
        resp = client.post("/generate", data=minimal_form)
        assert UNIT_NAME.encode() in resp.data

    def test_ai_off_does_not_crash(self, client, minimal_form):
        # AI is disabled (no real API key); form submit without AI flag should work.
        minimal_form.pop("use_ai", None)
        resp = client.post("/generate", data=minimal_form)
        assert resp.status_code == 200


class TestFormToOpordData:
    def test_maps_operation_name(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert data.operation_name == "IRON HAWK"

    def test_maps_mission(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert "OBJ EAGLE" in data.mission

    def test_maps_enemy_composition(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert data.situation.enemy.composition == "OPFOR platoon"

    def test_maps_insert_method(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert data.insert_method == "Airborne (Static Line)"

    def test_maps_tasks_to_subordinates(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert "1st Platoon (Rifle)" in data.execution.tasks_to_subordinates
        assert data.execution.tasks_to_subordinates["1st Platoon (Rifle)"] == "Assault OBJ EAGLE."

    def test_blank_tasks_excluded(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert "Weapons Platoon" not in data.execution.tasks_to_subordinates

    def test_maps_frequencies(self, minimal_form):
        data = _form_to_opord_data(minimal_form)
        assert "46.250" in data.command_and_signal.frequencies
