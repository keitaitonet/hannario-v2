from typing import Literal

from pydantic import BaseModel, model_validator


class CuratorProposal(BaseModel):
    action: Literal["none", "append", "replace"]
    target: Literal["playbook", "persona", "server_context"] | None
    reason: str
    proposal: str | None

    @model_validator(mode="after")
    def validate_action_fields(self) -> "CuratorProposal":
        if self.action == "none":
            if self.target is not None or self.proposal is not None:
                raise ValueError("none action must not include target or proposal")
            return self

        if self.target is None or self.proposal is None:
            raise ValueError(f"{self.action} action requires target and proposal")

        return self
