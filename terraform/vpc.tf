resource "google_compute_network" "trusted_vpc" {
  name                    = "trusted-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "app_subnet" {
  name          = "app-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "asia-southeast2"
  network       = google_compute_network.trusted_vpc.id
}

resource "google_compute_network" "untrusted_vpc" {
  name                    = "untrusted-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "dmz_subnet" {
  name          = "dmz-subnet"
  ip_cidr_range = "10.0.2.0/24"
  region        = "asia-southeast2"
  network       = google_compute_network.untrusted_vpc.id
}