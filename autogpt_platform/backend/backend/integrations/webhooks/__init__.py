from typing import TYPE_CHECKING

from .github import GithubWebhooksManager
from .simple_webhook_manager import CompassWebhookManager, SimpleWebhooksManager
from .slant3d import Slant3DWebhooksManager

if TYPE_CHECKING:
    from .base import BaseWebhooksManager

# --8<-- [start:WEBHOOK_MANAGERS_BY_NAME]
WEBHOOK_MANAGERS_BY_NAME: dict[str, type["BaseWebhooksManager"]] = {
    handler.PROVIDER_NAME: handler
    for handler in [
        CompassWebhookManager,
        GithubWebhooksManager,
        SimpleWebhooksManager,
        Slant3DWebhooksManager,
    ]
}
# --8<-- [end:WEBHOOK_MANAGERS_BY_NAME]

__all__ = ["WEBHOOK_MANAGERS_BY_NAME"]
