// Theme toggle and reduced-motion handling.
// The toggle cycles system -> light -> dark. "System" removes data-theme from <html>, so the CSS
// follows prefers-color-scheme; "light" and "dark" set it and are remembered in localStorage.
// The saved value is applied before first paint by the inline script in partials/head-styles.hbs
// (same key). localStorage can be blocked (private window, site data off): every access is guarded
// and the toggle then works for the current page only.
;(function () {
  'use strict'

  var KEY = 'arcadedb-docs-theme'
  var ORDER = ['system', 'light', 'dark']
  var NAMES = { system: 'follows the system', light: 'light', dark: 'dark' }
  var root = document.documentElement

  function current () {
    var t = root.getAttribute('data-theme')
    return t === 'light' || t === 'dark' ? t : 'system'
  }

  function apply (mode, save) {
    if (mode === 'system') root.removeAttribute('data-theme')
    else root.setAttribute('data-theme', mode)
    if (save) {
      try {
        if (mode === 'system') localStorage.removeItem(KEY)
        else localStorage.setItem(KEY, mode)
      } catch (e) { /* storage unavailable: the choice lasts for this page only */ }
    }
  }

  function label (btn, mode) {
    var next = ORDER[(ORDER.indexOf(mode) + 1) % ORDER.length]
    btn.setAttribute('data-mode', mode)
    btn.setAttribute('title', 'Color theme: ' + NAMES[mode])
    btn.setAttribute('aria-label', 'Color theme: ' + NAMES[mode] + '. Activate to switch to ' + NAMES[next] + '.')
  }

  function ready (fn) {
    if (document.readyState !== 'loading') fn()
    else document.addEventListener('DOMContentLoaded', fn)
  }

  ready(function () {
    var btn = document.querySelector('.theme-toggle')
    if (btn) {
      label(btn, current())
      btn.addEventListener('click', function () {
        var mode = ORDER[(ORDER.indexOf(current()) + 1) % ORDER.length]
        apply(mode, true)
        label(btn, mode)
      })
    }

    // The dots that travel along the lines of the inline SVG diagrams are SMIL animations, which CSS
    // cannot switch off. Readers who ask for reduced motion get the still diagram.
    var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)')
    function stillDiagrams () {
      var svgs = document.querySelectorAll('svg')
      for (var i = 0; i < svgs.length; i++) {
        try {
          if (rm.matches) svgs[i].pauseAnimations()
          else svgs[i].unpauseAnimations()
        } catch (e) {}
      }
    }
    if (rm) {
      stillDiagrams()
      if (rm.addEventListener) rm.addEventListener('change', stillDiagrams)
    }
  })
})()
