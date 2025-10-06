resource "google_artifact_registry_repository" "agents" {
  location      = var.region
  repository_id = "agents"
  description   = "Docker repository for AI agents"
  format        = "DOCKER"
  
  depends_on = [
    google_project_service.required_apis
  ]
}