from sentinel_tools.scoring.health import relevant_journal_errors


def test_relevant_journal_errors_groups_stack_trace() -> None:
    journal = """
Jul 24 16:39:24 host systemd-coredump[1738]: Process 1734 (hypridle) dumped core.
                                                      Stack trace of thread 1734:
                                                      #0  address libc.so.6
                                                      #1  address raise
                                                      ELF object binary architecture: AMD x86-64
"""

    errors = relevant_journal_errors(journal)

    assert len(errors) == 1
    assert "hypridle" in errors[0]


def test_relevant_journal_errors_deduplicates_repeated_events() -> None:
    journal = """
Jul 24 16:39:26 host systemd[1537]: Failed to start Swaync notification daemon.
Jul 24 16:39:27 host systemd[1537]: Failed to start Swaync notification daemon.
Jul 24 16:39:28 host systemd[1537]: Failed to start Swaync notification daemon.
"""

    errors = relevant_journal_errors(journal)

    assert len(errors) == 1
