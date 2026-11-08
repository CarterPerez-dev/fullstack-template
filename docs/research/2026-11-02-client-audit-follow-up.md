<!-- ©AngelaMos | 2026 -->
<!-- 2026-11-02-client-audit-follow-up.md -->

# Client dependency audit follow-up, 2026-11-02

The first complete fresh-install run passed the five web builds and the native
SDK 54 checks, but all six clients failed their production dependency audit.
This follow-up records repairs and verification through native SDK 58 exports.
The native production audit now passes; binary/device behavior remains unverified.

## Zod

All five web audits identified Zod 4.1.13. The reviewed
[GHSA-mrhx-c7xc-m3w5 advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5),
published October 1 and updated October 23, affects versions below 4.6.6 and
names 4.6.6 as patched. It describes excessive memory allocation while collecting
validation errors for large arrays. These audit results establish an affected
dependency version, not an attacker-controlled application path to exhaustion.

All six client manifests now select exact version 4.6.6. The follow-up web report
at `/tmp/template-dependency-check-_3ik_0un/report.json` passes all five projects,
including fresh frozen installs, lint/types/builds, 44 authentication cases, and
production audits reporting no known vulnerabilities. Input hashes match the
checkout. Native's later SDK 58 audit is recorded below. No transitive version or
integrity entries were hand-edited.

## Native SDK and tooling

