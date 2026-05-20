resource "google_artifact_registry_repository" "bank_app_repo" {
  location      = "ASIA-SOUTHEAST2"
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

resource "google_artifact_registry_repository_iam_member" "repo_reader" {
  location   = google_artifact_registry_repository.bank_app_repo.location
  repository = google_artifact_registry_repository.bank_app_repo.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.app_sa.email}"
}