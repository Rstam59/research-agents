import logging
import argparse

from research_agent.config import validate_settings 
from research_agent.graph import build_graph
from research_agent.logging_config import configure_logging

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Research Agent")
    parser.add_argument(
        'topic',
        type=str,
        help='The research topic to investigate'
    )
    return parser.parse_args()


def main() -> None:
    configure_logging()
    validate_settings()

    args = parse_args()
    topic = args.topic

    logger.info("Starting Research Agent...")
    app = build_graph()

    logger.info(f"Invoking research agent for topic: {topic}")

    result = app.invoke({
        "topic": topic,
        "notes": [],
        "draft": ""
    })

    logger.info("Research agent finished")

    print("Final Research Draft:")
    print(result['draft'])


if __name__ == "__main__":
    main()