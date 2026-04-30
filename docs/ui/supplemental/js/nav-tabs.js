// Sidebar tab activation. Each top-level entry in page.navigation
// (one per nav.adoc) is rendered as a tab pane in nav-menu.hbs.
// Active tab is chosen as: pane containing current page > localStorage
// > first tab.
;(function () {
  'use strict'

  var STORAGE_KEY = 'arcadedb.nav-tab'

  function ready (fn) {
    if (document.readyState !== 'loading') fn()
    else document.addEventListener('DOMContentLoaded', fn)
  }

  function activate (tabs, panes, index) {
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.toggle('is-active', i === index)
    }
    for (var j = 0; j < panes.length; j++) {
      panes[j].classList.toggle('is-active', j === index)
    }
    try { localStorage.setItem(STORAGE_KEY, String(index)) } catch (e) {}
  }

  ready(function () {
    var tabs = document.querySelectorAll('.nav-tab')
    var panes = document.querySelectorAll('.nav-tab-pane')
    if (!tabs.length || !panes.length) return

    var initial = 0
    var foundCurrent = -1
    for (var i = 0; i < panes.length; i++) {
      if (panes[i].querySelector('.is-current-page')) {
        foundCurrent = i
        break
      }
    }
    if (foundCurrent >= 0) {
      initial = foundCurrent
    } else {
      try {
        var stored = localStorage.getItem(STORAGE_KEY)
        if (stored !== null) {
          var parsed = parseInt(stored, 10)
          if (!isNaN(parsed) && parsed >= 0 && parsed < tabs.length) initial = parsed
        }
      } catch (e) {}
    }

    for (var k = 0; k < tabs.length; k++) {
      (function (idx) {
        tabs[idx].addEventListener('click', function () { activate(tabs, panes, idx) })
      })(k)
    }

    activate(tabs, panes, initial)
  })
})()
