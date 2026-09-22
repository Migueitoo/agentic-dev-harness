AGENTIC SOFTWARE ENGINEER + RAG

PLAN DE ACCIÓN / RUTA DE APRENDIZAJE



Objetivo general

\----------------

Construir un Agentic Development Harness independiente del modelo, capaz de trabajar con herramientas como Codex, Claude Code u OpenCode, y darle contexto relevante de un repositorio mediante:



\- Repository Discovery

\- Context Engineering

\- Retrieval / RAG

\- MCP

\- Workflows agentic

\- Evaluaciones

\- Seguridad / gobernanza

\- Optimización multi-modelo





ARQUITECTURA OBJETIVO

\---------------------



Developer

&#x20;  ↓

Codex / Claude Code / OpenCode

&#x20;  ↓

Agentic Development Harness

&#x20;  ↓

Context Engine

&#x20;  ↓

Retrieval / RAG

&#x20;  ↓

Repository + CodeGraphContext + Git + Docs + Instructions

&#x20;  ↓

Contexto relevante

&#x20;  ↓

Agente





==================================================

FASE 1 - REPOSITORY DISCOVERY

==================================================



ESTADO: COMPLETADA



Objetivo:

Recibir cualquier repositorio y construir una representación estructurada de su composición.



Entrada:

\- Ruta del repositorio



Salida:

\- RepositoryInfo



Actualmente detectamos:



\- Nombre del repositorio

\- Ruta

\- Branch actual

\- Lenguajes

\- Frameworks

\- Capabilities

\- Archivos de contexto

&#x20; - README.md

&#x20; - AGENTS.md

&#x20; - CLAUDE.md

\- Proyectos .NET

\- SDK

\- Target Framework

\- Tipo de proyecto

&#x20; - web

&#x20; - library

&#x20; - test

\- Framework de testing

\- PackageReference

\- Versiones de paquetes

\- ProjectReference

\- Dependencias entre proyectos



Ejemplo:



FindThatBook.API

&#x20;  ├── Application

&#x20;  └── Infrastructure



Application

&#x20;  └── Domain



Infrastructure

&#x20;  └── Application



Tests

&#x20;  └── Application



Archivos principales:



src/repository/

├── models.py

├── scanner.py

└── detectors/

&#x20;   └── dotnet.py



Concepto aprendido:

El scanner responde:



"¿Qué existe realmente en este repositorio?"



Importante:

Esto NO reemplaza completamente AGENTS.md.



Scanner:

\- descubre hechos automáticamente



AGENTS.md:

\- contiene instrucciones humanas



Ejemplos:

\- convenciones

\- restricciones

\- comandos

\- arquitectura deseada

\- reglas para modificar el código



Son complementarios.





==================================================

FASE 2 - CONTEXT ENGINEERING

==================================================



ESTADO: EN PROGRESO



Objetivo:

Tomar toda la información disponible del repositorio y decidir qué contexto debe recibir un agente para una tarea concreta.



Arquitectura:



Repository

&#x20;  ↓

Scanner

&#x20;  ↓

RepositoryInfo

&#x20;  ↓

Context Engine

&#x20;  ↓

ContextBundle

&#x20;  ↓

Agente





\--------------------------------------------------

2.1 CONTEXT MODEL

\--------------------------------------------------



ESTADO: COMPLETADO



Creamos:



ContextItem



Representa una pieza de contexto.



Contiene:



\- kind

\- source

\- content

\- priority



Ejemplos:



repository\_summary

project

instructions





Creamos también:



ContextBundle



Contiene:



\- repository\_name

\- task

\- items

\- max\_tokens





\--------------------------------------------------

2.2 CONTEXT ENGINE

\--------------------------------------------------



ESTADO: COMPLETADO



Archivo:



src/context\_engine/engine.py



Responsabilidad:



El engine NO inspecciona repositorios directamente.



Su trabajo es:



\- recibir RepositoryInfo

\- recibir la tarea

\- construir piezas de contexto

\- aplicar prioridades

\- aplicar retrieval

\- aplicar presupuesto

\- producir ContextBundle



Responsabilidades actuales:



scanner.py

&#x20;   ¿Qué existe?



scoring.py

&#x20;   ¿Qué proyecto parece más relevante?



chunking.py

&#x20;   ¿Cómo divido documentos grandes?



retrieval.py

&#x20;   ¿Qué texto es relevante para la tarea?



semantic.py

&#x20;   ¿Qué contenido tiene significado similar?



budget.py

&#x20;   ¿Qué contexto cabe?



engine.py

&#x20;   ¿Cómo coordino todo?





\--------------------------------------------------

2.3 TASK-AWARE SCORING

\--------------------------------------------------



ESTADO: COMPLETADO



Archivo:



src/context\_engine/scoring.py



Objetivo:

