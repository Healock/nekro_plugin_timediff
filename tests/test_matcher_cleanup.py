from __future__ import annotations

import pytest

from nekro_plugin_timediff.matcher_cleanup import destroy_matcher


@pytest.mark.parametrize("error", [KeyError, ValueError])
def test_destroy_ignores_matcher_already_removed(error: type[Exception]) -> None:
    class RemovedMatcher:
        def destroy(self) -> None:
            raise error("not registered")

    destroy_matcher(RemovedMatcher())


def test_repeated_cleanup_is_safe_for_removed_matcher() -> None:
    class OnceMatcher:
        removed = False

        def destroy(self) -> None:
            if self.removed:
                raise ValueError("already removed")
            self.removed = True

    matcher = OnceMatcher()
    destroy_matcher(matcher)
    destroy_matcher(matcher)

    assert matcher.removed
