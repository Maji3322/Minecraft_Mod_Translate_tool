"""Tests for Ollama endpoint resolution helpers."""

import unittest
from unittest.mock import Mock, patch

from src.core.ollama_api import candidate_ollama_base_urls, resolve_ollama_base_url


class OllamaApiHelperTests(unittest.TestCase):
    """Regression tests for executable/runtime Ollama endpoint handling."""

    def test_candidate_urls_add_ipv4_fallback_for_localhost(self):
        """localhost should produce an IPv4 fallback candidate."""
        self.assertEqual(
            candidate_ollama_base_urls("http://localhost:11434"),
            ["http://localhost:11434", "http://127.0.0.1:11434"],
        )

    def test_candidate_urls_leave_non_localhost_untouched(self):
        """Remote hosts should not be rewritten."""
        self.assertEqual(
            candidate_ollama_base_urls("http://192.168.1.10:11434"),
            ["http://192.168.1.10:11434"],
        )

    @patch("src.core.ollama_api.httpx.get")
    def test_resolve_returns_ipv4_fallback_when_localhost_fails(self, mock_get):
        """Runtime requests should fall back to 127.0.0.1 when needed."""

        def side_effect(url, timeout):
            if url == "http://localhost:11434/api/tags":
                raise OSError("connection refused")
            response = Mock()
            response.status_code = 200
            return response

        mock_get.side_effect = side_effect

        self.assertEqual(
            resolve_ollama_base_url("http://localhost:11434"),
            "http://127.0.0.1:11434",
        )

    @patch("src.core.ollama_api.httpx.get")
    def test_resolve_returns_original_when_no_candidate_is_reachable(self, mock_get):
        """The configured URL should be preserved if nothing responds."""
        mock_get.side_effect = OSError("still down")

        self.assertEqual(
            resolve_ollama_base_url("http://localhost:11434"),
            "http://localhost:11434",
        )
