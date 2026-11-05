param(
  [switch]$Reset,
  [switch]$NoBrowser,
  [switch]$SkipBuild,
  [switch]$Reinstall
)

$ErrorActionPreference = 'Continue'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
Set-Location $Root

$BackendDir = Join-Path $Root 'backend'
if (-not (Test-Path $BackendDir)) { $BackendDir = Join-Path $Root '后端代码' }
$FrontendDir = Join-Path $Root 'frontend'
if (-not (Test-Path $FrontendDir)) { $FrontendDir = Join-Path $Root '前端代码' }
$SqlDir = Join-Path $Root 'sql'
if (-not (Test-Path $SqlDir)) { $SqlDir = Join-Path $Root '数据库' }

$LogDir = Join-Path $Root 'logs'
$RunDir = Join-Path $Root '.run'
New-Item -ItemType Directory -Force -Path $LogDir, $RunDir | Out-Null

function Step($message) { Write-Host ""; Write-Host "==> $message" -ForegroundColor Cyan }
function Info($message) { Write-Host "    $message" -ForegroundColor Gray }
function Fail($message) {
  Write-Host ""
  Write-Host "[失败] $message" -ForegroundColor Red
  exit 1
}

# ---------- 1. 读取 .env ----------
$envFile = Join-Path $Root '.env'
if (Test-Path $envFile) {
  Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
      $name = $matches[1]
      $value = $matches[2]
      if ($value.StartsWith('"') -and $value.EndsWith('"') -and $value.Length -ge 2) {
        $value = $value.Substring(1, $value.Length - 2)
      }
      Set-Item -Path ('env:' + $name) -Value $value
    }
  }
}

if (-not $env:DB_HOST) { $env:DB_HOST = '127.0.0.1' }
if (-not $env:DB_PORT) { $env:DB_PORT = '3306' }
if (-not $env:DB_NAME) { $env:DB_NAME = 'campus_headlines' }
if (-not $env:DB_USER) { $env:DB_USER = 'root' }
if (-not $env:DB_PASSWORD) { $env:DB_PASSWORD = '123456' }
if (-not $env:BACKEND_PORT) { $env:BACKEND_PORT = '8080' }
if (-not $env:FRONTEND_PORT) { $env:FRONTEND_PORT = '5173' }

Step '检查运行环境'

# ---------- 2. JDK 17 ----------
$java = $null
$javaCandidates = @()
if ($env:JAVA_HOME) { $javaCandidates += (Join-Path $env:JAVA_HOME 'bin\java.exe') }
$javaCandidates += 'C:\Program Files\Java\jdk-17\bin\java.exe'
$javaCmd = Get-Command java.exe -ErrorAction SilentlyContinue
if ($javaCmd) { $javaCandidates += $javaCmd.Source }
foreach ($candidate in $javaCandidates) {
  if ($candidate -and (Test-Path $candidate)) {
    $versionText = (& $candidate -version 2>&1) -join ' '
    if ($versionText -match 'version "17\.') { $java = $candidate; break }
  }
}
if (-not $java) { Fail '未找到 JDK 17。请安装 JDK 17，并在 .env 中设置 JAVA_HOME。' }
$env:JAVA_HOME = Split-Path -Parent (Split-Path -Parent $java)
Info ("JDK: " + ((& $java -version 2>&1) -join ' '))

