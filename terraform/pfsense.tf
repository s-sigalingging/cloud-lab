resource "google_compute_disk" "pfsense_target_disk" {
  name  = "pfsense-target-disk"
  type  = "pd-ssd"
  zone  = var.zone
  size  = 20
}

resource "google_compute_instance" "pfsense_gateway" {
  name         = "pfsense-gateway"
  machine_type = "e2-medium"
  zone         = var.zone
  can_ip_forward = true 
  tags         = ["pfsense-firewall"]

  network_interface {
    network    = google_compute_network.untrusted_vpc.id
    subnetwork = google_compute_subnetwork.dmz_subnet.id
    access_config {}
  }

  network_interface {
    network    = google_compute_network.trusted_vpc.id
    subnetwork = google_compute_subnetwork.app_subnet.id
  }

  scheduling {
    preemptible                 = true            
    automatic_restart           = false           
    provisioning_model          = "SPOT"         
    instance_termination_action = "STOP" 
  }

  boot_disk {
    initialize_params {
      image = google_compute_image.pfsense_custom.self_link
      # Keep this small, it's just the installer
    }
  }

  attached_disk {
    source      = google_compute_disk.pfsense_target_disk.id
    device_name = "target-disk"
  }

  metadata = {
    serial-port-enable = "1" 
  }
}