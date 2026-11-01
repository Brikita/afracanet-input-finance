# Consolidation checkpoint — 1 November 2026

AFRACANet AI now has one canonical source repository. Credit intelligence is
tracked directly under `modules/credit-intelligence/`; execution and the public
site remain in root `backend/` and `src/`. The imported folder is ordinary Git
content, not a submodule or a dependency on a second code checkout. Source
history was merged additively, preserving authors/messages/relationships in a
sanitized import. Original source history was not rewritten or force-pushed.

## Recorded verification

| Check                             | Result                                                                                                                                                                                                                                 |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Root `npm run setup`              | Both npm clean installs and shared pinned Python installation passed. An incomplete inherited credit lock was repaired with its missing lru-cache peer entry.                                                                          |
| TypeScript                        | Both projects passed through `npm run check:all`.                                                                                                                                                                                      |
| Frontend builds                   | Both passed through `npm run build:all`, using their existing Vite/TanStack configurations. Existing upstream bundler notices remain.                                                                                                  |
| Input/backend and workspace tests | 150 passed. New cases cover service-environment isolation, local path references and nested credit configuration/data ownership.                                                                                                       |
| Credit backend                    | 16 passed against the shared Python runtime.                                                                                                                                                                                           |
| Signed integration                | Passed actual signing/verification, lost acknowledgment retry, deduplication, revocation, unpaid collection blocking and preservation of paid collection. Payment is explicitly simulated.                                             |
| Input/public browser suite        | Final complete run: 11 passed. The keyboard journey now waits for modal focus before pressing Escape.                                                                                                                                  |
| Connected browser suite           | Final run: 1 passed, including graph/source inspection, signed delivery, scoped receiving sign-in, revocation and responsive views. Its status assertions now use the actual middle-dot character.                                     |
| Whole-platform startup            | Both APIs and both UIs returned HTTP200 through one supervisor; all four ports were free after its smoke-check cleanup.                                                                                                                |
| Clean tracked source archive      | Contains both modules and no `.env`, node_modules or virtual environment. The signed workflow passed from the extracted source using the already installed shared Python runtime only. This is not a clean-machine installation claim. |
| Secret scanning                   | Sanitized credit import and complete committed consolidated history: zero Gitleaks findings. Three historical findings were removed from the private import before merging.                                                            |

The root CI workflow installs both frontend locks and the shared runtime, checks
both APIs and TypeScript projects, builds both UIs, checks whole-platform startup
and runs isolated input/public browser journeys. This records local validation;
GitHub-hosted CI is a separate run and is not claimed to have passed here.

## Preserved boundaries

No credentials, databases, local sessions or installed environments were copied
into Git. Existing private files can remain external through ignored local path
references. Provider settings, private signing keys, officer sessions and lending
authority remain service-scoped. The receiving API still independently checks
signed authority, lender/officer policy, farmer mappings, integer amounts and
available stock/credit. Consolidation introduces no new provider transactions.

The old credit repository retains historical provenance; active development
belongs here. Its previous Lovable connection is not silently retargeted.
Imported credit licensing remains recorded in its NOTICE. Older dated documents
may still describe the former two-checkout setup; the root README and MONOREPO.md
are the current operational authority.

Stable public hosting, broader provider/AI/SMS evaluation, authentic partner data,
validated credit modelling, video and Devpost submission remain separate work.
