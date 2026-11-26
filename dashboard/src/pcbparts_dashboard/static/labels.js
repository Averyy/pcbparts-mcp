// Plain words for the server's fixed labels (pcbparts-mcp stats.py: REASONS, BAD_REQUEST_REASONS,
// ARG_ERROR_TYPES, distributor hold-back causes, upstream status classes). A label the server adds
// later falls back to its own text with underscores as spaces, so nothing ever shows blank.

const table = (o) => Object.assign(Object.create(null), o);
const fallback = (code) => String(code).replace(/_/g, " ");

// Why a call worked but found nothing (not_found outcome).
const NOT_FOUND = table({
  offset_past_end: "Asked for a page past the last result",
  blocked_by_library_type: "Matches exist, but not in the library type asked for",
  blocked_by_package: "Matches exist, but not in the package asked for",
  blocked_by_min_stock: "Matches exist, but under the stock minimum asked for",
  blocked_by_several: "Matches exist, but several filters together ruled them out",
  part_number_not_in_stock: "Part number not in the in-stock catalog",
  part_number_sold_out: "Part number JLCPCB listed before, now sold out",
  part_number_unknown: "Part number JLCPCB has never listed",
  part_number_filtered_out: "Part number found, but the filters excluded it",
  words_unmatched: "The search words matched nothing",
  no_part_type: "Couldn't tell what kind of part was wanted",
  no_catalog_subcategory: "No catalog category for that kind of part",
  value_not_listed: "No part with that value",
  filter_ignored_or_sparse: "A filter had too little data to use",
  spec_filters_no_match: "No part met the spec filters",
  stock_below_minimum: "Parts found, but under the stock minimum",
  part_number_fragment: "Part number too short or partial",
  no_results: "No results",
  no_results_filtered: "No results with the filters given",
  no_results_part_number: "No results for that part number",
  no_results_words: "No results for those words",
  mpn_not_in_snapshot: "Part number not in the JLCPCB catalog",
  placeholder_mpn: "A placeholder part number (like TBD)",
  lcsc_code_as_mpn: "An LCSC code given as a part number",
  part_not_found: "The distributor has no listing for that part number",
  lcsc_not_found: "That LCSC code doesn't exist",
  board_not_found: "No such reference board",
  no_parts_for_query: "SamacSys found no part for the query",
  no_ecad_model: "SamacSys has no KiCad model for the part",
  no_kicad_in_archive: "The downloaded model had no KiCad files",
  no_easyeda_symbol: "EasyEDA has no symbol for the part",
  no_alternatives: "No alternatives found",
  not_sent: "Not a real part number (like 10k or TBD), so not looked up",
});

// Why a call failed (failed outcome): something broke here or in a service we call.
const FAILED = table({
  service_not_ready: "The server was still starting",
  not_configured: "Not set up on the server",
  no_pcba_types: "JLCPCB's assembly types were unavailable",
  query_too_complex: "The query was too complex to run",
  board_db_failed: "Board database error",
  jlcpcb_waf: "JLCPCB's firewall blocked the request",
  jlcpcb_unavailable: "JLCPCB didn't answer",
  easyeda_failed: "EasyEDA request failed",
  mouser_failed: "Mouser request failed",
  digikey_failed: "DigiKey request failed",
  cse_auth_failed: "SamacSys sign-in failed",
  cse_lookup_failed: "SamacSys search failed",
  cse_download_http_4xx: "SamacSys download rejected",
  cse_download_http_5xx: "SamacSys download hit a server error",
  cse_download_http: "SamacSys download failed",
  cse_download_network: "SamacSys download lost its connection",
  cse_download_too_large: "SamacSys download too large",
  cse_invalid_zip: "SamacSys sent a broken file",
  cse_download_refused: "SamacSys refused the download (its quota)",
  lifecycle_lookup_failed: "Lifecycle lookup failed",
  exception: "Server error (a bug in our code)",
  unexpected_error: "Server error (a bug in our code)",
});

export const isFailureReason = (code) => Object.hasOwn(FAILED, code);
export const reasonLabel = (code) => FAILED[code] || NOT_FOUND[code] || (code === "other" ? "Other" : fallback(code));

const BAD_REQUEST = table({
  category_not_found: "Unknown category name",
  too_long: "Query too long",
  too_many: "Too many items in one call",
  invalid_value: "A value the tool can't use",
  unsupported_exclusion: "An exclusion the tool doesn't support",
  strict_unmet: "A strict match couldn't be met",
  unsupported_value: "A value the tool doesn't support",
  unsupported_sort: "A sort order the tool doesn't support",
  missing_argument: "A required argument was missing",
  invalid_lcsc: "Not a valid LCSC code",
  query_unsearchable: "Nothing searchable in the query",
  invalid_id: "Not a valid ID",
  all_inputs_invalid: "Every item in the batch was invalid",
  unknown_tool: "Called a tool that doesn't exist",
  other: "Other",
});

