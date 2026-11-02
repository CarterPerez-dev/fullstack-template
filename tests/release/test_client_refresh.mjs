// ©AngelaMos | 2026
// test_client_refresh.mjs

import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { createRequire } from 'node:module'
import { resolve } from 'node:path'
import { test } from 'node:test'
import { createContext, SourceTextModule, SyntheticModule } from 'node:vm'

const project = resolve(process.argv[2])
const require = createRequire(`${process.env.TEMPLATE_TEST_DEPENDENCIES ?? project}/package.json`)
const ts = require('typescript')
const axios = require('axios')
const { MutationObserver, QueryClient } = require('@tanstack/react-query')

function deferred() {
  let resolvePromise
  const promise = new Promise((resolve) => { resolvePromise = resolve })
  return { promise, resolve: resolvePromise }
}

async function bounded(promise) {
  let timer
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Request did not settle')), 1500)
      }),
    ])
  } finally {
    clearTimeout(timer)
  }
}

async function loadClient() {
  const state = {
    accessToken: 'old-token',
    sessionVersion: 0,
    logouts: 0,
    setAccessToken(token) { state.accessToken = token },
    logout() { state.accessToken = null; state.sessionVersion += 1; state.logouts += 1 },
  }
  const storage = new Map([['refresh-token', 'old-refresh']])
  class ApiError extends Error {}
  const context = createContext({
    __DEV__: true,
    window: { location: { href: '/' } },
  })
  const config = {
    API_ENDPOINTS: {
      AUTH: {
        REFRESH: '/auth/refresh', REFRESH_MOBILE: '/auth/mobile/refresh', LOGIN: '/auth/login',
        LOGOUT: '/auth/logout', LOGOUT_ALL: '/auth/logout-all', CHANGE_PASSWORD: '/auth/change-password',
      },
      USERS: { REGISTER: '/users' },
    },
    HTTP_STATUS: { UNAUTHORIZED: 401, NO_CONTENT: 204 },
    APP_CONFIG: { API_URL: 'https://api.example.com/api' },
    QUERY_KEYS: { AUTH: { ALL: ['auth'], ME: () => ['auth', 'me'] } },
    ROUTES: { LOGIN: '/login' },
  }
  const useAuthStore = Object.assign((selector) => selector ? selector(state) : state, { getState: () => state })
  const imports = {
    axios: { default: axios },
    '@/config': config,
    '@/core/config': config,
    '@/core/lib': { useAuthStore },
    '@/core/storage': {
      SECURE_KEYS: { REFRESH_TOKEN: 'refresh-token' },
      secureStorage: {
        getItem: async (key) => storage.get(key) ?? null,
        setItem: async (key, value) => { storage.set(key, value); return true },
        deleteItem: async (key) => { storage.delete(key); return true },
      },
    },
    './errors': {
      ApiError,
      ApiErrorCode: { AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR' },
      transformAxiosError: (error) => error,
    },
    './go-contract': { decodeGoResponse: (data) => data },
  }
  const source = await readFile(`${project}/src/core/api/api.config.ts`, 'utf8')
  const compiled = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  })
  const module = new SourceTextModule(compiled.outputText, {
    context,
    initializeImportMeta(meta) { meta.env = {} },
  })
  await module.link((specifier) => {
    const values = imports[specifier]
    assert.ok(values, `Unexpected dependency: ${specifier}`)
    return new SyntheticModule(Object.keys(values), function () {
      for (const [key, value] of Object.entries(values)) this.setExport(key, value)
    }, { context })
  })
  await module.evaluate()
  module.namespace.setAccessToken?.('old-token')
  module.namespace.setAuthFailureHandler?.(() => { state.logouts += 1 })
  return {
    client: module.namespace.apiClient,
    state,
    storage,
    currentToken: () => module.namespace.getAccessToken ? module.namespace.getAccessToken() : state.accessToken,
    refresh: module.namespace.refreshAccessToken,
    async loadHooks() {
      const queryClient = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
      const hookSource = await readFile(`${project}/src/api/hooks/useAuth.ts`, 'utf8')
      const hookCompiled = ts.transpileModule(hookSource, {
        compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
      })
      const hookModule = new SourceTextModule(hookCompiled.outputText, { context })
      const hookImports = {
        ...imports,
        '@tanstack/react-query': {
          useMutation: (options) => new MutationObserver(queryClient, options),
          useQueryClient: () => queryClient,
          useQuery: () => { throw new Error('Unexpected query hook') },
        },
        sonner: { toast: { success() {}, error() {} } },
        'expo-router': { router: { replace: (path) => { context.window.location.href = path } } },
        '@/core/api': {
          ...module.namespace,
          QUERY_STRATEGIES: {},
          queryClientPersister: { removeClient: async () => {} },
        },
        '@/api/types': {
          AUTH_ERROR_MESSAGES: {}, AUTH_SUCCESS_MESSAGES: {}, AuthResponseError: class extends Error {},
          isValidLogoutAllResponse: () => true, isValidMobileLoginResponse: () => true,
          isValidTokenWithUserResponse: () => true, isValidUserResponse: () => true,
        },
      }
      await hookModule.link((specifier) => {
        const values = hookImports[specifier]
        assert.ok(values, `Unexpected hook dependency: ${specifier}`)
        return new SyntheticModule(Object.keys(values), function () {
          for (const [key, value] of Object.entries(values)) this.setExport(key, value)
        }, { context })
      })
      await hookModule.evaluate()
      return { hooks: hookModule.namespace, queryClient, location: context.window.location }
    },
    logout() {
      state.logout()
      module.namespace.setAccessToken?.(null)
      storage.delete('refresh-token')
    },
    login(token) {
      state.sessionVersion += 1
      state.setAccessToken(token)
      module.namespace.setAccessToken?.(token)
      storage.set('refresh-token', `${token}-refresh`)
    },
  }
}

