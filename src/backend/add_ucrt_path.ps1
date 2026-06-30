$bin='C:\msys64\ucrt64\bin'
$current=[Environment]::GetEnvironmentVariable('Path','User')
if ($current -notmatch [regex]::Escape($bin)) {
    [Environment]::SetEnvironmentVariable('Path', "$current;$bin", 'User')
    Write-Output 'PATH updated (User)'
} else {
    Write-Output "PATH already contains $bin"
}

# run gcc directly
$gcc = Join-Path $bin 'gcc.exe'
if (Test-Path $gcc) {
    & $gcc --version
} else {
    Write-Output "gcc.exe NOT FOUND at $bin"
}
