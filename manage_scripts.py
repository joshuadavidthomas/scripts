#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
#     "typer",
# ]
# ///
from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import Prompt

app = typer.Typer(
    help="Manage scripts from scripts.joshthomas.dev"
)
console = Console()

BIN_DIR = Path.home() / ".local/bin"
BASE_URL = "https://scripts.joshthomas.dev"

AVAILABLE_SCRIPTS = [
    "git-bare-clone",
    "install-windsurf",
    # Add future command names here
]


def _install_single_script(script_name: str) -> bool:
    """Installs a single script and returns True on success, False on failure."""
    console.print(f"\nAttempting to install '{script_name}'...", style="yellow")

    if script_name not in AVAILABLE_SCRIPTS:
        console.print(
            f"Error: Unknown script name '{script_name}'. Skipping.", style="red"
        )
        console.print("Available scripts:", AVAILABLE_SCRIPTS)
        return False

    # Derive filename: replace '-' with '_' and add '.py'
    filename = script_name.replace("-", "_") + ".py"
    script_url = f"{BASE_URL}/{filename}"
    target_path = BIN_DIR / script_name

    console.print(f"  Target installation path: {target_path}", style="blue")
    console.print(f"  Source script URL: {script_url}", style="blue")

    BIN_DIR.mkdir(parents=True, exist_ok=True)

    wrapper_content = f"""#!/bin/sh
# Generated wrapper for {script_name} by manage_scripts.py
# Executes the remote script using uv run

# Use --quiet to suppress uv's own output unless there's an error
exec uv run --quiet {script_url} "$@"
"""

    try:
        console.print(f"  Writing wrapper script to {target_path}...", style="blue")
        with target_path.open("w", encoding="utf-8") as f:
            f.write(wrapper_content)

        console.print(f"  Making script executable at {target_path}...", style="blue")
        # Set permissions to rwxr-xr-x (755)
        target_path.chmod(0o755)

        console.print(
            f"Successfully installed '{script_name}' to {target_path}",
            style="green",
        )
        return True

    except Exception as e:
        console.print(
            f"An error occurred during installation of '{script_name}': {e}",
            style="red",
        )
        # Attempt to clean up partially created file
        if target_path.exists():
            try:
                target_path.unlink()
                console.print(f"  Cleaned up partially created file: {target_path}", style="yellow")
            except Exception as cleanup_e:
                console.print(f"  Error during cleanup: {cleanup_e}", style="red")
        return False


@app.command()
def install(
    script_names: Annotated[
        list[str] | None,  # Allow None
        typer.Argument(
            help=(
                "One or more script names to install (e.g., 'git-bare-clone')."
                " If none are provided, an interactive prompt will be shown."
            ),
            metavar="SCRIPT_NAME",
        ),
    ] = None,  # Default to None to detect if arguments were passed
):
    """
    Install one or more scripts as executable commands in ~/.local/bin.

    Creates small wrapper scripts that use 'uv run' to execute the
    latest version of the script directly from the web.
    """
    selected_scripts: list[str] = []
    available_scripts = AVAILABLE_SCRIPTS # Use the new list directly

    if not script_names:
        # No arguments provided, show interactive prompt
        console.print(
            "\nAvailable scripts for installation:",
            style="yellow",
        )
        for i, script in enumerate(available_scripts, 1):
            console.print(f"  [bold cyan]{i}[/]: {script}")

        while not selected_scripts:
            raw_selection = Prompt.ask(
                "\nEnter the numbers of the scripts to install (comma-separated, e.g., 1,3)"
            )
            try:
                indices = [
                    int(n.strip()) - 1
                    for n in raw_selection.split(",")
                    if n.strip()
                ]
                valid_indices = [
                    idx for idx in indices if 0 <= idx < len(available_scripts)
                ]
                invalid_indices = [
                    idx + 1 for idx in indices if idx not in valid_indices
                ]

                if invalid_indices:
                    console.print(
                        f"Warning: Invalid numbers ignored: {invalid_indices}",
                        style="yellow",
                    )

                if not valid_indices:
                    console.print(
                        "No valid script numbers entered. Please try again.",
                        style="red",
                    )
                    continue  # Ask again

                # Get script names based on valid indices
                potential_scripts = [
                    available_scripts[idx] for idx in valid_indices
                ]
                # Remove duplicates while preserving order
                selected_scripts = list(dict.fromkeys(potential_scripts))

            except ValueError:
                console.print(
                    "Invalid input. Please enter numbers separated by commas.",
                    style="red",
                )
                # Loop will continue to ask again

        if not selected_scripts: # Should not happen if loop exits correctly, but safety check
            console.print("No scripts selected. Exiting.", style="yellow")
            raise typer.Exit()
    else:
        # Use arguments provided, remove duplicates
        selected_scripts = list(dict.fromkeys(script_names))

    console.print(
        f"\nSelected scripts for installation: {selected_scripts}",
        style="bold blue",
    )

    success_count = 0
    fail_count = 0

    for name in selected_scripts:
        if _install_single_script(name):
            success_count += 1
        else:
            fail_count += 1

    console.print("\n--- Installation Summary ---", style="bold")
    console.print(f"Successfully installed: {success_count}", style="green")
    console.print(f"Failed installations: {fail_count}", style="red")

    if success_count > 0:
        console.print(
            f"\nEnsure '{BIN_DIR}' is in your system's PATH.", style="cyan"
        )
        console.print(
            "You can now run the installed script(s) using their names.",
            style="cyan",
        )

    if fail_count > 0:
        sys.exit(1) # Exit with error code if any installation failed


if __name__ == "__main__":
    app()
