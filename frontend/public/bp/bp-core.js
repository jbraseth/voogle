import { i as h, s as g, x as c, e as u, b as wr, n as l, a as sr, c as _, o as T, g as xr, f as Or, t as lr, d as Sr, h as Cr, j as M, A as Tr, k as Ar } from "./classroom-DB1AAjAg.js";
var Nr = Object.getOwnPropertyDescriptor, jr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Nr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = n(e) || e);
  return e;
};
let rr = class extends g {
  render() {
    return c`
      <figure>
        <blockquote>
          <slot></slot>
        </blockquote>

        <slot name="caption"></slot>
      </figure>
    `;
  }
};
rr.styles = h`
    :host {
      display: block;
      margin: var(--size-2) 0;
    }

    figure {
      box-shadow: inset var(--size-1) 0 0 -5px var(--color-black);
      padding: 0 0 0 var(--size-2);
      margin: 0;
      line-height: var(--line-height-normal);
    }

    blockquote {
      margin: 0;
    }

    ::slotted(p) {
      margin: var(--size-2) 0;
    }

    figcaption ::slotted(*) {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }
  `;
rr = jr([
  u("bp-blockquote")
], rr);
var Lr = Object.defineProperty, Ir = Object.getOwnPropertyDescriptor, kr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Ir(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Lr(t, o, e), e;
};
const Br = wr`<svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path d="m256 0c-141.4 0-256 114.6-256 256s114.6 256 256 256 256-114.6 256-256-114.6-256-256-256zm0 400c-18 0-32-14-32-32s13.1-32 32-32c17.1 0 32 14 32 32s-14.9 32-32 32zm69.1-142-45.1 28v2c0 13-11 24-24 24s-24-11-24-24v-16c0-8 4-16 12-21l57-34c7-4 11-11 11-19 0-12-10.9-22-22.9-22h-51.1c-12.9 0-22 10-22 22 0 13-11 24-24 24s-24-11-24-24c0-39 31-70 69.1-70h51.1c40.8 0 71.8 31 71.8 70 0 24-13 47-34.9 60z"/></svg>`;
let q = class extends g {
  constructor() {
    super(...arguments), this.intent = "question";
  }
  render() {
    return c`
      <div class="callout">
        ${Br}
        <aside>
          <slot></slot>
        </aside>
      </div>
    `;
  }
};
q.styles = h`
    :host {
      display: block;
      line-height: var(--line-height-normal);
      margin: var(--size-2) 0;
    }

    .callout {
      display: grid;
      grid-template-columns: var(--size-5) 1fr;
      column-gap: var(--size-1-5);
      align-items: center;
      border: 2px solid var(--color-black);
      border-radius: var(--radius-md);
      padding: var(--size-1-5);
    }
  `;
kr([
  l()
], q.prototype, "intent", 2);
q = kr([
  u("bp-callout")
], q);
var Mr = Object.getOwnPropertyDescriptor, Rr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Mr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = n(e) || e);
  return e;
};
let tr = class extends g {
  handleLinkClick(r) {
    globalThis.window.BibleProjectApp && r.preventDefault(), document.dispatchEvent(
      new CustomEvent("bp:external_link", {
        detail: {
          href: r.currentTarget.href
        }
      })
    );
  }
  handleSlotChange() {
    this.querySelectorAll("a").forEach((r) => {
      r.setAttribute("target", "_blank"), r.removeEventListener("click", this.handleLinkClick), r.addEventListener("click", this.handleLinkClick);
    });
  }
  render() {
    return c`
      <figcaption>
        <slot @slotchange=${this.handleSlotChange}></slot>
      </figcaption>
    `;
  }
};
tr.styles = h`
    :host {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }

    ::slotted(a) {
      color: inherit;
      text-decoration: underline;
    }
  `;
tr = Rr([
  u("bp-caption")
], tr);
var qr = Object.defineProperty, Hr = Object.getOwnPropertyDescriptor, zr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Hr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && qr(t, o, e), e;
};
let H = class extends g {
  handleClick(r) {
    globalThis.window.BibleProjectApp && r.preventDefault(), document.dispatchEvent(
      new CustomEvent("bp:external_link", {
        detail: { href: this.href }
      })
    );
  }
  render() {
    const r = this.href ? c`
          <a href="${this.href}" target="_blank" @click="${this.handleClick}">
            <slot></slot>
          </a>
        ` : c`<slot></slot>`;
    return c`<cite>${r}</cite>`;
  }
};
H.styles = h`
    cite {
      color: var(--bp-cite-color, var(--color-gray));
      font-size: inherit;
    }

    a {
      color: inherit;
      text-decoration: underline;
    }
  `;
zr([
  l()
], H.prototype, "href", 2);
H = zr([
  u("bp-cite")
], H);
var Vr = Object.getOwnPropertyDescriptor, Kr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Vr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = n(e) || e);
  return e;
};
const Ur = wr`
  <svg height="31" viewBox="0 0 34 31" width="34" xmlns="http://www.w3.org/2000/svg"><path d="m0 4.5c0-2.05078 1.64062-3.75 3.75-3.75h15c2.0508 0 3.75 1.69922 3.75 3.75v7.9102c-4.3359 1.2304-7.5 5.2148-7.5 9.9023 0 3.5156 1.6992 6.5625 4.2773 8.4375-.1757 0-.3515 0-.5273 0h-15c-2.10938 0-3.75-1.6406-3.75-3.75zm4.6875 5.625h13.125c.4687 0 .9375-.41016.9375-.9375 0-.46875-.4688-.9375-.9375-.9375h-13.125c-.52734 0-.9375.46875-.9375.9375 0 .52734.41016.9375.9375.9375zm0 3.75c-.52734 0-.9375.4688-.9375.9375 0 .5273.41016.9375.9375.9375h9.375c.4687 0 .9375-.4102.9375-.9375 0-.4687-.4688-.9375-.9375-.9375zm0 5.625c-.52734 0-.9375.4688-.9375.9375 0 .5273.41016.9375.9375.9375h5.625c.4687 0 .9375-.4102.9375-.9375 0-.4687-.4688-.9375-.9375-.9375zm12.1875 2.8125c0-4.6289 3.75-8.4375 8.4375-8.4375 4.6289 0 8.4375 3.8086 8.4375 8.4375 0 4.6875-3.8086 8.4375-8.4375 8.4375-4.6875 0-8.4375-3.75-8.4375-8.4375zm8.4375-2.8125c.7617 0 1.4063-.5859 1.4063-1.4062 0-.7618-.6446-1.4063-1.4063-1.4063-.8203 0-1.4063.6445-1.4063 1.4063 0 .8203.586 1.4062 1.4063 1.4062zm-.9375 3.75v2.8125c-.5273 0-.9375.4687-.9375.9375 0 .5273.4102.9375.9375.9375h1.875c.4688 0 .9375-.4102.9375-.9375 0-.4688-.4687-.9375-.9375-.9375v-3.75c0-.4687-.4688-.9375-.9375-.9375h-.9375c-.5273 0-.9375.4688-.9375.9375 0 .5273.4102.9375.9375.9375z" /></svg>
`;
let er = class extends g {
  render() {
    return c`
      <div class="empty-state">
        ${Ur}
        <slot></slot>
      </div>
    `;
  }
};
er.styles = h`
    :host {
      display: block;
      color: var(--color-gray);
    }

    .empty-state {
      background-color: var(--color-white);
      border-radius: var(--radius-md);
      border: 2px solid var(--color-neutral-10);
      padding: var(--size-4) var(--size-3);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: var(--size-1-5);
      font-weight: var(--font-weight-semibold);
      text-align: center;
    }

    svg {
      max-width: var(--size-5);
      max-height: var(--size-5);
      fill: currentColor;
    }
  `;
