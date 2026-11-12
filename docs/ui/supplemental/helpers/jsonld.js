'use strict'

// Schema.org JSON-LD for every page: the docs WebSite, a BreadcrumbList built
// from the nav, and a TechArticle (WebPage on a component home). The
// Organization and SoftwareApplication nodes live on arcadedb.com and are
// referenced by @id only. Building the object in JS and serialising it with
// JSON.stringify keeps quotes and entities in titles from breaking the script
// block. Use as {{{jsonld}}} inside <script type="application/ld+json">.

// Same as helpers/plain.js: Antora loads each helper from a string, so a
// relative require() of a sibling helper does not resolve.
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

const ORG = 'https://arcadedb.com/#organization'
const SOFTWARE = 'https://arcadedb.com/#software'
const MAIN_SITE = 'https://arcadedb.com/#website'
const IMAGE = 'https://arcadedb.com/assets/images/arcadedb-logo.png'

module.exports = ({ data: { root } }) => {
  const { page = {}, site = {} } = root
  const siteUrl = (site.url || '').replace(/\/$/, '')
  const pageUrl = page.canonicalUrl
  if (!siteUrl || !pageUrl) return ''
  const abs = (url) => (/^https?:/.test(url) ? url : siteUrl + url)
  const websiteId = siteUrl + '/#website'

  const website = {
    '@type': 'WebSite',
    '@id': websiteId,
    url: siteUrl + '/',
    name: plain(site.title) || 'ArcadeDB Documentation',
    inLanguage: 'en',
    publisher: { '@id': ORG },
    isPartOf: { '@id': MAIN_SITE },
  }

  // Component home first, then the nav trail, then the page itself. Crumbs
  // without a link (group labels) or pointing at a fragment are skipped:
  // Google allows a missing item only on the last element.
  const crumbs = []
  const add = (name, url) => {
    if (!name || !url || url.includes('#')) return
    const item = abs(url)
    if (crumbs.length && crumbs[crumbs.length - 1].item === item) return
    crumbs.push({ name: plain(name), item })
  }
  const cv = page.componentVersion
  if (cv) add(cv.title, cv.url)
  for (const crumb of page.breadcrumbs || []) {
    if (crumb.urlType === 'internal') add(crumb.content, crumb.url)
  }
  if (!crumbs.length || crumbs[crumbs.length - 1].item !== pageUrl) {
    crumbs.push({ name: plain(page.title), item: pageUrl })
  }

  const graph = [website]
  if (crumbs.length > 1) {
    graph.push({
      '@type': 'BreadcrumbList',
      '@id': pageUrl + '#breadcrumb',
      itemListElement: crumbs.map((c, i) => ({ '@type': 'ListItem', position: i + 1, name: c.name, item: c.item })),
    })
  }

  const isHome = cv && page.url === cv.url
  const article = {
    '@type': isHome ? 'WebPage' : 'TechArticle',
    '@id': pageUrl + (isHome ? '#webpage' : '#article'),
    url: pageUrl,
    mainEntityOfPage: pageUrl,
    [isHome ? 'name' : 'headline']: plain(page.title),
    inLanguage: 'en',
    isPartOf: { '@id': websiteId },
    about: { '@id': SOFTWARE },
    author: { '@id': ORG },
    publisher: { '@id': ORG },
    image: IMAGE,
  }
  if (page.description) article.description = plain(page.description)
  if (crumbs.length > 1) article.breadcrumb = { '@id': pageUrl + '#breadcrumb' }
  graph.push(article)

  return JSON.stringify({ '@context': 'https://schema.org', '@graph': graph }, null, 2)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026')
}
