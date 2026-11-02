/**
 * @AngelaMos | 2026
 * tokens.ts
 */

import { createTokens } from 'tamagui'
import { APP_CONFIG } from '@/core/config'

export const tokens = createTokens({
  // Neutral baseline: flat grayscale, no design identity. Keys are stable --
  // redefine these values when you build the app's real look.
  color: {
    bgDefault: '#111111',
    bgAlternative: '#0e0e0e',
    bgPage: '#161616',
    bgCard: '#131313',

    bgShellBase: '#151515',
    bgShellDot: '#1c1c1c',

    bgContentBase: '#0f0f0f',
    bgContentDot: '#161616',

    bgSurface75: '#161616',
    bgSurface100: '#1a1a1a',
    bgSurface200: '#222222',
    bgSurface300: '#2a2a2a',

    bgControl: '#1a1a1a',
    bgSelection: '#303030',
    bgOverlay: '#222222',
    bgOverlayHover: '#2c2c2c',

    borderMuted: '#222222',
    borderDefault: '#2c2c2c',
    borderStrong: '#363636',
    borderStronger: '#444444',
    borderControl: '#383838',

    textDefault: '#f5f5f5',
    textLight: '#b0b0b0',
    textLighter: '#888888',
    textMuted: '#4d4d4d',

    white: '#ffffff',
    black: '#000000',

    accent: APP_CONFIG.ACCENT_COLOR,

    errorDefault: '#dc2626',
    errorLight: '#ef4444',

    transparent: 'transparent',
  },

  space: {
    0: 0,
    0.5: 2,
    1: 4,
    1.5: 6,
    2: 8,
    2.5: 10,
    3: 12,
    3.5: 14,
    4: 16,
    5: 20,
    6: 24,
    7: 28,
    8: 32,
    9: 36,
    10: 40,
    12: 48,
    14: 56,
    16: 64,
    20: 80,
    24: 96,
    true: 16,
  },

  size: {
    0: 0,
    0.5: 2,
    1: 4,
    1.5: 6,
    2: 8,
    2.5: 10,
    3: 12,
    3.5: 14,
    4: 16,
    5: 20,
    6: 24,
    7: 28,
    8: 32,
    9: 36,
    10: 40,
    11: 44,
    12: 48,
    14: 56,
    16: 64,
    20: 80,
    true: 16,
  },

  radius: {
    0: 0,
    1: 2,
    2: 4,
    3: 6,
    4: 8,
    5: 10,
    6: 12,
    true: 6,
  },

  zIndex: {
    0: 0,
    1: 100,
    2: 200,
    3: 300,
    4: 400,
    5: 500,
  },
})

export const colors = tokens.color
