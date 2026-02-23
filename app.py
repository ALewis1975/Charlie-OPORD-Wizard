"""
Charlie OPORD Wizard — Flask web application.

Routes
------
GET  /           Display the OPORD input form.
POST /generate   Accept form data, optionally call AI, render OPORD preview.
POST /export     Export the current OPORD to Google Slides.
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, flash

from opord.generator import (
    OPORDData,
    OPORDGenerator,
    Situation,
    EnemyForces,
    FriendlyForces,
    Execution,
    Sustainment,
    CommandAndSignal,
)
from opord.ai_helper import generate_full_opord, get_client
from opord.slides_helper import export_to_slides

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


def _form_to_opord_data(form: dict) -> OPORDData:
    """Map flat HTML form fields to an OPORDData object."""
    tasks = {}
    for unit in [
        "1st Platoon (Rifle)",
        "2nd Platoon (Rifle)",
        "3rd Platoon (Rifle)",
        "Weapons Platoon",
        "Headquarters & Support Element",
    ]:
        key = f"task_{unit.split()[0].lower()}"
        val = form.get(key, "").strip()
        if val:
            tasks[unit] = val

    return OPORDData(
        operation_name=form.get("operation_name", "").strip(),
        classification=form.get("classification", "UNCLASSIFIED // TRAINING USE ONLY").strip(),
        dtg=form.get("dtg", "").strip(),
        reference_maps=form.get("reference_maps", "").strip(),
        time_zone=form.get("time_zone", "ZULU").strip(),
        insert_method=form.get("insert_method", "").strip(),
        dz_lz=form.get("dz_lz", "").strip(),
        situation=Situation(
            enemy=EnemyForces(
                composition=form.get("enemy_composition", "").strip(),
                disposition=form.get("enemy_disposition", "").strip(),
                strength=form.get("enemy_strength", "").strip(),
                recent_activity=form.get("enemy_recent_activity", "").strip(),
                capabilities=form.get("enemy_capabilities", "").strip(),
                most_likely_coa=form.get("enemy_most_likely_coa", "").strip(),
                most_dangerous_coa=form.get("enemy_most_dangerous_coa", "").strip(),
            ),
            friendly=FriendlyForces(
                higher_hq_mission=form.get("friendly_higher_hq_mission", "").strip(),
                adjacent_units=form.get("friendly_adjacent_units", "").strip(),
                supporting_units=form.get("friendly_supporting_units", "").strip(),
            ),
            attachments_detachments=form.get("attachments_detachments", "").strip(),
            civil_considerations=form.get("civil_considerations", "").strip(),
        ),
        mission=form.get("mission", "").strip(),
        execution=Execution(
            commanders_intent=form.get("commanders_intent", "").strip(),
            concept_of_operations=form.get("concept_of_operations", "").strip(),
            scheme_of_maneuver=form.get("scheme_of_maneuver", "").strip(),
            scheme_of_fires=form.get("scheme_of_fires", "").strip(),
            tasks_to_subordinates=tasks,
            coordinating_instructions=form.get("coordinating_instructions", "").strip(),
            rules_of_engagement=form.get("rules_of_engagement", "").strip(),
        ),
        sustainment=Sustainment(
            logistics=form.get("sustainment_logistics", "").strip(),
            personnel=form.get("sustainment_personnel", "").strip(),
            medical=form.get("sustainment_medical", "").strip(),
        ),
        command_and_signal=CommandAndSignal(
            command=form.get("command_cp", "").strip(),
            succession_of_command=form.get("succession_of_command", "").strip(),
            signal=form.get("signal", "").strip(),
            frequencies=form.get("frequencies", "").strip(),
            challenge_and_password=form.get("challenge_and_password", "").strip(),
        ),
    )


@app.route("/", methods=["GET"])
def index():
    """Render the OPORD input form."""
    default_dtg = datetime.now(timezone.utc).strftime("%d%H%MZ %b %Y").upper()
    ai_enabled = get_client() is not None
    return render_template("index.html", default_dtg=default_dtg, ai_enabled=ai_enabled)


@app.route("/generate", methods=["POST"])
def generate():
    """Process form, optionally run AI enrichment, render OPORD preview."""
    form_data = dict(request.form)
    use_ai = request.form.get("use_ai") == "on"
    form_data.pop("use_ai", None)

    # Flatten single-item lists from MultiDict
    flat = {k: (v[0] if isinstance(v, list) else v) for k, v in form_data.items()}

    if use_ai:
        try:
            flat = generate_full_opord(flat)
        except Exception as exc:  # noqa: BLE001
            flash(f"AI enrichment failed: {exc}. Proceeding without AI.", "warning")

    opord_data = _form_to_opord_data(flat)
    generator = OPORDGenerator(opord_data)
    opord_text = generator.generate_text()
    opord_dict = generator.generate_dict()

    # Store for the export route
    session["opord_dict"] = opord_dict

    slides_enabled = bool(
        os.environ.get("GOOGLE_CREDENTIALS_FILE")
        and os.path.exists(os.environ.get("GOOGLE_CREDENTIALS_FILE", ""))
    )

    return render_template(
        "result.html",
        opord_text=opord_text,
        opord=opord_dict,
        slides_enabled=slides_enabled,
    )


@app.route("/export", methods=["POST"])
def export():
    """Export the stored OPORD to Google Slides."""
    opord_dict = session.get("opord_dict")
    if not opord_dict:
        flash("No OPORD found in session. Please generate one first.", "warning")
        return redirect(url_for("index"))

    try:
        url = export_to_slides(opord_dict)
    except Exception as exc:  # noqa: BLE001
        flash(f"Export to Google Slides failed: {exc}", "danger")
        return redirect(url_for("index"))

    if url:
        flash(f"Presentation created: {url}", "success")
    else:
        flash(
            "Google Slides export is not configured. "
            "Set GOOGLE_CREDENTIALS_FILE in your .env file.",
            "warning",
        )
    return redirect(url_for("index"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
