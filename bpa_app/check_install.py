"""
Run this first to diagnose and fix the startup crash:
    python check_install.py
"""
import subprocess, sys

required = [
    "streamlit",
    "pandas",
    "numpy",
    "plotly",
    "scipy",
    "scikit-learn",
    "openpyxl",
    "xlrd",
    "anthropic",
]

print("Checking installed packages...\n")
missing = []
for pkg in required:
    try:
        __import__(pkg.replace("-","_"))
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} — MISSING")
        missing.append(pkg)

if missing:
    print(f"\nInstalling {len(missing)} missing package(s)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    print("\n✅ All packages installed. Now run:  streamlit run app.py")
else:
    print("\n✅ All packages present.")
    print("\nTrying to import app modules...")
    import importlib.util, os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for mod_file in ["modules/session.py", "modules/calcs.py", "modules/ui_styles.py"]:
        spec = importlib.util.spec_from_file_location("mod", mod_file)
        mod  = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            print(f"  ✅ {mod_file}")
        except Exception as e:
            print(f"  ❌ {mod_file}: {e}")

    print("\nIf all ✅ — run:  streamlit run app.py")
