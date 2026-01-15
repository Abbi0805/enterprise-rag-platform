# Ingest CV Script
$backendUrl = "http://localhost:8000"
$dataPath = Resolve-Path "..\data\*.pdf"

if (-not $dataPath) {
    Write-Error "❌ Keine PDF-Datei in ../data/ gefunden! Bitte legen Sie Ihren Lebenslauf dort ab."
    exit 1
}

$file = $dataPath[0].Path
Write-Host "📄 Gefundene Datei: $file"
Write-Host "🚀 Starte Upload..."

try {
    # Escape backslashes for JSON
    $jsonPath = $file.Replace('\', '\\')
    
    $response = Invoke-RestMethod -Uri "$backendUrl/ingest/demo" `
        -Method Post `
        -ContentType "application/json" `
        -Body "{""file_path"": ""$jsonPath""}" `
        -Headers @{"Authorization"="Bearer sk-admin"}
    
    Write-Host "✅ Upload erfolgreich!" -ForegroundColor Green
    Write-Host "Details: $($response | ConvertTo-Json -Depth 2)"
} catch {
    Write-Error "❌ Fehler beim Upload: $_"
    Write-Host "Ist das Backend gestartet? (uvicorn src.api.main:app ...)" -ForegroundColor Yellow
}
