#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
#     "typer",
# ]
# ///
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer(
    help="Manage scripts from scripts.joshthomas.dev"
)
console = Console()

BIN_DIR = Path.home() / ".local/bin"
BASE_URL = "https://scripts.joshthomas.dev"

# Maps the desired command name (key) to the actual script filename (value)
SCRIPT_NAME_MAP = {
    "git-bare-clone": "git_bare_clone.py",
    "install-windsurf": "install_windsurf.py",
    # Add future scripts here, e.g.:
    # "my-other-script": "my_other_script.py",
}


@app.command()
def install(
    script_name: Annotated[
        str,
        typer.Argument(
            help=(
                "The name of the script to install (e.g., 'git-bare-clone')."
                " This will also be the command name."
            )
        ),
    ]
):
    """
    Install a script as an executable command in ~/.local/bin.

    This creates a small wrapper script that uses 'uv run'
    to execute the latest version of the script directly from the web.
    """
    console.print(f"Attempting to install '{script_name}'...", style="yellow")

    if script_name not in SCRIPT_NAME_MAP:
        console.print(
            f"Error: Unknown script name '{script_name}'.", style="red"
        )
        console.print("Available scripts for installation:")
        for name in SCRIPT_NAME_MAP:
            console.print(f"  - {name}")
        raise typer.Exit(code=1)

    filename = SCRIPT_NAME_MAP[script_name]
    script_url = f"{BASE_URL}/{filename}"
    target_path = BIN_DIR / script_name

    console.print(f"Target installation path: {target_path}", style="blue")
    console.print(f"Source script URL: {script_url}", style="blue")

    BIN_DIR.mkdir(parents=True, exist_ok=True)

    wrapper_content = f"""#!/bin/sh
# Generated wrapper for {script_name} by manage_scripts.py
# Executes the remote script using uv run

# Use --quiet to suppress uv's own output unless there's an error
exec uv run --quiet {script_url} "$@"
"""

    try:
        console.print(f"Writing wrapper script to {target_path}...", style="blue")
        with target_path.open("w", encoding="utf-8") as f:
            f.write(wrapper_content)

        console.print(f"Making script executable at {target_path}...", style="blue")
        # Set permissions to rwxr-xr-x (755)
        target_path.chmod(0o755)

        console.print(
            f"Successfully installed '{script_name}' to {target_path}",
            style="green",
        )
        console.print(
            f"Ensure '{BIN_DIR}' is in your PATH.", style="cyan"
        )
        console.print(
            f"You can now run the script using: {script_name} <args...>",
            style="cyan",
        )

    except Exception as e:
        console.print(f"An error occurred during installation: {e}", style="red")
        # Attempt to clean up partially created file
        if target_path.exists():
            try:
                target_path.unlink()
            except Exception as cleanup_e:
                console.print(f"Error during cleanup: {cleanup_e}", style="red")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
