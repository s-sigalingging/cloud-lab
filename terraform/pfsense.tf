resource "google_compute_instance" "pfsense_gateway" {
  name         = "pfsense-gateway"
  machine_type = "e2-medium"
  zone         = var.zone
  can_ip_forward = true 
  tags         = ["pfsense-firewall"]

  # WAN Interface (External facing)
  network_interface {
    network    = google_compute_network.untrusted_vpc.id
    subnetwork = google_compute_subnetwork.dmz_subnet.id
    access_config {
      # Leaving this empty assigns an Ephemeral Public IP
    }
  }

  # LAN Interface (Internal banking side)
  network_interface {
    network    = google_compute_network.trusted_vpc.id
    subnetwork = google_compute_subnetwork.app_subnet.id
  }

  boot_disk {
    initialize_params {
      image = google_compute_image.pfsense_custom.self_link
    }
  }
  metadata = {
  serial-port-enable = "1"
}
}