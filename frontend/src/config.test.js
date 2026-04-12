import { describe, it, expect } from 'vitest'
import config from './config.js'

describe('frontend config', () => {
  it('exposes string defaults', () => {
    expect(typeof config.API_URL).toBe('string')
    expect(config.API_URL.length).toBeGreaterThan(0)
    expect(typeof config.VERSION).toBe('string')
  })
})
