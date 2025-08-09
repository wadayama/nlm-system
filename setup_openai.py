#!/usr/bin/env python
"""OpenAI API key setup utility for NLM System"""

import os
import stat
from pathlib import Path


def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    print("OpenAI API Key Setup for NLM System")
    print("=" * 40)
    print("\nSupported models:")
    print("  🌐 OpenAI Models (API key required):")
    print("     - gpt-5      (Most capable, Premium tier)")
    print("     - gpt-5-mini (Balanced performance, Standard tier)")
    print("     - gpt-5-nano (Fast & economical, Economy tier)")
    print("\n  💻 Local Model (no API key needed):")
    print("     - gpt-oss:20b (Default, runs via LMStudio)")
    
    print("\n" + "-" * 40)
    print("To use OpenAI models, you need an API key from:")
    print("https://platform.openai.com/api-keys")
    
    key = input("\nEnter your OpenAI API key (sk-...): ").strip()
    
    if not key:
        print("❌ No key provided. Exiting.")
        return
    
    if not key.startswith("sk-"):
        print("⚠️  Warning: OpenAI API keys typically start with 'sk-'")
        confirm = input("Continue anyway? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("❌ Setup cancelled.")
            return
    
    # Choose save location
    print("\n" + "-" * 40)
    print("Where to save the API key?")
    print("1. Current directory (.openai_key) - Project specific")
    print("2. User config (~/.config/nlm/openai_key) - Global")
    print("3. Cancel")
    
    while True:
        choice = input("Choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            key_file = Path(".openai_key")
            break
        elif choice == "2":
            config_dir = Path.home() / ".config" / "nlm"
            config_dir.mkdir(parents=True, exist_ok=True)
            key_file = config_dir / "openai_key"
            break
        elif choice == "3":
            print("❌ Setup cancelled.")
            return
        else:
            print("Please enter 1, 2, or 3")
    
    try:
        # Save the key
        key_file.write_text(key + "\n")
        
        # Set restrictive permissions (owner read/write only)
        key_file.chmod(0o600)
        
        print(f"\n✅ API key saved to: {key_file}")
        print("🔒 File permissions set to 600 (owner read/write only)")
        
        # Test usage examples
        print("\n" + "-" * 40)
        print("Usage examples:")
        print("  python -c \"from nlm_interpreter import NLMSession; s=NLMSession(model='gpt-5-nano'); print('OpenAI ready!')\"")
        print("  python nlm_interpreter.py -m gpt-5-mini \"Save 'test' to {{var}}\"")
        print("\nFor local LLM (no charges):")
        print("  python -c \"from nlm_interpreter import NLMSession; s=NLMSession(); print('Local LLM ready!')\"")
        
        print(f"\n🎉 Setup complete! You can now use OpenAI models.")
        
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        print("Please check file permissions and try again.")


def check_openai_setup():
    """Check if OpenAI API key is already configured"""
    local_key = Path(".openai_key")
    global_key = Path.home() / ".config" / "nlm" / "openai_key"
    
    print("OpenAI API Key Status")
    print("=" * 25)
    
    if local_key.exists():
        print(f"✅ Local key found: {local_key}")
        # Check if it looks like a valid key
        try:
            key_content = local_key.read_text().strip()
            if key_content.startswith("sk-"):
                print("   Format looks correct (starts with 'sk-')")
            else:
                print("   ⚠️  Format warning: doesn't start with 'sk-'")
        except:
            print("   ❌ Error reading key file")
    else:
        print("❌ No local key (.openai_key)")
    
    if global_key.exists():
        print(f"✅ Global key found: {global_key}")
        try:
            key_content = global_key.read_text().strip()
            if key_content.startswith("sk-"):
                print("   Format looks correct (starts with 'sk-')")
            else:
                print("   ⚠️  Format warning: doesn't start with 'sk-'")
        except:
            print("   ❌ Error reading key file")
    else:
        print("❌ No global key (~/.config/nlm/openai_key)")
    
    if not local_key.exists() and not global_key.exists():
        print("\n💡 No OpenAI API key found. Run setup to configure:")
        print("   python setup_openai.py")
    else:
        print("\n🎉 OpenAI API key is configured!")


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_openai_setup()
    else:
        setup_openai_key()


if __name__ == "__main__":
    main()