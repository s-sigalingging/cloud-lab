resource "google_compute_route" "app_to_pfsense" {
  name                   = "app-to-pfsense-route"
  dest_range             = "0.0.0.0/0"
  network                = google_compute_network.trusted_vpc.id
  next_hop_instance      = google_compute_instance.pfsense_gateway.id
  next_hop_instance_zone = var.zone
  priority               = 100 
}

resource "google_compute_route" "trusted_vpc_internet_route" {
  name             = "trusted-vpc-internet-route"
  dest_range       = "0.0.0.0/0"
  network          = google_compute_network.trusted_vpc.name
  next_hop_gateway = "default-internet-gateway"
  priority         = 1000
}