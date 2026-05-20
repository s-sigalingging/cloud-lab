output "secret_name" {
  value       = google_secret_manager_secret.db_secret.secret_id
}

output "bucket_name" {
  value       = google_storage_bucket.asset_bucket.name
}

output "service_account_email" {
  value       = google_service_account.app_sa.email 
}

output "registry_url" {
  value       = "${google_artifact_registry_repository.bank_app_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.bank_app_repo.repository_id}"
}