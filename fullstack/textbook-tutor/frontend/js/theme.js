/** Light/dark theme: resolve, apply, persist, toggle.
 *
 * The resolved theme is written to <html data-theme> by a tiny inline script in
 * index.html *before* first paint — otherwise a dark-mode user who chose light
 * gets a white flash on every load. This module owns everything after that.
 */
import { $ } from "./dom.js";

const KEY = "theme";           // "light" | "dark"; absent = follow the OS
const DARK_QUERY = "(prefers-color-scheme: dark)";

const stored = () => {
  try { return localStorage.getItem(KEY); } catch (e) { return null; }
};

const systemTheme = () =>
  window.matchMedia && window.matchMedia(DARK_QUERY).matches ? "dark" : "light";

export const currentTheme = () => document.documentElement.dataset.theme || systemTheme();

const SUN = `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.2v2M12 19.8v2M2.2 12h2M19.8 12h2M4.9 4.9l1.5 1.5M17.6 17.6l1.5 1.5M19.1 4.9l-1.5 1.5M6.4 17.6l-1.5 1.5"/></svg>`;
const MOON = `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.3A8.5 8.5 0 0 1 9.7 3.5a8.5 8.5 0 1 0 10.8 10.8z"/></svg>`;

function paintButton(theme) {
  const btn = $("themeToggle");
  if (!btn) return;
  // Show the mode you'd switch TO, so the icon reads as an action.
  const next = theme === "dark" ? "light" : "dark";
  btn.innerHTML = next === "dark" ? MOON : SUN;
  btn.title = `Switch to ${next} mode`;
  btn.setAttribute("aria-label", btn.title);
}

function apply(theme, persist) {
  document.documentElement.dataset.theme = theme;
  if (persist) {
    try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode */ }
  }
  paintButton(theme);
}

export function initTheme() {
  apply(currentTheme(), false);
  const btn = $("themeToggle");
  if (btn) btn.onclick = () => apply(currentTheme() === "dark" ? "light" : "dark", true);

  // Follow the OS only while the user hasn't made an explicit choice.
  if (window.matchMedia) {
    window.matchMedia(DARK_QUERY).addEventListener("change", (e) => {
      if (!stored()) apply(e.matches ? "dark" : "light", false);
    });
  }
}
