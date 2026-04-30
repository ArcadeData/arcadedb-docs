// Cookie consent banner. Ported from src/main/asciidoc/web-footer.adoc.
// Sets a localStorage flag and a 1-year cookie scoped to .arcadedb.com,
// so dismissals on docs.arcadedb.com persist across the property.
;(function () {
  'use strict'

  var CONSENT_KEY = 'arcadedb_cookie_consent'

  function hasConsented () {
    try {
      if (localStorage.getItem(CONSENT_KEY)) return true
    } catch (e) { /* localStorage unavailable */ }
    var cookies = document.cookie.split(';')
    for (var i = 0; i < cookies.length; i++) {
      if (cookies[i].trim().indexOf(CONSENT_KEY + '=') === 0) return true
    }
    return false
  }

  function storeConsent () {
    try { localStorage.setItem(CONSENT_KEY, '1') } catch (e) {}
    var expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toUTCString()
    document.cookie =
      CONSENT_KEY + '=1; expires=' + expires +
      '; path=/; domain=.arcadedb.com; SameSite=Lax'
  }

  function ready (fn) {
    if (document.readyState !== 'loading') fn()
    else document.addEventListener('DOMContentLoaded', fn)
  }

  ready(function () {
    if (hasConsented()) return
    var banner = document.getElementById('arcadedb-cookie-banner')
    var btn = document.getElementById('arcadedb-cookie-ok')
    if (!banner || !btn) return
    banner.style.display = 'flex'
    btn.addEventListener('click', function () {
      storeConsent()
      banner.style.display = 'none'
    })
  })
})()
