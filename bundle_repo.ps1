$ErrorActionPreference = 'Stop'

$root = (Get-Location).Path
$outDir = Join-Path $root "_repo_bundle"
$bundleBase = "repo_bundle"
$maxBytes = 350000   # ~350 KB per part; adjust if needed

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
    '\.next\',
    '\out\'
)

$specialNames = @(
    'Dockerfile',
    'Makefile',
    '.gitignore',
    '.dockerignore',
    '.env.example',
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
    'tsconfig.json',
    'vite.config.ts',
    'vite.config.js'
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

    if ($specialNames -contains $File.Name) { return $true }
    if ($textExts -contains $File.Extension.ToLower()) { return $true }

    return $false
}

function Get-RelativePath {
    param([string]$FullPath, [string]$RootPath)
    return $FullPath.Substring($RootPath.Length).TrimStart('\')
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

$manifest |
    Export-Csv -NoTypeInformation (Join-Path $outDir "manifest.csv")

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

$summary = @"
Bundle created in: $outDir

Files included: $($files.Count)
Total bundle bytes: $($bytes.Length)
Parts created: $partCount

Upload:
- manifest.csv
- all repo_bundle_*.txt files
"@

$summary | Set-Content (Join-Path $outDir "README.txt")

Write-Host $summary