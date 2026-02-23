"""
Google Slides helper for exporting an OPORD as a Google Slides presentation.

Authentication uses OAuth 2.0. On first run the user will be prompted to
authorise the application; a token is then cached in token.json.

If GOOGLE_SLIDES_TEMPLATE_ID is set, the helper copies that template and
replaces placeholder text. Otherwise it creates a blank presentation with
one slide per OPORD paragraph.

Default template:
  https://docs.google.com/presentation/d/1yktdbM4Rw0dcWcD07fYlY37AqF9eaCtx3Pdvkf0ReCw/edit

Placeholder convention (for template-based workflow):
  Heading:
    {{UNIT_NAME}}, {{OPERATION_NAME}}, {{DTG}}, {{TIME_ZONE}},
    {{CLASSIFICATION}}, {{REFERENCE_MAPS}}
  Situation — Enemy Forces:
    {{SITUATION_ENEMY}}, {{ENEMY_COMPOSITION}}, {{ENEMY_DISPOSITION}},
    {{ENEMY_STRENGTH}}, {{ENEMY_RECENT_ACTIVITY}}, {{ENEMY_CAPABILITIES}},
    {{ENEMY_MOST_LIKELY_COA}}, {{ENEMY_MOST_DANGEROUS_COA}}
  Situation — Friendly Forces:
    {{SITUATION_FRIENDLY}}, {{ADJACENT_UNITS}}, {{SUPPORTING_UNITS}}
  Situation — Other:
    {{ATTACHMENTS_DETACHMENTS}}, {{CIVIL_CONSIDERATIONS}}
  Mission:
    {{MISSION}}, {{INSERT_METHOD}}, {{DZ_LZ}}
  Execution:
    {{COMMANDERS_INTENT}}, {{CONCEPT_OF_OPS}}, {{SCHEME_OF_MANEUVER}},
    {{SCHEME_OF_FIRES}}, {{TASKS_TO_SUBORDINATES}},
    {{COORDINATING_INSTRUCTIONS}}, {{RULES_OF_ENGAGEMENT}}
  Sustainment:
    {{SUSTAINMENT_LOGISTICS}}, {{SUSTAINMENT_PERSONNEL}},
    {{SUSTAINMENT_MEDICAL}}
  Command and Signal:
    {{COMMAND_AND_SIGNAL}}, {{CP_LOCATION}}, {{SUCCESSION_OF_COMMAND}},
    {{SIGNAL}}, {{FREQUENCIES}}, {{CHALLENGE_AND_PASSWORD}}
"""

import os
from typing import Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    _google_available = True
except ImportError:  # pragma: no cover
    _google_available = False

SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]

TOKEN_FILE = "token.json"


def _get_credentials(credentials_file: str) -> Optional["Credentials"]:
    """Load or refresh OAuth2 credentials."""
    if not _google_available:
        return None

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                return None
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def _make_text_replace_request(placeholder: str, value: str) -> dict:
    """Build a Google Slides replaceAllText API request."""
    return {
        "replaceAllText": {
            "containsText": {"text": f"{{{{{placeholder}}}}}", "matchCase": True},
            "replaceText": value or "N/A",
        }
    }


