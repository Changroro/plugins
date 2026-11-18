import { expect, test } from 'claude-code/testing'

test('the backdrop draws on desktop', async ($, on) => {
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('clock.now', () => ({ value: Date.UTC(2026, 10, 19, 7, 28) }))
  on('clock.every', () => ({ value: undefined }))
  on('theme.set', () => ({ value: { isDrawn: true, requestId: 'backdrop' } }))
  on('tool.register', () => ({ value: { tool: 'mcp__changroro-room__todo' } }))
  await $.session.start({ cwd: '/x/couple-app', surface: 'desktop', isInteractive: true })
  const ui = await $.ui.mount({
    plugin: 'changroro-room',
    surface: 'desktop',
    component: 'Backdrop',
    requestId: 'backdrop',
    props: { scene: 'changroro-room', plugin: 'changroro-room', glass: { blur: 12, opacity: 0.85 } },
  })
  const svg = await ui.find({ type: 'Svg' })
  expect(svg !== undefined && svg !== null).toBe(true)
  await ui.unmount()
})
