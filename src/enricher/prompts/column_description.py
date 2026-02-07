"""Prompt templates for generating column descriptions."""

from typing import Any, Dict, List


def build_column_description_prompt(dataset_name: str, columns: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for generating column descriptions.

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
        existing_desc = col.get("description", "")
        nullable = col.get("nullable", True)

        info = f"- {field_path} ({data_type})"
        if not nullable:
            info += " [NOT NULL]"
        if existing_desc:
            info += f"\n  Current description: {existing_desc}"

        column_info.append(info)

    columns_text = "\n".join(column_info)

    prompt = f"""You are a data catalog documentation assistant. Your task is to generate clear,
concise descriptions for database columns based on their names and data types.

Dataset: {dataset_name}

Columns:
{columns_text}

Please provide a brief, informative description for each column. The description should:
1. Explain what the column represents in plain English
2. Include any business context you can infer from the name
3. Be 1-2 sentences maximum
4. Avoid repeating the column name verbatim
5. Focus on the purpose and content, not technical details

Format your response as a JSON object where keys are column names and values are descriptions:

{{
  "column_name": "description",
  "another_column": "description"
}}

Only include columns that need descriptions (skip those with good existing descriptions)."""

    return prompt