# ---------- 3. Maven ----------
$maven = $null
$mvnCmd = Get-Command mvn.cmd -ErrorAction SilentlyContinue
if ($mvnCmd) { $maven = $mvnCmd.Source }
$mavenCandidates = @()
if ($env:MAVEN_HOME) { $mavenCandidates += (Join-Path $env:MAVEN_HOME 'bin\mvn.cmd') }
$mavenCandidates += 'C:\tools\apache-maven-3.9.9\bin\mvn.cmd'
$mavenCandidates += (Get-ChildItem (Join-Path $Root 'tools\apache-maven-*\bin\mvn.cmd') -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
if (-not $maven) {
  foreach ($candidate in $mavenCandidates) {
    if ($candidate -and (Test-Path $candidate)) { $maven = $candidate; break }
  }
}
if (-not $maven) { Fail '未找到 Maven。请安装 Maven 3.6+，并在 .env 中设置 MAVEN_HOME。' }
Info ("Maven: " + $maven)

# ---------- 4. MySQL 8.0 ----------
$mysql = $null
$mysqlCandidates = @()
if ($env:MYSQL_BIN) { $mysqlCandidates += $env:MYSQL_BIN }
$mysqlCmd = Get-Command mysql.exe -ErrorAction SilentlyContinue
if ($mysqlCmd) { $mysqlCandidates += $mysqlCmd.Source }
$mysqlCandidates += 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
$mysqlCandidates += 'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe'
$mysqlCandidates += (Get-ChildItem 'F:\MySQL\8.0\*\bin\mysql.exe' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
$mysqlCandidates += (Get-ChildItem 'D:\MySQL\8.0\*\bin\mysql.exe' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
foreach ($candidate in $mysqlCandidates) {
  if ($candidate -and (Test-Path $candidate)) {
    $mysqlVersion = (& $candidate --version 2>&1) -join ' '
    if ($mysqlVersion -match '8\.0\.') { $mysql = $candidate; break }
  }
}
if (-not $mysql) { Fail '未找到 MySQL 8.0 客户端。请安装 MySQL 8.0，并在 .env 中设置 MYSQL_BIN。' }
Info ("MySQL: " + ((& $mysql --version 2>&1) -join ' '))

# ---------- 5. Node / npm ----------
$npmCmd = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npmCmd) { $npmCmd = Get-Command npm -ErrorAction SilentlyContinue }
if (-not $npmCmd) { Fail '未找到 Node.js / npm，请安装 Node 18 或 20 LTS。' }
$nodeCmd = Get-Command node.exe -ErrorAction SilentlyContinue
if ($nodeCmd) { Info ("Node: " + (& $nodeCmd.Source -v)) }
Info ("npm: " + $npmCmd.Source)

$mysqlArgs = @('-h', $env:DB_HOST, '-P', $env:DB_PORT, '-u', $env:DB_USER, '--default-character-set=utf8mb4')
if ($env:DB_PASSWORD) { $mysqlArgs += ('-p' + $env:DB_PASSWORD) }

function Invoke-MysqlQuery($sql) {
  $output = & $mysql @mysqlArgs -N -e $sql 2>$null
  if ($LASTEXITCODE -ne 0) { Fail 'MySQL 连接失败，请检查 .env 中的 DB_USER / DB_PASSWORD。' }
  return $output
}

function Import-SqlFile($file) {
  $errFile = Join-Path $LogDir 'mysql-import.log'
  $process = Start-Process -FilePath $mysql -ArgumentList $mysqlArgs -RedirectStandardInput $file -RedirectStandardError $errFile -NoNewWindow -Wait -PassThru
  if ($process.ExitCode -ne 0) {
    if (Test-Path $errFile) { Get-Content $errFile -Tail 20 | ForEach-Object { Write-Host $_ -ForegroundColor Red } }
    Fail ('SQL 导入失败: ' + $file)
  }
}

# ---------- 6. 数据库初始化 ----------
Step '初始化数据库'

if ($Reset) {
  Write-Host '    -Reset 已启用：即将删除并重建数据库 ' -NoNewline
  Write-Host $env:DB_NAME -ForegroundColor Yellow
  Invoke-MysqlQuery ("DROP DATABASE IF EXISTS " + $env:DB_NAME + ";") | Out-Null
}

$tableCount = Invoke-MysqlQuery ("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='" + $env:DB_NAME + "' AND table_name='news';")
$tableCount = [int]($tableCount | Select-Object -First 1)
if ($tableCount -eq 0) {
  Info '首次运行，导入表结构与种子数据…'
  Import-SqlFile (Join-Path $SqlDir 'schema.sql')
  Import-SqlFile (Join-Path $SqlDir 'data.sql')
  Info '数据库初始化完成'
} else {
  Info '数据库已存在，跳过初始化（数据表已就绪）'
}

# ---------- 7. 构建后端 ----------
Step '构建后端'
$backendUp = $false
try {
  $probe = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $env:BACKEND_PORT + '/api/health') -TimeoutSec 2
  $backendUp = ($probe.code -eq 0)
} catch { }

if ($backendUp) {
  Info '后端已在运行，跳过构建（如需更新代码，请先执行 stop.ps1 再启动）'
} elseif ($SkipBuild) {
  Info '已指定 -SkipBuild，跳过 Maven 构建'
} else {
  $buildLog = Join-Path $LogDir 'build.log'
  Push-Location $BackendDir
  & $maven -B -DskipTests package 2>&1 | Out-File -FilePath $buildLog -Encoding utf8
  $buildCode = $LASTEXITCODE
  Pop-Location
  if ($buildCode -ne 0) {
    Get-Content $buildLog -Tail 30 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    Fail '后端构建失败，完整日志见 logs\build.log'
  }
  Info '后端构建成功'
}

function Test-Backend {
  try {
    $response = Invoke-RestMethod -Uri ('http://127.0.0.1:' + $env:BACKEND_PORT + '/api/health') -TimeoutSec 2
    return ($response.code -eq 0)
  } catch {
    return $false
  }
}

function Test-Frontend {
  try {
    $response = Invoke-WebRequest -Uri ('http://127.0.0.1:' + $env:FRONTEND_PORT) -UseBasicParsing -TimeoutSec 2
    return ($response.StatusCode -eq 200)
  } catch {
    return $false
  }
}

# ---------- 8. 启动后端 ----------
Step '启动后端服务'
if (Test-Backend) {
  Info ('后端已在运行: http://127.0.0.1:' + $env:BACKEND_PORT)
} else {
  $portOwner = Get-NetTCPConnection -LocalPort ([int]$env:BACKEND_PORT) -State Listen -ErrorAction SilentlyContinue
  if ($portOwner) {
    Fail ('端口 ' + $env:BACKEND_PORT + ' 已被进程 ' + $portOwner.OwningProcess + ' 占用，请先释放或修改 .env 中的 BACKEND_PORT。')
  }
  $jarPath = Join-Path $BackendDir 'target\campus-headlines.jar'
  if (-not (Test-Path $jarPath)) { Fail '未找到后端 jar，请移除 -SkipBuild 后重试。' }

  $backendOut = Join-Path $LogDir 'backend.log'
  $backendErr = Join-Path $LogDir 'backend-err.log'
  $backendProcess = Start-Process -FilePath $java -ArgumentList @('-Dfile.encoding=UTF-8', '-jar', $jarPath) -WorkingDirectory $BackendDir -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr -PassThru -WindowStyle Hidden
  $backendProcess.Id | Set-Content (Join-Path $RunDir 'backend.pid')

  $healthy = $false
  for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Backend) { $healthy = $true; break }
  }
  if (-not $healthy) {
    if (Test-Path $backendOut) { Get-Content $backendOut -Tail 30 | ForEach-Object { Write-Host $_ -ForegroundColor Red } }
    Fail '后端启动超时，请查看 logs\backend.log'
  }
  Info ('后端已启动: http://127.0.0.1:' + $env:BACKEND_PORT)
}

