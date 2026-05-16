resource "google_compute_instance" "bastion_server" {
  name         = "bastion-server"
  machine_type = "e2-micro"
  zone         = var.zone
  tags         = ["bastion"]

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
    access_config {}
  }

  scheduling {
    preemptible                 = true            
    automatic_restart           = false           
    provisioning_model          = "SPOT"         
    instance_termination_action = "STOP" 
  }

  metadata = {
    serial-port-enable = "1"
  }
}