er = Kr([
  u("bp-empty-state")
], er);
var Yr = Object.defineProperty, Gr = Object.getOwnPropertyDescriptor, j = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Gr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Yr(t, o, e), e;
};
let z = class extends g {
  annotateTags(r, t) {
    let o = 1;
    const i = new RegExp(`<([^>]*)class="${r}"([^>]*)>`, "g");
    return t.replace(i, (e, a, n) => {
      let p = `<${a}class="${r}" data-id="${r}-${o}"${n}>`;
      return this.debug && (p += `<div class="group-debug-label">Id: ${r}-${o}</div>`), o += 1, p;
    });
  }
  get annotatedHtml() {
    let r = this.data ?? "";
    return r = this.annotateTags("group", r), r = this.annotateTags("group-title", r), r = r == null ? void 0 : r.replace("<bp-mark", "<bp-mark can-spotlight "), r;
  }
  render() {
    if (!this.data) return;
    const r = _({ debug: this.debug });
    return c`<div class="${r}">
      ${this.designTitle ? c`<div class="title">${this.designTitle}</div>` : null}
      ${this.reference ? c`<div class="reference">${this.reference}</div>` : null}
      <div class="design">${T(this.annotatedHtml)}</div>
    </div>`;
  }
};
z.styles = [
  sr,
  h`
      :host {
        display: block;
        white-space: nowrap;
        --group-body-font-size: 16px;
        --group-title-font-size: 14px;
        --title-font-size: 22px;
        --reference-font-size: 18px;
      }

      .design {
        overflow-x: auto;
        padding-bottom: var(--size-1);
      }

      .title {
        font-size: var(--title-font-size);
        font-weight: var(--font-weight-normal);
        line-height: var(--line-height-snug);
      }

      .reference {
        font-size: var(--reference-font-size);
        font-weight: var(--font-weight-bold);
        margin-bottom: var(--size-3);
      }

      .group-title {
        font-size: var(--group-title-font-size);
        font-weight: var(--font-weight-semibold);
        margin: var(--size-3) 0 var(--size-1);
      }

      .group-title[data-id="group-title-1"] {
        margin-top: 0;
      }

      .group {
        align-items: flex-start;
        display: flex;
        flex-direction: column;
        font-size: var(--group-body-font-size);
        white-space: nowrap;
        position: relative;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .arrow-bottom {
        background-color: var(--color-neutral-10);
        position: absolute;
        left: calc(var(--size-1) + 2px);
        top: var(--size-1);
        bottom: var(--size-0-5);
        width: 4px;
      }

      .arrow-top {
        position: absolute;
        left: var(--size-0-5);
        top: var(--size-0-5);
        bottom: var(--size-0-5);
        width: 0;
        height: 0;
        border-left: 8px solid transparent;
        border-right: 8px solid transparent;
        border-bottom: 8px solid var(--color-neutral-10);
      }

      .group:not(:has(.group)) {
        display: inline-block;
      }

      .group-debug-label {
        display: none;
      }
      .debug .group:hover {
        outline: 2px solid lightgrey;
      }
      .debug > .group:hover {
        outline: 2px solid white;
      }
      .debug .group:not(:has(.group:hover)):hover {
        outline: 2px solid red;
      }

      .debug .group:hover > .group-debug-label {
        font-size: 12px;
        font-weight: 700;
        z-index: 10;
        background-color: grey;
        color: white;
        display: block;
        position: absolute;
        left: 0;
        top: 0;
        padding: 2px;
      }
      .debug .group:not(:has(.group)):hover > .group-debug-label {
        left: calc(100% + 4px);
      }
      .debug .group:not(:has(.group:hover)):hover > .group-debug-label {
        background-color: red;
      }

      .group[indent="1"] {
        margin-inline-start: 10px;
      }
      .group[indent="2"] {
        margin-inline-start: 20px;
      }
      .group[indent="3"] {
        margin-inline-start: 30px;
      }
      .group[indent="4"] {
        margin-inline-start: 40px;
      }
      .group[indent="5"] {
        margin-inline-start: 50px;
      }
      .group[indent="6"] {
        margin-inline-start: 60px;
      }
      .group[indent="7"] {
        margin-inline-start: 70px;
      }
      .group[indent="8"] {
        margin-inline-start: 80px;
      }
      .group[indent="9"] {
        margin-inline-start: 90px;
      }
      .group[indent="10"] {
        margin-inline-start: 100px;
      }
      .group[indent="11"] {
        margin-inline-start: 110px;
      }
      .group[indent="12"] {
        margin-inline-start: 120px;
      }
      .group[indent="13"] {
        margin-inline-start: 130px;
      }
      .group[indent="14"] {
        margin-inline-start: 140px;
      }
      .group[indent="15"] {
        margin-inline-start: 150px;
      }
      .group[indent="16"] {
        margin-inline-start: 160px;
      }
      .group[indent="17"] {
        margin-inline-start: 170px;
      }
      .group[indent="18"] {
        margin-inline-start: 180px;
      }
      .group[indent="19"] {
        margin-inline-start: 190px;
      }
      .group[indent="20"] {
        margin-inline-start: 200px;
      }
      .group[indent="21"] {
        margin-inline-start: 210px;
      }
      .group[indent="22"] {
        margin-inline-start: 220px;
      }
      .group[indent="23"] {
        margin-inline-start: 230px;
      }
      .group[indent="24"] {
        margin-inline-start: 240px;
      }
      .group[indent="25"] {
        margin-inline-start: 250px;
      }
      .group[indent="26"] {
        margin-inline-start: 260px;
      }
      .group[indent="27"] {
        margin-inline-start: 270px;
      }
      .group[indent="28"] {
        margin-inline-start: 280px;
      }
      .group[indent="29"] {
        margin-inline-start: 290px;
      }
      .group[indent="30"] {
        margin-inline-start: 300px;
      }
      .group[indent="31"] {
        margin-inline-start: 310px;
      }
      .group[indent="32"] {
        margin-inline-start: 320px;
      }
      .group[indent="33"] {
        margin-inline-start: 330px;
      }
      .group[indent="34"] {
        margin-inline-start: 340px;
      }
      .group[indent="35"] {
        margin-inline-start: 350px;
      }
      .group[indent="36"] {
        margin-inline-start: 360px;
      }
      .group[indent="37"] {
        margin-inline-start: 370px;
      }
      .group[indent="38"] {
        margin-inline-start: 380px;
      }
      .group[indent="39"] {
        margin-inline-start: 390px;
      }
      .group[indent="40"] {
        margin-inline-start: 400px;
      }
      .group[indent="41"] {
        margin-inline-start: 410px;
      }
      .group[indent="42"] {
        margin-inline-start: 420px;
      }
      .group[indent="43"] {
        margin-inline-start: 430px;
      }
      .group[indent="44"] {
        margin-inline-start: 440px;
      }
      .group[indent="45"] {
        margin-inline-start: 450px;
      }
      .group[indent="46"] {
        margin-inline-start: 460px;
      }
      .group[indent="47"] {
        margin-inline-start: 470px;
      }
      .group[indent="48"] {
        margin-inline-start: 480px;
      }
      .group[indent="49"] {
        margin-inline-start: 490px;
      }
      .group[indent="50"] {
        margin-inline-start: 500px;
      }
    `
];
j([
  l()
], z.prototype, "reference", 2);
j([
  l({ attribute: "title" })
], z.prototype, "designTitle", 2);
j([
  l({ attribute: "data" })
], z.prototype, "data", 2);
j([
  l({ type: Boolean, attribute: "debug" })
], z.prototype, "debug", 2);
z = j([
  u("bp-ephesians-literary-design")
], z);
function Wr(r) {
  var o;
  const t = (o = r.trim().match(/^((?<miliseconds>[0-9]+)ms)|((?<seconds>[0-9]+)s)$/)) == null ? void 0 : o.groups;
  return t != null && t.miliseconds ? Number(t == null ? void 0 : t.miliseconds) : t != null && t.seconds ? Number(t == null ? void 0 : t.seconds) * 1e3 : 0;
}
var Fr = Object.defineProperty, Xr = Object.getOwnPropertyDescriptor, C = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Xr(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Fr(t, o, e), e;
};
let w = class extends g {
  constructor() {
    super(...arguments), this.color = "yellow", this.userRevealTime = 1, this.noAnimation = !1, this.show = !1, this.revealTime = 1, this.shouldResetState = !1, this.shownState = "initHidden", this.resetStateTimeoutId = null;
  }
  resetShownState() {
    const r = Wr(
      globalThis.window.getComputedStyle(this).getPropertyValue("--duration-x-long")
    ), t = this.revealTime * r + 50;
    this.resetStateTimeoutId = setTimeout(() => {
      this.shouldResetState = !0, this.requestUpdate();
    }, t);
  }
  willUpdate(r) {
    if (r.has("show") && (this.shouldResetState = !1, this.resetStateTimeoutId && clearTimeout(this.resetStateTimeoutId)), this.shouldResetState) {
      this.revealTime = 0, this.shownState = "initHidden", this.shouldResetState = !1;
      return;
    }
    this.noAnimation ? this.revealTime = 0 : this.userRevealTime && (this.revealTime = this.userRevealTime), this.shownState = this.show ? "shown" : this.lastState === "shown" ? "hiddenAfterShown" : "initHidden", this.shownState === "hiddenAfterShown" && this.resetShownState();
  }
  render() {
    const r = _("highlight", this.color, this.shownState, {
      "can-spotlight": this.canSpotlight
    }), t = `--reveal-time: calc(${this.revealTime} * var(--duration-x-long))`;
    return c`<span class="${r}" style="${t}"><slot></slot></span>`;
  }
  updated() {
    this.lastState = this.shownState;
  }
};
w.styles = h`
    :host {
      --reveal-time: var(--duration-x-long);
      --left-gradient-color: var(--color-highlight-yellow-1);
      --right-gradient-color: var(--color-highlight-yellow-2);
    }

    .highlight {
      transition: background-position var(--reveal-time);
      background-color: none;
      background: linear-gradient(
        90deg,
        var(--left-gradient-color) 1.46%,
        var(--right-gradient-color) 50%,
        rgba(255, 255, 255, 0) 50%
      );
      background-size: 201% 100%;
      background-position: 100% 0;
    }

    .can-spotlight {
      color: var(--color-black);
      transition:
        color var(--spotlight-transition-duration),
        background var(--spotlight-transition-duration);
    }

    .highlight.shown {
      background-position: 0 0;
    }

    .highlight.hiddenAfterShown {
      background-position: -99% 0;
    }

    .highlight.pink {
      --left-gradient-color: var(--color-highlight-pink-1);
      --right-gradient-color: var(--color-highlight-pink-2);
    }

    .highlight.orange {
      --left-gradient-color: var(--color-highlight-orange-1);
      --right-gradient-color: var(--color-highlight-orange-2);
    }

    .highlight.blue {
      --left-gradient-color: var(--color-highlight-blue-1);
      --right-gradient-color: var(--color-highlight-blue-2);
    }

    .highlight.green {
      --left-gradient-color: var(--color-highlight-green-1);
      --right-gradient-color: var(--color-highlight-green-2);
    }
  `;
