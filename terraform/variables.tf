variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The region to deploy resources in"
  type        = string
  default     = "asia-southeast2"
}

variable "zone" {
  description = "The specific zone within the region"
  type        = string
  default     = "asia-southeast2-a"
}