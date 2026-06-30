$bin='C:\msys64\mingw64\bin'
$current=[Environment]::GetEnvironmentVariable('Path','User')
if ($current -notmatch [regex]::Escape($bin)) {
    [Environment]::SetEnvironmentVariable('Path', "$current;$bin", 'User')
    Write-Output 'PATH updated (User)'
} else {
    Write-Output "PATH already contains $bin"
}

& "$bin\gcc.exe" --version
