import type { FsEntry } from 'claude-code'

import type { Shot } from '../types'

const IMAGE = 'png|jpe?g|gif|webp|bmp|svg|heic|tiff?'
const EXT = [
  'pdf|hwpx?|docx?|pptx?|xlsx?|od[tps]|rtf|pages|key|numbers|epub|html?|md|markdown|txt|csv|tsv|log',
  IMAGE,
  'mp4|mov|webm|mkv|mp3|wav|m4a|flac|zip',
].join('|')

export const isShelved = (path: string) => new RegExp(`\\.(?:${EXT})$`, 'i').test(path)

const FILE_URL = /file:\/\/(\/[^\s"'`)>\]]+)/g
const QUOTED = /["'`]([^"'`\n]*[\\/.][^"'`\n]*)["'`]/g
const PART = '[\\w가-힣.@+\\-]+'
const TOKEN = new RegExp(`(^|[\\s(<\\[\`"'*_])((?:~[\\\\/]|\\.{1,2}[\\\\/]|[A-Za-z]:[\\\\/]|\\/)?${PART}(?:[\\\\/]${PART})*[\\\\/]?)(?=$|[\\s)>\\],:;!?\`"'*_]|\\.(?:\\s|$))`, 'gm')
const INLINE = /`([^`\s]+)`/g

// 슬래시가 있거나 확장자가 붙은 것만 경로 후보 (1.5, v2 같은 단어 제외)
const pathLike = (raw: string) => /[\\/]/.test(raw) || /[^.\s]\.[A-Za-z][A-Za-z0-9]{0,7}$/.test(raw)

export const isAbsolute = (raw: string) => raw.startsWith('/') || /^[A-Za-z]:[\\/]/.test(raw)

export function resolve(raw: string, cwd: string, home: string) {
  if (raw === '~' || /^~[\\/]/.test(raw)) return `${home}${raw.slice(1)}`
  if (isAbsolute(raw)) return raw
  return `${cwd.replace(/[\\/]$/, '')}/${raw.replace(/^\.[\\/]/, '')}`
}

export function candidates(text: string) {
  const found = [
    ...[...text.matchAll(FILE_URL)].map(m => decodeURIComponent(m[1])),
    ...[...text.matchAll(QUOTED)].map(m => m[1].trim().replace(/:\d+(?::\d+)?$/, '')),
    ...[...text.matchAll(TOKEN)].map(m => m[2].replace(/(?<=[^.])\.$/, '')),
  ]
  const inline = [...text.matchAll(INLINE)].map(m => m[1].replace(/:\d+(?::\d+)?$/, '')).filter(raw => /[A-Za-z가-힣]/.test(raw))
  return [...new Set([...found.filter(pathLike), ...inline].filter(raw => !raw.includes('://')))]
}

// 한 문자열을 조사로 나누는 방법이 하나뿐이어야 함 (이+나로 되는 "이나" 같은 겹침을 넣으면 긴 한글 이름에서 느려짐)
const JOSA = '으로|에서|에게|한테|까지|부터|처럼|같이|보다|마다|조차|마저|밖에|하고|라는|라고|라서|지만|니까|인데|이다|입니다|였습니다|이었습니다|이에요|예요|[이가은는을를의에와과도만로나랑며든인일임고께]'
const TAIL = new RegExp(`^(?:${JOSA})+$`)

// 끝의 한글이 조사일 때만 뗀 후보, 덜 뗀 것부터
export function unsuffixed(raw: string) {
  const run = raw.match(/[가-힣]+$/)?.[0].length ?? 0
  return Array.from({ length: run }, (_, i) => i + 1).filter(n => TAIL.test(raw.slice(-n)) && /[^\\/]$/.test(raw.slice(0, -n))).map(n => raw.slice(0, -n))
}

const LINK = /https?:\/\/[A-Za-z0-9\-._~:/?#@!$&+,;=%]+/g

export const isLink = (path: string) => /^https?:\/\//i.test(path)

// shortcut: 한글이 그대로 든 주소는 한글 앞에서 잘림, 조사가 붙은 주소와 구분할 방법이 생기면 넓힘
export const links = (text: string) => [...new Set([...text.matchAll(LINK)].map(m => m[0].replace(/[.,;:!?]+$/, '')))]

export function linkLabel(url: string) {
  const short = url.replace(/^https?:\/\//i, '').replace(/\/$/, '')
  return short.length > 32 ? `${short.slice(0, 31)}…` : short
}

export function pick(entries: readonly FsEntry[], dir: string): Shot[] {
  return entries
    .filter(entry => entry.kind === 'file' && /^\d+\.[a-z]+$/i.test(entry.name))
    .map(entry => ({ path: `${dir}/${entry.name}`, number: Number.parseInt(entry.name, 10), mtimeMs: entry.mtimeMs }))
    .sort((a, b) => a.number - b.number)
}

// Claude Code 내부 규약: <임시 루트>/claude-<uid, Windows는 0>/<프로젝트 폴더>/<세션 ID>/images/<번호>.<확장자>
export const slug = (cwd: string) => cwd.replace(/[^A-Za-z0-9]/g, '-')

export const refsOf = (text: string) => [...new Set([...text.matchAll(/\[Image #(\d+)\]/g)].map(m => Number(m[1])))]

export const visible = (shots: Shot[], draft: number[], sent: number[]) => shots.filter(shot => draft.includes(shot.number) || sent.includes(shot.number))
