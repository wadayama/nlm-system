#!/usr/bin/env python
"""Test model switching functionality"""

import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for importing

from nlm_interpreter import NLMSession


def test_local_model_default():
    """Test that local model (gpt-oss:20b) is used by default"""
    print("Testing default local model...")
    
    with patch('nlm_interpreter.OpenAI') as mock_openai:
        session = NLMSession(namespace="test_local")
        
        # Check model and endpoint
        assert session.model == "gpt-oss:20b"
        assert session.endpoint == "http://localhost:1234/v1"
        assert session.api_key == "ollama"
        
        # Check that OpenAI client was initialized with local settings
        mock_openai.assert_called_once_with(
            base_url="http://localhost:1234/v1",
            api_key="ollama"
        )
    
    print("✅ Default local model test passed")


def test_openai_model_detection():
    """Test that OpenAI models are detected correctly"""
    print("Testing OpenAI model detection...")
    
    openai_models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]
    
    for model in openai_models:
        with patch('nlm_interpreter.OpenAI') as mock_openai:
            # Mock the API key loading
            with patch.object(NLMSession, '_load_openai_key', return_value="sk-test-key"):
                # Capture print output
                with patch('builtins.print') as mock_print:
                    session = NLMSession(model=model, namespace=f"test_{model}")
                    
                    # Check model and endpoint
                    assert session.model == model
                    assert session.endpoint == "https://api.openai.com/v1"
                    assert session.api_key == "sk-test-key"
                    
                    # Check that OpenAI client was initialized with OpenAI settings
                    mock_openai.assert_called_once_with(
                        base_url="https://api.openai.com/v1",
                        api_key="sk-test-key"
                    )
                    
                    # Check that OpenAI usage message was printed
                    mock_print.assert_any_call(f"🌐 Using OpenAI API: {model}")
    
    print("✅ OpenAI model detection test passed")


def test_api_key_loading():
    """Test API key loading from files"""
    print("Testing API key loading...")
    
    # Test with temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.openai_key', delete=False) as f:
        test_key = "sk-test-api-key-12345"
        f.write(test_key)
        f.flush()
        temp_file = Path(f.name)
    
    try:
        with patch('nlm_interpreter.OpenAI'):
            # Mock Path.exists and read_text to simulate key file
            with patch('pathlib.Path.exists') as mock_exists:
                with patch('pathlib.Path.read_text') as mock_read:
                    # Mock that local .openai_key exists
                    def exists_side_effect(self):
                        return str(self).endswith('.openai_key')
                    
                    mock_exists.side_effect = exists_side_effect
                    mock_read.return_value = test_key
                    
                    # Capture print output
                    with patch('builtins.print'):
                        session = NLMSession(model="gpt-5-nano")
                        assert session.api_key == test_key
    finally:
        temp_file.unlink()  # Clean up
    
    print("✅ API key loading test passed")


def test_api_key_missing_error():
    """Test error when API key is missing for OpenAI models"""
    print("Testing missing API key error...")
    
    with patch('nlm_interpreter.OpenAI'):
        # Mock that no API key files exist
        with patch('pathlib.Path.exists', return_value=False):
            try:
                session = NLMSession(model="gpt-5")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "OpenAI API key not found" in str(e)
                assert "setup_openai.py" in str(e)
    
    print("✅ Missing API key error test passed")


def test_model_info_display():
    """Test that model information is displayed correctly"""
    print("Testing model info display...")
    
    with patch('nlm_interpreter.OpenAI'):
        with patch.object(NLMSession, '_load_openai_key', return_value="sk-test"):
            with patch('builtins.print') as mock_print:
                session = NLMSession(model="gpt-5-mini")
                
                # Check that usage info was printed
                mock_print.assert_any_call("🌐 Using OpenAI API: gpt-5-mini")
                mock_print.assert_any_call("⚠️  Using OpenAI API - Standard tier")
                mock_print.assert_any_call("   Charges will apply to your OpenAI account")
    
    print("✅ Model info display test passed")


def test_explicit_api_key():
    """Test providing API key explicitly"""
    print("Testing explicit API key...")
    
    with patch('nlm_interpreter.OpenAI') as mock_openai:
        with patch('builtins.print'):
            explicit_key = "sk-explicit-key"
            session = NLMSession(model="gpt-5", api_key=explicit_key)
            
            assert session.api_key == explicit_key
            mock_openai.assert_called_once_with(
                base_url="https://api.openai.com/v1",
                api_key=explicit_key
            )
    
    print("✅ Explicit API key test passed")


def test_custom_endpoint():
    """Test custom endpoint override"""
    print("Testing custom endpoint...")
    
    with patch('nlm_interpreter.OpenAI') as mock_openai:
        custom_endpoint = "http://custom.api.com/v1"
        session = NLMSession(endpoint=custom_endpoint, api_key="test-key")
        
        assert session.endpoint == custom_endpoint
        mock_openai.assert_called_once_with(
            base_url=custom_endpoint,
            api_key="test-key"
        )
    
    print("✅ Custom endpoint test passed")


def run_all_model_switching_tests():
    """Run all model switching tests"""
    print("=" * 60)
    print("MODEL SWITCHING TESTS")
    print("=" * 60)
    
    tests = [
        ("Default Local Model", test_local_model_default),
        ("OpenAI Model Detection", test_openai_model_detection),
        ("API Key Loading", test_api_key_loading),
        ("Missing API Key Error", test_api_key_missing_error),
        ("Model Info Display", test_model_info_display),
        ("Explicit API Key", test_explicit_api_key),
        ("Custom Endpoint", test_custom_endpoint),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            
            test_func()
            passed += 1
            print(f"✅ {name} PASSED")
            
        except Exception as e:
            failed += 1
            print(f"❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"MODEL SWITCHING TESTS SUMMARY")
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_model_switching_tests()
    sys.exit(0 if success else 1)