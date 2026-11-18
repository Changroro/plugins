import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, ThemeSetArgs } from 'claude-code'

import type { Todo } from '../types'

import { makeColors } from './make-colors.js'
import { buildScene } from './scene'

const P = 'changroro-room'
const TOOL = 'todo'

const minute = atom({ plugin: 'changroro-room', key: 'minute' } as const, 0)
const ctx = atom({ plugin: 'changroro-room', key: 'ctx' } as const, null)
const cacheAt = atom({ plugin: 'changroro-room', key: 'cacheAt' } as const, null)
const project = atom({ plugin: 'changroro-room', key: 'project' } as const, '')
const todos = atom({ plugin: 'changroro-room', key: 'todos' } as const, [])
const cheerAt = atom({ plugin: 'changroro-room', key: 'cheerAt' } as const, 0)

// ponytail: assumes the 1h prompt cache; read a step's cacheTtl if 5m sessions matter.
const CACHE_MS = 3_600_000
// ponytail: fixed KST; switch to Intl time zones if this is used outside Korea.
const KST_MS = 9 * 3_600_000
const CHEER_MS = 8_000

const kst = (now: number): string => new Date(now + KST_MS).toISOString()

// Ink & Paper design-system tokens (claude.ai design system "Ink & Paper").
const { theme, problems } = makeColors({
  label: 'Ink & Paper',
  id: 'ink-and-paper',
  only: 'light',
  roles: { accent: '#2563eb', danger: '#dc2626', success: '#16a34a', warning: '#d97706', pro: '#9333ea' },
  light: {
    gray: {
      anchors: {
        'surface-0': '#f9f9f9',
        'surface-1': '#ffffff',
        'surface-2': '#ffffff',
        'text-primary': '#1a1a1a',
        'text-secondary': '#4a5565',
        'text-muted': '#6a7282',
      },
    },
  },
})

const LOOK: ThemeSetArgs = {
  colors: theme,
  backdrop: { scene: P, glass: { blur: 4, tint: '#ffffff', opacity: 0.35 } },
}

type Saved = { day: string; items: Todo[] }

async function loadTodos($: EngineInterface, now: number): Promise<Todo[]> {
  const saved = (await $.store.get('todos')) as Saved | undefined
  return saved !== undefined && saved.day === kst(now).slice(0, 10) ? saved.items : []
}

async function saveTodos($: EngineInterface, items: Todo[]): Promise<void> {
  await $.store.set('todos', { day: kst(await $.clock.now()).slice(0, 10), items } satisfies Saved)
  await update($, todos, () => items)
}

const TOOL_DESCRIPTION = `Today's to-do list, drawn on the board at the right of the person's desktop app.
Use it when the person tells you what they plan to do today, or says one of those tasks is done.
actions: "add" (items: task texts, kept exactly as the person wrote them), "done" / "undo" (indexes: 1-based),
"remove" (indexes), "clear", "list". The list resets each day (KST). Answer with the current list.`

const TOOL_SCHEMA = {
  type: 'object',
  properties: {
    action: { type: 'string', enum: ['add', 'done', 'undo', 'remove', 'clear', 'list'] },
    items: { type: 'array', items: { type: 'string' } },
    indexes: { type: 'array', items: { type: 'integer', minimum: 1 } },
  },
  required: ['action'],
}

type TodoInput = { action?: string; items?: unknown; indexes?: unknown }

export function applyTodo(list: Todo[], input: TodoInput): Todo[] | string {
  const items = Array.isArray(input.items) ? input.items.filter((s): s is string => typeof s === 'string') : []
  const idx = Array.isArray(input.indexes)
    ? input.indexes.filter((n): n is number => Number.isInteger(n) && n >= 1 && n <= list.length).map(n => n - 1)
    : []
  switch (input.action) {
    case 'add':
      return items.length === 0 ? 'add needs items' : [...list, ...items.map(text => ({ text: text.trim(), done: false }))]
    case 'done':
    case 'undo':
      return idx.length === 0 ? `${input.action} needs indexes between 1 and ${list.length}` : list.map((t, i) => (idx.includes(i) ? { ...t, done: input.action === 'done' } : t))
    case 'remove':
      return idx.length === 0 ? `remove needs indexes between 1 and ${list.length}` : list.filter((_, i) => !idx.includes(i))
    case 'clear':
      return []
    case 'list':
      return list
    default:
      return `unknown action: ${String(input.action)}`
  }
}

