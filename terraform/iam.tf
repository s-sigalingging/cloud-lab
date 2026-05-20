resource "google_service_account" "app_sa" {
  account_id   = "banking-app-runner"
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