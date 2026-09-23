# Servidor MCP local

El harness expone una herramienta de solo lectura llamada
`search_repository_context`. Recibe la ruta absoluta de un repositorio local,
una tarea y un presupuesto aproximado de tokens. Devuelve los elementos del
`ContextBundle` existente; no cambia el ranking ni modifica archivos del repo.

## Preparación

Instala las dependencias con el Python que usará el cliente MCP:

```text
python -m pip install -r requirements.txt
```

En Windows, puedes usar `py` en lugar de `python`. La primera consulta con una
tarea puede descargar los modelos de embeddings y reranking si aún no están
en la caché local. Para uso sin conexión, precárgalos antes.

## Prueba local

Desde la raíz del harness:

```text
python scripts/smoke_mcp.py --repo "RUTA_ABSOLUTA_DEL_REPO" --task "Describir una tarea de desarrollo"
```

El script lanza el servidor como subproceso `stdio`, descubre la herramienta,
la llama y muestra únicamente los tipos y rutas de los elementos recibidos.
No imprime el contenido del código recuperado.

## Configuración en un cliente MCP

Configura un servidor local de transporte `stdio` con estos dos valores:

```text
command = RUTA_ABSOLUTA_DEL_PYTHON_CON_DEPENDENCIAS
args    = [RUTA_ABSOLUTA_DEL_HARNESS/src/mcp_server.py]
```

Para averiguar la ruta exacta de Python:

```text
python -c "import sys; print(sys.executable)"
```

En Windows también puedes ejecutar ese comando con `py`. Cada cliente tiene
su propio formato de configuración, pero el comando y el argumento son los
mismos. No fijes aquí una ruta del repositorio de trabajo: se pasa en cada
llamada como `repo_path`, lo que permite usar el servidor con repositorios
distintos.

La herramienta acepta:

- `repo_path`: ruta absoluta al repositorio, en la máquina donde corre el servidor;
- `task`: descripción no vacía de la tarea;
- `max_tokens`: presupuesto aproximado positivo, por defecto 2000.

El resultado contiene `repository_name`, `task`, `max_tokens` e `items`. Cada
item incluye `kind`, `source`, `priority` y `content`. `priority` es una
prioridad interna, no una probabilidad ni una garantía de relevancia.

El transporte `stdio` no abre un servidor de red. Aun así, el cliente que
invoque la herramienta recibirá fragmentos del repositorio: úsalo únicamente
con clientes y repositorios autorizados. Las reglas de seguridad y exclusión
de archivos sensibles todavía son una fase pendiente del harness.
