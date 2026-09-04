from github_compliance_engine_api.objective_mapping import anchor_public_interfaces


# Scaffold acceptance coverage: TC-ING-001, TC-OBJ-001, TC-CORE-001, V-ING-001, V-OBJ-001, V-CORE-001
# @golden-thread FEAT-SCAFFOLD-001, FR-OBJ-001, TC-OBJ-001, V-OBJ-001
def test_anchor_objectives_to_public_interfaces_only() -> None:
    anchors = anchor_public_interfaces(
        [
            {"name": "POST /api/analyze", "public": True},
            {"name": "internal.clone_repo", "public": False},
        ]
    )

    assert anchors == [
        {
            "interface": "POST /api/analyze",
            "objective": "Expose repository analysis capability to end users",
        }
    ]
