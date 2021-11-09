from typing import Any, Callable, List

import attr

from repoma.pre_commit_hooks.errors import PrecommitError


@attr.s(on_setattr=attr.setters.frozen)
class Executor:
    """Execute functions and collect any `.PrecommitError` exceptions."""

    error_messages: List[str] = attr.ib(factory=list, init=False)

    def __call__(self, function: Callable, *args: Any, **kwargs: Any) -> None:
        try:
            function(*args, **kwargs)
        except PrecommitError as exception:
            error_message = str("\n".join(exception.args))
            self.error_messages.append(error_message)