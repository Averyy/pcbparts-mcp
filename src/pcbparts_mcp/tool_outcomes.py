"""Pure classification of tool replies for usage counts and failed-search records."""

import re
from typing import Any


# Error replies meaning it worked and found nothing, with the reason shown in the usage counts
_NOT_FOUND_ERRORS = (
    ("mpn_not_in_snapshot", r"No part found in the local snapshot for MPN "),
    ("part_not_found", r"Part not found: "),
    ("lcsc_not_found", r"Part .* not found$"),
    ("board_not_found", r"Board '.*' not found$"),
    ("no_parts_for_query", r"No (JLCPCB parts|parts) found for "),
    ("no_ecad_model", r"No ECAD model available for "),
    ("no_kicad_in_archive", r"No KiCad files found in model archive "),
    ("no_easyeda_symbol", r"No EasyEDA symbol (available|UUID) for "),
    ("no_easyeda_symbol", r"EasyEDA has no symbol "),
)

# Our error replies, sorted for the usage counts by the start of their text (stats.OUTCOMES). Anchored
# at the start because many messages end with what the user typed. A message that matches none of
# these counts as "failed", so an unexpected failure shows up. tests/test_usage_stats.py checks every
# error message in the code against this list.
# re.S: messages echo caller input, which can hold a newline ("Board 'a\nb' not found")
_BAD_REQUEST_ERRORS = [(label, re.compile(pattern, re.S)) for label, pattern in (
    ("category_not_found", r"(Subcategory|Category) not found: "),
    ("category_not_found", r"(Subcategory|Category) ID \S+ not found$"),
    ("too_long", r"[\w ]+ too long \(max \d+ characters\)$"),
    ("too_many", r"Too many "),
    ("invalid_value", r"Invalid [\w ]+: "),
    ("unsupported_exclusion", r"Part-number exclusions are not supported: "),
    ("strict_unmet", r"Strict search cannot apply every constraint; "),
    ("unsupported_value", r"Unsupported (library_type|pcba_type|sort_spec|tag|value for \w+): "),
    ("unsupported_sort", r"Can't sort "),
    ("missing_argument", r"Must provide "),
    ("invalid_lcsc", r"lcsc must be "),
    ("invalid_value", r"board_quantity and placements_per_board must be "),
    ("missing_argument", r"Give (a|at least one) "),
    ("too_many", r"Mouser takes up to "),
    ("invalid_value", r"Each Mouser part number must be "),
    ("query_unsearchable", r"Query contains (invalid characters|no searchable terms)$"),
    ("invalid_id", r"(Invalid slug|Invalid UUID format|UUID is required)$"),
)]

_ERROR_KINDS = [(kind, re.compile(pattern, re.S)) for kind, pattern in (
    # a limit turned the request away: ours, Mouser's, DigiKey's, JLCPCB's or EasyEDA's
    ("rate_limited", r"\w+ daily quota exceeded "),
    ("rate_limited", r"This address has used its \d+ Mouser and DigiKey lookups for today on this shared server;"),
    ("rate_limited", r"\w+ lookups are limited to "),
    ("rate_limited", r"\w+ is limiting requests"),
    ("rate_limited", r"\w+ refused this server's requests"),
    ("rate_limited", r"DigiKey lookups are (paused|busy) on this shared server"),
    ("rate_limited", r"JLCPCB rate limited"),
    ("rate_limited", r"SamacSys's daily model download limit for this shared server is used up;"),
    ("rate_limited", r"Couldn't check EasyEDA for .* right now"),
    ("failed", r"Stock history is not available on this server"),
    *(("bad_request", pattern.pattern) for _, pattern in _BAD_REQUEST_ERRORS),
    # it worked and found nothing
    *(("not_found", pattern) for _, pattern in _NOT_FOUND_ERRORS),
)]

_NOT_FOUND_REASONS = [(reason, re.compile(pattern, re.S)) for reason, pattern in _NOT_FOUND_ERRORS]

