resource "google_compute_route" "app_to_pfsense" {
  name                   = "app-to-pfsense-route"
  dest_range             = "0.0.0.0/0"
  network                = google_compute_network.trusted_vpc.id
  next_hop_instance      = google_compute_instance.pfsense_builder.id
  next_hop_instance_zone = var.zone
  priority               = 100
}