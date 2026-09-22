from .models import CodeDocument

DEFAULT_CODE_CHUNK_MAX_CHARS = 2000


def chunk_code_documents(
    documents: list[CodeDocument],
    max_chars: int = DEFAULT_CODE_CHUNK_MAX_CHARS,
) -> list[CodeDocument]:
    chunks = []

    for document in documents:
        content_chunks = split_code_content(
            document.content,
            max_chars,
        )

        for index, content in enumerate(
            content_chunks,
            start=1,
        ):
            chunks.append(
                CodeDocument(
                    source=(f"{document.source}" f"#chunk-{index}"),
                    content=content,
                    language=document.language,
                    project=document.project,
                )
            )

    return chunks


def split_code_content(
    content: str,
    max_chars: int,
) -> list[str]:
    if not content.strip():
        return []

    if len(content) <= max_chars:
        return [content]

    chunks = []
    current_lines = []
    current_size = 0

    for line in content.splitlines():
        line_size = len(line) + 1

        if current_lines and current_size + line_size > max_chars:
            chunks.append("\n".join(current_lines).strip())

            current_lines = []
            current_size = 0

        current_lines.append(line)
        current_size += line_size

    if current_lines:
        chunks.append("\n".join(current_lines).strip())

    return chunks
