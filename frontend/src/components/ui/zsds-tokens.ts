/**
 * ZABID STUDIO DESIGN SYSTEM (ZSDS) — MASTER DESIGN TOKENS
 * =========================================================================
 * Single source of truth for colors, typography, glassmorphism, buttons, and app themes
 * across all Zabid Studio applications (Clip Assassin, DolaFlow Studio, EchoFlow, etc.).
 *
 * App Accents Palette:
 * - Clip Assassin : Electric Violet  (#A855F7)
 * - DolaFlow Studio: Cyber Cyan      (#06B6D4)
 * - EchoFlow       : Neon Emerald    (#10B981)
 */

export type AppIdentity = 'clip_assassin' | 'dolaflow_studio' | 'echoflow' | 'future_vfx';
export type CategoryKey = 'magic' | 'organize' | 'destructive' | 'output' | 'render' | 'neutral';

// -----------------------------------------------------------------------
// 1. APP-SPECIFIC MASTER THEMES
// -----------------------------------------------------------------------
export const ZSDS_APP_THEMES: Record<AppIdentity, {
  appName: string;
  tagline: string;
  primaryAccent: string;
  glowColor: string;
  accentText: string;
  gradientBg: string;
}> = {
  clip_assassin: {
    appName: 'Clip Assassin',
    tagline: 'DaVinci Resolve Timeline & Ingest Automator',
    primaryAccent: '#A855F7', // Electric Violet
    glowColor: 'rgba(168, 85, 247, 0.4)',
    accentText: '#C4B5FD',
    gradientBg: 'from-purple-900/20 via-brand-bg to-brand-bg',
  },

  dolaflow_studio: {
    appName: 'DolaFlow Studio',
    tagline: 'Fluid Automation & Workflow Engine',
    primaryAccent: '#06B6D4', // Cyber Cyan
    glowColor: 'rgba(6, 182, 212, 0.4)',
    accentText: '#67E8F9',
    gradientBg: 'from-cyan-900/20 via-brand-bg to-brand-bg',
  },

  echoflow: {
    appName: 'EchoFlow',
    tagline: 'Audio Frequency Science & Voice AI Suite',
    primaryAccent: '#10B981', // Neon Emerald
    glowColor: 'rgba(16, 185, 129, 0.4)',
    accentText: '#6EE7B7',
    gradientBg: 'from-emerald-900/20 via-brand-bg to-brand-bg',
  },

  future_vfx: {
    appName: 'Vortex Visuals',
    tagline: 'Next-Gen GFX & Motion Rendering Tool',
    primaryAccent: '#F97316', // Solar Amber
    glowColor: 'rgba(249, 115, 22, 0.4)',
    accentText: '#FDBA74',
    gradientBg: 'from-orange-900/20 via-brand-bg to-brand-bg',
  },
};

// -----------------------------------------------------------------------
// 2. SHARED CANVAS & GLASSMORPHISM SURFACES
// -----------------------------------------------------------------------
export const ZSDS_SURFACES = {
  canvasBg: '#0A0915', // Signature Deep Space Dark
  cardBg: 'rgba(16, 14, 30, 0.6)', // Glassmorphism dark fill
  backdropFilter: 'backdrop-blur-xl',
  borderColor: 'rgba(255, 255, 255, 0.05)',
  borderColorHover: 'rgba(255, 255, 255, 0.12)',
  cardRadius: 'rounded-[24px]',
  cardHoverTranslate: 'hover:-translate-y-1 hover:shadow-2xl',
};

// -----------------------------------------------------------------------
// 3. CATEGORY COLOR SYSTEM
// -----------------------------------------------------------------------
export const CATEGORY_COLORS: Record<CategoryKey, { name: string; solid: string; glow: string; text: string }> = {
  magic: {
    name: 'Magic',
    solid: '#A855F7',
    glow: 'rgba(168, 85, 247, 0.4)',
    text: '#C4B5FD',
  },
  organize: {
    name: 'Organize',
    solid: '#10B981',
    glow: 'rgba(16, 185, 129, 0.4)',
    text: '#6EE7B7',
  },
  destructive: {
    name: 'Destructive',
    solid: '#F43F5E',
    glow: 'rgba(244, 63, 94, 0.4)',
    text: '#FDA4AF',
  },
  output: {
    name: 'Output',
    solid: '#06B6D4',
    glow: 'rgba(6, 182, 212, 0.4)',
    text: '#67E8F9',
  },
  render: {
    name: 'Render',
    solid: '#F97316',
    glow: 'rgba(249, 115, 22, 0.4)',
    text: '#FDBA74',
  },
  neutral: {
    name: 'Neutral',
    solid: '#64748B',
    glow: 'rgba(100, 116, 139, 0.25)',
    text: '#CBD5E1',
  },
};
