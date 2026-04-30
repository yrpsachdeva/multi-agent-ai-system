from agents import (
    create_supervisor_chain,
    create_researcher_agent,
    create_writer_chain,
    create_critique_chain
)

def run_workflow(task):
    state = {
        "main_task": task,
        "research_findings": [],
        "draft": "",
        "critique_notes": "",
        "revision_number": 0
    }

    supervisor = create_supervisor_chain()
    researcher = create_researcher_agent()
    writer = create_writer_chain()
    critique = create_critique_chain()

    while True:
        decision = supervisor(state)
        step = decision["next_step"]

        print(f"\n➡️ Next Step: {step}")

        if step == "END":
            print("\n✅ FINAL OUTPUT:\n")
            print(state.get("draft", "No draft generated"))
            break

        elif step == "researcher":
            result = researcher({"input": state["main_task"]})
            state["research_findings"].append(result["output"])

        elif step == "writer":
            state["draft"] = writer(state)

        # Run critique after writing
        if state["draft"]:
            state["critique_notes"] = critique(state)
            state["revision_number"] += 1


if __name__ == "__main__":
    task = input("Enter your research topic: ")
    run_workflow(task)