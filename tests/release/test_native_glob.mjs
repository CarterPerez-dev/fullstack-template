// ©AngelaMos | 2026
// test_native_glob.mjs

import assert from 'node:assert/strict'
import * as fs from 'node:fs'
import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { test } from 'node:test'

const project = resolve(process.argv[2])
const projectRequire = createRequire(`${project}/package.json`)
const expoRequire = createRequire(projectRequire.resolve('expo/package.json'))
const cliManifest = expoRequire.resolve('@expo/cli/package.json')
const cliRequire = createRequire(cliManifest)
const cliRoot = dirname(cliManifest)
const { anyMatchAsync, everyMatchAsync } = cliRequire(join(cliRoot, 'build/src/utils/glob.js'))
const { getApiRoutesForDirectory, getMiddlewareForDirectory, getRoutePaths } = cliRequire(
  join(cliRoot, 'build/src/start/server/metro/router.js'),
)
const { resolveXcodeProject } = cliRequire(join(cliRoot, 'build/src/run/ios/options/resolveXcodeProject.js'))
const { globStream } = cliRequire('glob')
const { getDefaultTarget } = expoRequire('@expo/config')
const { AndroidConfig, IOSConfig } = expoRequire('@expo/config-plugins')
const metroRoot = dirname(expoRequire.resolve('@expo/metro-config/package.json'))
const { globAllPackageJsonPaths } = expoRequire(join(metroRoot, 'build/getWatchFolders.js'))
const fingerprintRoot = dirname(expoRequire.resolve('@expo/fingerprint/package.json'))
const { resolveProjectWorkflowAsync } = expoRequire(join(fingerprintRoot, 'build/ProjectWorkflow.js'))
const { buildDirMatchObjects, buildPathMatchObjects, isIgnoredPath, isIgnoredPathWithMatchObjects } = expoRequire(
  join(fingerprintRoot, 'build/utils/Path.js'),
)

async function fixture(t, files) {
  const root = await mkdtemp(join(tmpdir(), 'template-native-glob-'))
  t.after(() => rm(root, { recursive: true, force: true }))
  for (const file of files) {
    const path = join(root, file)
    await mkdir(dirname(path), { recursive: true })
    await writeFile(path, 'fixture\n')
  }
  return root
}

test('Expo async file discovery preserves dotfiles, extension groups, and ignores', async (t) => {
  const root = await fixture(t, ['.hidden/route.ts', 'routes/home.tsx', 'routes/help.jsx', 'ignored/skip.ts', 'readme.md'])
  const matches = await everyMatchAsync('**/*.@(ts|tsx|js|jsx)', {
    cwd: root, dot: true, ignore: ['**/ignored/**'],
  })
  assert.deepEqual(matches.sort(), ['.hidden/route.ts', 'routes/help.jsx', 'routes/home.tsx'])
})

test('Expo first-match discovery finishes after cancellation and when nothing matches', { timeout: 1500 }, async (t) => {
  const root = await fixture(t, ['routes/one.ts', 'routes/two.ts'])
  const matches = await anyMatchAsync('**/*.ts', { cwd: root })
  assert.equal(matches.length, 1)
  assert.ok(['routes/one.ts', 'routes/two.ts'].includes(matches[0]))
  assert.deepEqual(await anyMatchAsync('**/*.missing', { cwd: root }), [])
})

test('Expo router discovers API and component routes with native route names', async (t) => {
  const files = ['users/[id]+api.ts', '.internal/status+api.js', '(app)/home.tsx', 'readme.md']
  const root = await fixture(t, files)
  assert.deepEqual(getApiRoutesForDirectory(root).sort(), [join(root, '.internal/status+api.js'), join(root, 'users/[id]+api.ts')].sort())
  assert.deepEqual(getRoutePaths(root).sort(), files.filter((file) => file !== 'readme.md').map((file) => `./${file}`).sort())
})

test('Expo middleware discovery stays at the route root and rejects ambiguity', async (t) => {
  const root = await fixture(t, ['nested/+middleware.ts'])
  assert.equal(getMiddlewareForDirectory(root, 'development'), null)
  await writeFile(join(root, '+middleware.ts'), 'fixture\n')
  assert.equal(getMiddlewareForDirectory(root, 'development'), join(root, '+middleware.ts'))
  await writeFile(join(root, '+middleware.js'), 'fixture\n')
  assert.throws(() => getMiddlewareForDirectory(root, 'development'), /Only one middleware file is allowed/)
})

