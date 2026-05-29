$base = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"
$files = @("ask-agent\Ask.agent.md","explore-agent\Explore.agent.md","plan-agent\Plan.agent.md")
foreach ($rel in $files) {
    $p   = Join-Path $base $rel
    $txt = [System.IO.File]::ReadAllText($p)
    $bad = ($txt -match "github/issue_read|issue_fetch|activePullRequest|Gemini 3 Flash")
    $ro  = (Get-ItemProperty $p).IsReadOnly
    Write-Host "$rel | bad=$bad | read-only=$ro"
}
