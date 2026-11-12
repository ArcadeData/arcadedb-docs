'use strict'

// Plain text from an Antora title or description: drop HTML tags and decode
// character references (`&#8212;`, `&amp;`, ...) so meta tags and JSON-LD
// carry the characters a reader sees. Output with {{plain x}} (double stash)
// so Handlebars escapes it again for the attribute it lands in.

const TAG_RX = /<[^>]+>/g
const ENTITY_RX = /&(#\d+|#x[0-9a-f]+|[a-z]+);/gi
const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' }

function plain (value) {
  if (value == null) return ''
  return String(value)
    .replace(TAG_RX, '')
    .replace(ENTITY_RX, (match, ref) => {
      if (ref[0] === '#') {
        const code = ref[1] === 'x' || ref[1] === 'X' ? parseInt(ref.slice(2), 16) : parseInt(ref.slice(1), 10)
        return Number.isFinite(code) ? String.fromCodePoint(code) : match
      }
      const named = NAMED[ref.toLowerCase()]
      return named === undefined ? match : named
    })
    .replace(/\s+/g, ' ')
    .trim()
}

module.exports = (value) => plain(value)
