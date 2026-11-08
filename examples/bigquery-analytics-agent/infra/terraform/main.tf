provider "google" {
  project = var.project_id
}

resource "google_project_service" "bigquery" {
  project            = var.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_bigquery_dataset" "demo" {
  project       = var.project_id
  dataset_id    = var.dataset_id
  friendly_name = "ADK BigQuery natural-language demo"
  description   = "Disposable synthetic retail data for the ADK BigQuery analytics agent."
  location      = var.location

  delete_contents_on_destroy  = true
  default_table_expiration_ms = 2592000000
  max_time_travel_hours       = 48

  labels = {
    application = "adk-bigquery-demo"
    environment = "demo"
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.bigquery]
}
