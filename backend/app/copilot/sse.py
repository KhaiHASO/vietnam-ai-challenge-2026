import json
from typing import Any

def format_sse_event(event_id: str, event_type: str, payload: dict[str, Any]) -> str:
    lines = []
    if event_id:
        lines.append(f"id: {event_id}")
    if event_type:
        lines.append(f"event: {event_type}")
    
    data_str = json.dumps(payload, ensure_ascii=False)
    for line in data_str.split("\n"):
        lines.append(f"data: {line}")
        
    lines.append("")
    lines.append("")
    return "\n".join(lines)
