"""
DataHub AI Enricher

An open-source DataHub plugin that uses LLMs to automatically suggest
metadata enrichments for data catalogs.
"""

__version__ = "0.1.0"
__author__ = "Newt Braswell"
__license__ = "Apache-2.0"

from enricher.config import EnricherConfig
from enricher.enrichment_engine import EnrichmentEngine

__all__ = ["EnricherConfig", "EnrichmentEngine", "__version__"]
