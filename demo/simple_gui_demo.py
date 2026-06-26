"""
Simple GUI demo using ANSA guitk (BC GUI Toolkit).

This script creates a window with:
- A label showing selected entities count
- A "Count Selected" button
- Standard OK/Cancel dialog buttons
"""

import ansa
from ansa import guitk, base, constants


def main():
    # ── Create window ──────────────────────────────────────────
    win = guitk.BCWindowCreate(
        "Simple Entity Counter",                    # Window title
        guitk.constants.BCOnExitDestroy             # Auto-destroy on close
    )

    # ── Create a label ─────────────────────────────────────────
    label = guitk.BCLabelCreate(
        win,                                         # Parent window
        "Click the button to count selected entities" # Label text
    )

    # ── Create a button ────────────────────────────────────────
    btn = guitk.BCPushButtonCreate(
        win,                                         # Parent window
        "Count Selected Entities",                   # Button text
        None,                                        # Callback (set later)
        None                                         # User data
    )

    # ── Create OK/Cancel button box ────────────────────────────
    dbb = guitk.BCDialogButtonBoxCreate(win)

    # ── Define button callback ─────────────────────────────────
    def on_count_clicked(button, data):
        """Count selected entities and update label text."""
        ents = base.GetSelectedEntities(
            constants.LSDYNA,                        # Deck type
            None                                     # All entity types
        )
        count = len(ents)
        guitk.BCLabelSetText(label, f"Selected entities: {count}")

    # ── Connect callback to button ─────────────────────────────
    guitk.BCButtonSetClickedFunction(btn, on_count_clicked, dbb)

    # ── Show window ────────────────────────────────────────────
    guitk.BCShow(win)


if __name__ == "__main__":
    main()
