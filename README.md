# Build a MCP Server 
A complete walkthrough on how to build a MCP server to serve a trained Random Forest model and integrate it with Bee Framework for ReAct interactivity.

## See it live and in action 📺
<a href="https://www.linkedin.com/posts/nicholasrenotte_mcp-servers-make-tools-a-bunch-easier-for-activity-7305748751162163200-dIEn?utm_source=share&utm_medium=member_desktop&rcm=ACoAABbxZgUBrud9C531KZPQHCs2riXCiv9Av2A"><img src="https://i.imgur.com/Y2LN9dd.png"/></a>

# Startup MCP Server 🚀
1. Clone this repo `git clone https://github.com/nicknochnack/BuildMCPServer`
2. To run the MCP server\
`cd BuildMCPServer`\
`uv venv`\
`source .venv/bin/activate`\
`uv add .`\
`uv add ".[dev]"`\
`uv run mcp dev faq_mcp_server.py`
3. To run the agent, in a separate terminal, run:\
`source .venv/bin/activate`\
`uv run faq_agent.py`

# Startup FastAPI Hosted ML Server 
`git clone https://github.com/nicknochnack/CodeThat-FastML`\
`cd CodeThat-FastML`\
`pip install -r requirements.txt`\
`uvicorn mlapi:app --reload`\
Detailed instructions on how to build it can also be found <a href="https://youtu.be/C82lT9cWQiA?si=dIsL6eM1lUMAVcf0">here</a></br>


# Other References 🔗 </br>
- <a href="https://github.com/RGGH/mcp-client-x/blob/main/src/client/mcp_client.py">Building MCP Clients (used in singleflow agent)</a></br>
- <a href="https://www.youtube.com/watch?v=C82lT9cWQiA&t=1003s ">Original Video where I build the ML server</a>


# Who, When, Why?
👨🏾‍💻 Author: Nick Renotte <br />
📅 Version: 1.x<br />
📜 License: This project is licensed under the MIT License </br>

#sample payload
[
    {
        "YearsAtCompany": 10,
        "EmployeeSatisfaction": 0.99,
        "Position": "Non-Manager",
        "Salary": 5
    }
]