def export_to_slides(opord_dict: dict) -> Optional[str]:
    """
    Export an OPORD dictionary to a Google Slides presentation.

    Parameters
    ----------
    opord_dict : dict
        Output of OPORDGenerator.generate_dict().

    Returns
    -------
    str or None
        URL of the created presentation, or None if export is unavailable.
    """
    credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    creds = _get_credentials(credentials_file)
    if creds is None:
        return None

    slides_service = build("slides", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    template_id = os.environ.get("GOOGLE_SLIDES_TEMPLATE_ID", "")
    title = (
        f"OPORD {opord_dict.get('operation_name', 'TBD')} - "
        f"{opord_dict.get('unit_short', 'C/1-7 CAV')}"
    )

    if template_id:
        # Copy the template
        copy_response = drive_service.files().copy(
            fileId=template_id,
            body={"name": title},
        ).execute()
        presentation_id = copy_response["id"]

        # Build replacement requests from OPORD data
        ex = opord_dict.get("execution", {})
        su = opord_dict.get("sustainment", {})
        cs = opord_dict.get("command_and_signal", {})
        sit = opord_dict.get("situation", {})
        enemy = sit.get("enemy", {})
        friendly = sit.get("friendly", {})

        tasks_text = "\n".join(
            f"{u}: {t}" for u, t in (ex.get("tasks_to_subordinates") or {}).items()
        ) or "Tasks TBD."

        requests = [
            # Heading
            _make_text_replace_request("UNIT_NAME", opord_dict.get("unit", "")),
            _make_text_replace_request("OPERATION_NAME", opord_dict.get("operation_name", "")),
            _make_text_replace_request("DTG", opord_dict.get("dtg", "")),
            _make_text_replace_request("TIME_ZONE", opord_dict.get("time_zone", "")),
            _make_text_replace_request("CLASSIFICATION", opord_dict.get("classification", "")),
            _make_text_replace_request("REFERENCE_MAPS", opord_dict.get("reference_maps", "")),
            # Situation — Enemy (composite)
            _make_text_replace_request(
                "SITUATION_ENEMY",
                "\n".join([
                    f"Composition: {enemy.get('composition', '')}",
                    f"Disposition: {enemy.get('disposition', '')}",
                    f"Strength: {enemy.get('strength', '')}",
                    f"Recent Activity: {enemy.get('recent_activity', '')}",
                    f"Capabilities: {enemy.get('capabilities', '')}",
                    f"Most Likely COA: {enemy.get('most_likely_coa', '')}",
                    f"Most Dangerous COA: {enemy.get('most_dangerous_coa', '')}",
                ])
            ),
            # Situation — Enemy (individual fields)
            _make_text_replace_request("ENEMY_COMPOSITION", enemy.get("composition", "")),
            _make_text_replace_request("ENEMY_DISPOSITION", enemy.get("disposition", "")),
            _make_text_replace_request("ENEMY_STRENGTH", enemy.get("strength", "")),
            _make_text_replace_request("ENEMY_RECENT_ACTIVITY", enemy.get("recent_activity", "")),
            _make_text_replace_request("ENEMY_CAPABILITIES", enemy.get("capabilities", "")),
            _make_text_replace_request("ENEMY_MOST_LIKELY_COA", enemy.get("most_likely_coa", "")),
            _make_text_replace_request("ENEMY_MOST_DANGEROUS_COA", enemy.get("most_dangerous_coa", "")),
            # Situation — Friendly
            _make_text_replace_request(
                "SITUATION_FRIENDLY",
                friendly.get("higher_hq_mission", "")
            ),
            _make_text_replace_request("ADJACENT_UNITS", friendly.get("adjacent_units", "")),
            _make_text_replace_request("SUPPORTING_UNITS", friendly.get("supporting_units", "")),
            # Situation — Other
            _make_text_replace_request("ATTACHMENTS_DETACHMENTS", sit.get("attachments_detachments", "")),
            _make_text_replace_request("CIVIL_CONSIDERATIONS", sit.get("civil_considerations", "")),
            # Mission
            _make_text_replace_request("MISSION", opord_dict.get("mission", "")),
            _make_text_replace_request("INSERT_METHOD", opord_dict.get("insert_method", "")),
            _make_text_replace_request("DZ_LZ", opord_dict.get("dz_lz", "")),
            # Execution
            _make_text_replace_request(
                "COMMANDERS_INTENT", ex.get("commanders_intent", "")
            ),
            _make_text_replace_request(
                "CONCEPT_OF_OPS", ex.get("concept_of_operations", "")
            ),
            _make_text_replace_request(
                "SCHEME_OF_MANEUVER", ex.get("scheme_of_maneuver", "")
            ),
            _make_text_replace_request(
                "SCHEME_OF_FIRES", ex.get("scheme_of_fires", "")
            ),
            _make_text_replace_request("TASKS_TO_SUBORDINATES", tasks_text),
            _make_text_replace_request(
                "COORDINATING_INSTRUCTIONS", ex.get("coordinating_instructions", "")
            ),
            _make_text_replace_request(
                "RULES_OF_ENGAGEMENT", ex.get("rules_of_engagement", "")
            ),
            # Sustainment
            _make_text_replace_request(
                "SUSTAINMENT_LOGISTICS", su.get("logistics", "")
            ),
            _make_text_replace_request(
                "SUSTAINMENT_PERSONNEL", su.get("personnel", "")
            ),
            _make_text_replace_request(
                "SUSTAINMENT_MEDICAL", su.get("medical", "")
            ),
            # Command and Signal (composite)
            _make_text_replace_request(
                "COMMAND_AND_SIGNAL",
                f"CP: {cs.get('command', '')}  "
                f"Succession: {cs.get('succession_of_command', '')}  "
                f"Signal: {cs.get('signal', '')}  "
                f"Frequencies: {cs.get('frequencies', '')}  "
                f"Challenge/Password: {cs.get('challenge_and_password', '')}"
            ),
            # Command and Signal (individual fields)
            _make_text_replace_request("CP_LOCATION", cs.get("command", "")),
            _make_text_replace_request("SUCCESSION_OF_COMMAND", cs.get("succession_of_command", "")),
            _make_text_replace_request("SIGNAL", cs.get("signal", "")),
            _make_text_replace_request("FREQUENCIES", cs.get("frequencies", "")),
            _make_text_replace_request("CHALLENGE_AND_PASSWORD", cs.get("challenge_and_password", "")),
        ]

        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests},
        ).execute()

    else:
        # Create a blank presentation with text slides
        presentation = slides_service.presentations().create(
            body={"title": title}
        ).execute()
        presentation_id = presentation["presentationId"]

        # Build slides for each paragraph
        generator_text = _build_slide_content(opord_dict)
        requests = []
        for idx, (slide_title, slide_body) in enumerate(generator_text):
            slide_id = f"slide_{idx}"
            title_id = f"title_{idx}"
            body_id = f"body_{idx}"

            if idx == 0:
                # Use the default first slide
                first_slide = presentation["slides"][0]
                existing_slide_id = first_slide["objectId"]
                requests += _text_slide_requests(
                    existing_slide_id,
                    first_slide["pageElements"],
                    slide_title,
                    slide_body,
                )
            else:
                requests += [
                    {
                        "createSlide": {
                            "objectId": slide_id,
                            "insertionIndex": idx,
                            "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"},
                            "placeholderIdMappings": [
                                {
                                    "layoutPlaceholder": {
                                        "type": "CENTERED_TITLE",
                                        "index": 0,
                                    },
                                    "objectId": title_id,
                                },
                                {
                                    "layoutPlaceholder": {"type": "BODY", "index": 0},
                                    "objectId": body_id,
                                },
                            ],
                        }
                    },
                    {
                        "insertText": {
                            "objectId": title_id,
                            "insertionIndex": 0,
                            "text": slide_title,
                        }
                    },
                    {
                        "insertText": {
                            "objectId": body_id,
                            "insertionIndex": 0,
                            "text": slide_body[:3000],  # Slides has text limits
                        }
                    },
                ]

        if requests:
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests},
            ).execute()

    url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    return url


