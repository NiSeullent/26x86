"""
Hardware E2E profile primitives for 26x86 (Track K).

Profiles fix apply order (EFI → root → optional extreme hooks) without
re-implementing domain logic owned by other tracks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class Phase(str, Enum):
    EFI = "efi"
    ROOT = "root"
    EXTREME = "extreme"


@dataclass(frozen=True)
class ProfileStep:
    id: str
    phase: Phase
    title: str
    description: str
    required: bool = True
    extreme_only: bool = False
    owns: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["phase"] = self.phase.value
        return payload


@dataclass
class StepResult:
    step_id: str
    status: str
    detail: str = ""
    mutations: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "status": self.status,
            "detail": self.detail,
            "mutations": self.mutations,
        }


@dataclass(frozen=True)
class HardwareProfile:
    id: str
    title: str
    model: str
    gpu_family: str
    gpu_device_ids: tuple[int, ...]
    target_xnu_major: int
    requires_pre_avx: bool
    steps: tuple[ProfileStep, ...]
    docs: str = ""
    notes: tuple[str, ...] = ()

    def ordered_steps(self, *, include_extreme: bool = False) -> list[ProfileStep]:
        return [
            step
            for step in self.steps
            if not step.extreme_only or include_extreme
        ]

    def plan(self, *, include_extreme: bool = False) -> list[dict[str, Any]]:
        return [step.as_dict() for step in self.ordered_steps(include_extreme=include_extreme)]

    def as_dict(self, *, include_extreme: bool = False) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "model": self.model,
            "gpu_family": self.gpu_family,
            "gpu_device_ids": [hex(d) for d in self.gpu_device_ids],
            "target_xnu_major": self.target_xnu_major,
            "requires_pre_avx": self.requires_pre_avx,
            "docs": self.docs,
            "notes": list(self.notes),
            "steps": self.plan(include_extreme=include_extreme),
        }


def extreme_enabled(environ: Optional[dict[str, str]] = None, flag: bool = False) -> bool:
    if flag:
        return True
    import os

    env = environ if environ is not None else dict(os.environ)
    value = str(env.get("X86_EXTREME", "")).strip().lower()
    return value in {"1", "true", "yes", "on"}
