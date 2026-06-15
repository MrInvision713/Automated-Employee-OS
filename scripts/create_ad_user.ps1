param (
    [string]$FirstName,
    [string]$LastName,
    [string]$Email,
    [string]$Department,
    [string]$JobTitle
)

$Username = ($FirstName.Substring(0,1) + $LastName).ToLower()
$DisplayName = "$FirstName $LastName"
$Password = ConvertTo-SecureString "TempPassword123!" -AsPlainText -Force

New-ADUser `
    -Name $DisplayName `
    -GivenName $FirstName `
    -Surname $LastName `
    -SamAccountName $Username `
    -UserPrincipalName $Email `
    -EmailAddress $Email `
    -Department $Department `
    -Title $JobTitle `
    -AccountPassword $Password `
    -Enabled $true `
    -ChangePasswordAtLogon $true `
    -Path "OU=NewHires,DC=company,DC=local"