def _text_slide_requests(slide_id: str, page_elements: list,
                         title_text: str, body_text: str) -> list:
    """Build insertText requests for the first (default) slide."""
    requests = []
    for element in page_elements:
        shape = element.get("shape", {})
        placeholder = shape.get("placeholder", {})
        p_type = placeholder.get("type", "")
        obj_id = element.get("objectId", "")
        if p_type in ("CENTERED_TITLE", "TITLE"):
            requests.append({
                "insertText": {
                    "objectId": obj_id,
                    "insertionIndex": 0,
                    "text": title_text,
                }
            })
        elif p_type == "BODY":
            requests.append({
                "insertText": {
                    "objectId": obj_id,
                    "insertionIndex": 0,
                    "text": body_text[:3000],
                }
            })
    return requests


def _build_slide_content(opord: dict) -> list:
    """Return list of (title, body) tuples for each OPORD slide."""
    unit = opord.get("unit", "")
    op = opord.get("operation_name", "TBD")
    dtg = opord.get("dtg", "")
    classification = opord.get("classification", "UNCLASSIFIED // TRAINING USE ONLY")
    sit = opord.get("situation", {})
    enemy = sit.get("enemy", {})
    friendly = sit.get("friendly", {})
    ex = opord.get("execution", {})
    su = opord.get("sustainment", {})
    cs = opord.get("command_and_signal", {})

    slides = [
        (
            f"OPORD {op} — {unit}",
            f"{classification}\nDTG: {dtg}\nReference Maps: {opord.get('reference_maps', 'N/A')}",
        ),
        (
            "1. SITUATION — Enemy Forces",
            (
                f"Composition: {enemy.get('composition', 'N/A')}\n"
                f"Disposition: {enemy.get('disposition', 'N/A')}\n"
                f"Strength: {enemy.get('strength', 'N/A')}\n"
                f"Recent Activity: {enemy.get('recent_activity', 'N/A')}\n"
                f"Capabilities: {enemy.get('capabilities', 'N/A')}\n"
                f"Most Likely COA: {enemy.get('most_likely_coa', 'N/A')}\n"
                f"Most Dangerous COA: {enemy.get('most_dangerous_coa', 'N/A')}"
            ),
        ),
        (
            "1. SITUATION — Friendly Forces",
            (
                f"Higher HQ Mission: {friendly.get('higher_hq_mission', 'N/A')}\n"
                f"Adjacent Units: {friendly.get('adjacent_units', 'N/A')}\n"
                f"Supporting Units: {friendly.get('supporting_units', 'N/A')}\n"
                f"Attachments/Detachments: {sit.get('attachments_detachments', 'N/A')}\n"
                f"Civil Considerations: {sit.get('civil_considerations', 'N/A')}"
            ),
        ),
        (
            "2. MISSION",
            (
                f"{opord.get('mission', 'N/A')}\n\n"
                f"Insert Method: {opord.get('insert_method', 'N/A')}\n"
                f"DZ/LZ: {opord.get('dz_lz', 'N/A')}"
            ),
        ),
        (
            "3. EXECUTION — Commander's Intent & Concept of Ops",
            (
                f"Commander's Intent:\n{ex.get('commanders_intent', 'N/A')}\n\n"
                f"Concept of Operations:\n{ex.get('concept_of_operations', 'N/A')}"
            ),
        ),
        (
            "3. EXECUTION — Maneuver, Fires & Tasks",
            (
                f"Scheme of Maneuver:\n{ex.get('scheme_of_maneuver', 'N/A')}\n\n"
                f"Scheme of Fires:\n{ex.get('scheme_of_fires', 'N/A')}\n\n"
                "Tasks to Subordinates:\n" +
                "\n".join(
                    f"  {u}: {t}"
                    for u, t in (ex.get("tasks_to_subordinates") or {}).items()
                )
            ),
        ),
        (
            "3. EXECUTION — Coordinating Instructions & ROE",
            (
                f"Coordinating Instructions:\n{ex.get('coordinating_instructions', 'N/A')}\n\n"
                f"Rules of Engagement:\n{ex.get('rules_of_engagement', 'N/A')}"
            ),
        ),
        (
            "4. SUSTAINMENT",
            (
                f"Logistics:\n{su.get('logistics', 'N/A')}\n\n"
                f"Personnel:\n{su.get('personnel', 'N/A')}\n\n"
                f"Medical:\n{su.get('medical', 'N/A')}"
            ),
        ),
        (
            "5. COMMAND AND SIGNAL",
            (
                f"CP Location: {cs.get('command', 'N/A')}\n"
                f"Succession of Command: {cs.get('succession_of_command', 'N/A')}\n\n"
                f"Signal:\n{cs.get('signal', 'N/A')}\n"
                f"Frequencies: {cs.get('frequencies', 'N/A')}\n"
                f"Challenge/Password: {cs.get('challenge_and_password', 'N/A')}"
            ),
        ),
    ]
    return slides
