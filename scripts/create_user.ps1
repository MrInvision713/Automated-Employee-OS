param (
    [string]$FirstName,
    [string]$LastName,
    [string]$Email,
    [string]$Department
)

$LogMessage = @"
Creating onboarding user:
Name: $FirstName $LastName
Email: $Email
Department: $Department
Timestamp: $(Get-Date)
-------------------------------
"@

Add-Content -Path "scripts/onboarding.log" -Value $LogMessage
