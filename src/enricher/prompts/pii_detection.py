"""Prompt templates for detecting PII and sensitive data."""

from typing import Any, Dict, List


def build_pii_detection_prompt(dataset_name: str, columns: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for detecting PII columns.

    Args:
        dataset_name: Name of the dataset
        columns: List of column metadata

    Returns:
        Formatted prompt string
    """
    column_info = []
    for col in columns:
        field_path = col.get("fieldPath", "unknown")
        data_type = col.get("nativeDataType", "unknown")
        description = col.get("description", "")

        info = f"- {field_path} ({data_type})"
        if description:
            info += f"\n  Description: {description}"

        column_info.append(info)

    columns_text = "\n".join(column_info)

    prompt = f"""You are a data privacy and security expert. Your task is to identify columns that
may contain Personally Identifiable Information (PII) or other sensitive data.

Dataset: {dataset_name}

Columns:
{columns_text}

Analyze each column and identify those that may contain:

1. **Direct PII**: Names, email addresses, phone numbers, SSN, passport numbers, etc.
2. **Indirect PII**: Birth dates, zip codes, IP addresses, device IDs, etc.
3. **Sensitive Data**: Health information, financial data, credentials, etc.
4. **Identifiers**: User IDs, customer IDs, account numbers (if they could identify individuals)

Consider:
- Column names and their semantic meaning
- Data types (strings often hold PII)
- Common naming patterns (e.g., email, phone, ssn, dob)
- Business context inferred from the dataset name

Format your response as a JSON object:

{{
  "pii_columns": [
    {{
      "field_path": "column_name",
      "pii_type": "email|phone|ssn|name|etc",
      "confidence": "high|medium|low",
      "reason": "Brief explanation"
    }}
  ]
}}

Only include columns where you have at least medium confidence that they contain PII or sensitive data."""

    return prompt
