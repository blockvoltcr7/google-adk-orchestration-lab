variable "project_id" {
  description = "Google Cloud project that owns the demo dataset and query jobs."
  type        = string
}

variable "location" {
  description = "BigQuery data location. The public source dataset is in US."
  type        = string
  default     = "US"

  validation {
    condition     = var.location == "US"
    error_message = "This demo must use US because the public source dataset is in US."
  }
}

variable "dataset_id" {
  description = "Disposable BigQuery dataset created for the ADK showcase."
  type        = string
  default     = "adk_bigquery_demo"

  validation {
    condition = (
      length(var.dataset_id) <= 1024 &&
      can(regex("^[A-Za-z_][A-Za-z0-9_]*$", var.dataset_id))
    )
    error_message = "dataset_id must be a valid BigQuery dataset identifier."
  }
}
