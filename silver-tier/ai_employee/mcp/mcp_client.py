import json
import asyncio
from typing import Optional
from mcp import ClientSession
from contextlib import AsyncExitStack
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import( ListToolsResult, CallToolResult, ListResourcesResult, 
ListResourceTemplatesResult, ReadResourceResult, ListPromptsResult,  GetPromptResult)

class MCPClient:
    def __init__(self, server_url):
        self._server_url : str = server_url
        self._session: Optional[ClientSession] = None
        self._exit_stack:AsyncExitStack= AsyncExitStack()

    async def connection(self):
        _read, _write, _ = await self._exit_stack.enter_async_context(
            streamablehttp_client(self._server_url)
        )
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_read,_write)
        )
        await self._session.initialize()
        return self._session
    
    async def Cleanup(self):
        await self._exit_stack.aclose()

    async def __aenter__(self):
        await self.connection()
        return self
    
    async def __aexit__(self,*args):
        await self.Cleanup()
        self._session = None

    # Tools
    async def tool_list(self)-> ListToolsResult:
        assert self._session, "Session Not Found"
        res = await self._session.list_tools()
        return res.tools
    
    async def tool_call(self, tool_name:str, arguments:dict[str,any])->CallToolResult:
        assert self._session, "Session Not Found"
        res = await self._session.call_tool(name=tool_name, arguments=arguments)
        return res.content
    
 

async def main():
    async with MCPClient("http://localhost:8000/mcp") as client:
        print("-"*100)
        tool_list = await client.tool_list()
        for tool in tool_list:
            print("Tools : ", tool.name)


if __name__ == "__main__":
    asyncio.run(main())