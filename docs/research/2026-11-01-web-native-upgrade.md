<!-- ©AngelaMos | 2026 -->
<!-- 2026-11-01-web-native-upgrade.md -->

# Web and native upgrade decisions, 2026-11-01

Use pnpm **10.34.9**, stable **Vite 8.3.5 / React plugin 6.1.2**, and the maintained Router 7 line for the five web clients. Native needs an Expo SDK migration as a coordinated dependency set. The verified current target is **Expo 58.0.22 / React 19.3.0 / React Native 0.88.1**. Tamagui 3 is a separate source migration, not a prerequisite established by a security advisory and not a safe version-only edit.

This report refreshes the October 25 research. New release and advisory evidence is dated **2026-03-01 through 2026-11-01**. Undated migration documentation and moving branches are explicitly corroborating sources. No dependency installation, lock generation, Docker operation, application build, or device test was performed by this research task. Listed targets are verified maintainer releases or compatibility-map values, not a tested dependency graph.

## Actual baseline

All six manifests, the two distinct lockfiles, all five Vite configs, the native Babel/app/Tamagui configs, and relevant native components were inspected. The five web lockfiles are byte-identical at this inspection; their Vite proxy targets differ by variant.

| Scope | Manifest / locked baseline |
| --- | --- |
| `frontends/auth/react-scss`, `frontends/open/react-scss`, `stacks/fastapi-react/frontend`, `stacks/go-react/frontend`, `stacks/portfolio/frontend` | React/DOM 19.2.1 locked; Router 7.10.1; Axios 1.13.2; TypeScript 5.9.3; plugin React 5.1.2; `vite` resolves to `rolldown-vite@7.2.5`, also forced by `pnpm.overrides.vite` |
| `frontends/auth/react-native` | Expo 54.0.31; React 19.1.0; RN 0.81.5; Router 6.0.21; SecureStore 15.0.8; Reanimated 4.1.6; Worklets 0.7.1; Tamagui packages 1.144.1; Babel core 7.28.5 / preset Expo 54.0.9; TypeScript 5.9.3 |
| All six | `packageManager: pnpm@10.29.1`, lockfile format 9.0; `.npmrc` sets `strict-dep-builds=false` and `auto-install-peers=true` |

The native manifest forces React and React DOM 19.1.0 through overrides. Its Babel config explicitly loads the Tamagui Babel plugin and `react-native-reanimated/plugin`; no custom Metro config exists. Every client uses `baseUrl: "."` with already-relative `./src/*` path mappings. Web builds explicitly select `esnext`, `chrome100`, hidden production maps, Oxc minification, and a function-form vendor chunk rule.

## Web and shared tooling candidates

