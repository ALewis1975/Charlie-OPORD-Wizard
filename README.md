# Charlie OPORD Wizard

AI-supported Operations Order (OPORD) generator for **Charlie Company, 1st Battalion, 7th Cavalry Gaming Regiment**.

Charlie Company is an Airborne / Air Assault company modelled after a Parachute Infantry Regiment (PIR) unit in the 82nd Airborne Division, operating within the 7th Cavalry Gaming Regiment.

> References: [7cav.us](https://7cav.us/) · [7CAV Wiki](https://wiki.7cav.us/wiki/Main_Page)

---

## Overview

The wizard walks a user through the standard **U.S. Army 5-paragraph OPORD format** (FM 6-0):

| Para | Topic |
|------|-------|
| 1 | **Situation** — Enemy & friendly forces, attachments, civil considerations |
| 2 | **Mission** — Who, What, When, Where, Why (5 Ws) |
| 3 | **Execution** — Commander's intent, concept of ops, tasks to subordinates, coordinating instructions, ROE |
| 4 | **Sustainment** — Logistics, personnel, medical (CASEVAC) |
| 5 | **Command and Signal** — CP location, succession, PACE plan, frequencies |

Airborne / Air Assault specifics (insert method, DZ/LZ) are first-class fields throughout.

**AI enrichment** (OpenAI) optionally generates text for any field left blank, keeping the OPORD doctrinally correct and contextually aware of the unit's Airborne/Air Assault mission set.

**Google Slides export** pushes the finished OPORD to a new (or template-based) Google Slides presentation for briefing use.

---

## Quick Start

### 1 · Prerequisites

- Python 3.10+
- (Optional) An [OpenAI API key](https://platform.openai.com/api-keys) for AI enrichment
- (Optional) Google Cloud credentials for Slides export

### 2 · Install

```bash
git clone https://github.com/ALewis1975/Charlie-OPORD-Wizard.git
cd Charlie-OPORD-Wizard
pip install -r requirements.txt
```

### 3 · Configure

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (and optionally Google credentials)
```

### 4 · Run

```bash
python app.py
# Open http://127.0.0.1:5000 in your browser
```

---

## Google Slides Export (optional)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Slides API** and **Google Drive API**.
3. Create an **OAuth 2.0 Client ID** (Desktop app), download `credentials.json`, and place it in the project root.
4. Set `GOOGLE_CREDENTIALS_FILE=credentials.json` in your `.env`.
5. (Optional) Set `GOOGLE_SLIDES_TEMPLATE_ID` to the ID of a Google Slides template that uses the `{{PLACEHOLDER}}` convention documented in `opord/slides_helper.py`.

On first export you will be prompted to authorise the app in your browser; a `token.json` file is cached for subsequent runs.

---

## Project Structure

```
Charlie-OPORD-Wizard/
├── app.py                  # Flask web application
├── requirements.txt
├── .env.example            # Environment variable template
├── opord/
│   ├── __init__.py
│   ├── generator.py        # OPORDData models + OPORDGenerator (text & dict output)
│   ├── ai_helper.py        # OpenAI integration for section generation
│   └── slides_helper.py    # Google Slides API export
├── templates/
│   ├── base.html
│   ├── index.html          # OPORD input form
│   └── result.html         # OPORD preview + export button
├── static/
│   └── style.css
└── tests/
    ├── test_generator.py
    ├── test_app.py
    └── test_ai_helper.py
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Classification

All output is labelled **UNCLASSIFIED // TRAINING USE ONLY**. This tool is intended for gaming / simulation use within the 7th Cavalry Gaming Regiment and does not generate or handle any classified information.
