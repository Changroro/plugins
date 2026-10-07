import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Entry } from '../types'
import { candidates, isShelved, pick, refsOf, resolve, slug, visible } from './paths'
import type { Os } from './platform'
import { baseName, openCommand, tmpRoot } from './platform'

const pasted = atom({ plugin: 'file-dock', key: 'pasted' } as const, [])
const draft = atom({ plugin: 'file-dock', key: 'draft' } as const, [])
const sent = atom({ plugin: 'file-dock', key: 'sent' } as const, [])
const mine = atom({ plugin: 'file-dock', key: 'mine' } as const, [])
const claude = atom({ plugin: 'file-dock', key: 'claude' } as const, [])
const SHOWN = 5
const written = new Set<string>()
const known = new Map<string, { entry: Entry | null; at: number }>()
let os: Os = 'linux'
let home = ''

async function osOf($: EngineInterface): Promise<Os> {
  if ((await $.env.get('OS')) === 'Windows_NT') return 'windows'
  return (await $.process.run(['uname', '-s'])).stdout.trim() === 'Darwin' ? 'mac' : 'linux'
}

async function lookup($: EngineInterface, raw: string, cwd: string) {
  const path = resolve(raw, cwd, home)
  const now = await $.clock.now()
  const cached = known.get(path)
  if (cached && (cached.entry || now - cached.at < 5_000)) return cached.entry
  const stat = (await $.fs.exists(path)) ? await $.fs.stat(path) : undefined
  const entry = stat?.kind === 'dir' ? { path, isDir: true } : stat?.kind === 'file' ? { path, isDir: false } : null
  known.set(path, { entry, at: now })
  return entry
}

async function existing($: EngineInterface, text: string) {
  const cwd = await $.session.cwd()
  const found: Entry[] = []
  for (const raw of candidates(text)) {
    const entry = await lookup($, raw, cwd)
    if (entry && (entry.isDir || isShelved(entry.path)) && !found.some(f => f.path === entry.path)) found.push(entry)
  }
  return found
}

const labelOf = (entry: Entry) => (entry.isDir ? `${baseName(entry.path.replace(/[\\/]$/, ''))}/` : baseName(entry.path))

async function findImages($: EngineInterface, base: string, cwd: string, sessionId: string) {
  const guess = `${base}/${slug(cwd)}/${sessionId}/images`
  if (await $.fs.exists(guess)) return guess
  if (!(await $.fs.exists(base))) return undefined
  for (const project of await $.fs.list(base)) {
    const dir = `${base}/${project.name}/${sessionId}/images`
    if (project.kind === 'dir' && (await $.fs.exists(dir))) return dir
  }
  return undefined
}

async function open($: EngineInterface, path: string) {
  const ran = await $.process.run(openCommand(os, path), { timeoutMs: 10_000 })
  $.ui.toast(ran.exitCode === 0 ? `📂 ${baseName(path)} 열었습니다` : `file-dock: 열지 못했습니다 (${ran.stderr.trim() || `exit ${ran.exitCode}`})`)
}

export const register: Register = on => {
  let polling = false

  on('session.start', async ($, e, next) => {
    if (polling) return next(e)
    polling = true
    os = await osOf($)
    home = (await $.env.get('HOME')) ?? (await $.env.get('USERPROFILE')) ?? ''
    const env = {
      CLAUDE_CODE_TMPDIR: await $.env.get('CLAUDE_CODE_TMPDIR'),
      TMPDIR: await $.env.get('TMPDIR'),
      TMP: await $.env.get('TMP'),
      TEMP: await $.env.get('TEMP'),
      SystemRoot: await $.env.get('SystemRoot'),
      windir: await $.env.get('windir'),
    }
    const uid = os === 'windows' ? '0' : (await $.process.run(['id', '-u'])).stdout.trim()
    const base = `${tmpRoot(os, env).replace(/\\/g, '/')}/claude-${uid}`
    const cwd = e.cwd
    const found = new Map<string, string>()
    let seen = ''
    $.clock.every(2_000, async () => {
      const sessionId = await $.session.id()
      const dir = found.get(sessionId) ?? (await findImages($, base, cwd, sessionId))
      if (dir) found.set(sessionId, dir)
      const shots = dir ? pick(await $.fs.list(dir), dir) : []
      const refs = refsOf((await $.prompt.read()).text)
      const key = `${shots.map(s => `${s.path}:${s.mtimeMs}`).join('|')}#${refs.join(',')}`
      if (key === seen) return
      seen = key
      await update($, pasted, () => shots)
      await update($, draft, () => refs)
    })
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    const typed = await read($, draft)
    const refs = refsOf(e.text)
    const result = await next(e)
    await update($, sent, list => [...new Set([...list, ...(refs.length ? refs : typed)])])
    await update($, draft, () => [])
    const paths = await existing($, e.text)
    if (paths.length) await update($, mine, list => [...list.filter(old => !paths.some(p => p.path === old.path)), ...paths].slice(-20))
    return result
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    const path = (e as unknown as { file_path?: unknown }).file_path
    if (!e.agentId && (e.tool === 'Write' || e.tool === 'Edit') && typeof path === 'string' && isShelved(path) && ran.deny === undefined && !ran.isError) written.add(path)
    return ran
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId || e.reason !== 'answer') return result
    const fromAnswer = await existing($, [e.answer, ...written].join('\n'))
    written.clear()
    await update($, claude, () => fromAnswer.slice(0, SHOWN))
    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const images = visible(await read($, pasted), await read($, draft), await read($, sent)).slice(-SHOWN)
    const paths = (await read($, mine)).slice(-SHOWN)
    const given = (await read($, claude)).filter(entry => !paths.some(p => p.path === entry.path))
    if (e.props.hasSurvey || (!images.length && !paths.length && !given.length)) return next(e)
    const { Box, Text, Button } = $.ui.resolve(e)
    const below = await next(e)
    return (
      <Box flexDirection="column">
        {below}
        <Box flexDirection="row" flexWrap="wrap" paddingX={1} columnGap={1}>
          {(images.length > 0 || paths.length > 0) && <Box flexShrink={0}><Text dimColor>나</Text></Box>}
          {images.map(shot => (
            <Button key={`image-${shot.number}`} label={`Image #${shot.number}`} onPress={() => open($, shot.path)} />
          ))}
          {paths.map((entry, index) => (
            <Button key={`mine-${index}`} label={labelOf(entry)} onPress={() => open($, entry.path)} />
          ))}
          {given.length > 0 && <Box flexShrink={0}><Text dimColor>Claude</Text></Box>}
          {given.map((entry, index) => (
            <Button key={`claude-${index}`} label={labelOf(entry)} onPress={() => open($, entry.path)} />
          ))}
        </Box>
      </Box>
    )
  })
}
