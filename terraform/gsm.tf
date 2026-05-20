resource "google_secret_manager_secret" "db_secret" {
  secret_id = "banking-db-secret"


  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_secret_val" {
  secret      = google_secret_manager_secret.db_secret.id
  secret_data = "GCP-TERRAFORM-MANAGED-SECURE-STRING-9900"
}