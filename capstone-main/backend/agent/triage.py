import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from database.database import SQLLiteDatabase
from database.vector_store import SQLLiteVectorStore, ChromaDBVectorStore
from pydantic import BaseModel, Field
from typing import List


class TriageAgent:
    def __init__(self, model="qwen2.5-coder-7b-instruct", temperature=0):
        self.model = model
        self.temperature = temperature
        self.llm = None  # LLM config instance for selecting the appropriate agent
        self.clarification_llm = (
            None  # LLM config instance for asking for clarification
        )
        self.conversation_history = []  # List of messages in the conversation
        self.generated_conversation_log = (
            []
        )  # List of actual messages in the conversation which include system and human messages
        self.current_agent = None  # The current agent
        self.agents = ["$OTHER_AGENT"]  # List of agents
        self.db = SQLLiteDatabase(
            "database/sqllite.db"
        )  # Database instance which stores the agent names
        self.vector_db = ChromaDBVectorStore(
            "database/chromadb"
        )  # Vector database instance

    def load_agent(self):
        # Read all metadata files from agent metadata directory
        # Load each metadata file into an agent
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            model_kwargs={
                "response_format": "json_schema",
            },
        )
        self.agents = self.db.get_all_agents()

        # Define the JSON schema for the query clarification
        other_json_schema = {
            "title": "Query Clarification",
            "description": "Schema for generating a better query or asking for clarification based on the user query.",
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "additionalProperties": False,
        }

        self.clarification_llm = self.llm.with_structured_output(
            other_json_schema, method="json_schema"
        )

        # Define the JSON schema for the agent selection
        json_schema = {
            "title": "Agent Selection",
            "description": "Schema for selecting the appropriate agent based on the query.",
            "type": "object",
            "properties": {
                "agent": {
                    "type": "string",
                    "enum": [agent.name for agent in self.agents],
                }
            },
            "additionalProperties": False,
        }

        self.llm = self.llm.with_structured_output(json_schema, method="json_schema")
        self.current_agent = self.agents[0]

    def add_human_message(self, message):
        """
        Add a human message to the conversation history
        """
        human_message = HumanMessage(content=message)
        self.conversation_history.append(human_message)
        self.generated_conversation_log.append(human_message)

    def add_system_message(self, message):
        """
        Add a system message to the conversation history
        """
        system_message = SystemMessage(content=message)
        self.conversation_history.append(system_message)
        self.generated_conversation_log.append(system_message)

    def remove_last_system_message(self):
        """
        Remove the last system message from the conversation history
        """
        for i in range(len(self.conversation_history) - 1, -1, -1):
            if isinstance(self.conversation_history[i], SystemMessage):
                self.conversation_history.pop(i)
                break

    def remove_last_human_message(self):
        """
        Remove the last human message from the conversation history
        """
        for i in range(len(self.conversation_history) - 1, -1, -1):
            if isinstance(self.conversation_history[i], HumanMessage):
                self.conversation_history.pop(i)
                break

    def get_conversation_history(self):
        """
        Get the conversation history
        """
        return self.conversation_history

    def get_generated_conversation_log(self):
        """
        Get the generated conversation log
        """
        return self.generated_conversation_log

    def set_current_agent(self, agent_name):
        """
        Set the current agent based on the agent name provided
        This method goes through the list of agents and sets the current agent to the one with the matching name
        if the agent is not found, it raises a ValueError
        """
        agent = None
        for a in self.agents:
            if a.name == agent_name:
                agent = a
                break
        if not agent:
            raise ValueError(f"Agent with name {agent_name} not found.")
        self.current_agent = agent

    def generate_better_query_or_ask_for_clarification(self, query):
        """
        Generate a better query or ask for clarification based on the user query
        """
        self.add_system_message(
            f"""Generate a better query or ask for clarification based on the user query. 
                Usually, if the query is a sensible sentence and not jargon or has some sensible keywords, then it is okay to proceed with the query.
                If you think the query is like "what is the internet" or "what is a computer", "Hello", "How are you", then it is better to ask for clarification and return $CLARIFY.
                If you think the query is not clear and doesn't make sense or have enough context for a RAG model to answer, return $CLARIFY.
                If you think the query is okay - write the query in a format which will perform better in the RAG model.
                In any case, do not response empty or with a single word. Always provide a sensible response.
                Now, if the query is OKAY, rewrite the query and return that as the response. If the query is not okay, return $CLARIFY. Like re-write the user query instead of answering the question.
                The user query is: {query}""",
        )
        self.add_human_message(query)
        res = self.clarification_llm.invoke(self.conversation_history)

        # This removes the messages to keep the conversation history clean
        self.remove_last_system_message()
        self.remove_last_human_message()
        return res["text"]

    def check_if_current_agent_can_answer(self, query) -> bool:
        """
        Check if the current agent can answer the query.
        This will return True if the current agent can answer the query
        and False if the current agent cannot answer the query.
        """
        self.add_system_message(
            f"""Determine if the question needs a redirection to another agent or the current agent is capable of answering it. 
                If the current agent is capable of answering it, then proceed with the current agent.
                Usually, internet_search is not the answer and try to use more of the specialized agents which we have
                The current agent is {str(self.current_agent)}. Here are the other agents for your context. {str(self.agents)} - DO NOT USE THESE NAMES IN THE RESPONSE.
                Usually, if the current agent is a specialized agent, then it is better to proceed with the current agent.
                So for example, if the current agent is 'agent1', then the response should be 'agent1' or '$OTHER_AGENT' to switch to another agent. 
                ONLY ANSWER WITH THE CURRENT AGENT NAME OR $OTHER_AGENT. DO NOT ANSWER WITH ANY OTHER AGENT NAME. Be intelligent and think if the current agent can answer the question or not.
                BE VERY STRICT AND CAREFUL THINKING IF THE CURRENT AGENT CAN ANSWER THE QUESTION OR NOT. IT IS OKAY TO SWITCH IF IN DOUBT.
        """,
        )
        self.add_human_message(query)
        res = self.llm.invoke(self.conversation_history)
        json_res = res
        print("FIRST STEP: ", json_res)
        self.remove_last_system_message()
        self.remove_last_human_message()
        if json_res["agent"] == self.current_agent.name:
            return True
        if json_res["agent"] == "$OTHER_AGENT":
            return False
        return False

    def get_relevant_agents(self, query):
        """
        Get relevant agents based on the query.
        This method uses the vector database to search for similar agents based on the query.
        The top 3 agents are selected and the LLM is asked to choose the most relevant agent.
        This also returns the top documents from the search results and other agents that were not selected.
        """
        # We only run a similarity search on the latest query because the latest query is the most important and other queries were already
        # used to determine if the current agent can answer the query or not.
        results = self.vector_db.similarity_search_agents(query, k=3)
        if results['ids'] == []:
            top_documents_ids = []
        else:
            top_documents_ids = results["ids"]
        top_documents = results["documents"]
        if not top_documents:
            # If no relevant agents are found, return the current agent or internet_search
            self.add_system_message(
                f"""
                No relevant agents found. Proceed internet_search based on the query. Current agent is {self.current_agent.name}.
                internet_search is usually preferred if no relevant agents are found but if the current agent has any capability to answer the question, then proceed with the current agent.
                ONLY CHOSE BETWEEN THE CURRENT AGENT OR INTERNET_SEARCH. DO NOT CHOOSE ANY OTHER AGENT. 
                """
            )
            self.add_human_message(query)
            res = self.llm.invoke(self.conversation_history)
            selected_agent = res["agent"]
            res = {"relevant_agent": selected_agent, "other_agents": []}
            self.set_current_agent(res["relevant_agent"])
            res["top_documents"] = top_documents_ids
            res["switched"] = True
            res["query_used"] = query
            self.remove_last_system_message()
            self.remove_last_human_message()
            return res
        agents_from_search = set()
        retrived_agents = set()
        for metadata in results["metadatas"]:
            retrived_agents.add(metadata["agent_name"])
        for agent in self.agents:
            if agent.name in retrived_agents:
                agents_from_search.add(agent.name)
        agents = self.db.get_agents(agents_from_search)
        self.add_system_message(
            f"""
            Determine the most relevant agent based on the conversation history. If the current agent is capable of answering the question, proceed with the current agent.
            The specialized available agents are: {str(agents)}.
            If there are no relevant agents, then proceed with the current agent or internet_search. Choose wisely between the both. 
            ONLY GIVE IMPORTANCE TO THE NEWEST HUMAN MESSAGE. YOU CAN USE THE CONTEXT OF THE PREVIOUS MESSAGES TO DETERMINE THE RELEVANT AGENT BUT LATEST MESSAGE IS THE MOST IMPORTANT.
            ONLY CHOOSE FROM THESE AGENTS. DO NOT CHOOSE FROM ANY OTHER AGENT
            """
        )
        self.add_human_message(query)
        res = self.llm.invoke(self.conversation_history)
        selected_agent = res["agent"]
        other_agents = [agent for agent in agents if agent.name != selected_agent]
        res = {"relevant_agent": selected_agent, "other_agents": other_agents}
        self.set_current_agent(res["relevant_agent"])
        res["top_documents"] = top_documents_ids
        res["switched"] = True
        res["query_used"] = query
        self.remove_last_system_message()  # We do not require this message in the conversation history
        self.remove_last_human_message()  # We do not require this message in the conversation history
        return res

    def get_relevant_agents_from_query(self, query):
        """
        This method is the main method which is called from the API to get relevant agents based on the query.
        The method first generates a better query or asks for clarification based on the user query.
        If the better query is generated, it checks if the current agent can answer the query.
        If the current agent cannot answer the query, it gets relevant agents based on the query.
        """
        better_query = self.generate_better_query_or_ask_for_clarification(query)
        if better_query == "$CLARIFY":
            return {
                "relevant_agent": None,
                "other_agents": [],
                "switched": False,
                "clarify": True,
            }

        can_answer = self.check_if_current_agent_can_answer(better_query)
        print("CAN ANSWER: ", can_answer)
        if not can_answer:
            agents = self.get_relevant_agents(better_query)
            return agents
        return {
            "relevant_agent": self.current_agent.name,
            "other_agents": [],
            "switched": False,
            "query_used": better_query,
        }
