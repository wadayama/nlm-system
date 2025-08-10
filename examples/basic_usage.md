# NLM System Basic Usage Examples

This document demonstrates basic usage of the Natural Language Macro (NLM) System using {{variable}} syntax.

## Simple Variable Operations

Save the word 'Hello' to {{greeting}}.

Get {{greeting}}.

Save my name 'Alice' to {{user_name}}.

Save the current date '2025-08-07' to {{today}}.

## Global Variables

Save 'production' to {{@environment}}.

Get {{@environment}}.

Save database connection string 'postgres://localhost/mydb' to {{@db_url}}.

Get {{@db_url}} for database connection.

### SystemSession Unified Interface

Using SystemSession for consistent global variable access between Python and natural language macros:

Set project configuration to 'AI Research 2024' in {{@project_name}}.

Save system status 'active' to {{@system_status}}.

Store API version '2.1' in {{@api_version}}.

Get {{@project_name}}, {{@system_status}}, and {{@api_version}} for system initialization.

## Cross-Session Communication

Save the analysis result 'correlation coefficient: 0.85' to {{stats_result}}.

Get {{data_analysis.stats_result}} and use it for the report.

## File Processing Example

Save the input filename 'data.csv' to {{input_file}}.

Save the output directory '/tmp/results' to {{output_dir}}.

Get {{input_file}} and prepare for processing.

## Configuration Management

Save debug level 'INFO' to {{global.log_level}}.

Save API endpoint 'https://api.example.com' to {{global.api_url}}.

Get {{global.log_level}} and {{global.api_url}}.

## Data Analysis Workflow

Save dataset path '/data/sales_2024.csv' to {{dataset}}.

Save analysis type 'regression' to {{model_type}}.

Get {{dataset}} and {{model_type}}, then prepare analysis parameters.

## Multi-Agent Coordination

Save task status 'completed' to {{data_prep_status}}.

Check if {{data_prep_status}} is completed and proceed with next step.

Save research findings 'significant correlation found' to {{research_notes}}.

## Error Handling Examples

Try to get {{missing_var}}.

Save an empty string '' to {{empty_test}}.

Get {{empty_test}} and handle appropriately.

## Variable Expansion Examples

Save 'Hello' to {{greeting}} and 'World' to {{target}}.

Create message using {{greeting}} {{target}}.

Process file {{input_file}} and save results to {{output_dir}}.

## Batch Operations

Save multiple configuration values:
- Save 'localhost' to {{host}}
- Save '5432' to {{port}}
- Save 'myapp' to {{database}}

List all variables to see current state.

Delete {{port}} as it's no longer needed.

Show me all remaining variables after deletion.