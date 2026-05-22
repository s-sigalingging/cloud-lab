# 1. Define the Private GKE Cluster Frame
resource "google_container_cluster" "primary" {
  name     = "s-shield-core-cluster"
  location = "asia-southeast2-a" # Keep it in your same zone to prevent cross-zone networking fees
  deletion_protection = false

  # Link it directly to your existing VPC network infrastructure
  network    = google_compute_network.trusted_vpc.name
  subnetwork = google_compute_subnetwork.app_subnet.name

  # Turn off the default node pool so we can build a customized one right below it
  remove_default_node_pool = true
  initial_node_count       = 2

  network_policy {
    enabled = true 
  }

  # Make it a private cluster so it doesn't get a public IP address on the internet
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false # Allows you to still manage it via your authenticated gcloud terminal
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/21"
    services_ipv4_cidr_block = "/24"
  }
}

# 2. Define the Managed Node Pool (Where our banking application pods will actually run)
resource "google_container_node_pool" "primary_nodes" {
  name       = "core-node-pool"
  location   = "asia-southeast2-a"
  cluster    = google_container_cluster.primary.name
  node_count = 1 # Keep it at 1 node for a compact, cost-efficient lab footprint

  node_config {
    preemptible  = true 
    machine_type = "e2-medium"
    disk_size_gb = 30
    disk_type    = "pd-standard"

    # Attach your secure application runner identity to the nodes
    service_account = "gitlab-runner@project-3ad3e57a-ebe0-4fe5-b00.iam.gserviceaccount.com"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    tags = ["gke-node", "s-shield-internal"]
  }
}