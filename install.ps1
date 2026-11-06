param([switch]$Force)
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg      = Join-Path $env:USERPROFILE ".config/opencode"
$dstAgents   = Join-Path $cfg "agents"
$dstSkills   = Join-Path $cfg "skills"
$dstCommands = Join-Path $cfg "commands"

Write-Host "Agente_Goal -> $cfg" -ForegroundColor Cyan

foreach ($d in @($dstAgents, $dstSkills, $dstCommands)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

# --- memoria del usuario: se conserva siempre
$memFiles = @("memory.md", "memory/current.md", "memory/lessons.md", "memory/INDEX.md")
$backup = Join-Path $env:TEMP "agente-goal-mem-backup"
Remove-Item $backup -Recurse -Force -ErrorAction SilentlyContinue
foreach ($f in $memFiles) {
    $p = Join-Path (Join-Path $dstSkills "goal") $f
    if (Test-Path $p) {
        $b = Join-Path $backup $f
        New-Item -ItemType Directory -Force -Path (Split-Path $b) | Out-Null
        Copy-Item $p $b -Force
    }
}

# --- agente
foreach ($a in @("goal.md", "team.md")) {
    $s = Join-Path $repoRoot ".opencode/agents/$a"
    if (Test-Path $s) {
        Copy-Item $s (Join-Path $dstAgents $a) -Force
        Write-Host "  OK agents/$a" -ForegroundColor Green
    }
}

# --- skills (goal + dependencias)
$skills = @(
    "goal", "goal-committee", "goal-discovery", "goal-plan",
    "goal-research", "goal-test", "goal-wait", "karpathy-guidelines"
)
foreach ($s in $skills) {
    $src = Join-Path $repoRoot ".opencode/skills/$s"
    if (-not (Test-Path $src)) { Write-Warning "falta skills/$s"; continue }
    $dst = Join-Path $dstSkills $s
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Recurse -Force "$src/*" $dst
    Write-Host "  OK skills/$s/" -ForegroundColor Green
}

# --- restaurar memoria previa
if (Test-Path $backup) {
    foreach ($f in $memFiles) {
        $b = Join-Path $backup $f
        if (Test-Path $b) {
            $d = Join-Path (Join-Path $dstSkills "goal") $f
            New-Item -ItemType Directory -Force -Path (Split-Path $d) | Out-Null
            Copy-Item $b $d -Force
        }
    }
    Write-Host "  OK memoria previa conservada" -ForegroundColor Green
}

# --- comandos
Get-ChildItem (Join-Path $repoRoot ".opencode/commands") -Filter *.md -File | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $dstCommands $_.Name) -Force
    Write-Host "  OK commands/$($_.Name)" -ForegroundColor Green
}

# --- comprobaciones
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Warning "python no encontrado: /goal-dashboard no arrancara (el resto funciona)."
} else {
    Write-Host "  OK python -> /goal-dashboard disponible" -ForegroundColor Green
}

$n = (Get-ChildItem (Join-Path $dstSkills "goal") -Recurse -File | Measure-Object).Count
Write-Host ""
Write-Host "Instalado: $n archivos en skills/goal, comandos en commands/." -ForegroundColor Cyan
Write-Host "Prueba:  opencode  ->  /goal `"algo`"   |   /goal-dashboard   |   /goal-autoresearch"