# ---------- 9. 启动前端 ----------
Step '启动前端服务'
$frontendDir = $FrontendDir
if ((-not (Test-Path (Join-Path $frontendDir 'node_modules'))) -or $Reinstall) {
  Info '安装前端依赖（首次运行需要几分钟）…'
  Push-Location $frontendDir
  & $npmCmd.Source install --no-audit --no-fund 2>&1 | Out-File -FilePath (Join-Path $LogDir 'npm-install.log') -Encoding utf8
  $npmCode = $LASTEXITCODE
  Pop-Location
  if ($npmCode -ne 0) { Fail '前端依赖安装失败，请查看 logs\npm-install.log' }
}

if (Test-Frontend) {
  Info ('前端已在运行: http://127.0.0.1:' + $env:FRONTEND_PORT)
} else {
  $portOwner = Get-NetTCPConnection -LocalPort ([int]$env:FRONTEND_PORT) -State Listen -ErrorAction SilentlyContinue
  if ($portOwner) {
    Fail ('端口 ' + $env:FRONTEND_PORT + ' 已被进程 ' + $portOwner.OwningProcess + ' 占用，请先释放或修改 .env 中的 FRONTEND_PORT。')
  }
  $frontendOut = Join-Path $LogDir 'frontend.log'
  $frontendErr = Join-Path $LogDir 'frontend-err.log'
  $frontendProcess = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', ('npm run dev -- --host 127.0.0.1 --port ' + $env:FRONTEND_PORT)) -WorkingDirectory $frontendDir -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr -PassThru -WindowStyle Hidden
  $frontendProcess.Id | Set-Content (Join-Path $RunDir 'frontend.pid')

  $ready = $false
  for ($i = 0; $i -lt 90; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Frontend) { $ready = $true; break }
  }
  if (-not $ready) {
    if (Test-Path $frontendOut) { Get-Content $frontendOut -Tail 30 | ForEach-Object { Write-Host $_ -ForegroundColor Red } }
    Fail '前端启动超时，请查看 logs\frontend.log'
  }
  Info ('前端已启动: http://127.0.0.1:' + $env:FRONTEND_PORT)
}

$url = 'http://127.0.0.1:' + $env:FRONTEND_PORT
if (-not $NoBrowser) { Start-Process $url }

Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  校园头条已启动" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ("  用户端:    " + $url)
Write-Host ("  自媒体端:  " + $url + "/media/login")
Write-Host ("  接口地址:  http://127.0.0.1:" + $env:BACKEND_PORT + "/api")
Write-Host ""
Write-Host "  演示账号"
Write-Host "    自媒体端: admin / 123456"
Write-Host "    用户端:   13800138000 / 验证码 123456"
Write-Host ""
Write-Host "  停止服务: scripts\stop.ps1"
Write-Host "  日志目录: logs\"
Write-Host ""