test('Expo Xcode discovery prefers the workspace and falls back to the project', async (t) => {
  const root = await fixture(t, ['ios/App.xcworkspace/contents.xcworkspacedata', 'ios/App.xcodeproj/project.pbxproj'])
  assert.deepEqual(resolveXcodeProject(root), { name: join(root, 'ios/App.xcworkspace'), isWorkspace: true })
  await rm(join(root, 'ios/App.xcworkspace'), { recursive: true })
  assert.deepEqual(resolveXcodeProject(root), { name: join(root, 'ios/App.xcodeproj'), isWorkspace: false })
})

test('a pre-cancelled CLI glob rejects before reading directory entries', { timeout: 1500 }, async (t) => {
  const root = await fixture(t, ['nested/example.txt'])
  const controller = new AbortController()
  controller.abort()
  let reads = 0
  await assert.rejects(async () => {
    const matches = []
    for await (const entry of globStream('**/*', {
      cwd: root,
      signal: controller.signal,
      fs: {
        ...fs,
        readdir(...args) {
          reads += 1
          return fs.readdir(...args)
        },
      },
    })) matches.push(entry)
    assert.deepEqual(matches, [])
  }, { name: 'AbortError' })
  await new Promise(setImmediate)
  assert.equal(reads, 0)
})

test('Expo config recognizes managed, iOS, and Android project layouts', async (t) => {
  const root = await fixture(t, [])
  await writeFile(join(root, 'package.json'), JSON.stringify({ name: 'native-glob-fixture' }))
  assert.equal(getDefaultTarget(root, {}), 'managed')
  await mkdir(join(root, 'ios/App.xcodeproj'), { recursive: true })
  assert.equal(getDefaultTarget(root, {}), 'bare')
  await rm(join(root, 'ios'), { recursive: true })
  await mkdir(join(root, 'android/app'), { recursive: true })
  await writeFile(join(root, 'android/app/build.gradle'), 'fixture\n')
  assert.equal(getDefaultTarget(root, {}), 'bare')
})

test('Expo config plugins find Kotlin, Swift, and project metadata paths', async (t) => {
  const activity = 'android/app/src/main/java/com/example/MainActivity.kt'
  const delegate = 'ios/App/AppDelegate.swift'
  const plist = 'ios/App/Info.plist'
  const root = await fixture(t, [activity, delegate, plist, 'ios/Podfile'])
  assert.equal(AndroidConfig.Paths.getProjectFilePath(root, 'MainActivity'), join(root, activity))
  assert.equal(IOSConfig.Paths.getAppDelegateFilePath(root), join(root, delegate))
  assert.deepEqual(IOSConfig.Paths.getAllInfoPlistPaths(root), [join(root, plist)])
  assert.equal(IOSConfig.Paths.getPodfilePath(root), join(root, 'ios/Podfile'))
})

test('Expo Metro discovers valid workspace packages and excludes dependency folders', async (t) => {
  const files = ['packages/mobile/package.json', 'packages/shared/package.json', 'packages/broken/package.json', 'packages/node_modules/hidden/package.json']
  const root = await fixture(t, files)
  for (const file of files.filter((file) => !file.includes('/broken/'))) {
    await writeFile(join(root, file), JSON.stringify({ name: dirname(file) }))
  }
  assert.deepEqual(globAllPackageJsonPaths(root, ['packages/**']).sort(), [join(root, files[0]), join(root, files[1])].sort())
})

test('Expo fingerprint respects native project ignore files without a git checkout', async (t) => {
  const root = await fixture(t, ['android/app/build.gradle', 'android/app/src/main/AndroidManifest.xml'])
  await mkdir(join(root, 'node_modules'))
  await symlink(dirname(projectRequire.resolve('expo/package.json')), join(root, 'node_modules/expo'), 'junction')
  assert.equal(await resolveProjectWorkflowAsync(root, 'android', []), 'generic')
  await writeFile(join(root, '.gitignore'), 'android/\n')
  assert.equal(await resolveProjectWorkflowAsync(root, 'android', []), 'managed')
})

test('Expo fingerprint matcher preserves ignore negation, dotfiles, and directory matching', () => {
  const patterns = ['assets/**', '!assets/public.txt']
  assert.equal(isIgnoredPath('assets/private.txt', patterns), true)
  assert.equal(isIgnoredPath('assets/public.txt', patterns), false)
  assert.equal(isIgnoredPath('.expo/cache.json', ['**/.expo/**']), true)
  assert.equal(isIgnoredPath('../node_modules/package/index.js', ['**/node_modules/**']), true)
  const directories = buildDirMatchObjects(buildPathMatchObjects(['android/**', 'ios/**/*']))
  assert.equal(isIgnoredPathWithMatchObjects('android', directories), true)
  assert.equal(isIgnoredPathWithMatchObjects('ios', directories), true)
  assert.equal(isIgnoredPathWithMatchObjects('src', directories), false)
})
