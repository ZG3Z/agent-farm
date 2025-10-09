terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "terraform-state-bucket-agents-prd"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "required_apis" {
  for_each = toset([
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com"
  ])
  
  service            = each.value
  disable_on_destroy = false
}

locals {
  agents_config = yamldecode(file("${path.module}/../agents_config.yaml"))
  
  agents = {
    for agent_name, config in local.agents_config.agents : agent_name => {
      provider     = config.provider
      model        = config.model
      api_key_env  = config.api_key_env
      temperature  = config.temperature
    }
  }
  
  secret_mappings = {
    "GOOGLE_API_KEY"     = google_secret_manager_secret.GOOGLE_API_KEY.secret_id
    "OPENWEATHER_API_KEY" = google_secret_manager_secret.OPENWEATHER_API_KEY.secret_id
  }
  
  image_uris = {
    for agent_name in keys(local.agents) : agent_name => 
      "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agents.name}/${agent_name}:${var.environment}"
  }
}

module "agents" {
  source   = "./modules/cloud-run-agent"
  for_each = local.agents
  
  agent_name            = each.key
  region                = var.region
  image_uri             = local.image_uris[each.key]
  service_account_email = google_service_account.agents_sa.email
  
  llm_provider = each.value.provider
  model       = each.value.model
  api_key_env = each.value.api_key_env
  temperature = each.value.temperature
  
  secret_env_vars = each.key == "crewai-weather" ? {
    (each.value.api_key_env) = local.secret_mappings[each.value.api_key_env]
    "OPENWEATHER_API_KEY"    = local.secret_mappings["OPENWEATHER_API_KEY"]
  } : {
    (each.value.api_key_env) = local.secret_mappings[each.value.api_key_env]
  }
  
  cpu           = "1"
  memory        = "512Mi"
  min_instances = 0
  max_instances = 1
  
  allow_unauthenticated = true
  
  depends_on = [
    google_artifact_registry_repository.agents,
    google_service_account.agents_sa,
    google_project_service.required_apis
  ]
}