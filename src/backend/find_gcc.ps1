$paths = @('C:\mingw64\bin','C:\msys64\mingw64\bin','C:\msys64\usr\bin','C:\Program Files\mingw-w64\mingw64\bin')
foreach ($p in $paths) {
    if (Test-Path $p) { Write-Output "FOUND:$p" }
}

Write-Output '--- Searching Downloads...'
Get-ChildItem -Path $env:USERPROFILE\Downloads -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'mingw|winlibs|msys|gcc' } | Select-Object -First 20 | ForEach-Object { Write-Output "DL:$($_.FullName)" }

Write-Output '--- Searching common roots C:\ and C:\Program Files x2 ---'
Get-ChildItem -Path C:\ -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'mingw|msys|winlibs|gcc' } | ForEach-Object { Write-Output "ROOT:$($_.FullName)" }
