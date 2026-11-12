"""Shared pre-publication/CI checks for component snapshots. No networking."""


def validate_manifest(previous: dict, current: dict, *, allow_count_drop: bool = False) -> list[str]:
    failures = []
    if current.get('failed_subcategories'):
        failures.append('failed subcategories remain')
    total = current.get('total_parts')
    if not isinstance(total, int) or total <= 0:
        return [*failures, 'invalid or empty total_parts']
    categories = current.get('categories') or {}
    if sum(c.get('count', 0) for c in categories.values()) != total:
        failures.append('category counts do not add up to total_parts')
    # Rows carried over from the previous scrape for a gap don't count as scraped: a broad failure
    # must still block publication rather than be papered over with yesterday's rows.
    carried: dict[str, int] = {}
    for gap in (current.get('carried_forward') or {}).values():
        carried[gap['category']] = carried.get(gap['category'], 0) + gap['parts']
    if not allow_count_drop:
        if total - sum(carried.values()) < previous.get('total_parts', 0) * 0.95:
            failures.append('total part count dropped more than 5%')
        for slug, category in (previous.get('categories') or {}).items():
            count = category.get('count', 0)
            scraped = categories.get(slug, {}).get('count', 0) - carried.get(slug, 0)
            if count >= 1000 and scraped < count * 0.70:
                failures.append(f'{slug}: part count dropped more than 30%')
    return failures
