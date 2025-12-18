import argparse
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pc_agent.agent import PcAgent, AgentConfig
from pc_agent.model.client import ModelConfig
from pc_agent.config.apps import list_supported_apps

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PC Agent - AI-powered computer automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with a specific task
    python main.py "帮我打开 Chrome 搜索 DeepSeek"

    # Specify model endpoint
    python main.py "打开微信" --base-url http://localhost:8000/v1

    # Use API key for authentication
    python main.py "写一份周报" --apikey sk-xxxxx

    # List supported apps
    python main.py --list-apps
        """,
    )

    # Task description
    parser.add_argument(
        "task",
        type=str,
        nargs="?",
        help="The task description in natural language",
    )

    # Model options
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("PC_AGENT_BASE_URL", "http://localhost:8000/v1"),
        help="Model API base URL",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("PC_AGENT_MODEL", "autoglm-phone-9b"),
        help="Model name",
    )

    parser.add_argument(
        "--apikey",
        type=str,
        default=os.getenv("PC_AGENT_API_KEY", "EMPTY"),
        help="API key for model authentication",
    )

    # Agent options
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("PC_AGENT_MAX_STEPS", "50")),
        help="Maximum steps per task",
    )

    parser.add_argument(
        "--lang",
        type=str,
        default="cn",
        choices=["cn", "en"],
        help="Language (cn/en)",
    )

    # Utility options
    parser.add_argument(
        "--list-apps",
        action="store_true",
        help="List supported PC applications",
    )

    return parser.parse_args()

def main():
    args = parse_args()

    if args.list_apps:
        print("\n🖥️  Supported PC Applications:")
        apps = list_supported_apps()
        for app in apps:
            print(f"  - {app}")
        return

    if not args.task:
        print("❌ Error: Please provide a task description.")
        print("Usage: python main.py \"your task here\"")
        return

    # 1. Create configurations
    model_config = ModelConfig(
        base_url=args.base_url,
        model_name=args.model,
        api_key=args.apikey,
    )

    agent_config = AgentConfig(
        max_steps=args.max_steps,
        lang=args.lang,
        verbose=True
    )

    # 2. Create agent
    agent = PcAgent(
        model_config=model_config,
        agent_config=agent_config,
    )

    # 3. Run task
    try:
        agent.run(args.task)
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
