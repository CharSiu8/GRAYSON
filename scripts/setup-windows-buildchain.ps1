<#
One-click Windows build-chain installer (PowerShell)

What this does:

IMPORTANT:

Usage (run in an elevated PowerShell):
    cd <project-root>
    .\scripts\setup-windows-buildchain.ps1
#>

function Ensure-RunningAsAdmin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
        Write-Host "Relaunching with elevation..." -ForegroundColor Yellow
        # Try PowerShell Core (pwsh) then fallback to Windows PowerShell (powershell.exe)
        $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
        if ($pwsh) {
            Start-Process -FilePath $pwsh.Source -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath) -Verb RunAs
        } else {
            Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$PSCommandPath) -Verb RunAs
        }
        Exit 0
    }
}

Ensure-RunningAsAdmin

Set-StrictMode -Version Latest

$TempDir = Join-Path $env:TEMP "grayson_build"
if (-not (Test-Path $TempDir)) { New-Item -ItemType Directory -Path $TempDir | Out-Null }

function Download-File($url, $dest) {
    Write-Host "Downloading $url -> $dest"
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -TimeoutSec 600
        return $true
    } catch {
        Write-Host "Failed to download $url : $_" -ForegroundColor Red
        return $false
    }
}

try {
    # 1) Visual Studio Build Tools
    $vsExe = Join-Path $TempDir "vs_BuildTools.exe"
    $vsUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    if (-not (Test-Path $vsExe)) { Download-File -url $vsUrl -dest $vsExe | Out-Null }

    if (Test-Path $vsExe) {
        Write-Host "Installing Visual Studio Build Tools (C++ workload). This can take a while..." -ForegroundColor Cyan
        $vsArgs = @('--quiet','--wait','--norestart','--nocache','--installPath','C:\BuildTools','--add','Microsoft.VisualStudio.Workload.VCTools','--add','Microsoft.VisualStudio.Component.Windows10SDK.19041.NativeTools')
        Start-Process -FilePath $vsExe -ArgumentList $vsArgs -Wait -NoNewWindow
        Write-Host "Visual Studio Build Tools install finished (check installer output)." -ForegroundColor Green
    } else {
        Write-Host "VS Build Tools download failed; skipping." -ForegroundColor Yellow
    }

    # 2) rustup (Rust toolchain)
    $rustExe = Join-Path $TempDir "rustup-init.exe"
    $rustUrl = "https://win.rustup.rs"
    if (-not (Test-Path $rustExe)) { Download-File -url $rustUrl -dest $rustExe | Out-Null }
    if (Test-Path $rustExe) {
        Write-Host "Installing Rust toolchain (rustup + stable)" -ForegroundColor Cyan
        Start-Process -FilePath $rustExe -ArgumentList "-y" -Wait -NoNewWindow
        Write-Host "Rust installer finished." -ForegroundColor Green
    } else {
        Write-Host "Rust installer download failed; skipping." -ForegroundColor Yellow
    }

    # 3) Optional: CMake + Ninja via winget
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing CMake and Ninja via winget (requires winget)" -ForegroundColor Cyan
        Start-Process -FilePath winget -ArgumentList "install --id Kitware.CMake -e --silent" -NoNewWindow -Wait
        Start-Process -FilePath winget -ArgumentList "install --id NinjaBuild.Ninja -e --silent" -NoNewWindow -Wait
        Write-Host "winget installs completed (if available)." -ForegroundColor Green
    } else {
        Write-Host "winget not found; skipping CMake/Ninja installation. Consider installing them manually." -ForegroundColor Yellow
    }

    # 4) Update current session PATH for cargo (best-effort)
    $cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
    if (Test-Path $cargoBin) {
        if ($env:PATH -notlike "*$cargoBin*") {
            $env:PATH = "$env:PATH;$cargoBin"
            Write-Host "Added $cargoBin to PATH for this session." -ForegroundColor Green
        }
    }

    Write-Host ""; Write-Host "Build toolchain installation script finished." -ForegroundColor Cyan
    Write-Host "Important next steps:" -ForegroundColor Yellow
    Write-Host " - Close and reopen your PowerShell/terminal so PATH changes take effect." -ForegroundColor Yellow
    Write-Host " - Activate your venv and run: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host " - If you use cl.exe (MSVC compiler), you may need to run the 'x64 Native Tools Command Prompt for VS 2022' or run vcvars64.bat from the Build Tools install." -ForegroundColor Yellow

} catch {
    Write-Host "Error during setup: $_" -ForegroundColor Red
    Exit 1
}

Exit 0
