"""Tests for configuration module."""

import os
import pytest
from unittest.mock import patch
from config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_from_env_with_valid_token_and_languages(self):
        """Test loading config with valid BOT_TOKEN and AVAILABLE_LANGUAGES."""
        with patch.dict(os.environ, {
            "BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "AVAILABLE_LANGUAGES": "ru,en,de"
        }):
            config = Config.from_env()
            
            assert config.bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            assert config.available_languages == ["ru", "en", "de"]
    
    def test_from_env_with_default_language(self):
        """Test loading config with missing AVAILABLE_LANGUAGES uses default."""
        with patch.dict(os.environ, {
            "BOT_TOKEN": "test_token_123"
        }, clear=True):
            config = Config.from_env()
            
            assert config.bot_token == "test_token_123"
            assert config.available_languages == ["en"]
    
    def test_from_env_missing_bot_token_exits(self):
        """Test that missing BOT_TOKEN causes system exit."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit) as exc_info:
                Config.from_env()
            
            assert exc_info.value.code == 1
    
    def test_from_env_empty_bot_token_exits(self):
        """Test that empty BOT_TOKEN causes system exit."""
        with patch.dict(os.environ, {"BOT_TOKEN": "   "}):
            with pytest.raises(SystemExit) as exc_info:
                Config.from_env()
            
            assert exc_info.value.code == 1
    
    def test_parse_languages_with_valid_codes(self):
        """Test parsing valid language codes."""
        result = Config._parse_languages("ru,en,de,fr")
        assert result == ["ru", "en", "de", "fr"]
    
    def test_parse_languages_with_whitespace(self):
        """Test parsing language codes with whitespace."""
        result = Config._parse_languages(" ru , en , de ")
        assert result == ["ru", "en", "de"]
    
    def test_parse_languages_filters_invalid_codes(self):
        """Test that invalid language codes are filtered out."""
        result = Config._parse_languages("ru,invalid,en,123,de")
        assert result == ["ru", "en", "de"]
    
    def test_parse_languages_with_empty_string(self):
        """Test parsing empty string returns empty list."""
        result = Config._parse_languages("")
        assert result == []
    
    def test_parse_languages_case_normalization(self):
        """Test that language codes are normalized to lowercase."""
        result = Config._parse_languages("RU,En,DE")
        assert result == ["ru", "en", "de"]
