$ErrorActionPreference = "Stop"
$base = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"

$bad = @(
    ", 'github/issue_read'",
    ", 'github.vscode-pull-request-github/issue_fetch'",
    ", 'github.vscode-pull-request-github/activePullRequest'",
    ", 'Gemini 3 Flash (Preview) (copilot)'"
)

$files = @(
    "ask-agent\Ask.agent.md",
    "explore-agent\Explore.agent.md",
    "plan-agent\Plan.agent.md"
)

# Step 1: Remove read-only if set, so we can write
foreach ($rel in $files) {
    $p = Join-Path $base $rel
    if (Test-Path $p) {
        Set-ItemProperty $p -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
    }
}

# Step 2: Fix content
foreach ($rel in $files) {
    $path = Join-Path $base $rel
    if (-not (Test-Path $path)) { continue }
    $content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    foreach ($token in $bad) { $content = $content.Replace($token, "") }
    $tmp = $path + ".tmp"
    [System.IO.File]::WriteAllText($tmp, $content, [System.Text.Encoding]::UTF8)
    [System.IO.File]::Copy($tmp, $path, $true)
    Remove-Item $tmp -ErrorAction SilentlyContinue
    Write-Host "Fixed: $rel" -ForegroundColor Green
}

# Step 3: Make read-only so VS Code extension cannot overwrite
foreach ($rel in $files) {
    $p = Join-Path $base $rel
    if (Test-Path $p) {
        Set-ItemProperty $p -Name IsReadOnly -Value $true
        Write-Host "Locked (read-only): $rel" -ForegroundColor Cyan
    }
}

Start-Sleep -Milliseconds 800

# Step 4: Verify
Write-Host ""
Write-Host "=== Verification ===" -ForegroundColor Yellow
$allClean = $true
foreach ($rel in $files) {
    $p = Join-Path $base $rel
    $txt = [System.IO.File]::ReadAllText($p)
    $hasBad = ($txt -match "github/issue_read|issue_fetch|activePullRequest|Gemini 3 Flash")
    $ro     = (Get-ItemProperty $p).IsReadOnly
    if ($hasBad) {
        Write-Host "  FAIL (still bad tokens): $rel" -ForegroundColor Red
        $allClean = $false
    } else {
        Write-Host "  PASS (clean, read-only=$ro): $rel" -ForegroundColor Green
    }
}

if ($allClean) {
    Write-Host ""
    Write-Host "All agent files are clean and locked. Now do:" -ForegroundColor Cyan
    Write-Host "  VS Code: Ctrl+Shift+P -> Developer: Reload Window" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Some files still have issues. Close VS Code and run again." -ForegroundColor Red
}
