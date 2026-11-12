import { expect, mock, test } from 'claude-code/testing'

import { candidates, isLink, isShelved, linkLabel, links, pick, refsOf, resolve, slug, unsuffixed, visible } from '../hooks/paths'
import { addMemo, forget, remember, when } from '../hooks/history'
import { baseName, openCommand, tmpRoot } from '../hooks/platform'

const file = (name: string, mtimeMs: number) => ({ name, kind: 'file' as const, size: 1, mtimeMs })
const dir = (name: string) => ({ name, kind: 'dir' as const, size: 0, mtimeMs: 0 })
const ok = (stdout = '') => ({ value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } })

test('경로 후보: 상대·절대·~·Windows·file://, 폴더 포함, 웹 주소와 숫자는 제외', () => {
  const text = [
    '보고서 "/home/u/문서/보고서 최종.hwp" 와 ~/Downloads/a.pdf, 차트 `out/chart.png`',
    'file:///home/u/%EB%AC%B8%EC%84%9C/%EA%B3%84%ED%9A%8D%EC%84%9C.docx  폴더 ./plugins/ 와 src/app.ts:12',
    'Windows C:\\Users\\u\\b.xlsx, 웹 https://x.com/c.pdf, 버전 1.5 와 v2',
  ].join('\n')
  const found = candidates(text)
  expect(found).toEqual(expect.arrayContaining([
    '/home/u/문서/보고서 최종.hwp', '~/Downloads/a.pdf', 'out/chart.png', '/home/u/문서/계획서.docx', './plugins/', 'src/app.ts', 'C:\\Users\\u\\b.xlsx',
  ]))
  expect(found.some(raw => raw.includes('x.com') || raw === '1.5' || raw === 'v2')).toBe(false)
  expect(candidates('파일 `a/b.ts:41:7` 와 "c/d.md:3"')).toEqual(expect.arrayContaining(['a/b.ts', 'c/d.md']))
  expect(resolve('./plugins/', '/w', '/home/u')).toBe('/w/plugins/')
  expect(resolve('~/a.pdf', '/w', '/home/u')).toBe('/home/u/a.pdf')
  expect(isShelved('src/app.ts')).toBe(false)
  expect(baseName('C:\\Users\\u\\b.xlsx')).toBe('b.xlsx')
})

test('경로 후보: 문장 끝 마침표는 경로에 넣지 않음', () => {
  expect(candidates('로그는 /tmp/out.log.\n보고서는 /tmp/a.pdf. 끝')).toEqual(expect.arrayContaining(['/tmp/out.log', '/tmp/a.pdf']))
  expect(candidates('위 폴더 ../ 와 ../..')).toEqual(expect.arrayContaining(['../', '../..']))
})

test('기록: 같은 경로는 메모를 지키며 최신으로 옮김, 폴더 끝 슬래시는 같은 경로', () => {
  const first = remember([], [{ path: '/w/a.pdf', isDir: false }, { path: '/w/d/', isDir: true }], 1)
  expect(first.map(item => item.path)).toEqual(['/w/a.pdf', '/w/d'])
  const noted = addMemo(addMemo(first, '/w/a.pdf', '첫째', 2), '/w/a.pdf', '둘째', 3)
  const again = remember(noted, [{ path: '/w/a.pdf', isDir: false }, { path: '/w/d', isDir: true }, { path: '/w/d/', isDir: true }], 4)
  expect(again.map(item => item.path)).toEqual(['/w/a.pdf', '/w/d'])
  expect(again[0]).toMatchObject({ at: 4 })
  expect(again[0].memos.map(memo => memo.text)).toEqual(['첫째', '둘째'])
  expect(when(new Date(2026, 10, 4, 9, 5).getTime())).toBe('11-04 09:05')
})

test('링크: 문장 부호와 마크다운을 빼고 http(s)만 찾음', () => {
  const text = '문서는 https://x.com/a?b=1&c=2. 와 [링크](http://y.io/p) 그리고 **https://z.dev/**, `https://w.app/q`에 있고 ftp://no.io 는 제외, https://x.com/a?b=1&c=2 중복'
  expect(links(text)).toEqual(['https://x.com/a?b=1&c=2', 'http://y.io/p', 'https://z.dev/', 'https://w.app/q'])
  expect(isLink('https://x.com')).toBe(true)
  expect(isLink('/tmp/a.pdf')).toBe(false)
  expect(links('문서는 https://docs.x.com/guide에서, 표는 https://x.com/t?a=1을 참고')).toEqual(['https://docs.x.com/guide', 'https://x.com/t?a=1'])
  expect(linkLabel('https://docs.x.com/guide/')).toBe('docs.x.com/guide')
  expect(linkLabel(`https://x.com/${'a'.repeat(60)}`)).toHaveLength(32)
  expect(openCommand('windows', 'https://x.com/a')).toEqual(['rundll32', 'url.dll,FileProtocolHandler', 'https://x.com/a'])
})

