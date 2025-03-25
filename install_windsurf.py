#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
#     "rich",
#     "typer",
# ]
# ///
"""
Windsurf Installation Script

This script installs the Windsurf editor to your home directory and sets up
automatic updates via systemd.
"""

import os
import sys
import shutil
import json
import tempfile
import subprocess
import inspect
from pathlib import Path
from typing import Any

import httpx
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(help="Install and manage Windsurf editor")

HOME_DIR = Path.home()
INSTALL_DIR = HOME_DIR / ".local/share/windsurf"
BIN_DIR = HOME_DIR / ".local/bin"
DESKTOP_DIR = HOME_DIR / ".local/share/applications"
SYSTEMD_DIR = HOME_DIR / ".config/systemd/user"
API_URL = "https://windsurf-stable.codeium.com/api/update/linux-x64/stable/latest"


def create_update_script() -> str:
    """Create the update script."""
    update_script_path = BIN_DIR / "update-windsurf"

    get_latest_version_info_source = inspect.getsource(get_latest_version_info)
    download_file_source = inspect.getsource(download_file)

    with update_script_path.open("w") as f:
        f.write(f'''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "httpx",
#     "rich",
# ]
# ///
"""
Windsurf Update Script

This script updates the Windsurf editor to the latest version.
"""

import os
import sys
import shutil
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Constants
HOME_DIR = Path.home()
INSTALL_DIR = HOME_DIR / ".local/share/windsurf"
API_URL = "https://windsurf-stable.codeium.com/api/update/linux-x64/stable/latest"


def get_current_version() -> str:
    """Get the current installed version of Windsurf."""
    product_json = INSTALL_DIR / "resources/app/product.json"

    if not product_json.exists():
        console.print("[red]Error: Windsurf installation not found.[/red]")
        sys.exit(1)

    with product_json.open() as f:
        data = json.load(f)

    return data.get("windsurfVersion", "unknown")


{get_latest_version_info_source}


{download_file_source}


def update_windsurf() -> None:
    """Update Windsurf to the latest version."""
    console.print("[bold]Windsurf Update[/bold]")

    # Check if Windsurf is installed
    if not INSTALL_DIR.exists():
        console.print("[red]Error: Windsurf installation not found at ~/.local/share/windsurf[/red]")
        sys.exit(1)

    # Get current version
    current_version = get_current_version()
    console.print(f"Current version: [green]{{current_version}}[/green]")

    # Get latest version information
    console.print("Checking for updates...")
    version_info = get_latest_version_info()
    remote_version = version_info.get("windsurfVersion", "unknown")
    download_url = version_info.get("url")

    console.print(f"Latest version: [green]{{remote_version}}[/green]")

    # Check if update is needed
    if current_version == remote_version:
        console.print("[green]Already running the latest version![/green]")
        return

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / "windsurf-latest.tar.gz"
        extract_path = temp_path / "windsurf-extract"
        extract_path.mkdir()

        # Download the latest version
        download_file(download_url, archive_path)

        # Extract the archive
        console.print("Extracting...")
        subprocess.run(
            ["tar", "-xzf", str(archive_path), "-C", str(extract_path)], check=True
        )

        # Check for top-level directory and adjust the extract_path if needed
        top_level_dirs = [item for item in extract_path.iterdir() if item.is_dir()]
        if len(top_level_dirs) == 1 and top_level_dirs[0].name == "Windsurf":
            # If the archive has a top-level "Windsurf" directory, use that as our source
            extract_path = top_level_dirs[0]

        # Install new version
        console.print("Installing...")

        # Clear the installation directory if it exists
        if INSTALL_DIR.exists():
            shutil.rmtree(str(INSTALL_DIR))

        # Create the installation directory
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)

        # Copy files from extracted directory to installation directory
        for item in extract_path.iterdir():
            if item.is_dir():
                shutil.copytree(str(item), str(INSTALL_DIR / item.name))
            else:
                shutil.copy2(str(item), str(INSTALL_DIR / item.name))

    console.print(f"[bold green]✅ Update complete![/bold green]")
    console.print(f"Windsurf updated from {{current_version}} to {{remote_version}}")

if __name__ == "__main__":
    update_windsurf()
''')

    update_script_path.chmod(0o755)
    return str(update_script_path)