function response(config, status = 200, data = {}) {
  return { config, status, statusText: String(status), data, headers: {} }
}

function rejectRequest(config, status) {
  return new axios.AxiosError(`HTTP ${status}`, 'ERR_BAD_REQUEST', config, null, response(config, status))
}

test('late 401 retries the current token while an earlier retry is pending', async () => {
  const { client, state } = await loadClient()
  const refreshStarted = deferred()
  const refreshRelease = deferred()
  const retryStarted = deferred()
  const retryRelease = deferred()
  const lateStarted = deferred()
  const lateRelease = deferred()
  let refreshes = 0
  client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      refreshes += 1
      refreshStarted.resolve()
      await refreshRelease.promise
      return response(config, 200, { access_token: 'new-token', refresh_token: 'new-refresh' })
    }
    if (config.headers.Authorization === 'Bearer old-token') {
      if (config.url === '/late') {
        lateStarted.resolve()
        await lateRelease.promise
      }
      throw rejectRequest(config, 401)
    }
    assert.equal(config.headers.Authorization, 'Bearer new-token')
    if (config.url === '/first') {
      retryStarted.resolve()
      await retryRelease.promise
    }
    return response(config)
  }

  const first = client.get('/first')
  await bounded(refreshStarted.promise)
  const late = client.get('/late')
  await bounded(lateStarted.promise)
  refreshRelease.resolve()
  await bounded(retryStarted.promise)
  lateRelease.resolve()
  try {
    assert.equal((await bounded(late)).status, 200)
  } finally {
    retryRelease.resolve()
    await bounded(first)
  }
  assert.equal(refreshes, 1)
  assert.equal(state.logouts, 0)
})

test('an application failure after successful refresh does not log the user out', async () => {
  const { client, state } = await loadClient()
  client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      return response(config, 200, { access_token: 'new-token', refresh_token: 'new-refresh' })
    }
    throw rejectRequest(config, config.headers.Authorization === 'Bearer old-token' ? 401 : 500)
  }
  await assert.rejects(bounded(client.get('/failure')))
  assert.equal(state.logouts, 0)
})

test('simultaneous expired requests share one refresh and all settle', async () => {
  const { client, state } = await loadClient()
  const gate = deferred()
  const expiredRequests = deferred()
  let expired = 0
  let refreshes = 0
  client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      refreshes += 1
      await gate.promise
      return response(config, 200, { access_token: 'new-token', refresh_token: 'new-refresh' })
    }
    if (config.headers.Authorization === 'Bearer old-token') {
      expired += 1
      if (expired === 10) expiredRequests.resolve()
      throw rejectRequest(config, 401)
    }
    return response(config)
  }
  const requests = Array.from({ length: 10 }, (_, index) => client.get(`/item/${index}`))
  await bounded(expiredRequests.promise)
  gate.resolve()
  const results = await bounded(Promise.all(requests))
  assert.equal(results.length, 10)
  assert.equal(refreshes, 1)
  assert.equal(state.logouts, 0)
})

test('refresh completion after logout cannot restore credentials', async () => {
  const session = await loadClient()
  const started = deferred()
  const release = deferred()
  let resourceCalls = 0
  session.client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      started.resolve()
      await release.promise
      return response(config, 200, { access_token: 'resurrected-token', refresh_token: 'resurrected-refresh' })
    }
    resourceCalls += 1
    if (config.headers.Authorization === 'Bearer old-token') throw rejectRequest(config, 401)
    return response(config)
  }
  const result = Promise.allSettled([session.client.get('/private')])
  await bounded(started.promise)
  session.logout()
  release.resolve()
  assert.equal((await bounded(result))[0].status, 'rejected')
  assert.equal(session.currentToken(), null)
  assert.equal(session.storage.has('refresh-token'), false)
  assert.equal(resourceCalls, 1)
})

