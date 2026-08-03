from benchmark.run_team_benchmark import TEAM_SPECS


def test_team_benchmark_covers_all_five_members_with_distinct_strategies():
    assert len(TEAM_SPECS) == 5
    assert len({spec["student_id"] for spec in TEAM_SPECS}) == 5
    assert len({spec["strategy"] for spec in TEAM_SPECS}) == 5
