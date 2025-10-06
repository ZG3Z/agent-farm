variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "github_repository" {
  description = "GitHub repository in format: owner/repo"
  type        = string
}