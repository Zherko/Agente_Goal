param([switch]$Force)
$ErrorActionPreference="Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$destAgents = Join-Path $env:USERPROFILE ".config/opencode/agents"
$destSkills = Join-Path $env:USERPROFILE ".config/opencode/skills/goal"

Write-Host "Agente_Goal installer — $repoRoot -> $destAgents + $destSkills" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $destAgents | Out-Null
New-Item -ItemType Directory -Force -Path $destSkills | Out-Null

# agents/goal.md
$srcAgent = Join-Path $repoRoot ".opencode/agents/goal.md"
if (-not (Test-Path $srcAgent)) { $srcAgent = Join-Path $repoRoot "agents-goal.md" }
Copy-Item $srcAgent (Join-Path $destAgents "goal.md") -Force
Write-Host "  ✓ agents/goal.md" -ForegroundColor Green

# skills/goal/
$srcSkills = Join-Path $repoRoot ".opencode/skills/goal"
if (Test-Path $srcSkills) {
  Copy-Item -Recurse -Force "$srcSkills/*" $destSkills
  Write-Host "  ✓ skills/goal/ ($((Get-ChildItem $destSkills -Recurse -File).Count) files)" -ForegroundColor Green
} else {
  Write-Warning "No se encontró .opencode/skills/goal en el repo"
}

Write-Host "`nInstalado. Verifica con: opencode --agent Goal ""hola""  o  /goal ""..." )" -ForegroundColor Cyan
Write-Host "Estructura:" 
Get-ChildItem $destSkills | Select-Object Name | Format-Table -AutoSize | Out-String | Write-Host
