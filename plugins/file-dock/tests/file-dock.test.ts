import { expect, mock, test } from 'claude-code/testing'

import { candidates, isShelved, pick, refsOf, resolve, slug, visible } from '../hooks/paths'
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

const cases = [
  { os: 'linux', env: { HOME: '/home/u' }, uname: 'Linux', base: '/tmp/claude-1000', open: 'xdg-open', project: '-w' },
  { os: 'mac', env: { HOME: '/home/u', TMPDIR: '/var/folders/ab/T/' }, uname: 'Darwin', base: '/var/folders/ab/T/claude-1000', open: 'open', project: '-w' },
  { os: 'windows', env: { USERPROFILE: '/home/u', OS: 'Windows_NT', TEMP: 'C:\\Temp' }, uname: '', base: 'C:/Temp/claude-0', open: 'rundll32', project: 'C--w' },
] as const

for (const c of cases) {
  test(`${c.os}: 붙여넣은 이미지·내가 적은 경로·Claude가 준 경로를 버튼으로 모아 기본 프로그램으로 엶`, async ($, on) => {
    const time = mock.clock(on)
    const images = `${c.base}/${c.project}/s1/images`
    const files = new Set(['/home/u/문서/보고서.hwp', '/w/out/result.pdf', '/w/chart.png', '/w/notes.md'])
    const dirs = new Set(['/w/plugins'])
    const opened: string[] = []
    let entries = [] as ReturnType<typeof file>[]
    let box = ''
    // Linux에서 도는 테스트 엔진은 C:/… 를 상대 경로로 보고 현재 폴더를 앞에 붙임
    const is = (path: string, want: string) => path === want || path.endsWith(`/${want}`)
    mock.env(on, c.env)
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
    on('ui.render', { component: 'AbovePrompt' }, () => ({ type: 'Box', props: {}, children: [] }))
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/w' } as any)
    const band = await $.ui.mount({ plugin: 'file-dock', surface: 'terminal', component: 'AbovePrompt', props: { hasSurvey: false, bodyColumns: 120 } } as any)

    entries = [file('2.png', 2), file('1.png', 1)]
    box = '[Image #1] [Image #2]'
    await time.advance(2_000)
    expect(await band.find({ key: 'image-1' })).toMatchObject({ props: { label: 'Image #1' } })
    box = '[Image #1] '
    await time.advance(2_000)
    expect(await band.find({ key: 'image-2' })).toBeUndefined()

    await $.prompt.submit({ text: '[Image #1] 이거랑 ~/문서/보고서.hwp 봐줘', asUser: true })
    box = ''
    await time.advance(2_000)
    expect(await band.find({ key: 'image-1' })).toBeDefined()
    expect(await band.find({ key: 'mine-0' })).toMatchObject({ props: { label: '보고서.hwp' } })

    await $.tool.call({ tool: 'Write', file_path: '/w/notes.md', content: '...' } as any)
    const answer = '결과는 `out/result.pdf`, 차트는 ./chart.png, 폴더는 `plugins` 와 **/w/plugins** 입니다. 없는 /w/gone.pdf'
    await $.turn.complete({ answer, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as any)
    const labels = await Promise.all([0, 1, 2, 3, 4].map(async i => (await band.find({ key: `claude-${i}` }))?.props.label))
    expect(labels).toEqual(['result.pdf', 'chart.png', 'plugins/', 'notes.md', undefined])


    await band.press({ key: 'image-1' })
    await band.press({ key: 'mine-0' })
    await band.press({ key: 'claude-0' })
    expect(toasts.at(-1)).toBe('📂 result.pdf 열었습니다')
    expect(opened.map(path => path.replace(/^.*\/(?=C:)/, ''))).toEqual([`${images.replace(/\\/g, '/')}/1.png`.replace(/^.*\/(?=C:)/, ''), '/home/u/문서/보고서.hwp', '/w/out/result.pdf'])

    await $.turn.complete({ answer: '파일 없음', durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer' } as any)
    expect(await band.find({ key: 'claude-0' })).toBeUndefined()
    expect(await band.find({ key: 'mine-0' })).toBeDefined()
    await band.unmount()
  })
}
