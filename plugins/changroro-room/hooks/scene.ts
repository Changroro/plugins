import type { Todo } from '../types'

import { CLAUDE, CODEX, CSS, DESK, DIGITS, MUG } from './parts'

export type View = {
  time: string
  ctx: number | null
  cacheLeftMin: number | null
  cacheTotalMin: number
  project: string
  todos: Todo[]
  isCheering: boolean
}

// Ink & Paper tokens.
const INK = '#000000'
const TEXT = '#1a1a1a'
const PAPER = '#f9f9f9'
const CARD = '#ffffff'
const RECESSED = '#e8e8e8'
const MUTED = '#6a7282'
const DANGER = '#dc2626'
const FONT = 'font-family="Space Grotesk, Work Sans, system-ui, sans-serif"'

// The scene must hold no markup characters from user text, and no entities.
const clean = (s: string): string =>
  s.replace(/&/g, '＆').replace(/</g, '＜').replace(/>/g, '＞').replace(/"/g, '”')

// Fits text into `width` units at `size`: wide (CJK) glyphs count as one em, the rest as 0.6.
export function fit(s: string, width: number, size: number): string {
  let used = 0
  let out = ''
  for (const ch of s) {
    const w = (/[\u0000-ÿ]/.test(ch) ? 0.6 : 1) * size
    if (used + w > width) {
      return `${out}…`
    }
    used += w
    out += ch
  }

  return out
}

function label(x: number, y: number, text: string): string {
  return `<text x="${x}" y="${y}" ${FONT} font-size="6" font-weight="700" letter-spacing="0.6" fill="${MUTED}">${text}</text>`
}

function clock(time: string, x: number, y: number, scale: number): string {
  let cx = 0
  let out = ''
  for (const ch of time) {
    const glyph = DIGITS[ch]
    if (glyph === undefined) {
      continue
    }
    out += `<g transform="translate(${cx} 0)">${glyph}</g>`
    cx += (ch === ':' ? 1 : 3) + 1
  }

  return `<g transform="translate(${x} ${y}) scale(${scale})">${out}</g>`
}

function battery(pct: number | null, x: number, y: number): string {
  const w = 56
  const fill = pct === null ? 0 : Math.round(((w - 6) * Math.min(100, pct)) / 100)
  const color = pct !== null && pct >= 80 ? DANGER : INK
  const shown = pct === null ? '—' : `${pct}%`

  return (
    `<rect x="${x}" y="${y}" width="${w}" height="18" fill="${CARD}" stroke="${INK}" stroke-width="2"/>` +
    `<rect x="${x + w}" y="${y + 5}" width="3" height="8" fill="${INK}"/>` +
    `<rect x="${x + 3}" y="${y + 3}" width="${fill}" height="12" fill="${color}"/>` +
    `<text x="${x + w + 8}" y="${y + 14}" ${FONT} font-size="13" font-weight="700" fill="${TEXT}">${shown}</text>`
  )
}

function mug(leftMin: number | null, totalMin: number, x: number, y: number): string {
  const wisps = leftMin === null || leftMin <= 0 ? 0 : Math.ceil((leftMin / totalMin) * 3)
  let steam = ''
  for (let i = 0; i < wisps; i += 1) {
    steam += `<rect class="st" style="animation-delay:${i * 0.8}s" x="${x + 6 + i * 6}" y="${y - 4}" width="2" height="5" fill="#999999" opacity="0"/>`
  }
  const shown = leftMin === null ? '—' : leftMin <= 0 ? '식었어요' : `${leftMin}분`

  return (
    `<g transform="translate(${x} ${y}) scale(3)">${MUG}</g>` +
    steam +
    `<text x="${x + 36}" y="${y + 16}" ${FONT} font-size="13" font-weight="700" fill="${TEXT}">${shown}</text>`
  )
}

function left(v: View): string {
  const name = fit(clean(v.project || 'no project'), 88, 9)

  return (
    '<svg x="0" y="0" width="28%" height="100%" viewBox="0 0 120 330" preserveAspectRatio="xMinYMid meet" overflow="visible">' +
    label(12, 14, 'NOW') +
    clock(v.time, 12, 20, 4) +
    label(12, 60, 'CONTEXT') +
    battery(v.ctx, 12, 66) +
    label(12, 106, 'CACHE') +
    mug(v.cacheLeftMin, v.cacheTotalMin, 12, 116) +
    `<g transform="translate(12 182)">${DESK}</g>` +
    `<rect x="-400" y="232" width="520" height="2" fill="${INK}"/>` +
    label(12, 252, 'PROJECT') +
    `<rect x="12" y="257" width="96" height="20" fill="${CARD}" stroke="${INK}" stroke-width="2"/>` +
    `<text x="60" y="271" text-anchor="middle" ${FONT} font-size="9" font-weight="700" fill="${TEXT}">${name}</text>` +
    '</svg>'
  )
}

function note(t: Todo, i: number, y: number): string {
  const text = fit(clean(t.text), 70, 8)
  if (t.done) {
    return (
      `<rect x="16" y="${y}" width="88" height="22" fill="${RECESSED}"/>` +
      `<rect x="21" y="${y + 6}" width="10" height="10" fill="${INK}"/>` +
      `<path d="M23 ${y + 11} l2 2 l4 -4" stroke="${CARD}" stroke-width="1.6" fill="none"/>` +
      `<text x="36" y="${y + 14}" ${FONT} font-size="8" fill="${MUTED}" text-decoration="line-through">${text}</text>`
    )
  }

  return (
    `<rect x="16" y="${y}" width="88" height="22" fill="${CARD}" stroke="${INK}" stroke-width="1.5"/>` +
    `<rect x="21.75" y="${y + 6.75}" width="8.5" height="8.5" fill="none" stroke="${INK}" stroke-width="1.5"/>` +
    `<text x="36" y="${y + 14}" ${FONT} font-size="8" font-weight="600" fill="${TEXT}">${text}</text>`
  )
}

function right(v: View): string {
  const done = v.todos.filter(t => t.done).length
  const shown = v.todos.slice(0, 9)
  let body = ''
  shown.forEach((t, i) => {
    body += note(t, i, 46 + i * 27)
  })
  if (v.todos.length > shown.length) {
    body += `<text x="60" y="${46 + shown.length * 27 + 8}" text-anchor="middle" ${FONT} font-size="7" fill="${MUTED}">+${v.todos.length - shown.length}</text>`
  }
  if (v.todos.length === 0) {
    body +=
      `<rect x="20" y="120" width="80" height="40" fill="none" stroke="#999999" stroke-width="1" stroke-dasharray="3 2"/>` +
      `<text x="60" y="137" text-anchor="middle" ${FONT} font-size="7" fill="${MUTED}">오늘 할 일을</text>` +
      `<text x="60" y="148" text-anchor="middle" ${FONT} font-size="7" fill="${MUTED}">말해 주세요</text>`
  }

  return (
    '<svg x="72%" y="0" width="28%" height="100%" viewBox="0 0 120 330" preserveAspectRatio="xMaxYMid meet" overflow="visible">' +
    `<rect x="10" y="10" width="100" height="24" fill="${INK}"/>` +
    `<text x="18" y="26" ${FONT} font-size="10" font-weight="700" fill="${CARD}">오늘 할 일</text>` +
    `<text x="102" y="26" text-anchor="end" ${FONT} font-size="11" font-weight="700" fill="${CARD}">${done}/${v.todos.length}</text>` +
    `<rect x="10" y="38" width="100" height="262" fill="${CARD}" stroke="${INK}" stroke-width="2"/>` +
    body +
    '</svg>'
  )
}

function floor(v: View): string {
  const cheer = v.isCheering ? ' cheer' : ''

  return (
    '<svg x="0" y="86%" width="100%" height="14%" viewBox="0 0 320 40" preserveAspectRatio="xMidYMax meet" overflow="visible">' +
    `<g transform="translate(0 27)"><g class="run${cheer}" transform="translate(150 0)"><g class="hop">${CLAUDE}</g></g></g>` +
    `<g transform="translate(0 20)"><g class="run run2${cheer}" transform="translate(126 0)"><g class="hop">${CODEX}</g></g></g>` +
    '</svg>'
  )
}

export function buildScene(v: View): string {
  return (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" shape-rendering="crispEdges">' +
    `<style>${CSS}</style>` +
    '<defs><pattern id="d" width="32" height="32" patternUnits="userSpaceOnUse">' +
    `<rect x="0" y="0" width="4" height="4" fill="${RECESSED}"/></pattern></defs>` +
    `<rect width="100%" height="100%" fill="${PAPER}"/><rect width="100%" height="100%" fill="url(#d)"/>` +
    left(v) +
    right(v) +
    floor(v) +
    '</svg>'
  )
}
