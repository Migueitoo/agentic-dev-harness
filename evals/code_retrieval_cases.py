from dataclasses import dataclass


@dataclass
class CodeRetrievalCase:
    name: str
    task: str
    expected_sources: tuple[str, ...]


CODE_RETRIEVAL_CASES = [
    CodeRetrievalCase(
        name="controller",
        task="Modificar BookDiscoveryController",
        expected_sources=(
            "FindThatBook.API/Controllers/" "BookDiscoveryController.cs",
        ),
    ),
    CodeRetrievalCase(
        name="service",
        task=("Agregar validación al servicio " "de búsqueda de libros"),
        expected_sources=(
            "FindThatBook.Application/"
            "BookDiscovery/Services/"
            "BookDiscoveryService.cs",
        ),
    ),
    CodeRetrievalCase(
        name="tests",
        task=("Actualizar las pruebas de " "BookDiscoveryService"),
        expected_sources=("FindThatBook.Tests/" "BookDiscoveryServiceTests.cs",),
    ),
]
