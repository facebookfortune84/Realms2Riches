<#
.SYNOPSIS
    Configures a Windows Server 2025 VM as a DHCP Server for Realms2Riches.
    
.DESCRIPTION
    1. Installs DHCP Server feature and management tools.
    2. Authorizes the DHCP server in corp.realms2riches.com.
    3. Configures a scope (192.168.1.100 - 192.168.1.200).
    4. Creates a reservation for 192.168.1.101.
    5. Provides instructions for MAC discovery.

.PARAMETER TargetMACAddress
    The Physical Address (MAC) of the host machine to be reserved for 192.168.1.101.
    Format: 00-00-00-00-00-00 or 000000000000 or 00:00:00:00:00:00
#>

param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the MAC address of the target machine.")]
    [ValidateNotNullOrEmpty()]
    [string]$TargetMACAddress
)

$ErrorActionPreference = "Stop"

# Configuration Constants
$Domain = "corp.realms2riches.com"
$ScopeId = "192.168.1.0"
$ScopeName = "Realms2Riches-Internal"
$StartRange = "192.168.1.100"
$EndRange = "192.168.1.200"
$SubnetMask = "255.255.255.0"
$ReservationIP = "192.168.1.101"
$ReservationName = "Primary-Workstation"

Write-Host "🚀 INITIATING DHCP CONFIGURATION SEQUENCE" -ForegroundColor Cyan
Write-Host "Target Domain: $Domain" -ForegroundColor Gray
Write-Host "Target MAC:    $TargetMACAddress" -ForegroundColor Gray

# 1. Install DHCP Server Feature and Management Tools
try {
    Write-Host "`nStep 1: Installing DHCP Server Feature & RSAT Tools..." -ForegroundColor Gray
    $dhcpFeature = Get-WindowsFeature -Name DHCP
    if (-not $dhcpFeature.Installed) {
        Install-WindowsFeature -Name DHCP -IncludeManagementTools
        Write-Host "✅ DHCP Feature and Management Tools installed successfully." -ForegroundColor Green
    } else {
        Write-Host "ℹ️ DHCP Feature is already installed. Skipping." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ FAILED to install DHCP feature: $_" -ForegroundColor Red
    exit 1
}

# 2. Authorize DHCP Server in Active Directory
try {
    Write-Host "`nStep 2: Authorizing DHCP Server in $Domain..." -ForegroundColor Gray
    $serverFQDN = ([System.Net.Dns]::GetHostByName(($env:computername))).HostName
    
    # Check if authorization is already present
    $isAuthorized = $false
    try {
        $authorizedServers = Get-DhcpServerInDC
        if ($authorizedServers -any { $_.DnsName -eq $serverFQDN }) {
            $isAuthorized = $true
        }
    } catch {
        # Get-DhcpServerInDC might fail if no servers are authorized yet
        $isAuthorized = $false
    }

    if ($isAuthorized) {
        Write-Host "ℹ️ Server $serverFQDN is already authorized in AD. Skipping." -ForegroundColor Yellow
    } else {
        Add-DhcpServerInDC -DnsName $serverFQDN
        Write-Host "✅ DHCP Server $serverFQDN successfully authorized." -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Authorization check/action encountered an error: $_" -ForegroundColor Yellow
    Write-Host "   Attempting to continue. Ensure you have Domain Admin privileges." -ForegroundColor Gray
}

# 3. Create DHCPv4 Scope
try {
    Write-Host "`nStep 3: Creating DHCPv4 Scope ($StartRange - $EndRange)..." -ForegroundColor Gray
    $existingScopes = Get-DhcpServerv4Scope
    $scopeExists = $existingScopes | Where-Object { $_.ScopeId -eq $ScopeId -or ($_.StartRange -eq $StartRange -and $_.EndRange -eq $EndRange) }
    
    if ($scopeExists) {
        Write-Host "ℹ️ DHCP Scope already exists for this range. Skipping creation." -ForegroundColor Yellow
    } else {
        Add-DhcpServerv4Scope -Name $ScopeName -StartRange $StartRange -EndRange $EndRange -SubnetMask $SubnetMask -State Active
        Write-Host "✅ DHCP Scope '$ScopeName' created and activated." -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FAILED to create DHCP scope: $_" -ForegroundColor Red
    exit 1
}

# 4. Create DHCPv4 Reservation
try {
    Write-Host "`nStep 4: Binding $ReservationIP to MAC $TargetMACAddress..." -ForegroundColor Gray
    # Sanitize MAC Address for DHCP ClientId (remove delimiters)
    $cleanMAC = $TargetMACAddress -replace "[:-]", ""
    
    $existingReservations = Get-DhcpServerv4Reservation -ScopeId $ScopeId -ErrorAction SilentlyContinue
    $reservationExists = $existingReservations | Where-Object { $_.IPAddress -eq $ReservationIP -or $_.ClientId -eq $cleanMAC }
    
    if ($reservationExists) {
        Write-Host "ℹ️ Reservation for IP $ReservationIP or MAC $cleanMAC already exists. Skipping." -ForegroundColor Yellow
    } else {
        Add-DhcpServerv4Reservation -ScopeId $ScopeId -IPAddress $ReservationIP -ClientId $cleanMAC -Description "Reserved for $ReservationName"
        Write-Host "✅ DHCP Reservation created for $ReservationIP." -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FAILED to create DHCP reservation: $_" -ForegroundColor Red
    exit 1
}

# 5. Instructions for User
Write-Host "`n"
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " HOW TO FIND YOUR MAC ADDRESS ON THE HOST MACHINE" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "1. On your PHYSICAL host machine (not the VM), open PowerShell."
Write-Host "2. Execute the following command:"
Write-Host "   Get-NetAdapter | Select-Object Name, InterfaceDescription, MacAddress" -ForegroundColor Yellow
Write-Host "3. Look for the 'MacAddress' column for your active network adapter."
Write-Host "   (Format will look like: 00-15-5D-01-CA-02)"
Write-Host "4. Alternatively, run 'ipconfig /all' and look for 'Physical Address'."
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`n✅ DHCP CONFIGURATION COMPLETE." -ForegroundColor Green
