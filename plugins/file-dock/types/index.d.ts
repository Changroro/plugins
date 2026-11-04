export type Shot = { path: string; number: number; mtimeMs: number }

export type Entry = { path: string; isDir: boolean }

export type Memo = { at: number; text: string }

export type Item = Entry & { at: number; project: string; memos: Memo[] }

declare module 'claude-code' {
  interface PluginState {
    'file-dock': { pasted: Shot[]; draft: number[]; sent: number[]; mine: Entry[]; claude: Entry[]; revision: number; writing: string; page: number }
  }
}
