resource "google_compute_subnetwork" "db_subnet" {
  name          = "banking_subnet"
  ip_cidr_range = "10.240.10.0/24" 
  region        = var.region
  network       = "default"        
  project       = var.project_id
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "banking_private_ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16               
  network       = "default"        
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = "default"
  service                 = "servicenetworking.googleapis.com"
  reserved_ip_range_names = [google_compute_global_address.private_ip_alloc.name]
}


resource "google_sql_database_instance" "postgres_instance" {
  name             = "banking-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id
  
  
  depends_on = [google_service_networking_connection.private_vpc_connection]

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
  name     = "ledger_db"
  instance = google_sql_database_instance.postgres_instance.name
  project  = var.project_id
}


resource "google_sql_user" "db_user" {
  name     = "ledger_admin"
  instance = google_sql_database_instance.postgres_instance.name
  password = "SuperSecureBankingPassword2026!"
  project  = var.project_id
}