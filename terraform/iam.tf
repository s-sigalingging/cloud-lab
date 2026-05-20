resource "google_service_account" "app_sa" {
  account_id   = "gitlab-runner"
  display_name = "Workload Identity Service Account"
}

resource "google_secret_manager_secret_iam_member" "secret_reader" {
  secret_id = google_secret_manager_secret.db_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_storage_bucket_iam_member" "bucket_reader" {
  bucket = google_storage_bucket.asset_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_service_account_iam_member" "github_actions_workload_identity" {
  service_account_id = google_service_account.app_sa.name 
  role               = "roles/iam.serviceAccountTokenCreator"
  
  member = "principalSet://iam.googleapis.com/projects/319432675110/locations/global/workloadIdentityPools/github-pool/attribute.repository/s-sigalingging/cloud-lab"
}