C([
  l({ attribute: "color" })
], w.prototype, "color", 2);
C([
  l({ type: Number, attribute: "reveal-time" })
], w.prototype, "userRevealTime", 2);
C([
  l({
    type: Boolean,
    attribute: "no-animation"
  })
], w.prototype, "noAnimation", 2);
C([
  l({ type: Boolean, attribute: "can-spotlight" })
], w.prototype, "canSpotlight", 2);
C([
  l({
    type: Boolean,
    attribute: "show"
  })
], w.prototype, "show", 2);
w = C([
  u("bp-highlight")
], w);
const Qr = "0.24.0", Jr = Qr;
window.matchMedia(
  "(min-width: 480px)"
  /* sm */
);
window.matchMedia(
  "(min-width: 768px)"
  /* md */
);
window.matchMedia(
  "(min-width: 1024px)"
  /* lg */
);
window.matchMedia(
  "(min-width: 1280px)"
  /* xl */
);
window.matchMedia("(prefers-reduced-motion: reduce)");
const Zr = (r, t) => t.some((o) => r instanceof o);
let vr, br;
function rt() {
  return vr || (vr = [
    IDBDatabase,
    IDBObjectStore,
    IDBIndex,
    IDBCursor,
    IDBTransaction
  ]);
}
function tt() {
  return br || (br = [
    IDBCursor.prototype.advance,
    IDBCursor.prototype.continue,
    IDBCursor.prototype.continuePrimaryKey
  ]);
}
const $r = /* @__PURE__ */ new WeakMap(), or = /* @__PURE__ */ new WeakMap(), _r = /* @__PURE__ */ new WeakMap(), X = /* @__PURE__ */ new WeakMap(), cr = /* @__PURE__ */ new WeakMap();
function et(r) {
  const t = new Promise((o, i) => {
    const e = () => {
      r.removeEventListener("success", a), r.removeEventListener("error", n);
    }, a = () => {
      o(y(r.result)), e();
    }, n = () => {
      i(r.error), e();
    };
    r.addEventListener("success", a), r.addEventListener("error", n);
  });
  return t.then((o) => {
    o instanceof IDBCursor && $r.set(o, r);
  }).catch(() => {
  }), cr.set(t, r), t;
}
function ot(r) {
  if (or.has(r))
    return;
  const t = new Promise((o, i) => {
    const e = () => {
      r.removeEventListener("complete", a), r.removeEventListener("error", n), r.removeEventListener("abort", n);
    }, a = () => {
      o(), e();
    }, n = () => {
      i(r.error || new DOMException("AbortError", "AbortError")), e();
    };
    r.addEventListener("complete", a), r.addEventListener("error", n), r.addEventListener("abort", n);
  });
  or.set(r, t);
}
let ir = {
  get(r, t, o) {
    if (r instanceof IDBTransaction) {
      if (t === "done")
        return or.get(r);
      if (t === "objectStoreNames")
        return r.objectStoreNames || _r.get(r);
      if (t === "store")
        return o.objectStoreNames[1] ? void 0 : o.objectStore(o.objectStoreNames[0]);
    }
    return y(r[t]);
  },
  set(r, t, o) {
    return r[t] = o, !0;
  },
  has(r, t) {
    return r instanceof IDBTransaction && (t === "done" || t === "store") ? !0 : t in r;
  }
};
function it(r) {
  ir = r(ir);
}
function at(r) {
  return r === IDBDatabase.prototype.transaction && !("objectStoreNames" in IDBTransaction.prototype) ? function(t, ...o) {
    const i = r.call(Q(this), t, ...o);
    return _r.set(i, t.sort ? t.sort() : [t]), y(i);
  } : tt().includes(r) ? function(...t) {
    return r.apply(Q(this), t), y($r.get(this));
  } : function(...t) {
    return y(r.apply(Q(this), t));
  };
}
function nt(r) {
  return typeof r == "function" ? at(r) : (r instanceof IDBTransaction && ot(r), Zr(r, rt()) ? new Proxy(r, ir) : r);
}
function y(r) {
  if (r instanceof IDBRequest)
    return et(r);
  if (X.has(r))
    return X.get(r);
  const t = nt(r);
  return t !== r && (X.set(r, t), cr.set(t, r)), t;
}
const Q = (r) => cr.get(r);
function st(r, t, { blocked: o, upgrade: i, blocking: e, terminated: a } = {}) {
  const n = indexedDB.open(r, t), p = y(n);
  return i && n.addEventListener("upgradeneeded", (s) => {
    i(y(n.result), s.oldVersion, s.newVersion, y(n.transaction), s);
  }), o && n.addEventListener("blocked", (s) => o(
    // Casting due to https://github.com/microsoft/TypeScript-DOM-lib-generator/pull/1405
    s.oldVersion,
    s.newVersion,
    s
  )), p.then((s) => {
    a && s.addEventListener("close", () => a()), e && s.addEventListener("versionchange", (d) => e(d.oldVersion, d.newVersion, d));
  }).catch(() => {
  }), p;
}
const lt = ["get", "getKey", "getAll", "getAllKeys", "count"], ct = ["put", "add", "delete", "clear"], J = /* @__PURE__ */ new Map();
function fr(r, t) {
  if (!(r instanceof IDBDatabase && !(t in r) && typeof t == "string"))
    return;
  if (J.get(t))
    return J.get(t);
  const o = t.replace(/FromIndex$/, ""), i = t !== o, e = ct.includes(o);
  if (
    // Bail if the target doesn't exist on the target. Eg, getAll isn't in Edge.
    !(o in (i ? IDBIndex : IDBObjectStore).prototype) || !(e || lt.includes(o))
  )
    return;
  const a = async function(n, ...p) {
    const s = this.transaction(n, e ? "readwrite" : "readonly");
    let d = s.store;
    return i && (d = d.index(p.shift())), (await Promise.all([
      d[o](...p),
      e && s.done
    ]))[0];
  };
  return J.set(t, a), a;
}
it((r) => ({
  ...r,
  get: (t, o, i) => fr(t, o) || r.get(t, o, i),
  has: (t, o) => !!fr(t, o) || r.has(t, o)
}));
const dt = "bp_web_components", pt = 1, Z = "expires", ht = 2;
class gt {
  constructor(t) {
    this.debug = xr("DEBUG"), this.connection = null, this.name = t.name;
  }
  /**
   * Opens a connection to an IndexedDB database and returns
   * an object store.
   */
  async getDatabase() {
    return this.connection || (this.connection = st(dt, pt, {
      upgrade: (t) => {
        t.createObjectStore(this.name).createIndex(Z, Z);
      }
    })), this.connection.then((t) => this.cleanUp(t));
  }
  /**
   * Removes expired items from the store.
   */
  async cleanUp(t) {
    const o = IDBKeyRange.upperBound(Date.now());
    let i = await t.transaction(this.name, "readwrite").store.index(Z).openCursor(o);
    for (; i; )
      await i.delete(), i = await i.continue();
    return t;
  }
  /**
   * Attempts to perform an IndexedDB transaction. Retries if
   * the transaction fails, usually because the connection was closed.
   * @see https://bugs.webkit.org/show_bug.cgi?id=197050
   */
  async attemptTransaction(t) {
    let o = 0;
    const i = async (e, a) => this.getDatabase().then(t).then(e).catch(async (n) => {
      if (++o > ht) {
        a(n);
        return;
      }
      return this.getDatabase().then((p) => (p.close(), this.connection = null, i(e, a))).catch(a);
    });
    return new Promise(i);
  }
  /**
   * Puts an item into the store.
   */
  async put(t, o) {
    return this.attemptTransaction((i) => i.put(this.name, o, t)).catch(
      (i) => {
        this.debug && console.error(i);
      }
    );
  }
  /**
   * Retrieves an item from the store.
   */
  async get(t) {
    return this.attemptTransaction(
      (o) => o.get(this.name, t)
    ).catch((o) => {
      this.debug && console.error(o);
    });
  }
  /**
   * Clears all records from the store.
   */
  async clear() {
    return this.attemptTransaction((t) => t.clear(this.name)).catch(
      (t) => {
        this.debug && console.error(t);
      }
    );
  }
}
const ut = 1e3 * 60 * 60 * 24 * 90, R = /* @__PURE__ */ new Map(), mr = new gt({ name: "icons" });
function vt(r) {
  var i;
  const { set: t = "regular", name: o } = ((i = r.match(/((?<set>.+):)?(?<name>.+)/)) == null ? void 0 : i.groups) ?? {};
  return { set: t, name: o };
}
async function bt(r) {
  const { set: t, name: o } = vt(r), i = `${t}:${o}:${Jr}`, e = await mr.get(i);
  if (e)
    return e.value;
  let a;
  const n = `/icons/${t}/${o}.svg`;
  return R.has(n) ? a = R.get(n) : (a = Or(n), R.set(n, a)), a.then((p) => (mr.put(i, {
    expires: Date.now() + ut,
    value: p
  }).then(() => {
    R.delete(n);
  }).catch(() => {
  }), p));
}
var ft = Object.defineProperty, mt = Object.getOwnPropertyDescriptor, U = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? mt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && ft(t, o, e), e;
};
let P = class extends g {
  updated(r) {
    !r.has("icon") || !this.icon || bt(this.icon).then((t) => {
      this.xml = t;
    });
  }
  render() {
    return this.xml ? T(this.xml) : c` <slot></slot> `;
  }
};
P.styles = h`
    :host {
      display: inline-flex;
      fill: var(--icon-color, currentColor);
      height: var(--icon-size, var(--size-2-5));
      width: var(--icon-size, var(--size-2-5));
    }

    :host([size="sm"]) {
      --icon-size: var(--size-2);
    }

    :host([size="lg"]) {
      --icon-size: var(--size-3);
    }

    :host([size="xl"]) {
      --icon-size: var(--size-4);
    }

    :host([size="2xl"]) {
      --icon-size: var(--size-5);
    }

    svg {
      display: block;
      width: 100%;
      height: 100%;
    }
  `;
