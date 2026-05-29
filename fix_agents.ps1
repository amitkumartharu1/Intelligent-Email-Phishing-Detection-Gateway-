# fix_agents.ps1
# Run this script ONCE with VS Code fully closed.
# It removes unsupported tool/model names from GitHub Copilot Chat agent files.
# After running, reopen VS Code — no further action needed.

$ErrorActionPreference = "Stop"

$files = @{
    "ask-agent\Ask.agent.md"     = $null
    "explore-agent\Explore.agent.md" = $null
    "plan-agent\Plan.agent.md"   = $null
}

$base = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"

$removals = @(
    ", 'github/issue_read'",
    ", 'github.vscode-pull-request-github/issue_fetch'",
    ", 'github.vscode-pull-request-github/activePullRequest'",
    ", 'Gemini 3 Flash (Preview) (copilot)'"
)

foreach ($rel in $files.Keys) {
    $path = Join-Path $base $rel
    if (-not (Test-Path $path)) {
        Write-Warning "Not found: $path"
        continue
    }
    $content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    foreach ($token in $removals) {
        $content = $content.Replace($token, "")
    }
    [System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
    Write-Host "Fixed: $rel" -ForegroundColor Green
}

Write-Host "`nAll agent files fixed. Reopen VS Code." -ForegroundColor Cyan
