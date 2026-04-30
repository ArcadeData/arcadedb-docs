'use strict'

// Inject Algolia DocSearch credentials into site.keys from env vars.
// Wired into antora-playbook.yml under antora.extensions; runs before
// the UI catalog renders, so {{site.keys.algolia*}} is populated for
// the head/footer/header partials.
//
// Required env vars (set as GH Actions secrets and exported by the
// workflow before invoking antora):
//   ALGOLIA_APP_ID
//   ALGOLIA_API_KEY      — search-only key, never the admin key
//   ALGOLIA_INDEX_NAME   — defaults to "arcadedb" if unset
module.exports.register = function () {
  this.once('contextStarted', ({ playbook }) => {
    if (!process.env.ALGOLIA_APP_ID) return
    playbook.site = playbook.site || {}
    playbook.site.keys = playbook.site.keys || {}
    playbook.site.keys.algoliaAppId = process.env.ALGOLIA_APP_ID
    playbook.site.keys.algoliaApiKey = process.env.ALGOLIA_API_KEY || ''
    playbook.site.keys.algoliaIndexName = process.env.ALGOLIA_INDEX_NAME || 'arcadedb'
  })
}
