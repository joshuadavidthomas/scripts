#!/usr/bin/env -S uv run --script
# adapted from @nicknisi's git-bare-clone script, found here:
# https://github.com/nicknisi/dotfiles/blob/662ec5c2bcd4a5fdfb4305d99e70af8f301f1983/bin/git-bare-clone
#
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
#     "typer",
# ]
# ///
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

app = typer.Typer()
console = Console()
BARE_DIR = ".bare"


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
