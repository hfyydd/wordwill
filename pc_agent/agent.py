"""PC Agent implementation for orchestrating the AI automation loop."""

import time
import logging
from dataclasses import dataclass
from typing import Any, List, Optional

from pc_agent.model.client import ModelClient, MessageBuilder, ModelConfig
from pc_agent.actions.handler import ActionHandler, ActionResult
from pc_agent.pc import get_screenshot, get_current_app
from pc_agent.config import get_system_prompt, get_message

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the PC Agent."""
    max_steps: int = 50
    verbose: bool = True
    lang: str = "cn"  # 'cn' or 'en'
    confirm_sensitive: bool = True

class PcAgent:
    """
    Agent for controlling PC applications.
    
    Orchestrates the loop: Perception -> Planning -> Action.
    """
    
    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None,
        agent_config: Optional[AgentConfig] = None
    ):
        self.agent_config = agent_config or AgentConfig()
        self.model_client = ModelClient(model_config)
        self.action_handler = ActionHandler()
        self.messages: List[dict] = []
        self._setup_initial_context()

    def _setup_initial_context(self):
        """Initialize the conversation with the system prompt."""
        system_prompt = get_system_prompt(self.agent_config.lang)
        self.messages.append(MessageBuilder.create_system_message(system_prompt))

    def run(self, task_description: str):
        """
        Run the agent to complete a specific task.
        
        Args:
            task_description: Natural language description of the task.
        """
        print(f"\n🚀 {get_message('starting_task', self.agent_config.lang)}: {task_description}")
        
        # Add initial user task
        self.messages.append(MessageBuilder.create_user_message(f"任务目标: {task_description}"))
        
        for step in range(1, self.agent_config.max_steps + 1):
            print(f"\n--- {get_message('step', self.agent_config.lang)} {step} ---")
            
            try:
                # 1. Perception: Capture state
                screenshot = get_screenshot()
                current_app = get_current_app()
                
                # Build context info
                screen_info = MessageBuilder.build_screen_info(
                    current_app=current_app,
                    width=screenshot.logical_width,
                    height=screenshot.logical_height
                )
                
                # 2. Planning: Get model response
                # We always send the latest state (screenshot + text info)
                user_msg = MessageBuilder.create_user_message(
                    text=f"当前状态: {screen_info}",
                    image_base64=screenshot.base64_data
                )
                
                # Temp message list for this request (don't keep screenshots in history to save tokens)
                request_messages = self.messages + [user_msg]
                
                print(f"🤔 {get_message('thinking', self.agent_config.lang)}...")
                response = self.model_client.request(request_messages)
                
                if response.thinking:
                    print(f"💡 {response.thinking}")
                
                print(f"🎬 {get_message('action', self.agent_config.lang)}: {response.action}")
                
                # Add model's thought and choice to history (without images)
                self.messages.append(MessageBuilder.create_assistant_message(response.raw_content))
                
                # 3. Execution: Run the action
                import pc_agent.actions.handler as handler
                action_dict = handler.parse_action(response.action)
                
                result = self.action_handler.execute(
                    action_dict, 
                    screenshot.logical_width, 
                    screenshot.logical_height
                )
                
                if not result.success:
                    print(f"❌ {result.message}")
                    # Optionally add failure info to history to help model recover
                    self.messages.append(MessageBuilder.create_user_message(f"Action failed: {result.message}"))
                
                if result.should_finish:
                    print(f"\n✅ {get_message('task_completed', self.agent_config.lang)}")
                    if result.message:
                        print(f"🏁 {get_message('final_result', self.agent_config.lang)}: {result.message}")
                    break
                    
                # Short wait for UI update
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error during step {step}: {e}")
                print(f"⚠️ {get_message('error', self.agent_config.lang) if 'error' in self.agent_config.lang else 'Error'}: {e}")
                break
        else:
            print(f"\n🛑 REACHED MAX STEPS ({self.agent_config.max_steps})")
