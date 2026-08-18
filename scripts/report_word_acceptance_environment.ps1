param(
    [Parameter(Mandatory=$false)][string]$Output = "word-merge-evidence\word-environment.json"
)

$ErrorActionPreference = "Stop"
$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    $clickToRun = Get-ItemProperty `
        -Path "HKLM:\SOFTWARE\Microsoft\Office\ClickToRun\Configuration" `
        -ErrorAction SilentlyContinue
    $computer = Get-CimInstance Win32_OperatingSystem
    $outputPath = [System.IO.Path]::GetFullPath($Output)
    $outputDirectory = [System.IO.Path]::GetDirectoryName($outputPath)
    if ($outputDirectory) {
        [System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
    }

    $payload = [ordered]@{
        captured_at_utc = [DateTime]::UtcNow.ToString("o")
        windows_caption = $computer.Caption
        windows_version = $computer.Version
        windows_build = $computer.BuildNumber
        os_architecture = $computer.OSArchitecture
        powershell_version = $PSVersionTable.PSVersion.ToString()
        word_version = [string]$word.Version
        word_build = [string]$word.Build
        word_path = [string]$word.Path
        office_platform = if ($clickToRun) { [string]$clickToRun.Platform } else { "unknown" }
        office_version_to_report = if ($clickToRun) {
            [string]$clickToRun.VersionToReport
        } else {
            "unknown"
        }
    }

    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outputPath -Encoding UTF8
    Write-Output $outputPath
}
finally {
    if ($null -ne $word) {
        try { $word.Quit() } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
