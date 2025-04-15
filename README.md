# scripts

Scripts to run with `uv run`.

- [`install_windsurf`](#install_windsurf)
- [`git_bare_clone`](#git_bare_clone)
- [`manage_scripts`](#manage_scripts)

All scripts are licensed under the MIT license. See the [`LICENSE`](https://github.com/joshuadavidthomas/scripts/blob/main/LICENSE) file for more information.

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

## `git_bare_clone`

Clones a git repository as a bare repository, setting it up for a workflow centered around git worktrees. This approach keeps the main repository directory clean, containing only the git metadata, while your working files reside in separate worktrees. This script is adapted from [@nicknisi's git-bare-clone script](https://github.com/nicknisi/dotfiles/blob/662ec5c2bcd4a5fdfb4305d99e70af8f301f1983/bin/git-bare-clone).

Using a bare repository with worktrees offers several advantages:

- Cleaner project root directory.
- Easier management of multiple branches or features simultaneously.
- Avoids conflicts between the main working directory and worktrees.

### Installation

To install the script as a git subcommand (`git bare-clone`), run the following command. This will download the script and place it in `~/.local/bin`. Ensure `~/.local/bin` is in your `PATH`.
This uses the `manage_scripts` utility (see below).
```bash
# Installs 'git_bare_clone.py' as the command 'git-bare-clone'
uv run https://scripts.joshthomas.dev/manage_scripts.py install git-bare-clone
```

### Usage Options

**After Installation:**

```bash
# Basic usage (clones to .bare directory in current folder)
git bare-clone <repository-url>

# Clone to a custom directory relative to current folder
git bare-clone <repository-url> --location <custom-dir>
```

**Direct Execution (without installation):**

```bash
# Basic usage (clones to .bare directory)
uv run https://scripts.joshthomas.dev/git_bare_clone.py clone <repository-url>

# Clone to a custom directory
uv run https://scripts.joshthomas.dev/git_bare_clone.py clone <repository-url> --location <custom-dir>
```

## `manage_scripts`

A utility script to install other scripts from this repository as executable commands in your local environment (`~/.local/bin` by default).

Instead of downloading the script content itself, this installer creates a small shell wrapper. When you run the installed command (e.g., `git-bare-clone`), the wrapper uses `uv run` to execute the latest version of the script directly from `https://scripts.joshthomas.dev`. This ensures you're always using the most up-to-date version without needing manual updates.

### Usage

```bash
# Install the 'git-bare-clone' script as the command 'git-bare-clone'
uv run https://scripts.joshthomas.dev/manage_scripts.py install git-bare-clone

# Install the 'install-windsurf' script as the command 'install-windsurf'
uv run https://scripts.joshthomas.dev/manage_scripts.py install install-windsurf

# (Ensure ~/.local/bin is in your PATH to use the installed commands)
```
