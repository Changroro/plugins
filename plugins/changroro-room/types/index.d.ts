export type Todo = { text: string; done: boolean }

declare module 'claude-code' {
  interface PluginState {
    'changroro-room': {
      minute: number
      ctx: number | null
      cacheAt: number | null
      project: string
      todos: Todo[]
      cheerAt: number
    }
  }
}
