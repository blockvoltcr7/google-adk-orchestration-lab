output "dataset_id" {
  description = "Dataset identifier used by the local ADK agent."
  value       = google_bigquery_dataset.demo.dataset_id
}

output "dataset_fqn" {
  description = "Fully qualified BigQuery dataset name."
  value       = "${var.project_id}.${google_bigquery_dataset.demo.dataset_id}"
}

output "cleanup_command" {
  description = "Safe entry point that previews cleanup unless --execute is passed."
  value       = "./scripts/cleanup.sh"
}
