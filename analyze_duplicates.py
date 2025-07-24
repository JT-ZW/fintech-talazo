#!/usr/bin/env python3
# analyze_duplicates.py
"""
Analyze duplicate files and directories in the Talazo AgriFinance Platform.
"""

import os
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).parent

def analyze_structure():
    """Analyze the current directory structure for duplicates."""
    print("=" * 60)
    print("📊 STRUCTURE ANALYSIS - Talazo AgriFinance Platform")
    print("=" * 60)
    
    # Check for duplicate directories
    print("\n📁 DIRECTORY ANALYSIS:")
    print("-" * 30)
    
    app_dir = ROOT_DIR / "app"
    talazo_dir = ROOT_DIR / "talazo"
    
    if app_dir.exists() and talazo_dir.exists():
        print("⚠️  DUPLICATE STRUCTURES FOUND:")
        print(f"   New structure: app/ ({len(list(app_dir.rglob('*.py')))} Python files)")
        print(f"   Old structure: talazo/ ({len(list(talazo_dir.rglob('*.py')))} Python files)")
        
        # Compare subdirectories
        app_subdirs = set(d.name for d in app_dir.iterdir() if d.is_dir())
        talazo_subdirs = set(d.name for d in talazo_dir.iterdir() if d.is_dir())
        
        common_dirs = app_subdirs & talazo_subdirs
        if common_dirs:
            print(f"   📂 Common subdirectories: {', '.join(common_dirs)}")
    
    # Check for duplicate files
    print("\n📄 FILE ANALYSIS:")
    print("-" * 30)
    
    # Files that exist in both app/ and root or talazo/
    potential_duplicates = [
        ("app.py", "app/__init__.py", "Root app.py vs new app factory"),
        ("config.py", "app/core/config.py", "Root config vs new config"),
        ("models.py", "app/models/", "Monolithic models vs modular models"),
        ("routes.py", "app/api/", "Monolithic routes vs API blueprints")
    ]
    
    for old_file, new_location, description in potential_duplicates:
        old_path = ROOT_DIR / old_file
        if old_path.exists():
            print(f"⚠️  {description}")
            print(f"   Old: {old_file}")
            print(f"   New: {new_location}")
    
    # Static and template files
    print("\n📊 STATIC & TEMPLATE FILES:")
    print("-" * 30)
    
    static_files = list(ROOT_DIR.glob("*.js")) + list(ROOT_DIR.glob("*.html")) + list(ROOT_DIR.glob("*.css"))
    if static_files:
        print("⚠️  Root-level web files found (should be in app/static/ or app/templates/):")
        for f in static_files:
            print(f"   {f.name}")
    
    # Database and model files
    print("\n🗄️  DATABASE & MODEL FILES:")
    print("-" * 30)
    
    db_files = list(ROOT_DIR.glob("*.db")) + list(ROOT_DIR.glob("*.pkl"))
    if db_files:
        print("📋 Model/database files found:")
        for f in db_files:
            print(f"   {f.name} ({f.stat().st_size} bytes)")
    
    # Build artifacts
    print("\n🏗️  BUILD ARTIFACTS:")
    print("-" * 30)
    
    build_dirs = [d for d in ROOT_DIR.iterdir() if d.is_dir() and d.name.endswith(('.egg-info', '__pycache__'))]
    if build_dirs:
        print("🧹 Build artifacts found (can be removed):")
        for d in build_dirs:
            print(f"   {d.name}/")
    
    print("\n" + "=" * 60)
    print("📋 RECOMMENDATIONS:")
    print("=" * 60)
    print("1. ✅ Keep: app/ directory (new organized structure)")
    print("2. 🗑️  Remove: talazo/ directory (old structure)")  
    print("3. 🗑️  Remove: Root-level duplicates (app.py, config.py, etc.)")
    print("4. 📁 Move: Static files to app/static/")
    print("5. 📁 Move: Templates to app/templates/")
    print("6. 📁 Move: ML models to app/ml_models/")
    print("7. 🧹 Clean: Build artifacts and cache files")
    print("=" * 60)

if __name__ == "__main__":
    analyze_structure()
