"""Tests for the Google Slides helper module."""
import pytest
from unittest.mock import MagicMock, patch

from opord.slides_helper import _make_text_replace_request, _build_slide_content


class TestMakeTextReplaceRequest:
    def test_wraps_placeholder_with_braces(self):
        req = _make_text_replace_request("UNIT_NAME", "C/1-7 CAV")
        assert req["replaceAllText"]["containsText"]["text"] == "{{UNIT_NAME}}"

    def test_sets_replace_text(self):
        req = _make_text_replace_request("OPERATION_NAME", "IRON HAWK")
        assert req["replaceAllText"]["replaceText"] == "IRON HAWK"

    def test_uses_na_for_empty_value(self):
        req = _make_text_replace_request("DTG", "")
        assert req["replaceAllText"]["replaceText"] == "N/A"

    def test_uses_na_for_none_value(self):
        req = _make_text_replace_request("DTG", None)
        assert req["replaceAllText"]["replaceText"] == "N/A"

    def test_match_case_is_true(self):
        req = _make_text_replace_request("MISSION", "Attack OBJ EAGLE")
        assert req["replaceAllText"]["containsText"]["matchCase"] is True


class TestBuildSlideContent:
    @pytest.fixture()
    def full_opord_dict(self):
        return {
            "unit": "Charlie Company, 1st Battalion, 7th Cavalry Gaming Regiment",
            "unit_short": "C/1-7 CAV",
            "operation_name": "STEEL TALON",
            "classification": "UNCLASSIFIED // TRAINING USE ONLY",
            "dtg": "231500Z FEB 2025",
            "reference_maps": "Kandahar, 1:50,000",
            "insert_method": "Airborne (Static Line)",
            "dz_lz": "DZ FALCON",
            "situation": {
                "enemy": {
                    "composition": "Reinforced platoon",
                    "disposition": "Defending grid 12ABC34567",
                    "strength": "~40 personnel",
                    "recent_activity": "Established positions",
                    "capabilities": "RPG, PKM",
                    "most_likely_coa": "Defend in place",
                    "most_dangerous_coa": "Counterattack",
                },
                "friendly": {
                    "higher_hq_mission": "1-7 CAV attacks to seize OBJ BULLDOG",
                    "adjacent_units": "Alpha Co (left)",
                    "supporting_units": "D/1-7 CAV (Aviation)",
                },
                "attachments_detachments": "1x JTAC attached",
                "civil_considerations": "Neutral population",
            },
            "mission": "C/1-7 CAV conducts airborne assault on OBJ EAGLE",
            "execution": {
                "commanders_intent": "Seize OBJ EAGLE",
                "concept_of_operations": "Two-phase operation",
                "scheme_of_maneuver": "1PLT left, 2PLT right",
                "scheme_of_fires": "CAS on call",
                "tasks_to_subordinates": {
                    "1st Platoon (Rifle)": "Assault OBJ EAGLE.",
                    "2nd Platoon (Rifle)": "Secure flanks.",
                },
                "coordinating_instructions": "H-Hour 231800Z",
                "rules_of_engagement": "PID required.",
            },
            "sustainment": {
                "logistics": "Basic load",
                "personnel": "See roster",
                "medical": "CASEVAC via UH-60",
            },
            "command_and_signal": {
                "command": "Grid 12ABC12345",
                "succession_of_command": "1PSG",
                "signal": "PACE plan IAW SOP",
                "frequencies": "CMD: 46.250",
                "challenge_and_password": "RAVEN / TALON",
            },
        }

    def test_returns_list_of_tuples(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        assert isinstance(slides, list)
        assert all(isinstance(s, tuple) and len(s) == 2 for s in slides)

    def test_first_slide_is_title(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        title, _ = slides[0]
        assert "STEEL TALON" in title

    def test_contains_enemy_info(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        enemy_slide = next(
            (body for title, body in slides if "Enemy" in title), ""
        )
        assert "Reinforced platoon" in enemy_slide

    def test_contains_mission(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        mission_slide = next(
            (body for title, body in slides if "MISSION" in title), ""
        )
        assert "airborne assault" in mission_slide

    def test_contains_sustainment(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        sus_slide = next(
            (body for title, body in slides if "SUSTAINMENT" in title), ""
        )
        assert "Basic load" in sus_slide
        assert "CASEVAC" in sus_slide

    def test_contains_command_and_signal(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        cs_slide = next(
            (body for title, body in slides if "COMMAND" in title), ""
        )
        assert "46.250" in cs_slide
        assert "RAVEN / TALON" in cs_slide

    def test_slide_count(self, full_opord_dict):
        slides = _build_slide_content(full_opord_dict)
        # Title + Enemy + Friendly + Mission + Intent&ConOps + Maneuver&Fires + Coord&ROE + Sustainment + C&S
        assert len(slides) == 9
