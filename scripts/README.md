# scripts/ - Utility Scripts

<!--
================================================================================
WHAT THIS FILE IS:
README for the scripts/ directory explaining utility and setup scripts.

WHY YOU NEED IT:
- Documents available scripts and their purposes
- Provides usage instructions for each script
- Helps developers set up their environment correctly
- Shows the project includes helpful automation
================================================================================
-->

## Overview

This directory contains utility scripts for setting up and maintaining the GRAYSON development environment.

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup-windows-buildchain.ps1` | Windows build tools installer |

## Script Descriptions

### `setup-windows-buildchain.ps1`

A one-click PowerShell script that installs the complete Windows build toolchain required for compiling Python packages with native dependencies (like ChromaDB's Rust components).

**What it installs:**
- Visual Studio Build Tools (C++ workload)
- Rust toolchain (rustup + stable)
- CMake and Ninja (via winget, if available)

**Requirements:**
- Windows 10/11
- Administrator privileges
- Internet connection

**Usage:**
```powershell
# Open PowerShell as Administrator
cd C:\path\to\grayson
.\scripts\setup-windows-buildchain.ps1
```

**After running:**
1. Close and reopen your terminal for PATH changes
2. Activate your virtual environment
3. Run `pip install -r requirements.txt`

**Note:** This script auto-elevates to Administrator if not already running with admin privileges.

## Adding New Scripts

When adding utility scripts:

1. **Document the purpose** at the top of the script
2. **Include usage examples** in comments
3. **Handle errors gracefully** with informative messages
4. **Update this README** with the new script

## Cross-Platform Considerations

- `.ps1` files are PowerShell scripts (Windows)
- `.sh` files are Bash scripts (macOS/Linux)
- Consider providing both when possible
- Use the `Makefile` in the project root for cross-platform task automation
