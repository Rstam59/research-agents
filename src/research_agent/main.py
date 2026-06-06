from research_agent.config import validate_settings 
from research_agent.graph import build_graph

def main():
    validate_settings()

    app = build_graph()

    result = app.invoke({
        "topic": "The impact of climate change on global agriculture",
        "notes": [],
        "draft": ""
    })

    print("Final Research Draft:")
    print(result['draft'])


if __name__ == "__main__":
    main()