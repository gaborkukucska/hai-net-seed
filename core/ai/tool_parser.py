# START OF FILE core/ai/tool_parser.py
"""
HAI-Net Tool Call Parser
Robust XML parsing for agent tool requests.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from core.config.settings import HAINetSettings
from core.logging.logger import get_logger


class ToolCallParser:
    """
    Parses tool calls from agent LLM output using robust XML parsing.
    """
    
    def __init__(self, settings: HAINetSettings):
        self.settings = settings
        self.logger = get_logger("ai.tool_parser", settings)
    
    def parse_tool_calls(self, text: str) -> Dict[str, Any]:
        """
        Parse tool calls from agent output text.
        
        Args:
            text: The LLM output text
            
        Returns:
            Dict with 'success', 'tool_calls', and optional 'error' keys
        """
        
        # Check if there are tool requests markers
        if "<tool_requests>" not in text or "</tool_requests>" not in text:
            return {"success": False, "tool_calls": [], "error": "No tool_requests block found"}
        
        try:
            # Extract the tool_requests block
            start_idx = text.find("<tool_requests>")
            end_idx = text.find("</tool_requests>") + len("</tool_requests>")
            xml_block = text[start_idx:end_idx]
            
            # Parse XML
            root = ET.fromstring(xml_block)
            
            tool_calls: List[Dict[str, Any]] = []
            
            # Find all tool_call elements
            calls_element = root.find("calls")
            if calls_element is None:
                return {"success": False, "tool_calls": [], "error": "No <calls> element found"}
            
            for tool_call_elem in calls_element.findall("tool_call"):
                tool_call = self._parse_single_tool_call(tool_call_elem)
                if tool_call:
                    tool_calls.append(tool_call)
            
            if not tool_calls:
                return {"success": False, "tool_calls": [], "error": "No valid tool calls found"}
            
            return {"success": True, "tool_calls": tool_calls}
            
        except ET.ParseError as e:
            self.logger.debug(f"XML parsing error, attempting fallback: {e}", category="ai", function="parse_tool_calls")
            # Attempt fallback parsing
            return self._fallback_parse(text)
        except Exception as e:
            self.logger.error(f"Tool call parsing error: {e}", category="ai", function="parse_tool_calls")
            return {"success": False, "tool_calls": [], "error": str(e)}
    
    def _parse_single_tool_call(self, tool_call_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """
        Parse a single tool_call element.
        
        Args:
            tool_call_elem: The tool_call XML element
            
        Returns:
            Dict with 'name' and 'args' or None if invalid
        """
        try:
            # Get tool name
            name_elem = tool_call_elem.find("name")
            if name_elem is None or not name_elem.text:
                self.logger.debug("Tool call missing <name> element", category="ai", function="_parse_single_tool_call")
                return None
            
            tool_name = name_elem.text.strip()
            
            # Get args
            args_elem = tool_call_elem.find("args")
            if args_elem is None:
                self.logger.debug(f"Tool call '{tool_name}' has no <args> element, using empty args", category="ai", function="_parse_single_tool_call")
                return {"name": tool_name, "args": {}}
            
            # Parse arguments
            args: Dict[str, Any] = {}
            for arg_elem in args_elem:
                arg_name = arg_elem.tag
                arg_value = arg_elem.text.strip() if arg_elem.text else ""
                args[arg_name] = arg_value
            
            return {"name": tool_name, "args": args}
            
        except Exception as e:
            self.logger.error(f"Error parsing single tool call: {e}", category="ai", function="_parse_single_tool_call")
            return None
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """
        Fallback parser using simple string extraction when XML parsing fails.
        
        Args:
            text: The LLM output text
            
        Returns:
            Dict with parsing results
        """
        try:
            # This is the simple parser from the original code
            tool_name = text.split("<name>")[1].split("</name>")[0].strip()
            
            args: Dict[str, Any] = {}
            
            # Try to extract common arguments
            if "<target_agent_id>" in text and "</target_agent_id>" in text:
                args["target_agent_id"] = text.split("<target_agent_id>")[1].split("</target_agent_id>")[0].strip()
            
            if "<message>" in text and "</message>" in text:
                args["message"] = text.split("<message>")[1].split("</message>")[0].strip()
            
            tool_call: Dict[str, Any] = {"name": tool_name, "args": args}
            
            self.logger.debug("Using fallback parser - may be incomplete", category="ai", function="_fallback_parse")
            return {"success": True, "tool_calls": [tool_call], "fallback": True}
            
        except Exception as e:
            self.logger.error(f"Fallback parsing also failed: {e}", category="ai", function="_fallback_parse")
            return {"success": False, "tool_calls": [], "error": f"Both XML and fallback parsing failed: {e}"}
    
    def extract_plan(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract a plan block from agent output.
        
        Args:
            text: The LLM output text
            
        Returns:
            Dict with plan details or None
        """
        if "<plan>" not in text or "</plan>" not in text:
            return None
        
        try:
            start_idx = text.find("<plan>")
            end_idx = text.find("</plan>") + len("</plan>")
            xml_block = text[start_idx:end_idx]
            
            root = ET.fromstring(xml_block)
            
            plan: Dict[str, Any] = {}
            
            # Extract plan elements
            for child in root:
                if child.text:
                    if child.tag == "objectives" or child.tag == "deliverables":
                        # These contain list items
                        items = [item.strip() for item in child.text.strip().split("\n") if item.strip() and item.strip().startswith("-")]
                        items = [item[1:].strip() for item in items]  # Remove the leading "-"
                        plan[child.tag] = items
                    else:
                        plan[child.tag] = child.text.strip()
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error extracting plan: {e}", category="ai", function="extract_plan")
            return None
    
    def extract_task_list(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Extract a task list from PM agent output.
        
        Args:
            text: The LLM output text
            
        Returns:
            List of task dicts or None
        """
        if "<task_list>" not in text or "</task_list>" not in text:
            return None
        
        try:
            start_idx = text.find("<task_list>")
            end_idx = text.find("</task_list>") + len("</task_list>")
            xml_block = text[start_idx:end_idx]
            
            root = ET.fromstring(xml_block)
            
            tasks: List[Dict[str, Any]] = []
            
            for task_elem in root.findall("task"):
                task: Dict[str, Any] = {}
                for child in task_elem:
                    if child.text:
                        task[child.tag] = child.text.strip()
                
                if task:
                    tasks.append(task)
            
            return tasks if tasks else None
            
        except Exception as e:
            self.logger.error(f"Error extracting task list: {e}", category="ai", function="extract_task_list")
            return None

    def extract_create_worker_request(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts a request to create a worker agent.

        Args:
            text: The LLM output text

        Returns:
            Dict with worker details or None
        """
        if "<create_worker_request>" not in text or "</create_worker_request>" not in text:
            return None

        try:
            start_idx = text.find("<create_worker_request>")
            end_idx = text.find("</create_worker_request>") + len("</create_worker_request>")
            xml_block = text[start_idx:end_idx]

            root = ET.fromstring(xml_block)

            request: Dict[str, Any] = {}

            # Extract request elements
            for child in root:
                if child.text:
                    request[child.tag] = child.text.strip()

            # A task_id is mandatory for a worker request
            return request if "task_id" in request else None

        except Exception as e:
            self.logger.error(f"Error extracting create_worker_request: {e}", category="ai", function="extract_create_worker_request")
            return None
