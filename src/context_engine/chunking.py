def chunk_markdown(
    content: str,
    max_chars: int = 2000,
) -> list[str]:
    if not content.strip():
        return []

    sections = split_markdown_sections(content)

    chunks = []

    for section in sections:
        if len(section) <= max_chars:
            chunks.append(section)
            continue

        chunks.extend(
            split_large_text(
                section,
                max_chars,
            )
        )

    return chunks


def split_markdown_sections(
    content: str,
) -> list[str]:
    sections = []
    current_lines = []

    for line in content.splitlines():
        if line.startswith("#") and current_lines:
            section = "\n".join(current_lines).strip()

            if section:
                sections.append(section)

            current_lines = []

        current_lines.append(line)

    if current_lines:
        section = "\n".join(current_lines).strip()

        if section:
            sections.append(section)

    return sections


def split_large_text(
    text: str,
    max_chars: int,
) -> list[str]:
    chunks = []

    current_lines = []
    current_size = 0

    for line in text.splitlines():
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
