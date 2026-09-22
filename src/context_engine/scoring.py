from repository.models import DotNetProjectInfo

WEB_TASK_KEYWORDS = {
    "endpoint",
    "api",
    "controller",
    "http",
    "route",
    "ruta",
    "swagger",
}

TEST_TASK_KEYWORDS = {
    "test",
    "tests",
    "testing",
    "prueba",
    "pruebas",
}


def score_project(
    project: DotNetProjectInfo,
    task: str | None,
) -> int:
    base_score = 80

    if not task:
        return base_score

    task_lower = task.lower()

    if contains_any(task_lower, WEB_TASK_KEYWORDS):
        if project.project_type == "web":
            return 100

        if project.project_type == "test":
            return 70

    if contains_any(task_lower, TEST_TASK_KEYWORDS):
        if project.project_type == "test":
            return 100

        if project.project_type == "web":
            return 75

    return base_score


def contains_any(
    text: str,
    keywords: set[str],
) -> bool:
    return any(keyword in text for keyword in keywords)