U([
  l()
], P.prototype, "icon", 2);
U([
  l()
], P.prototype, "size", 2);
U([
  lr()
], P.prototype, "xml", 2);
P = U([
  u("bp-icon")
], P);
var yt = Object.defineProperty, wt = Object.getOwnPropertyDescriptor, L = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? wt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && yt(t, o, e), e;
};
const v = "bp-literary-design", xt = /* @__PURE__ */ new Set([
  "book",
  "cell",
  "chapter",
  "char",
  "figure",
  "group",
  "note",
  "optbreak",
  "para",
  "ref",
  "row",
  "sidebar",
  "table",
  "usx",
  "verse"
]);
let $ = class extends g {
  constructor() {
    super(...arguments), this.contentRef = Sr(), this.excludedKeyPaths = "[]";
  }
  parseScript(r) {
    var a, n, p, s, d;
    const i = new DOMParser().parseFromString(r ?? "", "text/xml").firstElementChild;
    if (!i || i.tagName !== "usx")
      throw new Error(`${v}: Missing required <usx> tag`);
    const e = Pr(
      i,
      (k) => k.nodeType === Node.ELEMENT_NODE && xt.has(k.nodeName) ? document.createElement(`${v}-${k.nodeName}`) : k.cloneNode(),
      (k, f) => f.name === "id" ? yr("data-id", f.value) : f.name === "style" ? yr(
        "data-style",
        f.value.split(" ").map((I) => `_${I}_`).join(" ")
      ) : f.cloneNode(!0)
    );
    kt(e, `${v}-group`.toUpperCase()), (p = (n = (a = this.contentRef) == null ? void 0 : a.value) == null ? void 0 : n.lastChild) == null || p.remove(), (d = (s = this.contentRef) == null ? void 0 : s.value) == null || d.appendChild(e);
  }
  firstUpdated(r) {
    r.has("usx") && this.usx && this.parseScript(this.usx);
  }
  willUpdate(r) {
    r.has("usx") && this.parseScript(this.usx ?? "");
  }
  getElementById(r) {
    var t;
    return ((t = this.shadowRoot) == null ? void 0 : t.querySelector(`[data-id="${r}"]`)) ?? null;
  }
  getElementByKeyPath(r) {
    var t;
    return ((t = this.shadowRoot) == null ? void 0 : t.querySelector(`[data-key-path="${r}"]`)) ?? null;
  }
  removeElementByKeyPath(r) {
    var o, i, e;
    const t = (o = this.shadowRoot) == null ? void 0 : o.querySelector(
      `[data-key-path="${r}"]`
    );
    t && (t.classList.add("hidden-group"), ((i = t.nextElementSibling) == null ? void 0 : i.nodeName) === "BP-LITERARY-DESIGN-OPTBREAK" && t.nextElementSibling.classList.add("hidden-group"), ((e = t.previousElementSibling) == null ? void 0 : e.nodeName) === "BP-LITERARY-DESIGN-OPTBREAK" && t.previousElementSibling.classList.add("hidden-group"));
  }
  updated() {
    var t, o, i;
    (t = this.shadowRoot) == null || t.querySelectorAll(".hidden-group").forEach((e) => e.classList.remove("hidden-group")), console.log("Excluded paths", this.excludedKeyPaths), (((i = (o = this.excludedKeyPaths.match(/\[(?<stringArray>.*)\]/)) == null ? void 0 : o.groups) == null ? void 0 : i.stringArray.split(",").map((e) => e.trim())) ?? []).forEach((e) => this.removeElementByKeyPath(e));
  }
  render() {
    return c`
      <div>
        ${this.designTitle ? c`<div class="title">${this.designTitle}</div>` : c`<div class="design-start"></div>`}
        ${this.reference ? c`<div class="reference">${this.reference}</div>` : null}
        <div ${Cr(this.contentRef)}></div>
        <slot name="caption"></slot>
      </div>
    `;
  }
};
$.styles = [
  sr,
  h`
      :host {
        --title-font-size: 22px;
        --reference-font-size: 18px;
      }

      bp-literary-design-usx {
        --group-sidebar-color-offset: 6px;
        --group-sidebar-color-width: 4px;
        --group-sidebar-value-offset: 8px;
        --group-body-font-size: 16px;
        --group-title-font-size: 14px;
        --group-sidebar-font-size: 13px;
        --verse-font-size: 12px;
        line-height: var(--line-height-normal);
      }

      /* Used because otherwise pseudo-elements will not be included
        in height calculation when no title. */
      .design-start {
        height: 1px;
      }

      .title {
        font-size: var(--title-font-size);
        font-weight: var(--font-weight-normal);
        line-height: var(--line-height-snug);
      }

      .reference {
        font-size: var(--reference-font-size);
        font-weight: var(--font-weight-bold);
      }

      .hidden-group {
        display: none;
      }

      .hidden-optbreak {
        display: none;
      }

      bp-literary-design-para {
        display: block;
      }

      bp-literary-design-group {
        font-size: var(--group-body-font-size);
        border-radius: var(--radius-lg);
        display: block;
        padding: 0;
        position: relative;
      }

      bp-literary-design-group[title] {
        margin-top: var(--group-title-height);
      }

      bp-literary-design-group[type="primary"],
      bp-literary-design-group[type="primary-alt"],
      bp-literary-design-group[type="secondary"] {
        box-sizing: border-box;
        margin: var(--size-1-5) 0;
        padding: var(--size-1-5);
      }

      bp-literary-design-group[type="primary-alt"] {
        padding: var(--size-1-5) 0 0;
      }

      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="primary"],
      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="primary-alt"],
      bp-literary-design-group
        > bp-literary-design-group:last-of-type[type="secondary"] {
        margin-bottom: 0;
      }

      bp-literary-design-group[type="primary"][title],
      bp-literary-design-group[type="primary-alt"][title],
      bp-literary-design-group[type="secondary"][title] {
        border-radius: 0 var(--radius-lg) var(--radius-lg) var(--radius-lg);
        margin-top: calc(var(--group-title-height) + var(--size-1-5));
      }

      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="primary"][title],
      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="primary-alt"][title],
      bp-literary-design-group
        > bp-literary-design-group:first-of-type[type="secondary"][title] {
        margin-top: var(--group-title-height);
      }

      bp-literary-design-group[type="primary-alt"][title] {
        border-radius: 0;
      }

      bp-literary-design-group[type="primary"][title]::before,
      bp-literary-design-group[type="primary-alt"][title]::before,
      bp-literary-design-group[type="secondary"][title]::before,
      bp-literary-design-group[type="bare"][title]::before {
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        bottom: 100%;
        box-sizing: border-box;
        content: attr(title);
        display: block;
        font-size: var(--group-title-font-size);
        font-weight: var(--font-weight-semibold);
        left: -2px;
        margin-right: var(--size-2);
        padding: var(--size-0-5) var(--size-1);
        position: absolute;
        z-index: 1;
      }

      bp-literary-design-group[type="bare"][title]::before {
        padding: var(--size-0-5) 0;
      }

      bp-literary-design-group::before {
        transition:
          color var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration);
      }

      bp-literary-design-group[type="primary"][title]::before {
        color: white;
        background-color: var(--color-black);
      }

      bp-literary-design-group[type="primary-alt"][title]::before {
        color: var(--color-black);
        padding: var(--size-0-5) var(--size-0-5);
      }

      bp-literary-design-group[type="secondary"][title]::before {
        background-color: var(--color-neutral-10);
        color: var(--color-black);
      }

      bp-literary-design-group {
        color: var(--color-black);
        transition:
          color var(--spotlight-transition-duration),
          border var(--spotlight-transition-duration);
      }

      bp-literary-design-group[type="primary"] {
        border: 2px solid var(--color-black);
      }

      bp-literary-design-group[type="primary-alt"] {
        border-top: 2px solid var(--color-black);
        border-radius: 0px;
      }

      bp-literary-design-group[type="secondary"] {
        border: 2px solid var(--color-neutral-10);
      }

      bp-literary-design-group::after {
        transition: background var(--spotlight-transition-duration);
      }

      bp-literary-design-group[sidebar-color]::after {
        background: var(--color-black);
        border-radius: 100px;
        bottom: 0;
        content: "";
        display: block;
        inset-inline-start: 0;
        position: absolute;
        top: 0;
        transform: translateX(calc(-100% - var(--group-sidebar-color-offset)));
        width: var(--group-sidebar-color-width);
      }

      [dir="rtl"] bp-literary-design-group[sidebar-color]::after {
        transform: translateX(calc(100% + var(--group-sidebar-color-offset)));
      }

      bp-literary-design-group[sidebar-color="red"]::after {
        background: var(--color-red-50);
      }

      bp-literary-design-group[sidebar-color="orange"]::after {
        background: var(--color-orange-50);
      }

      bp-literary-design-group[sidebar-color="green"]::after {
        background: var(--color-green-50);
      }

      bp-literary-design-group[sidebar-color="turquoise"]::after {
        background: var(--color-turquoise-50);
      }

      bp-literary-design-group[sidebar-color="cyan"]::after {
        background: var(--color-cyan-50);
      }

      bp-literary-design-group[sidebar-color="blue"]::after {
        background: var(--color-blue-50);
      }

      bp-literary-design-group[sidebar-color="violet"]::after {
        background: var(--color-violet-50);
      }

      bp-literary-design-group[sidebar-color="purple"]::after {
        background: var(--color-purple-50);
      }

      bp-literary-design-group[sidebar-color="tan"]::after {
        background: var(--color-tan-50);
      }

      bp-literary-design-group[indent="1"] {
        margin-inline-start: 1.5rem;
      }

      bp-literary-design-group[indent="2"] {
        margin-inline-start: 3rem;
      }

      bp-literary-design-group[indent="3"] {
        margin-inline-start: 4.5rem;
      }

      bp-literary-design-group[indent="4"] {
        margin-inline-start: 6rem;
      }

      bp-literary-design-group[indent="5"] {
        margin-inline-start: 7.5rem;
      }

      bp-literary-design-group-sidebar-value {
        transition: color var(--spotlight-transition-duration);
        color: var(--color-gray);
        font-size: var(--group-sidebar-font-size);
        display: block;
        inset-inline-start: 0;
        padding-bottom: 2px;
        position: absolute;
        top: 50%;
        transform: translate(
          calc(-100% - var(--group-sidebar-value-offset)),
          -50%
        );
      }

      [dir="rtl"] bp-literary-design-group-sidebar-value {
        transform: translate(
          calc(100% + var(--group-sidebar-value-offset)),
          -50%
        );
      }

      bp-literary-design-group[sidebar-color]
        bp-literary-design-group-sidebar-value {
        transform: translate(
          calc(
            -100% - var(--group-sidebar-color-width) - var(
                --group-sidebar-color-offset
              ) - var(--group-sidebar-value-offset)
          ),
          -50%
        );
      }

      bp-literary-design-char {
        transition: color var(--spotlight-transition-duration);
        color: var(--color-black);
      }

      bp-literary-design-char[data-style="_em_"] {
        color: inherit;
        font-style: italic;
      }

      bp-literary-design-verse {
        font-size: var(--verse-font-size);
        vertical-align: 4px;
      }

      bp-literary-design-optbreak {
        transition: border var(--spotlight-transition-duration);
        border-bottom: 2px solid var(--color-neutral-10);
        display: block;
        margin: var(--size-1-5) 0;
      }

      bp-literary-design-note {
        display: none;
      }

      bp-literary-design-word-transliteration {
        font-style: italic;
      }

      bp-literary-design-word {
        white-space: nowrap;
      }
    `
];
L([
  l()
], $.prototype, "reference", 2);
L([
  l({ attribute: "title" })
], $.prototype, "designTitle", 2);
L([
  l({ attribute: "excluded-key-paths" })
], $.prototype, "excludedKeyPaths", 2);
L([
  l({ attribute: "usx" })
], $.prototype, "usx", 2);
$ = L([
  u(v)
], $);
window.customElements.define(
  `${v}-group`,
  class extends HTMLElement {
    connectedCallback() {
      if (this.hasAttribute("title") && this.style.setProperty(
        "--group-title-height",
        window.getComputedStyle(this, ":before").height
      ), this.hasAttribute("sidebar-value")) {
        const r = document.createElement(
          `${v}-group-sidebar-value`
        );
        r.innerText = this.getAttribute("sidebar-value"), this.insertBefore(r, this.firstChild);
      }
    }
  }
);
window.customElements.define(
  `${v}-verse`,
  class extends HTMLElement {
    connectedCallback() {
      const r = this.getAttribute("number") ?? "";
      this.innerText = r;
    }
  }
);
window.customElements.define(
  `${v}-char`,
  class extends HTMLElement {
    connectedCallback() {
      const r = this.getAttribute("word-lang"), t = this.getAttribute("word-original"), o = this.getAttribute("word-transliteration");
      if (t || o) {
        const s = [];
        if (t && s.push(
          `<bp-text-${r}>${t}</bp-text-${r}>`
        ), o && s.push(
          `<${v}-word-transliteration>${o}</${v}-word-transliteration>`
        ), s.length) {
          const d = document.createElement(`${v}-word`);
          d.innerHTML = `&nbsp;(${s.join(" • ")})`, this.appendChild(d);
        }
      }
      const i = this.getAttribute("highlight-show"), e = this.getAttribute("highlight-color"), a = this.getAttribute("highlight-reveal-time");
      if (i || a || e) {
        const s = document.createElement("bp-highlight");
        a && s.setAttribute("reveal-time", a), e && s.setAttribute("color", e), s.setAttribute("can-spotlight", "true"), s.setAttribute("show", i ?? "false"), s.setAttribute("data-id", this.getAttribute("data-id") ?? ""), this.setAttribute("data-id", "");
        for (const d of Array.from(this.childNodes))
          s.appendChild(d);
        this.appendChild(s);
      }
      const n = this.getAttribute("mark-variant"), p = this.getAttribute("mark-color");
      if (n || p) {
        const s = document.createElement("bp-mark");
        s.setAttribute("color", p ?? ""), s.setAttribute("variant", n ?? "");
        for (const d of Array.from(this.childNodes))
          s.appendChild(d);
        this.appendChild(s);
      }
    }
  }
);
function yr(r, t) {
  const o = document.createAttribute(r);
  return o.value = t, o;
}
function kt(r, t) {
  const o = document.createTreeWalker(r, NodeFilter.SHOW_ELEMENT);
  let i = null, e = null, a = [];
  const n = /* @__PURE__ */ new Map(), p = () => a.map((d) => d.value).join("."), s = () => "group-" + a.map((d) => d.value).join("-");
  for (; o.nextNode(); ) {
    if (o.currentNode.nodeName !== t) continue;
    const d = o.currentNode.parentNode;
    !i || d !== i ? (d && n.has(d) ? (a = a.slice(0, (n.get(d) ?? 0) + 1), a[a.length - 1].value += 1) : (!e || !e.contains(o.currentNode) ? (a.length ? (a = a.slice(0, 1), a[a.length - 1].value += 1) : a.push({ value: 1 }), e = d) : a.push({ value: 1 }), d && n.set(d, a.length - 1)), i = d) : a[a.length - 1].value += 1, o.currentNode.setAttribute(
      "data-key-path",
      p()
    ), o.currentNode.setAttribute("data-id", s());
  }
}
function Pr(r, t, o) {
  const i = t(r);
  if (r.childNodes.forEach((e) => {
    i.appendChild(Pr(e, t, o));
  }), r.nodeType === Node.ELEMENT_NODE && i.nodeType === Node.ELEMENT_NODE) {
    const e = r, a = i;
    for (let n = 0, p = e.attributes.length; n < p; n++) {
      const s = e.attributes.item(n);
      if (!s) continue;
      const d = o(r, s);
      d && a.setAttributeNode(d);
    }
  }
  return i;
}
var zt = Object.defineProperty, $t = Object.getOwnPropertyDescriptor, Er = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? $t(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && zt(t, o, e), e;
};
let V = class extends g {
  renderGroup(r, t, o, i = 0) {
    var f, I, hr, gr;
    const e = _("group", {
      leaf: !((f = r.subgroups) != null && f.length),
      "has-detail-list": (I = r.detailList) == null ? void 0 : I.length,
      "has-title": r.title,
      "fill-background": r.fillBackground
    }), a = r.reference ? c`<div class="reference">
          <bp-mark color="${r.markColor}" variant="${r.markVariant}">
            ${r.reference}
          </bp-mark>
        </div>` : "", n = r.title ? c`<div class="title">${T(r.title)}</div>` : "", p = _("detail-list", r.detailListType), s = (hr = r.detailList) != null && hr.length ? c`<div class="${p}">
          <ol>
            ${r.detailList.map((B) => {
      const m = B, ur = r.detailListType == "custom" && m.ref ? c`<span class="li-ref">${m.ref}</span> ` : "";
      return m ? c`<li
                data-indent="${m.indent ?? 0}"
                value="${m.tag ?? ""}"
              >
                ${t == "vertical" ? ur : ""}
                <span class="li-detail">
                  ${t == "horizontal" ? ur : ""}
                  ${T(m.detail ?? B)}</span
                >
              </li>` : null;
    })}
          </ol>
        </div>` : "", d = (gr = r.subgroups) != null && gr.length ? c`<div class="subgroups">
          ${r.subgroups.map(
      (B, m) => this.renderGroup(
        B,
        t,
        `${o}-${m + 1}`,
        i + 1
      )
    )}
        </div>` : "", k = r.tag ? c`<div class="tag">${r.tag}</div>` : "";
    return c`<div
      class="${e}"
      data-mark-color="${r.markColor}"
      data-mark-variant="${r.markVariant}"
      data-id="group-${o}"
      data-indent="${r.indent}"
      data-depth=${i}
    >
      ${a} ${n} ${s} ${d} ${k}
    </div>`;
  }
  render() {
    var t, o;
    if (!((o = (t = this.data) == null ? void 0 : t.groups) != null && o.length)) return;
    const r = _("container", this.data.direction);
    return c`<div class="${r}">
      ${this.data.groups.map(
      (i, e) => {
        var a;
        return this.renderGroup(i, ((a = this.data) == null ? void 0 : a.direction) ?? "", `${e + 1}`);
      }
    )}
    </div>`;
  }
};
V.styles = [
  sr,
  h`
      :host {
        /* Prevent text contents from being resized by slide. */
        --font-size-xs: 13px;
        --font-size-sm: 14px;
        --font-size-md: 16px;
        --font-size-lg: 18px;
        --font-size-xl: 20px;
      }

      .container {
        display: flex;
        flex-direction: row;
        gap: var(--size-1);
        padding: var(--size-1);
      }

      .container.vertical {
        width: var(--vertical-width);
        flex-direction: column;
      }

      .group {
        --border-color: var(--color-black);
        --indent: 0px;
        position: relative;
        padding: var(--size-1);
        border-radius: var(--radius-md);
        border: 2px solid var(--border-color);
        gap: var(--size-0-5);
        display: flex;
        flex-direction: column;
        margin-top: var(--indent);
        transition:
          color var(--spotlight-transition-duration),
          border var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration);
      }

      .vertical .group {
        align-content: start;
        margin-top: unset;
        margin-inline-start: var(--indent);
      }

      .leaf {
        width: var(--size-10);
        min-height: calc(var(--size-25) - var(--indent));
      }

      .leaf.has-detail-list {
        min-width: var(--size-20);
        width: var(--size-20);
      }

      .leaf.has-title {
        min-width: var(--size-15);
        width: var(--size-15);
      }

      .leaf.has-detail-list.has-title {
        min-width: var(--size-20);
        width: var(--size-20);
      }

      .vertical .leaf {
        min-height: unset;
        width: unset;
      }

      .vertical .leaf.has-detail-list.has-title {
        min-height: unset;
        width: unset;
      }

      .title {
        font-weight: var(--font-weight-semibold);
        hyphens: auto;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .detail-list {
        font-size: var(--font-size-sm);
        line-height: var(--line-height-normal);
        hyphens: auto;
        color: var(--color-black);
        transition: color var(--spotlight-transition-duration);
      }

      .detail-list ol {
        margin: var(--size-1) 0 var(--size-1) -26px;
        list-style: disc;
      }

      .detail-list.custom ol {
        margin-left: -32px;
        list-style: none;
      }

      .detail-list.custom li {
        display: flex;
      }

      .detail-list.custom li::before {
        padding-right: 5px;
        white-space: nowrap;
      }

      .custom li::before {
        content: attr(value) " -";
      }

      .custom li[value=""]::before {
        content: "•";
        font-size: 22px;
        line-height: 23px;
        margin-top: -2px;
        margin-right: 4px;
        margin-left: -1px;
      }

      .detail-list.custom li[data-indent="1"] {
        padding-left: var(--size-2);
      }

      .detail-list.custom li[data-indent="2"] {
        padding-left: var(--size-4);
      }

      .detail-list.custom li[data-indent="3"] {
        padding-left: var(--size-6);
      }

      .li-ref {
        white-space: nowrap;
        margin-right: 4px;
        font-weight: var(--font-weight-semibold);
      }

      .li-detail {
        word-wrap: break-word;
        min-width: var(--size-1);
      }

      .group[data-indent="1"] {
        --indent: var(--size-3);
      }

      .group[data-indent="2"] {
        --indent: var(--size-6);
      }

      .group[data-indent="3"] {
        --indent: var(--size-9);
      }

      .group[data-indent="4"] {
        --indent: var(--size-12);
      }

      .group[data-indent="5"] {
        --indent: var(--size-15);
      }

      .group[data-indent="6"] {
        --indent: calc(var(--size-15) + var(--size-3));
      }

      .group[data-indent="7"] {
        --indent: calc(var(--size-15) + var(--size-6));
      }

      .subgroups {
        padding-top: var(--size-0-5);
        display: flex;
        flex-direction: row;
        gap: var(--size-1);
        flex-grow: 1;
      }

      .vertical .subgroups {
        flex-direction: column;
      }

      .fill-background {
        background-color: color-mix(
          in srgb,
          var(--border-color),
          transparent 85%
        );
      }

      .tag {
        position: absolute;
        bottom: calc(100% + var(--size-1));
        inset-inline-end: 0;
        inset-inline-start: 0;
        display: flex;
        flex-direction: row;
        justify-content: center;
      }

      .vertical .tag {
        inset-inline-end: calc(100% + var(--size-1));
        inset-inline-start: unset;
        top: 0;
        bottom: 0;
        flex-direction: column;
      }

      .group[data-mark-color="red"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-red-10);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-orange-10);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-green-10);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-turquoise-10);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-cyan-10);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-blue-10);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-violet-10);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-purple-10);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-tan-10);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight-light"] {
        --border-color: var(--color-neutral-10);
      }

      .group[data-mark-color="red"][data-mark-variant="highlight"] {
        --border-color: var(--color-red-50);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight"] {
        --border-color: var(--color-orange-50);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight"] {
        --border-color: var(--color-green-50);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight"] {
        --border-color: var(--color-turquoise-50);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight"] {
        --border-color: var(--color-cyan-50);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight"] {
        --border-color: var(--color-blue-50);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight"] {
        --border-color: var(--color-violet-50);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight"] {
        --border-color: var(--color-purple-50);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight"] {
        --border-color: var(--color-tan-50);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight"] {
        --border-color: var(--color-neutral-50);
      }

      .group[data-mark-color="red"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-red-70);
      }

      .group[data-mark-color="orange"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-orange-70);
      }

      .group[data-mark-color="green"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-green-70);
      }

      .group[data-mark-color="turquoise"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-turquoise-70);
      }

      .group[data-mark-color="cyan"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-cyan-70);
      }

      .group[data-mark-color="blue"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-blue-70);
      }

      .group[data-mark-color="violet"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-violet-70);
      }

      .group[data-mark-color="purple"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-purple-70);
      }

      .group[data-mark-color="tan"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-tan-70);
      }

      .group[data-mark-color="black"][data-mark-variant="highlight-dark"] {
        --border-color: var(--color-neutral-70);
      }
    `
];
Er([
  l({ type: Object, attribute: "design-data" })
], V.prototype, "data", 2);
V = Er([
  u("bp-macro-literary-design")
], V);
var _t = Object.defineProperty, Pt = Object.getOwnPropertyDescriptor, Y = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Pt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && _t(t, o, e), e;
};
let E = class extends g {
  constructor() {
    super(...arguments), this.title = "BibleProject Logo", this.variant = "default", this.lang = xr("LANGUAGE") ?? "en";
  }
  get src() {
    switch (this.variant) {
      case "logo-mark":
        return M("/bibleproject-logo-mark.svg");
      case "word-mark":
        return this.lang === "es" ? M("/proyectobiblia-word-mark.svg") : M("/bibleproject-word-mark.svg");
      default:
        return this.lang === "es" ? "/proyectobiblia.svg" : M("/bibleproject.svg");
    }
  }
  render() {
    return c`
      <img
        src="${this.src}"
        style="height: var(--height);"
        title="${this.title}"
      />
    `;
  }
};
E.styles = h`
    :host {
      --height: var(--logo-height, var(--size-4));

      display: block;
    }

    img {
      display: block;
    }
  `;