def create_systemd_service() -> None:
    """Create the systemd service and timer for auto-updates."""
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)

    service_path = SYSTEMD_DIR / "windsurf-update.service"
    with service_path.open("w") as f:
        f.write(f"""[Unit]
Description=Update Windsurf Editor
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart={BIN_DIR}/update-windsurf
StandardOutput=journal

[Install]
WantedBy=default.target
""")

    timer_path = SYSTEMD_DIR / "windsurf-update.timer"
    with timer_path.open("w") as f:
        f.write("""[Unit]
Description=Check for Windsurf updates weekly

[Timer]
OnBootSec=10min
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
""")

    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(
            ["systemctl", "--user", "enable", "windsurf-update.timer"], check=True
        )
        subprocess.run(
            ["systemctl", "--user", "start", "windsurf-update.timer"], check=True
        )
        console.print("[green]Systemd timer enabled and started.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[yellow]Warning: Could not enable systemd timer: {e}[/yellow]")
        console.print("You can manually update using the update-windsurf script.")


def create_desktop_entry() -> None:
    """Create the desktop entry for Windsurf."""
    DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

    desktop_path = DESKTOP_DIR / "windsurf.desktop"
    with desktop_path.open("w") as f:
        f.write(f"""[Desktop Entry]
Name=Windsurf
Comment=Windsurf Code Editor
GenericName=Text Editor
Exec=windsurf %F
Icon={INSTALL_DIR}/resources/app/resources/linux/code.png
Type=Application
StartupNotify=true
StartupWMClass=windsurf
Categories=TextEditor;Development;IDE;
MimeType=text/plain;inode/directory;application/x-code-workspace;
Keywords=windsurf;editor;code;development;
""")

    console.print("[green]Desktop entry created.[/green]")


def create_launcher() -> None:
    """Create the launcher script for Windsurf."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    launcher_path = BIN_DIR / "windsurf"
    with launcher_path.open("w") as f:
        f.write(f"""#!/bin/bash
