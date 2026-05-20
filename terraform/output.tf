output "secret_name" {
  value       = google_secret_manager_secret.db_secret.secret_id
}

output "bucket_name" {
  value       = google_storage_bucket.asset_bucket.name
}

output "service_account_email" {
  value       = google_service_account.app_sa.email 
}