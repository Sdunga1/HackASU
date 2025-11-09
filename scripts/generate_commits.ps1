# PowerShell script to help generate commits for demo tickets
# Usage: .\scripts\generate_commits.ps1 -TicketId "SCRUM-XXX" -Message "Commit message" -Date "2025-11-10 09:00:00"

param(
    [Parameter(Mandatory=$true)]
    [string]$TicketId,
    
    [Parameter(Mandatory=$true)]
    [string]$Message,
    
    [Parameter(Mandatory=$false)]
    [string]$Date
)

# Format commit message with ticket ID
$FullMessage = "$TicketId`: $Message"

# Create commit with optional date
if ($Date) {
    $env:GIT_AUTHOR_DATE = $Date
    $env:GIT_COMMITTER_DATE = $Date
    git commit -m $FullMessage
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
} else {
    git commit -m $FullMessage
}

Write-Host "✅ Created commit: $FullMessage" -ForegroundColor Green
if ($Date) {
    Write-Host "   Date: $Date" -ForegroundColor Gray
} else {
    Write-Host "   Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
}

