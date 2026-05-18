resource "google_compute_firewall" "pfsense_management" {
  name    = "allow-pfsense-mgmt"
  network = google_compute_network.untrusted_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["443", "22"] 
  }

  # Replace with YOUR actual public IP for safety
  source_ranges = ["103.26.188.5/32","103.165.124.44"] 
  target_tags   = ["pfsense-firewall"]
}

resource "google_compute_firewall" "allow_ssh_to_bastion" {
  name    = "allow-ssh-to-bastion"
  network = "trusted-vpc" 

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["bastion"]  
}