resource "google_storage_bucket" "asset_bucket" {
  name          = "lab-assets-app" 
  location      = "ASIA-SOUTHEAST2"                      
  force_destroy = true

  public_access_prevention = "enforced" 

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}