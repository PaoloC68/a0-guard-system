from helpers.extension import Extension
from helpers.errors import RepairableException
from helpers.plugins import get_plugin_config
from helpers.print_style import PrintStyle


class ScanStatusGuard(Extension):
    # Tools that must never be blocked — they're how the agent communicates
    WHITELISTED_TOOLS = frozenset({"response", "call_subordinate", "delegation"})

    async def execute(self, tool_args=None, tool_name="", **kwargs):
        config = get_plugin_config("guard-system", agent=self.agent) or {}
        if not config.get("enabled", True):
            return

        if tool_name in self.WHITELISTED_TOOLS:
            return

        scan_results = config.get("scan_results", {})
        
        # Check exact tool name and also check if tool relates to a scanned skill
        for scanned_name, result in scan_results.items():
            if not isinstance(result, dict):
                continue
            status = result.get("status", "").lower()
            
            if scanned_name == tool_name or self._tool_matches_skill(tool_name, tool_args, scanned_name):
                if status == "blocked":
                    reason = result.get("reason", "Security scan flagged this skill as unsafe")
                    raise RepairableException(
                        f"[Guard] Tool '{tool_name}' blocked: {reason}. "
                        f"Skill '{scanned_name}' has been flagged by security scanning. "
                        f"Use a different approach or ask the user to review the scan results."
                    )
                elif status == "needs_review":
                    PrintStyle(font_color="yellow", padding=True).print(
                        f"[Guard] Warning: Tool '{tool_name}' relates to skill '{scanned_name}' "
                        f"which needs security review."
                    )

    @staticmethod
    def _tool_matches_skill(tool_name, tool_args, skill_name):
        """Check if a tool execution relates to a scanned skill."""
        if not tool_args:
            return False
        # Check if skill name appears in any tool argument values
        for value in tool_args.values():
            if isinstance(value, str) and skill_name.lower() in value.lower():
                return True
        return False
