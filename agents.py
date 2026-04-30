# agents.py

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering
import torch

from prompts import (
    supervisor_prompt_template,
    researcher_prompt_template,
    writer_prompt_template,
    critique_prompt_template
)

# Load environment variables
load_dotenv()
import getpass

if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = getpass.getpass("Tavily API key:\n")

# ------------------ #
# LOAD YOUR MODELS 🔥
# ------------------ #

print("Loading local models...")
writer_tokenizer = AutoTokenizer.from_pretrained(
    "models/writer_model/final_model",
    use_fast=False
)

writer_model = AutoModelForSeq2SeqLM.from_pretrained(
    "models/writer_model/final_model"
)

researcher_tokenizer = AutoTokenizer.from_pretrained(
    "models/researcher_model/researcher_model",
    use_fast=False
)
researcher_model = AutoModelForQuestionAnswering.from_pretrained("models/researcher_model/researcher_model")

print("Models loaded successfully ✅")

# --- 1. Setup LLM and Tools ---

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

tavily_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_answer=False,
    include_raw_content=False,
    search_depth="basic"
)


def _call_llm(llm_obj, *args, **kwargs):
    if hasattr(llm_obj, "invoke"):
        return llm_obj.invoke(*args, **kwargs)
    if hasattr(llm_obj, "run"):
        return llm_obj.run(*args, **kwargs)
    if callable(llm_obj):
        return llm_obj(*args, **kwargs)
    raise AttributeError("LLM/tool not callable")


# ----------------- #
# SUPERVISOR NODE   #
# ----------------- #
def create_supervisor_chain():
    def supervisor_invoke(state):
        research = state.get("research_findings", [])
        revision = state.get("revision_number", 0)
        draft = state.get("draft", "")
        critique = state.get("critique_notes", "")

        if "APPROVED" in critique.upper() and draft:
            return {"next_step": "END", "task_description": "Done"}

        if not research:
            return {"next_step": "researcher", "task_description": state.get("main_task", "")}

        if research and not draft:
            return {"next_step": "writer", "task_description": "Write draft"}

        if draft and not critique:
            return {"next_step": "writer", "task_description": "Prepare draft"}

        if critique and "APPROVED" not in critique.upper() and revision < 3:
            return {"next_step": "writer", "task_description": "Revise"}

        return {"next_step": "END", "task_description": "Finished"}

    return supervisor_invoke


# ----------------- #
# RESEARCHER NODE   #
# ----------------- #
def create_researcher_agent():
    def researcher_invoke(input_dict):
        question = input_dict.get("input", "What is AI?")
        context = "Artificial Intelligence is a field of computer science."

        inputs = researcher_tokenizer(question, context, return_tensors="pt")

        with torch.no_grad():
            outputs = researcher_model(**inputs)

        start = torch.argmax(outputs.start_logits)
        end = torch.argmax(outputs.end_logits) + 1

        answer = researcher_tokenizer.decode(inputs["input_ids"][0][start:end])

        return {
            "output": answer,
            "input": question
        }

    return researcher_invoke


# ----------------- #
# WRITER NODE       #
# ----------------- #
def create_writer_chain():
    def writer_invoke(state):
        research = state.get("research_findings", [])
        text = " ".join(research)[:1000] if research else state.get("main_task", "")

        inputs = writer_tokenizer("summarize: " + text, return_tensors="pt")

        output = writer_model.generate(**inputs, max_length=150)

        result = writer_tokenizer.decode(output[0], skip_special_tokens=True)

        return result

    return writer_invoke


# ----------------- #
# CRITIQUE NODE     #
# ----------------- #
def create_critique_chain():
    def critique_invoke(state):
        draft = state.get("draft", "")

        if len(draft) < 50:
            return "APPROVED"

        prompt = critique_prompt_template.format(
            main_task=state.get("main_task", ""),
            draft=draft
        )

        try:
            response = _call_llm(llm, prompt)
            return response.content if hasattr(response, "content") else str(response)
        except:
            return "APPROVED"

    return critique_invoke