resource "google_service_account" "agents_sa" {
  account_id   = "sa-agent-farm"
  display_name = "Agents Farm Service Account"
  description  = "Service account for AI agents running on Cloud Run"
}

resource "google_secret_manager_secret_iam_member" "GOOGLE_API_KEY" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.GOOGLE_API_KEY.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agents_sa.email}"
}
 
resource "google_secret_manager_secret_iam_member" "OPENAI_API_KEY" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.OPENAI_API_KEY.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agents_sa.email}"
}
 
resource "google_secret_manager_secret_iam_member" "ANTHROPIC_API_KEY" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.ANTHROPIC_API_KEY.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agents_sa.email}"
}
 
resource "google_secret_manager_secret_iam_member" "OPENWEATHER_API_KEY" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.OPENWEATHER_API_KEY.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.agents_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "agents_sa_reader" {
  location   = google_artifact_registry_repository.agents.location
  repository = google_artifact_registry_repository.agents.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.agents_sa.email}"
}