Y([
  l()
], E.prototype, "title", 2);
Y([
  l()
], E.prototype, "variant", 2);
Y([
  l()
], E.prototype, "lang", 2);
E = Y([
  u("bp-logo")
], E);
var Et = Object.defineProperty, Dt = Object.getOwnPropertyDescriptor, x = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Dt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Et(t, o, e), e;
};
let b = class extends g {
  constructor() {
    super(...arguments), this.anchorPosition = "bottom-left", this.noAnimation = !1, this.show = !1;
  }
  render() {
    const r = this.noAnimation ? "--lookup-reveal-duration: 0;" : "";
    return c`
      <div
        style=${r}
        class="lookup ${this.show ? "shown" : "hidden"} anchor-${this.anchorPosition}"
      >
        <div class="background"></div>
        <span class="word"><slot></slot></span>
        <div class="box-arrow"></div>
        <div class="information-container">
          <div class="information">
            <div class="top-info">
              <bp-text-hebrew class="hebrew">${this.hebrew}</bp-text-hebrew>
              <div class="roman">${this.roman}</div>
            </div>
            <div class="bottom-info">
              <div class="phonetic">${this.phonetic}</div>
              <div class="num-results">${this.numResults} Results</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
b.styles = h`
    .lookup {
      --arrow-size: 12px;
      --min-box-width: 250px;
      --lookup-reveal-duration: var(--duration-long);
      display: inline-block;
      position: relative;
    }

    .word {
      position: relative;
    }

    .background {
      position: absolute;
      top: 0;
      bottom: 0;
      left: -3px;
      right: -3px;
      transition: background-color var(--lookup-reveal-duration);
      z-index: -1;
    }

    .box-arrow {
      position: absolute;
      border-left: var(--arrow-size) solid transparent;
      border-right: var(--arrow-size) solid transparent;
      box-shadow: 0px 4px 34px rgb(0 0 0 / 15%);
      transition:
        border-bottom-color var(--lookup-reveal-duration),
        border-top-color var(--lookup-reveal-duration);
      z-index: var(--z-20);
    }

    .anchor-bottom-left .box-arrow,
    .anchor-bottom-right .box-arrow {
      top: calc(100% - 2px);
      border-bottom: var(--arrow-size) solid transparent;
    }

    .anchor-top-left .box-arrow,
    .anchor-top-right .box-arrow {
      bottom: calc(100% - 2px);
      border-top: var(--arrow-size) solid transparent;
    }

    .anchor-bottom-left .box-arrow,
    .anchor-top-left .box-arrow {
      left: 16px;
    }

    .anchor-bottom-right .box-arrow,
    .anchor-top-right .box-arrow {
      right: 16px;
    }

    .shown .background {
      background-color: #d7ecff;
    }

    .shown .box-arrow {
      border-bottom-color: #298ae2;
    }

    .anchor-top-left.shown .box-arrow,
    .anchor-top-right.shown .box-arrow {
      border-top-color: var(--color-white);
    }

    .information-container {
      position: absolute;
      z-index: var(--z-10);
    }

    .anchor-bottom-left .information-container,
    .anchor-bottom-right .information-container {
      top: calc(100% + 10px);
    }

    .anchor-top-left .information-container,
    .anchor-top-right .information-container {
      bottom: calc(100% + 10px);
    }

    .anchor-top-left .information-container,
    .anchor-bottom-left .information-container {
      left: -4px;
    }

    .anchor-top-right .information-container,
    .anchor-bottom-right .information-container {
      right: -4px;
    }

    .information {
      background: var(--color-white);
      box-shadow: 0px 4px 34px rgb(0 0 0 / 15%);
      border-radius: 12px;
      min-width: var(--min-box-width);
      opacity: 0;
      transition: opacity var(--lookup-reveal-duration);
    }

    .shown .information {
      opacity: 1;
    }

    .top-info {
      border-radius: 12px 12px 0 0;
      background-color: #298ae2;
      padding: var(--size-2) var(--size-2-5);
    }

    .hebrew {
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-6xl);
      line-height: var(--line-height-tight);
      color: #9fd2ff;
    }

    .roman {
      font-weight: var(--font-weight-semibold);
      font-size: var(--font-size-6xl);
      line-height: var(--line-height-tight);
      color: var(--color-white);
    }

    .bottom-info {
      border-radius: 0 0 12px 12px;
      padding: var(--size-2) var(--size-2-5);
    }

    .phonetic {
      font-family: sans-serif; // Graphik messes phoenetics up
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-4xl);
      line-height: var(--line-height-tight);
      color: var(--color-black);
    }

    .num-results {
      font-weight: var(--font-weight-normal);
      font-size: var(--font-size-4xl);
      line-height: var(--line-height-tight);
      color: var(--color-neutral-50);
    }
  `;
x([
  l({ attribute: "anchor-position" })
], b.prototype, "anchorPosition", 2);
x([
  l({
    type: Boolean,
    attribute: "no-animation",
    converter: (r) => r === "true"
  })
], b.prototype, "noAnimation", 2);
x([
  l({
    type: Boolean,
    attribute: "show"
  })
], b.prototype, "show", 2);
x([
  l({ attribute: "hebrew" })
], b.prototype, "hebrew", 2);
x([
  l({ attribute: "roman" })
], b.prototype, "roman", 2);
x([
  l({ attribute: "phonetic" })
], b.prototype, "phonetic", 2);
x([
  l({ attribute: "num-results" })
], b.prototype, "numResults", 2);
b = x([
  u("bp-lookup")
], b);
const Ot = h`
  mark {
    padding: var(--size-px) var(--size-0-5);
    border-radius: var(--radius-sm);
    font-weight: var(--font-weight-semibold);
    -webkit-box-decoration-break: clone;
    box-decoration-break: clone;
    line-height: var(--line-height-normal);
    transition:
      color var(--spotlight-transition-duration),
      background-color var(--spotlight-transition-duration);
  }

  .text {
    background-color: transparent;
    padding: 0px;
    border-radius: 0px;
  }

  .red {
    color: var(--color-red-50);
  }

  .orange {
    color: var(--color-orange-50);
  }

  .green {
    color: var(--color-green-50);
  }

  .turquoise {
    color: var(--color-turquoise-50);
  }

  .cyan {
    color: var(--color-cyan-50);
  }

  .blue {
    color: var(--color-blue-50);
  }

  .violet {
    color: var(--color-violet-50);
  }

  .purple {
    color: var(--color-purple-50);
  }

  .tan {
    color: var(--color-tan-50);
  }

  .black {
    color: var(--color-neutral-90);
  }

  .red.highlight-light {
    color: var(--color-red-60);
    background-color: var(--color-red-10);
  }

  .orange.highlight-light {
    color: var(--color-orange-60);
    background-color: var(--color-orange-10);
  }

  .green.highlight-light {
    color: var(--color-green-60);
    background-color: var(--color-green-10);
  }

  .turquoise.highlight-light {
    color: var(--color-turquoise-60);
    background-color: var(--color-turquoise-10);
  }

  .cyan.highlight-light {
    color: var(--color-cyan-60);
    background-color: var(--color-cyan-10);
  }

  .blue.highlight-light {
    color: var(--color-blue-60);
    background-color: var(--color-blue-10);
  }

  .violet.highlight-light {
    color: var(--color-violet-60);
    background-color: var(--color-violet-10);
  }

  .purple.highlight-light {
    color: var(--color-purple-60);
    background-color: var(--color-purple-10);
  }

  .tan.highlight-light {
    color: var(--color-tan-60);
    background-color: var(--color-tan-10);
  }

  .black.highlight-light {
    color: var(--color-neutral-60);
    background-color: var(--color-neutral-10);
  }

  .red.highlight {
    color: var(--color-white);
    background-color: var(--color-red-50);
  }

  .orange.highlight {
    color: var(--color-white);
    background-color: var(--color-orange-50);
  }

  .green.highlight {
    color: var(--color-white);
    background-color: var(--color-green-50);
  }

  .turquoise.highlight {
    color: var(--color-white);
    background-color: var(--color-turquoise-50);
  }

  .cyan.highlight {
    color: var(--color-white);
    background-color: var(--color-cyan-50);
  }

  .blue.highlight {
    color: var(--color-white);
    background-color: var(--color-blue-50);
  }

  .violet.highlight {
    color: var(--color-white);
    background-color: var(--color-violet-50);
  }

  .purple.highlight {
    color: var(--color-white);
    background-color: var(--color-purple-50);
  }

  .tan.highlight {
    color: var(--color-white);
    background-color: var(--color-tan-50);
  }

  .black.highlight {
    color: var(--color-white);
    background-color: var(--color-neutral-50);
  }

  .red.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-red-70);
  }

  .orange.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-orange-70);
  }

  .green.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-green-70);
  }

  .turquoise.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-turquoise-70);
  }

  .cyan.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-cyan-70);
  }

  .blue.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-blue-70);
  }

  .violet.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-violet-70);
  }

  .purple.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-purple-70);
  }

  .tan.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-tan-70);
  }

  .black.highlight-dark {
    color: var(--color-white);
    background-color: var(--color-neutral-70);
  }
