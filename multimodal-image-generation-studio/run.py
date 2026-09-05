"""Runner script to launch Multimodal Image Generation Studio via Streamlit."""

import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> None:
    """Launch the Streamlit web application."""
    project_root = Path(__file__).resolve().parent
    app_file = project_root / "streamlit_app.py"

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
    ] + sys.argv[1:]

    # Pass UTF-8 environment variables for Windows console safety
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    print("=" * 60)
    print("Launching Multimodal Image Generation Studio...")
    print(f"Project Root: {project_root}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as exc:
        print(f"\nError launching application: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
