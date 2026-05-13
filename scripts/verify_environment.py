#!/usr/bin/env python3
"""
Environment verification script for claude-seo-unified
Checks all dependencies, API keys, and configuration
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} detected. Require 3.10+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package, import_name=None):
    """Check if Python package is installed"""
    import_name = import_name or package
    try:
        __import__(import_name)
        print(f"✅ {package}")
        return True
    except ImportError:
        print(f"❌ {package} not installed")
        return False

def check_playwright():
    """Verify Playwright browsers installed"""
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "chromium" in result.stdout.lower():
            print("✅ Playwright browsers")
            return True
        print("⚠️ Playwright installed but browsers missing")
        print("   Run: playwright install chromium")
        return False
    except Exception as e:
        print(f"❌ Playwright: {e}")
        return False

def check_env_file():
    """Check for .env file"""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        print("✅ .env file found")
        return True
    print("⚠️ .env file not found (optional)")
    return True  # Not critical

def check_api_keys():
    """Check critical API keys"""
    keys = {
        "ANTHROPIC_API_KEY": "Claude API",
        "OPENAI_API_KEY": "OpenAI API (optional)",
    }
    found = []
    missing = []
    
    for key, name in keys.items():
        if os.getenv(key):
            print(f"✅ {name}")
            found.append(key)
        else:
            print(f"⚠️ {name} not configured")
            missing.append(key)
    
    return len(found) > 0  # At least one API key required

def check_directories():
    """Verify required directories"""
    dirs = [".seo-cache", "output", "logs", "config"]
    all_ok = True
    for d in dirs:
        path = Path.cwd() / d
        if path.exists():
            print(f"✅ {d}/")
        else:
            print(f"⚠️ {d}/ missing (will be created)")
            path.mkdir(parents=True, exist_ok=True)
    return all_ok

def main():
    print("🔍 Claude SEO Unified - Environment Verification\n")
    
    results = []
    
    print("📦 Core Dependencies:")
    results.append(check_python_version())
    results.append(check_package("requests"))
    results.append(check_package("beautifulsoup4", "bs4"))
    results.append(check_package("lxml"))
    results.append(check_package("pyyaml", "yaml"))
    results.append(check_package("playwright"))
    results.append(check_package("selenium"))
    results.append(check_package("pandas"))
    results.append(check_package("weasyprint"))
    
    print("\n🌐 Browser Automation:")
    results.append(check_playwright())
    
    print("\n⚙️ Configuration:")
    results.append(check_env_file())
    results.append(check_api_keys())
    results.append(check_directories())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\n🚀 Ready to run: ./seo audit https://example.com")
        return 0
    else:
        print(f"⚠️ {total - passed} issues found ({passed}/{total} passed)")
        print("\n📋 Fix issues and run: python scripts/verify_environment.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
