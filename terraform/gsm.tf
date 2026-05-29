resource "google_secret_manager_secret" "db_secret" {
  secret_id = "banking-db-secret"


  replication {
    auto {}
  }
}