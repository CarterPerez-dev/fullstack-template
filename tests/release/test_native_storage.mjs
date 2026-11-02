// ©AngelaMos | 2026
// test_native_storage.mjs

import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { resolve } from 'node:path'
import { test } from 'node:test'
import { createContext, SourceTextModule, SyntheticModule } from 'node:vm'

const project = resolve(process.argv[2])
const require = createRequire(`${project}/package.json`)
const ts = require('typescript')

function deferred() {
  let resolvePromise
  const promise = new Promise((resolve) => { resolvePromise = resolve })
  return { promise, resolve: resolvePromise }
}

async function loadStorage(adapter) {
  const context = createContext({})
  const source = await readFile(`${project}/src/core/storage/secure.storage.ts`, 'utf8')
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  })
  const module = new SourceTextModule(compiled.outputText, { context })
  const imports = {
    'expo-secure-store': { ...adapter, WHEN_UNLOCKED_THIS_DEVICE_ONLY: 'device-only' },
    '@/core/config': { APP_CONFIG: { KEYCHAIN_SERVICE: 'test-keychain' } },
  }
  await module.link((specifier) => {
    const values = imports[specifier]
    assert.ok(values, `Unexpected storage dependency: ${specifier}`)
    return new SyntheticModule(Object.keys(values), function () {
      for (const [key, value] of Object.entries(values)) this.setExport(key, value)
    }, { context })
  })
  await module.evaluate()
  return module.namespace.secureStorage
}

test('logout deletion finishes after an earlier slow token write', { timeout: 1500 }, async () => {
  let saved = 'old-refresh'
  const started = deferred()
  const release = deferred()
  const storage = await loadStorage({
    getItemAsync: async () => saved,
    setItemAsync: async (_key, value) => { started.resolve(); await release.promise; saved = value },
    deleteItemAsync: async () => { saved = null },
  })
  const writing = storage.setItem('refresh_token', 'rotated-refresh')
  await started.promise
  const deleting = storage.deleteItem('refresh_token')
  release.resolve()
  assert.deepEqual(await Promise.all([writing, deleting]), [true, true])
  assert.equal(await storage.getItem('refresh_token'), null)
})

test('a newer login remains saved after an earlier slow write', { timeout: 1500 }, async () => {
  let saved = null
  const started = deferred()
  const release = deferred()
  const storage = await loadStorage({
    getItemAsync: async () => saved,
    setItemAsync: async (_key, value) => {
      if (value === 'old-refresh') { started.resolve(); await release.promise }
      saved = value
    },
    deleteItemAsync: async () => { saved = null },
  })
  const oldWrite = storage.setItem('refresh_token', 'old-refresh')
  await started.promise
  const newWrite = storage.setItem('refresh_token', 'new-login-refresh')
  release.resolve()
  assert.deepEqual(await Promise.all([oldWrite, newWrite]), [true, true])
  assert.equal(await storage.getItem('refresh_token'), 'new-login-refresh')
})

test('a failed storage write does not prevent later deletion', { timeout: 1500 }, async () => {
  let saved = 'old-refresh'
  const storage = await loadStorage({
    getItemAsync: async () => saved,
    setItemAsync: async () => { throw new Error('keychain unavailable') },
    deleteItemAsync: async () => { saved = null },
  })
  assert.equal(await storage.setItem('refresh_token', 'new-refresh'), false)
  assert.equal(await storage.deleteItem('refresh_token'), true)
  assert.equal(await storage.getItem('refresh_token'), null)
})
