resource "google_compute_firewall" "pfsense_management" {
  name    = "allow-pfsense-mgmt"
  network = google_compute_network.untrusted_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["443", "22"] 
  }

  # Replace with YOUR actual public IP for safety
  source_ranges = ["103.26.188.5/32"] 
  target_tags   = ["pfsense-firewall"]
}