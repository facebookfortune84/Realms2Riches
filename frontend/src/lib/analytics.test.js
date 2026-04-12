import { describe, it, expect } from 'vitest'
import { trackEvent } from './analytics.js'

describe('trackEvent', () => {
  it('is a function', () => {
    expect(typeof trackEvent).toBe('function')
  })

  it('returns a promise (does not throw synchronously)', async () => {
    // ANALYTICS_ENABLED is false in test env (no VITE_ANALYTICS_ENABLED=true set)
    // so trackEvent resolves immediately without network calls
    const result = trackEvent('test_event', { product_id: 'prod_test' })
    expect(result).toBeInstanceOf(Promise)
    await expect(result).resolves.toBeUndefined()
  })

  it('accepts an event name with no payload', async () => {
    await expect(trackEvent('smoke_test')).resolves.not.toThrow()
  })
})