test('failure of an old refresh does not log out a replacement session', async () => {
  const session = await loadClient()
  const started = deferred()
  const release = deferred()
  session.client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      started.resolve()
      await release.promise
    }
    throw rejectRequest(config, 401)
  }
  const result = Promise.allSettled([session.client.get('/private')])
  await bounded(started.promise)
  session.login('replacement-token')
  release.resolve()
  assert.equal((await bounded(result))[0].status, 'rejected')
  assert.equal(session.currentToken(), 'replacement-token')
  assert.equal(session.storage.get('refresh-token'), 'replacement-token-refresh')
  assert.equal(session.state.logouts, 0)
})

test('a delayed unauthorized mutation is never retried as another user', async () => {
  const session = await loadClient()
  const started = deferred()
  const release = deferred()
  let calls = 0
  session.client.defaults.adapter = async (config) => {
    calls += 1
    if (calls === 1) {
      started.resolve()
      await release.promise
      throw rejectRequest(config, 401)
    }
    return response(config)
  }
  const result = Promise.allSettled([session.client.post('/private', { change: 'old-user-operation' })])
  await bounded(started.promise)
  session.login('replacement-token')
  release.resolve()
  assert.equal((await bounded(result))[0].status, 'rejected')
  assert.equal(calls, 1)
  assert.equal(session.currentToken(), 'replacement-token')
})

test('a delayed successful response cannot populate a replacement session', async () => {
  const session = await loadClient()
  const started = deferred()
  const release = deferred()
  session.client.defaults.adapter = async (config) => {
    started.resolve()
    await release.promise
    return response(config, 200, { private: 'old-user-data' })
  }
  const result = Promise.allSettled([session.client.get('/private')])
  await bounded(started.promise)
  session.login('replacement-token')
  release.resolve()
  assert.equal((await bounded(result))[0].status, 'rejected')
  assert.equal(session.currentToken(), 'replacement-token')
})

test('a replacement session can refresh while an obsolete refresh is pending', async () => {
  const session = await loadClient()
  const oldStarted = deferred()
  const oldRelease = deferred()
  let refreshes = 0
  session.client.defaults.adapter = async (config) => {
    if (config.url.includes('refresh')) {
      refreshes += 1
      if (refreshes === 1) {
        oldStarted.resolve()
        await oldRelease.promise
        throw rejectRequest(config, 401)
      }
      return response(config, 200, { access_token: 'replacement-refreshed', refresh_token: 'replacement-new-refresh' })
    }
    if (config.headers.Authorization !== 'Bearer replacement-refreshed') throw rejectRequest(config, 401)
    return response(config)
  }
  const obsolete = Promise.allSettled([session.client.get('/obsolete')])
  await bounded(oldStarted.promise)
  session.login('replacement-token')
  try {
    assert.equal((await bounded(session.client.get('/replacement'))).status, 200)
  } finally {
    oldRelease.resolve()
    await bounded(obsolete)
  }
  assert.equal(session.currentToken(), 'replacement-refreshed')
  assert.equal(refreshes, 2)
  assert.equal(session.state.logouts, 0)
})

test('logout callbacks preserve a newer login and its cached user', async () => {
  const session = await loadClient()
  const { hooks, queryClient, location } = await session.loadHooks()
  const started = deferred()
  const release = deferred()
  session.client.defaults.adapter = async (config) => {
    started.resolve()
    await release.promise
    return response(config)
  }
  const result = Promise.allSettled([hooks.useLogout().mutate()])
  await bounded(started.promise)
  session.login('replacement-token')
  queryClient.setQueryData(['auth', 'me'], 'replacement-user')
  release.resolve()
  await bounded(result)
  assert.equal(session.currentToken(), 'replacement-token')
  assert.equal(session.state.logouts, 0)
  assert.equal(queryClient.getQueryData(['auth', 'me']), 'replacement-user')
  assert.equal(location.href, '/')
  queryClient.clear()
})

for (const status of [200, 401]) {
  test(`logout clears the current session after HTTP ${status}`, async () => {
    const session = await loadClient()
    const { hooks, queryClient, location } = await session.loadHooks()
    queryClient.setQueryData(['auth', 'me'], 'original-user')
    session.client.defaults.adapter = async (config) => {
      if (status === 401) throw rejectRequest(config, status)
      return response(config)
    }
    await bounded(Promise.allSettled([hooks.useLogout().mutate()]))
    assert.equal(session.currentToken(), null)
    assert.equal(session.state.logouts, 1)
    assert.equal(queryClient.getQueryData(['auth', 'me']), undefined)
    assert.match(location.href, /login/)
    queryClient.clear()
  })
}
