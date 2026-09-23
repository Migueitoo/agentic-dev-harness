\# Agentic Development Harness



Objetivo:



Construir un harness agéntico reutilizable para trabajar con repositorios locales usando Codex, Claude Code y OpenCode.



El harness debe ayudar a:



\- descubrir la estructura de un repositorio;

\- recuperar contexto relevante;

\- integrar CodeGraphContext;

\- incorporar RAG;

\- preparar contexto para agentes;

\- evaluar la calidad del contexto recuperado;

\- soportar workflows de desarrollo con agentes;

\- mantener independencia del modelo utilizado.

Servidor MCP local: consulta [docs/MCP.md](docs/MCP.md) para configurar y
probar la herramienta `search_repository_context`.



\## Primera etapa



Construir un Repository Scanner capaz de analizar un repositorio local y producir una representación estructurada de su contenido.

