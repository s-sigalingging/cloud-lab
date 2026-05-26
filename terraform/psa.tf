resource "google_compute_subnetwork" "db_subnet" {
  name          = "banking-subnet"
  ip_cidr_range = "10.240.10.0/24" 
  region        = var.region
  network       = "trusted-vpc"        
  project       = var.project_id
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "banking-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16               
  network       = "trusted-vpc"
  project       = var.project_id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = "trusted-vpc"        
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}