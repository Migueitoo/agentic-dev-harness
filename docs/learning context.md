PROYECTO: agentic-dev-harness

OBJETIVO: aprender y construir un Agentic Development Harness con Context Engineering + RAG para código, usable con Codex / Claude Code / OpenCode.



PERFIL / ENFOQUE

\- Ya tengo experiencia con .NET, Vue, Node, SQL, Mongo, RabbitMQ, AWS, Redis, CI/CD.

\- Ya uso herramientas agentic como Codex, Claude Code y OpenCode.

\- Quiero profundizar especialmente en RAG para código y Agentic Software Engineering.

\- No queremos depender de LangChain/LangGraph por ahora.

\- Queremos entender las piezas desde cero y construir baselines medibles.

\- Preferencia: cuando haya que modificar una feature, pasar archivos/código completos, no cambios línea por línea.



==================================================

ARQUITECTURA OBJETIVO

==================================================



Developer

&#x20; ↓

Codex / Claude Code / OpenCode

&#x20; ↓

Agentic Development Harness

&#x20; ↓

Context Engine

&#x20; ↓

Retrieval / RAG

&#x20; ↓

Repository + Docs + AGENTS.md + CodeGraphContext

&#x20; ↓

ContextBundle

&#x20; ↓

Agente



==================================================

PROYECTO LOCAL

==================================================



Harness:

C:\\Users\\migue\\source\\repos\\agentic-dev-harness



Repo de prueba:

C:\\Users\\migue\\source\\repos\\FindThatBook



Python:

py

Python 3.13



Ejecución principal:



py src\\main.py --repo "C:\\Users\\migue\\source\\repos\\FindThatBook"



Con contexto:



py src\\main.py --repo "C:\\Users\\migue\\source\\repos\\FindThatBook" --context --task "Agregar un nuevo endpoint para buscar libros"



==================================================

FASE 1 - REPOSITORY DISCOVERY

==================================================



ESTADO: COMPLETADA



El scanner recibe un repositorio y genera RepositoryInfo.



Detecta:



\- nombre

\- path

\- branch

\- lenguajes

\- frameworks

\- capabilities

\- README.md / AGENTS.md / CLAUDE.md

\- proyectos .NET

\- sdk

\- target framework

\- tipo de proyecto

\- test framework

\- PackageReference + versión

\- ProjectReference



Archivos:



src/repository/

├── models.py

├── scanner.py

└── detectors/

&#x20;   └── dotnet.py



Modelos principales:



PackageReferenceInfo

DotNetProjectInfo

RepositoryInfo



Repo FindThatBook detectado:



Languages:

C#



Framework:

ASP.NET Core



Capabilities:

\- Code Coverage

\- MCP

\- Swagger / OpenAPI

\- Testing

\- xUnit



Proyectos:



FindThatBook.API

&#x20; -> Application

&#x20; -> Infrastructure



FindThatBook.Application

&#x20; -> Domain



FindThatBook.Infrastructure

&#x20; -> Application



FindThatBook.Tests

&#x20; -> Application



Concepto:

Scanner = "¿Qué existe realmente en el repo?"



AGENTS.md NO es reemplazado totalmente.



Scanner:

\- hechos automáticos



AGENTS.md:

\- instrucciones humanas

\- reglas

\- convenciones

\- restricciones



Son complementarios.



==================================================

FASE 2 - CONTEXT ENGINE

==================================================



ESTADO: EN PROGRESO



Archivos:



src/context\_engine/

├── \_\_init\_\_.py

├── models.py

├── engine.py

├── scoring.py

├── budget.py

├── chunking.py

├── retrieval.py

└── semantic.py   <- siguiente / actual



ContextItem:



\- kind

\- source

\- content

\- priority



ContextBundle:



\- repository\_name

\- task

\- items

\- max\_tokens



Responsabilidades:



scanner.py

&#x20; ¿Qué existe?



scoring.py

&#x20; ¿Qué proyecto parece más relevante?



chunking.py

&#x20; ¿Cómo divido documentos grandes?



retrieval.py

&#x20; Retrieval lexical / BM25



semantic.py

&#x20; Retrieval semántico con embeddings



budget.py

&#x20; ¿Qué contexto cabe?



engine.py

&#x20; Orquesta todo y produce ContextBundle



==================================================

TASK-AWARE SCORING

==================================================



ESTADO: COMPLETADO



scoring.py usa reglas simples.



Ejemplo:



Task:

"Agregar un nuevo endpoint para buscar libros"



Resultado:



API             100

Application      80

Infrastructure   80

Domain           80

Tests            70



Es un baseline, no RAG.



==================================================

CONTEXT BUDGET

==================================================



ESTADO: COMPLETADO



budget.py limita el contexto.



Presupuesto actual:



DEFAULT\_CONTEXT\_BUDGET = 2000



Estimación temporal:



tokens ≈ len(text) / 4



Objetivo:

No meter todo el repo al prompt.



==================================================

CHUNKING

==================================================



ESTADO: COMPLETADO



chunking.py divide Markdown por encabezados y por tamaño.



Antes:



README.md

&#x20; -> un bloque gigante



Ahora:



README.md#chunk-1

README.md#chunk-2

README.md#chunk-3

...



Ejemplo FindThatBook:



chunk-1

Introducción



chunk-2

Notas de despliegue



chunk-3

MCP / Gemini / Open Library



chunk-4

Arquitectura



chunk-5

Flujo principal



chunk-6

Requisitos / tests



chunk-7

Mejoras futuras



==================================================

LEXICAL RETRIEVAL

==================================================



ESTADO: COMPLETADO



Primera versión:

comparación de palabras entre task y chunks.



Normalización:

\- lowercase

