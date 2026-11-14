from test_monitor_journal import journal_claude
from test_monitor_scope import NativeScopeFixture
from test_claude import rate_event

from aitm_usage.monitor_scope import ScopeState
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.types import DiagnosticCode


def test_ordinary_terminal_claude_reserves_but_cannot_advance(journal_claude):
    native = journal_claude
    with native.native.registry.writer() as writer:
        native.approve(writer)
        journal = RoutingJournal(writer, ScopeState(writer))
        native.append(native.request(3))
        locator = native.locator()
        first = journal.prepare(native.source_id, locator)
        assert any(c.observation.revision == 1 for c in first.candidates)
        assert DiagnosticCode.COVERAGE_GAP in {d.code for d in first._read.batch.diagnostics}
        outcomes = journal.reserve_batch(first)
        assert any(x.status == "pending" for x in outcomes)
        assert journal.as_of().claims
        assert journal.cursor_for(native.source_id, locator) is None
        native.append(rate_event(native.anchor))
        prepared = journal.prepare(native.source_id, native.locator())
        assert DiagnosticCode.COVERAGE_GAP in {d.code for d in prepared._read.batch.diagnostics}
        journal.reserve_batch(prepared)
        assert journal.cursor_for(native.source_id, locator) is None


def test_independent_codex_ordinary_stream_existing_frontier(journal_claude):
    native = journal_claude.native
    assert type(native) is NativeScopeFixture
    with native.registry.writer() as writer:
        from test_monitor_scope import SOURCE
        journal = RoutingJournal(writer, ScopeState(writer))
        read = journal.prepare(SOURCE, native.locator())
        assert {d.code for d in read._read.batch.diagnostics} == set()
        journal.reserve_batch(read)
        assert journal.as_of().claims
        assert journal.cursor_for(SOURCE, native.locator()) == read.progress
