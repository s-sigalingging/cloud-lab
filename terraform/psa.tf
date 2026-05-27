# 0. Query Google Cloud for the existing pre-built VPC
data "google_compute_network" "existing_vpc" {
  name    = "trusted-vpc"
  project = var.project_id
}

# 1. Your Custom Subnet referencing the discovered data source
resource "google_compute_subnetwork" "db_subnet" {
  name          = "banking-subnet"
  ip_cidr_range = "10.240.10.0/24" 
  region        = var.region
  project       = var.project_id
  
  network       = data.google_compute_network.existing_vpc.id
}

# 2. Private IP Allocation Range
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "banking-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16               
  project       = var.project_id

  network       = data.google_compute_network.existing_vpc.id
}

# 3. Private VPC Service Networking Connection
resource "google_service_networking_connection" "private_vpc_connection" {
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]

  network                 = data.google_compute_network.existing_vpc.id
}