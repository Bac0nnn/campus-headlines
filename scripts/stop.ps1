$ErrorActionPreference = 'Continue'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
$RunDir = Join-Path $Root '.run'

function Stop-Tree($processId, $label) {
  if (-not $processId) { return }
  $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
  if (-not $process) {
    Write-Host ("  " + $label + " 进程不存在，跳过")
    return
  }
  & taskkill.exe /PID $processId /T /F | Out-Null
  Write-Host ("  已停止 " + $label + "（PID " + $processId + "）") -ForegroundColor Yellow
}

Write-Host "正在停止校园头条服务…" -ForegroundColor Cyan

$backendPidFile = Join-Path $RunDir 'backend.pid'
if (Test-Path $backendPidFile) {
  $backendPid = [int](Get-Content $backendPidFile | Select-Object -First 1)
  $info = Get-CimInstance Win32_Process -Filter ("ProcessId=" + $backendPid) -ErrorAction SilentlyContinue
  if ($info -and $info.CommandLine -notlike '*campus-headlines*') {
    Write-Host "  跳过非本项目进程（PID $backendPid）" -ForegroundColor Yellow
  } else {
    Stop-Tree $backendPid '后端'
  }
  Remove-Item $backendPidFile -Force -ErrorAction SilentlyContinue
}

$frontendPidFile = Join-Path $RunDir 'frontend.pid'
if (Test-Path $frontendPidFile) {
  $frontendPid = [int](Get-Content $frontendPidFile | Select-Object -First 1)
  Stop-Tree $frontendPid '前端'
  Remove-Item $frontendPidFile -Force -ErrorAction SilentlyContinue
}

Write-Host "完成。" -ForegroundColor Green
