"""Tests for AI helper module (mocked — no real API calls)."""
import pytest
from unittest.mock import MagicMock, patch

from opord.ai_helper import generate_section, generate_full_opord, get_client


class TestGetClient:
    def test_returns_none_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert get_client() is None

    def test_returns_none_with_placeholder_key(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
        assert get_client() is None


class TestGenerateSection:
    def test_returns_empty_string_when_no_client(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        result = generate_section("Mission Statement", "Attack objective EAGLE")
        assert result == ""

    def test_returns_ai_text_when_client_configured(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "C/1-7 CAV attacks OBJ EAGLE."
        mock_client.chat.completions.create.return_value = mock_response

        with patch("opord.ai_helper.get_client", return_value=mock_client):
            result = generate_section("Mission Statement", "Attack objective EAGLE")
        assert result == "C/1-7 CAV attacks OBJ EAGLE."


class TestGenerateFullOpord:
    def test_returns_input_unchanged_when_no_client(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        form = {"operation_name": "IRON HAWK", "mission": "Attack OBJ EAGLE."}
        result = generate_full_opord(form)
        assert result["operation_name"] == "IRON HAWK"
        assert result["mission"] == "Attack OBJ EAGLE."

    def test_fills_blank_fields_with_ai(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "AI-generated content."
        mock_client.chat.completions.create.return_value = mock_response

        with patch("opord.ai_helper.get_client", return_value=mock_client):
            form = {
                "operation_name": "IRON HAWK",
                "mission": "Attack OBJ EAGLE.",
                "commanders_intent": "",  # blank — should be filled
            }
            result = generate_full_opord(form)
        assert result["commanders_intent"] == "AI-generated content."

    def test_preserves_existing_values(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "AI-generated content."
        mock_client.chat.completions.create.return_value = mock_response

        with patch("opord.ai_helper.get_client", return_value=mock_client):
            form = {
                "operation_name": "IRON HAWK",
                "mission": "Attack OBJ EAGLE.",
                "commanders_intent": "User-provided intent.",  # should NOT be overwritten
            }
            result = generate_full_opord(form)
        assert result["commanders_intent"] == "User-provided intent."
