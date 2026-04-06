# Build Frontend and integrate with Django
$ErrorActionPreference = "Stop"

Write-Host "Building frontend..." -ForegroundColor Cyan
Set-Location -Path "$PSScriptRoot\frontend"
npm run build

Write-Host "Copying dist assets to Django static..." -ForegroundColor Cyan
$source = "$PSScriptRoot\frontend\dist"
$dest = "$PSScriptRoot\smartoffer_django\static"

if (-Not (Test-Path $dest)) {
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
}

# Remove old assets
Remove-Item -Path "$dest\assets" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$dest\favicon.svg" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$dest\index.html" -Force -ErrorAction SilentlyContinue

# Copy new assets
Copy-Item -Path "$source\assets" -Destination "$dest\assets" -Recurse -Force
if (Test-Path "$source\favicon.svg") {
    Copy-Item -Path "$source\favicon.svg" -Destination "$dest\favicon.svg" -Force
}

Write-Host "Generating Django template..." -ForegroundColor Cyan
$html = Get-Content -Path "$source\index.html" -Raw -Encoding UTF8

# Replace static references with Django static tags
$html = $html -replace 'href="/favicon\.svg"', 'href="{% static ''favicon.svg'' %}"'
$html = $html -replace 'src="/assets/([^"]+)"', 'src="{% static ''assets/$1'' %}"'
$html = $html -replace 'href="/assets/([^"]+)"', 'href="{% static ''assets/$1'' %}"'

# Add load static at the top if not present
if (-not ($html.Contains("{% load static %}"))) {
    $html = $html -replace '<!doctype html>', "{% load static %}`n<!doctype html>"
}

# Ensure templates directory exists
$templatesDir = "$PSScriptRoot\templates"
if (-Not (Test-Path $templatesDir)) {
    New-Item -ItemType Directory -Force -Path $templatesDir | Out-Null
}

# Write UTF-8 without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$templatesDir\index.html", $html, $utf8NoBom)

Write-Host "Done! Frontend integrated with Django." -ForegroundColor Green
Write-Host "Run 'python manage.py collectstatic --noinput' before production deployment." -ForegroundColor Yellow
