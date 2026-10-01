# Contexto para Claude

Este proyecto es un mapeador de repositorios Git. Lee primero [AGENTS.md](AGENTS.md)
y [docs/MCP.md](docs/MCP.md); ambos describen la implementación y las reglas
actuales.

La única herramienta MCP es `create_repository_map(repo_path)`. Recibe la ruta
absoluta de **un** repositorio Git, genera `REPOSITORY_MAP.md` y deja una
referencia breve en sus `AGENTS.md` y `CLAUDE.md`, preservando el contenido
existente. El comando `python src/main.py --repo <ruta>` permite previsualizar
el mapa sin escribir; `--write` aplica los mismos cambios que la herramienta.

El análisis usa Git y metadatos de manifiestos; no necesita modelos ni RAG.
Para validar cambios en el mapeador, utiliza los tests y el smoke MCP con
repositorios temporales. No escribas en otros proyectos durante esas pruebas.
