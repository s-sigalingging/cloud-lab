resource "google_compute_firewall" "pfsense_management" {
  name    = "allow-pfsense-mgmt"
  network = google_compute_network.untrusted_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["443", "22"] # WebGUI and SSH
  }

  # Replace with YOUR actual public IP for safety
  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["pfsense-firewall"]
}