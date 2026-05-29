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

foreach ($rel in $files) {
    $path = Join-Path $base $rel
    if (-not (Test-Path $path)) {
        Write-Warning "Not found: $path"
        continue
    }
    $content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    foreach ($token in $bad) {
        $content = $content.Replace($token, "")
    }
    $tmp = $path + ".tmp"
    [System.IO.File]::WriteAllText($tmp, $content, [System.Text.Encoding]::UTF8)
    [System.IO.File]::Copy($tmp, $path, $true)
    Remove-Item $tmp -ErrorAction SilentlyContinue
    Write-Host "Fixed: $rel" -ForegroundColor Green
}

Start-Sleep -Milliseconds 1000

Write-Host ""
Write-Host "Verification:" -ForegroundColor Cyan
foreach ($rel in $files) {
    $path = Join-Path $base $rel
    $txt  = [System.IO.File]::ReadAllText($path)
    $still_bad = ($txt -match "github/issue_read|issue_fetch|activePullRequest|Gemini 3 Flash")
    if ($still_bad) {
        Write-Host "  STILL BAD: $rel" -ForegroundColor Red
    } else {
        Write-Host "  CLEAN:     $rel" -ForegroundColor Green
    }
}
