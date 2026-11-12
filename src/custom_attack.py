"""Control Tower attack policy with a caller-supplied system prompt.

Load this file as a local Control Tower policy with ``path/to/custom_attack.py@custom_attack``.
The attack mechanics (planning, private tools, and optional side-task probing) come from
Control Tower's built-in ``AttackPolicy``.
"""

from typing import Annotated, Literal

from inspect_ai.model import ChatMessageSystem
from pydantic import Field

from control_tower.eval.game.messages import side_tasks_description
from control_tower.eval.game.red import PrivateToolsArg
from control_tower.eval.game.registry import policies
from control_tower.eval.game.view import RedView
from control_tower.policies.attack import AttackPolicy, ProbeArg

Plan = Literal["none", "once", "each-step"]


@policies.register(
    name="custom_attack",
    attempts_main_task=True,
    attempts_side_task=True,
    attempts_sneaky=True,
)
class CustomAttackPolicy(AttackPolicy):
    """Control Tower's standard attack policy with a configurable prompt.

    ``prompt`` uses the same format placeholders as ControlArena's attack policy:
    ``{side_task_description}`` and ``{setting_description}``. With no prompt
    supplied, Control Tower's built-in prompt is used, including its planning
    prompt when ``plan`` is enabled.
    """

    def __init__(
        self,
        prompt: Annotated[
            str | None,
            Field(
                description="System prompt for the attacker. Supports {side_task_description} "
                "and {setting_description} placeholders."
            ),
        ] = None,
        private_tools: PrivateToolsArg = frozenset(),
        plan: Plan = "none",
        probe: ProbeArg = False,
    ) -> None:
        if prompt is not None and not prompt.strip():
            raise ValueError("Attacker prompt must not be empty")
        self.custom_prompt = prompt
        super().__init__(private_tools=private_tools, plan=plan, probe=probe)

    def setup(self, view: RedView) -> None:
        super().setup(view)
        if self.custom_prompt is not None:
            self.system = ChatMessageSystem(
                content=self.custom_prompt.format(
                    side_task_description=side_tasks_description(view.side_tasks),
                    setting_description=view.environment.description,
                )
            )
