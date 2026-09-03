# Safari 26 Pre-AVX Fix (vendored)

**Upstream:** [kilinccagatay/Safari26-PreAVX-Fix](https://github.com/kilinccagatay/Safari26-PreAVX-Fix)  
**Release:** [v1.1.8](https://github.com/kilinccagatay/Safari26-PreAVX-Fix/releases/tag/v1.1.8)  
**License:** BSD 3-Clause — see `LICENSE.txt` (Acidanthera RestrictEvents fork)

This directory contains RestrictEvents 1.1.8 with the Safari 26.6.1 JavaScriptCore `ctiMasmProbeTrampoline` SSE rewrite. 26x86 injects it only when building OpenCore EFI for a **MacPro5,1** whose CPU does not report AVX.

| File | SHA-256 |
|------|---------|
| `RestrictEvents` executable (upstream installer) | `5862fd1c5415fa94b6d0165e70200eae80ef9e3b1dd4d89220c669507d79f7ef` |
| Release zip `Safari26-PreAVX-Fix-1.1.8.zip` | `2429b456e64f99b000dbae3e41bb446c215e9b4ea3b1a693ed55dbc84814e610` |

The kext is community-signed experimental code. Test on a USB EFI before replacing an internal volume.
