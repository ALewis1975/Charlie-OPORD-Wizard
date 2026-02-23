"""
OPORD data models and 5-paragraph format generator for
Charlie Company, 1st Battalion, 7th Cavalry Gaming Regiment.

Doctrine reference: FM 6-0, Appendix C (Operation Order format).
Unit model: Airborne / Air Assault company based on a PIR in the 82nd Airborne Division.
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Unit constants
# ---------------------------------------------------------------------------

UNIT_NAME = "Charlie Company, 1st Battalion, 7th Cavalry Gaming Regiment"
UNIT_SHORT = "C/1-7 CAV"
UNIT_TYPE = "Airborne / Air Assault (PIR model)"
HIGHER_HQ = "1st Battalion, 7th Cavalry Gaming Regiment (1-7 CAV)"
REGIMENT = "7th Cavalry Gaming Regiment"

# Standard subordinate elements (company-level)
SUBORDINATE_UNITS = [
    "1st Platoon (Rifle)",
    "2nd Platoon (Rifle)",
    "3rd Platoon (Rifle)",
    "Weapons Platoon",
    "Headquarters & Support Element",
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EnemyForces:
    """Para 1a - Enemy Forces."""
    composition: str = ""
    disposition: str = ""
    strength: str = ""
    recent_activity: str = ""
    capabilities: str = ""
    most_likely_coa: str = ""
    most_dangerous_coa: str = ""


@dataclass
class FriendlyForces:
    """Para 1b - Friendly Forces."""
    higher_hq_mission: str = ""
    adjacent_units: str = ""
    supporting_units: str = ""


@dataclass
class Situation:
    """Paragraph 1 - Situation."""
    enemy: EnemyForces = field(default_factory=EnemyForces)
    friendly: FriendlyForces = field(default_factory=FriendlyForces)
    attachments_detachments: str = ""
    civil_considerations: str = ""


@dataclass
class Execution:
    """Paragraph 3 - Execution."""
    commanders_intent: str = ""
    higher_commanders_intent: str = ""
    concept_of_operations: str = ""
    scheme_of_maneuver: str = ""
    scheme_of_fires: str = ""
    tasks_to_subordinates: dict = field(default_factory=dict)
    coordinating_instructions: str = ""
    rules_of_engagement: str = ""


@dataclass
class Sustainment:
    """Paragraph 4 - Sustainment."""
    logistics: str = ""
    personnel: str = ""
    medical: str = ""


@dataclass
class CommandAndSignal:
    """Paragraph 5 - Command and Signal."""
    command: str = ""
    succession_of_command: str = ""
    signal: str = ""
    frequencies: str = ""
    challenge_and_password: str = ""


@dataclass
class OPORDData:
    """Complete Operation Order data object."""
    # Heading
    operation_name: str = ""
    classification: str = "UNCLASSIFIED // TRAINING USE ONLY"
    dtg: str = ""
    reference_maps: str = ""
    time_zone: str = "ZULU"

    # Insert / movement method (Airborne/Air Assault specific)
    insert_method: str = ""
    dz_lz: str = ""

    # Five paragraphs
    situation: Situation = field(default_factory=Situation)
    mission: str = ""
    execution: Execution = field(default_factory=Execution)
    sustainment: Sustainment = field(default_factory=Sustainment)
    command_and_signal: CommandAndSignal = field(default_factory=CommandAndSignal)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class OPORDGenerator:
    """
    Generates a formatted 5-paragraph OPORD for Charlie Company, 1-7 CAV.
    """

    def __init__(self, data: OPORDData):
        self.data = data

    def _header(self) -> str:
        lines = [
            self.data.classification,
            "",
            f"OPERATION ORDER {self.data.operation_name or 'TBD'}-XX",
            f"({self.data.dtg or 'DTG TBD'} {self.data.time_zone})",
            "",
            f"Issuing HQ: {UNIT_NAME}",
            f"Reference Map(s): {self.data.reference_maps or 'N/A'}",
            "",
            ("=" * 70),
        ]
        return "\n".join(lines)

    def _paragraph_1(self) -> str:
        s = self.data.situation
        e = s.enemy
        f = s.friendly

        lines = [
            "1. SITUATION",
            "",
            "  a. Enemy Forces.",
            f"     Composition:        {e.composition or 'Not reported.'}",
            f"     Disposition:        {e.disposition or 'Not reported.'}",
            f"     Strength:           {e.strength or 'Not reported.'}",
            f"     Recent Activity:    {e.recent_activity or 'Not reported.'}",
            f"     Capabilities:       {e.capabilities or 'Not reported.'}",
            f"     Most Likely COA:    {e.most_likely_coa or 'Not reported.'}",
            f"     Most Dangerous COA: {e.most_dangerous_coa or 'Not reported.'}",
            "",
            "  b. Friendly Forces.",
            f"     Higher HQ Mission:  {f.higher_hq_mission or 'See higher OPORD.'}",
            f"     Adjacent Units:     {f.adjacent_units or 'None identified.'}",
            f"     Supporting Units:   {f.supporting_units or 'None identified.'}",
            "",
            "  c. Attachments and Detachments.",
            f"     {s.attachments_detachments or 'None.'}",
            "",
            "  d. Civil Considerations.",
            f"     {s.civil_considerations or 'None assessed at this time.'}",
        ]
        return "\n".join(lines)

    def _paragraph_2(self) -> str:
        lines = [
            "2. MISSION",
            "",
            f"  {self.data.mission or 'Mission not specified.'}",
        ]
        if self.data.insert_method:
            lines += [
                "",
                f"  Insert Method: {self.data.insert_method}",
            ]
        if self.data.dz_lz:
            lines += [f"  DZ/LZ: {self.data.dz_lz}"]
        return "\n".join(lines)

    def _paragraph_3(self) -> str:
        ex = self.data.execution
        lines = [
            "3. EXECUTION",
            "",
            "  a. Commander's Intent.",
            f"     Purpose:    {ex.commanders_intent or 'Not specified.'}",
            "",
            "  b. Higher Commander's Intent.",
            f"     {ex.higher_commanders_intent or 'See higher OPORD.'}",
            "",
            "  c. Concept of Operations.",
            f"     {ex.concept_of_operations or 'Not specified.'}",
            "",
            "  d. Scheme of Maneuver.",
            f"     {ex.scheme_of_maneuver or 'Not specified.'}",
            "",
            "  e. Scheme of Fires.",
            f"     {ex.scheme_of_fires or 'Not specified.'}",
            "",
            "  f. Tasks to Subordinate Units.",
        ]
        if ex.tasks_to_subordinates:
            for unit, task in ex.tasks_to_subordinates.items():
                lines.append(f"     ({unit}): {task}")
        else:
            for unit in SUBORDINATE_UNITS:
                lines.append(f"     ({unit}): Tasks TBD.")
        lines += [
            "",
            "  g. Coordinating Instructions.",
            f"     {ex.coordinating_instructions or 'As required.'}",
            "",
            "  h. Rules of Engagement.",
            f"     {ex.rules_of_engagement or 'Standard ROE apply. PID required prior to engagement.'}",
        ]
        return "\n".join(lines)

    def _paragraph_4(self) -> str:
        su = self.data.sustainment
        lines = [
            "4. SUSTAINMENT",
            "",
            "  a. Logistics.",
            f"     {su.logistics or 'Standard combat load. Resupply via higher HQ.'}",
            "",
            "  b. Personnel.",
            f"     {su.personnel or 'See unit manning roster.'}",
            "",
            "  c. Medical.",
            f"     {su.medical or 'Casevac IAW unit SOP. Nearest MTF: TBD.'}",
        ]
        return "\n".join(lines)

    def _paragraph_5(self) -> str:
        cs = self.data.command_and_signal
        lines = [
            "5. COMMAND AND SIGNAL",
            "",
            "  a. Command.",
            f"     Commander:               {UNIT_SHORT} CDR",
            f"     Succession of Command:   {cs.succession_of_command or '1PSG, then 1PLT LDR, then 2PLT LDR'}",
            f"     CP Location:             {cs.command or 'TBD'}",
            "",
            "  b. Signal.",
            f"     {cs.signal or 'PACE plan IAW unit SOP.'}",
            f"     Frequencies:             {cs.frequencies or 'See signal annex.'}",
            f"     Challenge / Password:    {cs.challenge_and_password or 'TBD'}",
        ]
        return "\n".join(lines)

    def _footer(self) -> str:
        return "\n".join([
            "",
            ("=" * 70),
            "",
            "ACKNOWLEDGE",
            "",
            f"  [Commander, {UNIT_SHORT}]",
            "",
            self.data.classification,
        ])

    def generate_text(self) -> str:
        """Return the complete OPORD as a formatted plain-text string."""
        sections = [
            self._header(),
            "",
            self._paragraph_1(),
            "",
            self._paragraph_2(),
            "",
            self._paragraph_3(),
            "",
            self._paragraph_4(),
            "",
            self._paragraph_5(),
            self._footer(),
        ]
        return "\n".join(sections)

    def generate_dict(self) -> dict:
        """Return the OPORD as a dictionary (useful for JSON / template rendering)."""
        d = self.data
        return {
            "unit": UNIT_NAME,
            "unit_short": UNIT_SHORT,
            "unit_type": UNIT_TYPE,
            "higher_hq": HIGHER_HQ,
            "classification": d.classification,
            "operation_name": d.operation_name,
            "dtg": d.dtg,
            "time_zone": d.time_zone,
            "reference_maps": d.reference_maps,
            "insert_method": d.insert_method,
            "dz_lz": d.dz_lz,
            "situation": {
                "enemy": {
                    "composition": d.situation.enemy.composition,
                    "disposition": d.situation.enemy.disposition,
                    "strength": d.situation.enemy.strength,
                    "recent_activity": d.situation.enemy.recent_activity,
                    "capabilities": d.situation.enemy.capabilities,
                    "most_likely_coa": d.situation.enemy.most_likely_coa,
                    "most_dangerous_coa": d.situation.enemy.most_dangerous_coa,
                },
                "friendly": {
                    "higher_hq_mission": d.situation.friendly.higher_hq_mission,
                    "adjacent_units": d.situation.friendly.adjacent_units,
                    "supporting_units": d.situation.friendly.supporting_units,
                },
                "attachments_detachments": d.situation.attachments_detachments,
                "civil_considerations": d.situation.civil_considerations,
            },
            "mission": d.mission,
            "execution": {
                "commanders_intent": d.execution.commanders_intent,
                "higher_commanders_intent": d.execution.higher_commanders_intent,
                "concept_of_operations": d.execution.concept_of_operations,
                "scheme_of_maneuver": d.execution.scheme_of_maneuver,
                "scheme_of_fires": d.execution.scheme_of_fires,
                "tasks_to_subordinates": d.execution.tasks_to_subordinates,
                "coordinating_instructions": d.execution.coordinating_instructions,
                "rules_of_engagement": d.execution.rules_of_engagement,
            },
            "sustainment": {
                "logistics": d.sustainment.logistics,
                "personnel": d.sustainment.personnel,
                "medical": d.sustainment.medical,
            },
            "command_and_signal": {
                "command": d.command_and_signal.command,
                "succession_of_command": d.command_and_signal.succession_of_command,
                "signal": d.command_and_signal.signal,
                "frequencies": d.command_and_signal.frequencies,
                "challenge_and_password": d.command_and_signal.challenge_and_password,
            },
            "subordinate_units": SUBORDINATE_UNITS,
        }