exec {INSTALL_DIR}/windsurf "$@"
""")

    # Make the launcher executable
    launcher_path.chmod(0o755)
    console.print("[green]Launcher script created at ~/.local/bin/windsurf[/green]")


def get_latest_version_info() -> dict[str, Any]:
    """Get information about the latest version from the API."""
    try:
        with httpx.Client() as client:
            response = client.get(API_URL)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        console.print(f"[red]Error connecting to update server: {e}[/red]")
        sys.exit(1)


def download_file(url: str, target_path: Path) -> None:
    """Download a file with progress bar."""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Downloading Windsurf...", total=None)

            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                with target_path.open("wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            progress.update(task, completed=True)
    except httpx.HTTPError as e:
        console.print(f"[red]Error downloading file: {e}[/red]")
        sys.exit(1)


@app.command()
def install(
    skip_systemd: bool = typer.Option(
        False, "--skip-systemd", help="Skip setting up systemd service"
    ),
    force: bool = typer.Option(
        False, "--force", help="Force installation even if already installed"
    ),
) -> None:
    """Install Windsurf editor and set up automatic updates."""
    console.print("[bold]Windsurf Installation[/bold]")

    # Check if Windsurf is already installed
    if INSTALL_DIR.exists() and not force:
        console.print("[yellow]Windsurf is already installed.[/yellow]")
        console.print("Use --force to reinstall.")
        return

    # Get latest version information
    console.print("Getting download information...")
    version_info = get_latest_version_info()
    version = version_info.get("windsurfVersion", "unknown")
    download_url = version_info.get("url")

    console.print(f"Installing Windsurf version: [green]{version}[/green]")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        archive_path = temp_path / "windsurf-latest.tar.gz"
        extract_path = temp_path / "windsurf-extract"
        extract_path.mkdir()

        # Download the latest version
        download_file(download_url, archive_path)

        # Extract the archive
        console.print("Extracting...")
        subprocess.run(
            ["tar", "-xzf", str(archive_path), "-C", str(extract_path)], check=True
        )

        # Check for top-level directory and adjust the extract_path if needed
        top_level_dirs = [item for item in extract_path.iterdir() if item.is_dir()]
        if len(top_level_dirs) == 1 and top_level_dirs[0].name == "Windsurf":
            # If the archive has a top-level "Windsurf" directory, use that as our source
            extract_path = top_level_dirs[0]

        # Install new version
        console.print("Installing...")

        # Clear the installation directory if it exists
        if INSTALL_DIR.exists():
            shutil.rmtree(str(INSTALL_DIR))

        # Create the installation directory
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)

        # Copy files from extracted directory to installation directory
        for item in extract_path.iterdir():
            if item.is_dir():
                shutil.copytree(str(item), str(INSTALL_DIR / item.name))
            else:
                shutil.copy2(str(item), str(INSTALL_DIR / item.name))

    # Create launcher script
    create_launcher()

    # Create desktop entry
    create_desktop_entry()

    # Create update script
    update_script = create_update_script()
    console.print(f"[green]Update script created at {update_script}[/green]")

    # Set up systemd service
    if not skip_systemd:
        create_systemd_service()

    # Add bin directory to PATH if not already there
    paths = os.environ.get("PATH", "").split(":")
    if str(BIN_DIR) not in paths:
        console.print(f"[yellow]Note: Make sure {BIN_DIR} is in your PATH.[/yellow]")
        console.print(
            "Add 'export PATH=\"$HOME/.local/bin:$PATH\"' to your shell profile."
        )

    console.print("[bold green]✅ Installation complete![/bold green]")
    console.print(
        "You can now run Windsurf by typing 'windsurf' or from your application menu."
    )


@app.command()
def version() -> None:
    """Display the current version of Windsurf if installed."""
    if not INSTALL_DIR.exists():
        console.print("[red]Error: Windsurf is not installed.[/red]")
        return

    product_json = INSTALL_DIR / "resources/app/product.json"
    if not product_json.exists():
        console.print("[red]Error: Cannot find version information.[/red]")
        return

    with product_json.open() as f:
        data = json.load(f)

    windsurf_version = data.get("windsurfVersion", "unknown")
    codeium_version = data.get("codeiumVersion", "unknown")
    vs_version = data.get("version", "unknown")

    console.print("[bold]Windsurf Version Information[/bold]")
    console.print(f"Windsurf: [green]{windsurf_version}[/green]")
    console.print(f"Codeium: [green]{codeium_version}[/green]")
    console.print(f"VS Core: [green]{vs_version}[/green]")


@app.command()
def update() -> None:
    """Update Windsurf to the latest version."""
    update_script = BIN_DIR / "update-windsurf"

    if not update_script.exists():
        console.print(
            "[red]Error: Update script not found. Please run the install command first.[/red]"
        )
        return

    subprocess.run([str(update_script)], check=True)


@app.command()
def uninstall(
    keep_config: bool = typer.Option(
        False, "--keep-config", help="Keep configuration files"
    ),
) -> None:
    """Uninstall Windsurf from the system."""
    console.print("[bold]Uninstalling Windsurf[/bold]")

    # Disable and stop systemd service
    try:
        subprocess.run(
            ["systemctl", "--user", "stop", "windsurf-update.timer"], check=False
        )
        subprocess.run(
            ["systemctl", "--user", "disable", "windsurf-update.timer"], check=False
        )
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
        console.print("[green]Systemd timer stopped and disabled.[/green]")
    except subprocess.CalledProcessError:
        pass

    # Remove systemd service files
    service_path = SYSTEMD_DIR / "windsurf-update.service"
    timer_path = SYSTEMD_DIR / "windsurf-update.timer"

    if service_path.exists():
        service_path.unlink()
    if timer_path.exists():
        timer_path.unlink()

    # Remove launcher script
    launcher_path = BIN_DIR / "windsurf"
    update_script_path = BIN_DIR / "update-windsurf"

    if launcher_path.exists():
        launcher_path.unlink()
        console.print("[green]Launcher script removed.[/green]")

    if update_script_path.exists():
        update_script_path.unlink()
        console.print("[green]Update script removed.[/green]")

    # Remove desktop entry
    desktop_path = DESKTOP_DIR / "windsurf.desktop"

    if desktop_path.exists():
        desktop_path.unlink()
        console.print("[green]Desktop entry removed.[/green]")

    # Remove installation
    if INSTALL_DIR.exists():
        shutil.rmtree(str(INSTALL_DIR))
        console.print("[green]Windsurf installation removed.[/green]")

    # Remove configuration
    if not keep_config:
        config_dir = HOME_DIR / ".config/windsurf"
        cache_dir = HOME_DIR / ".cache/windsurf"

        if config_dir.exists():
            shutil.rmtree(str(config_dir))
            console.print("[green]Configuration files removed.[/green]")

        if cache_dir.exists():
            shutil.rmtree(str(cache_dir))
            console.print("[green]Cache files removed.[/green]")

    console.print("[bold green]✅ Uninstallation complete![/bold green]")


if __name__ == "__main__":
    app()
