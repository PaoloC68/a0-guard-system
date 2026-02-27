import re
from python.helpers.extension import Extension
from python.helpers.plugins import get_plugin_config
from python.helpers.print_style import PrintStyle
from agent import LoopData


class PromptLengthGuard(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        config = get_plugin_config("guard-system", agent=self.agent) or {}
        if not config.get("enabled", True):
            return

        warnings = []

        # Check prompt length
        max_length = config.get("max_prompt_length", 500000)
        total_length = sum(len(s) for s in loop_data.system)
        if total_length > max_length:
            warnings.append(
                f"Prompt length ({total_length:,} chars) exceeds safety limit ({max_length:,}). "
                f"Content may have been injected or is excessively large."
            )
            PrintStyle(font_color="yellow", padding=True).print(
                f"[Guard] Prompt length warning: {total_length:,} chars (limit: {max_length:,})"
            )

        # Check for injection patterns
        if config.get("injection_detection", True):
            patterns = config.get("injection_patterns", [])
            full_prompt = "\n".join(loop_data.system)
            for pattern in patterns:
                try:
                    if re.search(pattern, full_prompt, re.IGNORECASE):
                        warnings.append(
                            f"Potential prompt injection detected (pattern: '{pattern}'). "
                            f"Exercise caution with the current input."
                        )
                        PrintStyle(font_color="red", padding=True).print(
                            f"[Guard] Injection pattern detected: {pattern}"
                        )
                except re.error:
                    pass  # Skip invalid regex patterns

        if warnings:
            loop_data.extras_temporary["guard_warnings"] = "\n".join(
                f"⚠ {w}" for w in warnings
            )
