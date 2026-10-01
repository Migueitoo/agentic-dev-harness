# Repository Mapper MCP

Este proyecto inspecciona un repositorio Git local y crea un mapa factual para
agentes. Conserva una sola herramienta MCP: `create_repository_map(repo_path)`.
Cada llamada trabaja sobre **un repositorio** y escribe únicamente en su raíz:

- `REPOSITORY_MAP.md`: inventario generado de lenguajes, composición, manifiestos,
  proyectos .NET, referencias, paquetes, proyectos Node/Python/Go/Maven y puntos de
  entrada candidatos.
- `AGENTS.md` y `CLAUDE.md`: una referencia corta al mapa, conservando el
  contenido que ya tengan.

El inventario se construye con Git y analizadores locales de manifiestos. No
utiliza embeddings, rerankers, modelos ni tokens de IA. El mapa describe el
árbol de trabajo actual; no prueba el despliegue ni el flujo de ejecución.
La herramienta se niega a reemplazar un `REPOSITORY_MAP.md` que no haya sido
generado por ella.

## Instalación

Requiere Python 3.11 o posterior y Git. La única dependencia Python externa es
`mcp`:

```powershell
python -m pip install -r requirements.txt
```

Un entorno virtual **no es obligatorio**, pero conviene aislar `mcp`. Si Codex
ya está configurado para ejecutar `.venv\Scripts\python.exe`, conserva ese
entorno o actualiza la ruta del intérprete en su configuración MCP. El entorno
actual puede seguir usándose después de quitar las dependencias de modelos del
proyecto.

## Vista previa local

```powershell
& .\.venv\Scripts\python.exe src\main.py --repo 'C:\Repos\MiProyecto'
```

Este comando imprime el mapa y no escribe en el repositorio. Para producir los
tres archivos documentales sin usar un cliente MCP:

```powershell
& .\.venv\Scripts\python.exe src\main.py --repo 'C:\Repos\MiProyecto' --write
```

## Uso desde un agente

La interfaz y sus efectos de escritura están detallados en [docs/MCP.md](docs/MCP.md).

El servidor MCP por `stdio` sigue siendo `src/mcp_server.py`. En Codex, Claude
Code u OpenCode, configura el servidor para ejecutar el Python que tenga
instalada la dependencia `mcp`, con la ruta absoluta de ese archivo como
argumento. La configuración MCP existente puede continuar apuntando al mismo
archivo; reinicia el cliente para que detecte la nueva herramienta.

Desde una conversación abierta en `C:\Repos`, indica al agente que enumere los
repositorios Git inmediatos y llame `create_repository_map` **una vez por
repositorio**, pasando su ruta absoluta. El agente puede revisar cada resultado
antes de continuar. Esta herramienta escribe documentación en el repositorio
seleccionado, así que el cliente debe tener permiso de escritura allí.

Por ejemplo:

> Recorre los repositorios Git hijos de `C:\Repos`. Para cada uno llama la
> herramienta MCP `create_repository_map` con su ruta absoluta. Al terminar,
> informa qué archivos cambió cada llamada y cuáles repositorios fallaron.
> No hagas commits ni modifiques código fuente.

## Comprobación

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
& .\.venv\Scripts\python.exe scripts\smoke_mcp.py
```

La prueba MCP utiliza un repositorio Git temporal; no modifica los proyectos de
`C:\Repos`.

## Alcance del análisis

El inventario considera archivos versionados y archivos nuevos no ignorados;
descarta carpetas de compilación, dependencias instaladas y archivos con nombres
sensibles. Los valores de configuración y las credenciales no se copian al mapa.
Las dependencias se presentan como declaraciones de sus manifiestos, sin
asegurar que estén instaladas o en uso. Si cambia la rama o el código, vuelve a
ejecutar la herramienta para actualizar el mapa.
