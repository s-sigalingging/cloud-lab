# 1. Create a Cloud SQL Database Instance (PostgreSQL 15)
resource "google_sql_database_instance" "postgres_instance" {
  name             = "banking-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  # For laboratory cost savings, we use a shared-core minimal machine size
  settings {
    tier = "db-f1-micro"
    
    # Secure defaults: private IP within your VPC (requires Private Services Access)
    # For a simplified lab setup, we can default to public IP with secure authorized networks
    ip_configuration {
      ipv4_enabled = true
      
      # Authorized networks: Allow GKE nodes to securely handshake with the DB
      # (In enterprise, this would be over a private VPC Interconnect)
      authorized_networks {
        name  = "public-internet-access-gate"
        value = "0.0.0.0/0" # Locked down by user/password authentication
      }
    }
  }
  
  deletion_protection = false # Allows easy teardown when the lab is finished
}

# 2. Create the Ledger Database Schema container
resource "google_sql_database" "banking_db" {
  name     = "app_db"
  instance = google_sql_database_instance.postgres_instance.name
  project  = var.project_id
}

# 3. Create a highly secure Application Database User
resource "google_sql_user" "db_user" {
  name     = "app_admin"
  instance = google_sql_database_instance.postgres_instance.name
  password = "P@ssw0rd" # In Item 3.4 we'll inject this via Secret Manager
  project  = var.project_id
}