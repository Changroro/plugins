import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Entry, Item } from '../types'
import { addMemo, remember, when } from './history'
import { candidates, isShelved, pick, refsOf, resolve, slug, visible } from './paths'
import type { Os } from './platform'
import { baseName, openCommand, tmpRoot } from './platform'

const pasted = atom({ plugin: 'file-dock', key: 'pasted' } as const, [])
const draft = atom({ plugin: 'file-dock', key: 'draft' } as const, [])
const sent = atom({ plugin: 'file-dock', key: 'sent' } as const, [])
const mine = atom({ plugin: 'file-dock', key: 'mine' } as const, [])
const claude = atom({ plugin: 'file-dock', key: 'claude' } as const, [])
const revision = atom({ plugin: 'file-dock', key: 'revision' } as const, 0)
const writing = atom({ plugin: 'file-dock', key: 'writing' } as const, '')
const PAGE = 100
const page = atom({ plugin: 'file-dock', key: 'page' } as const, PAGE)
const PANE = 'file-dock'
const SHOWN = 5
// 사람이 보낸 프롬프트가 아닌 것: 이것들로는 '나' 버튼을 바꾸지 않음
const AUTOMATED = new Set(['task-notification', 'scheduled-trigger', 'peer', 'peer-send-message', 'projects-relay', 'coordinator', 'observer', 'observer-activity', 'auto-continuation', 'plugin'])
const written = new Set<string>()
const kept = new Set<string>()
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

const historyOf = async ($: EngineInterface) => ((await $.store.get('history')) ?? []) as Item[]

// shortcut: 세션마다 읽고 바로 쓰므로 같은 순간의 동시 기록은 한쪽이 질 수 있음, 잦아지면 항목별 키로 나눔
async function change($: EngineInterface, edit: (list: Item[]) => Item[]) {
  try {
    await $.store.set('history', edit(await historyOf($)))
  } catch (error) {
    $.ui.toast(`file-dock: 기록을 저장하지 못했습니다 (${error instanceof Error ? error.message : error})`)
    return false
  }
  await update($, revision, count => count + 1)
  return true
}

async function record($: EngineInterface, entries: Entry[]) {
  if (!entries.length) return
  const at = await $.clock.now()
  const project = baseName((await $.session.cwd()).replace(/[\\/]$/, ''))
  await change($, list => remember(list, entries, project, at))
}

async function toggleMemo($: EngineInterface, path: string) {
  const opening = (await read($, writing)) !== path
  await update($, writing, () => (opening ? path : ''))
  // 포커스가 안 옮겨져도 입력칸은 Tab으로 닿으므로 메모 흐름을 막지 않음
  if (opening) await $.ui.focus({ requestId: PANE, key: 'memo-input' }).catch(() => undefined)
}

async function saveMemo($: EngineInterface, path: string, text: string) {
  if (!text.trim()) return
  const at = await $.clock.now()
  if (await change($, list => addMemo(list, path, text.trim(), at))) await update($, writing, () => '')
}

export const register: Register = on => {
  let polling = false

  on('session.start', async ($, e, next) => {
    if (polling) return next(e)
    polling = true
    await $.command.register({ name: 'file-dock', description: '모든 세션의 파일·폴더 기록과 메모 패널을 엽니다' })
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
      const fresh = visible(shots, [], await read($, sent)).filter(shot => !kept.has(shot.path))
      fresh.forEach(shot => kept.add(shot.path))
      await record($, fresh.map(shot => ({ path: shot.path, isDir: false })))
    })
    return next(e)
  })

  on('command.run', { command: 'file-dock' }, async $ => {
    await update($, revision, count => count + 1)
    const opened = await $.ui.open({ id: PANE, title: '기록', focus: true })
    return { text: opened.isPlaced ? 'file-dock 기록 패널을 열었습니다.' : `file-dock 패널을 열지 못했습니다: ${opened.reason}` }
  })

  on('prompt.submit', async ($, e, next) => {
    if (AUTOMATED.has(e.origin?.kind) || e.text.startsWith('/')) return next(e)
    const typed = await read($, draft)
    const refs = refsOf(e.text)
    const result = await next(e)
    await update($, sent, () => (refs.length ? refs : typed))
    await update($, draft, () => [])
    const paths = await existing($, e.text)
    await update($, mine, () => paths)
    await record($, paths)
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
    await record($, fromAnswer)
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
  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input } = $.ui.resolve(e)
    await read($, revision)
    const list = [...(await historyOf($))].reverse()
    const editing = await read($, writing)
    const limit = await read($, page)
    return (
      <Box flexDirection="column" rowGap={1}>
        {list.length === 0 && <Text dimColor>아직 기록이 없습니다.</Text>}
        {list.slice(0, limit).map(item => (
          <Box flexDirection="column">
            <Text dimColor>{`${when(item.at)} · ${item.project}`}</Text>
            <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
              <Button key={`open:${item.path}`} label={labelOf(item)} onPress={() => open($, item.path)} />
              <Button key={`memo:${item.path}`} label={item.memos.length ? `메모 ${item.memos.length}` : '메모'} onPress={() => toggleMemo($, item.path)} />
            </Box>
            {item.memos.map(memo => <Text>{`  ${when(memo.at)} ${memo.text}`}</Text>)}
            {editing === item.path && <Input key="memo-input" rows={2} autoFocus placeholder="메모를 쓰고 Enter" submitLabel="저장" onSubmit={text => saveMemo($, item.path, text)} />}
          </Box>
        ))}
        {list.length > limit && <Button key="more" label={`이전 기록 더 보기 (${list.length - limit}개 남음)`} onPress={() => update($, page, count => count + PAGE)} />}
      </Box>
    )
  })
}
