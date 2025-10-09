variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "environment" {
  description = "Environment (dev, stg, prd)"
  type        = string
  default     = "prd"
}

variable "github_repository" {
  description = "GitHub repository in format: owner/repo"
  type        = string
}