| Component | Proposed declaration or floor | Dated primary evidence and decision |
| --- | --- | --- |
| pnpm | `pnpm@10.34.9` everywhere, including build/CI/generator pins | [10.34.9, October 25](https://github.com/pnpm/pnpm/releases/tag/v10.34.9), fixes recording the selected manager in fresh locks so subsequent frozen installs work. [10.34.8, October 25](https://github.com/pnpm/pnpm/releases/tag/v10.34.8), also refreshes the standalone embedded runtime. Prefer this small maintenance upgrade over migrating configuration to pnpm 12. |
| Web React / DOM | Align both to `19.3.1` for the modernization candidate | [19.3.1, October 14](https://github.com/react/react/releases/tag/v19.3.1). Its release note concerns RSC transport. This is not a demonstrated SPA security requirement; keeping the maintained 19.2 line is a smaller alternative. Do not apply the web React version to native independently of Expo. |
| React Router DOM | `7.18.5` | [7.18.5, October 27](https://github.com/remix-run/react-router/releases/tag/react-router@7.18.5). The [v7 changelog](https://raw.githubusercontent.com/remix-run/react-router/v7/CHANGELOG.md) records server/RSC route-processing bounds and stream decoding hardening. Remain on 7; adopting Router 8 is unnecessary for these fixes. |
| Axios, web and native | `1.21.0`; reviewed security floor `1.20.0` | [1.21.0 release](https://github.com/axios/axios/releases/tag/v1.21.0): release notes dated October 21, GitHub publication October 26. It changes header-default classification, so run the actual interceptor harness and adapter tests. `1.20.0` remains the narrower security-floor option. |
| Vite / plugin React | `vite: 8.3.5`, `@vitejs/plugin-react: 6.1.2`; remove the `rolldown-vite` override | [Vite 8.3.5, October 21](https://github.com/vitejs/vite/releases/tag/v8.3.5), and [plugin 6.1.2, October 5](https://github.com/vitejs/vite-plugin-react/releases/tag/plugin-react@6.1.2). The plugin's [tagged manifest](https://raw.githubusercontent.com/vitejs/vite-plugin-react/plugin-react@6.1.2/packages/plugin-react/package.json) requires Vite `^8.0.0` and Node `^20.19.0 || >=22.12.0`; optional compiler peers need not be enabled for `react()`. |
| TypeScript | `~6.0.3`, after removing obsolete `baseUrl` | [6.0.3, April 16](https://github.com/microsoft/TypeScript/releases/tag/v6.0.3). This is a deliberate bridge upgrade, not a security floor. [TypeScript 6, March 23](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/), describes the transition from 5.9 toward the new compiler. The current Expo SDK 58 template also chooses `~6.0.3`. Avoid adding TypeScript 7's compiler migration to the release dependency work. |
| Node runtime | On existing major 22, at least `22.23.4`; on major 24, at least `24.22.1` | [October 21 security release](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases). These are verified security floors, not claims of latest patches. Host Node 24.11.1 satisfies the SDK engine range but predates these fixes. Record the actual Node version inside each final build environment. |

Use exact candidate versions while resolving and testing the release, then retain the reviewed lockfiles. This report does not propose broad upgrades of every Query, Zustand, Zod, icon, SCSS, and lint package simultaneously. Their existing constraints should be resolved and audited, with additional changes driven by concrete peer failures or advisory evidence.

The [pnpm 11 migration announcement](https://pnpm.io/blog/releases/11.0), released April 28, documents configuration moving out of `.npmrc`, removal of the `package.json` `pnpm` field, Node 22+, and build-policy changes. Global pnpm 12.11.2 does not make these repositories pnpm 12 projects. Select the manifest-pinned manager explicitly and record the effective version before generating locks.

## Security applicability

| Finding | Verified scope and action |
| --- | --- |
| pnpm repository configuration secret expansion | [GHSA-3qhv-2rgh-x77r, June 10](https://github.com/pnpm/pnpm/security/advisories/GHSA-3qhv-2rgh-x77r), is fixed in 10.34.2. It can occur before lifecycle scripts, so disabling scripts alone does not address it. The current 10.29.1 pin is in range; no malicious template configuration was observed. |
| pnpm tarball and virtual-store path traversal | [GHSA-vq4v-j7r6-jq4m, August 2](https://github.com/pnpm/pnpm/security/advisories/GHSA-vq4v-j7r6-jq4m), and [GHSA-c59q-g84q-2gj5, August 3](https://github.com/pnpm/pnpm/security/advisories/GHSA-c59q-g84q-2gj5), set a higher reviewed 10.x floor of 10.34.5. Both require attacker-controlled dependency/lock input; neither establishes a compromised local checkout. |
| New standalone pnpm advisory | [GHSA-w8f5-6m3h-r453, October 30](https://github.com/pnpm/pnpm/security/advisories/GHSA-w8f5-6m3h-r453), affects embedded Node trust roots and lists 10.34.8 / 11.28.8 as patched. It distinguishes standalone `@pnpm/exe` from JavaScript pnpm running on the host Node. pnpm 12 may fetch a pinned older standalone manager, making both the pin and embedded runtime relevant. The advisory's broad narrative describes the pre-fix builds; use its explicit patched ranges and the dated release notes. |
| Router navigation bypass | [GHSA-wrjc-x8rr-h8h6, July 22](https://github.com/remix-run/react-router/security/advisories/GHSA-wrjc-x8rr-h8h6), affects versions below 7.18.0 when attacker-controlled paths reach navigation. The locked 7.10.1 matches; actual exploitability depends on a redirect input path. Test encoded separators and external schemes. RSC-only fixes are not evidence of a SPA flaw. |
| Axios inherited-header gadget | [GHSA-j8rh-479h-cp32, September 16](https://github.com/axios/axios/security/advisories/GHSA-j8rh-479h-cp32), identifies 1.20.0 as patched. It requires prior prototype pollution plus a trusted interceptor returning an ordinary replacement object without its own headers. Existing clients mutate their config and populate headers; this specific exploit chain is not established. Adapter-specific Node advisories must not be relabeled browser vulnerabilities. |
| Vite development file access | [GHSA-rq7h-c2jc-7f22, October 6](https://github.com/vitejs/vite/security/advisories/GHSA-rq7h-c2jc-7f22), is fixed in standard Vite 8.3.3 and 7.3.7. It requires exposed development service plus particular project/host path overlap on non-Windows. These configs bind `0.0.0.0`; the remaining conditions are unproven. The old fork cannot be declared affected solely from standard Vite version ranges. |
| Babel source-map read | [GHSA-4x5r-pxfx-6jf8, June 13](https://github.com/babel/babel/security/advisories/GHSA-4x5r-pxfx-6jf8), names core 7.29.6 as patched. It requires attacker-controlled compilation input, readable output, and a known map path. Native should resolve Babel 7 at or above this floor. A monorepo 7.29.11 release does not prove that `@babel/core@7.29.11` exists. |

These are reviewed advisory boundaries, not a complete transitive audit. Refresh production and full dependency audit output after the network-backed resolution. React RSC advisories cannot be inferred from the React version alone: the inspected web apps use browser routers and static Vite output.

## Native release tuple

Expo's [SDK 57 maintenance note, June 30](https://expo.dev/changelog/sdk-57), says SDK 54 receives critical fixes until the following September/October SDK release. [SDK 58 shipped October 15](https://expo.dev/changelog/sdk-58). Retaining SDK 54 for the public release therefore lacks current maintenance coverage under that note. SDK 57 with Expo at least 57.0.17 is useful as an intermediate diagnostic step because the August 27 update fixes documented Hermes regressions.

Use the [Expo 58.0.22 tag, October 31](https://github.com/expo/expo/releases/tag/expo@58.0.22), and its [tagged compatibility map](https://raw.githubusercontent.com/expo/expo/expo@58.0.22/packages/expo/bundledNativeModules.json), rather than choosing native package versions independently:

| Existing dependency | SDK 58 declaration |
| --- | --- |
| `expo` | `~58.0.22` |
| `react` | `19.3.0` |
| `react-native` | `0.88.1` |
| `@react-native-community/netinfo` | `12.0.1` |
| `expo-constants` | `~58.0.14` |
| `expo-haptics` | `~58.0.7` |
| `expo-linking` | `~58.0.15` |
| `expo-local-authentication` | `~58.0.2` |
| `expo-router` | `~58.0.29` |
| `expo-secure-store` | `~58.0.2` |
| `expo-splash-screen` | `~58.0.12` |
| `expo-status-bar` | `~58.0.4` |
| `react-native-gesture-handler` | `~3.3.0` |
| `react-native-reanimated` | `4.7.1` |
| `react-native-worklets` | `0.13.0` |
| `react-native-safe-area-context` | `~5.10.1` |
| `react-native-screens` | `~4.30.1` |
| `react-native-svg` | `15.16.0` |

The animation packages also have independent dated releases: [Reanimated 4.7.1, October 2](https://github.com/software-mansion/react-native-reanimated/releases/tag/4.7.1), and [Worklets 0.13.0, September 21](https://github.com/software-mansion/react-native-reanimated/releases/tag/worklets-0.13.0). Their presence in the Expo map is the compatibility evidence for this tuple.

The current [SDK 58 template manifest](https://raw.githubusercontent.com/expo/expo/sdk-58/templates/expo-template-default/package.json), a moving-source corroboration, selects `@types/react: ~19.3.0` and `typescript: ~6.0.3`. Align native React/DOM overrides with 19.3.0 or remove them after confirming the resolved graph has one compatible React. Do not leave the 19.1.0 override in place.

The Expo 58.0.22 release names **babel-preset-expo 58.0.23**. A separately fetched moving-branch preset manifest still returned 58.0.22, so the published release metadata and installed Expo dependency must settle that discrepancy. Candidate declaration: `~58.0.23`, subject to registry verification. Exact current Babel core patch and Expo Doctor version were not resolved. SDK 58's tagged Expo manifest requires Node `^22.13.0 || ^24.3.0 || ^26.0.0 || >=27.0.0`.

The [SecureStore changelog's September 10 entry](https://raw.githubusercontent.com/expo/expo/sdk-58/packages/expo-secure-store/CHANGELOG.md) fixes false-success deletion on Android/iOS and ignored accessibility changes on iOS overwrites. These are dated correctness fixes, not a separately verified CVE. SDK 54 backports were not established. Device tests must verify that token removal actually survives restart and that failed deletion cannot masquerade as logout success.

## Concrete migration surfaces

| Surface | Deliberate change and boundary |
| --- | --- |
| Five web `package.json` files | Change Vite and its plugin together; delete `pnpm.overrides.vite`; align React/DOM; raise Router/Axios; change manager pin. Preserve backend-specific API code. Resolve all five locks, including portfolio's own installation. |
| Five web `tsconfig.app.json`, native `tsconfig.json` | Remove `baseUrl` while retaining `"@/*": ["./src/*"]`. This small preparatory edit works without changing source imports. TypeScript 6 deprecates `baseUrl`; do not hide the migration with `ignoreDeprecations`. |
| Five web `vite.config.ts` | The current function-form `manualChunks` is deprecated, not removed. The [Vite migration guide](https://vite.dev/guide/migration), current undated corroboration, replaces the preview alias, renames `rollupOptions` to `rolldownOptions`, and recommends `output.codeSplitting`. First validate the same build behavior; then translate or remove the custom chunk rule based on measured output. Keep browser target and source-map exposure an explicit decision. |
| Native `package.json`, `babel.config.js`, `app.json` | Upgrade Expo-managed packages as one tuple. Review/remove legacy `newArchEnabled` configuration as directed by the chosen SDK. Prefer the matching Expo Babel preset's automatic Worklets integration; inspect its resolved config before removing the redundant explicit Reanimated plugin. Rebuild the native binary after changing native packages. |
| Native `src/shared/components/ui/Input.tsx`, `PasswordInput.tsx` | Existing refs use the old `TextInput` type. RN's [strict TypeScript API](https://reactnative.dev/docs/strict-typescript-api), corroborating the October SDK 58 release, introduces instance types. Use the actual new component ref type, such as `TextInputInstance`, after installing the tuple; verify Tamagui's input-ref contract rather than preserving broad casts. |
| Native `src/theme/tamagui.config.ts`, shared UI, routes, Babel/Metro | Tamagui 3.1.9 is the verified current candidate, released [October 30](https://github.com/tamagui/tamagui/releases/tag/v3.1.9). This is optional major modernization. No fresh guarantee that the existing 1.144.1 works with RN 0.88 was established. Test it during SDK migration before deciding whether it can be retained. |

If adopting Tamagui 3, use two source passes following the [October 9 announcement](https://tamagui.dev/blog/version-three) and its current [upgrade guide](https://tamagui.dev/docs/guides/how-to-upgrade): apply v1-to-v2 API changes first, including `Stack` to `View`, then v2-to-v3. The local code uses `Stack`, `createMedia`, custom tokens, input wrappers, and a Babel plugin that require review. V3 removes `@tamagui/babel-plugin` and the `createMedia` call. Preserve the custom theme intent while updating token/component APIs. `@tamagui/config` and `@tamagui/toast` have no imports in inspected app/source files, so assess removal instead of blindly assigning them new versions. Keep retained Tamagui packages on one release. Do not enable the optional native runtime beta.

The current [Tamagui Metro guide](https://tamagui.dev/docs/guides/metro) says Expo's default Metro config works without a compiler plugin. That is the smallest starting point after removing the obsolete Babel plugin. Add the aligned `@tamagui/metro-plugin` only if config watching or extraction is required; its cost is an extra tooling dependency. No automated codemod writes are authorized by this research report.

Native still advertises `expo start --web` while its credential storage uses SecureStore. A native SDK upgrade does not solve that platform contract. Either implement and test a browser auth/storage adapter with explicit web peers, or remove the unsupported web promise. Do not substitute browser persistent token storage merely to make export succeed. Third-party native modules such as `burnt` also need an actual RN 0.88 binary build; Expo's compatibility map does not certify them.

## Ordered verification

1. Apply the shared manager/security changes and the small TypeScript config preparation. Preserve current locks until network-backed resolution is available; do not hand-edit integrity or transitive resolution entries.
2. Resolve the five web candidates with the pinned manager. Perform clean frozen installations, lint, SCSS lint, typecheck, production build, and the existing actual-client auth tests. Inspect peer warnings, the effective adapter, header defaults, emitted maps, and the generated project's own dependency graph.
3. Migrate native through SDK checkpoints in a generated scratch project, using each SDK's matching `pnpm exec expo install --fix` and `--check`. Do not apply independent latest versions to RN peers. Resolve the preset discrepancy from the installed Expo package. Run a pinned, recorded Expo Doctor version.
4. Run native lint/typecheck, iOS and Android exports, then actual iOS/Android development and release builds. Exercise navigation, gestures, fonts, inputs, biometrics, deep links, background/foreground transitions, storage failure, refresh concurrency, account switching, offline logout, and restart after logout. An export alone cannot close binary/runtime gates.
5. Retain production/full advisory results and rerun the coordinated variant matrix from generated outputs. Mark release readiness only after those results exist. Research, candidate manifests, cached installs, and prior SDK 54 exports do not establish an upgraded release.

Open evidence: registry-resolved peer graph and lock integrity; exact Babel core/Doctor versions; the preset's published patch; native third-party module compatibility; actual binary/device behavior; fresh transitive audits. This task changed only this research document.
