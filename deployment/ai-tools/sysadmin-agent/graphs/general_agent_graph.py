"""
General Agent Graph for SysAdmin Dashboard
ReAct-style workflow for handling user queries and executing tasks
"""

from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from .common import AgentState, create_llm, get_system_prompt, log_decision, log_tool_call
from tools.monitoring_tools import (
    get_system_health,
    get_disk_usage,
    get_running_services,
    get_recent_logs,
    get_network_status,
    get_firewall_status,
    get_security_summary,
)
from tools.shell_tool import execute_command, requires_approval


# =============================================================================
# Tool Definitions (as LangChain tools)
# =============================================================================

@tool
def check_system_health() -> str:
    """Get current system health metrics including CPU, memory, disk, and top processes."""
    health = get_system_health()
    return f"""## System Health Report

**CPU:** {health['cpu']['percent']}% {health['cpu']['status']}
- Cores: {health['cpu']['count']}
- Load Average: {health['load_average']['1min']} / {health['load_average']['5min']} / {health['load_average']['15min']}

**Memory:** {health['memory']['percent']}% {health['memory']['status']}
- Used: {health['memory']['used_gb']} GB / {health['memory']['total_gb']} GB
- Available: {health['memory']['available_gb']} GB

**Uptime:** {health['uptime']['uptime_str']}

**Top Processes by CPU:**
{chr(10).join([f"- {p['name']} (PID {p['pid']}): CPU {p['cpu_percent']}%, Mem {p['memory_percent']}%" for p in health['top_processes']])}
"""


@tool
def check_disk_usage() -> str:
    """Get disk usage for all mounted partitions with alerts for high usage."""
    usage = get_disk_usage()
    result = "## Disk Usage Report\n\n"

    for part in usage['partitions']:
        result += f"**{part['mountpoint']}** ({part['device']})\n"
        result += f"- {part['used_gb']} GB / {part['total_gb']} GB ({part['percent']}%) {part['status']}\n"
        result += f"- Free: {part['free_gb']} GB\n\n"

    if usage['alerts']:
        result += "### ⚠️ Alerts\n"
        for alert in usage['alerts']:
            result += f"- {alert}\n"

    return result


@tool
def check_services() -> str:
    """Get status of critical system services."""
    services = get_running_services()
    result = "## Service Status Report\n\n"

    for svc in services.get('services', []):
        result += f"{svc['status_icon']} **{svc['name']}**: {svc['status']}\n"

    if services.get('failed_services'):
        result += "\n### ⚠️ Failed Services\n"
        for svc in services['failed_services']:
            result += f"- {svc}\n"

    return result


@tool
def check_logs(log_name: str = "messages", lines: int = 50) -> str:
    """
    Get recent entries from system logs.

    Args:
        log_name: Name of log to check (messages, secure, audit, dnf)
        lines: Number of lines to retrieve (default 50)
    """
    logs = get_recent_logs(log_name, lines)

    if 'error' in logs:
        return f"Error reading log: {logs['error']}"

    result = f"## Recent Logs: {log_name}\n\n"
    result += f"**Errors found:** {logs['error_count']}\n"
    result += f"**Warnings found:** {logs['warning_count']}\n\n"

    if logs['recent_errors']:
        result += "### Recent Errors:\n```\n"
        result += "\n".join(logs['recent_errors'][-3:])
        result += "\n```\n\n"

    result += "### Log Content:\n```\n"
    result += logs['content'][-2000:]  # Last 2000 chars
    result += "\n```"

    return result


@tool
def check_network() -> str:
    """Check network interfaces and connectivity to key hosts."""
    network = get_network_status()
    result = "## Network Status Report\n\n"

    result += "### Connectivity Tests\n"
    for test in network['connectivity']:
        result += f"{test['status']} {test['name']} ({test['host']})\n"

    result += "\n### Network Interfaces\n"
    for iface in network['interfaces']:
        if iface.get('ipv4'):
            result += f"- **{iface['name']}**: {iface.get('ipv4', 'N/A')}\n"

    return result