test('조사가 붙은 경로: 끝이 조사일 때만 떼고, 이름의 일부나 폴더 이름 전체는 떼지 않음', () => {
  expect(unsuffixed('/w/plugins에서는')).toEqual(['/w/plugins에서', '/w/plugins'])
  expect(unsuffixed('/w/out에서부터는')).toEqual(['/w/out에서부터', '/w/out에서', '/w/out'])
  expect(unsuffixed('/w/a.pdf를')).toEqual(['/w/a.pdf'])
  expect(unsuffixed('/w/out입니다')).toEqual(['/w/out'])
  expect(unsuffixed('/w/보고서에')).toEqual(['/w/보고서'])
  expect(unsuffixed('/w/보고서')).toEqual([])
  expect(unsuffixed('/w/에서')).toEqual([])
  expect(unsuffixed('/w/a.pdf')).toEqual([])
})

test('기록 삭제: 그 항목만 지움', () => {
  const list = remember([], [{ path: '/w/a.pdf', isDir: false }, { path: '/w/b.pdf', isDir: false }], 1)
  expect(forget(list, '/w/a.pdf').map(item => item.path)).toEqual(['/w/b.pdf'])
})

const SCREEN = '지금 위치는 **/home/bch/Project/claude-marketplace**입니다.\n\n→ 하위 프로젝트: `changroro-plugins`, `find-me.git`(bare 저장소)와 `없는폴더` 가 있습니다.'

test('화면 그대로의 답변: 굵게 표시된 절대 경로와 백틱 속 폴더 이름도 후보', () => {
  expect(candidates(SCREEN)).toEqual(expect.arrayContaining(['/home/bch/Project/claude-marketplace', 'changroro-plugins', 'find-me.git', '없는폴더']))
})

test('붙여넣은 이미지: 폴더 규약, 번호순, 입력창·전송 기준', () => {
  expect(slug('/home/bch/Project/claude-marketplace')).toBe('-home-bch-Project-claude-marketplace')
  const shots = pick([file('10.png', 3), file('2.jpg', 2), file('1.png', 1), file('notes.txt', 9)], '/d')
  expect(shots.map(s => s.number)).toEqual([1, 2, 10])
  expect(refsOf('[Image #2] 이거 [Image #10] 와 [Image #2]')).toEqual([2, 10])
  expect(visible(shots, [10], [1]).map(s => s.number)).toEqual([1, 10])
})

test('OS별 임시 루트와 여는 명령', () => {
  expect(tmpRoot('linux', {})).toBe('/tmp')
  expect(tmpRoot('mac', { TMPDIR: '/var/folders/ab/T/' })).toBe('/var/folders/ab/T')
  expect(tmpRoot('windows', { TEMP: 'C:\\Temp' })).toBe('C:\\Temp')
  expect(tmpRoot('mac', { CLAUDE_CODE_TMPDIR: '/x', TMPDIR: '/y' })).toBe('/x')
  expect(openCommand('mac', '/a b.pdf')).toEqual(['open', '/a b.pdf'])
  expect(openCommand('windows', 'C:/T/a.hwp')).toEqual(['rundll32', 'url.dll,FileProtocolHandler', 'C:\\T\\a.hwp'])
  expect(openCommand('linux', '/a.png')).toEqual(['xdg-open', '/a.png'])
})

const PANE = { plugin: 'file-dock', surface: 'terminal', component: 'Pane', requestId: 'file-dock', props: { title: '기록', isFocused: true, bodyColumns: 50, placement: 'dock', scroll: { offset: 0, bodyRows: 30 }, view: {} } } as any

const cases = [
  { os: 'linux', env: { HOME: '/home/u' }, uname: 'Linux', base: '/tmp/claude-1000', open: 'xdg-open', project: '-w' },
  { os: 'mac', env: { HOME: '/home/u', TMPDIR: '/var/folders/ab/T/' }, uname: 'Darwin', base: '/var/folders/ab/T/claude-1000', open: 'open', project: '-w' },
  { os: 'windows', env: { USERPROFILE: '/home/u', OS: 'Windows_NT', TEMP: 'C:\\Temp' }, uname: '', base: 'C:/Temp/claude-0', open: 'rundll32', project: 'C--w' },
] as const

