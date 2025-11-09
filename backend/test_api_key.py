#!/usr/bin/env python3
"""Quick test script to verify API key is loaded correctly."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from anthropic_client import get_api_key
    
    print("Testing API key loading...")
    api_key = get_api_key()
    
    if api_key:
        print(f"✅ API key loaded successfully!")
        print(f"   Length: {len(api_key)} characters")
        print(f"   First 10 chars: {api_key[:10]}...")
        print(f"   Last 10 chars: ...{api_key[-10:]}")
        
        # Check if it looks like a valid Anthropic key
        if api_key.startswith('sk-ant-'):
            print("✅ Key format looks correct (starts with 'sk-ant-')")
        else:
            print("⚠️  Warning: Key doesn't start with 'sk-ant-' (might still be valid)")
    else:
        print("❌ API key is empty or not found")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error loading API key: {e}")
    sys.exit(1)

