<!-- ©AngelaMos | 2026 -->
<!-- 2026-10-25-web-native.md -->

# Web and native release research, 2026-10-25

The five web clients have a coherent upgrade path: refresh the maintained dependency lines, replace the old `rolldown-vite` preview with stable Vite 8, and test the authentication transport through each actual backend. Native requires an Expo SDK migration with its React, React Native, native modules, Babel preset, and animation packages moving together. A successful JavaScript export does not establish native binary compatibility or secure credential lifecycle behavior.

This is research and source inspection, not a completed package upgrade or runtime security certification. No manifests, lockfiles, application source, or installed dependencies were changed by this research task.

## Evidence boundary

New recommendations below use primary evidence published or substantively updated from **2026-02-25 through 2026-10-25**, inclusive. Dates shown are release, advisory publication, specification publication, or substantive changelog dates. Search crawl dates are not evidence of freshness. Undated current source and documentation are identified as corroboration, and older evidence is segregated rather than presented as new research.

Version targets are candidates supported by maintainer evidence. They still require package registry resolution, lockfile generation, a frozen installation, and the validation matrix below. A maintainer release is evidence that a version exists; it is not proof that this repository passes with it. Advisory floors cover the identified advisory, not every possible issue in the ecosystem.

The source observations are a snapshot during concurrent release work on 2026-10-25. Findings about the refresh implementation should be reconciled with the implementation diff before marking them open or fixed.

## Runtime and lockfile inventory

The manifests, lockfile importers, Vite configuration, API client, and router files were read for all five web clients:

| Client | Actual application boundary |
| --- | --- |
| `frontends/auth/react-scss` | Vite SPA, browser router, bearer access token in memory, refresh through cookies; development proxy uses `VITE_API_TARGET` with a host-backend fallback |
| `frontends/open/react-scss` | Vite SPA without the auth refresh machinery; API client remains available for projects to extend |
| `stacks/fastapi-react/frontend` | Vite SPA through `/api` to FastAPI; browser refresh cookies |
| `stacks/go-react/frontend` | Vite SPA through `/api` to Go; `X-Auth-Transport: cookie` selects the browser contract |
| `stacks/portfolio/frontend` | Vite SPA through `/api` to its FastAPI backend; shares the generic auth infrastructure |

All five web lockfiles resolve React and React DOM **19.2.1**, React Router DOM **7.10.1**, Axios **1.13.2**, React Query **5.90.12**, Query Devtools **5.91.1**, Zustand **5.0.9**, Zod **4.1.13**, TypeScript **5.9.3**, `@vitejs/plugin-react` **5.1.2**, and `vite` aliased to **rolldown-vite 7.2.5**. Both the dependency declaration and `pnpm.overrides.vite` pin the preview. All package managers are pinned to **pnpm 10.29.1**. Docker build and development stages use the floating **node:22-slim** tag and the same pnpm pin. The concrete Node patch in an already cached image remains unverified.

The build command is `tsc -b && vite build`. Configuration explicitly sets `build.target: 'esnext'`, `cssTarget: 'chrome100'`, `minify: 'oxc'`, hidden production sourcemaps, and manual vendor chunks. These are browser compatibility and artifact publication decisions, not generic defaults to overlook during the migration. The production Nginx configurations serve static assets; the development server is not the production application server.

Native at `frontends/auth/react-native` resolves Expo **54.0.31**, React **19.1.0**, React Native **0.81.5**, Expo Router **6.0.21**, SecureStore **15.0.8**, Tamagui packages **1.144.1**, Reanimated **4.1.6**, Worklets **0.7.1**, Babel core **7.28.5**, and Babel preset Expo **54.0.9**. Its Query packages are **5.90.16 / 5.90.18**, Axios is **1.13.2**, Zod is **4.3.5**, and Zustand is **5.0.9**. The React and React DOM overrides force **19.1.0**. `main` is `expo-router/entry`; the root layout and inspected route modules have default exports. The root Tamagui config correctly forwards the named and default configuration exports.

Native API calls use the FastAPI mobile endpoints, memory-only access tokens, and a SecureStore refresh token. The API URL must be HTTP(S), with HTTPS enforced outside development. Authentication state persistence excludes access and refresh tokens. Query persistence is opt-in through `meta.persist === true`, with a cache buster and no persisted mutations.

