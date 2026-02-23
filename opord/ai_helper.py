"""
AI helper for OPORD generation using the OpenAI API.

Provides functions to generate individual OPORD section text from
brief user-supplied prompts using a context-aware system prompt
scoped to Charlie Company, 1-7 CAV (Airborne / Air Assault).
"""

import os
from typing import Optional

try:
    from openai import OpenAI
    _openai_available = True
except ImportError:  # pragma: no cover
    _openai_available = False

from .generator import UNIT_NAME, UNIT_TYPE, HIGHER_HQ

_SYSTEM_PROMPT = f"""You are a U.S. Army operations order (OPORD) writing assistant for
{UNIT_NAME}, an {UNIT_TYPE} company modeled after a Parachute Infantry Regiment (PIR)
unit in the 82nd Airborne Division.

Your role is to produce concise, doctrinally correct OPORD text following FM 6-0
and the standard 5-paragraph order format (Situation, Mission, Execution, Sustainment,
Command and Signal). When writing about this unit always keep in mind:
- Airborne insert (static line or HALO) and Air Assault (helicopter) operations.
- References to DZ (drop zone) and LZ (landing zone) as appropriate.
- The unit is a gaming / simulation regiment; keep language realistic but clearly
  labelled UNCLASSIFIED // TRAINING USE ONLY.
- Be concise and use the active voice. Use military time (24-hour clock).
- Do NOT invent classified information or real-world operational details.

When asked to generate a specific OPORD paragraph or sub-paragraph, output only
the requested content (do not repeat headings already provided by the caller).
"""


def get_client() -> Optional["OpenAI"]:
    """Return an OpenAI client if credentials are available, else None."""
    if not _openai_available:
        return None
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        return None
    return OpenAI(api_key=api_key)


def generate_section(section_name: str, user_notes: str, model: Optional[str] = None) -> str:
    """
    Generate OPORD section text using the OpenAI API.

    Parameters
    ----------
    section_name : str
        Name of the OPORD section to generate (e.g. "Mission Statement",
        "Commander's Intent", "Concept of Operations").
    user_notes : str
        Brief notes or keywords provided by the user describing the operation.
    model : str, optional
        OpenAI model name; defaults to the OPENAI_MODEL env var or "gpt-4o".

    Returns
    -------
    str
        AI-generated text for the requested section, or an empty string if the
        OpenAI client is not configured.
    """
    client = get_client()
    if client is None:
        return ""

    model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")

    user_message = (
        f"Generate the '{section_name}' section of an OPORD for {UNIT_NAME}. "
        f"Use the following operational notes as context:\n\n{user_notes}\n\n"
        "Write only the content of that section (no headings). "
        "Keep it under 150 words."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def generate_full_opord(form_data: dict, model: Optional[str] = None) -> dict:
    """
    Given a dictionary of raw user inputs, call the AI for each OPORD
    paragraph that is missing or sparse, and return an enriched dictionary.

    Parameters
    ----------
    form_data : dict
        Dictionary of user-submitted form fields (may be partially filled).
    model : str, optional
        OpenAI model name.

    Returns
    -------
    dict
        Copy of form_data with AI-generated values inserted for blank fields.
    """
    client = get_client()
    if client is None:
        return form_data

    result = dict(form_data)
    # Build a short operational summary to feed as context for every call.
    op_summary = (
        f"Operation: {form_data.get('operation_name', 'TBD')}. "
        f"Mission: {form_data.get('mission', 'TBD')}. "
        f"Insert method: {form_data.get('insert_method', 'TBD')}. "
        f"DZ/LZ: {form_data.get('dz_lz', 'TBD')}. "
        f"Enemy: {form_data.get('enemy_composition', 'unknown')}."
    )

    # Map of (result key, section label) for fields to auto-fill if blank.
    auto_fill_fields = [
        ("enemy_capabilities", "Enemy Capabilities"),
        ("enemy_most_likely_coa", "Enemy Most Likely Course of Action"),
        ("enemy_most_dangerous_coa", "Enemy Most Dangerous Course of Action"),
        ("commanders_intent", "Commander's Intent"),
        ("concept_of_operations", "Concept of Operations"),
        ("scheme_of_maneuver", "Scheme of Maneuver"),
        ("scheme_of_fires", "Scheme of Fires"),
        ("coordinating_instructions", "Coordinating Instructions"),
        ("sustainment_logistics", "Logistics paragraph"),
        ("sustainment_medical", "Medical paragraph"),
        ("signal", "Command and Signal paragraph"),
    ]

    for key, label in auto_fill_fields:
        if not result.get(key):
            result[key] = generate_section(label, op_summary, model=model)

    return result