The old SDK 54 graph reported 130 audit findings: two critical, 85 high,
36 moderate, and seven low. Tooling and repeated transitive paths contribute to
that count. Two critical findings concern
[shell-quote, patched in 1.8.4](https://github.com/advisories/GHSA-w7jw-789q-3m8p)
and [tar, patched in 7.5.19](https://github.com/advisories/GHSA-23hp-3jrh-7fpw).
They were published May 22 and June 27 respectively. This is not evidence that
all findings are reachable in the installed mobile application.

The manifest selects Expo 58.0.22 with React 19.3.0, React Native 0.88.1,
and the [tagged native package map](https://raw.githubusercontent.com/expo/expo/expo@58.0.22/packages/expo/bundledNativeModules.json).
The October 31 [Expo release](https://github.com/expo/expo/releases/tag/expo@58.0.22)
names Babel preset 58.0.23. The rechecked
[SDK 58 preset manifest](https://raw.githubusercontent.com/expo/expo/sdk-58/packages/babel-preset-expo/package.json)
now agrees, resolving the moving-branch discrepancy recorded November 1.
The first SDK 58 install confirms these published versions, but the resolution
had failed on an old Metro runtime peer and therefore does not validate the graph.

The [SDK 58 preset implementation](https://raw.githubusercontent.com/expo/expo/sdk-58/packages/babel-preset-expo/src/configs/expo.ts)
automatically enables the installed Worklets plugin. The native Babel config
therefore removes its explicit Reanimated plugin. Input refs derive their type
from React Native's actual component. The SDK 58 type check exposed an upstream
declaration mismatch, addressed below.

Unused direct Tamagui config/toast packages and the unsupported web launch script
are removed. The used Tamagui 1 packages and compiler remain pinned at 1.144.1
while their new-SDK binary/device compatibility is evaluated. No fresh primary
evidence establishes that a Tamagui
3 migration is required. Burnt and the retained Tamagui implementation still need
actual native binary/device checks; permissive peers do not prove compatibility.

Node's [October 21 security releases](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)
set reviewed floors of 22.23.4, 24.22.1, and 26.12.1 on those release lines.
The observed local Node 24.11.1 satisfies Expo's engine range but predates that
security floor. Updating the project's dependencies does not update the host
runtime. Record a patched runtime for final checks and built images.

## Installed SDK 58 findings

Expo Router 58.0.29 and router-server 58.0.20 require Metro runtime `^58.0.16`,
but the lock retained the auto-installed SDK 54 runtime 6.1.2. The native manifest
now declares `@expo/metro-runtime: ~58.0.16`, matching the tagged Expo map. This
makes the required peer explicit and includes it in Expo's direct-package check.
The later frozen installation's skipped resolution did not clear the earlier
peer error. Keep strict peer validation and require a successful resolver first.

RN's [strict TypeScript API](https://reactnative.dev/docs/strict-typescript-api)
separates input components from their ref instances. Inspection of the installed
Tamagui source and native JavaScript confirms it forwards the real input ref;
its `types/views/Input.d.ts` instead uses the old `TextInput` component type as
an instance. Both application and Tamagui resolve the same RN package, excluding
duplicate RN installations as the cause of these three errors.

The deliberate patch at `patches/tamagui@1.144.1.patch` aliases the native
component and derives its instance with `React.ComponentRef`. It changes no
JavaScript behavior and avoids casts or disabling the strict API. pnpm records
the exact-version patch; Docker includes it before installing dependencies.
Dependency verification now fingerprints patches and rejects mutation, with a
regression that failed before the fingerprint repair and passes afterward.

The exact original TypeScript errors were reproduced. A newly generated project
at `/tmp/template-native-repair` preserves the patch bytes, and the patch passes
forward/reverse applicability checks. Its isolated SDK 58 dependency copy passes
lint/types plus 11 authentication and three storage tests with the corrected
declaration. This first check used a deliberate local declaration application.

The subsequent normal-terminal reports at
`/tmp/template-dependency-check-wfbkibzx/report.json` (06:34:19 EST) and
`/tmp/template-dependency-check-s_pzl5sv/report.json` (06:45:31 EST) both matched
the manifest, lock, and recorded patch hashes at that checkpoint.
Both passed strict frozen pnpm installation, Expo package alignment,
lint/types, all 14 authentication/storage cases, and both iOS and Android
exports. Those results verify that pnpm applies the recorded patch and that the
corrected Metro graph bundles both targets. Actual native execution remains open.

## SDK 58 dependency audit and resolver repair

Both pre-refresh audits stopped on 34 findings: one critical, 24 high, nine moderate.
The previous `--audit-level high` output displayed 25 advisory records and only
the count of moderate findings. The displayed records concern these seven package
groups. The dates and fixed versions below were rechecked against the linked
primary advisories on November 2; each published advisory is within the requested
recent research window.

| Dependency in the lock | Reviewed compatible fixed version | Advisory evidence |
| --- | --- | --- |
| shell-quote 1.8.3 | 1.9.0 or later on the existing range; 1.8.4 fixes the earlier critical advisory but not this later high finding | [GHSA-395f-4hp3-45gv](https://github.com/advisories/GHSA-395f-4hp3-45gv), published June 25 |
| picomatch 2.3.1 and 4.0.3; 4.0.7 is also present | 2.3.2 on the 2.x line, 4.0.4 on the 4.x line | [GHSA-c2c7-rcm5-vvqj](https://github.com/advisories/GHSA-c2c7-rcm5-vvqj), published March 23, updated March 27 |
| @xmldom/xmldom 0.8.11 | 0.8.15 on the 0.8 line | [GHSA-c7q8-3ch8-vqpv](https://github.com/advisories/GHSA-c7q8-3ch8-vqpv), published August 21, updated September 8 |
| ws 7.5.10 and 8.19.0 | 7.5.11 on the 7.x line, 8.21.0 on the 8.x line | [GHSA-96hv-2xvq-fx4p](https://github.com/advisories/GHSA-96hv-2xvq-fx4p), published May 22, updated July 13 |
| js-yaml 4.1.1 | 4.3.2 on the 4.x line | [GHSA-2883-xcg3-v3hh](https://github.com/advisories/GHSA-2883-xcg3-v3hh), published August 26, updated September 8 |
| browserslist 4.28.1 | 4.28.7 or later on the existing range | [GHSA-c83g-rgw3-j3cx](https://github.com/advisories/GHSA-c83g-rgw3-j3cx), published July 21, updated September 1 |
| compression 1.8.1 | 1.8.2 or later on the existing range | [GHSA-vc2v-76pw-4v95](https://github.com/advisories/GHSA-vc2v-76pw-4v95), published upstream September 11, GitHub review October 5 |

Inspection of the installed parent manifests confirms all listed fixes fit their
existing constraints. Examples include react-devtools-core's shell-quote `^1.6.1`,
Expo CLI's compression `^1.7.4` and ws `^8.12.1`, React Native's ws `^7.5.10`,
plist's xmldom `^0.8.8`, and Tamagui static tooling's js-yaml `^4.1.0`.
The audit establishes affected dependency versions and paths, including Expo,
Metro, and development tooling. It does not establish exploit reachability in a
shipped mobile application. That older output did not include the nine moderate
advisory details; the later full JSON audits identify the remaining findings.

The old resolver's `pnpm install --lockfile-only` reused existing satisfying
versions. A real offline fixture reproduced that behavior: a shell-quote
`^1.8.3` requirement retained its old 1.8.3 lock. Running the installed pnpm
10.34.9 with `update --depth Infinity --lockfile-only --no-save` moved that fixture
to 1.12.0 without changing the manifest. A separate exact-pin case stayed pinned.
This matches the documented [pnpm 10 update behavior](https://pnpm.io/10.x/cli/update).
That first refresh used no `--latest` flag or cross-major override.

The client resolver now uses that update command, followed by
`pnpm install --resolution-only --lockfile-only --no-frozen-lockfile
--strict-peer-dependencies`. The second command matters: a real incompatible-peer
fixture made pnpm's update warn and succeed, while the resolution-only command
failed. Exercising the actual helper confirmed it stops on that failure; the
compatible-peer fixture completed both commands and preserved its exact pin.

Local and CI client checks now run `pnpm audit --prod --json`. The installed pnpm
implementation filters JSON advisories by `--audit-level` too, so retaining the
old high threshold would still omit the moderate details. Removing that option
both records the complete advisory set and strengthens the gate to fail on any
reported severity. That first repair added no advisory ignores or transitive overrides.

The networked resolution at `/tmp/template-dependency-resolution-4hkntnx_`
refreshed the native graph. All seven package groups above now resolve at or
above the reviewed fixed versions. The initial fresh run stopped in Biome;
subsequent verification is recorded below. Registry DNS remains unavailable to
this runner, so live audit results come from the retained normal-terminal runs.

## Biome migration and the remaining two advisories

The deep refresh upgraded Biome from 2.3.11 to 2.6.4 within the old declared range.
`/tmp/template-dependency-check-x17swp_a` reproduced ten raw-text diagnostics and
one export-order diagnostic. TypeScript passed independently. The four flagged
card components extend Tamagui Text, whose native rendering uses the base Text
component. The rule's documented
[additional text component option](https://biomejs.dev/linter/rules/no-react-native-raw-text/javascript/)
now registers those four names. Separate fixtures confirm View and CardFooter
still fail the rule. The configuration uses the current schema/preset, the export
list is ordered, and Biome is pinned to 2.6.4. pnpm updated the lock; no integrity
entries were edited manually.

`/tmp/template-dependency-check-ar8prrrn/report.json` then passed frozen
installation, Expo alignment, lint/types, 14 auth/storage cases, and both exports.
Its complete JSON audit reported two moderate advisories and zero high/critical
findings. Both were published October 27 and reviewed/updated October 30:

| Package in that graph | Patched floor | Primary advisory |
| --- | --- | --- |
| glob 13.0.6 | 14.0.2 | [GHSA-3g3m-2fjr-6pw4](https://github.com/advisories/GHSA-3g3m-2fjr-6pw4): cancelled walks can continue filesystem traversal |
| minimatch 10.2.6 | 11.0.1 | [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249): supplied patterns can amplify preprocessing work |

The reported paths initially pointed through Expo CLI. A scoped CLI override
passed its six compatibility cases and both exports in
`/tmp/template-dependency-check-m__p733r`, but the audit still reported the same
two advisory IDs through config. The paths were representative, not exhaustive.
Inspection of every installed parent, `pnpm why --prod`, and the lock graph found
five production glob consumers: CLI 58.1.18, config 58.0.10, config-plugins
58.0.11, fingerprint 0.21.8, and metro-config 58.0.20. Fingerprint also requires
minimatch 10 directly.

The current manifest overrides only those exact parent/dependency pairs to glob
14.0.3 and minimatch 11.0.4. This crosses upstream major-version constraints and
must be reviewed again when any parent changes. The
[glob 14 changelog](https://raw.githubusercontent.com/isaacs/node-glob/v14.0.3/changelog.md)
describes matcher and edge-case pattern changes as well as cancellation fixes.
The installed Expo consumers use its public matching, synchronous discovery,
asynchronous discovery, and stream APIs. Eleven executable cases cover their
actual routing, native project paths, workspace discovery, fingerprint ignore
semantics, first-match cancellation, and pre-cancelled traversal behavior.
The pre-cancelled case passes on the old version too; it is a compatibility check,
not a reproduction of the cancellation advisory.

pnpm generated the full override lock offline after the required metadata became
available. A traversal of all 695 production snapshot nodes found only glob
14.0.3 and minimatch 11.0.4, including fingerprint's direct reference. The retained
graph inventory is `/tmp/template-native-production-glob-closure.json`.
`/tmp/template-dependency-check-dt4bpkh_/report.json` verifies the complete set:
fresh strict frozen installation, Expo alignment, lint/types, all 25 regressions,
both exports, and a production audit with zero findings at every severity across
696 dependencies. The separate graph inventory counts 695 dependency snapshot
nodes. Manifest, lock, patch, Biome config, and
input source match the checkout. No advisory ignore was added. Glob 9 remains
under the development-only Babel module resolver and is outside the production
audit; the clean production result does not claim that every development package
has no advisories.

## Next verification

1. The five web clients have passed their Zod 4.6.6 follow-up; their Vite configs
   also use `import.meta.dirname`. Preserve that completed report.
2. Preserve the passing native report and full JSON audit. The tested host was
   Node 24.11.1; final release checks still need the patched runtime noted above.
   Continue with PostgreSQL and generated Docker runtime verification.
3. Run a recorded Expo Doctor version on a generated native project, then build
   and exercise real iOS/Android binaries. Expo Doctor 1.21.5 was found in current
   upstream source; its registry dist-tag was not independently established.
4. Verify the behaviors listed in the November 1 report, including gestures,
   fonts, input refs, biometrics, navigation, secure storage, logout persistence,
   and background/foreground transitions. An export cannot close these gates.

The local checker and CI now enforce strict peers, Expo package alignment, and
iOS plus Android exports. Full output is retained in logs while the local
terminal defaults to brief command/result output. This improves recoverability
after a terminal failure; it is not a diagnosed fix for the Konsole crash.
