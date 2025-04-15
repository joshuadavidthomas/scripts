#!/usr/bin/env -S uv run --script
# adapted from @nicknisi's git-bare-clone script, found here:
# https://github.com/nicknisi/dotfiles/blob/662ec5c2bcd4a5fdfb4305d99e70af8f301f1983/bin/git-bare-clone
#
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
#     "typer",
#     "httpx",
# ]
# ///
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import httpx
import typer
from rich.console import Console

app = typer.Typer()
console = Console()
BARE_DIR = ".bare"
BIN_DIR = Path.home() / ".local/bin"
SCRIPT_NAME = "git-bare-clone"
SCRIPT_URL = "https://scripts.joshthomas.dev/git_bare_clone.py"


@app.command()
def install():
    """
    Install the script to ~/.local/bin/git-bare-clone for use as a git subcommand.
    """
    console.print(f"Installing {SCRIPT_NAME} to {BIN_DIR}...", style="yellow")

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    target_path = BIN_DIR / SCRIPT_NAME

    try:
        console.print(f"Downloading script from {SCRIPT_URL}...", style="blue")
        # Use httpx to download the script content
        with httpx.stream("GET", SCRIPT_URL, follow_redirects=True, timeout=30) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            with target_path.open("wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        console.print(f"Making script executable at {target_path}...", style="blue")
        # Set permissions to rwxr-xr-x (755)
        target_path.chmod(0o755)

        console.print(
            f"Successfully installed {SCRIPT_NAME} to {target_path}", style="green"
        )
        console.print(f"You can now run it using: git bare-clone <repository-url>", style="cyan")

    except httpx.RequestError as e:
        console.print(f"Error downloading script: {e}", style="red")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"An error occurred during installation: {e}", style="red")
        raise typer.Exit(code=1)


@app.command()
def clone(
    repository: str,
    location: Annotated[
        str, typer.Option(help="Location of the bare repo contents")
    ] = BARE_DIR,
):
    """
    Clone a bare git repo and set up environment for working comfortably and exclusively from worktrees.
    """

    location: Path = Path(location)

    console.print(f"Cloning bare repository to {location}...", style="yellow")
    subprocess.run(["git", "clone", "--bare", repository, location], check=True)

    console.print("Adjusting origin fetch locations...", style="yellow")
    subprocess.run(
        [
            "git",
            "config",
            "remote.origin.fetch",
            '"+refs/heads/*:refs/remotes/origin/*"',
        ],
        check=True,
        cwd=location,
    )

    console.print("Setting .git file contents...", style="yellow")
    dotgit_file = location.parent / ".git"
    dotgit_file.write_text(f"gitdir: ./{location}")

    console.print("Success.", style="green")


if __name__ == "__main__":
    app()
