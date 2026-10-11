import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts/select_model.py"
SPEC = importlib.util.spec_from_file_location("select_model", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def model(identifier, *, capabilities, metric="API input-token cost",
          unit="USD per million input tokens", workload="same task",
          window="last 7 days", rank=1, available=True, authorized=True,
          capabilities_complete=True, source="synthetic", as_of="2026-10-11"):
    return {"id": identifier, "capabilities": capabilities,
            "capabilities_complete": capabilities_complete,
            "cost": {"metric": metric, "unit": unit, "workload": workload,
                     "window": window, "relative_rank": rank,
                     "source": source, "as_of": as_of},
            "available": available, "authorized": authorized}


def test_selects_lowest_comparable_capable_and_excludes_unavailable():
    result = module.select({"required_capabilities": ["code", "debug"], "models": [
        model("too-weak", capabilities=["code"], rank=0),
        model("standard", capabilities=["code", "debug"], rank=2),
        model("unavailable", capabilities=["code", "debug"], rank=0, available=False),
        model("costlier", capabilities=["code", "debug"], rank=5),
    ]})
    assert result["status"] == "selected"
    assert result["selected"] == "standard"


def test_refuses_to_compare_api_input_and_output_cost():
    result = module.select({"required_capabilities": ["code"], "models": [
        model("input", capabilities=["code"], metric="API input-token cost", rank=1),
        model("output", capabilities=["code"], metric="API output-token cost", rank=0),
    ]})
    assert result["status"] == "needs_information"
    assert result["selected"] is None


def test_missing_cost_for_capable_candidate_stays_unknown():
    unknown = model("unknown", capabilities=["code"])
    unknown.pop("cost")
    result = module.select({"required_capabilities": ["code"], "models": [
        model("priced", capabilities=["code"], rank=2), unknown,
    ]})
    assert result["status"] == "needs_information"
    assert result["missing_cost"] == ["unknown"]


def test_unknown_availability_authorization_or_capabilities_remains_unresolved():
    result = module.select({"required_capabilities": ["code"], "models": [
        model("availability-unknown", capabilities=["code"], available=None),
        model("authorization-unknown", capabilities=["code"], authorized=None),
        model("capabilities-incomplete", capabilities=["code"], capabilities_complete=False),
    ]})
    assert result["status"] == "needs_information"
    assert result["selected"] is None
    assert {item["id"] for item in result["unresolved"]} == {
        "availability-unknown", "authorization-unknown", "capabilities-incomplete"}


def test_known_exclusion_is_reported_alongside_other_unknown_states():
    result = module.select({"required_capabilities": ["code"], "models": [
        model("unknown-and-forbidden", capabilities=["code"], authorized=False, available=None),
        model("unavailable-but-authorization-unknown", capabilities=["code"],
              available=False, authorized=None),
    ]})
    excluded = {item["id"]: item["reasons"] for item in result["excluded"]}
    unresolved = {item["id"]: item["questions"] for item in result["unresolved"]}
    assert "unauthorized" in excluded["unknown-and-forbidden"]
    assert "availability unknown" in unresolved["unknown-and-forbidden"]
    assert "unavailable" in excluded["unavailable-but-authorization-unknown"]
    assert "authorization unknown" in unresolved["unavailable-but-authorization-unknown"]


def test_duplicate_ids_are_rejected():
    repeated = model("same", capabilities=["code"])
    try:
        module.select({"required_capabilities": ["code"], "models": [repeated, dict(repeated)]})
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate model ids must fail closed")


@pytest.mark.parametrize("catalogue", [None, [], "not-an-object"])
def test_invalid_catalogue_root_returns_named_error(catalogue):
    with pytest.raises(ValueError, match="catalogue root must be a JSON object"):
        module.select(catalogue)


def test_no_capability_candidate_only_claims_catalogue_scope_and_reports_exclusions():
    result = module.select({"required_capabilities": ["debug"], "models": [
        model("weak", capabilities=["code"]),
        model("off", capabilities=["debug"], available=False),
    ]})
    assert result["status"] == "no_candidate_in_catalogue"
    assert "outside it" in result["reason"]
    assert {tuple(x["reasons"]) for x in result["excluded"]} == {
        ("required capability absent from complete list",), ("unavailable",)}
