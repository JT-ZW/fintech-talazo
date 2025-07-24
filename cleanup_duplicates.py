#!/usr/bin/env python3
# cleanup_duplicates.py
"""
Cleanup script to remove duplicate files and organize the Talazo AgriFinance Platform.

This script will:
1. Remove the old 'talazo/' directory structure
2. Remove duplicate root-level files
3. Consolidate templates and static files
4. Clean up build artifacts
5. Update any remaining references
"""

import os
import shutil
import sys
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent

def backup_important_files():
    """Backup any important files before cleanup."""
    backup_dir = ROOT_DIR / "backup_before_cleanup"
    backup_dir.mkdir(exist_ok=True)
    
    important_files = [
        "talazo/talazo.db",  # Database file
        "yield_model.pkl",   # ML model
    ]
    
    for file_path in important_files:
        source = ROOT_DIR / file_path
        if source.exists():
            dest = backup_dir / source.name
            shutil.copy2(source, dest)
            print(f"✓ Backed up: {file_path}")

def remove_duplicate_directories():
    """Remove duplicate directory structures."""
    dirs_to_remove = [
        "talazo",  # Old structure
        "talazo.egg-info",
        "talazo_agrifinance.egg-info",
        "__pycache__"
    ]
    
    for dir_name in dirs_to_remove:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Removed directory: {dir_name}")
            except Exception as e:
                print(f"⚠ Could not remove {dir_name}: {e}")

def remove_duplicate_files():
    """Remove duplicate files in root directory."""
    files_to_remove = [
        "app.py",  # Old monolithic app
        "app_factory.py",  # Duplicate of app/__init__.py
        "config.py",  # Duplicate of app/core/config.py
        "demo.py",  # Covered by app/services/data_generator.py
        "demo_server.py",  # Not needed
        "farm_viability_scorer.py",  # Moved to app/services/
        "soil_health_algorithm.js",  # JavaScript version, keep for frontend
        "dashboard-loader.js",  # Will be moved to static/
        "dashboard.html",  # Will be moved to templates/
        "dashboard.js",  # Will be moved to static/
        "missing_classes.js",  # Will be moved to static/
        "test_reorganization.py",  # Old test file
        "yield_model.pkl"  # Will be moved to proper location
    ]
    
    for file_name in files_to_remove:
        file_path = ROOT_DIR / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"✓ Removed file: {file_name}")
            except Exception as e:
                print(f"⚠ Could not remove {file_name}: {e}")

def consolidate_static_files():
    """Move static files to the proper app structure."""
    # Create app static directory if it doesn't exist
    app_static = ROOT_DIR / "app" / "static"
    app_static.mkdir(exist_ok=True)
    
    # Move JavaScript files
    js_files = [
        "dashboard.js",
        "dashboard-loader.js", 
        "missing_classes.js",
        "soil_health_algorithm.js"
    ]
    
    js_dir = app_static / "js"
    js_dir.mkdir(exist_ok=True)
    
    for js_file in js_files:
        source = ROOT_DIR / js_file
        if source.exists():
            dest = js_dir / js_file
            try:
                shutil.move(str(source), str(dest))
                print(f"✓ Moved {js_file} to app/static/js/")
            except Exception as e:
                print(f"⚠ Could not move {js_file}: {e}")
    
    # Copy existing static files if any
    root_static = ROOT_DIR / "static"
    if root_static.exists():
        try:
            # Copy contents rather than replace directory
            for item in root_static.iterdir():
                if item.is_file():
                    dest = app_static / item.name
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    dest_dir = app_static / item.name
                    if not dest_dir.exists():
                        shutil.copytree(item, dest_dir)
            print("✓ Consolidated static files")
        except Exception as e:
            print(f"⚠ Error consolidating static files: {e}")

def consolidate_templates():
    """Move template files to the proper app structure."""
    # Create app templates directory if it doesn't exist
    app_templates = ROOT_DIR / "app" / "templates"
    app_templates.mkdir(exist_ok=True)
    
    # Move HTML files
    html_files = ["dashboard.html"]
    
    for html_file in html_files:
        source = ROOT_DIR / html_file
        if source.exists():
            dest = app_templates / html_file
            try:
                shutil.move(str(source), str(dest))
                print(f"✓ Moved {html_file} to app/templates/")
            except Exception as e:
                print(f"⚠ Could not move {html_file}: {e}")
    
    # Copy existing templates if any
    root_templates = ROOT_DIR / "templates"
    if root_templates.exists():
        try:
            for item in root_templates.iterdir():
                if item.is_file():
                    dest = app_templates / item.name
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    dest_dir = app_templates / item.name
                    if not dest_dir.exists():
                        shutil.copytree(item, dest_dir)
            print("✓ Consolidated template files")
        except Exception as e:
            print(f"⚠ Error consolidating templates: {e}")

def move_models():
    """Move ML models to proper location."""
    models_dir = ROOT_DIR / "app" / "ml_models"
    models_dir.mkdir(exist_ok=True)
    
    model_files = ["yield_model.pkl"]
    
    for model_file in model_files:
        source = ROOT_DIR / model_file
        if source.exists():
            dest = models_dir / model_file
            try:
                shutil.move(str(source), str(dest))
                print(f"✓ Moved {model_file} to app/ml_models/")
            except Exception as e:
                print(f"⚠ Could not move {model_file}: {e}")

def cleanup_remaining_artifacts():
    """Clean up remaining build artifacts and cache files."""
    patterns_to_clean = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        ".pytest_cache"
    ]
    
    for pattern in patterns_to_clean:
        for path in ROOT_DIR.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"✓ Cleaned: {path.relative_to(ROOT_DIR)}")
            except Exception as e:
                print(f"⚠ Could not clean {path}: {e}")

def update_remaining_files():
    """Update any remaining files that might reference old paths."""
    print("\n📝 Files that might need manual review:")
    
    # Files that might need updating
    files_to_check = [
        ".gitignore",
        "setup.py", 
        "README.md",
        "migrations/env.py"
    ]
    
    for file_name in files_to_check:
        file_path = ROOT_DIR / file_name
        if file_path.exists():
            print(f"   - {file_name}")

def main():
    """Main cleanup function."""
    print("=" * 60)
    print("🧹 TALAZO AGRIFINANCE - DUPLICATE CLEANUP")
    print("=" * 60)
    print("This script will clean up duplicate files and directories.")
    print("Make sure you have committed any important changes to git first!")
    print("=" * 60)
    
    response = input("Continue with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("Cleanup cancelled.")
        return
    
    print("\n1. Backing up important files...")
    backup_important_files()
    
    print("\n2. Consolidating static files...")
    consolidate_static_files()
    
    print("\n3. Consolidating templates...")
    consolidate_templates()
    
    print("\n4. Moving ML models...")
    move_models()
    
    print("\n5. Removing duplicate directories...")
    remove_duplicate_directories()
    
    print("\n6. Removing duplicate files...")
    remove_duplicate_files()
    
    print("\n7. Cleaning up artifacts...")
    cleanup_remaining_artifacts()
    
    print("\n8. Checking remaining files...")
    update_remaining_files()
    
    print("\n" + "=" * 60)
    print("🎉 CLEANUP COMPLETE!")
    print("=" * 60)
    print("Next steps:")
    print("1. Review the files listed above for any needed updates")
    print("2. Test the application: python run.py")
    print("3. Run tests: python test_reorganized_app.py")
    print("4. Commit the cleaned structure to git")
    print("=" * 60)

if __name__ == "__main__":
    main()
