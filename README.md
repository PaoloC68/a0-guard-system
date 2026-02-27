# Guard System

Security guards for Agent Zero tool execution and prompt safety. Blocks tools associated with flagged scan results and detects prompt injection patterns in assembled prompts.

## Features

- **Scan Status Guard** — Blocks tool execution when a skill/tool has been flagged as `blocked` by an external security scanner. Tools flagged as `needs_review` produce a warning but are allowed to run.
- **Prompt Length Guard** — Monitors assembled prompt size and warns the LLM when content exceeds a configurable character limit.
- **Injection Detection** — Scans prompts for known injection patterns (regex-supported) and surfaces warnings to the LLM context.

## Configuration

| Option | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | Master switch for all guards |
| `max_prompt_length` | int | `500000` | Maximum allowed prompt length in characters |
| `injection_detection` | bool | `true` | Enable prompt injection pattern scanning |
| `injection_patterns` | list[str] | *(see default_config.yaml)* | Regex patterns to detect injection attempts |
| `scan_results` | dict | `{}` | Tool/skill scan results from external scanners |

## How Scan Results Work

External scanners (or manual review) write results into the plugin's `scan_results` config. Each key is a tool or skill name, and the value is a dict with `status` and optional metadata.

### Statuses

| Status | Behavior |
|---|---|
| `blocked` | Tool execution is prevented. A `RepairableException` is raised so the LLM can try a different approach. |
| `needs_review` | A warning is printed but execution proceeds. |
| *(anything else)* | No action taken. |

### Setting Scan Results via Python

```python
from python.helpers.plugins import get_plugin_config, save_plugin_config

config = get_plugin_config("guard-system", agent=agent) or {}
config.setdefault("scan_results", {})["my_skill"] = {
    "status": "blocked",
    "reason": "Malicious code detected",
    "scanner": "cisco"
}
save_plugin_config("guard-system", settings=config)
```

### Clearing a Scan Result

```python
config = get_plugin_config("guard-system", agent=agent) or {}
config.get("scan_results", {}).pop("my_skill", None)
save_plugin_config("guard-system", settings=config)
```

## Extension Points

| Hook | File | Purpose |
|---|---|---|
| `tool_execute_before` | `_05_scan_status_guard.py` | Checks scan results before each tool runs |
| `message_loop_prompts_after` | `_05_prompt_length_guard.py` | Checks prompt size and injection patterns after prompt assembly |

## Installation

Copy the `guard-system/` directory into `usr/plugins/` and enable it from the Agent Zero settings UI.
