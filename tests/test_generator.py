"""Tests for the OPORD generator package."""
import pytest

from opord.generator import (
    OPORDData,
    OPORDGenerator,
    Situation,
    EnemyForces,
    FriendlyForces,
    Execution,
    Sustainment,
    CommandAndSignal,
    UNIT_NAME,
    UNIT_SHORT,
    HIGHER_HQ,
    SUBORDINATE_UNITS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_data() -> OPORDData:
    """Minimal OPORD with only required fields set."""
    return OPORDData(
        operation_name="IRON HAWK",
        mission=(
            "C/1-7 CAV conducts an airborne assault on OBJ EAGLE NLT 231800Z FEB 25 "
            "to destroy OPFOR element and seize key terrain."
        ),
    )


@pytest.fixture()
def full_data() -> OPORDData:
    """Fully populated OPORD data object."""
    return OPORDData(
        operation_name="STEEL TALON",
        classification="UNCLASSIFIED // TRAINING USE ONLY",
        dtg="231500Z FEB 2025",
        reference_maps="Kandahar, 1:50,000, Series V502",
        time_zone="ZULU",
        insert_method="Airborne (Static Line)",
        dz_lz="DZ FALCON",
        situation=Situation(
            enemy=EnemyForces(
                composition="Reinforced OPFOR platoon",
                disposition="Defending grid 12ABC34567",
                strength="~40 personnel",
                recent_activity="Established defensive positions 23FEB",
                capabilities="Man-portable RPG, PKM MG",
                most_likely_coa="Defend in place",
                most_dangerous_coa="Counterattack toward DZ FALCON",
            ),
            friendly=FriendlyForces(
                higher_hq_mission="1-7 CAV attacks to seize OBJ BULLDOG NLT 231800Z FEB 25",
                adjacent_units="Alpha Co (left), Bravo Co (right)",
                supporting_units="D/1-7 CAV (Aviation), 1-7 CAV FSE",
            ),
            attachments_detachments="1x JTAC attached",
            civil_considerations="Local population: neutral.",
        ),
        mission=(
            "C/1-7 CAV conducts an airborne assault on OBJ EAGLE NLT 231800Z FEB 25 "
            "to destroy OPFOR element."
        ),
        execution=Execution(
            commanders_intent="Seize OBJ EAGLE and consolidate.",
            higher_commanders_intent="Regain initiative and dismantle enemy control on the islands.",
            concept_of_operations="Two-phase: airborne insert then assault.",
            scheme_of_maneuver="1PLT left, 2PLT right, 3PLT reserve.",
            scheme_of_fires="CAS on call; mortars suppress DZ FALCON ingress.",
            tasks_to_subordinates={
                "1st Platoon (Rifle)": "Assault OBJ EAGLE.",
                "2nd Platoon (Rifle)": "Secure OBJ HAWK.",
                "Weapons Platoon": "Provide suppressive fires.",
            },
            coordinating_instructions="H-Hour 231800Z. No fires without CDR approval.",
            rules_of_engagement="PID required prior to engagement.",
        ),
        sustainment=Sustainment(
            logistics="Basic load plus 2 days of supply.",
            personnel="See manning roster.",
            medical="CASEVAC via UH-60 to FOB LIBERTY.",
        ),
        command_and_signal=CommandAndSignal(
            command="Grid 12ABC12345",
            succession_of_command="1PSG, then 1PLT LDR",
            signal="PACE: Primary=FM, Alternate=HF, Contingency=SATCOM, Emergency=Messenger",
            frequencies="CMD: 46.250 / LOG: 47.100",
            challenge_and_password="RAVEN / TALON",
        ),
    )


# ---------------------------------------------------------------------------
# Unit constants
# ---------------------------------------------------------------------------

def test_unit_name_contains_charlie_company():
    assert "Charlie Company" in UNIT_NAME


def test_unit_name_contains_7th_cavalry():
    assert "7th Cavalry" in UNIT_NAME


def test_unit_short_is_correct():
    assert UNIT_SHORT == "C/1-7 CAV"


def test_higher_hq_contains_battalion():
    assert "1st Battalion" in HIGHER_HQ


def test_subordinate_units_has_four_elements():
    assert len(SUBORDINATE_UNITS) >= 4
    platoon_units = [u for u in SUBORDINATE_UNITS if "Platoon" in u]
    assert len(platoon_units) >= 4  # 3 rifle + weapons


# ---------------------------------------------------------------------------
# OPORDGenerator — generate_text
# ---------------------------------------------------------------------------

class TestGenerateText:
    def test_returns_string(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        result = gen.generate_text()
        assert isinstance(result, str)

    def test_contains_operation_name(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        text = gen.generate_text()
        assert "IRON HAWK" in text

    def test_contains_five_paragraphs(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        text = gen.generate_text()
        for para in ["1. SITUATION", "2. MISSION", "3. EXECUTION", "4. SUSTAINMENT", "5. COMMAND"]:
            assert para in text, f"Missing paragraph heading: {para}"

    def test_contains_classification(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        text = gen.generate_text()
        assert "UNCLASSIFIED" in text

    def test_contains_mission_statement(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        text = gen.generate_text()
        assert "airborne assault" in text

    def test_full_data_enemy_info_present(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Reinforced OPFOR platoon" in text
        assert "12ABC34567" in text

    def test_full_data_friendly_info_present(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Alpha Co" in text

    def test_full_data_insert_method_present(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Airborne (Static Line)" in text

    def test_full_data_dz_lz_present(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "DZ FALCON" in text

    def test_full_data_commanders_intent(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Seize OBJ EAGLE" in text

    def test_full_data_higher_commanders_intent(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Regain initiative" in text

    def test_full_data_tasks_to_subordinates(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "1st Platoon (Rifle)" in text
        assert "Assault OBJ EAGLE" in text

    def test_full_data_sustainment(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "Basic load" in text
        assert "CASEVAC" in text

    def test_full_data_signal(self, full_data):
        gen = OPORDGenerator(full_data)
        text = gen.generate_text()
        assert "46.250" in text
        assert "RAVEN / TALON" in text

    def test_empty_fields_use_defaults(self):
        gen = OPORDGenerator(OPORDData())
        text = gen.generate_text()
        # Should still produce all paragraphs without errors
        for para in ["1. SITUATION", "2. MISSION", "3. EXECUTION", "4. SUSTAINMENT"]:
            assert para in text
        # Default fallback values should appear
        assert "Not reported" in text

    def test_ends_with_acknowledge(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        text = gen.generate_text()
        assert "ACKNOWLEDGE" in text


# ---------------------------------------------------------------------------
# OPORDGenerator — generate_dict
# ---------------------------------------------------------------------------

class TestGenerateDict:
    def test_returns_dict(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        d = gen.generate_dict()
        assert isinstance(d, dict)

    def test_contains_required_keys(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        d = gen.generate_dict()
        required_keys = [
            "unit", "unit_short", "unit_type", "higher_hq",
            "classification", "operation_name", "mission",
            "situation", "execution", "sustainment", "command_and_signal",
            "subordinate_units",
        ]
        for key in required_keys:
            assert key in d, f"Missing key: {key}"

    def test_unit_name_matches_constant(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        d = gen.generate_dict()
        assert d["unit"] == UNIT_NAME

    def test_operation_name_round_trips(self, full_data):
        gen = OPORDGenerator(full_data)
        d = gen.generate_dict()
        assert d["operation_name"] == "STEEL TALON"

    def test_situation_structure(self, full_data):
        gen = OPORDGenerator(full_data)
        d = gen.generate_dict()
        assert "enemy" in d["situation"]
        assert "friendly" in d["situation"]
        assert d["situation"]["enemy"]["composition"] == "Reinforced OPFOR platoon"

    def test_execution_tasks_in_dict(self, full_data):
        gen = OPORDGenerator(full_data)
        d = gen.generate_dict()
        tasks = d["execution"]["tasks_to_subordinates"]
        assert "1st Platoon (Rifle)" in tasks
        assert tasks["1st Platoon (Rifle)"] == "Assault OBJ EAGLE."

    def test_execution_higher_intent_in_dict(self, full_data):
        gen = OPORDGenerator(full_data)
        d = gen.generate_dict()
        assert "higher_commanders_intent" in d["execution"]
        assert "Regain initiative" in d["execution"]["higher_commanders_intent"]

    def test_subordinate_units_list(self, minimal_data):
        gen = OPORDGenerator(minimal_data)
        d = gen.generate_dict()
        assert isinstance(d["subordinate_units"], list)
        assert len(d["subordinate_units"]) >= 4
