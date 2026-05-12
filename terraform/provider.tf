terraform {
  required_version = ">= 1.5.0"

  backend "gcs" {
    bucket = "cloud-lab-tf-state"
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
} 