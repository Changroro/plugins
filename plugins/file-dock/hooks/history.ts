import type { Entry, Item } from '../types'

const trimmed = (path: string) => path.replace(/(?<=.)[\\/]$/, '')

export function remember(list: Item[], entries: Entry[], at: number): Item[] {
  const fresh = new Map(entries.map(entry => [trimmed(entry.path), entry.isDir]))
  const moved = [...fresh].map(([path, isDir]) => ({ path, isDir, at, memos: list.find(item => item.path === path)?.memos ?? [] }))
  return [...list.filter(item => !fresh.has(item.path)), ...moved]
}

export const addMemo = (list: Item[], path: string, text: string, at: number) => list.map(item => (item.path === path ? { ...item, memos: [...item.memos, { at, text }] } : item))

export const forget = (list: Item[], path: string) => list.filter(item => item.path !== path)

export function when(at: number) {
  const date = new Date(at)
  const two = (value: number) => String(value).padStart(2, '0')
  return `${two(date.getMonth() + 1)}-${two(date.getDate())} ${two(date.getHours())}:${two(date.getMinutes())}`
}
