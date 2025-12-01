@echo off
setlocal
set ROOT=%~dp0
cd /d "%ROOT%server_cpp"

if not exist build mkdir build
cd build

if not exist CMakeCache.txt (
    cmake .. || goto :error
)

cmake --build . --config Release || goto :error

set "BACKEND_EXE=bin\Release\voting_server.exe"
if not exist "%BACKEND_EXE%" (
    if exist "Release\voting_server.exe" (
        set "BACKEND_EXE=Release\voting_server.exe"
    ) else (
        echo voting_server.exe not found.
        goto :error
    )
)

"%BACKEND_EXE%"
goto :eof

:error
echo Backend start failed.
pause
goto :eof