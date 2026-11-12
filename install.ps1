# digi4school-summarizer - one-command installer (Windows PowerShell)
# Copies the skill into %USERPROFILE%\.claude\skills\ and installs the Python deps
# used for Word output. After this, restart Claude and type /digi4school-summarizer.
$ErrorActionPreference = "Stop"

$src      = Join-Path $PSScriptRoot "skills\digi4school-summarizer"
$destRoot = Join-Path $HOME ".claude\skills"
$dest     = Join-Path $destRoot "digi4school-summarizer"

Write-Host "Installing digi4school-summarizer..."

if (-not (Test-Path (Join-Path $src "SKILL.md"))) {
  Write-Error "Could not find skills\digi4school-summarizer\SKILL.md next to this script."
  exit 1
}

New-Item -ItemType Directory -Force -Path $destRoot | Out-Null
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
Copy-Item -Recurse -Force $src $destRoot
Write-Host "Skill installed to $dest"

# Python deps (only needed for Word/PDF output)
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if ($py) {
  & $py.Source -c "import docx, PIL" 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "Python deps (python-docx, Pillow) already present"
  } else {
    Write-Host "Installing Python deps (python-docx, Pillow)..."
    & $py.Source -m pip install --user --quiet python-docx Pillow
    if ($LASTEXITCODE -eq 0) { Write-Host "Python deps installed" }
    else { Write-Host "Could not auto-install. Run:  pip install python-docx Pillow" }
  }
} else {
  Write-Host "python not found. Install Python 3, then:  pip install python-docx Pillow"
}

Write-Host ""
Write-Host "Done. Restart Claude, then type:  /digi4school-summarizer"