for (const c of cases) {
  test(`${c.os}: 보낸 이미지·내가 적은 경로·Claude가 준 경로를 패널에 쌓고 기본 프로그램으로 엶`, async ($, on) => {
    const time = mock.clock(on)
    const images = `${c.base}/${c.project}/s1/images`
    const files = new Set(['/home/u/문서/보고서.hwp', '/w/out/result.pdf', '/w/chart.png', '/w/chart2.png', '/w/notes.md'])
    const dirs = new Set(['/w/plugins'])
    const opened: string[] = []
    let entries = [] as ReturnType<typeof file>[]
    let box = ''
    // Linux에서 도는 테스트 엔진은 C:/… 를 상대 경로로 보고 현재 폴더를 앞에 붙임
    const is = (path: string, want: string) => path === want || path.endsWith(`/${want}`)
    mock.env(on, c.env)
    mock.store(on)
    on('command.register', () => ({ value: { command: 'file-dock' } }))
    on('process.run', ($, e) => {
      if (e.argv[0] === c.open) opened.push(String(e.argv.at(-1)).replace(/\\/g, '/'))
      return ok(e.argv[0] === 'id' ? '1000\n' : e.argv[0] === 'uname' ? `${c.uname}\n` : '')
    })
    const toasts: string[] = []
    on('ui.toast', ($, e) => { toasts.push(e.text); return { value: undefined } })
    on('session.id', () => ({ value: 's1' }))
    on('session.cwd', () => ({ value: '/w' }))
    on('session.start', ($, e) => ({ cwd: e.cwd }))
    on('prompt.read', () => ({ value: { text: box, cursor: box.length } }))
    on('prompt.submit', ($, e) => ({ text: e.text }))
    on('turn.complete', ($, e) => ({ text: e.answer }))
    on('tool.call', () => ({ result: {} }))
    on('fs.exists', ($, e) => ({ value: files.has(e.path) || dirs.has(e.path) || is(e.path, c.base) || (is(e.path, images) && entries.length > 0) }))
    on('fs.stat', ($, e) => ({ value: { kind: dirs.has(e.path) ? 'dir' : 'file', size: 1, mtimeMs: 1, isLink: false } }))
    on('fs.list', ($, e) => ({ value: is(e.path, c.base) ? [dir('other'), dir(c.project)] : entries }))
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/w' } as any)
    const pane = await $.ui.mount(PANE) as any
    const shot = (n: number) => `open:${images.replace(/\\/g, '/')}/${n}.png`.replace(/^open:.*\/(?=C:)/, 'open:')

    entries = [file('2.png', 2), file('1.png', 1)]
    box = '[Image #1] [Image #2]'
    await time.advance(2_000)
    expect(await pane.find({ key: shot(1) })).toBeUndefined()
    box = '[Image #1] '
    await time.advance(2_000)

    await $.prompt.submit({ text: '[Image #1] 이거랑 ~/문서/보고서.hwp 봐줘', asUser: true })
    box = ''
    await time.advance(2_000)
    expect(await pane.find({ key: shot(1) })).toMatchObject({ props: { label: '1.png' } })
    expect(await pane.find({ key: shot(2) })).toBeUndefined()
    expect(await pane.find({ key: 'open:/home/u/문서/보고서.hwp' })).toMatchObject({ props: { label: '보고서.hwp' } })

    await $.tool.call({ tool: 'Write', file_path: '/w/notes.md', content: '...' } as any)
    const answer = '결과는 `out/result.pdf`, 차트는 ./chart.png, 폴더는 `plugins` 와 **/w/plugins** 입니다. 없는 /w/gone.pdf'
    await $.turn.complete({ answer, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as any)
    for (const [path, label] of [['/w/out/result.pdf', 'result.pdf'], ['/w/chart.png', 'chart.png'], ['/w/plugins', 'plugins/'], ['/w/notes.md', 'notes.md']]) {
      expect(await pane.find({ key: `open:${path}` })).toMatchObject({ props: { label } })
    }
    expect(await pane.find({ key: 'open:/w/gone.pdf' })).toBeUndefined()

    await pane.press({ key: 'open:/w/out/result.pdf' })
    expect(toasts.at(-1)).toBe('📂 result.pdf 열었습니다')
    expect(opened).toEqual(['/w/out/result.pdf'])

    await $.prompt.submit({ text: '/model /w/chart2.png', asUser: true })
    expect(await pane.find({ key: 'open:/w/chart2.png' })).toBeUndefined()
    await pane.unmount()
  })
}

test('FileDock 버튼: 파일이 없어도 보이고, 누르면 패널을 열고 다시 누르면 닫음', async ($, on) => {
  const opened: string[] = []
  const closed: string[] = []
  mock.store(on)
  on('ui.render', { component: 'AbovePrompt' }, () => ({ type: 'Box', props: {}, children: [] }))
  on('ui.panes', () => ({ value: opened.filter(id => !closed.includes(id)).map(id => ({ id, title: 'FileDock', isShown: true, isFocused: false, isPlaced: true })) }) as any)
  on('ui.open', ($, e) => { opened.push(e.id); return { value: { isPlaced: true } } })
  on('ui.close', ($, e) => { closed.push(e.id); return { value: undefined } })
  const band = await $.ui.mount({ plugin: 'file-dock', surface: 'terminal', component: 'AbovePrompt', props: { hasSurvey: false, bodyColumns: 120 } } as any)
  expect(await band.find({ key: 'dock' })).toMatchObject({ props: { label: 'FileDock' } })
  await band.press({ key: 'dock' })
  expect(opened).toEqual(['file-dock'])
  await band.press({ key: 'dock' })
  expect(closed).toEqual(['file-dock'])
  await band.unmount()
})


test('패널: 세션을 넘어 쌓인 기록을 최신순으로 보여 주고 메모를 쌓음', async ($, on) => {
  const time = mock.clock(on)
  const opened: string[] = []
  const old = { path: '/old/옛날.pdf', isDir: false, at: 1, memos: [{ at: 1, text: '이어 연 세션 메모' }] }
  const elsewhere = { path: '/other/남의세션.pdf', isDir: false, at: 1, memos: [] }
  const files = new Set(['/w/new.png', '/w/app.ts', '/w/doc.pdf', '/w/out'])
  let box = ''
  let images = [] as ReturnType<typeof file>[]
  mock.store(on, { 'history:s1': [old], 'history:s2': [elsewhere], history: [elsewhere] })
  mock.env(on, { HOME: '/home/u' })
  on('process.run', ($, e) => {
    if (e.argv[0] === 'xdg-open') opened.push(String(e.argv.at(-1)))
    return ok(e.argv[0] === 'id' ? '1000\n' : e.argv[0] === 'uname' ? 'Linux\n' : '')
  })
  on('command.register', () => ({ value: { command: 'file-dock' } }))
  const panes: unknown[] = []
  on('ui.open', ($, e) => { panes.push(e); return { value: { isPlaced: true } } })
  on('ui.toast', () => ({ value: undefined }))
  on('ui.render', { component: 'AbovePrompt' }, () => ({ type: 'Box', props: {}, children: [] }))
  on('session.id', () => ({ value: 's1' }))
  on('session.cwd', () => ({ value: '/w' }))
  on('session.start', ($, e) => ({ cwd: e.cwd }))
  on('prompt.read', () => ({ value: { text: box, cursor: box.length } }))
  on('prompt.submit', ($, e) => ({ text: e.text }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('fs.exists', ($, e) => ({ value: files.has(e.path) || e.path.startsWith('/tmp/claude-1000') }))
  on('fs.stat', ($, e) => ({ value: { kind: e.path === '/w/out' ? 'dir' : 'file', size: 1, mtimeMs: 1, isLink: false } }))
  on('fs.list', ($, e) => ({ value: e.path.endsWith('/images') ? images : [] }))
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/w' } as any)
  await $.command.run({ command: 'file-dock', args: '' } as any)
  expect(panes).toHaveLength(1)

  const pane = await $.ui.mount(PANE) as any
  expect(await pane.find({ key: 'open:/old/옛날.pdf' })).toMatchObject({ props: { label: '옛날.pdf' } })
  expect(await pane.find({ key: 'memo:/old/옛날.pdf' })).toMatchObject({ props: { label: '이어 연 세션 메모' } })
  expect(await pane.find({ key: 'open:/other/남의세션.pdf' })).toBeUndefined()
  const band = await $.ui.mount({ plugin: 'file-dock', surface: 'terminal', component: 'AbovePrompt', props: { hasSurvey: false, bodyColumns: 120 } } as any)

  await $.turn.complete({ answer: '결과는 /w/new.png, 코드는 /w/app.ts 입니다.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as any)
  expect(await pane.find({ key: 'open:/w/new.png' })).toBeDefined()
  expect(await pane.find({ key: 'open:/w/app.ts' })).toBeUndefined()
  expect(await band.find({ key: 'claude-0' })).toMatchObject({ props: { label: 'new.png' } })
  expect(await band.find({ type: 'Text', text: /^Claude$/ })).toBeDefined()
  expect(await band.find({ type: 'Text', text: /^나$/ })).toBeUndefined()

  box = '[Image #1] '
  images = [file('1.png', 1)]
  await time.advance(2_000)
  await $.prompt.submit({ text: '[Image #1] 봐줘', asUser: true })
  box = ''
  await time.advance(2_000)
  expect(await pane.find({ key: 'open:/tmp/claude-1000/-w/s1/images/1.png' })).toMatchObject({ props: { label: '1.png' } })
  expect(await band.find({ key: 'image-1' })).toMatchObject({ props: { label: 'Image #1' } })
  expect(await band.find({ key: 'claude-0' })).toBeUndefined()
  expect(await band.find({ type: 'Text', text: /^Claude$/ })).toBeUndefined()
  expect(await band.find({ type: 'Text', text: /^나$/ })).toBeDefined()

  expect(await pane.find({ key: 'memo:/w/new.png' })).toMatchObject({ props: { label: '메모' } })
  await pane.press({ key: 'memo:/w/new.png' })
  await pane.input({ key: 'memo-input', text: '  ' })
  await pane.input({ key: 'memo-input', text: '첫 메모' })
  expect(await pane.find({ key: 'memo:/w/new.png' })).toMatchObject({ props: { label: '첫 메모' } })
  await pane.press({ key: 'memo:/w/new.png' })
  await pane.input({ key: 'memo-input', text: '둘째 메모' })
  expect(await pane.find({ key: 'memo-input' })).toBeUndefined()
  expect(await pane.find({ key: 'memo:/w/new.png' })).toMatchObject({ props: { label: '둘째 메모' } })
  expect((await pane.find({ type: 'Text', text: /첫 메모/ }))?.text).toContain('첫 메모')
  expect(await pane.find({ type: 'Text', text: /둘째 메모/ })).toBeUndefined()

  await pane.press({ key: 'open:/w/new.png' })
  expect(opened).toEqual(['/w/new.png'])
  await $.prompt.submit({ text: '/w/new.png 다시', asUser: true })
  await band.press({ key: 'mine-0' })
  expect(opened).toEqual(['/w/new.png', '/w/new.png'])

  await $.turn.complete({ answer: '보고서는 /w/doc.pdf를 /w/out에 두었고, 자세한 건 https://docs.x.com/guide에서 참고', durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer' } as any)
  expect(await pane.find({ key: 'open:https://docs.x.com/guide' })).toMatchObject({ props: { label: 'docs.x.com/guide' } })
  expect(await pane.find({ key: 'open:/w/doc.pdf' })).toMatchObject({ props: { label: 'doc.pdf' } })
  expect(await pane.find({ key: 'open:/w/out' })).toMatchObject({ props: { label: 'out/' } })
  expect(await Promise.all([0, 1, 2].map(async n => (await band.find({ key: `claude-${n}` }))?.props.label))).toEqual(['doc.pdf', 'out/', 'docs.x.com/guide'])
  expect(await band.find({ key: 'mine-0' })).toMatchObject({ props: { label: 'new.png' } })
  await band.unmount()
  await pane.press({ key: 'open:https://docs.x.com/guide' })
  expect(opened.at(-1)).toBe('https://docs.x.com/guide')

  expect(await pane.find({ key: 'drop:/old/옛날.pdf' })).toMatchObject({ props: { label: '삭제' } })
  await pane.press({ key: 'drop:/old/옛날.pdf' })
  expect(await pane.find({ key: 'drop:/old/옛날.pdf' })).toMatchObject({ props: { label: '기록에서 삭제' } })
  expect(await pane.find({ key: 'open:/old/옛날.pdf' })).toBeDefined()
  await pane.press({ key: 'drop:/old/옛날.pdf' })
  expect(await pane.find({ key: 'open:/old/옛날.pdf' })).toBeUndefined()
  expect(await pane.find({ key: 'open:/w/new.png' })).toBeDefined()
  await pane.unmount()

  const again = await $.ui.mount(PANE)
  expect((await again.find({ type: 'Text', text: /첫 메모/ }))?.text).toContain('첫 메모')
  await again.unmount()
})
