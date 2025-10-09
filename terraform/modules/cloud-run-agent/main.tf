resource "google_cloud_run_v2_service" "agent" {
  name     = var.agent_name
  location = var.region
  
  template {
    service_account = var.service_account_email
    
    containers {
      image = var.image_uri
      
      env {
        name  = "AGENT_NAME"
        value = var.agent_name
      }
      
      env {
        name  = "PROVIDER"
        value = var.llm_provider
      }
      
      env {
        name  = "MODEL"
        value = var.model
      }
      
      env {
        name  = "API_KEY_ENV"
        value = var.api_key_env
      }
      
      env {
        name  = "TEMPERATURE"
        value = tostring(var.temperature)
      }
      
      env {
        name  = "ENDPOINT"
        value = "https://${var.agent_name}-${var.cloud_run_hash}.run.app"
      }
      
      dynamic "env" {
        for_each = var.secret_env_vars
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value
              version = "latest"
            }
          }
        }
      }
      
      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        cpu_idle = true
        startup_cpu_boost = false
      }
      
      ports {
        container_port = var.port
      }
      
      startup_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }
      
      liveness_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }
    }
    
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }
    
    timeout = "300s"
  }
  
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  count = var.allow_unauthenticated ? 1 : 0
  
  name     = google_cloud_run_v2_service.agent.name
  location = google_cloud_run_v2_service.agent.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}