## Upgrade decision matrix

| Component | Minimal verified boundary | Recommended candidate and compatibility gate | Fresh primary evidence |
| --- | --- | --- | --- |
| Web React / React DOM 19.2.1 | **19.2.7** is a verified same-minor maintenance release, not an assertion that these SPAs have an RSC vulnerability | **19.3.1**, with React and React DOM aligned; rerun types, route loading, forms, error boundaries, StrictMode, and production rendering | [19.2.7 release](https://github.com/react/react/releases/tag/v19.2.7), **2026-06-01**; [19.3.1 release](https://github.com/react/react/releases/tag/v19.3.1), **2026-10-14** |
| React Router 7.10.1 | **7.18.0** fixes the reviewed untrusted-path navigation bypass; **7.18.2** additionally covers the reviewed RSC-only CSRF follow-up | **7.18.4**, staying on the current major. Router 8 exists, but changing application mode or adopting its major migration is unnecessary to resolve these reviewed 7.x issues | [7.18.4 release list and tag](https://github.com/remix-run/react-router/releases), **2026-09-15**; advisory details below |
| Axios 1.13.2 | **1.20.0** for the reviewed September prototype-pollution gadgets | **1.20.0**, browser and native adapters tested separately, including interceptor retry behavior and header typing | [1.20.0 release](https://github.com/axios/axios/releases/tag/v1.20.0): release notes **2026-08-19**, GitHub release publication **2026-08-24**; advisory publication **2026-09-16** |
| rolldown-vite 7.2.5 | No fresh patched preview version was independently established. Standard Vite **7.3.7** addresses the reviewed October advisory, but is a different bundler path and is not a drop-in claim for the preview | **Vite 8.3.5** plus **@vitejs/plugin-react 6.1.2**; replace the alias and its override, then check SCSS, chunks, HMR, proxies, sourcemaps, and browser output | [Vite 8 announcement](https://vite.dev/blog/announcing-vite8), **2026-03-12**; [8.3.5 release](https://github.com/vitejs/vite/releases/tag/v8.3.5), **2026-10-21**; [React plugin releases](https://github.com/vitejs/vite-plugin-react/releases), **6.1.2 on 2026-10-05** |
| pnpm 10.29.1 | **10.34.2** for the reviewed repository configuration secret-interpolation advisory | **10.34.7** as the smaller maintenance upgrade; update every manifest and Docker pin together. A move to 11 or 12 requires an explicit configuration and lockfile migration | [10.34.7 release](https://github.com/pnpm/pnpm/releases/tag/v10.34.7), **2026-10-12**; advisory **2026-06-10** |
| Node 22 Docker stages | **22.23.4** incorporates the October security release for the current major | Pull and verify **22.23.4** first; **24.22.1** is a separately testable upgrade candidate. Record the resolved image digest and actual `node --version` | [Node security release](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases), **2026-10-21** |
| TanStack Query and persistence/devtools packages | No new security floor established by this review | Align the relevant packages on **5.104.5**, a verified same-major release set; validate auth query invalidation, cancellation, refetch, and cache restoration | [maintainer release](https://github.com/TanStack/query/releases/tag/release-2026-10-19-1659), **2026-10-19** |
| Zustand 5.0.9 | No new security floor established by this review | **5.0.16**, with persisted state hydration, selector behavior, and logout tests | [5.0.16 release](https://github.com/pmndrs/zustand/releases/tag/v5.0.16), **2026-10-22** |
| Zod 4.1.13 / 4.3.5 | No new security floor established by this review | **4.6.7**, retaining major 4; validate actual login, registration, profile, pagination, and backend error payloads instead of relying only on TypeScript | [4.6.7 release](https://github.com/colinhacks/zod/releases/tag/v4.6.7), **2026-10-12** |
| Expo 54 / RN 0.81 | Retaining SDK 54 can preserve a baseline for diagnosis, but is not a supported public release recommendation under the maintainer's current maintenance note | Migrate SDKs sequentially, ending on **SDK 58** if the native matrix passes. **SDK 57 with expo >=57.0.17** is an intermediate candidate with the documented Hermes fixes | [SDK 55](https://expo.dev/changelog/sdk-55), **2026-02-25**; [SDK 57](https://expo.dev/changelog/sdk-57), **2026-06-30**, substantive regression update **2026-08-27**; [SDK 58](https://expo.dev/changelog/sdk-58), **2026-10-15** |
| Native React and native peers | Keep the existing Expo-compatible tuple while establishing the baseline; do not transplant the web React upgrade into RN 0.81 | Select React, RN, Router, gestures, screens, safe-area, SVG, Reanimated, Worklets, and Expo modules from the chosen Expo release's compatibility map | SDK release evidence above; current maintainer [SDK 58 compatibility map](https://raw.githubusercontent.com/expo/expo/sdk-58/packages/expo/bundledNativeModules.json) is corroboration, not an independently dated release |
| Tamagui 1.144.1 | No fresh same-major patch or support guarantee was established | **3.1.3** is a verified current release, but v1 to v3 is an intentional UI/compiler migration. Keep all `tamagui` and `@tamagui/*` packages aligned and validate the existing tokens, themes, styled components, and Babel plugin. Do not enable the optional native runtime beta just to refresh dependencies | [Tamagui 3 announcement](https://tamagui.dev/blog/version-three), **2026-10-09**; [3.1.3 release](https://github.com/tamagui/tamagui/releases/tag/v3.1.3), **2026-10-23** |
| Babel core 7.28.5 | **7.29.6** for the reviewed source-map disclosure advisory | Refresh compatible Babel 7 packages under the selected Expo preset. Babel's monorepo **7.29.11** release is verified, but it is not proof that every individual Babel package has that version; resolve the actual core target before editing | [Babel advisory](https://github.com/babel/babel/security/advisories/GHSA-4x5r-pxfx-6jf8), **2026-06-13**; [Babel releases](https://github.com/babel/babel/releases), **7.29.11 on 2026-10-23** |
| Expo SecureStore 15.0.8 | No verified SDK 54 backport of the newly documented deletion/accessibility fixes | Use the SecureStore release selected by SDK 58, then test failed deletion, overwrite accessibility, reinstall, and session revocation. Current SDK 58 map selects **~58.0.2** | [SecureStore changelog](https://github.com/expo/expo/blob/main/packages/expo-secure-store/CHANGELOG.md), substantive **58.0.0 entry dated 2026-09-10** |

The Vite 8 release retains Node requirements of 20.19+ or 22.12+. The proposed Node 22 security patch satisfies them. The current React plugin source declares Vite 8 as its peer and Node 20.19+/22.12+ as its engine; this corroborates the dated plugin release. The [Vite migration guide](https://vite.dev/guide/migration) explicitly describes replacing the `rolldown-vite` alias with Vite 8. That guide is current but undated, so the March release supplies the freshness evidence. Its browser defaults do not override this repository's explicit `esnext` target.

The [pnpm 11 announcement](https://pnpm.io/blog/releases/11.0), **2026-04-28**, documents Node 22+, non-auth configuration moving out of `.npmrc`, removal of the `pnpm` field in `package.json`, and changed dependency build policies. This repository currently uses both `.npmrc` and `package.json` overrides. Merely changing the package manager pin across a major would therefore be incomplete. The maintainer's [12.15.0 release](https://pnpm.io/blog/releases/12.15.0), **2026-10-21**, also means any earlier claim that pnpm 11 is the current latest major is stale.

## Advisory applicability, independently checked

### React and React Router

These web applications use `createBrowserRouter` and Vite SPA output, without an RSC server build. No `react-server-dom-*` package resolution was found in the five web lockfiles. Native Expo Router has an optional RSC peer declaration, which is not itself an installed RSC server or an enabled RSC application. React version numbers alone do not establish exposure to React Server Component vulnerabilities.

The Router advisory [GHSA-jjmj-jmhj-qwj2](https://github.com/remix-run/react-router/security/advisories/GHSA-jjmj-jmhj-qwj2), **2026-07-22**, affects React Router 7.9.6 through 7.12.0 and is patched at 7.13.0. It requires an application with an open redirect. The later navigation bypass [GHSA-wrjc-x8rr-h8h6](https://github.com/remix-run/react-router/security/advisories/GHSA-wrjc-x8rr-h8h6), also **2026-07-22**, covers attacker-supplied navigation paths below 7.18.0. These are dependency matches; an exploitable redirect is not proved merely by matching the lockfile. Test saved return paths, double slashes, backslashes, encoded delimiters, and non-HTTP schemes before calling redirect handling safe.

[GHSA-qwww-vcr4-c8h2](https://github.com/remix-run/react-router/security/advisories/GHSA-qwww-vcr4-c8h2), **2026-07-22**, expressly affects unstable RSC APIs and is patched at 7.18.2 / 8.3.0. That execution mode was not found here. It must not be reported as a demonstrated SPA CSRF flaw.

### Axios

[GHSA-j8rh-479h-cp32](https://github.com/axios/axios/security/advisories/GHSA-j8rh-479h-cp32), **2026-09-16**, describes inherited header injection after a trusted interceptor returns a replacement ordinary object without an own `headers` property. It additionally requires another same-process prototype pollution primitive. The inspected clients mutate and return the existing config and explicitly initialize headers. The advisory is a reason to refresh Axios, but its complete exploit conditions are not established in this source.

[GHSA-vh66-26gq-q6x8](https://github.com/axios/axios/security/advisories/GHSA-vh66-26gq-q6x8), **2026-09-16**, is a fetch-adapter gadget requiring prior prototype pollution. The application does not explicitly select `adapter: 'fetch'`; adapter selection must be verified in each actual runtime. Node HTTP/2 and proxy advisories are not automatically browser vulnerabilities. Both reviewed gadgets name 1.20.0 as patched.

The [maintainer repository incident thread](https://github.com/axios/axios/issues/10604), opened **2026-03-31** with collaborator responses that day, records the compromised releases **1.14.1 and 0.30.4**. The six inspected lockfiles instead resolve 1.13.2 and contain no `plain-crypto-js` package resolution. This is a lockfile observation, not a claim about historical host installations. Upgrade directly to the reviewed target, inspect the new lockfile and package integrity, and do not use the compromised intermediate versions as upgrade steps.

### Vite development exposure

[GHSA-p9ff-h696-f583](https://github.com/vitejs/vite/security/advisories/GHSA-p9ff-h696-f583), **2026-04-06**, documents file access through the development WebSocket path. It affects standard Vite 7 through 7.3.1, with 7.3.2 patched, and requires an exposed development server with WebSockets enabled. This repository binds development Vite to `0.0.0.0`, so that configuration condition exists. However, the locked package is the `rolldown-vite` fork; the standard Vite advisory range is not direct proof about the fork's code. A source comparison or bounded reproduction is still required for a confirmed fork vulnerability.

[GHSA-rq7h-c2jc-7f22](https://github.com/vitejs/vite/security/advisories/GHSA-rq7h-c2jc-7f22), **2026-10-06**, adds a Linux/macOS development file-read condition involving project paths that coincide with host paths. Patched standard versions include 7.3.7, 8.1.6, 8.2.4, and 8.3.3. The full path preconditions have not been reproduced here. Vite 8.3.5 is above the reviewed 8.3 patch floor. High host ports alone do not constrain who can reach a bound development server.

### Build tooling

[GHSA-3qhv-2rgh-x77r](https://github.com/pnpm/pnpm/security/advisories/GHSA-3qhv-2rgh-x77r), **2026-06-10**, affects pnpm below 10.34.2. Malicious repository configuration can expand environment variables into registry requests before install scripts run. Current templates do not contain the malicious registry configuration, but their 10.29.1 manager pin is within the affected range. This matters for a public generator expected to fetch and install projects. Skipping lifecycle scripts is not a complete mitigation for this particular advisory.

[GHSA-4x5r-pxfx-6jf8](https://github.com/babel/babel/security/advisories/GHSA-4x5r-pxfx-6jf8), **2026-06-13**, affects Babel core through 7.29.0 and fixes the issue at 7.29.6. Its source-map disclosure requires attacker-controlled compilation input, readable output, and a known source-map path. Current core 7.28.5 matches, including the web plugin's transitive version. Ordinary trusted-source compilation is not the advisory's exploit scenario.

[GHSA-fv7c-fp4j-7gwp](https://github.com/babel/babel/security/advisories/GHSA-fv7c-fp4j-7gwp), **2026-05-05**, specifically affects the SystemJS transform through 7.29.3, patched at 7.29.4. A vulnerable package appearing transitively does not prove execution: the inspected Babel configuration selects Expo and Tamagui, with no `modules: 'systemjs'` configuration. Refresh the graph and inspect its usage before classifying reachability.

## Authentication behavior requiring verification or correction

The following are source findings, not claims borrowed from an advisory.

Implementation follow-up, October 25: the baseline findings below are retained
for provenance. All five clients now use a refresh promise scoped to a local
session version, reject obsolete requests/responses, and guard logout callbacks.
The expanded harness executes actual clients and logout hooks with installed
Axios and React Query mutation observers: 11 cases pass per client, 55 total.
Three tests of the actual native storage wrapper also pass, covering ordered
write/delete operations and a failed write. Platform transport, state, and keychain
adapters are controlled fixtures. Browser cookie ordering, multiple tabs, device
execution, and SDK/lock upgrades remain separate requirements.

1. **Late refresh subscribers can remain unresolved.** In each authenticated web client and native, a successful refresh drains subscribers, then awaits the original retried request while `isRefreshing` is still true. A second request whose old-token 401 arrives during that await is added to the now-empty queue. If the original retry succeeds, `finally` only changes the boolean; nothing resolves the late subscriber. A pending API promise can therefore survive indefinitely.
2. **The refresh try/catch also covers the retried business request.** A successful refresh followed by an unrelated 403, 404, 500, or transport failure on the original request is caught as a refresh failure and triggers logout. Refresh completion and business-request completion need separate failure boundaries.
3. **Deduplication is local to one JavaScript realm.** No BroadcastChannel, Web Locks, or storage-event synchronization was found. Two tabs can present the same rotating cookie before either receives its replacement. Test this against the actual FastAPI and Go replay/revocation logic before selecting coordination behavior. This is a scenario to reproduce, not proof that every two-tab use logs the user out.
4. **Logout can race with refresh.** Test whether a response already in flight restores access or refresh credentials after logout, password change, or an account switch. A session generation or cancellation boundary can prevent stale responses from restoring a deliberately cleared session.
5. **Persisted UI state is not authentication authority.** The existing protected route refreshes the current user rather than trusting persisted roles. Preserve that behavior while validating expired cookies, startup hydration, browser back navigation, and user switching.

Representative source locations at initial inspection: `frontends/auth/react-scss/src/core/api/api.config.ts:142`, `stacks/go-react/frontend/src/core/api/api.config.ts:143`, `frontends/auth/react-native/src/core/api/api.config.ts:187`, and the corresponding FastAPI/portfolio copies. These findings were handed to the implementation owner during the audit.

Implementation update, 2026-10-25: the implementation owner reproduced and fixed findings 1 and 2 in all four authenticated web clients and native. The revised clients retry an already-refreshed token for a late old-token 401 and keep the business request outside the refresh failure boundary. The new `tests/release/test_client_refresh.mjs` executes the actual TypeScript interceptors with installed Axios, a custom adapter, and mocked state/storage. The owner reports all three scenarios passing for each client: late 401 during a pending first retry, application 500 after successful refresh without logout, and ten concurrent 401s sharing one refresh with every request settling. The old implementation failed the first two scenarios. This research task inspected the test and revised interceptors; it did not independently rerun those tests. Portfolio used sibling dependencies, so these results do not establish a clean portfolio installation. Cross-tab coordination, logout/refresh races, and device credential deletion remain open verification items.

For further simplification, a shared refresh promise could make the refresh lifetime explicit; the current queue implementation can also satisfy the tested boundary. Requests sent with an older access token should retry the already-refreshed token rather than immediately rotating again. Cross-tab coordination additionally needs a browser-supported lock/session notification design and backend race tests. Do not persist raw tokens in localStorage merely to share them between tabs.

[RFC 10017](https://www.rfc-editor.org/rfc/rfc10017.html), **August 2026**, supplies fresh browser-token threat analysis: HttpOnly cookies prevent direct JavaScript reads of session material, but malicious same-origin script can still perform authorized requests. A full backend-for-frontend can keep access tokens out of browser JavaScript, at the cost of proxying API traffic. This repository implements first-party username/password authentication, not the full OAuth deployment described by that RFC. Its architectural comparison informs an optional future variant; it does not mandate an OAuth or BFF rewrite of these templates.

## Native migration and storage boundaries

The SDK 57 release note states that SDK 54 receives critical fixes until the next September/October 2026 SDK. SDK 58 was released on October 15. Taken together, that is evidence that retaining SDK 54 now exceeds the stated maintenance horizon. The same SDK 57 note was substantively updated on August 27 to identify **expo 57.0.17 / RN 0.86.3** as fixing Hermes regressions affecting Worklets and Reanimated. Do not stop on an older SDK 56/57 tuple while carrying those packages.

SDK 55 removes the Legacy Architecture option. This project already enables the New Architecture, but that obsolete option should be reconciled during migration. SDK 58's October release requires Node 22.13+ on the 22 line or 24.3+ on the 24 line; the proposed patched Node versions satisfy that boundary. SDK 58 also recommends development builds and warns that store-distributed Expo Go availability trails the SDK release. Docker Metro plus a phone is not interchangeable with a release binary build.

The currently published SDK 58 source map of compatible versions corroborates **React 19.3.0, RN 0.88.0, Reanimated 4.7.1, Worklets 0.13.0, gestures ~3.3.0, screens ~4.30.0, safe-area ~5.10.1, SVG 15.16.0, and SecureStore ~58.0.2**. These are the branch's observed compatibility values, not a lockfile generated here. Resolve the chosen Expo patch and its bundled map at installation time. Update/remove the old React 19.1.0 overrides as part of that atomic graph change. Web React 19.3.1 is not a reason to override the Expo-selected React version.

The direct `babel-preset-expo` declaration now matches the existing `presets: ['babel-preset-expo']` configuration. Keep the preset direct and aligned to the SDK. Route default exports and the Tamagui configuration default export are present; these are different concerns from preset resolution. The native Justfile's `ci` currently runs lint and typecheck, while EAS recipes only name iOS. Add explicit export checks for every advertised target and separately validate native build profiles. An iOS bundle export does not cover Android native linking or iOS signing/build settings.

SecureStore's **2026-09-10** changelog is directly relevant to this implementation. It documents fixes for Android deletion reporting success while a retried deletion leaves data on disk, iOS deletion reporting success when Keychain refuses removal, and `keychainAccessible` being ignored on overwrites. The existing wrapper sets `WHEN_UNLOCKED_THIS_DEVICE_ONLY`, catches errors and returns booleans, but some callers ignore deletion failure. `app.storage.ts` also starts `deleteItemAsync` from a `void` `removeItem`, so a caller cannot await actual deletion completion. Test both API failure and post-operation storage state; backend session revocation must remain authoritative.

The native package advertises `expo start --web`, but storage is implemented directly with native SecureStore APIs and no web adapter. `react-dom` and `react-native-web` are currently resolved through the peer graph rather than explicit application dependencies. A supported native-web target therefore requires a deliberate browser authentication/storage path, explicit direct dependencies, export validation, and runtime login testing. Otherwise narrow the advertised support to the native platforms instead of exposing a misleading web command. Browser localStorage is not an equivalent secure storage replacement.

The existing Reanimated **4.1.6 / Worklets 0.7.1** pair must not be called incompatible merely because a broad matrix says 4.1.x expects older Worklets. The maintainer's exact [4.1.6 release](https://github.com/software-mansion/react-native-reanimated/releases/tag/4.1.6) explicitly adds Worklets 0.7.x support. That release is **2025-12-04**, outside the requested freshness window, and is used only to correct the baseline compatibility claim. It does not justify retaining the old SDK for release.

Context7's SDK 54 SecureStore documentation was consulted for API semantics, but is undated and excluded as fresh recommendation evidence. Its platform behavior is background to the device test plan, not a substitute for the dated storage fixes or device execution. No fresh same-SDK backport of those fixes was verified.

## Neutral presentation and accessibility

Fresh accessibility evidence supports auditing complete tasks, not making the scaffold visually prescriptive. The [WCAG-EM 2.0 Group Note](https://www.w3.org/TR/2026/NOTE-wcag-em-2-20260723/), **2026-07-23**, provides an evaluation methodology spanning digital products, representative views, and complete processes. It is informative guidance, not a new set of WCAG requirements. Apply it to registration, login errors, expired sessions, settings, logout, and mobile equivalents, including loading and failure states.

The [WCAG 3 Working Draft](https://www.w3.org/TR/2026/WD-wcag-3.0-20260910/), **2026-09-10**, is explicitly work in progress. Its recent date does not make it a replacement release conformance target. Keep the established accessibility target and record which browsers, screen readers, native accessibility tools, and flows were actually tested.

For this scaffold, the implementation gate should include keyboard navigation, visible focus, field names and error association, password-manager/paste support, readable contrast, zoom/reflow, reduced motion, touch targets, and VoiceOver/TalkBack state announcements. These are concrete test cases, not claims that a screenshot or neutral color palette proves accessibility. Maintain simple layout and tokens so downstream projects can change visual direction without discarding working semantics.

## Validation matrix for the implementation pass

| Boundary | Variants | Required evidence before release |
| --- | --- | --- |
| Clean dependency installation | All five web clients and native, separately generated into clean directories | Correct package-manager and Node versions; fresh registry-backed lock resolution; frozen reinstall without an old `node_modules`; reviewed peer/build warnings; production and full dependency advisory output retained |
| Web compilation | All five web clients | Repository lint, SCSS lint, typecheck, production build; static serving through each variant's Docker/Nginx configuration; route reloads, missing routes, icons, fonts, and assets |
| Vite development | All five web clients | Docker HMR, arbitrary configured host ports, API proxy routing, backend startup ordering, host access policy; no assumption that a high port is private |
| Browser auth contracts | Standalone auth with its documented backend, FastAPI stack, Go stack, portfolio | Register/login/current-user/logout/logout-all/password-change; actual cookie Secure/HttpOnly/SameSite/path behavior; bad credentials do not initiate refresh; CORS/Origin rejection and same-origin proxy behavior |
| Refresh concurrency | Every authenticated web client and native | Simultaneous 401s cause one refresh; a late old-token 401 completes; retry failure does not falsely invalidate a valid session; cancellation/timeout releases all waiters; logout during refresh cannot restore a session |
| Multiple browser contexts | FastAPI, Go, portfolio | Two tabs refreshing together; logout and password change from another tab; account switching with cached queries; no raw token persisted for synchronization |
| Native JavaScript | iOS and Android, plus web only if advertised | Frozen install, `pnpm exec expo install --check`, a pinned/reviewed Expo Doctor invocation, lint/typecheck, production exports for each target, expected Babel/Metro/Tamagui resolution |
| Native binary/runtime | iOS development/release build and Android debug/release build | Autolinking and New Architecture compatibility; gestures, transitions, screens, safe-area, fonts, biometrics, deep links, API TLS, background/foreground transitions |
| Native credentials | Both operating systems | Restart, lock/unlock, expired/revoked token, failed write/delete, logout offline, reinstall, backup restore, changed biometric enrollment if authentication-bound storage is enabled, cache purge after account changes |
| Accessibility | Representative web and native complete flows | Keyboard and screen-reader runs, zoom/text scaling, reduced motion, contrast and focus checks, actionable error announcements; record actual tool and platform versions |
| Generated output parity | Each public variant | Re-run installation/build/auth checks from generator output rather than only in the template checkout; confirm placeholder replacement preserves pins, API URLs, ports, and compose commands |

The exact Expo Doctor package version, final Expo patch, current Babel core 7.x target above the patch floor, transitive advisory inventory, Docker image digests, and final peer graph remain unresolved until network-backed package resolution is available. No Docker/PostgreSQL matrix, browser concurrency reproduction, fresh dependency installation, emulator/device run, or native binary build was performed by this research task. Existing successful checks from other work must be reported separately with their actual environment and dependency graph.
