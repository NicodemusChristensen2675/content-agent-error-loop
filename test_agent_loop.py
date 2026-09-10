from agent_loop import build_release_plan


def test_release_plan_blocks_incomplete_creator_input():
    assert build_release_plan("  ", "rev-7") == {
        "status": "blocked",
        "reason": "asset and revision are required",
    }


def test_release_plan_marks_complete_input_ready():
    assert build_release_plan("clip-042", "rev-7")["status"] == "ready"
