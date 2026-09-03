# NOTICE — Extreme-Interpose (Track I)

Community-authored DYLD_INTERPOSE PoC only.

**Do not** place Apple frameworks, metallibs, SkyLight/CoreDisplay binaries, or
PatcherSupportPkg proprietary trees here.

`X86_EXTREME=1` required for non-passthrough hooks.
`X86_EXTREME_INSTALL=1` required for install helpers.

AVX `report1` without opcode emulation can SIGILL on pre-AVX CPUs.
