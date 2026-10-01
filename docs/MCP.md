# Servidor MCP de mapeo

`src/mcp_server.py` inicia un servidor MCP local por `stdio` y registra una sola
herramienta:

```text
create_repository_map(repo_path: str)
```

`repo_path` debe ser la ruta absoluta a la **raíz** de un repositorio Git. Una
llamada procesa un repositorio; para mapear todos los proyectos de una carpeta,
el agente debe enumerar sus repositorios Git y llamar la herramienta por cada
uno. La herramienta escribe documentación en el repositorio elegido, por lo
que el cliente MCP necesita permiso de escritura allí.

## Resultado y archivos

El resultado incluye nombre y ruta del repositorio, rama y commit locales,
cantidad de archivos inventariados, proyectos detectados, advertencias y la
lista `changed_files`. El servidor escribe solo estos archivos de la raíz:

| Archivo | Acción |
| --- | --- |
| `REPOSITORY_MAP.md` | Crea o actualiza el inventario generado. Rechaza un mapa existente que no tenga su marcador de generación. |
| `AGENTS.md` | Crea o agrega una referencia acotada al mapa; conserva las instrucciones humanas. |
| `CLAUDE.md` | Hace lo mismo para agentes que consultan este archivo. |

Las llamadas repetidas son idempotentes cuando el repositorio no ha cambiado.
El mapeo lee archivos versionados y nuevos no ignorados, hasta 50 000 archivos,
y limita la lectura individual de manifiestos a 512 KiB. Excluye directorios de
compilación y dependencias instaladas; no copia valores de configuración ni
credenciales. Un proyecto, paquete o punto de entrada declarado es evidencia
estática, no una afirmación sobre el ambiente desplegado.

## Ejecución

Requiere Python 3.11+, Git y `mcp>=2.2,<3`. Un entorno virtual no es obligatorio.
El comando del servidor es el intérprete Python con `mcp` instalado y su
argumento es la ruta absoluta de `src/mcp_server.py`. En esta instalación, la
configuración MCP existente apunta a `.venv\Scripts\python.exe`; conserva ese
entorno o ajusta la ruta del intérprete al cambiar de instalación. Reinicia el
cliente MCP después de modificar el servidor para actualizar la lista de
herramientas.

Para inspeccionar el resultado sin escribir en un repositorio:

```powershell
& .\.venv\Scripts\python.exe src\main.py --repo 'C:\Repos\MiProyecto'
```

Para escribir los archivos sin cliente MCP:

```powershell
& .\.venv\Scripts\python.exe src\main.py --repo 'C:\Repos\MiProyecto' --write
```

Para probar la herramienta MCP sin modificar proyectos reales:

```powershell
& .\.venv\Scripts\python.exe scripts\smoke_mcp.py
```

El smoke crea un repositorio Git temporal, comprueba que solo está registrada
`create_repository_map`, la invoca y verifica los tres archivos documentales.
