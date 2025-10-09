variable "agent_name" {
  description = "Name of the agent"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run"
  type        = string
}

variable "image_uri" {
  description = "Full URI of the container image"
  type        = string
}

variable "service_account_email" {
  description = "Service account email for the Cloud Run service"
  type        = string
}

variable "llm_provider" {
  description = "LLM provider (openai, anthropic, gemini)"
  type        = string
}

variable "model" {
  description = "Model name"
  type        = string
}

variable "api_key_env" {
  description = "Environment variable name for API key"
  type        = string
}

variable "temperature" {
  description = "Model temperature"
  type        = number
}

variable "port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "cloud_run_hash" {
  description = "Hash suffix for Cloud Run URL (not needed, Cloud Run auto-generates)"
  type        = string
  default     = ""
}

variable "secret_env_vars" {
  description = "Map of environment variable names to Secret Manager secret IDs"
  type        = map(string)
  default     = {}
}

variable "cpu" {
  description = "CPU allocation"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "allow_unauthenticated" {
  description = "Allow unauthenticated access"
  type        = bool
  default     = true
}