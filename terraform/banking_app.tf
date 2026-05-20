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

  service_account {
  email  = google_service_account.app_sa.email
  scopes = ["cloud-platform"]
}
  metadata = {
    serial-port-enable = "1"
  }

  metadata = {
  ssh-keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDAK2vSJhwmv3KNjliSzMV8n7Ejos5EjQ9p0DLrO/Ob4GVAwSao6LADkYmj9XyCY1QF2v+pRq37h5lRUN4SHqmRm7e+zUa6+3PrPq5VPg/0uDpeenyWIQEKN3JkuVPSF4B3r8BAdKfTC2aF/89qllv2MWwtYkPSQEpWw6vlneEB3HM2HA/QD0GzZLJiVw2VAuBJYibrhKSSSh1xwfh8x+Dw/d/ND9HVXLDh+FMGFwTTvxdeHWzOJwy/Gs2FO8ITcl6iREq3iO3rIEjVN6nlq+9pPvqNtqeHgbuefUy9Gr2pmE0GKOBHxFU3s0hnYqlfM94GOmlv+Njm/rm3nvZpavFLLtJbf6yK1vVQonuTEPLoqmCizK9sZriMbQDNCgcXSZixof+YBeWxTXxvZBvi17RQafi5qGYpmTpRhwxxLKl63njVm2HJDh1ZlVGFvuzfh6R/iYKtf4vUNvvYkKVvt42RUhr8SNBSswgenkMDbt6Ws0YIURw1hUiKIiE34Vk3dbc= silver"
}

}