@tool
def check_firewall() -> str:
    """Get firewall status and rules summary."""
    fw = get_firewall_status()

    if 'error' in fw:
        return f"Error checking firewall: {fw['error']}"

    return f"""## Firewall Status

**State:** {fw['status']}

**Active Zones:**
```
{fw['active_zones']}
```

**Default Zone Rules:**
```
{fw['default_zone_rules']}
```
"""


@tool
def check_security() -> str:
    """Get security status summary including failed logins and SELinux."""
    security = get_security_summary()

    if 'error' in security:
        return f"Error checking security: {security['error']}"

    return f"""## Security Summary

**Status:** {security['status']}

**Failed SSH attempts (24h):** {security['failed_ssh_attempts_24h']}
**SELinux:** {security['selinux_status']}

**Recent root logins:**
```
{security['recent_root_logins']}
```
"""


@tool
def run_command(command: str) -> str:
    """
    Execute a whitelisted shell command.

    Only safe, pre-approved commands can be executed.
    High-risk commands require explicit user approval.

    Args:
        command: The shell command to execute
    """
    # Check if approval is needed
    if requires_approval(command):
        return f"""⚠️ **APPROVAL REQUIRED**

This command requires human approval before execution:
```
{command}
```

Please confirm you want to execute this command."""

    result = execute_command(command)

    if not result['success']:
        return f"❌ Command failed: {result['error']}"

    output = result['output'] if result['output'] else "(no output)"
    return f"✅ Command executed successfully:\n```\n{output}\n```"


# List of all tools
TOOLS = [
    check_system_health,
    check_disk_usage,
    check_services,
    check_logs,
    check_network,
    check_firewall,
    check_security,
    run_command,
]


# =============================================================================
# Graph Nodes
# =============================================================================

def agent_node(state: AgentState) -> AgentState:
    """
    Main agent node that processes user input and decides on actions.
    """
    llm = create_llm()
    llm_with_tools = llm.bind_tools(TOOLS)

    # Build messages with system prompt
    messages = [SystemMessage(content=get_system_prompt())] + state["messages"]

    # Get response from LLM
    response = llm_with_tools.invoke(messages)

    # Log the decision
    state = log_decision(state, f"Agent response: {response.content[:200]}...")

    # Add response to messages
    state["messages"].append(response)

    return state


def tool_node(state: AgentState) -> AgentState:
    """
    Execute tools called by the agent.
    """
    tool_executor = ToolNode(TOOLS)

    # Get the last message (should be AIMessage with tool calls)
    last_message = state["messages"][-1]

    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            state = log_tool_call(
                state,
                tool_call['name'],
                tool_call['args'],
                "executing..."
            )

    # Execute tools
    result = tool_executor.invoke(state)

    # Update state with tool results
    if "messages" in result:
        state["messages"].extend(result["messages"])

    return state


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Determine if we should continue to tools or end the conversation.
    """
    last_message = state["messages"][-1]

    # If the LLM made tool calls, continue to tool node
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"

    # Otherwise, end the conversation
    return "end"


# =============================================================================
# Graph Construction
# =============================================================================

def create_general_agent_graph():
    """
    Create the general agent graph for handling user queries.

    Returns:
        Compiled LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )

    # Tools always go back to agent
    workflow.add_edge("tools", "agent")

    # Compile and return
    return workflow.compile()


# =============================================================================
# Convenience Functions
# =============================================================================

def run_query(query: str, state: AgentState = None) -> AgentState:
    """
    Run a single query through the agent.

    Args:
        query: User's question or command
        state: Existing state (or None for fresh state)

    Returns:
        Updated state with response
    """
    from .common import create_initial_state

    if state is None:
        state = create_initial_state()

    # Add user message
    state["messages"].append(HumanMessage(content=query))

    # Create and run graph
    graph = create_general_agent_graph()
    result = graph.invoke(state)

    return result


def get_last_response(state: AgentState) -> str:
    """Extract the last AI response from the state."""
    for message in reversed(state["messages"]):
        if isinstance(message, AIMessage) and message.content:
            return message.content
    return "No response generated."
