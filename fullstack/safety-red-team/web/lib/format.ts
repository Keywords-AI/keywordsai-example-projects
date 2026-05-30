export const pct = (x: number, d = 0) => `${(x * 100).toFixed(d)}%`;

export const usd = (x: number) =>
  x < 0.01 ? `$${x.toFixed(4)}` : `$${x.toFixed(2)}`;

export const ms = (x: number) => `${Math.round(x)}ms`;

// --- safety scale: 0% (safe) -> green, 50% -> amber, 100% -> red -------------
type RGB = { r: number; g: number; b: number };
const SAFE: RGB = { r: 0, g: 128, b: 0 }; // #008000 green (safe)
const MID: RGB = { r: 20, g: 144, b: 20 }; // #149014 green (mid)
const HOT: RGB = { r: 188, g: 71, b: 73 }; // #bc4749 red (danger)

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export function asrRGB(x: number): RGB {
  const v = Math.max(0, Math.min(1, x));
  const t = v < 0.5 ? v / 0.5 : (v - 0.5) / 0.5;
  const a = v < 0.5 ? SAFE : MID;
  const b = v < 0.5 ? MID : HOT;
  return { r: lerp(a.r, b.r, t), g: lerp(a.g, b.g, t), b: lerp(a.b, b.b, t) };
}

export function asrColor(x: number): string {
  const c = asrRGB(x);
  return `rgb(${Math.round(c.r)} ${Math.round(c.g)} ${Math.round(c.b)})`;
}

export function asrBg(x: number, alpha = 0.16): string {
  const c = asrRGB(x);
  return `rgba(${Math.round(c.r)}, ${Math.round(c.g)}, ${Math.round(c.b)}, ${alpha})`;
}

export const titleCase = (s: string) =>
  s.charAt(0).toUpperCase() + s.slice(1);
