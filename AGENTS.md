# Repository Mapper

Este repositorio implementa un mapeador local de repositorios Git para agentes.
Lee [README.md](README.md) para el uso y [docs/MCP.md](docs/MCP.md) para el
contrato de la herramienta MCP.

## Estructura actual

- `src/mcp_server.py`: servidor MCP por `stdio`; expone únicamente
  `create_repository_map(repo_path)`.
- `src/repository/mapping.py`: inventario Git, lectura de manifiestos, generación
  de `REPOSITORY_MAP.md` y actualización acotada de `AGENTS.md` y `CLAUDE.md` del
  repositorio objetivo.
- `src/repository/detectors/dotnet.py` y `src/repository/models.py`: metadatos de
  proyectos .NET, referencias y paquetes.
- `src/main.py`: vista previa de solo lectura; `--write` ejecuta el mismo mapeo
  con escritura sin cliente MCP.
- `tests/test_repository_mapping.py` y `scripts/smoke_mcp.py`: pruebas con Git
  temporal.

## Reglas de trabajo

- El propósito de este proyecto es el **mapeo estructural**. No reintroduzcas
  búsqueda para bugs, RAG, embeddings o clasificación de solicitudes como parte
  del mapeo salvo que el usuario lo pida.
- Distingue hechos declarados en archivos de inferencias. Un manifiesto no
  prueba qué versión corre en un ambiente ni qué código se ejecutó.
- El mapa generado no debe copiar credenciales ni valores de configuración.
  Conserva contenido humano preexistente en `AGENTS.md` y `CLAUDE.md`; no
  sobrescribas un `REPOSITORY_MAP.md` no generado por esta herramienta.
- Para probar escrituras, usa repositorios Git temporales. No mapees ni cambies
  otros proyectos de `C:\Repos` durante las pruebas de este código.
- Python 3.11+, Git y `mcp` son los requisitos. El `.venv` es opcional, aunque
  la configuración MCP local puede apuntar a su intérprete.

## Verificación

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe scripts\smoke_mcp.py
```
