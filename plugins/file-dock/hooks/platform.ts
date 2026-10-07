export type Os = 'mac' | 'windows' | 'linux'

export type Env = Record<string, string | undefined>

// Node os.tmpdir() 규칙: Claude Code가 붙여넣은 이미지를 두는 임시 루트
export function tmpRoot(os: Os, env: Env) {
  if (env.CLAUDE_CODE_TMPDIR) return env.CLAUDE_CODE_TMPDIR
  if (os === 'windows') return env.TEMP || env.TMP || `${env.SystemRoot || env.windir || 'C:\\Windows'}\\temp`
  return (env.TMPDIR || env.TMP || env.TEMP || '/tmp').replace(/(.)\/+$/, '$1')
}

export function openCommand(os: Os, path: string) {
  if (os === 'mac') return ['open', path]
  if (os === 'windows') return ['rundll32', 'url.dll,FileProtocolHandler', path.replace(/\//g, '\\')]
  return ['xdg-open', path]
}

export const baseName = (path: string) => path.split(/[\\/]/).at(-1) ?? path
