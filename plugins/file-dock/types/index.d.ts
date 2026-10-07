export type Shot = { path: string; number: number; mtimeMs: number }

export type Entry = { path: string; isDir: boolean }

declare module 'claude-code' {
  interface PluginState {
    'file-dock': { pasted: Shot[]; draft: number[]; sent: number[]; mine: Entry[]; claude: Entry[] }
  }
}
