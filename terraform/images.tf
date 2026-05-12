resource "google_compute_image" "pfsense_custom" {
  name = "pfsense-custom-image"
  raw_disk {
    source = "https://storage.googleapis.com/cloud-lab-tf-state/pfSense-CE-memstick-serial-2.7.0-RELEASE-amd64.img.tar"
  }
  guest_os_features {
    type = "UEFI_COMPATIBLE"
  }
}