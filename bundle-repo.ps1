$ErrorActionPreference = 'Stop'

$root = (Get-Location).Path
$outDir = Join-Path $root "_repo_bundle"
$bundleBase = "repo_bundle"
$maxBytes = 350000

$excludeDirs = @(
    '\.git\',
    '\node_modules\',
    '\dist\',
    '\build\',
    '\coverage\',
    '\.venv\',
    '\venv\',
    '\__pycache__\',
    '\target\',
    '\bin\',
    '\obj\',
    '\out\',
    '\.next\',
    '\.nuxt\',
    '\logs\',
    '\tmp\',
    '\temp\',
    '\uploads\',
    '\videos\',
    '\media\'
)

$excludeExtensions = @(
    '.mp4','.mov','.avi','.mkv','.webm',
    '.mp3','.wav','.flac','.ogg',
    '.png','.jpg','.jpeg','.gif','.bmp','.ico','.svg',
    '.pdf','.zip','.7z','.rar','.gz','.tar',
    '.exe','.dll','.so','.dylib',
    '.pyc','.pyo','.class',
    '.db','.sqlite','.sqlite3',
    '.woff','.woff2','.ttf','.otf',
    '.lock'
)

$specialNames = @(
    'Dockerfile',
    'Makefile',
    '.gitignore',
    '.dockerignore',
    '.env.example',
    '.env.local.example',
    'requirements.txt',
    'pyproject.toml',
    'package.json',
    'package-lock.json',
    'pnpm-lock.yaml',
    'yarn.lock',
    'docker-compose.yml',
    'docker-compose.yaml',
    'compose.yml',
    'compose.yaml',
    'tsconfig.json'
)

$textExts = @(
    '.ps1','.psm1','.psd1',
    '.py',
    '.js','.cjs','.mjs',
    '.ts','.tsx','.jsx',
    '.json',
    '.yml','.yaml',
    '.toml',
    '.ini','.cfg','.conf',
    '.md','.txt',
    '.html','.css','.scss',
    '.sql',
    '.sh','.bat','.cmd',
    '.xml',
    '.cs','.java','.go','.rs','.php','.rb',
    '.env',
    '.gitignore','.dockerignore'
)

function Test-ExcludedPath {
    param([string]$Path)
    foreach ($pattern in $excludeDirs) {
        if ($Path -like "*$pattern*") { return $true }
    }
    return $false
}

function Test-IncludeFile {
    param([System.IO.FileInfo]$File)

    if ($excludeExtensions -contains $File.Extension.ToLower()) { return $false }
    if ($specialNames -contains $File.Name) { return $true }
    if ($textExts -contains $File.Extension.ToLower()) { return $true }

    return $false
}

function Get-RelativePath {
    param([string]$FullPath, [string]$RootPath)
    return $FullPath.Substring($RootPath.Length).TrimStart('\')
}

function Redact-Line {
    param([string]$Line)

    $patterns = @(
        '(?i)^(\s*[A-Z0-9_]*?(KEY|SECRET|TOKEN|PASSWORD|PASS|LICENSE|API_KEY|PRIVATE_KEY)\s*=\s*)(.*)$',
        '(?i)^(\s*("?[A-Z0-9_]*?(KEY|SECRET|TOKEN|PASSWORD|PASS|LICENSE|API_KEY|PRIVATE_KEY)"?\s*:\s*"))([^"]*)(".*)$',
        "(?i)^(\s*('?[A-Z0-9_]*?(KEY|SECRET|TOKEN|PASSWORD|PASS|LICENSE|API_KEY|PRIVATE_KEY)'?\s*:\s*'))([^']*)('.*)$"
    )

    foreach ($pattern in $patterns) {
        if ($Line -match $pattern) {
            if ($matches.Count -ge 5) {
                return ($matches[1] + '[REDACTED]' + $matches[5])
            } else {
                return '[REDACTED LINE]'
            }
        }
    }

    return $Line
}

function Redact-Content {
    param([string]$Content)

    $lines = $Content -split "`r?`n"
    $redacted = foreach ($line in $lines) {
        Redact-Line $line
    }
    return ($redacted -join "`r`n")
}

if (Test-Path $outDir) {
    Remove-Item -Recurse -Force $outDir
}
New-Item -ItemType Directory -Path $outDir | Out-Null

$files = Get-ChildItem -Recurse -File |
    Where-Object { -not (Test-ExcludedPath $_.FullName) } |
    Where-Object { Test-IncludeFile $_ } |
    Sort-Object FullName

$allText = New-Object System.Text.StringBuilder
$manifest = New-Object System.Collections.Generic.List[object]

foreach ($file in $files) {
    $rel = Get-RelativePath -FullPath $file.FullName -RootPath $root
    $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash

    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        $content = Redact-Content $content
    }
    catch {
        $content = "[[READ ERROR: $($_.Exception.Message)]]"
    }

    $null = $allText.AppendLine("===== FILE: $rel =====")
    $null = $allText.AppendLine("SHA256: $hash")
    $null = $allText.AppendLine("SIZE: $($file.Length)")
    $null = $allText.AppendLine("----- BEGIN CONTENT -----")
    $null = $allText.AppendLine($content)
    $null = $allText.AppendLine("----- END CONTENT -----")
    $null = $allText.AppendLine()

    $manifest.Add([PSCustomObject]@{
        Path = $rel
        SHA256 = $hash
        Size = $file.Length
    })
}

$manifestPath = Join-Path $outDir "manifest.csv"
$manifest | Export-Csv -NoTypeInformation $manifestPath

$fullBundle = $allText.ToString()
$utf8 = [System.Text.UTF8Encoding]::new($false)
$bytes = $utf8.GetBytes($fullBundle)
$partCount = [Math]::Ceiling($bytes.Length / $maxBytes)

for ($i = 0; $i -lt $partCount; $i++) {
    $start = $i * $maxBytes
    $length = [Math]::Min($maxBytes, $bytes.Length - $start)
    $partBytes = New-Object byte[] $length
    [Array]::Copy($bytes, $start, $partBytes, 0, $length)

    $partPath = Join-Path $outDir ("{0}_{1:D3}.txt" -f $bundleBase, ($i + 1))
    [System.IO.File]::WriteAllBytes($partPath, $partBytes)
}

$readme = @"
Bundle created in: $outDir

Files included: $($files.Count)
Total bundle bytes: $($bytes.Length)
Parts created: $partCount

Upload these files:
- manifest.csv
- repo_bundle_001.txt, repo_bundle_002.txt, etc.
"@

$readmePath = Join-Path $outDir "README.txt"
$readme | Set-Content $readmePath

Write-Host ""
Write-Host "Done."
Write-Host "Bundle folder: $outDir"
Write-Host "Files included: $($files.Count)"
Write-Host "Parts created: $partCount"
Write-Host ""
Write-Host "Upload manifest.csv and all repo_bundle_*.txt files."