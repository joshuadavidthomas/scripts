# scripts

Scripts to run with `uv run`.

## `install_windsurf`

Installs the [Windsurf editor](https://codeium.com/windsurf) from Codium to `$HOME/.local/share`. This script provides a convenient way to install Windsurf on Linux systems without using the deb package or manually extracting the tarball.

This script:

 - Downloads and installs the latest version of Windsurf from the official API
 - Creates a desktop entry for easy access through your application menu
 - Sets up a launcher script in ~/.local/bin for command-line access
 - Configures automatic weekly updates via systemd (optional)
 - Provides commands for version checking, manual updates, and uninstallation

### Usage Options

```bash
# Basic installation
uv run https://scripts.joshthomas.dev/install_windsurf.py install

# Skip systemd auto-update setup
uv run https://scripts.joshthomas.dev/install_windsurf.py install --skip-systemd

# Force reinstallation
uv run https://scripts.joshthomas.dev/install_windsurf.py install --force

# Check current version
uv run https://scripts.joshthomas.dev/install_windsurf.py version

# Update to latest version
uv run https://scripts.joshthomas.dev/install_windsurf.py update

# Uninstall Windsurf
uv run https://scripts.joshthomas.dev/install_windsurf.py uninstall

# Uninstall but keep configuration files
uv run https://scripts.joshthomas.dev/install_windsurf.py uninstall --keep-config
```
