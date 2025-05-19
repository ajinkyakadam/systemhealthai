from enum import Enum
from typing import Optional, List
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from systemhealthai.prompts import Prompts
from rich.console import Console

# Create console for rich output
console = Console()

class ShaiAIAgent:
    """Agent for system health monitoring and troubleshooting."""
    
    def __init__(self, model: Optional[str] = "o4-mini", provider: Optional[str] = "openai"):
        self.config_file = "example_mcp_server_config.json"
        self.client = None
        self.agent = None
        self.model = model
        self.provider = provider
        self.llm = self.set_llm()
        
    
    def set_llm(self):
        """ 
        Set the LLM based on the provider and model.
        """
        if self.provider.lower() == 'openai':
            return ChatOpenAI(model=self.model)
        
        # TODO: add support for other providers anthropic, local llms, groq
    
    async def initialize(self) -> bool:
        """Initialize the MCP client and agent."""
            
        self.client = MCPClient.from_dict(self.config_file)

        # Initialize the MCP client
        max_steps = 30
        self.agent = MCPAgent(
            llm=self.llm, 
            client=self.client, 
            max_steps=max_steps,
            verbose=True,
            memory_enabled=True,
            use_server_manager=True
        )
        return True
    
    async def run_query(self, query_params: dict) -> str:
        """Run a query using the initialized agent."""
        prompt = Prompts()
        if not self.agent:
            console.print("[bold red]Agent not initialized. Run initialize() first.[/bold red]")
            return "Error: Agent not initialized"
        
        nodename= query_params.get("nodename")
        
        console.print(f"[bold blue] Running query for node: {nodename}[/bold blue]")
            
        try:
            result = await self.agent.run(prompt.get_prometheus_prompt_for_node_metrics(query_params))
            return result
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    async def close(self):
        """Close all MCP sessions."""
        if self.client and self.client.sessions:
            await self.client.close_all_sessions()
