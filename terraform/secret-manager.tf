resource "google_secret_manager_secret" "GOOGLE_API_KEY" {
  secret_id = "GOOGLE_API_KEY"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    google_project_service.required_apis
  ]
}
 
resource "google_secret_manager_secret" "OPENAI_API_KEY" {
  secret_id = "OPENAI_API_KEY"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    google_project_service.required_apis
  ]
}
 
resource "google_secret_manager_secret" "ANTHROPIC_API_KEY" {
  secret_id = "ANTHROPIC_API_KEY"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    google_project_service.required_apis
  ]
}
 
resource "google_secret_manager_secret" "OPENWEATHER_API_KEY" {
  secret_id = "OPENWEATHER_API_KEY"
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  depends_on = [
    google_project_service.required_apis
  ]
}