Dar mayor prioridad a proyectos relacionados con la tarea.



Ejemplo:



Task:

"Agregar un nuevo endpoint para buscar libros"



Resultado:



API             100

Application      80

Infrastructure   80

Domain           80

Tests            70



Esto es un baseline basado en reglas.



No es RAG.



Sirve para comparar posteriormente si los mecanismos más avanzados realmente mejoran la selección.





\--------------------------------------------------

2.4 CONTEXT BUDGET

\--------------------------------------------------



ESTADO: COMPLETADO



Archivo:



src/context\_engine/budget.py



Problema:

No podemos enviar todo un repositorio al modelo.



Solución:

Definir un presupuesto máximo de contexto.



Actualmente:



DEFAULT\_CONTEXT\_BUDGET = 2000



Estimación temporal:



tokens ≈ caracteres / 4



Flujo:



items

&#x20;  ↓

ordenar por prioridad

&#x20;  ↓

estimar tokens

&#x20;  ↓

seleccionar lo que cabe



Más adelante se puede usar tokenización real.





\--------------------------------------------------

2.5 CHUNKING

\--------------------------------------------------



ESTADO: COMPLETADO



Archivo:



src/context\_engine/chunking.py



Problema anterior:



README.md

&#x20;  ↓

un ContextItem enorme



Problema:

Si no cabe completo, se pierde todo.



Solución:



README.md

&#x20;  ↓

chunking

&#x20;  ├── chunk 1

&#x20;  ├── chunk 2

&#x20;  ├── chunk 3

&#x20;  ├── chunk 4

&#x20;  └── ...



Actualmente se divide Markdown respetando encabezados.



Ejemplo:



README.md#chunk-1

README.md#chunk-2

README.md#chunk-3

...



Esto permite recuperar únicamente partes relevantes.





==================================================

FASE 3 - RETRIEVAL

==================================================



ESTADO: EN PROGRESO





\--------------------------------------------------

3.1 SIMPLE LEXICAL RETRIEVAL

\--------------------------------------------------



ESTADO: COMPLETADO



Primera versión:



Task:

"Agregar un nuevo endpoint para buscar libros"



Se comparaban palabras de la tarea contra palabras de cada chunk.



Se normalizaban:



\- mayúsculas/minúsculas

\- acentos

\- algunas formas plurales

\- stop words



Problema detectado:



coincidencia textual

&#x20;   !=

relevancia semántica





\--------------------------------------------------

3.2 BM25

\--------------------------------------------------



ESTADO: COMPLETADO



Archivo:



src/context\_engine/retrieval.py



Implementamos BM25 manualmente.



BM25 considera:



\- frecuencia de términos

\- rareza del término

\- longitud del documento

\- frecuencia del término dentro del documento



Resultado observado:



README chunk de despliegue

&#x20;   obtuvo prioridad muy alta



README chunk de flujo principal

&#x20;   obtuvo prioridad baja



Razón:



BM25 sigue siendo lexical.



Ejemplo:



Task:

"Agregar un endpoint"



Chunk:

"BookDiscoveryController"



Para BM25 esas palabras no necesariamente están relacionadas.



Aprendizaje:



BM25 mejora el lexical retrieval,

pero no entiende significado.





\--------------------------------------------------

3.3 SEMANTIC RETRIEVAL / EMBEDDINGS

\--------------------------------------------------



ESTADO: SIGUIENTE PASO / EN IMPLEMENTACIÓN



Objetivo:

Comparar significado en lugar de únicamente palabras.



Modelo local planeado:



sentence-transformers/

paraphrase-multilingual-MiniLM-L12-v2



Sin usar:

\- OpenAI API

\- Anthropic API



El modelo genera embeddings locales.



Ejemplo esperado:



"Agregar endpoint"

&#x20;       ≈

"controladores HTTP"



"buscar libros"

&#x20;       ≈

"BookDiscoveryService"



"endpoint"

&#x20;       ≈

"POST /api/book-discovery"



Archivo:



src/context\_engine/semantic.py





Experimentos:



A. BM25 solo



B. Embeddings solo



Después compararemos resultados.





==================================================

FASE 4 - HYBRID SEARCH

==================================================



ESTADO: PENDIENTE



Objetivo:

Combinar:



BM25

\+

Embeddings



Porque cada técnica resuelve problemas diferentes.



BM25:

\- excelente con nombres exactos

\- clases

\- métodos

\- identificadores

\- nombres de paquetes

\- errores

\- mensajes específicos



Embeddings:

\- excelente con significado

\- intención

\- conceptos equivalentes

\- consultas en lenguaje natural



Arquitectura:



Task

&#x20;  ↓

┌─────────────┐

│             │

BM25       Embeddings

│             │

└──────┬──────┘

&#x20;      ↓