`;
var St = Object.defineProperty, Ct = Object.getOwnPropertyDescriptor, G = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Ct(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && St(t, o, e), e;
};
let D = class extends g {
  constructor() {
    super(...arguments), this.color = "orange", this.variant = "highlight";
  }
  render() {
    const r = _(this.color, this.variant, {
      "can-spotlight": this.canSpotlight
    });
    return c`<mark class="${r}"><slot></slot></mark>`;
  }
};
D.styles = Ot;
G([
  l()
], D.prototype, "color", 2);
G([
  l()
], D.prototype, "variant", 2);
G([
  l({ type: Boolean, attribute: "can-spotlight" })
], D.prototype, "canSpotlight", 2);
D = G([
  u("bp-mark")
], D);
var Tt = Object.defineProperty, At = Object.getOwnPropertyDescriptor, W = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? At(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Tt(t, o, e), e;
};
let O = class extends g {
  render() {
    return c`
      <figure>
        <header>
          ${this.reference && c` <span class="reference">${this.reference}</span> `}
          ${this.translation && c` <span class="translation">${this.translation}</span> `}
        </header>

        <slot></slot>

        ${this.footnote && c` <footer>${this.footnote}</footer> `}

        <slot name="caption"></slot>
      </figure>
    `;
  }
};
O.styles = h`
    :host {
      display: block;
      margin: var(--size-2) 0;
    }

    ::slotted(p) {
      margin: 0 !important;
    }

    ::slotted(bp-caption) {
      padding: var(--size-1);
      font-size: inherit;
      background-color: var(--color-neutral-05);
      border-radius: var(--radius-md);
    }

    figure {
      display: flex;
      flex-direction: column;
      gap: var(--size-1);
      box-shadow: inset var(--size-1) 0 0 -5px var(--color-neutral-10);
      padding: 0 0 0 var(--size-2);
      margin: 0;
      line-height: var(--line-height-normal);
    }

    header {
      display: flex;
      gap: var(--size-1);
    }

    footer {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
    }

    .reference {
      font-weight: var(--font-weight-bold);
    }

    .translation {
      color: var(--color-gray);
      font-size: var(--font-size-xs);
      font-weight: var(--font-weight-semibold);
      vertical-align: 4px;
    }
  `;
W([
  l()
], O.prototype, "reference", 2);
W([
  l()
], O.prototype, "translation", 2);
W([
  l()
], O.prototype, "footnote", 2);
O = W([
  u("bp-scripture-callout")
], O);
var Nt = Object.defineProperty, jt = Object.getOwnPropertyDescriptor, Dr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? jt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Nt(t, o, e), e;
};
let K = class extends g {
  handleClick(r) {
    r.preventDefault(), document.dispatchEvent(
      new CustomEvent("bp:scripture_link", {
        detail: { reference: this.reference }
      })
    );
  }
  render() {
    return c` <button @click="${this.handleClick}"><slot></slot></button> `;
  }
};
K.styles = h`
    :host {
      display: inline-block;
    }

    button {
      font: var(--font-sans);
      border: unset;
      background: unset;
      padding: unset;
      font-size: inherit;
      color: inherit;
      cursor: pointer;
      text-align: inherit;
      line-height: inherit;
      text-decoration: underline;
    }
  `;
Dr([
  l()
], K.prototype, "reference", 2);
K = Dr([
  u("bp-scripture-link")
], K);
/**
 * @license
 * Copyright 2018 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Lt = (r) => r ?? Tr;
var It = Object.defineProperty, Bt = Object.getOwnPropertyDescriptor, F = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Bt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && It(t, o, e), e;
};
let S = class extends g {
  constructor() {
    super(...arguments), this.show = !1, this.empty = !0;
  }
  scrollIntoView() {
    var o, i, e;
    let r;
    (o = this.parentElement) != null && o.tagName && ((i = this.parentElement) == null ? void 0 : i.tagName) === "P" ? r = this.parentElement.previousElementSibling : r = this.previousElementSibling;
    const t = ["H1", "H2", "H3", "H4"];
    if (r) {
      const a = t.includes(r.nodeName) ? r : (e = this.shadowRoot) == null ? void 0 : e.querySelector("a");
      a == null || a.scrollIntoView({ behavior: "smooth", inline: "nearest" });
    }
  }
  handleSlotchange({ target: r }) {
    this.empty = !this.show || !r.assignedNodes({ flatten: !0 }).length;
  }
  render() {
    return c`
      <a id="${Lt(this.slideId)}" data-empty="${this.empty}">
        <slot @slotchange=${this.handleSlotchange}></slot>
      </a>
    `;
  }
};
S.styles = h`
    a[data-empty="false"] {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: var(--line-height-normal);
      color: inherit;
      border: 1px solid currentColor;
      font-weight: var(--font-weight-semibold);
      border-radius: var(--radius-full);
      padding: var(--size-0-5) var(--size-1-5);
    }

    a[data-empty="true"] {
      display: none;
    }
  `;
F([
  l({ attribute: "slide-id" })
], S.prototype, "slideId", 2);
F([
  l({ type: Boolean, attribute: "show" })
], S.prototype, "show", 2);
F([
  lr()
], S.prototype, "empty", 2);
S = F([
  u("bp-slide-anchor")
], S);
const Mt = h`
  :host {
    --spinner-color: #222225;
    --spinner-size: var(--size-3);
    --part-height: 8px;
    --part-width: 4px;
    --part-offset: 10px;

    display: inline-block;
  }

  .spinner {
    position: relative;
    width: var(--spinner-size);
    height: var(--spinner-size);
  }

  [data-invert] {
    --spinner-color: var(--color-white);
  }

  [data-size="xs"] {
    --spinner-size: var(--size-2);
    --part-height: 5px;
    --part-width: 2.5px;
    --part-offset: 6.5px;
  }

  [data-size="sm"] {
    --spinner-size: var(--size-2-5);
    --part-height: 6.5px;
    --part-width: 3.5px;
    --part-offset: 8.5px;
  }

  [data-size="lg"] {
    --spinner-size: var(--size-5);
    --part-height: 13.25px;
    --part-width: 5.25px;
    --part-offset: 17.5px;
  }

  .spinner > div {
    position: absolute;
    top: var(--part-height);
    left: var(--part-offset);
    width: var(--part-width);
    height: var(--part-height);
    background-color: var(--spinner-color);
    border-radius: var(--part-width);
    animation: spinner-part 1s linear infinite;
    will-change: opacity;
  }

  .spinner > div:nth-child(1) {
    transform: rotate(45deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.625s;
  }

  .spinner > div:nth-child(2) {
    transform: rotate(90deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.5s;
  }

  .spinner > div:nth-child(3) {
    transform: rotate(135deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.375s;
  }

  .spinner > div:nth-child(4) {
    transform: rotate(180deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.25s;
  }

  .spinner > div:nth-child(5) {
    transform: rotate(225deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1.125s;
  }

  .spinner > div:nth-child(6) {
    transform: rotate(270deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -1s;
  }

  .spinner > div:nth-child(7) {
    transform: rotate(315deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -0.875s;
  }

  .spinner > div:nth-child(8) {
    transform: rotate(360deg) translateY(calc(-1 * var(--part-height)));
    animation-delay: -0.75s;
  }

  @keyframes spinner-part {
    0% {
      opacity: 0.85;
    }
    50% {
      opacity: 0.25;
    }
    100% {
      opacity: 0.25;
    }
  }
`;
var Rt = Object.defineProperty, qt = Object.getOwnPropertyDescriptor, dr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? qt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Rt(t, o, e), e;
};
let A = class extends g {
  constructor() {
    super(...arguments), this.size = "md", this.invert = !1;
  }
  render() {
    return c`
      <div
        class="spinner"
        data-size="${this.size}"
        ?data-invert=${!!this.invert}
        role="status"
      >
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
    `;
  }
};
A.styles = Mt;
dr([
  l()
], A.prototype, "size", 2);
dr([
  l({ type: Boolean })
], A.prototype, "invert", 2);
A = dr([
  u("bp-spinner")
], A);
const Ht = h`
  :host {
    display: block;
    line-height: var(--line-height-normal);
  }

  strong {
    font-weight: var(--font-weight-semibold);
  }

  h1,
  h2,
  h3,
  h4 {
    margin: var(--size-2) 0 var(--size-2) 0;
    line-height: var(--line-height-snug);
  }

  h1 {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-normal);
    margin-top: 0px;
  }

  h2 {
    font-size: var(--font-size-lg);
  }

  h3 {
    font-size: var(--font-size-md);
  }

  h4 {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
  }

  p {
    margin: var(--size-2) 0;
  }

  a {
    color: var(--color-black);
  }

  ul {
    padding: 0 0 0 var(--size-3);
    margin: var(--size-2) 0;
  }

  ol {
    padding: 0 0 0 var(--size-3);
    margin: var(--size-2) 0;
  }

  ol ::marker {
    font-weight: var(--font-weight-semibold);
  }

  li {
    margin: 0;
  }

  ul li span {
    margin-left: 1px;
  }

  ol li span {
    margin-left: 0px;
  }

  ul ul,
  ol ol,
  ol li ul,
  ul li ol {
    margin: 0;
  }

  blockquote {
    box-shadow: inset var(--size-1) 0 0 -5px currentColor;
    padding: 0 0 0 var(--size-2);
    margin: 0 0 0 var(--size-1);
  }

  bp-cite {
    --bp-cite-color: var(--color-black);
  }

  bp-spinner {
    margin-top: var(--size-1);
    margin-bottom: var(--size-1);
    margin-left: 50%;
    transform: translate(-50%);
  }
`;
var Vt = Object.defineProperty, Kt = Object.getOwnPropertyDescriptor, pr = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Kt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = (i ? n(t, o, e) : n(e)) || e);
  return i && e && Vt(t, o, e), e;
};
let N = class extends g {
  scrollToSlideAnchor(r) {
    var t, o;
    (o = (t = this.shadowRoot) == null ? void 0 : t.querySelector(`[slide-id="${r}"]`)) == null || o.scrollIntoView();
  }
  updated(r) {
    !r.has("arcId") || !this.arcId || Ar(this.arcId).then(async ({ data: t }) => {
      this.data = t, this.updateDOMNodes();
    }).catch(() => {
    });
  }
  handleLinkClick(r) {
    globalThis.window.BibleProjectApp && r.preventDefault(), document.dispatchEvent(
      new CustomEvent("bp:external_link", {
        detail: {
          href: r.currentTarget.href
        }
      })
    );
  }
  async updateDOMNodes() {
    var r;
    await this.updateComplete, (r = this.shadowRoot) == null || r.querySelectorAll("a").forEach((t) => {
      t.setAttribute("target", "_blank"), t.removeEventListener("click", this.handleLinkClick), t.addEventListener("click", this.handleLinkClick);
    });
  }
  render() {
    return this.data ? T(this.data.contentHtml) : c`<bp-spinner size="lg"></bp-spinner>`;
  }
};
N.styles = Ht;
pr([
  l({ attribute: "arc-id" })
], N.prototype, "arcId", 2);
pr([
  lr()
], N.prototype, "data", 2);
N = pr([
  u("bp-teacher-notes")
], N);
var Ut = Object.getOwnPropertyDescriptor, Yt = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Ut(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = n(e) || e);
  return e;
};
let ar = class extends g {
  render() {
    return c` <slot></slot> `;
  }
};
ar.styles = h`
    :host {
      font-family: var(--font-greek);
      display: inline-block;
      font-weight: normal;
    }
  `;
ar = Yt([
  u("bp-text-greek")
], ar);
var Gt = Object.getOwnPropertyDescriptor, Wt = (r, t, o, i) => {
  for (var e = i > 1 ? void 0 : i ? Gt(t, o) : t, a = r.length - 1, n; a >= 0; a--)
    (n = r[a]) && (e = n(e) || e);
  return e;
};
let nr = class extends g {
  render() {
    return c` <slot></slot> `;
  }
};
nr.styles = h`
    :host {
      font-family: var(--font-hebrew);
      display: inline-block;
      font-weight: normal;
      direction: rtl;
    }
  `;
nr = Wt([
  u("bp-text-hebrew")
], nr);
