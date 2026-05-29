Start-Sleep -Seconds 4
$base = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"
$files = @("ask-agent\Ask.agent.md","explore-agent\Explore.agent.md","plan-agent\Plan.agent.md")
foreach ($rel in $files) {
    $txt = [System.IO.File]::ReadAllText((Join-Path $base $rel))
    $bad = ($txt -match "github/issue_read|issue_fetch|activePullRequest|Gemini 3 Flash")
    if ($bad) { Write-Host "REVERTED: $rel" -ForegroundColor Red }
    else       { Write-Host "STILL CLEAN: $rel" -ForegroundColor Green }
}
