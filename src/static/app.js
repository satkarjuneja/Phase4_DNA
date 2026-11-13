// Forms and buttons on the pages talk to the Python backend's JSON API.
// The browser never talks to the database.
(function () {
  "use strict";

  const banner = document.getElementById("banner");

  function showBanner(message, kind) {
    banner.textContent = message;
    banner.className = "banner " + kind;
    banner.hidden = false;
    clearTimeout(showBanner.timer);
    if (kind === "ok") showBanner.timer = setTimeout(() => { banner.hidden = true; }, 5000);
  }
  banner.addEventListener("click", () => { banner.hidden = true; });

  // A message saved before a reload/redirect is shown on the next page
  try {
    const saved = sessionStorage.getItem("flash");
    if (saved) { sessionStorage.removeItem("flash"); showBanner(saved, "ok"); }
  } catch (e) { /* storage unavailable: no message, page still works */ }

  // "/races/{race_id}" + {race_id: 7} -> "/races/7"
  function fill(template, ...sources) {
    return template.replace(/\{(\w+)\}/g, (whole, key) => {
      for (const s of sources) if (s && s[key] != null) return encodeURIComponent(s[key]);
      return whole;
    });
  }

  function sentence(text) {
    text = String(text || "Done");
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  async function send(method, url, payload, options) {
    let response, data = {};
    try {
      response = await fetch(url, {
        method,
        headers: payload ? { "Content-Type": "application/json" } : {},
        body: payload ? JSON.stringify(payload) : undefined,
      });
      data = await response.json().catch(() => ({}));
    } catch (e) {
      showBanner("Could not reach the server. Is the application still running?", "error");
      return;
    }
    if (!response.ok) {
      showBanner(data.detail || "Request failed (" + response.status + ")", "error");
      return;
    }
    try { sessionStorage.setItem("flash", sentence(data.result)); } catch (e) { /* ignore */ }
    if (options.redirect) window.location.href = fill(options.redirect, data, payload);
    else window.location.reload();
  }

  // <form class="api-form" data-api="/api/..." data-method="POST|PUT">
  document.addEventListener("submit", (event) => {
    const form = event.target.closest("form.api-form");
    if (!form) return;
    event.preventDefault();
    const payload = {};
    for (const el of form.elements) {
      if (!el.name || el.type === "submit") continue;
      const value = el.value.trim();
      if (el.dataset.merge !== undefined) {
        // One <select> that fills several fields, e.g. venue country + name
        if (value === "") el.dataset.merge.split(",").forEach((k) => { payload[k] = null; });
        else Object.assign(payload, JSON.parse(value));
      } else if (value === "") {
        payload[el.name] = null;
      } else if (el.type === "number" || el.dataset.type === "number") {
        payload[el.name] = Number(value);
      } else {
        payload[el.name] = value;
      }
    }
    const button = form.querySelector("button[type=submit]");
    if (button) button.disabled = true;
    send(form.dataset.method, form.dataset.api, payload, { redirect: form.dataset.redirect })
      .finally(() => { if (button) button.disabled = false; });
  });

  // <button data-api="/api/..." data-method="DELETE" data-confirm="...">
  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-api]");
    if (!button) return;
    if (button.dataset.confirm && !window.confirm(button.dataset.confirm)) return;
    send(button.dataset.method || "DELETE", button.dataset.api, null, { redirect: button.dataset.redirect });
  });

  // Admin mode: shows the add / edit / delete controls
  const toggle = document.getElementById("admin-toggle");
  toggle.checked = document.documentElement.classList.contains("admin");
  toggle.addEventListener("change", () => {
    document.documentElement.classList.toggle("admin", toggle.checked);
    try { localStorage.setItem("admin", toggle.checked ? "1" : "0"); } catch (e) { /* ignore */ }
  });
})();
