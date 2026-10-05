def validate_conflicts(
    conflicts,
    sources
):

    valid_ids = {
        source.get("citation_id")
        for source in sources
    }

    cleaned = []

    for conflict in conflicts:

        source_a = conflict.get(
            "source_a"
        )

        source_b = conflict.get(
            "source_b"
        )

        if (
            source_a in valid_ids
            and source_b in valid_ids
            and source_a != source_b
        ):

            cleaned.append(
                conflict
            )

    return cleaned