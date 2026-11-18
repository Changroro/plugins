import { expect, test } from 'claude-code/testing'

import { applyTodo } from '../hooks/register'
import { buildScene, fit } from '../hooks/scene'

test('to-do actions keep the person\'s words and index from 1', async () => {
  const added = applyTodo([], { action: 'add', items: ['기획서 마무리', ' 경비 정산 '] })
  expect(added).toEqual([
    { text: '기획서 마무리', done: false },
    { text: '경비 정산', done: false },
  ])
  const done = applyTodo(added as never, { action: 'done', indexes: [2] })
  expect(done).toEqual([
    { text: '기획서 마무리', done: false },
    { text: '경비 정산', done: true },
  ])
  expect(applyTodo(done as never, { action: 'done', indexes: [9] })).toBe('done needs indexes between 1 and 2')
  expect(applyTodo(done as never, { action: 'remove', indexes: [1] })).toEqual([{ text: '경비 정산', done: true }])
})

test('the scene stays within the Svg limits whatever the person typed', async () => {
  const long = '<script>&"' + '아주 긴 할 일'.repeat(40)
  const svg = buildScene({
    time: '09:05',
    ctx: 97,
    cacheLeftMin: 0,
    cacheTotalMin: 60,
    project: long,
    todos: Array.from({ length: 30 }, (_, i) => ({ text: long, done: i % 2 === 0 })),
    isCheering: true,
  })
  expect(svg.length < 131_072).toBe(true)
  expect(svg.includes('<script')).toBe(false)
  expect(svg.includes('&')).toBe(false)
  expect(fit('abcdef', 3, 1)).toBe('abcde…')
})
