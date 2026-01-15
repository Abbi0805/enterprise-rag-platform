# Start Qdrant Docker Container
Write-Host "Starting Qdrant Database..."
docker run -d -p 6333:6333 -v qdrant_data:/qdrant/storage --name qdrant qdrant/qdrant

if ($?) {
    Write-Host "✅ Qdrant Database started successfully on port 6333!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker command failed. Is Docker Desktop running?" -ForegroundColor Yellow
}
