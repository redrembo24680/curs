Write-Host "=== Встановлення залежностей для курсового проєкту ==="

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "1) Python залежності (Flask фронтенд)"
pip install -r (Join-Path $repo "web_flask\requirements.txt")

Write-Host "2) Підготовка CMake build для C++ сервера"
$buildDir = Join-Path $repo "server_cpp\build"
if (!(Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}

Push-Location $buildDir
cmake ..
Pop-Location

Write-Host "Готово! Можна запускати start_all.ps1"










