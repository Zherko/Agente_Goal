param([switch]$Force)
$ErrorActionPreference="Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$destAgents = Join-Path $env:USERPROFILE ".config/opencode/agents"
$destSkills = Join-Path $env:USERPROFILE ".config/opencode/skills/goal"

Write-Host "Agente_Goal installer â€” $repoRoot -> $destAgents + $destSkills" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $destAgents | Out-Null
New-Item -ItemType Directory -Force -Path $destSkills | Out-Null

# agents/goal.md
$srcAgent = Join-Path $repoRoot ".opencode/agents/goal.md"
if (-not (Test-Path $srcAgent)) { $srcAgent = Join-Path $repoRoot "agents-goal.md" }
Copy-Item $srcAgent (Join-Path $destAgents "goal.md") -Force
Write-Host "  âœ“ agents/goal.md" -ForegroundColor Green

# skills/goal/
$srcSkills = Join-Path $repoRoot ".opencode/skills/goal"
if (Test-Path $srcSkills) {
  Copy-Item -Recurse -Force "$srcSkills/*" $destSkills
  Write-Host "  âœ“ skills/goal/ ($((Get-ChildItem $destSkills -Recurse -File).Count) files)" -ForegroundColor Green
} else {
  Write-Warning "No se encontrÃ³ .opencode/skills/goal en el repo"
}

# dependencias: karpathy + team + skills sueltos
$srcKarpathy = Join-Path $repoRoot ".opencode/skills/karpathy-guidelines"
if (Test-Path $srcKarpathy) {
  $dstKarpathy = Join-Path (Join-Path $env:USERPROFILE ".config/opencode/skills") "karpathy-guidelines"
  New-Item -ItemType Directory -Force -Path $dstKarpathy | Out-Null
  Copy-Item -Recurse -Force "$srcKarpathy/*" $dstKarpathy
  Write-Host "  OK skills/karpathy-guidelines/" -ForegroundColor Green
}
$srcTeam = Join-Path $repoRoot ".opencode/agents/team.md"
if (Test-Path $srcTeam) { Copy-Item $srcTeam (Join-Path $destAgents "team.md") -Force; Write-Host "  OK agents/team.md" -ForegroundColor Green }
foreach($n in @("goal-committee","goal-discovery","goal-plan","goal-research","goal-test")){
  $s = Join-Path $repoRoot ".opencode/skills/$n"
  if(Test-Path $s){ $d=Join-Path (Join-Path $env:USERPROFILE ".config/opencode/skills") $n; New-Item -ItemType Directory -Force -Path $d | Out-Null; Copy-Item -Recurse -Force "$s/*" $d; Write-Host "  OK skills/$n/" -ForegroundColor Green }
}

Write-Host "
Instalado. Verifica con: opencode --agent Goal ""hola""  o  /goal ""..." )" -ForegroundColor Cyan
Write-Host "Estructura:" 
Get-ChildItem $destSkills | Select-Object Name | Format-Table -AutoSize | Out-String | Write-Host

