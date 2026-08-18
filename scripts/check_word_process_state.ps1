param(
    [Parameter(Mandatory=$true)][ValidateSet("before", "after")][string]$Phase,
    [Parameter(Mandatory=$false)][string]$Output = "word-merge-evidence\word-process-state.json"
)

$ErrorActionPreference = "Stop"

if ($Phase -eq "after") {
    Start-Sleep -Seconds 2
}

$processes = @(Get-Process -Name WINWORD -ErrorAction SilentlyContinue)
$outputPath = [System.IO.Path]::GetFullPath($Output)
$outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
if ($outputDirectory) {
    [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
}

$payload = [ordered]@{
    captured_at_utc = [DateTime]::UtcNow.ToString("o")
    phase = $Phase
    winword_process_count = $processes.Count
    clean = ($processes.Count -eq 0)
}

$payload | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $outputPath -Encoding UTF8
Write-Output $outputPath

if ($processes.Count -gt 0) {
    $processIds = ($processes | ForEach-Object { $_.Id }) -join ", "
    throw "WINWORD process state is not clean during '$Phase' acceptance check. Process IDs: $processIds"
}
