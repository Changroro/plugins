import type { FsEntry } from 'claude-code'

import type { Shot } from '../types'

const EXT = [
  'pdf|hwpx?|docx?|pptx?|xlsx?|od[tps]|rtf|pages|key|numbers|epub|html?|md|markdown|txt|csv|tsv|log',
  'png|jpe?g|gif|webp|bmp|svg|heic|tiff?',
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
    ...[...text.matchAll(TOKEN)].map(m => m[2]),
  ]
  const inline = [...text.matchAll(INLINE)].map(m => m[1].replace(/:\d+(?::\d+)?$/, '')).filter(raw => /[A-Za-z가-힣]/.test(raw))
  return [...new Set([...found.filter(pathLike), ...inline].filter(raw => !raw.includes('://')))]
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
