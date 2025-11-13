<#
.SYNOPSIS
    A basic PowerShell script for 'soft' hardening a Windows system.
    Applies foundational security settings.

.NOTES
    *** DANGER: DO NOT RUN ON A PRODUCTION SYSTEM WITHOUT TESTING! ***
    Always test these settings in a virtual machine or isolated lab environment first.
    Run this script with Administrator privileges.
#>

Write-Host "Starting basic Windows hardening script..." -ForegroundColor Yellow

# --- 1. Enable Windows Defender Firewall ---
Write-Host "[+] Enabling Windows Defender Firewall for all profiles..."
# The firewall is your first line of defense against network-based attacks.
Set-NetFirewallProfile -Profile Domain, Private, Public -Enabled True
Write-Host "    ...Firewall enabled."

# --- 2. Enable Enhanced PowerShell Logging ---
Write-Host "[+] Enabling PowerShell Module Logging and Script Block Logging..."
# This is crucial for defenders. It logs what scripts are run and what
# modules are used, helping you detect malicious PowerShell activity.
$ModuleLogPath = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging'
$ScriptBlockLogPath = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging'

If (-not (Test-Path $ModuleLogPath)) { New-Item -Path $ModuleLogPath -Force | Out-Null }
Set-ItemProperty -Path $ModuleLogPath -Name EnableModuleLogging -Value 1 -Force
Set-ItemProperty -Path $ModuleLogPath -Name ModuleNames -Value '*' -Force

If (-not (Test-Path $ScriptBlockLogPath)) { New-Item -Path $ScriptBlockLogPath -Force | Out-Null }
Set-ItemProperty -Path $ScriptBlockLogPath -Name EnableScriptBlockLogging -Value 1 -Force
Write-Host "    ...PowerShell logging enhanced."

# --- 3. Disable SMBv1 (Known vulnerable protocol) ---
Write-Host "[+] Disabling SMBv1 protocol..."
# SMBv1 is an outdated protocol with known vulnerabilities (e.g., exploited by WannaCry).
# This is one of the most important hardening steps.
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart
Write-Host "    ...SMBv1 disabled. A restart may be required to complete."

# --- 4. Enable Basic Audit Policies ---
Write-Host "[+] Enabling basic audit policies for logon and process creation..."
# This logs successful/failed logins and tracks every process that is started.
# This data is essential for threat hunting and incident response.
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Detailed Tracking" /subcategory:"Process Creation" /success:enable
Write-Host "    ...Audit policies set. (Check Event Viewer)"

# --- 5. Harden Remote Desktop (RDP) ---
Write-Host "[+] Requiring Network Level Authentication (NLA) for RDP..."
# If RDP is enabled, this forces authentication before a full session
# is established, mitigating some RDP brute-force and denial-of-service attacks.
$RDPPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp"
Set-ItemProperty -Path $RDPPath -Name "UserAuthentication" -Value 1 -Force
Write-Host "    ...NLA for RDP is now required."

# --- 6. Disable LM Hash Storage (Insecure) ---
Write-Host "[+] Disabling LM hash storage for better password security..."
# LM hash is an old, weak password hashing algorithm that is easily cracked.
# This registry key prevents Windows from storing it.
$LMHashPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa"
Set-ItemProperty -Path $LMHashPath -Name "NoLMHash" -Value 1 -Force
Write-Host "    ...LM hash storage disabled."

Write-Host "Basic hardening script completed." -ForegroundColor Green
Write-Host "Please review the output and consider a system restart for all changes to apply." -ForegroundColor Yellow
