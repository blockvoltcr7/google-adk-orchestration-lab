"""Definition of encapsulated sub-workflows."""

from google.adk.workflow import Workflow, START
from app.nodes import (
    parse_content,
    extract_metadata,
    check_editorial_tone,
    generate_seo_tags,
    bundle_distribution_package,
    archive_and_publish,
)

# Subworkflow 1: Ingestion & normalization
ingestion_subworkflow = Workflow(
    name="ingestion_subworkflow",
    description="Encapsulated pipeline for raw text intake, sanitization, and word counting",
    edges=[
        (START, parse_content),
        (parse_content, extract_metadata),
    ],
)

# Subworkflow 2: Editorial enhancement & SEO
editorial_subworkflow = Workflow(
    name="editorial_subworkflow",
    description="Encapsulated pipeline for tone grading and SEO meta generation",
    edges=[
        (START, check_editorial_tone),
        (check_editorial_tone, generate_seo_tags),
    ],
)

# Subworkflow 3: Packaging and CDN distribution
distribution_subworkflow = Workflow(
    name="distribution_subworkflow",
    description="Encapsulated pipeline for CDN bundling and live archival",
    edges=[
        (START, bundle_distribution_package),
        (bundle_distribution_package, archive_and_publish),
    ],
)