# Why a call failed, for the usage counts. Anchored, like _ERROR_KINDS; no match is "unexpected_error".
_FAILED_REASONS = [(reason, re.compile(pattern, re.S)) for reason, pattern in (
    ("service_not_ready", r"(Boards database|Sensor database|Database) not available|Design rules are not available"
                          r"|Categories not loaded|CSE client not initialized|Stock history is not available on this server"),
    ("not_configured", r"(CSE credentials|Mouser API key|DigiKey API credentials) not configured"),
    ("no_pcba_types", r"This catalog doesn't have PCBA types yet"),
    ("query_too_complex", r"Search failed: query too complex"),
    ("board_db_failed", r"Board (search|retrieval) failed"),
    ("jlcpcb_waf", r"JLCPCB blocked request"),
    ("jlcpcb_unavailable", r"JLCPCB (returned|connection|request|API)"),
    ("easyeda_failed", r"Failed to fetch (EasyEDA data|component data from EasyEDA)|Invalid EasyEDA response"),
    ("mouser_failed", r"Mouser part lookup failed"),
    ("digikey_failed", r"DigiKey part lookup failed"),
    ("cse_auth_failed", r"CSE authentication failed"),
    ("cse_lookup_failed", r"CSE (search|get_kicad) failed"),
    ("cse_download_http_4xx", r"CSE model download failed \(HTTP 4"),
    ("cse_download_http_5xx", r"CSE model download failed \(HTTP 5"),
    ("cse_download_http", r"CSE model download failed \(HTTP"),
    ("cse_download_network", r"CSE model download failed \(network"),
    ("cse_download_too_large", r"CSE model download too large"),
    ("cse_invalid_zip", r"CSE returned invalid zip file"),
    ("cse_download_refused", r"CSE refused the model download for part "),
)]

# What an empty reply's hint opens with: its most specific cause comes first
_EMPTY_HINT_REASONS = [(reason, re.compile(pattern, re.S)) for reason, pattern in (
    ("part_number_filtered_out", r"\d+ in-stock parts? match "),
    ("part_number_not_in_stock", r"No in-stock part matches "),
    ("words_unmatched", r"No part's description has all of the words "),
    ("no_part_type", r"No part type matched "),
    ("blocked_by_library_type", r"No (basic|preferred|no-fee) part matches"),
    ("no_catalog_subcategory", r"JLCPCB has no "),
    ("stock_below_minimum", r"No part \S+ with stock >= "),
    ("part_number_fragment", r"JLCPCB's search matches whole part numbers"),
)]
_LCSC_CODE_HINT = re.compile(r"'.*' looks like an LCSC code")


def _error_kind(message: str) -> str:
    return next((kind for kind, pattern in _ERROR_KINDS if pattern.match(message)), "failed")


def _call_outcome(result: Any) -> str:
    """For the usage counts, how a tool call that returned went (stats.OUTCOMES)."""
    content = getattr(result, "structured_content", None)
    if not isinstance(content, dict):
        return "ok"
    if content.get("error"):
        return _error_kind(str(content["error"]))
    if "status_counts" in content:
        return _lifecycle_outcome(content)
    if _is_parts_reply(content):
        return _parts_outcome(content)
    if "parts" in content and "what_is_recorded" in content:
        # Single history replies count as ok even with no events or snapshot stock. A batch
        # follows that rule if any valid code was answered; all-invalid codes are bad_request.
        return "ok" if any(not part.get("error") for part in content["parts"]) else "bad_request"
    if "alternatives" in content:
        if content["alternatives"]:
            return "ok"
        return "similar_only" if (content.get("similar_parts") or content.get("unverified_alternatives")) else "not_found"
    if content.get("not_checked") and not content.get("results"):  # Mouser: a limit held the rest back
        return "rate_limited"
    if any(key in content and not content[key] for key in ("results", "matched_files")):
        return "not_found"
    return "ok"


def _lifecycle_errors(content: dict) -> list[str]:
    """part_lifecycle's per-part errors (inputs that couldn't be looked up)."""
    return [str(row["error"]) for row in content.get("results") or [] if isinstance(row, dict) and row.get("error")]


def _lifecycle_outcome(content: dict) -> str:
    """part_lifecycle answers every part, unknown when it can't: ok when any has a reading; else
    what kept the rest unknown (a limit, a failed lookup, or neither distributor lists them). When
    no part could be looked up, the parts' own errors decide (a catalog outage fails, LCSC codes
    not in the catalog are not found, the rest were invalid)."""
    rows = [row for row in content.get("results") or [] if isinstance(row, dict) and not row.get("error")]
    if not rows:
        kinds = {_error_kind(error) for error in _lifecycle_errors(content)}
        return "failed" if "failed" in kinds else "not_found" if "not_found" in kinds else "bad_request"
    if any(row.get("status") != "unknown" or "source" in row or row.get("makers") for row in rows):
        return "ok"
    if any("retry_after" in row for row in rows):
        return "rate_limited"
    if any(row.get("lookup_failed") for row in rows):
        return "failed"
    return "not_found"


