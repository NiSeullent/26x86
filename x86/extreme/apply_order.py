"""
EFI → root → yellow → extreme apply-order planner (dry-run first).

Real root/EFI mutation stays behind profile apply; this module documents and
validates the **fixed sequence** for MacPro5 + Vega Tahoe missions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional, Sequence

PHASE_ORDER: tuple[str, ...] = ("efi", "root", "yellow", "extreme")

PHASE_STEPS: dict[str, tuple[str, ...]] = {
    "efi": (
        "efi.agdpmod_shikigva",
        "efi.kdkless",
        "efi.restrictevents_jsc",
    ),
    "root": ("root.amd_vega",),
    "yellow": ("root.yellow_mitigations",),
    "extreme": ("extreme.hooks",),
}


@dataclass(frozen=True)
class PhasePlan:
    phase: str
    step_ids: tuple[str, ...]
    status: str  # planned | skipped | blocked
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ApplyOrderReport:
    profile_id: str
    dry_run: bool
    include_extreme: bool
    phases: tuple[PhasePlan, ...]
    flat_order: tuple[str, ...]
    reboot_after: tuple[str, ...] = ("efi",)
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "dry_run": self.dry_run,
            "include_extreme": self.include_extreme,
            "phases": [asdict(p) for p in self.phases],
            "flat_order": list(self.flat_order),
            "reboot_after": list(self.reboot_after),
            "notes": list(self.notes),
        }


def plan_apply_order(
    *,
    profile_id: str = "macpro5-vega64-tahoe",
    dry_run: bool = True,
    include_extreme: bool = False,
    environ: Optional[Mapping[str, str]] = None,
    phases: Optional[Sequence[str]] = None,
) -> ApplyOrderReport:
    """
    Build the mission apply sequence without touching the live volume.

    When ``include_extreme`` is False, extreme phase is ``skipped`` unless
    ``X86_EXTREME`` is truthy in ``environ``.
    """
    from x86.profiles.base import extreme_enabled

    env = environ if environ is not None else {}
    extreme_on = include_extreme or extreme_enabled(env)
    wanted = tuple(phases) if phases is not None else PHASE_ORDER
    phase_plans: list[PhasePlan] = []
    flat: list[str] = []
    notes: list[str] = [
        "Always EFI → reboot → root AMD Vega → yellow mitigations → extreme.",
        "dry_run=True plans only; use profile apply for config.plist mutation.",
    ]

    for phase in wanted:
        if phase not in PHASE_STEPS:
            phase_plans.append(
                PhasePlan(phase=phase, step_ids=(), status="blocked", notes=("unknown phase",))
            )
            continue
        steps = PHASE_STEPS[phase]
        if phase == "extreme" and not extreme_on:
            phase_plans.append(
                PhasePlan(
                    phase=phase,
                    step_ids=steps,
                    status="skipped",
                    notes=("Set X86_EXTREME=1 or include_extreme=True",),
                )
            )
            continue
        phase_plans.append(
            PhasePlan(
                phase=phase,
                step_ids=steps,
                status="planned",
                notes=("dry-run" if dry_run else "live"),
            )
        )
        flat.extend(steps)

    return ApplyOrderReport(
        profile_id=profile_id,
        dry_run=dry_run,
        include_extreme=extreme_on,
        phases=tuple(phase_plans),
        flat_order=tuple(flat),
        notes=notes,
    )


def dry_run_profile_apply(
    *,
    include_extreme: bool = True,
    environ: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """Profile dry-run + ordered phase report in one payload."""
    from x86.profiles.macpro5_vega64_tahoe import apply_profile

    env = dict(environ or {})
    if include_extreme:
        env.setdefault("X86_EXTREME", "1")
    plan = plan_apply_order(
        dry_run=True, include_extreme=include_extreme, environ=env
    )
    report = apply_profile(dry_run=True, include_extreme=include_extreme, environ=env)
    return {
        "apply_order": plan.as_dict(),
        "profile_report": {
            "order": report.get("order"),
            "results": [
                {
                    "step_id": r.get("step_id"),
                    "status": r.get("status"),
                }
                for r in (report.get("results") or [])
            ],
        },
        "order_matches_phases": list(report.get("order") or []) == list(plan.flat_order),
    }


def main(argv: Optional[list[str]] = None) -> int:
    import json
    import sys

    args = list(argv if argv is not None else sys.argv[1:])
    extreme = "--extreme" in args or "-e" in args
    payload = dry_run_profile_apply(include_extreme=extreme)
    print(json.dumps(payload, indent=2, default=str))
    return 0 if payload.get("order_matches_phases") else 1


if __name__ == "__main__":
    raise SystemExit(main())
