resource "google_artifact_registry_repository" "bank_app_repo" {
  location      = "asia-southeast2"
  repository_id = "lab-images"
  description   = "Docker Repository for Lab"
  format        = "DOCKER"

  
  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"
    condition {
      tag_state    = "ANY"
      older_than   = "2592000s" 
    }
  }
}

resource "google_project_iam_member" "artifact_repo_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}