def _is_parts_reply(content: dict) -> bool:
    """A jlc_get_parts reply (counts of found, not_found and error rows)."""
    return isinstance(content.get("counts"), dict) and "results" in content


def _parts_outcome(content: dict) -> str:
    """jlc_get_parts: ok when any part was found, in the snapshot or gone from it; not_found when
    parts were looked up and none was; with neither, failed when the database failed on a part
    number (that row's "Database not available"), else bad_request (every input was unusable)."""
    counts = content["counts"]
    if counts.get("found") or counts.get("gone"):  # a gone part's answer is an answer, from our data
        return "ok"
    if counts.get("not_found"):
        return "not_found"
    return "failed" if "failed" in {_error_kind(error) for error in _lifecycle_errors(content)} else "bad_request"


def _parts_empty_reason(content: dict) -> str:
    """Why no jlc_get_parts part was found: its LCSC codes or its MPNs aren't in the snapshot, or both."""
    missed = {"results" in row for row in content.get("results") or [] if isinstance(row, dict) and row.get("not_found")}
    return "lcsc_not_found" if missed == {False} else "mpn_not_in_snapshot" if missed == {True} else "part_not_found"


def _first_reason(table: list[tuple[str, re.Pattern]], text: str) -> str | None:
    return next((reason for reason, pattern in table if pattern.match(text)), None)


def _empty_reason(content: dict) -> str:
    """Why a reply counted as not_found (stats.REASONS): one reason, the most specific it shows."""
    not_sent = content.get("not_sent")  # Mouser: by number; DigiKey: the one number's reason
    if not_sent and not content.get("results") and (
            isinstance(not_sent, str) or set(content.get("not_found") or ()) <= set(not_sent)):
        return "not_sent"  # nothing that was worth a request
    if content.get("not_found") and not content.get("results") and isinstance(content["not_found"], list):
        return "part_not_found"
    if content.get("error"):
        reason = _first_reason(_NOT_FOUND_REASONS, str(content["error"])) or "no_results"
        if reason == "mpn_not_in_snapshot":
            if content.get("next_call") is None:
                return "placeholder_mpn"
            if _LCSC_CODE_HINT.match(str(content.get("hint") or "")):
                return "lcsc_code_as_mpn"
        return reason
    if "alternatives" in content:
        return "no_alternatives"
    if "status_counts" in content:  # part_lifecycle: neither distributor lists the parts
        for error in _lifecycle_errors(content):  # or, with nothing looked up, LCSC codes not in the catalog
            if reason := _first_reason(_NOT_FOUND_REASONS, error):
                return reason
        rows = [row for row in content.get("results") or [] if isinstance(row, dict) and not row.get("error")]
        if rows and all(row.get("not_sent") for row in rows):  # none worth a request
            return "not_sent"
        return "part_not_found"
    if _is_parts_reply(content):
        return _parts_empty_reason(content)
    if content.get("total") and not content.get("results"):
        return "offset_past_end"
    blocking = {item.get("constraint") for item in (content.get("why_empty") or {}).get("blocking") or []}
    if blocking:
        return "blocked_by_several" if len(blocking) > 1 else f"blocked_by_{blocking.pop()}"
    if reason := _first_reason(_EMPTY_HINT_REASONS, str(content.get("hint") or "")):
        return reason
    if content.get("unlisted"):
        return "value_not_listed"
    if content.get("ignored_filters"):
        return "filter_ignored_or_sparse"
    if (content.get("filters_applied") or {}).get("spec_filters"):
        return "spec_filters_no_match"
    return "no_results"


def _why_empty_result(why_empty: dict) -> str:
    """How the checks behind a why_empty reply went (stats.WHY_EMPTY_RESULTS)."""
    if why_empty.get("status"):
        return str(why_empty["status"])
    if not why_empty.get("extra_queries"):
        return "no_counterfactual"
    return "complete" if why_empty.get("diagnostics_complete") else "incomplete"


def _call_reason(outcome: str, content: dict, error: Exception | None) -> str:
    """Why a call counted as not_found or failed (stats.REASONS)."""
    if error is not None:
        return "exception"
    if outcome == "not_found":
        return _empty_reason(content)
    if ("status_counts" in content or _is_parts_reply(content)) and not content.get("error"):
        reasons = (_first_reason(_FAILED_REASONS, error) for error in _lifecycle_errors(content))
        return next(filter(None, reasons), "lifecycle_lookup_failed" if "status_counts" in content else "unexpected_error")
    return _first_reason(_FAILED_REASONS, str(content.get("error") or "")) or "unexpected_error"


