"""Prompt templates for suggesting dataset tags."""

from typing import Any, Dict, List


def build_tag_suggestion_prompt(
    dataset_name: str, dataset_description: str, columns: List[Dict[str, Any]]
) -> str:
    """
    Build a prompt for suggesting dataset tags.

    Args:
        dataset_name: Name of the dataset
        dataset_description: Description of the dataset
        columns: List of column metadata

    Returns:
        Formatted prompt string
    """
    column_names = [col.get("fieldPath", "unknown") for col in columns[:20]]  # Limit to 20
    columns_text = ", ".join(column_names)
    if len(columns) > 20:
        columns_text += f", ... and {len(columns) - 20} more"

    desc_text = dataset_description if dataset_description else "No description provided"

    prompt = f"""You are a data governance expert helping to classify and tag datasets in a data catalog.

Dataset: {dataset_name}
Description: {desc_text}
Sample Columns: {columns_text}

Based on the dataset name, description, and column structure, suggest relevant tags that would help
users discover and understand this dataset.

Consider these tag categories:

1. **Domain/Subject**: What business area does this relate to?
   Examples: finance, marketing, sales, hr, operations, customer_data

2. **Data Type/Format**: What kind of data is this?
   Examples: transactional, analytical, reference_data, time_series, dimensional

3. **Sensitivity**: What's the sensitivity level?
   Examples: public, internal, confidential, restricted

4. **Quality/Status**: What's the data quality or maturity?
   Examples: production, staging, raw, curated, deprecated

5. **Source System**: Where does this data come from?
   Examples: crm, erp, warehouse, api, third_party

6. **Use Case**: How is this data typically used?
   Examples: reporting, ml_training, analytics, compliance, audit

Guidelines:
- Suggest 3-7 tags maximum
- Use lowercase with underscores (e.g., customer_data)
- Be specific but not overly detailed
- Focus on tags that aid discovery and governance
- Avoid redundant tags

Format your response as a JSON object:

{{
  "suggested_tags": [
    {{
      "tag": "tag_name",
      "category": "domain|data_type|sensitivity|quality|source|use_case",
      "confidence": "high|medium|low",
      "reason": "Brief explanation"
    }}
  ]
}}"""

    return prompt
