export type Shot = { path: string; number: number; mtimeMs: number }

export type Entry = { path: string; isDir: boolean }

export type Memo = { at: number; text: string }

export type Item = Entry & { at: number; project: string; memos: Memo[] }

declare module 'claude-code' {
  interface PluginState {
    'file-dock': { draft: number[]; sent: number[]; revision: number; writing: string; removing: string; page: number }
  }
}
