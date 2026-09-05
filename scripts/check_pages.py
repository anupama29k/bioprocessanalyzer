from pathlib import Path
import sys

# Make existing app modules importable (same logic as synapse.py)
_here = Path(__file__).resolve().parent.parent
_bpa_dir = _here / "bpa_app"
_adb_dir = _here / "analytical_databank"

for p in (_bpa_dir, _adb_dir):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

def main():
    try:
        import synapse_pages.live_run as live_run  # noqa: F401
        import synapse_pages.instrument_reference as instrument_reference  # noqa: F401
        import synapse_pages.batch_history as batch_history  # noqa: F401
        print("Imported synapse pages: OK")
    except Exception:
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