\- acentos

\- stop words

\- plural básico



Problema descubierto:



coincidencia textual != relevancia semántica



==================================================

BM25

==================================================



ESTADO: COMPLETADO



retrieval.py implementa BM25 manualmente.



Considera:

\- term frequency

\- document frequency

\- rareza

\- longitud



Resultado observado para:



"Agregar un nuevo endpoint para buscar libros"



Ranking aproximado:



README chunk-2 Deployment      -> 100

README chunk-7 Future          -> 90

README chunk-4 Architecture    -> 89

README chunk-5 Main Flow       -> 70



Problema:



chunk-2 contiene literalmente:

endpoint

buscar libro

API



chunk-7 contiene:

Agregar...



Por eso BM25 los premia.



Pero chunk-5 contiene:



POST /api/book-discovery

BookDiscoveryController

BookDiscoveryService



y BM25 no entiende que eso es semánticamente muy relevante.



Aprendizaje:



BM25 es lexical.

No entiende significado.



==================================================

PUNTO ACTUAL

==================================================



SIGUIENTE PASO:

SEMANTIC RETRIEVAL CON EMBEDDINGS LOCALES



Modelo elegido:



sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2



Motivo:

\- local

\- multilingüe

\- no requiere OpenAI API

\- no requiere Anthropic API



Instalación:



py -m pip install sentence-transformers



Archivo a crear / usar:



src/context\_engine/semantic.py



Objetivo:



comparar:



task

vs

README chunks



usando embeddings + cosine similarity.



Ejemplo de relaciones que queremos detectar:



"Agregar endpoint"

≈

"controladores HTTP"



"endpoint"

≈

"POST /api/book-discovery"



"buscar libros"

≈

"BookDiscoveryService"



Primero vamos a probar:



A) BM25 solo



B) Embeddings solo



Luego:



C) Hybrid Search



==================================================

SIGUIENTES FASES

==================================================



10\. Semantic Retrieval

11\. Comparar BM25 vs Embeddings

12\. Hybrid Search

13\. Reranking

14\. Indexar archivos de código

15\. RAG para código

16\. Integrar CodeGraphContext

17\. Exponer retrieval mediante MCP

18\. Workflows agentic

19\. Evals

20\. Seguridad / Governance

21\. Multi-model routing



==================================================

HYBRID SEARCH

==================================================



Pendiente.



Combinar:



BM25

\+

Embeddings



BM25 sirve bien para:

\- nombres exactos

\- clases

\- métodos

\- packages

\- errores

\- identificadores



Embeddings sirven bien para:

\- significado

\- intención

\- conceptos equivalentes

\- lenguaje natural



Arquitectura futura:



Task

&#x20; ↓

┌───────────────┐

BM25        Embeddings

└──────┬────────┘

&#x20;      ↓

Hybrid Search

&#x20;      ↓

Reranking

&#x20;      ↓

Budget

&#x20;      ↓

ContextBundle



==================================================

RAG PARA CÓDIGO

==================================================



Más adelante indexaremos:



\- .cs

\- .py

\- .ts

\- etc.



Cada chunk debería tener metadata:



\- path

\- project

\- language

\- symbol

\- kind

\- dependencies



Ejemplo:



source:

FindThatBook.API/Controllers/BookDiscoveryController.cs



project:

FindThatBook.API



language:

C#



kind:

class



symbol:

BookDiscoveryController



==================================================

CODE GRAPH

==================================================



Luego integraremos CodeGraphContext.



Objetivo:



Retriever encuentra:

BookDiscoveryController



CodeGraph expande:

BookDiscoveryService

interfaces

implementaciones

callers

dependencies



Así combinamos:



text relevance

\+

code structure



==================================================

MCP

==================================================



Luego expondremos el RAG como MCP.



Ejemplo conceptual:



search\_repository\_context(

&#x20; query="Agregar endpoint de autores"

)



Resultado:



\- archivos relevantes

\- chunks

\- proyectos

\- dependencias

\- instrucciones

\- scores



Así:



Codex

Claude Code

OpenCode



pueden usar el mismo Context Engine.



==================================================

EVALS

==================================================



Muy importante.



Compararemos:



Rules

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



Métricas futuras:



\- Recall@K

\- Precision@K

\- MRR

\- Context relevance

\- Context size

\- Latency



Ejemplo:



Task:

"Agregar endpoint"



Expected:



\- FindThatBook.API

\- BookDiscoveryController

\- BookDiscoveryService



El sistema debería recuperarlos en Top K.



==================================================

PRINCIPIOS DEL PROYECTO

==================================================



1\. Entender las piezas antes de meter frameworks.



2\. Mantener responsabilidades separadas.



3\. Crear baselines simples.



4\. Medir antes de asumir mejoras.



5\. No meter todo el repo al prompt.



6\. Recuperar contexto relevante.



7\. AGENTS.md e información automática son complementarios.



8\. El Harness debe ser independiente del modelo.



9\. Evolución:



rules

→ lexical

→ BM25

→ embeddings

→ hybrid

→ reranking

→ code RAG

→ code graph

→ MCP

→ agentic workflows

→ evals



==================================================

PARA RETOMAR EN UNA CONVERSACIÓN NUEVA

==================================================



Decir:



"Continuemos el proyecto agentic-dev-harness desde Semantic Retrieval.



Ya completamos:

Repository Scanner,

Context Engine,

Task-aware scoring,

Context Budget,

Markdown Chunking,

Lexical Retrieval

y BM25.



Estamos por implementar embeddings locales con

paraphrase-multilingual-MiniLM-L12-v2.



Usamos FindThatBook como repo de prueba.



Cuando haya que modificar código, pásame los archivos completos."



==================================================