const describe = (list: Todo[]): string =>
  list.length === 0 ? 'Today: (empty)' : list.map((t, i) => `${i + 1}. [${t.done ? 'x' : ' '}] ${t.text}`).join('\n')

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const unpainted = problems.find(line => line.startsWith("Desktop won't paint"))
    if (unpainted !== undefined) {
      $.ui.toast(unpainted)
    }
    const set = await $.theme.set(LOOK)
    // A client that attaches later still draws the theme, so the reason is only shown until then.
    $.ui.status(set.isDrawn ? undefined : set.reason)

    const now = await $.clock.now()
    const cwd = await $.session.cwd()
    const repo = await $.session.repo()
    const usage = await $.session.usage()
    await update($, project, () => repo?.name ?? cwd.split('/').filter(Boolean).pop() ?? '')
    await update($, ctx, () => usage.context.percent ?? null)
    const items = await loadTodos($, now)
    await update($, todos, () => items)
    await update($, minute, () => Math.floor(now / 60_000))
    $.clock.every(15_000, async () => {
      const m = Math.floor((await $.clock.now()) / 60_000)
      if (m !== (await read($, minute))) {
        await update($, minute, () => m)
        if (m % 60 === 0) {
          const fresh = await loadTodos($, m * 60_000)
          await update($, todos, () => fresh)
        }
      }
    })

    await $.tool.register({ name: TOOL, description: TOOL_DESCRIPTION, inputSchema: TOOL_SCHEMA, isDeferred: false })

    return next(e)
  })

  // Answered at tool.call, ahead of the permission check: the list is the mod's own data.
  on('tool.call', { tool: /^mcp__changroro-room__todo$/ }, async ($, e) => {
    try {
      const list = await loadTodos($, await $.clock.now())
      const changed = applyTodo(list, e as unknown as TodoInput)
      if (typeof changed === 'string') {
        return { result: `Error: ${changed}\n${describe(list)}` }
      }
      await saveTodos($, changed)

      return { result: describe(changed) }
    } catch (err) {
      return { result: `Error: the to-do list could not be saved (${String(err)})` }
    }
  })

  on('session.measure', async ($, e, next) => {
    await update($, ctx, () => e.context.percent ?? null)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    // ponytail: the cache clock starts at turn end, a few seconds after the last request.
    const doneAt = await $.clock.now()
    await update($, cheerAt, () => doneAt)
    await update($, cacheAt, () => doneAt)

    return next(e)
  })

  on('ui.render', { component: 'Backdrop' }, async ($, e, next) => {
    if (e.props.plugin !== P || e.props.scene !== P) {
      return next(e)
    }
    if (e.surface !== 'desktop' && e.surface !== 'mobile') {
      return next(e)
    }
    const m = await read($, minute)
    const now = Math.max(m * 60_000, await $.clock.now())
    const at = await read($, cacheAt)
    const left = at === null ? null : Math.max(0, Math.ceil((at + CACHE_MS - now) / 60_000))
    const svg = buildScene({
      time: kst(now).slice(11, 16),
      ctx: await read($, ctx),
      cacheLeftMin: left,
      cacheTotalMin: CACHE_MS / 60_000,
      project: await read($, project),
      todos: await read($, todos),
      isCheering: now - (await read($, cheerAt)) < CHEER_MS,
    })
    $.ui.status(undefined)
    const { Svg } = $.ui.resolve(e)

    return <Svg source={svg} alt="Desk scene: clock, context battery, cache mug, project plate and today's to-do board" isInteractive />
  })
}
