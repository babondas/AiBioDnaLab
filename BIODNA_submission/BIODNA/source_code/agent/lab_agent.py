"""The BIODNA agent: an LLM that chooses which tool to use before it answers.

    Question
       |
    chain = prompt | model_with_tools
       |
    LLM picks a tool:  search_lab_documents / lookup_table_rows / list_lab_documents
       |                         |
       |                    the tool returns passages with sources
       |                         |
    LLM reads them  <------------+
       |
    LLM writes the answer with sources

Usage:
    agent = LabAgent(vector_store)
    answer = agent.ask("Which tube is used for HbA1c?")
    print(answer.text)
"""
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from source_code.agent.agent_instructions import FINAL_ANSWER_INSTRUCTION, SYSTEM_PROMPT
from source_code.agent.agent_tools import LabTools
from source_code.agent.llm_connection import create_chat_model
from source_code.common import config
from source_code.common import user_messages as messages
from source_code.common.data_models import AgentAnswer
from source_code.rag_pipeline.step4_vector_store import VectorStore


class LabAgent:

    def __init__(self, vector_store: VectorStore):
        # 1. The tools the LLM may call
        self.lab_tools = LabTools(vector_store)
        tools = self.lab_tools.create_tools()
        self.tools_by_name = {}
        for one_tool in tools:
            self.tools_by_name[one_tool.name] = one_tool

        # 2. The prompt: rules + question + the agent's steps so far
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
            MessagesPlaceholder("agent_steps"),
        ])

        # 3. The chain: fill the prompt, then send it to the LLM (which knows the tools)
        model_with_tools = create_chat_model().bind_tools(tools)
        self.chain = prompt | model_with_tools

    # ---------------------------------------------------------------
    # Public method: the app calls this
    # ---------------------------------------------------------------
    def ask(self, question: str) -> AgentAnswer:
        self.lab_tools.clear_history()
        agent_steps = []          # the LLM's tool calls and the tool results, in order

        for attempt in range(config.MAX_AGENT_STEPS):
            llm_reply = self.chain.invoke({"question": question, "agent_steps": agent_steps})
            agent_steps.append(llm_reply)

            if self._is_final_answer(llm_reply):
                return self._build_answer(llm_reply.content)

            self._run_requested_tools(llm_reply, agent_steps)

        # The LLM used all its tool calls without answering: ask it to answer with what it found
        final_text = self._ask_for_final_answer(question, agent_steps)
        return self._build_answer(final_text)

    # ---------------------------------------------------------------
    # Private helper methods
    # ---------------------------------------------------------------
    def _ask_for_final_answer(self, question: str, agent_steps: list) -> str:
        """Search limit reached: one last call, telling the LLM to answer without more tools."""
        final_steps = agent_steps + [HumanMessage(content=FINAL_ANSWER_INSTRUCTION)]
        llm_reply = self.chain.invoke({"question": question, "agent_steps": final_steps})

        # Any tool call in this reply is ignored; only its text is used
        if llm_reply.content.strip() == "":
            return messages.AGENT_NO_CLEAR_ANSWER
        return llm_reply.content

    def _build_answer(self, text: str) -> AgentAnswer:
        """Packs the answer text with the sources and tools used for this question."""
        return AgentAnswer(
            text=text,
            sources=self.lab_tools.sources_used,
            tools_used=self.lab_tools.tools_used,
        )

    def _is_final_answer(self, llm_reply: AIMessage) -> bool:
        """If the LLM did not ask for a tool, its reply is the final answer."""
        return len(llm_reply.tool_calls) == 0

    def _run_requested_tools(self, llm_reply: AIMessage, agent_steps: list):
        """Runs every tool the LLM asked for and adds each result to the agent's steps."""
        for tool_call in llm_reply.tool_calls:
            requested_tool = self.tools_by_name.get(tool_call["name"])

            if requested_tool is None:
                tool_result = f"There is no tool called '{tool_call['name']}'."
            else:
                tool_result = requested_tool.invoke(tool_call["args"])

            agent_steps.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))