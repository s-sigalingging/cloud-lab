# 1. The Protected Master Cluster Frame (No node configurations inside here!)
resource "google_container_cluster" "primary" {
  name     = "s-shield-core-cluster"
  location = "asia-southeast2-a"

  network    = google_compute_network.trusted_vpc.name
  subnetwork = google_compute_subnetwork.app_subnet.name

  # This tells Google to wipe out the hidden default starter nodes immediately
  remove_default_node_pool = true
  initial_node_count       = 1

  lifecycle {
    prevent_destroy = true
  }
}

# 2. The Completely Independent Node Pool Resource
resource "google_container_node_pool" "primary_nodes" {
  name       = "core-node-pool"
  location   = "asia-southeast2-a"
  
  # Link them via the cluster name pointer string
  cluster    = google_container_cluster.primary.name
  node_count = 2 # Your updated capacity target

  node_config {
    preemptible  = true
    machine_type = "e2-medium"
    
    # Your quota-saving disk overrides
    disk_size_gb = 30
    disk_type    = "pd-standard"

    service_account = "gitlab-runner@project-3ad3e57a-ebe0-4fe5-b00.iam.gserviceaccount.com"
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    tags            = ["gke-node", "s-shield-internal"]
  }
}