&#x20;Hybrid Search

&#x20;      ↓

&#x20;ranking combinado





==================================================

FASE 5 - RERANKING

==================================================



ESTADO: PENDIENTE



Objetivo:

Después de obtener candidatos mediante hybrid search, volver a ordenarlos con un mecanismo más preciso.



Flujo:



Repositorio

&#x20;  ↓

muchos chunks

&#x20;  ↓

retrieval

&#x20;  ↓

Top 20

&#x20;  ↓

reranking

&#x20;  ↓

Top 5

&#x20;  ↓

Context Budget

&#x20;  ↓

ContextBundle



Esto evita gastar recursos procesando todo el repositorio.





==================================================

FASE 6 - FILE / CODE RETRIEVAL

==================================================



ESTADO: PENDIENTE



Hasta ahora estamos trabajando principalmente con:



\- metadata

\- README

\- instrucciones



El siguiente salto será recuperar código real.



Ejemplos:



Task:

"Agregar endpoint para buscar autores"



Queremos recuperar archivos como:



BookDiscoveryController.cs

BookDiscoveryService.cs

IBookDiscoveryService.cs



y no:



RandomUtility.cs

Migration123.cs

otro código irrelevante





Necesitamos:



\- detectar archivos fuente

\- construir documentos

\- agregar metadata

\- dividir código de forma inteligente

\- identificar proyecto

\- path

\- lenguaje

\- símbolos

\- relaciones





==================================================

FASE 7 - RAG PARA CÓDIGO

==================================================



ESTADO: PENDIENTE



Construiremos un índice local de código.



Cada chunk debería tener metadata como:



source

path

language

project

symbol

kind

dependencies



Ejemplo:



{

&#x20; source:

&#x20; "FindThatBook.API/Controllers/BookDiscoveryController.cs",



&#x20; project:

&#x20; "FindThatBook.API",



&#x20; language:

&#x20; "C#",



&#x20; kind:

&#x20; "class",



&#x20; symbol:

&#x20; "BookDiscoveryController"

}





El RAG debería poder responder:



"¿Dónde se implementa la búsqueda?"



"¿Qué archivos necesito modificar para agregar un endpoint?"



"¿Qué depende de BookDiscoveryService?"





==================================================

FASE 8 - CODEGRAPHCONTEXT

==================================================



ESTADO: PENDIENTE



Ya existe CodeGraphContext mediante MCP en el entorno.



Objetivo:

Combinar:



Text Retrieval

\+

Code Graph



Ejemplo:



Task

&#x20;  ↓

Retriever encuentra:

BookDiscoveryController

&#x20;  ↓

CodeGraph encuentra:

BookDiscoveryService

&#x20;  ↓

CodeGraph encuentra:

interfaces / implementaciones / callers

&#x20;  ↓

Context Engine



Esto nos permite combinar:



relevancia textual

\+

estructura real del código





==================================================

FASE 9 - RAG EXPUESTO MEDIANTE MCP

==================================================



ESTADO: PENDIENTE



Objetivo:

Que Codex, Claude Code y OpenCode puedan consultar el mismo sistema de contexto.



Ejemplo conceptual:



search\_repository\_context(

&#x20;   query="Agregar endpoint de autores"

)



Resultado:



\- archivos relevantes

\- chunks

\- proyectos

\- dependencias

\- instrucciones

\- scores





Así obtenemos:



Codex

Claude

OpenCode

&#x20;  ↓

mismo MCP

&#x20;  ↓

mismo Context Engine / RAG





==================================================

FASE 10 - AGENTIC DEVELOPMENT HARNESS

==================================================



ESTADO: PENDIENTE



Construir workflows de desarrollo.



Roles conceptuales:



Planner

Developer

Tester

Reviewer



Ejemplo:



Task

&#x20;  ↓

Planner

&#x20;  ↓

Context Retrieval

&#x20;  ↓

Developer

&#x20;  ↓

Changes

&#x20;  ↓

Tester

&#x20;  ↓

Reviewer





No necesariamente serán cuatro LLM diferentes.



Son responsabilidades / etapas del workflow.





==================================================

FASE 11 - EVALUATIONS

==================================================



ESTADO: PENDIENTE



Muy importante.



No queremos decir:



"parece que funciona mejor"



Queremos medirlo.



Compararemos:



Baseline reglas



vs



Lexical



vs



BM25



vs



Embeddings



vs



Hybrid



vs



Hybrid + Reranking





Métricas posibles:



Recall@K

Precision@K

MRR

Context relevance

Context size

Latency





Ejemplo de eval:



Task:

"Agregar endpoint"



Expected relevant context:



\- FindThatBook.API

\- BookDiscoveryController

\- BookDiscoveryService



El sistema debería recuperar esos elementos dentro del Top K.





==================================================

