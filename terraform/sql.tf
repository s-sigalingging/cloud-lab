resource "google_sql_database_instance" "postgres_instance" {
  name             = "banking-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  

  settings {
    tier = "db-f1-micro" 
    
    ip_configuration {
      ipv4_enabled    = false 
      private_network = "projects/${var.project_id}/global/networks/default"
    }
  }
  
  deletion_protection = false
}


resource "google_sql_database" "banking_db" {
  name     = "ledger-db"
  instance = google_sql_database_instance.postgres_instance.name
  project  = var.project_id
}


resource "google_sql_user" "db_user" {
  name     = "ledger-admin"
  instance = google_sql_database_instance.postgres_instance.name
  password = "SuperSecureBankingPassword2026!"
  project  = var.project_id
}