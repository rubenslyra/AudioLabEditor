param(
    [switch]$System
)

$ErrorActionPreference = "Stop"
$AppName = "AudioLabEditor"
$BinaryName = "AudioLabEditor.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$BinaryPath = Join-Path $RootDir "dist" $BinaryName

if (-not (Test-Path $BinaryPath)) {
    Write-Error "Build nao encontrado em $BinaryPath. Execute 'python -m PyInstaller scripts/AudioLabEditor.spec' primeiro."
    exit 1
}

if ($System) {
    $InstallDir = Join-Path $env:ProgramFiles $AppName
} else {
    $InstallDir = Join-Path $env:LOCALAPPDATA $AppName
}

Write-Host "==> Instalando em ${InstallDir}..."
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item $BinaryPath (Join-Path $InstallDir $BinaryName) -Force

$InstallDir = $InstallDir.Replace('"', '""')
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$InstallDir*") {
    $NewPath = "$InstallDir;$UserPath"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "==> Adicionado ao PATH do usuario"
}

$ShortcutPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\${AppName}.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $InstallDir $BinaryName
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "AudioLab Editor — Capture, edite e separe audio e video com IA"

$IcoPath = Join-Path $RootDir "src\presentation\assets\logo.ico"
if (Test-Path $IcoPath) {
    $Shortcut.IconLocation = $IcoPath
}
$Shortcut.Save()

Write-Host ""
Write-Host "==> Instalacao concluida!"
Write-Host "    Executavel: $InstallDir\$BinaryName"
Write-Host "    Atalho no menu Iniciar como '${AppName}'"
Write-Host ""
Write-Host "    Use '${AppName}' no terminal ou busque no menu Iniciar."
Write-Host "    Para desinstalar, remova o diretorio e o atalho manualmente."
