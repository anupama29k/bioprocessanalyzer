"""Atlas viewer: loads the release (GitHub or bundled snapshot) and renders every tab."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from streamlit.testing.v1 import AppTest

SCRIPT = """
import sys; sys.path.insert(0, %r)
from views import atlas
atlas.render()
""" % str(Path(__file__).parent)


def run(latest):
    at = AppTest.from_string(SCRIPT, default_timeout=120)
    at.run()
    if not latest:
        at.toggle[0].set_value(False).run()
    assert not at.exception, at.exception
    cap = " ".join(c.value for c in at.caption)
    assert ("latest release" in cap) if latest else ("bundled snapshot" in cap), cap
    assert at.metric[1].value == "77", at.metric[1].value
    for i, camp in enumerate(at.selectbox[0].options):
        at.selectbox[0].set_value(camp).run()
        assert not at.exception, (camp, at.exception)
    return at


if __name__ == "__main__":
    ok = 0
    for latest in (False, True):
        try:
            run(latest); ok += 1; print("PASS", "github" if latest else "bundled")
        except AssertionError as e:
            print("FAIL", "github" if latest else "bundled", e)
    from views.atlas import REL, FILES
    missing = [f for f in FILES if not (REL / f).exists()]
    print("PASS snapshot complete" if not missing else f"FAIL missing {missing}"); ok += not missing
    print(f"{ok}/3 passed"); sys.exit(ok != 3)