FASE 12 - SEGURIDAD Y GOVERNANCE

==================================================



ESTADO: PENDIENTE



Añadir controles para:



\- archivos sensibles

\- secretos

\- .env

\- claves

\- operaciones destructivas

\- comandos shell

\- acceso a producción

\- permisos

\- read-only vs write

\- branch awareness





==================================================

FASE 13 - MULTI-MODEL ROUTING

==================================================



ESTADO: PENDIENTE



El Harness debe ser independiente del modelo.



Queremos poder usar:



Codex

Claude Code

OpenCode



según:



\- tarea

\- costo

\- límites

\- rendimiento

\- contexto disponible



Sin duplicar toda la infraestructura.





==================================================

ORDEN ACTUAL DE TRABAJO

==================================================



\[COMPLETADO]

1\. Repository Scanner



\[COMPLETADO]

2\. RepositoryInfo estructurado



\[COMPLETADO]

3\. ContextItem / ContextBundle



\[COMPLETADO]

4\. Context Engine v1



\[COMPLETADO]

5\. Task-aware project scoring



\[COMPLETADO]

6\. Context Budget



\[COMPLETADO]

7\. Markdown Chunking



\[COMPLETADO]

8\. Simple lexical retrieval



\[COMPLETADO]

9\. BM25



\[ACTUAL]

10\. Semantic Retrieval con embeddings locales



\[SIGUE]

11\. Comparar BM25 vs Embeddings



\[SIGUE]

12\. Hybrid Search



\[SIGUE]

13\. Reranking



\[SIGUE]

14\. Indexar archivos de código



\[SIGUE]

15\. RAG para código



\[SIGUE]

16\. Integrar CodeGraphContext



\[SIGUE]

17\. Exponer retrieval mediante MCP



\[SIGUE]

18\. Workflows agentic



\[SIGUE]

19\. Evals



\[SIGUE]

20\. Seguridad / Governance



\[SIGUE]

21\. Multi-model routing





==================================================

PRINCIPIOS QUE ESTAMOS SIGUIENDO

==================================================



1\. No saltar directamente a frameworks complejos.



2\. Entender primero cada pieza.



3\. Construir baselines simples.



4\. Medir antes de asumir que algo es mejor.



5\. Mantener responsabilidades separadas.



6\. No meter todo el repo en el prompt.



7\. Recuperar únicamente contexto relevante.



8\. Mantener el Harness independiente del modelo.



9\. Usar instrucciones humanas y contexto automático como cosas complementarias.



10\. Evolucionar:



rules

→ lexical

→ BM25

→ embeddings

→ hybrid

→ reranking

→ RAG

→ code graph

→ agentic workflows

→ evals





==================================================

ESTADO EXACTO DONDE RETOMAR

==================================================



Estamos entrando en:



SEMANTIC RETRIEVAL CON EMBEDDINGS LOCALES



Ya tenemos:



\- scanner

\- context engine

\- scoring

\- budget

\- chunking

\- lexical retrieval

\- BM25



Ahora debemos:



1\. Instalar sentence-transformers.



2\. Crear:



src/context\_engine/semantic.py



3\. Usar:



paraphrase-multilingual-MiniLM-L12-v2



4\. Calcular similitud entre:



task

vs

README chunks



5\. Comparar el ranking obtenido con BM25.



6\. Después combinar ambos usando Hybrid Search.





ESTRUCTURA ACTUAL APROXIMADA

\----------------------------



agentic-dev-harness/

│

├── src/

│   │

│   ├── repository/

│   │   ├── models.py

│   │   ├── scanner.py

│   │   └── detectors/

│   │       └── dotnet.py

│   │

│   ├── context\_engine/

│   │   ├── \_\_init\_\_.py

│   │   ├── models.py

│   │   ├── engine.py

│   │   ├── scoring.py

│   │   ├── budget.py

│   │   ├── chunking.py

│   │   ├── retrieval.py

│   │   └── semantic.py

│   │

│   └── main.py

│

├── tests/

├── docs/

├── evals/

├── context/

├── tools/

├── scripts/

├── AGENTS.md

├── CLAUDE.md

├── README.md

└── pyproject.toml





META FINAL

\----------



Repository

&#x20;   ↓

Discovery

&#x20;   ↓

Structured Metadata

&#x20;   ↓

Documents / Code Chunks

&#x20;   ↓

BM25 + Embeddings

&#x20;   ↓

Hybrid Retrieval

&#x20;   ↓

Reranking

&#x20;   ↓

Code Graph Expansion

&#x20;   ↓

Context Budget

&#x20;   ↓

ContextBundle

&#x20;   ↓

MCP

&#x20;   ↓

Codex / Claude / OpenCode

&#x20;   ↓

Agentic Development Workflows

&#x20;   ↓

Evals + Governance





