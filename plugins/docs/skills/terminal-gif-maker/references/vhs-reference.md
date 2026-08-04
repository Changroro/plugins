# VHS `.tape` Full Reference

VHS (Charmbracelet) scripted terminal recorder. All directives case-sensitive. One directive per line. `#` starts a comment.

## Output

```tape
Output <path>.gif
Output <path>.mp4
Output <path>.webm
```

Multiple `Output` directives produce all formats from a single run (saves time vs. re-rendering).

## Require

Ensures a binary is on `$PATH` before the tape runs. Fail-fast if missing.

```tape
Require docker
Require uv
```

## Set (terminal / recording options)

| Directive | Type | Default | Notes |
|---|---|---|---|
| `Set FontSize <n>` | int | 22 | pixels |
| `Set FontFamily "<name>"` | string | system mono | e.g. `"JetBrains Mono"` |
| `Set Width <n>` | int | 1200 | **must be even** |
| `Set Height <n>` | int | 600 | **must be even** |
| `Set LetterSpacing <f>` | float | 0 | tracking |
| `Set LineHeight <f>` | float | 1.0 |  |
| `Set LoopOffset <p>%` | percent | 0% | GIF loop starts at this % of frames |
| `Set Theme "<name>"` | string\|JSON | | 348 built-in themes (`vhs themes`) or JSON `{ "background": "...", "foreground": "...", "cursor": "...", ... }` |
| `Set Padding <n>` | int | 60 | inner padding |
| `Set Framerate <n>` | int | 50 | 24 is fine for GIF; 30/60 for MP4 |
| `Set PlaybackSpeed <f>` | float | 1.0 | `2.0` = 2× speed on output |
| `Set MarginFill "<file\|#hex>"` | string | none | image or color for margin |
| `Set Margin <n>` | int | 0 | outer margin (only works with MarginFill) |
| `Set BorderRadius <n>` | int | 0 | rounded corners |
| `Set WindowBar "<style>"` | enum | none | `Rings` / `RingsRight` / `Colorful` / `ColorfulRight` — macOS-style window chrome |
| `Set WindowBarSize <n>` | int | 40 | chrome height |
| `Set TypingSpeed <t>` | time | 50ms | default typing cadence |
| `Set Shell "<name>"` | string | user login shell | `"bash"` is recommended for deterministic prompt |

## Env

Set environment variables for the recording session.

```tape
Env PS1 "$ "
Env PATH "/custom/bin:$PATH"
```

## Sleep

```tape
Sleep 1s
Sleep 500ms
Sleep 1500ms
```

## Type

Simulated typing with per-character delay.

```tape
Type "git status"                # uses Set TypingSpeed
Type@100ms "slowly typed"        # override speed
Type@0ms "instant"               # no delay between chars
```

## Keys

All keys accept optional timing and repeat count.

```
<Key>[@<time>] [<count>]
```

Examples:

```tape
Enter                     # press once
Down 5                    # press Down 5 times, default timing
Tab@200ms 3               # press Tab 3 times, 200ms between
Escape@50ms               # quick Escape
```

### Supported keys

- Navigation: `Up`, `Down`, `Left`, `Right`, `PageUp`, `PageDown`
- Editing: `Enter`, `Space`, `Tab`, `Escape`, `Backspace`, `Delete`, `Insert`
- Combinations: `Ctrl+<key>` (e.g. `Ctrl+C`, `Ctrl+U`, `Ctrl+R`, `Ctrl+A`, `Ctrl+E`, `Ctrl+L`)

Note: `Shift+` and `Alt+` modifiers are NOT supported in VHS 0.11.0. For uppercase use `Type "A"`.

## Display control

```tape
Hide                      # subsequent commands run but don't appear in output
<commands>
Show                      # resume recording
```

Useful for:
- venv activation / env setup without cluttering the demo
- `clear` before starting the real scenario
- running docker pull in advance

## Scrolling

```tape
ScrollUp 10               # scroll viewport up by N lines
ScrollDown 10
ScrollUp@100ms 20         # with timing
```

Note: this scrolls the *terminal emulator's* viewport. If the running app has its own scroll (like `less` or a TUI), use that app's key bindings instead.

## CLI subcommands

```bash
vhs <tape>                # render a tape file
vhs new <path>            # emit an annotated sample tape
vhs validate <glob>       # parse-check without running
vhs record                # record your live session into a tape file
vhs themes                # list 348 theme names
vhs publish <gif>         # upload to vhs.charm.sh, get shareable URL
vhs serve                 # run a VHS SSH server (batch rendering service)
```

Flags:
- `-o, --output`: override `Output` directive (can repeat)
- `-p, --publish`: publish after render, print URL
- `-q, --quiet`: suppress progress logs
- `-v, --version`

## Theming cookbook

```tape
# Dark themes good for README on dark background
Set Theme "Dracula"
Set Theme "Tokyo Night"
Set Theme "Catppuccin Mocha"
Set Theme "Nord"
Set Theme "GitHub Dark"

# Light themes for light-background pages
Set Theme "GitHub Light"
Set Theme "Catppuccin Latte"

# Custom theme (JSON)
Set Theme { "background": "#1e1e2e", "foreground": "#cdd6f4", "cursor": "#f5e0dc", "selection": "#585b70" }
```

List all: `vhs themes` or pipe through grep.

## Timing shorthand

```tape
Sleep 1          # literal, but allow units
Sleep 1s
Sleep 500ms
Sleep 1.5s       # fractional seconds OK
```

`@<time>` modifier on keys/Type:
- `Type@50ms` — per-char delay (for typing)
- `Down@200ms 5` — delay between key repeats

## Output size / quality tuning

- GIF under 3MB for README: keep under ~30s @ 24fps @ 1280×720
- For longer demos: use MP4 (smaller files, better quality) + `<video>` embed
- Trim start delay with `Set LoopOffset` combined with timing discipline

## Debugging a tape

```bash
# validate syntax without running
vhs validate demo/foo.tape

# check output length and frame count
ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames,duration \
  -of json demo/foo.gif

# extract frame at t seconds as PNG
ffmpeg -ss 5 -i demo/foo.gif -frames:v 1 frame.png

# compare two renders frame-by-frame
ffmpeg -i demo/v1.gif -i demo/v2.gif -filter_complex \
  "[0:v][1:v]hstack" -frames:v 1 compare.png
```

## Escape sequences in Type

Within `Type "..."` most strings pass through literally. Caveats:
- `$` — literal dollar (shell does NOT expand inside Type; VHS sends the characters as-is)
- Newlines — use `Enter` directive, not `\n`
- Quotes inside string — escape: `Type "echo \"hi\""`

## Known limitations (as of vhs 0.11.0)

- No `Shift+`/`Alt+` modifier keys
- No conditional logic (`if/else`) in tapes — they're linear scripts
- `Set FontFamily` requires the font to be installed on the host running vhs
- MacOS notarization may block pre-built binaries → `xattr -d com.apple.quarantine vhs` after download
- `Require` only checks binaries on PATH; it doesn't verify library versions
