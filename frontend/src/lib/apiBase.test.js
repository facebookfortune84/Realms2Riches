import { describe, it, expect } from 'vitest'
import { getApiBase, getWsBase } from './apiBase.js'

describe('getApiBase', () => {
  it('returns a non-empty string', () => {
    const base = getApiBase()
    expect(typeof base).toBe('string')
  })

  it('does not end with a trailing slash', () => {
    const base = getApiBase()
    // empty string (dev same-origin) or a URL without trailing slash
    expect(base.endsWith('/')).toBe(false)
  })
})

describe('getWsBase', () => {
  it('returns a string', () => {
    expect(typeof getWsBase()).toBe('string')
  })

  it('does not end with a trailing slash', () => {
    const ws = getWsBase()
    expect(ws.endsWith('/')).toBe(false)
  })
})
