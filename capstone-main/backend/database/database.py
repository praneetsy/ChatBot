import sqlite3
from typing import Optional
from pydantic import BaseModel

class AgentData(BaseModel):
    '''
    Class to represent the agent data and capabilities.
    '''
    name: str
    capability: Optional[str] = "" # Think of agent capabilities as the skills or expertise of the agent or a brief description of what the agent can do.
    description: Optional[str] = "" # A brief description of the agent.
    specialization_keywords: Optional[list[str]] = [] # Keywords that describe the agent's specializations.
    
    def __str__(self):
        return f"AgentData(name={self.name}, capability={self.capability}, description={self.description}, specialization_keywords={self.specialization_keywords})"
    
    def to_dict(self):
        return {
            "name": self.name,
            "capability": self.capability,
            "description": self.description,
            "specialization_keywords": self.specialization_keywords
        }

class SQLLiteDatabase():
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
    
    
    def get_all_agents(self) -> list[AgentData]:
        '''
        Get all agents from the database
        '''
        self.cursor.execute("SELECT name, capability, description, specialization_keywords FROM ai_agent")
        data = self.cursor.fetchall()
        agents = []
        for row in data:
            agent = AgentData(name=row[0], capability=row[1], description=row[2], specialization_keywords=row[3])
            agents.append(agent)
        return agents
        
    def get_agents(self, agent_names : set) -> list[AgentData]:
        '''
        Get agents from the database based on the agent names
        '''
        agents = []
        for name in agent_names:
            self.cursor.execute("SELECT name, capability, description, specialization_keywords FROM ai_agent WHERE name=?", (name,))
            data = self.cursor.fetchone()
            if data:
                agent = AgentData(name=data[0], capability=data[1], description=data[2], specialization_keywords=data[3])
                agents.append(agent)
        return agents