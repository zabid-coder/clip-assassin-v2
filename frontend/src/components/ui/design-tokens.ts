/**
 * Clip Assassin — Design Tokens
 * -----------------------------------------------------------------------
 * Single source of truth for colors, button variants, and card layout.
 * Import this into components instead of hardcoding hex/tailwind classes,
 * so every tool card stays visually consistent as the app grows.
 *
 * Usage:
 *   import { CATEGORY_COLORS, BUTTON_VARIANTS, CARD_STYLES } from './design-tokens';
 */

export type CategoryKey = 'magic' | 'organize' | 'destructive' | 'output' | 'render' | 'neutral';

// -----------------------------------------------------------------------
// 1. CATEGORY COLOR SYSTEM
// -----------------------------------------------------------------------
export const CATEGORY_COLORS: Record<CategoryKey, { name: string; solid: string; glow: string; text: string; examples?: string[] }> = {
  // Purple — AI / Magic / generative tools
  magic: {
    name: 'Magic',
    solid: '#8B5CF6',
    glow: 'rgba(139, 92, 246, 0.4)',
    text: '#C4B5FD',
    examples: ['Timeline Snapshot', 'Batch Clip Renamer', 'Quick Title', 'Quick Adjustment Layer'],
  },

  // Teal/Green — Organize, safe & reversible actions
  organize: {
    name: 'Organize',
    solid: '#10B981',
    glow: 'rgba(16, 185, 129, 0.4)',
    text: '#6EE7B7',
    examples: ['Magic Bin Organizer', 'Multi-Cam Auto Sync', 'Templates / Asset Library'],
  },

  // Red/Pink — Destructive or irreversible actions
  destructive: {
    name: 'Destructive',
    solid: '#F43F5E',
    glow: 'rgba(244, 63, 94, 0.4)',
    text: '#FDA4AF',
    examples: ['Silence Remover', 'Timecode Cutter', 'Clip Picker', 'BadWords Cleaner', 'Quick Cut & Ripple Delete'],
  },

  // Blue/Cyan — Export / Output actions
  output: {
    name: 'Output',
    solid: '#06B6D4',
    glow: 'rgba(6, 182, 212, 0.4)',
    text: '#67E8F9',
    examples: ['Multi-Cam Sync', 'Extract Thumbnails', 'Client Shotlist', 'Watermark Track'],
  },

  // Orange — Warnings / render-queue / merge-in-place actions
  render: {
    name: 'Render',
    solid: '#F97316',
    glow: 'rgba(249, 115, 22, 0.4)',
    text: '#FDBA74',
    examples: ['Multi-Platform Render', 'Merge Timelines', 'Auto YouTube Chapters'],
  },

  // Slate — Secondary/neutral actions
  neutral: {
    name: 'Neutral',
    solid: '#64748B',
    glow: 'rgba(100, 116, 139, 0.25)',
    text: '#CBD5E1',
    examples: ['Extract Flagged Clips', 'Extract Marked Clips', 'secondary/bulk actions'],
  },
};

// -----------------------------------------------------------------------
// 2. BUTTON VARIANTS
// -----------------------------------------------------------------------
export const BUTTON_VARIANTS = {
  primary: (categoryKey: CategoryKey) => {
    const c = CATEGORY_COLORS[categoryKey];
    return {
      className: 'font-semibold rounded-xl px-6 py-3 transition-all duration-150 hover:brightness-110 active:scale-[0.98] flex items-center justify-center gap-2',
      style: {
        backgroundColor: c.solid,
        boxShadow: `0 0 24px ${c.glow}`,
        color: '#0A0F0D', // dark text on bright fill for contrast
      },
    };
  },

  secondary: {
    className: 'font-semibold rounded-xl px-6 py-3 transition-all duration-150 hover:brightness-125 active:scale-[0.98] border border-white/10 flex items-center justify-center gap-2',
    style: {
      backgroundColor: '#334155', // slate-700, flat, no glow
      color: '#E2E8F0',
    },
  },
};

// -----------------------------------------------------------------------
// 3. CARD LAYOUT
// -----------------------------------------------------------------------
export const CARD_STYLES = {
  base: 'rounded-[24px] p-6 bg-[#0F1712] border border-white/5 transition-all duration-300 ease-out hover:border-white/10 hover:bg-black/40 hover:-translate-y-1 hover:shadow-2xl flex flex-col relative group',
  minHeight: 'min-h-[180px]',
  gap: 'gap-6',
  iconWrapper: (categoryKey: CategoryKey) => ({
    className: 'w-10 h-10 rounded-lg flex items-center justify-center shrink-0',
    style: { backgroundColor: `${CATEGORY_COLORS[categoryKey].solid}22`, color: CATEGORY_COLORS[categoryKey].solid }, 
  }),
};

// -----------------------------------------------------------------------
// 4. INPUT FIELDS
// -----------------------------------------------------------------------
export const INPUT_STYLES = {
  base: 'w-full rounded-lg px-4 py-3 bg-[#1A241E] border border-white/10 placeholder:text-gray-500 text-gray-100 transition-colors duration-150 focus:outline-none focus:border-opacity-100 focus:ring-1',
  focusRing: (categoryKey: CategoryKey) => ({
    '--tw-ring-color': CATEGORY_COLORS[categoryKey].solid,
  } as React.CSSProperties),
};

// -----------------------------------------------------------------------
// 5. SPACING SCALE
// -----------------------------------------------------------------------
export const SPACING = {
  cardInternalStack: 'space-y-4',
  inlineControlsGap: 'gap-3',
  sectionGap: 'space-y-6',
};
