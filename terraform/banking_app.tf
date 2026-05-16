resource "google_compute_instance" "banking_app_server" {
  name         = "banking-app-server"
  machine_type = "e2-micro"
  zone         = var.zone
  can_ip_forward = true

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 20
      type  = "pd-ssd"
    }
  }

  network_interface {
    network    = google_compute_network.trusted_vpc.id
    subnetwork = google_compute_subnetwork.app_subnet.id
  }

  metadata = {
    serial-port-enable = "1"
  }
}