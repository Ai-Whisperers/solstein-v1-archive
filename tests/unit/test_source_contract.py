from solstein.domain.source_contract import canonical_source_uri, is_valid_source_uri, normalize_source_key


def test_normalize_source_key_uses_namespace_and_slugs() -> None:
    key = normalize_source_key("SEC_EDGAR", "SEC Edgar API", "corp")
    assert key == "corp:sec-edgar:sec-edgar-api"


def test_canonical_source_uri_prefers_http_url() -> None:
    uri = canonical_source_uri(None, "https://example.com/doc", "solstein:web:example")
    assert uri == "https://example.com/doc"


def test_canonical_source_uri_falls_back_to_urn() -> None:
    uri = canonical_source_uri(None, None, "solstein:web:example")
    assert uri == "urn:source:solstein:web:example"


def test_is_valid_source_uri_accepts_http_and_urn() -> None:
    assert is_valid_source_uri("https://example.com/x")
    assert is_valid_source_uri("urn:source:solstein:web:example")
    assert not is_valid_source_uri("example.com/x")
