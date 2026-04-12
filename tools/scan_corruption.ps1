$root = "C:\Realms2Riches"

$patterns = @(
    "edge_all_open_tabs",
    "User's Edge browser tabs metadata",
    "<WebsiteContent_",
    "</WebsiteContent_",
    "tabId",
    "isCurrent",
    "pageTitle",
    "pageUrl"
)

Write-Host "Scanning for corruption..." -ForegroundColor Cyan

Get-ChildItem -Path $root -Recurse -File -Include *.js, *.jsx, *.ts, *.tsx, *.json, *.html, *.config | ForEach-Object {
    $file = $_.FullName
    $lines = Get-Content $file
    $cleaned = @()
    $skip = $false
    $modified = $false

    foreach ($line in $lines) {
        if ($patterns | Where-Object { $line -match $_ }) {
            $skip = $true
            $modified = $true
            continue
        }

        if ($skip -and $line.Trim() -eq "]") {
            $skip = $false
            continue
        }

        if (-not $skip) {
            $cleaned += $line
        }
    }

    if ($modified) {
        Copy-Item $file "$file.bak_before_cleanup" -ErrorAction SilentlyContinue
        Set-Content -Path $file -Value $cleaned -Encoding UTF8
        Write-Host "Cleaned: $file" -ForegroundColor Yellow
    }
}

Write-Host "Corruption scan complete." -ForegroundColor Green