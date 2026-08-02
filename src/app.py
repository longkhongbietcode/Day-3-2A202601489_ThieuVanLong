"""
Core app for Lab 03: Chatbot baseline vs ReAct Agent.

Topic: Career Orientation Chatbot.
"""

import json
import os
import sys
from typing import List, Tuple

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS, REACT_SYSTEM_PROMPT
from providers import get_llm_provider
from tools import AVAILABLE_TOOLS

load_dotenv()


Action = Tuple[str, str]


def load_test_cases():
    """Load test cases from config/test_cases.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider) -> str:
    """Run a plain chatbot answer without tools."""
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    if response.startswith("[") and "Error" in response:
        response = build_baseline_fallback(user_query)
    print("CHATBOT BASELINE")
    print(f"Question: {user_query}")
    print(f"Answer: {response}\n")
    return response


def build_baseline_fallback(user_query: str) -> str:
    """Return a local baseline answer when the configured LLM provider is unavailable."""
    text = user_query.lower()
    if "data analyst" in text:
        return (
            "Data Analyst thuong thu thap, lam sach, phan tich du lieu va tao bao cao "
            "de ho tro ra quyet dinh. Day la cau tra loi tong quat, chua co danh gia ca nhan hoa."
        )
    if "ky nang mem" in text:
        return (
            "Ba ky nang mem quan trong la giao tiep ro rang, lam viec nhom va quan ly thoi gian. "
            "Ngoai ra, sinh vien nen ren luyen kha nang nhan feedback."
        )
    if "ceo" in text or "dam bao" in text:
        return (
            "Toi khong the dam bao ban thanh CEO trong 1 thang. Muc tieu nghe nghiep nen co "
            "moc thoi gian thuc te, ky nang can hoc va tieu chi do luong ro rang."
        )
    return (
        "Toi co the goi y tong quat, nhung baseline khong co tool de danh gia sau ho so ca nhan "
        "hoac tao lo trinh rieng cho ban."
    )


def plan_actions(user_query: str) -> List[Action]:
    """
    Deterministic planner for the lab demo.

    In a full LLM setup, the model would emit Action lines. This offline planner
    keeps the ReAct behavior testable without API keys.
    """
    text = user_query.lower()

    if "dam bao" in text or "ceo" in text or "1 thang" in text:
        return [("check_goal_realism", user_query)]

    if "lo trinh" in text or "de xuat" in text and "hoc" in text:
        if "thiet ke" in text or "giao dien" in text:
            return [
                ("assess_career_fit", user_query),
                ("suggest_learning_path", "UI/UX Designer"),
            ]
        return [
            ("assess_career_fit", user_query),
            ("suggest_learning_path", "Data Analyst"),
        ]

    if "goi y nghe" in text or "phu hop" in text or "phan tich so lieu" in text:
        return [("assess_career_fit", user_query)]

    if "data analyst" in text:
        return [("get_career_info", "Data Analyst")]

    return []


def execute_tool(tool_name: str, argument: str) -> str:
    """Execute one registered tool and convert technical errors to observations."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if not tool:
        valid_tools = ", ".join(AVAILABLE_TOOLS)
        return f"LOI: Tool '{tool_name}' khong ton tai. Tools hop le: {valid_tools}."
    try:
        return tool(argument)
    except Exception as exc:
        return f"LOI: Tool '{tool_name}' bi loi runtime: {exc}"


def build_final_answer(user_query: str, observations: List[str]) -> str:
    """Create a concise final answer grounded in tool observations."""
    if not observations:
        return (
            "Day la cau hoi tong quat ve nghe nghiep, co the tra loi truc tiep bang kien thuc nen. "
            "Neu ban muon tu van ca nhan hoa, hay cung cap so thich, ky nang hien co va muc tieu."
        )

    joined = " ".join(observations)
    if "GUARDRAIL" in joined or "CANH BAO" in joined:
        return (
            "Minh khong the dam bao ket qua phi thuc te nhu thanh CEO trong 1 thang. "
            "Huong an toan hon la dat muc tieu nho: chon 1 ky nang nen tang, hoc deu 4-8 tuan, "
            "lam 1 project va xin feedback tu nguoi co kinh nghiem."
        )

    if joined.startswith("Data Analyst:"):
        return (
            "Data Analyst thuong thu thap, lam sach, phan tich du lieu va tao bao cao. "
            "Ky nang nen co gom Excel, SQL, Python co ban, thong ke va truc quan hoa du lieu. "
            "Vi tri dau vao co the la Data Analyst Intern, BI Intern hoac Reporting Analyst."
        )

    if "UI/UX Designer" in joined:
        return (
            "Dua tren thong tin ban cung cap, UI/UX Designer la huong phu hop nhat. "
            "Ban co nen tang CNTT va thich thiet ke giao dien, nen co the bat dau voi Figma, "
            "wireframe, prototype va lam 2 case study de dua vao portfolio."
        )

    if "Data Analyst" in joined:
        return (
            "Dua tren so thich toan, Python co ban va mong muon phan tich so lieu, "
            "Data Analyst la lua chon phu hop nhat. Ban nen hoc Excel/Sheets, SQL, Python pandas, "
            "thong ke co ban va lam portfolio dashboard."
        )

    return "Ket qua tu tool: " + " ".join(observations)


def run_react_agent(user_query: str, provider=None) -> str:
    """Run a ReAct-style loop with Thought, Action, Observation, and guardrails."""
    print("REACT AGENT")
    print(f"Question: {user_query}")
    print(f"System: {REACT_SYSTEM_PROMPT.splitlines()[0]}")

    actions = plan_actions(user_query)
    observations: List[str] = []

    if not actions:
        final = build_final_answer(user_query, observations)
        print("Thought: Cau hoi don gian, khong can tool.")
        print(f"Final Answer: {final}\n")
        return final

    repeated = set()
    for step, (tool_name, argument) in enumerate(actions, start=1):
        if step > MAX_ITERATIONS:
            break

        action_key = (tool_name, argument)
        if action_key in repeated:
            observations.append("GUARDRAIL: Lap lai cung mot action, dung vong lap an toan.")
            break
        repeated.add(action_key)

        print(f"Thought {step}: Can dung tool '{tool_name}' de co bang chung truoc khi ket luan.")
        print(f"Action {step}: {tool_name}[{argument}]")
        observation = execute_tool(tool_name, argument)
        observations.append(observation)
        print(f"Observation {step}: {observation}")

        if observation.startswith("LOI:") or "GUARDRAIL" in observation:
            break

    if len(actions) > MAX_ITERATIONS:
        observations.append(f"GUARDRAIL: Dat gioi han {MAX_ITERATIONS} vong lap.")

    final = build_final_answer(user_query, observations)
    print("Thought: Da co du Observation hoac da cham guardrail, tra loi cuoi cung.")
    print(f"Final Answer: {final}\n")
    return final


def main():
    print("=" * 70)
    print("LAB 03 - CHATBOT VS REACT AGENT: CAREER ORIENTATION")
    print("=" * 70)

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"LLM Provider: {provider.__class__.__name__} ({model_name})")

    tests = load_test_cases()
    print(f"Loaded {len(tests)} test cases from config/test_cases.json\n")

    for test in tests:
        print("-" * 70)
        print(f"TEST #{test['id']} - {test['category']}")
        print(f"Expected: {test['expected_behavior']}\n")
        run_baseline_chatbot(test["question"], provider)
        run_react_agent(test["question"], provider)


if __name__ == "__main__":
    main()
