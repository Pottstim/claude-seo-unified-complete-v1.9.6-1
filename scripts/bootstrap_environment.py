#!/usr/bin/env python3
"""
Bootstrap script for first-time setup
Creates directories, copies config templates, guides API key setup
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create required directories"""
    dirs = [
        ".seo-cache",
        "output",
        "logs",
        "config/credentials",
        "assets",
    ]
    
    print("📁 Creating directories...")
    for d in dirs:
        path = Path(d)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}/")

def copy_config_templates():
    """Copy example configs to active configs"""
    templates = [
        ("config/config.example.yaml", "config/config.yaml"),
        ("config/.env.example", ".env"),
    ]
    
    print("\n⚙️ Copying configuration templates...")
    for src, dst in templates:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if dst_path.exists():
            print(f"  ⏭️ {dst} already exists (skipping)")
            continue
            
        if src_path.exists():
            shutil.copy(src_path, dst_path)
            print(f"  ✅ {src} → {dst}")
        else:
            print(f"  ⚠️ {src} not found")

def display_next_steps():
    """Show user what to do next"""
    print("\n" + "="*60)
    print("✅ Bootstrap complete!\n")
    print("📋 Next steps:\n")
    print("1. Edit .env file:")
    print("   - Add ANTHROPIC_API_KEY from https://console.anthropic.com")
    print("   - Add OPENAI_API_KEY from https://platform.openai.com/api-keys")
    print("")
    print("2. (Optional) Configure extensions:")
    print("   - DataForSEO: bash extensions/dataforseo/install.sh")
    print("   - Google APIs: bash extensions/google/install.sh")
    print("   - Firecrawl: bash extensions/firecrawl/install.sh")
    print("")
    print("3. Verify installation:")
    print("   python scripts/verify_environment.py")
    print("")
    print("4. Run your first audit:")
    print("   ./seo audit https://example.com")
    print("="*60)

def main():
    print("🚀 Claude SEO Unified - Bootstrap\n")
    
    create_directories()
    copy_config_templates()
    display_next_steps()
    
    return 0

if __name__ == "__main__":
    exit(main())
