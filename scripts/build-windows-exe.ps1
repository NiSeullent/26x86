Param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$pyiArgs = @(
    "--noconfirm",
    "--distpath", "dist",
    "--workpath", "build",
    "26x86-Windows.spec"
)

if ($Clean) {
    $pyiArgs += "--clean"
}

python -m PyInstaller @pyiArgs

$exePath = Join-Path $root "dist/26x86/26x86.exe"
if (-not (Test-Path $exePath)) {
    throw "Build succeeded but EXE not found: $exePath"
}

Write-Host "Windows EXE build complete: $exePath"