const ARG_PROBLEM = table({
  missing: (p) => `Left out ${p}`,
  missing_argument: (p) => `Left out ${p}`,
  missing_keyword_only_argument: (p) => `Left out ${p}`,
  missing_positional_only_argument: (p) => `Left out ${p}`,
  extra_forbidden: (p) => `Sent ${p}, which the tool doesn't take`,
  unexpected_keyword_argument: (p) => `Sent ${p}, which the tool doesn't take`,
  unexpected_positional_argument: (p) => `Sent an extra unnamed argument`,
  multiple_argument_values: (p) => `Gave ${p} twice`,
  int_parsing: (p) => `${cap(p)} wasn't a whole number`,
  int_type: (p) => `${cap(p)} wasn't a whole number`,
  float_parsing: (p) => `${cap(p)} wasn't a number`,
  string_type: (p) => `${cap(p)} wasn't text`,
  bool_parsing: (p) => `${cap(p)} wasn't true or false`,
  list_type: (p) => `${cap(p)} wasn't a list`,
  literal_error: (p) => `${cap(p)} wasn't one of the allowed values`,
  enum: (p) => `${cap(p)} wasn't one of the allowed values`,
  greater_than_equal: (p) => `${cap(p)} was too small`,
  greater_than: (p) => `${cap(p)} was too small`,
  less_than_equal: (p) => `${cap(p)} was too large`,
  less_than: (p) => `${cap(p)} was too large`,
  string_too_long: (p) => `${cap(p)} was too long`,
  too_long: (p) => `${cap(p)} was too long`,
  string_too_short: (p) => `${cap(p)} was too short`,
  too_short: (p) => `${cap(p)} was too short`,
  value_error: (p) => `${cap(p)} had a value the tool can't use`,
  json_invalid: (p) => `${cap(p)} wasn't valid JSON`,
});
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

/** "arg:<parameter or unknown_argument>:<type>" or a fixed label, as words. */
export function badRequestLabel(code) {
  const m = /^arg:([^:]+):(.+)$/.exec(String(code));
  if (!m) return BAD_REQUEST[code] || fallback(code);
  const [, param, kind] = m;
  if (param === "unknown_argument") return "Used an argument name the tool doesn't have";
  const p = `"${param}"`;
  return (ARG_PROBLEM[kind] || ((x) => `Bad value for ${x}`))(p);
}

/** Why a lookup was held back; address allowances and distributor budgets have separate resets. */
export function heldBackLabel(cause, who, reset, budgetReset = reset) {
  const resets = reset ? ` (resets ${reset})` : "";
  return ({
    minute_cap: `our limit on ${who} requests a minute`,
    daily_count: `our ${who} budget for the day ran out${budgetReset ? ` (resets ${budgetReset})` : ""}`,
    address_daily: `the calling address had used its daily allowance${resets}`,
    address_blocked: "the calling address is on the server's block list",
    distributor_daily: `${who}'s own daily limit was reached`,
    distributor_minute: `${who}'s own per-minute limit was reached`,
    distributor_refused: `${who} refused requests, so we paused`,
    other: "other limits",
  })[cause] || fallback(cause);
}

/** Requests the distributor itself refused. */
export function refusedLabel(cause) {
  return ({ daily: "daily limit", minute: "per-minute limit", refused: "refused" })[cause] || fallback(cause);
}

/** The per-address limiter's groups. */
export const refusalGroupLabel = (g) => ({
  everyone_else: "an address sent more requests in a minute than its limit",
  platform_ranges: "an AI platform address sent more requests in a minute than its limit",
  too_many_clients: "the server was tracking as many addresses as it can",
  server_busy: "the server was busy (0.10.0 only)",
})[g] || fallback(g);

export const UPSTREAM_LABEL = table({
  jlcpcb: "JLCPCB parts search", lcsc: "LCSC product data", easyeda_products: "EasyEDA footprint checks",
  easyeda_components: "EasyEDA symbols and footprints", easyeda_pads: "EasyEDA footprint pads",
  cse: "SamacSys (CSE)", mouser: "Mouser", digikey: "DigiKey",
});
export const upstreamLabel = (src) => UPSTREAM_LABEL[src] || fallback(src);

/** How a service answered our requests, grouped for a reader. The last three are the error answers. */
export const STATUS_GROUPS = [
  { label: "Answered", keys: ["2xx", "3xx"], color: "--good" },
  { label: "Cancelled by us", keys: ["cancelled"], color: "--silk-dim" },
  { label: "Too many requests", keys: ["429"], color: "--warning" },
  { label: "Rejected our request", keys: ["4xx", "too_large"], color: "--serious" },
  { label: "Server error or no answer", keys: ["5xx", "timeout", "connection", "challenge", "other_error"], color: "--critical" },
];

export const TOOL_SHORT = table({ mouser_get_part: "Mouser", digikey_get_part: "DigiKey", part_lifecycle: "Lifecycle" });
export const DISTRIBUTOR_LABEL = table({ mouser: "Mouser", digikey: "DigiKey" });
