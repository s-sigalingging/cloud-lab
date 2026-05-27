# 1. Create the Production Cloud SQL Database Instance (PostgreSQL 15)
resource "google_sql_database_instance" "postgres_instance" {
  name             = "app-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  # CRITICAL: Wait for the network peering connection to be completely 
  # active in your GCP project before attempting to deploy the database hardware.
  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    google_compute_subnetwork.db_subnet
  ]

  settings {
    # Laboratory cost-saving shared-core minimal machine size
    tier = "db-f1-micro"
    
    ip_configuration {
      ipv4_enabled    = false # Zero public internet footprint. Completely un-routable from the web.
      
      # Forces internal network card routing to bind straight into your trusted VPC network
      private_network = "projects/${var.project_id}/global/networks/trusted-vpc"
    }
  }
  
  deletion_protection = false # Set to true in real production environments to prevent accidental deletion
}

# 2. Create the Database Schema Container inside PostgreSQL
resource "google_sql_database" "banking_db" {
  name     = "ledger_db"
  instance = google_sql_database_instance.postgres_instance.name
  project  = var.project_id
}

# 3. Create the Database Admin User for Application Authentication
resource "google_sql_user" "db_user" {
  name     = "ledger_admin"
  instance = google_sql_database_instance.postgres_instance.name
  password = "SuperSecureBankingPassword2026!" # Later we will feed this to Secret Manager
  project  = var.project_id
}

# 4. Optional: Output the Assigned Private IP Address to the terminal
output "cloud_sql_private_ip" {
  description = "The internal private IP address of the secure database instance."
  value       = google_sql_database_instance.postgres_instance.private_ip_address
}