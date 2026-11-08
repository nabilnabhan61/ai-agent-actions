param(
    [Parameter(Mandatory = $true)][string]$Image,
    [string]$EnvFile = (Join-Path $env:USERPROFILE '.ai-agent-actions.env')
)
$ErrorActionPreference = 'Stop'

function Invoke-Docker {
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Docker failed: $($args[0]) (exit $LASTEXITCODE)" }
}

if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
    throw "Create $EnvFile from .env.example before deploying. See SETUP.md."
}
$containerOS = Invoke-Docker info --format '{{.OSType}}'
if ($containerOS.Trim() -ne 'linux') { throw 'Switch Docker Desktop to Linux containers.' }

# A failed pull leaves the existing app running.
Invoke-Docker pull --platform linux/amd64 $Image
Invoke-Docker volume create ai-agent-actions-data
$existing = Invoke-Docker ps -aq --filter 'name=^/ai-agent-actions-app$'
if ($existing) { Invoke-Docker rm -f ai-agent-actions-app }

Invoke-Docker run -d --platform linux/amd64 --name ai-agent-actions-app `
    --restart unless-stopped -p 127.0.0.1:8000:8000 `
    --env-file $EnvFile --mount 'type=volume,source=ai-agent-actions-data,target=/data' $Image

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    $health = Invoke-Docker inspect --format '{{.State.Health.Status}}' ai-agent-actions-app
    if ($health.Trim() -eq 'healthy') {
        Write-Host 'Deployment healthy: http://localhost:8000'
        exit 0
    }
    if ($health.Trim() -eq 'unhealthy') { break }
    Start-Sleep -Seconds 3
}
Invoke-Docker logs --tail 80 ai-agent-actions-app
throw 'The deployed container did not become healthy.'
