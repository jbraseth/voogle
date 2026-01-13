import { l as il, m as sl, i as St, a as mr, n as P, s as ft, d as Le, S as rl, c as pr, h as Re, x as N, e as gt, A as nl, o as dt, t as ne, b as ga, q as ei, p as ii, r as al } from "./classroom-DB1AAjAg.js";
class Xi {
  constructor(t, { target: e, config: i, callback: s, skipInitial: r }) {
    this.t = /* @__PURE__ */ new Set(), this.o = !1, this.i = !1, this.h = t, e !== null && this.t.add(e ?? t), this.l = i, this.o = r ?? this.o, this.callback = s, window.ResizeObserver ? (this.u = new ResizeObserver((a) => {
      this.handleChanges(a), this.h.requestUpdate();
    }), t.addController(this)) : console.warn("ResizeController error: browser does not support ResizeObserver.");
  }
  handleChanges(t) {
    var e;
    this.value = (e = this.callback) == null ? void 0 : e.call(this, t, this.u);
  }
  hostConnected() {
    for (const t of this.t) this.observe(t);
  }
  hostDisconnected() {
    this.disconnect();
  }
  async hostUpdated() {
    !this.o && this.i && this.handleChanges([]), this.i = !1;
  }
  observe(t) {
    this.t.add(t), this.u.observe(t, this.l), this.i = !0, this.h.requestUpdate();
  }
  unobserve(t) {
    this.t.delete(t), this.u.unobserve(t);
  }
  disconnect() {
    this.u.disconnect();
  }
  target(t) {
    return ol(this, t);
  }
}
const ol = il(class extends sl {
  constructor() {
    super(...arguments), this.observing = !1;
  }
  render(n, t) {
  }
  update(n, [t, e]) {
    this.controller = t, this.part = n, this.observe = e, e === !1 ? (t.unobserve(n.element), this.observing = !1) : this.observing === !1 && (t.observe(n.element), this.observing = !0);
  }
  disconnected() {
    var n;
    (n = this.controller) == null || n.unobserve(this.part.element), this.observing = !1;
  }
  reconnected() {
    var n;
    this.observe !== !1 && this.observing === !1 && ((n = this.controller) == null || n.observe(this.part.element), this.observing = !0);
  }
}), ma = St`
  .zoomable-slide,
  .scrollable-slide {
    --scroll-transition: transform var(--duration-x-long);
    --title-transition: font-size var(--duration-x-long),
      margin var(--duration-x-long), border-bottom var(--duration-long);
    --title-font-size: var(--font-size-6xl);
    --title-border-height: 0px;
    --scrim-transition: opacity var(--duration-long);
    --scrim-opacity: 1;
    --scrim-height: 40px;
    --scrim-top-color: rgba(0, 0, 0, 0);
    --scrim-bottom-color: var(--color-white);
    --content-translate-y: 0;
    --content-translate-x: 0;
    --content-scale: 1;
    --title-sup-size: var(--font-size-xl);
    color: var(--color-black);
    background-color: var(--color-white);
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .zoomable-slide.background-class-primary,
  .scrollable-slide.background-class-primary {
    background-color: var(--slide-accent-color);
  }

  .zoomable-slide.background-class-secondary,
  .scrollable-slide.background-class-secondary {
    background-color: var(--slide-secondary-color);
  }

  .title-minimized {
    --title-font-size: var(--font-size-3xl);
    --title-border-height: 2px;
    --title-sup-size: var(--font-size-md);
  }

  ::slotted([slot="title"]) {
    border-bottom: var(--title-border-height) solid var(--color-neutral-10);
    font-size: var(--title-font-size);
    line-height: var(--line-height-tight);
    font-weight: var(--font-weight-semibold);
    transition: var(--title-transition);
    margin: var(--size-6) var(--size-5) 0;
    display: block;
  }

  .content-window {
    width: 100%;
    flex-grow: 1;
    overflow: hidden;
    position: relative;
  }

  .zoomable-slide .content-window {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .transformed-content {
    position: absolute;
    transform: translateX(var(--content-translate-x))
      translateY(var(--content-translate-y)) scale(var(--content-scale));
    transform-origin: top center;
    transition: var(--scroll-transition);
  }

  .hidden {
    --scrim-opacity: 0;
  }

  .overflow-shadow {
    opacity: var(--scrim-opacity);
    position: absolute;
    bottom: 0;
    z-index: var(--z-10);
    width: var(--slide-default-width);
    height: var(--scrim-height);
    background: linear-gradient(
      180deg,
      var(--scrim-top-color) 0%,
      var(--scrim-bottom-color) 100%
    );
    transition: var(--scrim-transition);
  }

  .overflow-shadow-hidden {
    --scrim-opacity: 0;
  }
`;
class pa {
  constructor() {
    this._initAnimation = !1;
  }
  set contentEl(t) {
    this._contentEl = t;
  }
  update({ shown: t = [], hidden: e = [] }) {
    setTimeout(() => this._initAnimation = !0, 50), this._contentEl && (t.forEach((i) => {
      var r;
      const s = (r = this._contentEl) == null ? void 0 : r.querySelector(
        `[data-id="${i}"]`
      );
      if (s) { s.show = true; s.setAttribute("show", ""); }
      this._initAnimation ? s == null || s.removeAttribute("no-animation") : s == null || s.setAttribute("no-animation", "");
    }), e.forEach((i) => {
      var r;
      const s = (r = this._contentEl) == null ? void 0 : r.querySelector(
        `[data-id="${i}"]`
      );
      if (s) { s.show = false; s.removeAttribute("show"); }
      this._initAnimation ? s == null || s.removeAttribute("no-animation") : s == null || s.setAttribute("no-animation", "");
    }));
  }
}
function Ws(n) {
  const {
    top: t,
    left: e,
    width: i,
    height: s
  } = n.getBoundingClientRect(), { marginLeft: r, marginRight: a, marginTop: o, marginBottom: c } = getComputedStyle(n), l = (E) => E ? parseFloat(E.replace("px", "")) * (i / n.offsetWidth) : 0, h = e - l(r), d = e + i + l(a), u = t - l(o), f = t + s + l(a), g = (h + d) / 2, v = (u + f) / 2, p = i + l(r) + l(a), y = s + l(c) + l(o);
  return { width: p, height: y, top: u, bottom: f, left: h, right: d, midX: g, midY: v };
}
function Ys(n) {
  let { top: t, bottom: e, left: i, right: s } = n[0];
  for (const r of n)
    t = Math.min(r.top, t), e = Math.max(r.bottom, e), i = Math.min(r.left, i), s = Math.max(r.right, s);
  return {
    top: t,
    bottom: e,
    midY: (e + t) / 2,
    left: i,
    right: s,
    midX: (s + i) / 2,
    width: s - i,
    height: e - t
  };
}
const ll = 2;
class cl {
  constructor({
    slideRef: t,
    minWindowHeight: e,
    maxWindowHeight: i,
    windowWidth: s,
    verticalPadding: r = 0,
    horizontalPadding: a = 0,
    defaultUnitScale: o = void 0
  }) {
    this._initAnimation = !1, this._contentHeight = 540, this._contentWidth = 960, this._maxWindowHeight = 540, this._minWindowHeight = 540, this._windowWidth = 960, this._scrollX = 0, this._scrollY = 0, this._scale = 1, this._slideRef = t, this._verticalPadding = r, this._horizontalPadding = a, this._maxWindowHeight = i, this._minWindowHeight = e, this._windowWidth = s, this._defaultUnitScale = o;
  }
  set contentEl(t) {
    this._contentEl = t;
  }
  get contentEl() {
    return this._contentEl;
  }
  set maxWindowHeight(t) {
    this._maxWindowHeight = t;
  }
  set minWindowHeight(t) {
    this._minWindowHeight = t;
  }
  set windowWidth(t) {
    this._windowWidth = t;
  }
  set contentHeight(t) {
    this._contentHeight = t;
  }
  set contentWidth(t) {
    this._contentWidth = t;
  }
  set defaultUnitScale(t) {
    this._defaultUnitScale = t;
  }
  get minScale() {
    return Math.min(
      (this._minWindowHeight - 2 * this._verticalPadding) / this._contentHeight,
      (this._windowWidth - 2 * this._horizontalPadding) / this._contentWidth
    );
  }
  get unitScale() {
    return this._defaultUnitScale ? this._defaultUnitScale : (this._windowWidth - 2 * this._horizontalPadding) / this._contentWidth;
  }
  get scaledContentHeight() {
    return this._scale * this._contentHeight;
  }
  get scaledContentWidth() {
    return this._scale * this._contentWidth;
  }
  get maxTranslateX() {
    return Math.max(
      0,
      this.scaledContentWidth - (this._windowWidth - 2 * this._horizontalPadding)
    );
  }
  get minTranslateY() {
    return Math.max(
      (this._minWindowHeight - this.scaledContentHeight) / 2,
      this._verticalPadding
    );
  }
  get maxTranslateY() {
    return this.scaledContentHeight + 2 * this._verticalPadding < this._minWindowHeight ? this.minTranslateY : this._scale <= this.minScale ? this.minTranslateY : -1 * Math.max(
      -1 * this.minTranslateY,
      this.scaledContentHeight - (this._maxWindowHeight - this.minTranslateY)
    );
  }
  get translateX() {
    return -1 * this._scrollX * this.maxTranslateX;
  }
  get translateY() {
    return this.interpolate(
      this.minTranslateY,
      this.maxTranslateY,
      this._scrollY
    );
  }
  get isScrolling() {
    return this.translateY < this.minTranslateY;
  }
  get isScrolledToBottom() {
    return this.translateY <= this.maxTranslateY;
  }
  calculateScale(t) {
    return t < 0 ? this.minScale : t < 1 ? this.interpolate(this.minScale, this.unitScale, t) : t * this.unitScale;
  }
  getScaleValue(t, e, i) {
    var d, u;
    const s = this.calculateScale(t);
    if (!this._contentEl || !(i != null && i.length) && !(e != null && e.length)) return s;
    const a = (i ?? e ?? []).map((f) => {
      var g;
      return (g = this._contentEl) == null ? void 0 : g.querySelector(`[data-id="${f}"]`);
    }).filter((f) => !!f).map((f) => f);
    if (!(a != null && a.length)) return s;
    const { width: o, height: c } = Ys(a.map(Ws)), l = ((d = this._contentEl) == null ? void 0 : d.offsetWidth) / ((u = this._contentEl) == null ? void 0 : u.getBoundingClientRect().width), h = Math.min(
      (this._windowWidth - 2 * this._horizontalPadding) / ((o || 1) * l),
      (this._maxWindowHeight - 2 * this._verticalPadding) / ((c || 1) * l)
    );
    return i != null && i.length ? h : Math.min(h, s);
  }
  getScrollValue(t, e, i, s) {
    let r = t, a = e;
    if (!this._contentEl || !(i != null && i.length)) return { scrollX: r, scrollY: a };
    const o = i.map(
      (D) => {
        var A;
        return (A = this._contentEl) == null ? void 0 : A.querySelector(`[data-id="${D}"]`);
      }
    ).filter((D) => !!D).map((D) => D);
    if (!(o != null && o.length)) return { scrollX: r, scrollY: a };
    const {
      left: c,
      top: l,
      width: h
    } = this._contentEl.getBoundingClientRect(), {
      left: d,
      midX: u,
      right: f,
      top: g,
      midY: v,
      bottom: p
    } = Ys(
      o.map(Ws)
    ), y = this._scale * this._contentEl.offsetWidth / h;
    let E, T;
    switch (s) {
      case "left":
      case "bottom-left":
      case "top-left":
        E = (d - c) * y, T = h * y / 2 - this._windowWidth / 2 + this._horizontalPadding;
        break;
      case "right":
      case "bottom-right":
      case "top-right":
        E = (f - c) * y, T = h * y / 2 + this._windowWidth / 2 - this._horizontalPadding;
        break;
      case "center":
      case "bottom":
      case "top":
      default:
        E = (u - c) * y, T = h * y / 2;
        break;
    }
    r = 0, this.maxTranslateX > 0 && (r = Math.min(
      0.5,
      Math.max(
        -0.5,
        (E - T) / this.maxTranslateX
      )
    ));
    let S, x;
    switch (s) {
      case "top":
      case "top-left":
      case "top-right":
        S = (g - l) * y, x = ll - this._verticalPadding;
        break;
      case "bottom":
      case "bottom-left":
      case "bottom-right":
        S = (p - l) * y, x = this._maxWindowHeight - 2 * this._verticalPadding;
        break;
      case "center":
      case "left":
      case "right":
      default:
        S = (v - l) * y, x = this._maxWindowHeight / 2 - this._verticalPadding;
        break;
    }
    return a = 0, Math.abs(this.maxTranslateY - this.minTranslateY) > 0 && (a = Math.min(
      1,
      Math.max(
        0,
        (S - x) / Math.abs(this.maxTranslateY - this.minTranslateY)
      )
    )), { scrollX: r, scrollY: a };
  }
  update({
    zoom: t = 0,
    zoomFillElements: e = void 0,
    zoomFitElements: i = void 0,
    scrollX: s = 0,
    scrollY: r = 0,
    scrollPoints: a = void 0,
    scrollAnchorPoint: o = void 0,
    minimizeTitle: c = void 0
  }) {
    setTimeout(() => this._initAnimation = !0, 50), this._scale = this.getScaleValue(t, i, e);
    const { scrollX: l, scrollY: h } = this.getScrollValue(
      s,
      r,
      a,
      o
    );
    if (this._scrollX = l ?? 0, this._scrollY = h ?? 0, this._slideRef.value) {
      const d = `
        ${this._initAnimation ? "" : "--scroll-transition: 0; --title-transition: 0;"}
        --content-translate-x: ${this.translateX}px;
        --content-translate-y: ${this.translateY}px;
        --content-scale: ${this._scale};
        --scrim-opacity: ${this.isScrolledToBottom ? 0 : 1};
      `;
      this._slideRef.value.setAttribute("style", d), this.isScrolling || c ? this._slideRef.value.classList.add("title-minimized") : this._slideRef.value.classList.remove("title-minimized");
    }
  }
  interpolate(t, e, i) {
    return t * (1 - i) + i * e;
  }
}
var hl = Object.defineProperty, dl = Object.getOwnPropertyDescriptor, Ee = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? dl(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && hl(t, e, s), s;
};
const zs = 40, js = 960, ul = 540, fl = 106, gl = 156, ml = 80, pl = 116, vl = 176, yl = 80, El = js / (js - 2 * zs), Tl = 1.5;
let Zt = class extends ft {
  constructor() {
    super(...arguments), this.slideHeight = ul, this.slideWidth = js, this.slideRef = Le(), this.contentContainerRef = Le(), this.slideObserver = new Xi(this, {
      callback: (n) => {
        n.filter((t) => t.target.className.includes("zoomable-slide")).forEach((t) => {
          this.slideHeight = t.contentRect.height, this.slideWidth = t.contentRect.width, this.zoomController.minWindowHeight = this.minContentWindowHeight, this.zoomController.maxWindowHeight = this.maxContentWindowHeight, this.updateState();
        });
      }
    }), this.contentObserver = new Xi(this, {
      callback: (n) => {
        n.filter((t) => t.target.className.includes("scaled-content")).forEach((t) => {
          this.zoomController.contentHeight = t.contentRect.height, this.zoomController.contentWidth = t.contentRect.width, this.updateState();
        });
      }
    }), this.viewMode = "default", this.largeContentMode = !1, this.titleWraps2Lines = !1, this.backgroundColor = "white", this.highlightController = new pa(), this.zoomController = new cl({
      slideRef: this.slideRef,
      minWindowHeight: this.minContentWindowHeight,
      maxWindowHeight: this.maxContentWindowHeight,
      windowWidth: this.slideWidth,
      verticalPadding: zs,
      horizontalPadding: zs,
      defaultUnitScale: this.defaultUnitScale
    }), this.spotlightController = new rl({
      spotlightContainerRef: this.contentContainerRef
    });
  }
  get maxTitleHeight() {
    return this.hideTitle ? 0 : this.viewMode === "default" ? this.titleWraps2Lines ? gl : fl : this.titleWraps2Lines ? vl : pl;
  }
  get minTitleHeight() {
    return this.hideTitle ? 0 : this.viewMode === "default" ? ml : yl;
  }
  get maxContentWindowHeight() {
    return this.slideHeight - this.minTitleHeight;
  }
  get minContentWindowHeight() {
    return this.slideHeight - this.maxTitleHeight;
  }
  get defaultUnitScale() {
    return this.largeContentMode ? Tl : void 0;
  }
  updateState() {
    var n, t, e;
    this.highlightController.update(((n = this.slideState) == null ? void 0 : n.highlightState) || {}), this.zoomController.update(((t = this.slideState) == null ? void 0 : t.transformState) || {}), this.spotlightController.update(((e = this.slideState) == null ? void 0 : e.spotlightState) || {});
  }
  willUpdate() {
    this.updateState(), this.zoomController.defaultUnitScale = this.defaultUnitScale;
  }
  handleContentUpdate(n) {
    var e, i, s;
    let t = n.target.assignedNodes({
      flatten: !0
    })[0];
    t.querySelector("bp-literary-design") ? t = (e = t.querySelector("bp-literary-design").shadowRoot) == null ? void 0 : e.querySelector("div") : t.querySelector("bp-ephesians-literary-design") ? t = (i = t.querySelector("bp-ephesians-literary-design").shadowRoot) == null ? void 0 : i.querySelector("div") : t.querySelector("bp-macro-literary-design") && (t = (s = t.querySelector("bp-macro-literary-design").shadowRoot) == null ? void 0 : s.querySelector("div")), this.highlightController.contentEl = t, this.zoomController.contentEl = t, this.spotlightController.contentEl = t, this.updateState();
  }
  render() {
    const n = "--scroll-transition: 0; --title-transition: 0;", t = pr("overflow-shadow", {
      "overflow-shadow-hidden": this.hideShadow
    });
    return N`
      <div
        ${Re(this.slideRef)}
        class="zoomable-slide ${this.viewMode} background-${this.backgroundColor}"
        style="${n}"
      >
        ${this.hideTitle ? "" : N`<slot name="title"></slot>`}
        <div class="content-window">
          <div class="transformed-content">
            <div
              class="scaled-content spotlight-container"
              ${Re(this.contentContainerRef)}
            >
              <slot name="content" @slotchange=${this.handleContentUpdate}>
              </slot>
            </div>
          </div>
        </div>
        <div class="${t}"></div>
      </div>
    `;
  }
  firstUpdated() {
    this.contentContainerRef.value && this.contentObserver.observe(this.contentContainerRef.value), this.slideRef.value && this.slideObserver.observe(this.slideRef.value);
  }
};
Zt.styles = [ma, mr];
Ee([
  P()
], Zt.prototype, "slideState", 2);
Ee([
  P({ attribute: "view-mode" })
], Zt.prototype, "viewMode", 2);
Ee([
  P({
    type: Boolean,
    attribute: "large-content-mode"
  })
], Zt.prototype, "largeContentMode", 2);
Ee([
  P({
    type: Boolean,
    attribute: "title-wraps-2-lines"
  })
], Zt.prototype, "titleWraps2Lines", 2);
Ee([
  P({ attribute: "background-color" })
], Zt.prototype, "backgroundColor", 2);
Ee([
  P({
    type: Boolean,
    attribute: "hide-shadow"
  })
], Zt.prototype, "hideShadow", 2);
Ee([
  P({
    type: Boolean,
    attribute: "hide-title"
  })
], Zt.prototype, "hideTitle", 2);
Zt = Ee([
  gt("bp-zoomable-slide")
], Zt);
var Sl = Object.defineProperty, xl = Object.getOwnPropertyDescriptor, Me = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? xl(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Sl(t, e, s), s;
};
let fe = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default", this.hideTitle = !1, this.titleWraps2Lines = !1, this.hideShadow = !1;
  }
  render() {
    if (!this.data) return;
    const { src: n, alt: t } = this.data;
    return N`
      <bp-zoomable-slide
        view-mode="${this.viewMode}"
        ?hide-title=${this.hideTitle}
        ?hide-shadow=${this.hideShadow}
        ?title-wraps-2-lines=${this.titleWraps2Lines}
        .slideState=${this.slideState}
      >
        <div slot="title">
          <slot name="title"></slot>
        </div>
        <img slot="content" src=${n} alt=${t} title=${t} />
      </bp-zoomable-slide>
    `;
  }
};
Me([
  P({ attribute: "view-mode" })
], fe.prototype, "viewMode", 2);
Me([
  P({ type: Object })
], fe.prototype, "slideState", 2);
Me([
  P({ type: Boolean, attribute: "hide-title" })
], fe.prototype, "hideTitle", 2);
Me([
  P({ type: Boolean, attribute: "title-wraps-2-lines" })
], fe.prototype, "titleWraps2Lines", 2);
Me([
  P({ type: Boolean, attribute: "hide-shadow" })
], fe.prototype, "hideShadow", 2);
Me([
  P({ type: Object })
], fe.prototype, "data", 2);
fe = Me([
  gt("bp-diagram-slide")
], fe);
const Al = St`
  .image-slide {
    --image-slide-caption-height: var(--size-6);
    width: 100%;
    height: var(--slide-current-height);
    display: flex;
    background-color: var(--color-white);
    box-sizing: border-box;
    flex-direction: column;
    padding: var(--size-4) var(--size-4);
  }

  .title {
    font-size: var(--font-size-6xl);
    line-height: var(--line-height-tight);
    font-weight: var(--font-weight-semibold);
    margin: var(--size-2) var(--size-1);
    display: block;
  }

  .image-container {
    display: flex;
    align-items: center;
    overflow: hidden;
    flex-grow: 1;
    margin: 0 var(--size-1);
  }

  .image-container img {
    height: 100%;
    width: 100%;
    object-fit: contain;
    margin: 0px;
  }

  .mobile,
  .mobile-tall {
    padding: var(--size-4);
  }

  .tall .image-container,
  .mobile-tall .image-container {
    flex-grow: 0;
  }
`;
var bl = Object.defineProperty, Il = Object.getOwnPropertyDescriptor, ds = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Il(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && bl(t, e, s), s;
};
let qe = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    if (!this.data) return;
    const { src: n, alt: t } = this.data;
    return N`
      <div class="image-slide ${this.viewMode}">
        ${this.slideTitle ? N`<div class="title">${dt(this.slideTitle)}</div>` : nl}
        <div class="image-container">
          <img src=${n} alt=${t} title=${t} />
        </div>
      </div>
    `;
  }
};
qe.styles = Al;
ds([
  P({ attribute: "title" })
], qe.prototype, "slideTitle", 2);
ds([
  P({ attribute: "view-mode" })
], qe.prototype, "viewMode", 2);
ds([
  P()
], qe.prototype, "data", 2);
qe = ds([
  gt("bp-image-slide")
], qe);
const B = Number.isFinite || function(n) {
  return typeof n == "number" && isFinite(n);
}, Ll = Number.isSafeInteger || function(n) {
  return typeof n == "number" && Math.abs(n) <= Rl;
}, Rl = Number.MAX_SAFE_INTEGER || 9007199254740991;
let Y = /* @__PURE__ */ (function(n) {
  return n.NETWORK_ERROR = "networkError", n.MEDIA_ERROR = "mediaError", n.KEY_SYSTEM_ERROR = "keySystemError", n.MUX_ERROR = "muxError", n.OTHER_ERROR = "otherError", n;
})({}), L = /* @__PURE__ */ (function(n) {
  return n.KEY_SYSTEM_NO_KEYS = "keySystemNoKeys", n.KEY_SYSTEM_NO_ACCESS = "keySystemNoAccess", n.KEY_SYSTEM_NO_SESSION = "keySystemNoSession", n.KEY_SYSTEM_NO_CONFIGURED_LICENSE = "keySystemNoConfiguredLicense", n.KEY_SYSTEM_LICENSE_REQUEST_FAILED = "keySystemLicenseRequestFailed", n.KEY_SYSTEM_SERVER_CERTIFICATE_REQUEST_FAILED = "keySystemServerCertificateRequestFailed", n.KEY_SYSTEM_SERVER_CERTIFICATE_UPDATE_FAILED = "keySystemServerCertificateUpdateFailed", n.KEY_SYSTEM_SESSION_UPDATE_FAILED = "keySystemSessionUpdateFailed", n.KEY_SYSTEM_STATUS_OUTPUT_RESTRICTED = "keySystemStatusOutputRestricted", n.KEY_SYSTEM_STATUS_INTERNAL_ERROR = "keySystemStatusInternalError", n.KEY_SYSTEM_DESTROY_MEDIA_KEYS_ERROR = "keySystemDestroyMediaKeysError", n.KEY_SYSTEM_DESTROY_CLOSE_SESSION_ERROR = "keySystemDestroyCloseSessionError", n.KEY_SYSTEM_DESTROY_REMOVE_SESSION_ERROR = "keySystemDestroyRemoveSessionError", n.MANIFEST_LOAD_ERROR = "manifestLoadError", n.MANIFEST_LOAD_TIMEOUT = "manifestLoadTimeOut", n.MANIFEST_PARSING_ERROR = "manifestParsingError", n.MANIFEST_INCOMPATIBLE_CODECS_ERROR = "manifestIncompatibleCodecsError", n.LEVEL_EMPTY_ERROR = "levelEmptyError", n.LEVEL_LOAD_ERROR = "levelLoadError", n.LEVEL_LOAD_TIMEOUT = "levelLoadTimeOut", n.LEVEL_PARSING_ERROR = "levelParsingError", n.LEVEL_SWITCH_ERROR = "levelSwitchError", n.AUDIO_TRACK_LOAD_ERROR = "audioTrackLoadError", n.AUDIO_TRACK_LOAD_TIMEOUT = "audioTrackLoadTimeOut", n.SUBTITLE_LOAD_ERROR = "subtitleTrackLoadError", n.SUBTITLE_TRACK_LOAD_TIMEOUT = "subtitleTrackLoadTimeOut", n.FRAG_LOAD_ERROR = "fragLoadError", n.FRAG_LOAD_TIMEOUT = "fragLoadTimeOut", n.FRAG_DECRYPT_ERROR = "fragDecryptError", n.FRAG_PARSING_ERROR = "fragParsingError", n.FRAG_GAP = "fragGap", n.REMUX_ALLOC_ERROR = "remuxAllocError", n.KEY_LOAD_ERROR = "keyLoadError", n.KEY_LOAD_TIMEOUT = "keyLoadTimeOut", n.BUFFER_ADD_CODEC_ERROR = "bufferAddCodecError", n.BUFFER_INCOMPATIBLE_CODECS_ERROR = "bufferIncompatibleCodecsError", n.BUFFER_APPEND_ERROR = "bufferAppendError", n.BUFFER_APPENDING_ERROR = "bufferAppendingError", n.BUFFER_STALLED_ERROR = "bufferStalledError", n.BUFFER_FULL_ERROR = "bufferFullError", n.BUFFER_SEEK_OVER_HOLE = "bufferSeekOverHole", n.BUFFER_NUDGE_ON_STALL = "bufferNudgeOnStall", n.ASSET_LIST_LOAD_ERROR = "assetListLoadError", n.ASSET_LIST_LOAD_TIMEOUT = "assetListLoadTimeout", n.ASSET_LIST_PARSING_ERROR = "assetListParsingError", n.INTERSTITIAL_ASSET_ITEM_ERROR = "interstitialAssetItemError", n.INTERNAL_EXCEPTION = "internalException", n.INTERNAL_ABORTED = "aborted", n.ATTACH_MEDIA_ERROR = "attachMediaError", n.UNKNOWN = "unknown", n;
})({}), m = /* @__PURE__ */ (function(n) {
  return n.MEDIA_ATTACHING = "hlsMediaAttaching", n.MEDIA_ATTACHED = "hlsMediaAttached", n.MEDIA_DETACHING = "hlsMediaDetaching", n.MEDIA_DETACHED = "hlsMediaDetached", n.MEDIA_ENDED = "hlsMediaEnded", n.STALL_RESOLVED = "hlsStallResolved", n.BUFFER_RESET = "hlsBufferReset", n.BUFFER_CODECS = "hlsBufferCodecs", n.BUFFER_CREATED = "hlsBufferCreated", n.BUFFER_APPENDING = "hlsBufferAppending", n.BUFFER_APPENDED = "hlsBufferAppended", n.BUFFER_EOS = "hlsBufferEos", n.BUFFERED_TO_END = "hlsBufferedToEnd", n.BUFFER_FLUSHING = "hlsBufferFlushing", n.BUFFER_FLUSHED = "hlsBufferFlushed", n.MANIFEST_LOADING = "hlsManifestLoading", n.MANIFEST_LOADED = "hlsManifestLoaded", n.MANIFEST_PARSED = "hlsManifestParsed", n.LEVEL_SWITCHING = "hlsLevelSwitching", n.LEVEL_SWITCHED = "hlsLevelSwitched", n.LEVEL_LOADING = "hlsLevelLoading", n.LEVEL_LOADED = "hlsLevelLoaded", n.LEVEL_UPDATED = "hlsLevelUpdated", n.LEVEL_PTS_UPDATED = "hlsLevelPtsUpdated", n.LEVELS_UPDATED = "hlsLevelsUpdated", n.AUDIO_TRACKS_UPDATED = "hlsAudioTracksUpdated", n.AUDIO_TRACK_SWITCHING = "hlsAudioTrackSwitching", n.AUDIO_TRACK_SWITCHED = "hlsAudioTrackSwitched", n.AUDIO_TRACK_LOADING = "hlsAudioTrackLoading", n.AUDIO_TRACK_LOADED = "hlsAudioTrackLoaded", n.AUDIO_TRACK_UPDATED = "hlsAudioTrackUpdated", n.SUBTITLE_TRACKS_UPDATED = "hlsSubtitleTracksUpdated", n.SUBTITLE_TRACKS_CLEARED = "hlsSubtitleTracksCleared", n.SUBTITLE_TRACK_SWITCH = "hlsSubtitleTrackSwitch", n.SUBTITLE_TRACK_LOADING = "hlsSubtitleTrackLoading", n.SUBTITLE_TRACK_LOADED = "hlsSubtitleTrackLoaded", n.SUBTITLE_TRACK_UPDATED = "hlsSubtitleTrackUpdated", n.SUBTITLE_FRAG_PROCESSED = "hlsSubtitleFragProcessed", n.CUES_PARSED = "hlsCuesParsed", n.NON_NATIVE_TEXT_TRACKS_FOUND = "hlsNonNativeTextTracksFound", n.INIT_PTS_FOUND = "hlsInitPtsFound", n.FRAG_LOADING = "hlsFragLoading", n.FRAG_LOAD_EMERGENCY_ABORTED = "hlsFragLoadEmergencyAborted", n.FRAG_LOADED = "hlsFragLoaded", n.FRAG_DECRYPTED = "hlsFragDecrypted", n.FRAG_PARSING_INIT_SEGMENT = "hlsFragParsingInitSegment", n.FRAG_PARSING_USERDATA = "hlsFragParsingUserdata", n.FRAG_PARSING_METADATA = "hlsFragParsingMetadata", n.FRAG_PARSED = "hlsFragParsed", n.FRAG_BUFFERED = "hlsFragBuffered", n.FRAG_CHANGED = "hlsFragChanged", n.FPS_DROP = "hlsFpsDrop", n.FPS_DROP_LEVEL_CAPPING = "hlsFpsDropLevelCapping", n.MAX_AUTO_LEVEL_UPDATED = "hlsMaxAutoLevelUpdated", n.ERROR = "hlsError", n.DESTROYING = "hlsDestroying", n.KEY_LOADING = "hlsKeyLoading", n.KEY_LOADED = "hlsKeyLoaded", n.LIVE_BACK_BUFFER_REACHED = "hlsLiveBackBufferReached", n.BACK_BUFFER_REACHED = "hlsBackBufferReached", n.STEERING_MANIFEST_LOADED = "hlsSteeringManifestLoaded", n.ASSET_LIST_LOADING = "hlsAssetListLoading", n.ASSET_LIST_LOADED = "hlsAssetListLoaded", n.INTERSTITIALS_UPDATED = "hlsInterstitialsUpdated", n.INTERSTITIALS_BUFFERED_TO_BOUNDARY = "hlsInterstitialsBufferedToBoundary", n.INTERSTITIAL_ASSET_PLAYER_CREATED = "hlsInterstitialAssetPlayerCreated", n.INTERSTITIAL_STARTED = "hlsInterstitialStarted", n.INTERSTITIAL_ASSET_STARTED = "hlsInterstitialAssetStarted", n.INTERSTITIAL_ASSET_ENDED = "hlsInterstitialAssetEnded", n.INTERSTITIAL_ASSET_ERROR = "hlsInterstitialAssetError", n.INTERSTITIAL_ENDED = "hlsInterstitialEnded", n.INTERSTITIALS_PRIMARY_RESUMED = "hlsInterstitialsPrimaryResumed", n.PLAYOUT_LIMIT_REACHED = "hlsPlayoutLimitReached", n.EVENT_CUE_ENTER = "hlsEventCueEnter", n;
})({});
var tt = {
  MANIFEST: "manifest",
  LEVEL: "level",
  AUDIO_TRACK: "audioTrack",
  SUBTITLE_TRACK: "subtitleTrack"
}, K = {
  MAIN: "main",
  AUDIO: "audio",
  SUBTITLE: "subtitle"
};
class Ne {
  //  About half of the estimated value will be from the last |halfLife| samples by weight.
  constructor(t, e = 0, i = 0) {
    this.halfLife = void 0, this.alpha_ = void 0, this.estimate_ = void 0, this.totalWeight_ = void 0, this.halfLife = t, this.alpha_ = t ? Math.exp(Math.log(0.5) / t) : 0, this.estimate_ = e, this.totalWeight_ = i;
  }
  sample(t, e) {
    const i = Math.pow(this.alpha_, t);
    this.estimate_ = e * (1 - i) + i * this.estimate_, this.totalWeight_ += t;
  }
  getTotalWeight() {
    return this.totalWeight_;
  }
  getEstimate() {
    if (this.alpha_) {
      const t = 1 - Math.pow(this.alpha_, this.totalWeight_);
      if (t)
        return this.estimate_ / t;
    }
    return this.estimate_;
  }
}
class _l {
  constructor(t, e, i, s = 100) {
    this.defaultEstimate_ = void 0, this.minWeight_ = void 0, this.minDelayMs_ = void 0, this.slow_ = void 0, this.fast_ = void 0, this.defaultTTFB_ = void 0, this.ttfb_ = void 0, this.defaultEstimate_ = i, this.minWeight_ = 1e-3, this.minDelayMs_ = 50, this.slow_ = new Ne(t), this.fast_ = new Ne(e), this.defaultTTFB_ = s, this.ttfb_ = new Ne(t);
  }
  update(t, e) {
    const {
      slow_: i,
      fast_: s,
      ttfb_: r
    } = this;
    i.halfLife !== t && (this.slow_ = new Ne(t, i.getEstimate(), i.getTotalWeight())), s.halfLife !== e && (this.fast_ = new Ne(e, s.getEstimate(), s.getTotalWeight())), r.halfLife !== t && (this.ttfb_ = new Ne(t, r.getEstimate(), r.getTotalWeight()));
  }
  sample(t, e) {
    t = Math.max(t, this.minDelayMs_);
    const i = 8 * e, s = t / 1e3, r = i / s;
    this.fast_.sample(s, r), this.slow_.sample(s, r);
  }
  sampleTTFB(t) {
    const e = t / 1e3, i = Math.sqrt(2) * Math.exp(-Math.pow(e, 2) / 2);
    this.ttfb_.sample(i, Math.max(t, 5));
  }
  canEstimate() {
    return this.fast_.getTotalWeight() >= this.minWeight_;
  }
  getEstimate() {
    return this.canEstimate() ? Math.min(this.fast_.getEstimate(), this.slow_.getEstimate()) : this.defaultEstimate_;
  }
  getEstimateTTFB() {
    return this.ttfb_.getTotalWeight() >= this.minWeight_ ? this.ttfb_.getEstimate() : this.defaultTTFB_;
  }
  get defaultEstimate() {
    return this.defaultEstimate_;
  }
  destroy() {
  }
}
function Dl(n, t, e) {
  return (t = Cl(t)) in n ? Object.defineProperty(n, t, {
    value: e,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : n[t] = e, n;
}
function nt() {
  return nt = Object.assign ? Object.assign.bind() : function(n) {
    for (var t = 1; t < arguments.length; t++) {
      var e = arguments[t];
      for (var i in e) ({}).hasOwnProperty.call(e, i) && (n[i] = e[i]);
    }
    return n;
  }, nt.apply(null, arguments);
}
function zr(n, t) {
  var e = Object.keys(n);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(n);
    t && (i = i.filter(function(s) {
      return Object.getOwnPropertyDescriptor(n, s).enumerable;
    })), e.push.apply(e, i);
  }
  return e;
}
function st(n) {
  for (var t = 1; t < arguments.length; t++) {
    var e = arguments[t] != null ? arguments[t] : {};
    t % 2 ? zr(Object(e), !0).forEach(function(i) {
      Dl(n, i, e[i]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(n, Object.getOwnPropertyDescriptors(e)) : zr(Object(e)).forEach(function(i) {
      Object.defineProperty(n, i, Object.getOwnPropertyDescriptor(e, i));
    });
  }
  return n;
}
function wl(n, t) {
  if (typeof n != "object" || !n) return n;
  var e = n[Symbol.toPrimitive];
  if (e !== void 0) {
    var i = e.call(n, t);
    if (typeof i != "object") return i;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(n);
}
function Cl(n) {
  var t = wl(n, "string");
  return typeof t == "symbol" ? t : t + "";
}
class Bt {
  constructor(t, e) {
    this.trace = void 0, this.debug = void 0, this.log = void 0, this.warn = void 0, this.info = void 0, this.error = void 0;
    const i = `[${t}]:`;
    this.trace = ce, this.debug = e.debug.bind(null, i), this.log = e.log.bind(null, i), this.warn = e.warn.bind(null, i), this.info = e.info.bind(null, i), this.error = e.error.bind(null, i);
  }
}
const ce = function() {
}, Pl = {
  trace: ce,
  debug: ce,
  log: ce,
  warn: ce,
  info: ce,
  error: ce
};
function qs() {
  return nt({}, Pl);
}
function kl(n, t) {
  const e = self.console[n];
  return e ? e.bind(self.console, `${t ? "[" + t + "] " : ""}[${n}] >`) : ce;
}
function jr(n, t, e) {
  return t[n] ? t[n].bind(t) : kl(n, e);
}
const Xs = qs();
function Ol(n, t, e) {
  const i = qs();
  if (typeof console == "object" && n === !0 || typeof n == "object") {
    const s = [
      // Remove out from list here to hard-disable a log-level
      // 'trace',
      "debug",
      "log",
      "info",
      "warn",
      "error"
    ];
    s.forEach((r) => {
      i[r] = jr(r, n, e);
    });
    try {
      i.log(`Debug logs enabled for "${t}" in hls.js version 1.6.15`);
    } catch {
      return qs();
    }
    s.forEach((r) => {
      Xs[r] = jr(r, n);
    });
  } else
    nt(Xs, i);
  return i;
}
const rt = Xs;
function ge(n = !0) {
  return typeof self > "u" ? void 0 : (n || !self.MediaSource) && self.ManagedMediaSource || self.MediaSource || self.WebKitMediaSource;
}
function Ml(n) {
  return typeof self < "u" && n === self.ManagedMediaSource;
}
function va(n, t) {
  const e = Object.keys(n), i = Object.keys(t), s = e.length, r = i.length;
  return !s || !r || s === r && !e.some((a) => i.indexOf(a) === -1);
}
function Ft(n, t = !1) {
  if (typeof TextDecoder < "u") {
    const l = new TextDecoder("utf-8").decode(n);
    if (t) {
      const h = l.indexOf("\0");
      return h !== -1 ? l.substring(0, h) : l;
    }
    return l.replace(/\0/g, "");
  }
  const e = n.length;
  let i, s, r, a = "", o = 0;
  for (; o < e; ) {
    if (i = n[o++], i === 0 && t)
      return a;
    if (i === 0 || i === 3)
      continue;
    switch (i >> 4) {
      case 0:
      case 1:
      case 2:
      case 3:
      case 4:
      case 5:
      case 6:
      case 7:
        a += String.fromCharCode(i);
        break;
      case 12:
      case 13:
        s = n[o++], a += String.fromCharCode((i & 31) << 6 | s & 63);
        break;
      case 14:
        s = n[o++], r = n[o++], a += String.fromCharCode((i & 15) << 12 | (s & 63) << 6 | (r & 63) << 0);
        break;
    }
  }
  return a;
}
function At(n) {
  let t = "";
  for (let e = 0; e < n.length; e++) {
    let i = n[e].toString(16);
    i.length < 2 && (i = "0" + i), t += i;
  }
  return t;
}
function ya(n) {
  return Uint8Array.from(n.replace(/^0x/, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" ")).buffer;
}
function Fl(n) {
  return n && n.__esModule && Object.prototype.hasOwnProperty.call(n, "default") ? n.default : n;
}
var Ts = { exports: {} }, qr;
function $l() {
  return qr || (qr = 1, (function(n, t) {
    (function(e) {
      var i = /^(?=((?:[a-zA-Z0-9+\-.]+:)?))\1(?=((?:\/\/[^\/?#]*)?))\2(?=((?:(?:[^?#\/]*\/)*[^;?#\/]*)?))\3((?:;[^?#]*)?)(\?[^#]*)?(#[^]*)?$/, s = /^(?=([^\/?#]*))\1([^]*)$/, r = /(?:\/|^)\.(?=\/)/g, a = /(?:\/|^)\.\.\/(?!\.\.\/)[^\/]*(?=\/)/g, o = {
        // If opts.alwaysNormalize is true then the path will always be normalized even when it starts with / or //
        // E.g
        // With opts.alwaysNormalize = false (default, spec compliant)
        // http://a.com/b/cd + /e/f/../g => http://a.com/e/f/../g
        // With opts.alwaysNormalize = true (not spec compliant)
        // http://a.com/b/cd + /e/f/../g => http://a.com/e/g
        buildAbsoluteURL: function(c, l, h) {
          if (h = h || {}, c = c.trim(), l = l.trim(), !l) {
            if (!h.alwaysNormalize)
              return c;
            var d = o.parseURL(c);
            if (!d)
              throw new Error("Error trying to parse base URL.");
            return d.path = o.normalizePath(
              d.path
            ), o.buildURLFromParts(d);
          }
          var u = o.parseURL(l);
          if (!u)
            throw new Error("Error trying to parse relative URL.");
          if (u.scheme)
            return h.alwaysNormalize ? (u.path = o.normalizePath(u.path), o.buildURLFromParts(u)) : l;
          var f = o.parseURL(c);
          if (!f)
            throw new Error("Error trying to parse base URL.");
          if (!f.netLoc && f.path && f.path[0] !== "/") {
            var g = s.exec(f.path);
            f.netLoc = g[1], f.path = g[2];
          }
          f.netLoc && !f.path && (f.path = "/");
          var v = {
            // 2c) Otherwise, the embedded URL inherits the scheme of
            // the base URL.
            scheme: f.scheme,
            netLoc: u.netLoc,
            path: null,
            params: u.params,
            query: u.query,
            fragment: u.fragment
          };
          if (!u.netLoc && (v.netLoc = f.netLoc, u.path[0] !== "/"))
            if (!u.path)
              v.path = f.path, u.params || (v.params = f.params, u.query || (v.query = f.query));
            else {
              var p = f.path, y = p.substring(0, p.lastIndexOf("/") + 1) + u.path;
              v.path = o.normalizePath(y);
            }
          return v.path === null && (v.path = h.alwaysNormalize ? o.normalizePath(u.path) : u.path), o.buildURLFromParts(v);
        },
        parseURL: function(c) {
          var l = i.exec(c);
          return l ? {
            scheme: l[1] || "",
            netLoc: l[2] || "",
            path: l[3] || "",
            params: l[4] || "",
            query: l[5] || "",
            fragment: l[6] || ""
          } : null;
        },
        normalizePath: function(c) {
          for (c = c.split("").reverse().join("").replace(r, ""); c.length !== (c = c.replace(a, "")).length; )
            ;
          return c.split("").reverse().join("");
        },
        buildURLFromParts: function(c) {
          return c.scheme + c.netLoc + c.path + c.params + c.query + c.fragment;
        }
      };
      n.exports = o;
    })();
  })(Ts)), Ts.exports;
}
var vr = $l();
class yr {
  constructor() {
    this.aborted = !1, this.loaded = 0, this.retry = 0, this.total = 0, this.chunkCount = 0, this.bwEstimate = 0, this.loading = {
      start: 0,
      first: 0,
      end: 0
    }, this.parsing = {
      start: 0,
      end: 0
    }, this.buffering = {
      start: 0,
      first: 0,
      end: 0
    };
  }
}
var at = {
  AUDIO: "audio",
  VIDEO: "video",
  AUDIOVIDEO: "audiovideo"
};
class Ea {
  constructor(t) {
    this._byteRange = null, this._url = null, this._stats = null, this._streams = null, this.base = void 0, this.relurl = void 0, typeof t == "string" && (t = {
      url: t
    }), this.base = t, Bl(this, "stats");
  }
  // setByteRange converts a EXT-X-BYTERANGE attribute into a two element array
  setByteRange(t, e) {
    const i = t.split("@", 2);
    let s;
    i.length === 1 ? s = (e == null ? void 0 : e.byteRangeEndOffset) || 0 : s = parseInt(i[1]), this._byteRange = [s, parseInt(i[0]) + s];
  }
  get baseurl() {
    return this.base.url;
  }
  get byteRange() {
    return this._byteRange === null ? [] : this._byteRange;
  }
  get byteRangeStartOffset() {
    return this.byteRange[0];
  }
  get byteRangeEndOffset() {
    return this.byteRange[1];
  }
  get elementaryStreams() {
    return this._streams === null && (this._streams = {
      [at.AUDIO]: null,
      [at.VIDEO]: null,
      [at.AUDIOVIDEO]: null
    }), this._streams;
  }
  set elementaryStreams(t) {
    this._streams = t;
  }
  get hasStats() {
    return this._stats !== null;
  }
  get hasStreams() {
    return this._streams !== null;
  }
  get stats() {
    return this._stats === null && (this._stats = new yr()), this._stats;
  }
  set stats(t) {
    this._stats = t;
  }
  get url() {
    return !this._url && this.baseurl && this.relurl && (this._url = vr.buildAbsoluteURL(this.baseurl, this.relurl, {
      alwaysNormalize: !0
    })), this._url || "";
  }
  set url(t) {
    this._url = t;
  }
  clearElementaryStreamInfo() {
    const {
      elementaryStreams: t
    } = this;
    t[at.AUDIO] = null, t[at.VIDEO] = null, t[at.AUDIOVIDEO] = null;
  }
}
function ut(n) {
  return n.sn !== "initSegment";
}
class Ss extends Ea {
  constructor(t, e) {
    super(e), this._decryptdata = null, this._programDateTime = null, this._ref = null, this._bitrate = void 0, this.rawProgramDateTime = null, this.tagList = [], this.duration = 0, this.sn = 0, this.levelkeys = void 0, this.type = void 0, this.loader = null, this.keyLoader = null, this.level = -1, this.cc = 0, this.startPTS = void 0, this.endPTS = void 0, this.startDTS = void 0, this.endDTS = void 0, this.start = 0, this.playlistOffset = 0, this.deltaPTS = void 0, this.maxStartPTS = void 0, this.minEndPTS = void 0, this.data = void 0, this.bitrateTest = !1, this.title = null, this.initSegment = null, this.endList = void 0, this.gap = void 0, this.urlId = 0, this.type = t;
  }
  get byteLength() {
    if (this.hasStats) {
      const t = this.stats.total;
      if (t)
        return t;
    }
    if (this.byteRange.length) {
      const t = this.byteRange[0], e = this.byteRange[1];
      if (B(t) && B(e))
        return e - t;
    }
    return null;
  }
  get bitrate() {
    return this.byteLength ? this.byteLength * 8 / this.duration : this._bitrate ? this._bitrate : null;
  }
  set bitrate(t) {
    this._bitrate = t;
  }
  get decryptdata() {
    var t;
    const {
      levelkeys: e
    } = this;
    if (!e || e.NONE)
      return null;
    if (e.identity)
      this._decryptdata || (this._decryptdata = e.identity.getDecryptData(this.sn));
    else if (!((t = this._decryptdata) != null && t.keyId)) {
      const i = Object.keys(e);
      if (i.length === 1) {
        const s = this._decryptdata = e[i[0]] || null;
        s && (this._decryptdata = s.getDecryptData(this.sn, e));
      }
    }
    return this._decryptdata;
  }
  get end() {
    return this.start + this.duration;
  }
  get endProgramDateTime() {
    if (this.programDateTime === null)
      return null;
    const t = B(this.duration) ? this.duration : 0;
    return this.programDateTime + t * 1e3;
  }
  get encrypted() {
    var t;
    if ((t = this._decryptdata) != null && t.encrypted)
      return !0;
    if (this.levelkeys) {
      var e;
      const i = Object.keys(this.levelkeys), s = i.length;
      if (s > 1 || s === 1 && (e = this.levelkeys[i[0]]) != null && e.encrypted)
        return !0;
    }
    return !1;
  }
  get programDateTime() {
    return this._programDateTime === null && this.rawProgramDateTime && (this.programDateTime = Date.parse(this.rawProgramDateTime)), this._programDateTime;
  }
  set programDateTime(t) {
    if (!B(t)) {
      this._programDateTime = this.rawProgramDateTime = null;
      return;
    }
    this._programDateTime = t;
  }
  get ref() {
    return ut(this) ? (this._ref || (this._ref = {
      base: this.base,
      start: this.start,
      duration: this.duration,
      sn: this.sn,
      programDateTime: this.programDateTime
    }), this._ref) : null;
  }
  addStart(t) {
    this.setStart(this.start + t);
  }
  setStart(t) {
    this.start = t, this._ref && (this._ref.start = t);
  }
  setDuration(t) {
    this.duration = t, this._ref && (this._ref.duration = t);
  }
  setKeyFormat(t) {
    const e = this.levelkeys;
    if (e) {
      var i;
      const s = e[t];
      s && !((i = this._decryptdata) != null && i.keyId) && (this._decryptdata = s.getDecryptData(this.sn, e));
    }
  }
  abortRequests() {
    var t, e;
    (t = this.loader) == null || t.abort(), (e = this.keyLoader) == null || e.abort();
  }
  setElementaryStreamInfo(t, e, i, s, r, a = !1) {
    const {
      elementaryStreams: o
    } = this, c = o[t];
    if (!c) {
      o[t] = {
        startPTS: e,
        endPTS: i,
        startDTS: s,
        endDTS: r,
        partial: a
      };
      return;
    }
    c.startPTS = Math.min(c.startPTS, e), c.endPTS = Math.max(c.endPTS, i), c.startDTS = Math.min(c.startDTS, s), c.endDTS = Math.max(c.endDTS, r);
  }
}
class Nl extends Ea {
  constructor(t, e, i, s, r) {
    super(i), this.fragOffset = 0, this.duration = 0, this.gap = !1, this.independent = !1, this.relurl = void 0, this.fragment = void 0, this.index = void 0, this.duration = t.decimalFloatingPoint("DURATION"), this.gap = t.bool("GAP"), this.independent = t.bool("INDEPENDENT"), this.relurl = t.enumeratedString("URI"), this.fragment = e, this.index = s;
    const a = t.enumeratedString("BYTERANGE");
    a && this.setByteRange(a, r), r && (this.fragOffset = r.fragOffset + r.duration);
  }
  get start() {
    return this.fragment.start + this.fragOffset;
  }
  get end() {
    return this.start + this.duration;
  }
  get loaded() {
    const {
      elementaryStreams: t
    } = this;
    return !!(t.audio || t.video || t.audiovideo);
  }
}
function Ta(n, t) {
  const e = Object.getPrototypeOf(n);
  if (e) {
    const i = Object.getOwnPropertyDescriptor(e, t);
    return i || Ta(e, t);
  }
}
function Bl(n, t) {
  const e = Ta(n, t);
  e && (e.enumerable = !0, Object.defineProperty(n, t, e));
}
const Xr = Math.pow(2, 32) - 1, Ul = [].push, Sa = {
  video: 1,
  audio: 2,
  id3: 3,
  text: 4
};
function vt(n) {
  return String.fromCharCode.apply(null, n);
}
function xa(n, t) {
  const e = n[t] << 8 | n[t + 1];
  return e < 0 ? 65536 + e : e;
}
function j(n, t) {
  const e = Aa(n, t);
  return e < 0 ? 4294967296 + e : e;
}
function Qr(n, t) {
  let e = j(n, t);
  return e *= Math.pow(2, 32), e += j(n, t + 4), e;
}
function Aa(n, t) {
  return n[t] << 24 | n[t + 1] << 16 | n[t + 2] << 8 | n[t + 3];
}
function Gl(n) {
  const t = n.byteLength;
  for (let e = 0; e < t; ) {
    const i = j(n, e);
    if (i > 8 && n[e + 4] === 109 && n[e + 5] === 111 && n[e + 6] === 111 && n[e + 7] === 102)
      return !0;
    e = i > 1 ? e + i : t;
  }
  return !1;
}
function Z(n, t) {
  const e = [];
  if (!t.length)
    return e;
  const i = n.byteLength;
  for (let s = 0; s < i; ) {
    const r = j(n, s), a = vt(n.subarray(s + 4, s + 8)), o = r > 1 ? s + r : i;
    if (a === t[0])
      if (t.length === 1)
        e.push(n.subarray(s + 8, o));
      else {
        const c = Z(n.subarray(s + 8, o), t.slice(1));
        c.length && Ul.apply(e, c);
      }
    s = o;
  }
  return e;
}
function Kl(n) {
  const t = [], e = n[0];
  let i = 8;
  const s = j(n, i);
  i += 4;
  let r = 0, a = 0;
  e === 0 ? (r = j(n, i), a = j(n, i + 4), i += 8) : (r = Qr(n, i), a = Qr(n, i + 8), i += 16), i += 2;
  let o = n.length + a;
  const c = xa(n, i);
  i += 2;
  for (let l = 0; l < c; l++) {
    let h = i;
    const d = j(n, h);
    h += 4;
    const u = d & 2147483647;
    if ((d & 2147483648) >>> 31 === 1)
      return rt.warn("SIDX has hierarchical references (not supported)"), null;
    const g = j(n, h);
    h += 4, t.push({
      referenceSize: u,
      subsegmentDuration: g,
      // unscaled
      info: {
        duration: g / s,
        start: o,
        end: o + u - 1
      }
    }), o += u, h += 4, i = h;
  }
  return {
    earliestPresentationTime: r,
    timescale: s,
    version: e,
    referencesCount: c,
    references: t
  };
}
function ba(n) {
  const t = [], e = Z(n, ["moov", "trak"]);
  for (let s = 0; s < e.length; s++) {
    const r = e[s], a = Z(r, ["tkhd"])[0];
    if (a) {
      let o = a[0];
      const c = j(a, o === 0 ? 12 : 20), l = Z(r, ["mdia", "mdhd"])[0];
      if (l) {
        o = l[0];
        const h = j(l, o === 0 ? 12 : 20), d = Z(r, ["mdia", "hdlr"])[0];
        if (d) {
          const u = vt(d.subarray(8, 12)), f = {
            soun: at.AUDIO,
            vide: at.VIDEO
          }[u], g = Z(r, ["mdia", "minf", "stbl", "stsd"])[0], v = Hl(g);
          f ? (t[c] = {
            timescale: h,
            type: f,
            stsd: v
          }, t[f] = st({
            timescale: h,
            id: c
          }, v)) : t[c] = {
            timescale: h,
            type: u,
            stsd: v
          };
        }
      }
    }
  }
  return Z(n, ["moov", "mvex", "trex"]).forEach((s) => {
    const r = j(s, 4), a = t[r];
    a && (a.default = {
      duration: j(s, 12),
      flags: j(s, 20)
    });
  }), t;
}
function Hl(n) {
  const t = n.subarray(8), e = t.subarray(86), i = vt(t.subarray(4, 8));
  let s = i, r;
  const a = i === "enca" || i === "encv";
  if (a) {
    const l = Z(t, [i])[0].subarray(i === "enca" ? 28 : 78);
    Z(l, ["sinf"]).forEach((d) => {
      const u = Z(d, ["schm"])[0];
      if (u) {
        const f = vt(u.subarray(4, 8));
        if (f === "cbcs" || f === "cenc") {
          const g = Z(d, ["frma"])[0];
          g && (s = vt(g));
        }
      }
    });
  }
  const o = s;
  switch (s) {
    case "avc1":
    case "avc2":
    case "avc3":
    case "avc4": {
      const c = Z(e, ["avcC"])[0];
      c && c.length > 3 && (s += "." + Ri(c[1]) + Ri(c[2]) + Ri(c[3]), r = Li(o === "avc1" ? "dva1" : "dvav", e));
      break;
    }
    case "mp4a": {
      const c = Z(t, [i])[0], l = Z(c.subarray(28), ["esds"])[0];
      if (l && l.length > 7) {
        let h = 4;
        if (l[h++] !== 3)
          break;
        h = xs(l, h), h += 2;
        const d = l[h++];
        if (d & 128 && (h += 2), d & 64 && (h += l[h++]), l[h++] !== 4)
          break;
        h = xs(l, h);
        const u = l[h++];
        if (u === 64)
          s += "." + Ri(u);
        else
          break;
        if (h += 12, l[h++] !== 5)
          break;
        h = xs(l, h);
        const f = l[h++];
        let g = (f & 248) >> 3;
        g === 31 && (g += 1 + ((f & 7) << 3) + ((l[h] & 224) >> 5)), s += "." + g;
      }
      break;
    }
    case "hvc1":
    case "hev1": {
      const c = Z(e, ["hvcC"])[0];
      if (c && c.length > 12) {
        const l = c[1], h = ["", "A", "B", "C"][l >> 6], d = l & 31, u = j(c, 2), f = (l & 32) >> 5 ? "H" : "L", g = c[12], v = c.subarray(6, 12);
        s += "." + h + d, s += "." + Vl(u).toString(16).toUpperCase(), s += "." + f + g;
        let p = "";
        for (let y = v.length; y--; ) {
          const E = v[y];
          (E || p) && (p = "." + E.toString(16).toUpperCase() + p);
        }
        s += p;
      }
      r = Li(o == "hev1" ? "dvhe" : "dvh1", e);
      break;
    }
    case "dvh1":
    case "dvhe":
    case "dvav":
    case "dva1":
    case "dav1": {
      s = Li(s, e) || s;
      break;
    }
    case "vp09": {
      const c = Z(e, ["vpcC"])[0];
      if (c && c.length > 6) {
        const l = c[4], h = c[5], d = c[6] >> 4 & 15;
        s += "." + jt(l) + "." + jt(h) + "." + jt(d);
      }
      break;
    }
    case "av01": {
      const c = Z(e, ["av1C"])[0];
      if (c && c.length > 2) {
        const l = c[1] >>> 5, h = c[1] & 31, d = c[2] >>> 7 ? "H" : "M", u = (c[2] & 64) >> 6, f = (c[2] & 32) >> 5, g = l === 2 && u ? f ? 12 : 10 : u ? 10 : 8, v = (c[2] & 16) >> 4, p = (c[2] & 8) >> 3, y = (c[2] & 4) >> 2, E = c[2] & 3;
        s += "." + l + "." + jt(h) + d + "." + jt(g) + "." + v + "." + p + y + E + "." + jt(1) + "." + jt(1) + "." + jt(1) + "." + 0, r = Li("dav1", e);
      }
      break;
    }
  }
  return {
    codec: s,
    encrypted: a,
    supplemental: r
  };
}
function Li(n, t) {
  const e = Z(t, ["dvvC"]), i = e.length ? e[0] : Z(t, ["dvcC"])[0];
  if (i) {
    const s = i[2] >> 1 & 127, r = i[2] << 5 & 32 | i[3] >> 3 & 31;
    return n + "." + jt(s) + "." + jt(r);
  }
}
function Vl(n) {
  let t = 0;
  for (let e = 0; e < 32; e++)
    t |= (n >> e & 1) << 31 - e;
  return t >>> 0;
}
function xs(n, t) {
  const e = t + 5;
  for (; n[t++] & 128 && t < e; )
    ;
  return t;
}
function Ri(n) {
  return ("0" + n.toString(16).toUpperCase()).slice(-2);
}
function jt(n) {
  return (n < 10 ? "0" : "") + n;
}
function Wl(n, t) {
  if (!n || !t)
    return;
  const e = t.keyId;
  e && t.isCommonEncryption && Ia(n, (i, s) => {
    const r = i.subarray(8, 24);
    r.some((a) => a !== 0) || (rt.log(`[eme] Patching keyId in 'enc${s ? "a" : "v"}>sinf>>tenc' box: ${At(r)} -> ${At(e)}`), i.set(e, 8));
  });
}
function Yl(n) {
  const t = [];
  return Ia(n, (e) => t.push(e.subarray(8, 24))), t;
}
function Ia(n, t) {
  Z(n, ["moov", "trak"]).forEach((i) => {
    const s = Z(i, ["mdia", "minf", "stbl", "stsd"])[0];
    if (!s) return;
    const r = s.subarray(8);
    let a = Z(r, ["enca"]);
    const o = a.length > 0;
    o || (a = Z(r, ["encv"])), a.forEach((c) => {
      const l = o ? c.subarray(28) : c.subarray(78);
      Z(l, ["sinf"]).forEach((d) => {
        const u = La(d);
        u && t(u, o);
      });
    });
  });
}
function La(n) {
  const t = Z(n, ["schm"])[0];
  if (t) {
    const e = vt(t.subarray(4, 8));
    if (e === "cbcs" || e === "cenc") {
      const i = Z(n, ["schi", "tenc"])[0];
      if (i)
        return i;
    }
  }
}
function zl(n, t, e) {
  const i = {}, s = Z(n, ["moof", "traf"]);
  for (let r = 0; r < s.length; r++) {
    const a = s[r], o = Z(a, ["tfhd"])[0], c = j(o, 4), l = t[c];
    if (!l)
      continue;
    i[c] || (i[c] = {
      start: NaN,
      duration: 0,
      sampleCount: 0,
      timescale: l.timescale,
      type: l.type
    });
    const h = i[c], d = Z(a, ["tfdt"])[0];
    if (d) {
      const T = d[0];
      let S = j(d, 4);
      T === 1 && (S === Xr ? e.warn("[mp4-demuxer]: Ignoring assumed invalid signed 64-bit track fragment decode time") : (S *= Xr + 1, S += j(d, 8))), B(S) && (!B(h.start) || S < h.start) && (h.start = S);
    }
    const u = l.default, f = j(o, 0) | (u == null ? void 0 : u.flags);
    let g = (u == null ? void 0 : u.duration) || 0;
    f & 8 && (f & 2 ? g = j(o, 12) : g = j(o, 8));
    const v = Z(a, ["trun"]);
    let p = h.start || 0, y = 0, E = g;
    for (let T = 0; T < v.length; T++) {
      const S = v[T], x = j(S, 4), D = h.sampleCount;
      h.sampleCount += x;
      const A = S[3] & 1, _ = S[3] & 4, R = S[2] & 1, b = S[2] & 2, C = S[2] & 4, F = S[2] & 8;
      let U = 8, W = x;
      for (A && (U += 4), _ && x && (!(S[U + 1] & 1) && h.keyFrameIndex === void 0 && (h.keyFrameIndex = D), U += 4, R ? (E = j(S, U), U += 4) : E = g, b && (U += 4), F && (U += 4), p += E, y += E, W--); W--; )
        R ? (E = j(S, U), U += 4) : E = g, b && (U += 4), C && (S[U + 1] & 1 || h.keyFrameIndex === void 0 && (h.keyFrameIndex = h.sampleCount - (W + 1), h.keyFrameStart = p), U += 4), F && (U += 4), p += E, y += E;
      !y && g && (y += g * x);
    }
    h.duration += y;
  }
  if (!Object.keys(i).some((r) => i[r].duration)) {
    let r = 1 / 0, a = 0;
    const o = Z(n, ["sidx"]);
    for (let c = 0; c < o.length; c++) {
      const l = Kl(o[c]);
      if (l != null && l.references) {
        r = Math.min(r, l.earliestPresentationTime / l.timescale);
        const h = l.references.reduce((d, u) => d + u.info.duration || 0, 0);
        a = Math.max(a, h + l.earliestPresentationTime / l.timescale);
      }
    }
    a && B(a) && Object.keys(i).forEach((c) => {
      i[c].duration || (i[c].duration = a * i[c].timescale - i[c].start);
    });
  }
  return i;
}
function jl(n) {
  const t = {
    valid: null,
    remainder: null
  }, e = Z(n, ["moof"]);
  if (e.length < 2)
    return t.remainder = n, t;
  const i = e[e.length - 1];
  return t.valid = n.slice(0, i.byteOffset - 8), t.remainder = n.slice(i.byteOffset - 8), t;
}
function Nt(n, t) {
  const e = new Uint8Array(n.length + t.length);
  return e.set(n), e.set(t, n.length), e;
}
function Zr(n, t) {
  const e = [], i = t.samples, s = t.timescale, r = t.id;
  let a = !1;
  return Z(i, ["moof"]).map((c) => {
    const l = c.byteOffset - 8;
    Z(c, ["traf"]).map((d) => {
      const u = Z(d, ["tfdt"]).map((f) => {
        const g = f[0];
        let v = j(f, 4);
        return g === 1 && (v *= Math.pow(2, 32), v += j(f, 8)), v / s;
      })[0];
      return u !== void 0 && (n = u), Z(d, ["tfhd"]).map((f) => {
        const g = j(f, 4), v = j(f, 0) & 16777215, p = (v & 1) !== 0, y = (v & 2) !== 0, E = (v & 8) !== 0;
        let T = 0;
        const S = (v & 16) !== 0;
        let x = 0;
        const D = (v & 32) !== 0;
        let A = 8;
        g === r && (p && (A += 8), y && (A += 4), E && (T = j(f, A), A += 4), S && (x = j(f, A), A += 4), D && (A += 4), t.type === "video" && (a = us(t.codec)), Z(d, ["trun"]).map((_) => {
          const R = _[0], b = j(_, 0) & 16777215, C = (b & 1) !== 0;
          let F = 0;
          const U = (b & 4) !== 0, W = (b & 256) !== 0;
          let G = 0;
          const k = (b & 512) !== 0;
          let H = 0;
          const $ = (b & 1024) !== 0, V = (b & 2048) !== 0;
          let z = 0;
          const O = j(_, 4);
          let M = 8;
          C && (F = j(_, M), M += 4), U && (M += 4);
          let X = F + l;
          for (let et = 0; et < O; et++) {
            if (W ? (G = j(_, M), M += 4) : G = T, k ? (H = j(_, M), M += 4) : H = x, $ && (M += 4), V && (R === 0 ? z = j(_, M) : z = Aa(_, M), M += 4), t.type === at.VIDEO) {
              let Q = 0;
              for (; Q < H; ) {
                const J = j(i, X);
                if (X += 4, ql(a, i[X])) {
                  const pt = i.subarray(X, X + J);
                  Er(pt, a ? 2 : 1, n + z / s, e);
                }
                X += J, Q += J + 4;
              }
            }
            n += G / s;
          }
        }));
      });
    });
  }), e;
}
function us(n) {
  if (!n)
    return !1;
  const t = n.substring(0, 4);
  return t === "hvc1" || t === "hev1" || // Dolby Vision
  t === "dvh1" || t === "dvhe";
}
function ql(n, t) {
  if (n) {
    const e = t >> 1 & 63;
    return e === 39 || e === 40;
  } else
    return (t & 31) === 6;
}
function Er(n, t, e, i) {
  const s = Ra(n);
  let r = 0;
  r += t;
  let a = 0, o = 0, c = 0;
  for (; r < s.length; ) {
    a = 0;
    do {
      if (r >= s.length)
        break;
      c = s[r++], a += c;
    } while (c === 255);
    o = 0;
    do {
      if (r >= s.length)
        break;
      c = s[r++], o += c;
    } while (c === 255);
    const l = s.length - r;
    let h = r;
    if (o < l)
      r += o;
    else if (o > l) {
      rt.error(`Malformed SEI payload. ${o} is too small, only ${l} bytes left to parse.`);
      break;
    }
    if (a === 4) {
      if (s[h++] === 181) {
        const u = xa(s, h);
        if (h += 2, u === 49) {
          const f = j(s, h);
          if (h += 4, f === 1195456820) {
            const g = s[h++];
            if (g === 3) {
              const v = s[h++], p = 31 & v, y = 64 & v, E = y ? 2 + p * 3 : 0, T = new Uint8Array(E);
              if (y) {
                T[0] = v;
                for (let S = 1; S < E; S++)
                  T[S] = s[h++];
              }
              i.push({
                type: g,
                payloadType: a,
                pts: e,
                bytes: T
              });
            }
          }
        }
      }
    } else if (a === 5 && o > 16) {
      const d = [];
      for (let g = 0; g < 16; g++) {
        const v = s[h++].toString(16);
        d.push(v.length == 1 ? "0" + v : v), (g === 3 || g === 5 || g === 7 || g === 9) && d.push("-");
      }
      const u = o - 16, f = new Uint8Array(u);
      for (let g = 0; g < u; g++)
        f[g] = s[h++];
      i.push({
        payloadType: a,
        pts: e,
        uuid: d.join(""),
        userData: Ft(f),
        userDataBytes: f
      });
    }
  }
}
function Ra(n) {
  const t = n.byteLength, e = [];
  let i = 1;
  for (; i < t - 2; )
    n[i] === 0 && n[i + 1] === 0 && n[i + 2] === 3 ? (e.push(i + 2), i += 2) : i++;
  if (e.length === 0)
    return n;
  const s = t - e.length, r = new Uint8Array(s);
  let a = 0;
  for (i = 0; i < s; a++, i++)
    a === e[0] && (a++, e.shift()), r[i] = n[a];
  return r;
}
function Xl(n) {
  const t = n[0];
  let e = "", i = "", s = 0, r = 0, a = 0, o = 0, c = 0, l = 0;
  if (t === 0) {
    for (; vt(n.subarray(l, l + 1)) !== "\0"; )
      e += vt(n.subarray(l, l + 1)), l += 1;
    for (e += vt(n.subarray(l, l + 1)), l += 1; vt(n.subarray(l, l + 1)) !== "\0"; )
      i += vt(n.subarray(l, l + 1)), l += 1;
    i += vt(n.subarray(l, l + 1)), l += 1, s = j(n, 12), r = j(n, 16), o = j(n, 20), c = j(n, 24), l = 28;
  } else if (t === 1) {
    l += 4, s = j(n, l), l += 4;
    const d = j(n, l);
    l += 4;
    const u = j(n, l);
    for (l += 4, a = 2 ** 32 * d + u, Ll(a) || (a = Number.MAX_SAFE_INTEGER, rt.warn("Presentation time exceeds safe integer limit and wrapped to max safe integer in parsing emsg box")), o = j(n, l), l += 4, c = j(n, l), l += 4; vt(n.subarray(l, l + 1)) !== "\0"; )
      e += vt(n.subarray(l, l + 1)), l += 1;
    for (e += vt(n.subarray(l, l + 1)), l += 1; vt(n.subarray(l, l + 1)) !== "\0"; )
      i += vt(n.subarray(l, l + 1)), l += 1;
    i += vt(n.subarray(l, l + 1)), l += 1;
  }
  const h = n.subarray(l, n.byteLength);
  return {
    schemeIdUri: e,
    value: i,
    timeScale: s,
    presentationTime: a,
    presentationTimeDelta: r,
    eventDuration: o,
    id: c,
    payload: h
  };
}
function Ql(n, ...t) {
  const e = t.length;
  let i = 8, s = e;
  for (; s--; )
    i += t[s].byteLength;
  const r = new Uint8Array(i);
  for (r[0] = i >> 24 & 255, r[1] = i >> 16 & 255, r[2] = i >> 8 & 255, r[3] = i & 255, r.set(n, 4), s = 0, i = 8; s < e; s++)
    r.set(t[s], i), i += t[s].byteLength;
  return r;
}
function Zl(n, t, e) {
  if (n.byteLength !== 16)
    throw new RangeError("Invalid system id");
  let i, s;
  i = 0, s = new Uint8Array();
  let r;
  i > 0 ? (r = new Uint8Array(4), t.length > 0 && new DataView(r.buffer).setUint32(0, t.length, !1)) : r = new Uint8Array();
  const a = new Uint8Array(4);
  return e.byteLength > 0 && new DataView(a.buffer).setUint32(0, e.byteLength, !1), Ql(
    [112, 115, 115, 104],
    new Uint8Array([
      i,
      0,
      0,
      0
      // Flags
    ]),
    n,
    // 16 bytes
    r,
    s,
    a,
    e
  );
}
function Jl(n) {
  const t = [];
  if (n instanceof ArrayBuffer) {
    const e = n.byteLength;
    let i = 0;
    for (; i + 32 < e; ) {
      const s = new DataView(n, i), r = tc(s);
      t.push(r), i += r.size;
    }
  }
  return t;
}
function tc(n) {
  const t = n.getUint32(0), e = n.byteOffset, i = n.byteLength;
  if (i < t)
    return {
      offset: e,
      size: i
    };
  if (n.getUint32(4) !== 1886614376)
    return {
      offset: e,
      size: t
    };
  const r = n.getUint32(8) >>> 24;
  if (r !== 0 && r !== 1)
    return {
      offset: e,
      size: t
    };
  const a = n.buffer, o = At(new Uint8Array(a, e + 12, 16));
  let c = null, l = null, h = 0;
  if (r === 0)
    h = 28;
  else {
    const u = n.getUint32(28);
    if (!u || i < 32 + u * 16)
      return {
        offset: e,
        size: t
      };
    c = [];
    for (let f = 0; f < u; f++)
      c.push(new Uint8Array(a, e + 32 + f * 16, 16));
    h = 32 + u * 16;
  }
  if (!h)
    return {
      offset: e,
      size: t
    };
  const d = n.getUint32(h);
  return t - 32 < d ? {
    offset: e,
    size: t
  } : (l = new Uint8Array(a, e + h + 4, d), {
    version: r,
    systemId: o,
    kids: c,
    data: l,
    offset: e,
    size: t
  });
}
const _a = () => /\(Windows.+Firefox\//i.test(navigator.userAgent), Xe = {
  audio: {
    a3ds: 1,
    "ac-3": 0.95,
    "ac-4": 1,
    alac: 0.9,
    alaw: 1,
    dra1: 1,
    "dts+": 1,
    "dts-": 1,
    dtsc: 1,
    dtse: 1,
    dtsh: 1,
    "ec-3": 0.9,
    enca: 1,
    fLaC: 0.9,
    // MP4-RA listed codec entry for FLAC
    flac: 0.9,
    // legacy browser codec name for FLAC
    FLAC: 0.9,
    // some manifests may list "FLAC" with Apple's tools
    g719: 1,
    g726: 1,
    m4ae: 1,
    mha1: 1,
    mha2: 1,
    mhm1: 1,
    mhm2: 1,
    mlpa: 1,
    mp4a: 1,
    "raw ": 1,
    Opus: 1,
    opus: 1,
    // browsers expect this to be lowercase despite MP4RA says 'Opus'
    samr: 1,
    sawb: 1,
    sawp: 1,
    sevc: 1,
    sqcp: 1,
    ssmv: 1,
    twos: 1,
    ulaw: 1
  },
  video: {
    avc1: 1,
    avc2: 1,
    avc3: 1,
    avc4: 1,
    avcp: 1,
    av01: 0.8,
    dav1: 0.8,
    drac: 1,
    dva1: 1,
    dvav: 1,
    dvh1: 0.7,
    dvhe: 0.7,
    encv: 1,
    hev1: 0.75,
    hvc1: 0.75,
    mjp2: 1,
    mp4v: 1,
    mvc1: 1,
    mvc2: 1,
    mvc3: 1,
    mvc4: 1,
    resv: 1,
    rv60: 1,
    s263: 1,
    svc1: 1,
    svc2: 1,
    "vc-1": 1,
    vp08: 1,
    vp09: 0.9
  },
  text: {
    stpp: 1,
    wvtt: 1
  }
};
function Tr(n, t) {
  const e = Xe[t];
  return !!e && !!e[n.slice(0, 4)];
}
function gi(n, t, e = !0) {
  return !n.split(",").some((i) => !Sr(i, t, e));
}
function Sr(n, t, e = !0) {
  var i;
  const s = ge(e);
  return (i = s == null ? void 0 : s.isTypeSupported(mi(n, t))) != null ? i : !1;
}
function mi(n, t) {
  return `${t}/mp4;codecs=${n}`;
}
function Jr(n) {
  if (n) {
    const t = n.substring(0, 4);
    return Xe.video[t];
  }
  return 2;
}
function Qi(n) {
  const t = _a();
  return n.split(",").reduce((e, i) => {
    const r = t && us(i) ? 9 : Xe.video[i];
    return r ? (r * 2 + e) / (e ? 3 : 2) : (Xe.audio[i] + e) / (e ? 2 : 1);
  }, 0);
}
const As = {};
function ec(n, t = !0) {
  if (As[n])
    return As[n];
  const e = {
    // Idealy fLaC and Opus would be first (spec-compliant) but
    // some browsers will report that fLaC is supported then fail.
    // see: https://bugs.chromium.org/p/chromium/issues/detail?id=1422728
    flac: ["flac", "fLaC", "FLAC"],
    opus: ["opus", "Opus"],
    // Replace audio codec info if browser does not support mp4a.40.34,
    // and demuxer can fallback to 'audio/mpeg' or 'audio/mp4;codecs="mp3"'
    "mp4a.40.34": ["mp3"]
  }[n];
  for (let s = 0; s < e.length; s++) {
    var i;
    if (Sr(e[s], "audio", t))
      return As[n] = e[s], e[s];
    if (e[s] === "mp3" && (i = ge(t)) != null && i.isTypeSupported("audio/mpeg"))
      return "";
  }
  return n;
}
const ic = /flac|opus|mp4a\.40\.34/i;
function Zi(n, t = !0) {
  return n.replace(ic, (e) => ec(e.toLowerCase(), t));
}
function sc(n, t) {
  const e = [];
  if (n) {
    const i = n.split(",");
    for (let s = 0; s < i.length; s++)
      Tr(i[s], "video") || e.push(i[s]);
  }
  return t && e.push(t), e.join(",");
}
function Gi(n, t) {
  if (n && (n.length > 4 || ["ac-3", "ec-3", "alac", "fLaC", "Opus"].indexOf(n) !== -1) && (tn(n, "audio") || tn(n, "video")))
    return n;
  if (t) {
    const e = t.split(",");
    if (e.length > 1) {
      if (n) {
        for (let i = e.length; i--; )
          if (e[i].substring(0, 4) === n.substring(0, 4))
            return e[i];
      }
      return e[0];
    }
  }
  return t || n;
}
function tn(n, t) {
  return Tr(n, t) && Sr(n, t);
}
function rc(n) {
  const t = n.split(",");
  for (let e = 0; e < t.length; e++) {
    const i = t[e].split(".");
    i.length > 2 && i[0] === "avc1" && (t[e] = `avc1.${parseInt(i[1]).toString(16)}${("000" + parseInt(i[2]).toString(16)).slice(-4)}`);
  }
  return t.join(",");
}
function nc(n) {
  if (n.startsWith("av01.")) {
    const t = n.split("."), e = ["0", "111", "01", "01", "01", "0"];
    for (let i = t.length; i > 4 && i < 10; i++)
      t[i] = e[i - 4];
    return t.join(".");
  }
  return n;
}
function en(n) {
  const t = ge(n) || {
    isTypeSupported: () => !1
  };
  return {
    mpeg: t.isTypeSupported("audio/mpeg"),
    mp3: t.isTypeSupported('audio/mp4; codecs="mp3"'),
    ac3: t.isTypeSupported('audio/mp4; codecs="ac-3"')
  };
}
function Qs(n) {
  return n.replace(/^.+codecs=["']?([^"']+).*$/, "$1");
}
const ac = {
  supported: !0,
  powerEfficient: !0,
  smooth: !0
  // keySystemAccess: null,
}, oc = {
  supported: !1,
  smooth: !1,
  powerEfficient: !1
  // keySystemAccess: null,
}, Da = {
  supported: !0,
  configurations: [],
  decodingInfoResults: [ac]
};
function wa(n, t) {
  return {
    supported: !1,
    configurations: t,
    decodingInfoResults: [oc],
    error: n
  };
}
function lc(n, t, e, i, s, r) {
  const a = n.videoCodec, o = n.audioCodec ? n.audioGroups : null, c = r == null ? void 0 : r.audioCodec, l = r == null ? void 0 : r.channels, h = l ? parseInt(l) : c ? 1 / 0 : 2;
  let d = null;
  if (o != null && o.length)
    try {
      o.length === 1 && o[0] ? d = t.groups[o[0]].channels : d = o.reduce((u, f) => {
        if (f) {
          const g = t.groups[f];
          if (!g)
            throw new Error(`Audio track group ${f} not found`);
          Object.keys(g.channels).forEach((v) => {
            u[v] = (u[v] || 0) + g.channels[v];
          });
        }
        return u;
      }, {
        2: 0
      });
    } catch {
      return !0;
    }
  return a !== void 0 && // Force media capabilities check for HEVC to avoid failure on Windows
  (a.split(",").some((u) => us(u)) || n.width > 1920 && n.height > 1088 || n.height > 1920 && n.width > 1088 || n.frameRate > Math.max(i, 30) || n.videoRange !== "SDR" && n.videoRange !== e || n.bitrate > Math.max(s, 8e6)) || !!d && B(h) && Object.keys(d).some((u) => parseInt(u) > h);
}
function Ca(n, t, e, i = {}) {
  const s = n.videoCodec;
  if (!s && !n.audioCodec || !e)
    return Promise.resolve(Da);
  const r = [], a = cc(n), o = a.length, c = hc(n, t, o > 0), l = c.length;
  for (let h = o || 1 * l || 1; h--; ) {
    const d = {
      type: "media-source"
    };
    if (o && (d.video = a[h % o]), l) {
      d.audio = c[h % l];
      const u = d.audio.bitrate;
      d.video && u && (d.video.bitrate -= u);
    }
    r.push(d);
  }
  if (s) {
    const h = navigator.userAgent;
    if (s.split(",").some((d) => us(d)) && _a())
      return Promise.resolve(wa(new Error(`Overriding Windows Firefox HEVC MediaCapabilities result based on user-agent string: (${h})`), r));
  }
  return Promise.all(r.map((h) => {
    const d = uc(h);
    return i[d] || (i[d] = e.decodingInfo(h));
  })).then((h) => ({
    supported: !h.some((d) => !d.supported),
    configurations: r,
    decodingInfoResults: h
  })).catch((h) => ({
    supported: !1,
    configurations: r,
    decodingInfoResults: [],
    error: h
  }));
}
function cc(n) {
  var t;
  const e = (t = n.videoCodec) == null ? void 0 : t.split(","), i = Pa(n), s = n.width || 640, r = n.height || 480, a = n.frameRate || 30, o = n.videoRange.toLowerCase();
  return e ? e.map((c) => {
    const l = {
      contentType: mi(nc(c), "video"),
      width: s,
      height: r,
      bitrate: i,
      framerate: a
    };
    return o !== "sdr" && (l.transferFunction = o), l;
  }) : [];
}
function hc(n, t, e) {
  var i;
  const s = (i = n.audioCodec) == null ? void 0 : i.split(","), r = Pa(n);
  return s && n.audioGroups ? n.audioGroups.reduce((a, o) => {
    var c;
    const l = o ? (c = t.groups[o]) == null ? void 0 : c.tracks : null;
    return l ? l.reduce((h, d) => {
      if (d.groupId === o) {
        const u = parseFloat(d.channels || "");
        s.forEach((f) => {
          const g = {
            contentType: mi(f, "audio"),
            bitrate: e ? dc(f, r) : r
          };
          u && (g.channels = "" + u), h.push(g);
        });
      }
      return h;
    }, a) : a;
  }, []) : [];
}
function dc(n, t) {
  if (t <= 1)
    return 1;
  let e = 128e3;
  return n === "ec-3" ? e = 768e3 : n === "ac-3" && (e = 64e4), Math.min(t / 2, e);
}
function Pa(n) {
  return Math.ceil(Math.max(n.bitrate * 0.9, n.averageBitrate) / 1e3) * 1e3 || 1;
}
function uc(n) {
  let t = "";
  const {
    audio: e,
    video: i
  } = n;
  if (i) {
    const s = Qs(i.contentType);
    t += `${s}_r${i.height}x${i.width}f${Math.ceil(i.framerate)}${i.transferFunction || "sd"}_${Math.ceil(i.bitrate / 1e5)}`;
  }
  if (e) {
    const s = Qs(e.contentType);
    t += `${i ? "_" : ""}${s}_c${e.channels}`;
  }
  return t;
}
const Zs = ["NONE", "TYPE-0", "TYPE-1", null];
function fc(n) {
  return Zs.indexOf(n) > -1;
}
const Ji = ["SDR", "PQ", "HLG"];
function gc(n) {
  return !!n && Ji.indexOf(n) > -1;
}
var Ki = {
  No: "",
  Yes: "YES",
  v2: "v2"
};
function sn(n) {
  const {
    canSkipUntil: t,
    canSkipDateRanges: e,
    age: i
  } = n, s = i < t / 2;
  return t && s ? e ? Ki.v2 : Ki.Yes : Ki.No;
}
class rn {
  constructor(t, e, i) {
    this.msn = void 0, this.part = void 0, this.skip = void 0, this.msn = t, this.part = e, this.skip = i;
  }
  addDirectives(t) {
    const e = new self.URL(t);
    return this.msn !== void 0 && e.searchParams.set("_HLS_msn", this.msn.toString()), this.part !== void 0 && e.searchParams.set("_HLS_part", this.part.toString()), this.skip && e.searchParams.set("_HLS_skip", this.skip), e.href;
  }
}
class pi {
  constructor(t) {
    if (this._attrs = void 0, this.audioCodec = void 0, this.bitrate = void 0, this.codecSet = void 0, this.url = void 0, this.frameRate = void 0, this.height = void 0, this.id = void 0, this.name = void 0, this.supplemental = void 0, this.videoCodec = void 0, this.width = void 0, this.details = void 0, this.fragmentError = 0, this.loadError = 0, this.loaded = void 0, this.realBitrate = 0, this.supportedPromise = void 0, this.supportedResult = void 0, this._avgBitrate = 0, this._audioGroups = void 0, this._subtitleGroups = void 0, this._urlId = 0, this.url = [t.url], this._attrs = [t.attrs], this.bitrate = t.bitrate, t.details && (this.details = t.details), this.id = t.id || 0, this.name = t.name, this.width = t.width || 0, this.height = t.height || 0, this.frameRate = t.attrs.optionalFloat("FRAME-RATE", 0), this._avgBitrate = t.attrs.decimalInteger("AVERAGE-BANDWIDTH"), this.audioCodec = t.audioCodec, this.videoCodec = t.videoCodec, this.codecSet = [t.videoCodec, t.audioCodec].filter((i) => !!i).map((i) => i.substring(0, 4)).join(","), "supplemental" in t) {
      var e;
      this.supplemental = t.supplemental;
      const i = (e = t.supplemental) == null ? void 0 : e.videoCodec;
      i && i !== t.videoCodec && (this.codecSet += `,${i.substring(0, 4)}`);
    }
    this.addGroupId("audio", t.attrs.AUDIO), this.addGroupId("text", t.attrs.SUBTITLES);
  }
  get maxBitrate() {
    return Math.max(this.realBitrate, this.bitrate);
  }
  get averageBitrate() {
    return this._avgBitrate || this.realBitrate || this.bitrate;
  }
  get attrs() {
    return this._attrs[0];
  }
  get codecs() {
    return this.attrs.CODECS || "";
  }
  get pathwayId() {
    return this.attrs["PATHWAY-ID"] || ".";
  }
  get videoRange() {
    return this.attrs["VIDEO-RANGE"] || "SDR";
  }
  get score() {
    return this.attrs.optionalFloat("SCORE", 0);
  }
  get uri() {
    return this.url[0] || "";
  }
  hasAudioGroup(t) {
    return nn(this._audioGroups, t);
  }
  hasSubtitleGroup(t) {
    return nn(this._subtitleGroups, t);
  }
  get audioGroups() {
    return this._audioGroups;
  }
  get subtitleGroups() {
    return this._subtitleGroups;
  }
  addGroupId(t, e) {
    if (e) {
      if (t === "audio") {
        let i = this._audioGroups;
        i || (i = this._audioGroups = []), i.indexOf(e) === -1 && i.push(e);
      } else if (t === "text") {
        let i = this._subtitleGroups;
        i || (i = this._subtitleGroups = []), i.indexOf(e) === -1 && i.push(e);
      }
    }
  }
  // Deprecated methods (retained for backwards compatibility)
  get urlId() {
    return 0;
  }
  set urlId(t) {
  }
  get audioGroupIds() {
    return this.audioGroups ? [this.audioGroupId] : void 0;
  }
  get textGroupIds() {
    return this.subtitleGroups ? [this.textGroupId] : void 0;
  }
  get audioGroupId() {
    var t;
    return (t = this.audioGroups) == null ? void 0 : t[0];
  }
  get textGroupId() {
    var t;
    return (t = this.subtitleGroups) == null ? void 0 : t[0];
  }
  addFallback() {
  }
}
function nn(n, t) {
  return !t || !n ? !1 : n.indexOf(t) !== -1;
}
function mc() {
  if (typeof matchMedia == "function") {
    const n = matchMedia("(dynamic-range: high)"), t = matchMedia("bad query");
    if (n.media !== t.media)
      return n.matches === !0;
  }
  return !1;
}
function pc(n, t) {
  let e = !1, i = [];
  if (n && (e = n !== "SDR", i = [n]), t) {
    i = t.allowedVideoRanges || Ji.slice(0);
    const s = i.join("") !== "SDR" && !t.videoCodec;
    e = t.preferHDR !== void 0 ? t.preferHDR : s && mc(), e || (i = ["SDR"]);
  }
  return {
    preferHDR: e,
    allowedVideoRanges: i
  };
}
const vc = (n) => {
  const t = /* @__PURE__ */ new WeakSet();
  return (e, i) => {
    if (n && (i = n(e, i)), typeof i == "object" && i !== null) {
      if (t.has(i))
        return;
      t.add(i);
    }
    return i;
  };
}, ot = (n, t) => JSON.stringify(n, vc(t));
function yc(n, t, e, i, s) {
  const r = Object.keys(n), a = i == null ? void 0 : i.channels, o = i == null ? void 0 : i.audioCodec, c = s == null ? void 0 : s.videoCodec, l = a && parseInt(a) === 2;
  let h = !1, d = !1, u = 1 / 0, f = 1 / 0, g = 1 / 0, v = 1 / 0, p = 0, y = [];
  const {
    preferHDR: E,
    allowedVideoRanges: T
  } = pc(t, s);
  for (let _ = r.length; _--; ) {
    const R = n[r[_]];
    h || (h = R.channels[2] > 0), u = Math.min(u, R.minHeight), f = Math.min(f, R.minFramerate), g = Math.min(g, R.minBitrate), T.filter((C) => R.videoRanges[C] > 0).length > 0 && (d = !0);
  }
  u = B(u) ? u : 0, f = B(f) ? f : 0;
  const S = Math.max(1080, u), x = Math.max(30, f);
  g = B(g) ? g : e, e = Math.max(g, e), d || (t = void 0);
  const D = r.length > 1;
  return {
    codecSet: r.reduce((_, R) => {
      const b = n[R];
      if (R === _)
        return _;
      if (y = d ? T.filter((C) => b.videoRanges[C] > 0) : [], D) {
        if (b.minBitrate > e)
          return Yt(R, `min bitrate of ${b.minBitrate} > current estimate of ${e}`), _;
        if (!b.hasDefaultAudio)
          return Yt(R, "no renditions with default or auto-select sound found"), _;
        if (o && R.indexOf(o.substring(0, 4)) % 5 !== 0)
          return Yt(R, `audio codec preference "${o}" not found`), _;
        if (a && !l) {
          if (!b.channels[a])
            return Yt(R, `no renditions with ${a} channel sound found (channels options: ${Object.keys(b.channels)})`), _;
        } else if ((!o || l) && h && b.channels[2] === 0)
          return Yt(R, "no renditions with stereo sound found"), _;
        if (b.minHeight > S)
          return Yt(R, `min resolution of ${b.minHeight} > maximum of ${S}`), _;
        if (b.minFramerate > x)
          return Yt(R, `min framerate of ${b.minFramerate} > maximum of ${x}`), _;
        if (!y.some((C) => b.videoRanges[C] > 0))
          return Yt(R, `no variants with VIDEO-RANGE of ${ot(y)} found`), _;
        if (c && R.indexOf(c.substring(0, 4)) % 5 !== 0)
          return Yt(R, `video codec preference "${c}" not found`), _;
        if (b.maxScore < p)
          return Yt(R, `max score of ${b.maxScore} < selected max of ${p}`), _;
      }
      return _ && (Qi(R) >= Qi(_) || b.fragmentError > n[_].fragmentError) ? _ : (v = b.minIndex, p = b.maxScore, R);
    }, void 0),
    videoRanges: y,
    preferHDR: E,
    minFramerate: f,
    minBitrate: g,
    minIndex: v
  };
}
function Yt(n, t) {
  rt.log(`[abr] start candidates with "${n}" ignored because ${t}`);
}
function ka(n) {
  return n.reduce((t, e) => {
    let i = t.groups[e.groupId];
    i || (i = t.groups[e.groupId] = {
      tracks: [],
      channels: {
        2: 0
      },
      hasDefault: !1,
      hasAutoSelect: !1
    }), i.tracks.push(e);
    const s = e.channels || "2";
    return i.channels[s] = (i.channels[s] || 0) + 1, i.hasDefault = i.hasDefault || e.default, i.hasAutoSelect = i.hasAutoSelect || e.autoselect, i.hasDefault && (t.hasDefaultAudio = !0), i.hasAutoSelect && (t.hasAutoSelectAudio = !0), t;
  }, {
    hasDefaultAudio: !1,
    hasAutoSelectAudio: !1,
    groups: {}
  });
}
function Ec(n, t, e, i) {
  return n.slice(e, i + 1).reduce((s, r, a) => {
    if (!r.codecSet)
      return s;
    const o = r.audioGroups;
    let c = s[r.codecSet];
    c || (s[r.codecSet] = c = {
      minBitrate: 1 / 0,
      minHeight: 1 / 0,
      minFramerate: 1 / 0,
      minIndex: a,
      maxScore: 0,
      videoRanges: {
        SDR: 0
      },
      channels: {
        2: 0
      },
      hasDefaultAudio: !o,
      fragmentError: 0
    }), c.minBitrate = Math.min(c.minBitrate, r.bitrate);
    const l = Math.min(r.height, r.width);
    return c.minHeight = Math.min(c.minHeight, l), c.minFramerate = Math.min(c.minFramerate, r.frameRate), c.minIndex = Math.min(c.minIndex, a), c.maxScore = Math.max(c.maxScore, r.score), c.fragmentError += r.fragmentError, c.videoRanges[r.videoRange] = (c.videoRanges[r.videoRange] || 0) + 1, o && o.forEach((h) => {
      if (!h)
        return;
      const d = t.groups[h];
      d && (c.hasDefaultAudio = c.hasDefaultAudio || t.hasDefaultAudio ? d.hasDefault : d.hasAutoSelect || !t.hasDefaultAudio && !t.hasAutoSelectAudio, Object.keys(d.channels).forEach((u) => {
        c.channels[u] = (c.channels[u] || 0) + d.channels[u];
      }));
    }), s;
  }, {});
}
function an(n) {
  if (!n)
    return n;
  const {
    lang: t,
    assocLang: e,
    characteristics: i,
    channels: s,
    audioCodec: r
  } = n;
  return {
    lang: t,
    assocLang: e,
    characteristics: i,
    channels: s,
    audioCodec: r
  };
}
function Xt(n, t, e) {
  if ("attrs" in n) {
    const i = t.indexOf(n);
    if (i !== -1)
      return i;
  }
  for (let i = 0; i < t.length; i++) {
    const s = t[i];
    if (_e(n, s, e))
      return i;
  }
  return -1;
}
function _e(n, t, e) {
  const {
    groupId: i,
    name: s,
    lang: r,
    assocLang: a,
    default: o
  } = n, c = n.forced;
  return (i === void 0 || t.groupId === i) && (s === void 0 || t.name === s) && (r === void 0 || Tc(r, t.lang)) && (r === void 0 || t.assocLang === a) && (o === void 0 || t.default === o) && (c === void 0 || t.forced === c) && (!("characteristics" in n) || Sc(n.characteristics || "", t.characteristics)) && (e === void 0 || e(n, t));
}
function Tc(n, t = "--") {
  return n.length === t.length ? n === t : n.startsWith(t) || t.startsWith(n);
}
function Sc(n, t = "") {
  const e = n.split(","), i = t.split(",");
  return e.length === i.length && !e.some((s) => i.indexOf(s) === -1);
}
function Ie(n, t) {
  const {
    audioCodec: e,
    channels: i
  } = n;
  return (e === void 0 || (t.audioCodec || "").substring(0, 4) === e.substring(0, 4)) && (i === void 0 || i === (t.channels || "2"));
}
function xc(n, t, e, i, s) {
  const r = t[i], o = t.reduce((u, f, g) => {
    const v = f.uri;
    return (u[v] || (u[v] = [])).push(g), u;
  }, {})[r.uri];
  o.length > 1 && (i = Math.max.apply(Math, o));
  const c = r.videoRange, l = r.frameRate, h = r.codecSet.substring(0, 4), d = on(t, i, (u) => {
    if (u.videoRange !== c || u.frameRate !== l || u.codecSet.substring(0, 4) !== h)
      return !1;
    const f = u.audioGroups, g = e.filter((v) => !f || f.indexOf(v.groupId) !== -1);
    return Xt(n, g, s) > -1;
  });
  return d > -1 ? d : on(t, i, (u) => {
    const f = u.audioGroups, g = e.filter((v) => !f || f.indexOf(v.groupId) !== -1);
    return Xt(n, g, s) > -1;
  });
}
function on(n, t, e) {
  for (let i = t; i > -1; i--)
    if (e(n[i]))
      return i;
  for (let i = t + 1; i < n.length; i++)
    if (e(n[i]))
      return i;
  return -1;
}
function ts(n, t) {
  var e;
  return !!n && n !== ((e = t.loadLevelObj) == null ? void 0 : e.uri);
}
class Ac extends Bt {
  constructor(t) {
    super("abr", t.logger), this.hls = void 0, this.lastLevelLoadSec = 0, this.lastLoadedFragLevel = -1, this.firstSelection = -1, this._nextAutoLevel = -1, this.nextAutoLevelKey = "", this.audioTracksByGroup = null, this.codecTiers = null, this.timer = -1, this.fragCurrent = null, this.partCurrent = null, this.bitrateTestDelay = 0, this.rebufferNotice = -1, this.supportedCache = {}, this.bwEstimator = void 0, this._abandonRulesCheck = (e) => {
      var i;
      const {
        fragCurrent: s,
        partCurrent: r,
        hls: a
      } = this, {
        autoLevelEnabled: o,
        media: c
      } = a;
      if (!s || !c)
        return;
      const l = performance.now(), h = r ? r.stats : s.stats, d = r ? r.duration : s.duration, u = l - h.loading.start, f = a.minAutoLevel, g = s.level, v = this._nextAutoLevel;
      if (h.aborted || h.loaded && h.loaded === h.total || g <= f) {
        this.clearTimer(), this._nextAutoLevel = -1;
        return;
      }
      if (!o)
        return;
      const p = v > -1 && v !== g, y = !!e || p;
      if (!y && (c.paused || !c.playbackRate || !c.readyState))
        return;
      const E = a.mainForwardBufferInfo;
      if (!y && E === null)
        return;
      const T = this.bwEstimator.getEstimateTTFB(), S = Math.abs(c.playbackRate);
      if (u <= Math.max(T, 1e3 * (d / (S * 2))))
        return;
      const x = E ? E.len / S : 0, D = h.loading.first ? h.loading.first - h.loading.start : -1, A = h.loaded && D > -1, _ = this.getBwEstimate(), R = a.levels, b = R[g], C = Math.max(h.loaded, Math.round(d * (s.bitrate || b.averageBitrate) / 8));
      let F = A ? u - D : u;
      F < 1 && A && (F = Math.min(u, h.loaded * 8 / _));
      const U = A ? h.loaded * 1e3 / F : 0, W = T / 1e3, G = U ? (C - h.loaded) / U : C * 8 / _ + W;
      if (G <= x)
        return;
      const k = U ? U * 8 : _, H = ((i = (e == null ? void 0 : e.details) || this.hls.latestLevelDetails) == null ? void 0 : i.live) === !0, $ = this.hls.config.abrBandWidthUpFactor;
      let V = Number.POSITIVE_INFINITY, z;
      for (z = g - 1; z > f; z--) {
        const et = R[z].maxBitrate, Q = !R[z].details || H;
        if (V = this.getTimeToLoadFrag(W, k, d * et, Q), V < Math.min(x, d + W))
          break;
      }
      if (V >= G || V > d * 10)
        return;
      A ? this.bwEstimator.sample(u - Math.min(T, D), h.loaded) : this.bwEstimator.sampleTTFB(u);
      const O = R[z].maxBitrate;
      this.getBwEstimate() * $ > O && this.resetEstimator(O);
      const M = this.findBestLevel(O, f, z, 0, x, 1, 1);
      M > -1 && (z = M), this.warn(`Fragment ${s.sn}${r ? " part " + r.index : ""} of level ${g} is loading too slowly;
      Fragment duration: ${s.duration.toFixed(3)}
      Time to underbuffer: ${x.toFixed(3)} s
      Estimated load time for current fragment: ${G.toFixed(3)} s
      Estimated load time for down switch fragment: ${V.toFixed(3)} s
      TTFB estimate: ${D | 0} ms
      Current BW estimate: ${B(_) ? _ | 0 : "Unknown"} bps
      New BW estimate: ${this.getBwEstimate() | 0} bps
      Switching to level ${z} @ ${O | 0} bps`), a.nextLoadLevel = a.nextAutoLevel = z, this.clearTimer();
      const X = () => {
        if (this.clearTimer(), this.fragCurrent === s && this.hls.loadLevel === z && z > 0) {
          const et = this.getStarvationDelay();
          if (this.warn(`Aborting inflight request ${z > 0 ? "and switching down" : ""}
      Fragment duration: ${s.duration.toFixed(3)} s
      Time to underbuffer: ${et.toFixed(3)} s`), s.abortRequests(), this.fragCurrent = this.partCurrent = null, z > f) {
            let Q = this.findBestLevel(this.hls.levels[f].bitrate, f, z, 0, et, 1, 1);
            Q === -1 && (Q = f), this.hls.nextLoadLevel = this.hls.nextAutoLevel = Q, this.resetEstimator(this.hls.levels[Q].bitrate);
          }
        }
      };
      p || G > V * 2 ? X() : this.timer = self.setInterval(X, V * 1e3), a.trigger(m.FRAG_LOAD_EMERGENCY_ABORTED, {
        frag: s,
        part: r,
        stats: h
      });
    }, this.hls = t, this.bwEstimator = this.initEstimator(), this.registerListeners();
  }
  resetEstimator(t) {
    t && (this.log(`setting initial bwe to ${t}`), this.hls.config.abrEwmaDefaultEstimate = t), this.firstSelection = -1, this.bwEstimator = this.initEstimator();
  }
  initEstimator() {
    const t = this.hls.config;
    return new _l(t.abrEwmaSlowVoD, t.abrEwmaFastVoD, t.abrEwmaDefaultEstimate);
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.FRAG_LOADING, this.onFragLoading, this), t.on(m.FRAG_LOADED, this.onFragLoaded, this), t.on(m.FRAG_BUFFERED, this.onFragBuffered, this), t.on(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.on(m.LEVEL_LOADED, this.onLevelLoaded, this), t.on(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.on(m.MAX_AUTO_LEVEL_UPDATED, this.onMaxAutoLevelUpdated, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.FRAG_LOADING, this.onFragLoading, this), t.off(m.FRAG_LOADED, this.onFragLoaded, this), t.off(m.FRAG_BUFFERED, this.onFragBuffered, this), t.off(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.off(m.LEVEL_LOADED, this.onLevelLoaded, this), t.off(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.off(m.MAX_AUTO_LEVEL_UPDATED, this.onMaxAutoLevelUpdated, this), t.off(m.ERROR, this.onError, this));
  }
  destroy() {
    this.unregisterListeners(), this.clearTimer(), this.hls = this._abandonRulesCheck = this.supportedCache = null, this.fragCurrent = this.partCurrent = null;
  }
  onManifestLoading(t, e) {
    this.lastLoadedFragLevel = -1, this.firstSelection = -1, this.lastLevelLoadSec = 0, this.supportedCache = {}, this.fragCurrent = this.partCurrent = null, this.onLevelsUpdated(), this.clearTimer();
  }
  onLevelsUpdated() {
    this.lastLoadedFragLevel > -1 && this.fragCurrent && (this.lastLoadedFragLevel = this.fragCurrent.level), this._nextAutoLevel = -1, this.onMaxAutoLevelUpdated(), this.codecTiers = null, this.audioTracksByGroup = null;
  }
  onMaxAutoLevelUpdated() {
    this.firstSelection = -1, this.nextAutoLevelKey = "";
  }
  onFragLoading(t, e) {
    const i = e.frag;
    if (!this.ignoreFragment(i)) {
      if (!i.bitrateTest) {
        var s;
        this.fragCurrent = i, this.partCurrent = (s = e.part) != null ? s : null;
      }
      this.clearTimer(), this.timer = self.setInterval(this._abandonRulesCheck, 100);
    }
  }
  onLevelSwitching(t, e) {
    this.clearTimer();
  }
  onError(t, e) {
    if (!e.fatal)
      switch (e.details) {
        case L.BUFFER_ADD_CODEC_ERROR:
        case L.BUFFER_APPEND_ERROR:
          this.lastLoadedFragLevel = -1, this.firstSelection = -1;
          break;
        case L.FRAG_LOAD_TIMEOUT: {
          const i = e.frag, {
            fragCurrent: s,
            partCurrent: r
          } = this;
          if (i && s && i.sn === s.sn && i.level === s.level) {
            const a = performance.now(), o = r ? r.stats : i.stats, c = a - o.loading.start, l = o.loading.first ? o.loading.first - o.loading.start : -1;
            if (o.loaded && l > -1) {
              const d = this.bwEstimator.getEstimateTTFB();
              this.bwEstimator.sample(c - Math.min(d, l), o.loaded);
            } else
              this.bwEstimator.sampleTTFB(c);
          }
          break;
        }
      }
  }
  getTimeToLoadFrag(t, e, i, s) {
    const r = t + i / e, a = s ? t + this.lastLevelLoadSec : 0;
    return r + a;
  }
  onLevelLoaded(t, e) {
    const i = this.hls.config, {
      loading: s
    } = e.stats, r = s.end - s.first;
    B(r) && (this.lastLevelLoadSec = r / 1e3), e.details.live ? this.bwEstimator.update(i.abrEwmaSlowLive, i.abrEwmaFastLive) : this.bwEstimator.update(i.abrEwmaSlowVoD, i.abrEwmaFastVoD), this.timer > -1 && this._abandonRulesCheck(e.levelInfo);
  }
  onFragLoaded(t, {
    frag: e,
    part: i
  }) {
    const s = i ? i.stats : e.stats;
    if (e.type === K.MAIN && this.bwEstimator.sampleTTFB(s.loading.first - s.loading.start), !this.ignoreFragment(e)) {
      if (this.clearTimer(), e.level === this._nextAutoLevel && (this._nextAutoLevel = -1), this.firstSelection = -1, this.hls.config.abrMaxWithRealBitrate) {
        const r = i ? i.duration : e.duration, a = this.hls.levels[e.level], o = (a.loaded ? a.loaded.bytes : 0) + s.loaded, c = (a.loaded ? a.loaded.duration : 0) + r;
        a.loaded = {
          bytes: o,
          duration: c
        }, a.realBitrate = Math.round(8 * o / c);
      }
      if (e.bitrateTest) {
        const r = {
          stats: s,
          frag: e,
          part: i,
          id: e.type
        };
        this.onFragBuffered(m.FRAG_BUFFERED, r), e.bitrateTest = !1;
      } else
        this.lastLoadedFragLevel = e.level;
    }
  }
  onFragBuffered(t, e) {
    const {
      frag: i,
      part: s
    } = e, r = s != null && s.stats.loaded ? s.stats : i.stats;
    if (r.aborted || this.ignoreFragment(i))
      return;
    const a = r.parsing.end - r.loading.start - Math.min(r.loading.first - r.loading.start, this.bwEstimator.getEstimateTTFB());
    this.bwEstimator.sample(a, r.loaded), r.bwEstimate = this.getBwEstimate(), i.bitrateTest ? this.bitrateTestDelay = a / 1e3 : this.bitrateTestDelay = 0;
  }
  ignoreFragment(t) {
    return t.type !== K.MAIN || t.sn === "initSegment";
  }
  clearTimer() {
    this.timer > -1 && (self.clearInterval(this.timer), this.timer = -1);
  }
  get firstAutoLevel() {
    const {
      maxAutoLevel: t,
      minAutoLevel: e
    } = this.hls, i = this.getBwEstimate(), s = this.hls.config.maxStarvationDelay, r = this.findBestLevel(i, e, t, 0, s, 1, 1);
    if (r > -1)
      return r;
    const a = this.hls.firstLevel, o = Math.min(Math.max(a, e), t);
    return this.warn(`Could not find best starting auto level. Defaulting to first in playlist ${a} clamped to ${o}`), o;
  }
  get forcedAutoLevel() {
    return this.nextAutoLevelKey ? -1 : this._nextAutoLevel;
  }
  // return next auto level
  get nextAutoLevel() {
    const t = this.forcedAutoLevel, i = this.bwEstimator.canEstimate(), s = this.lastLoadedFragLevel > -1;
    if (t !== -1 && (!i || !s || this.nextAutoLevelKey === this.getAutoLevelKey()))
      return t;
    const r = i && s ? this.getNextABRAutoLevel() : this.firstAutoLevel;
    if (t !== -1) {
      const a = this.hls.levels;
      if (a.length > Math.max(t, r) && a[t].loadError <= a[r].loadError)
        return t;
    }
    return this._nextAutoLevel = r, this.nextAutoLevelKey = this.getAutoLevelKey(), r;
  }
  getAutoLevelKey() {
    return `${this.getBwEstimate()}_${this.getStarvationDelay().toFixed(2)}`;
  }
  getNextABRAutoLevel() {
    const {
      fragCurrent: t,
      partCurrent: e,
      hls: i
    } = this;
    if (i.levels.length <= 1)
      return i.loadLevel;
    const {
      maxAutoLevel: s,
      config: r,
      minAutoLevel: a
    } = i, o = e ? e.duration : t ? t.duration : 0, c = this.getBwEstimate(), l = this.getStarvationDelay();
    let h = r.abrBandWidthFactor, d = r.abrBandWidthUpFactor;
    if (l) {
      const p = this.findBestLevel(c, a, s, l, 0, h, d);
      if (p >= 0)
        return this.rebufferNotice = -1, p;
    }
    let u = o ? Math.min(o, r.maxStarvationDelay) : r.maxStarvationDelay;
    if (!l) {
      const p = this.bitrateTestDelay;
      p && (u = (o ? Math.min(o, r.maxLoadingDelay) : r.maxLoadingDelay) - p, this.info(`bitrate test took ${Math.round(1e3 * p)}ms, set first fragment max fetchDuration to ${Math.round(1e3 * u)} ms`), h = d = 1);
    }
    const f = this.findBestLevel(c, a, s, l, u, h, d);
    if (this.rebufferNotice !== f && (this.rebufferNotice = f, this.info(`${l ? "rebuffering expected" : "buffer is empty"}, optimal quality level ${f}`)), f > -1)
      return f;
    const g = i.levels[a], v = i.loadLevelObj;
    return v && (g == null ? void 0 : g.bitrate) < v.bitrate ? a : i.loadLevel;
  }
  getStarvationDelay() {
    const t = this.hls, e = t.media;
    if (!e)
      return 1 / 0;
    const i = e && e.playbackRate !== 0 ? Math.abs(e.playbackRate) : 1, s = t.mainForwardBufferInfo;
    return (s ? s.len : 0) / i;
  }
  getBwEstimate() {
    return this.bwEstimator.canEstimate() ? this.bwEstimator.getEstimate() : this.hls.config.abrEwmaDefaultEstimate;
  }
  findBestLevel(t, e, i, s, r, a, o) {
    var c;
    const l = s + r, h = this.lastLoadedFragLevel, d = h === -1 ? this.hls.firstLevel : h, {
      fragCurrent: u,
      partCurrent: f
    } = this, {
      levels: g,
      allAudioTracks: v,
      loadLevel: p,
      config: y
    } = this.hls;
    if (g.length === 1)
      return 0;
    const E = g[d], T = !!((c = this.hls.latestLevelDetails) != null && c.live), S = p === -1 || h === -1;
    let x, D = "SDR", A = (E == null ? void 0 : E.frameRate) || 0;
    const {
      audioPreference: _,
      videoPreference: R
    } = y, b = this.audioTracksByGroup || (this.audioTracksByGroup = ka(v));
    let C = -1;
    if (S) {
      if (this.firstSelection !== -1)
        return this.firstSelection;
      const k = this.codecTiers || (this.codecTiers = Ec(g, b, e, i)), H = yc(k, D, t, _, R), {
        codecSet: $,
        videoRanges: V,
        minFramerate: z,
        minBitrate: O,
        minIndex: M,
        preferHDR: X
      } = H;
      C = M, x = $, D = X ? V[V.length - 1] : V[0], A = z, t = Math.max(t, O), this.log(`picked start tier ${ot(H)}`);
    } else
      x = E == null ? void 0 : E.codecSet, D = E == null ? void 0 : E.videoRange;
    const F = f ? f.duration : u ? u.duration : 0, U = this.bwEstimator.getEstimateTTFB() / 1e3, W = [];
    for (let k = i; k >= e; k--) {
      var G;
      const H = g[k], $ = k > d;
      if (!H)
        continue;
      if (y.useMediaCapabilities && !H.supportedResult && !H.supportedPromise) {
        const Q = navigator.mediaCapabilities;
        typeof (Q == null ? void 0 : Q.decodingInfo) == "function" && lc(H, b, D, A, t, _) ? (H.supportedPromise = Ca(H, b, Q, this.supportedCache), H.supportedPromise.then((J) => {
          if (!this.hls)
            return;
          H.supportedResult = J;
          const pt = this.hls.levels, mt = pt.indexOf(H);
          J.error ? this.warn(`MediaCapabilities decodingInfo error: "${J.error}" for level ${mt} ${ot(J)}`) : J.supported ? J.decodingInfoResults.some((Rt) => Rt.smooth === !1 || Rt.powerEfficient === !1) && this.log(`MediaCapabilities decodingInfo for level ${mt} not smooth or powerEfficient: ${ot(J)}`) : (this.warn(`Unsupported MediaCapabilities decodingInfo result for level ${mt} ${ot(J)}`), mt > -1 && pt.length > 1 && (this.log(`Removing unsupported level ${mt}`), this.hls.removeLevel(mt), this.hls.loadLevel === -1 && (this.hls.nextLoadLevel = 0)));
        }).catch((J) => {
          this.warn(`Error handling MediaCapabilities decodingInfo: ${J}`);
        })) : H.supportedResult = Da;
      }
      if ((x && H.codecSet !== x || D && H.videoRange !== D || $ && A > H.frameRate || !$ && A > 0 && A < H.frameRate || (G = H.supportedResult) != null && (G = G.decodingInfoResults) != null && G.some((Q) => Q.smooth === !1)) && (!S || k !== C)) {
        W.push(k);
        continue;
      }
      const V = H.details, z = (f ? V == null ? void 0 : V.partTarget : V == null ? void 0 : V.averagetargetduration) || F;
      let O;
      $ ? O = o * t : O = a * t;
      const M = F && s >= F * 2 && r === 0 ? H.averageBitrate : H.maxBitrate, X = this.getTimeToLoadFrag(U, O, M * z, V === void 0);
      if (
        // if adjusted bw is greater than level bitrate AND
        O >= M && // no level change, or new level has no error history
        (k === h || H.loadError === 0 && H.fragmentError === 0) && // fragment fetchDuration unknown OR live stream OR fragment fetchDuration less than max allowed fetch duration, then this level matches
        // we don't account for max Fetch Duration for live streams, this is to avoid switching down when near the edge of live sliding window ...
        // special case to support startLevel = -1 (bitrateTest) on live streams : in that case we should not exit loop so that findBestLevel will return -1
        (X <= U || !B(X) || T && !this.bitrateTestDelay || X < l)
      ) {
        const Q = this.forcedAutoLevel;
        return k !== p && (Q === -1 || Q !== p) && (W.length && this.trace(`Skipped level(s) ${W.join(",")} of ${i} max with CODECS and VIDEO-RANGE:"${g[W[0]].codecs}" ${g[W[0]].videoRange}; not compatible with "${x}" ${D}`), this.info(`switch candidate:${d}->${k} adjustedbw(${Math.round(O)})-bitrate=${Math.round(O - M)} ttfb:${U.toFixed(1)} avgDuration:${z.toFixed(1)} maxFetchDuration:${l.toFixed(1)} fetchDuration:${X.toFixed(1)} firstSelection:${S} codecSet:${H.codecSet} videoRange:${H.videoRange} hls.loadLevel:${p}`)), S && (this.firstSelection = k), k;
      }
    }
    return -1;
  }
  set nextAutoLevel(t) {
    const e = this.deriveNextAutoLevel(t);
    this._nextAutoLevel !== e && (this.nextAutoLevelKey = "", this._nextAutoLevel = e);
  }
  deriveNextAutoLevel(t) {
    const {
      maxAutoLevel: e,
      minAutoLevel: i
    } = this.hls;
    return Math.min(Math.max(t, i), e);
  }
}
const Oa = {
  /**
   * Searches for an item in an array which matches a certain condition.
   * This requires the condition to only match one item in the array,
   * and for the array to be ordered.
   *
   * @param list The array to search.
   * @param comparisonFn
   *      Called and provided a candidate item as the first argument.
   *      Should return:
   *          > -1 if the item should be located at a lower index than the provided item.
   *          > 1 if the item should be located at a higher index than the provided item.
   *          > 0 if the item is the item you're looking for.
   *
   * @returns the object if found, otherwise returns null
   */
  search: function(n, t) {
    let e = 0, i = n.length - 1, s = null, r = null;
    for (; e <= i; ) {
      s = (e + i) / 2 | 0, r = n[s];
      const a = t(r);
      if (a > 0)
        e = s + 1;
      else if (a < 0)
        i = s - 1;
      else
        return r;
    }
    return null;
  }
};
function bc(n, t, e) {
  if (t === null || !Array.isArray(n) || !n.length || !B(t))
    return null;
  const i = n[0].programDateTime;
  if (t < (i || 0))
    return null;
  const s = n[n.length - 1].endProgramDateTime;
  if (t >= (s || 0))
    return null;
  for (let r = 0; r < n.length; ++r) {
    const a = n[r];
    if (Lc(t, e, a))
      return a;
  }
  return null;
}
function De(n, t, e = 0, i = 0, s = 5e-3) {
  let r = null;
  if (n) {
    r = t[1 + n.sn - t[0].sn] || null;
    const o = n.endDTS - e;
    o > 0 && o < 15e-7 && (e += 15e-7), r && n.level !== r.level && r.end <= n.end && (r = t[2 + n.sn - t[0].sn] || null);
  } else e === 0 && t[0].start === 0 && (r = t[0]);
  if (r && ((!n || n.level === r.level) && ln(e, i, r) === 0 || Ic(r, n, Math.min(s, i))))
    return r;
  const a = Oa.search(t, ln.bind(null, e, i));
  return a && (a !== n || !r) ? a : r;
}
function Ic(n, t, e) {
  if (t && t.start === 0 && t.level < n.level && (t.endPTS || 0) > 0) {
    const i = t.tagList.reduce((s, r) => (r[0] === "INF" && (s += parseFloat(r[1])), s), e);
    return n.start <= i;
  }
  return !1;
}
function ln(n = 0, t = 0, e) {
  if (e.start <= n && e.start + e.duration > n)
    return 0;
  const i = Math.min(t, e.duration + (e.deltaPTS ? e.deltaPTS : 0));
  return e.start + e.duration - i <= n ? 1 : e.start - i > n && e.start ? -1 : 0;
}
function Lc(n, t, e) {
  const i = Math.min(t, e.duration + (e.deltaPTS ? e.deltaPTS : 0)) * 1e3;
  return (e.endProgramDateTime || 0) - i > n;
}
function Ma(n, t, e) {
  if (n && n.startCC <= t && n.endCC >= t) {
    let i = n.fragments;
    const {
      fragmentHint: s
    } = n;
    s && (i = i.concat(s));
    let r;
    return Oa.search(i, (a) => a.cc < t ? 1 : a.cc > t ? -1 : (r = a, a.end <= e ? 1 : a.start > e ? -1 : 0)), r || null;
  }
  return null;
}
function es(n) {
  switch (n.details) {
    case L.FRAG_LOAD_TIMEOUT:
    case L.KEY_LOAD_TIMEOUT:
    case L.LEVEL_LOAD_TIMEOUT:
    case L.MANIFEST_LOAD_TIMEOUT:
      return !0;
  }
  return !1;
}
function Fa(n) {
  return n.details.startsWith("key");
}
function $a(n) {
  return Fa(n) && !!n.frag && !n.frag.decryptdata;
}
function cn(n, t) {
  const e = es(t);
  return n.default[`${e ? "timeout" : "error"}Retry`];
}
function xr(n, t) {
  const e = n.backoff === "linear" ? 1 : Math.pow(2, t);
  return Math.min(e * n.retryDelayMs, n.maxRetryDelayMs);
}
function hn(n) {
  return st(st({}, n), {
    errorRetry: null,
    timeoutRetry: null
  });
}
function is(n, t, e, i) {
  if (!n)
    return !1;
  const s = i == null ? void 0 : i.code, r = t < n.maxNumRetry && (Rc(s) || !!e);
  return n.shouldRetry ? n.shouldRetry(n, t, e, i, r) : r;
}
function Rc(n) {
  return Js(n) || !!n && (n < 400 || n > 499);
}
function Js(n) {
  return n === 0 && navigator.onLine === !1;
}
var xt = {
  DoNothing: 0,
  SendAlternateToPenaltyBox: 2,
  RemoveAlternatePermanently: 3,
  RetryRequest: 5
}, kt = {
  None: 0,
  MoveAllAlternatesMatchingHost: 1,
  MoveAllAlternatesMatchingHDCP: 2,
  MoveAllAlternatesMatchingKey: 4
};
class _c extends Bt {
  constructor(t) {
    super("error-controller", t.logger), this.hls = void 0, this.playlistError = 0, this.hls = t, this.registerListeners();
  }
  registerListeners() {
    const t = this.hls;
    t.on(m.ERROR, this.onError, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.LEVEL_UPDATED, this.onLevelUpdated, this);
  }
  unregisterListeners() {
    const t = this.hls;
    t && (t.off(m.ERROR, this.onError, this), t.off(m.ERROR, this.onErrorOut, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.LEVEL_UPDATED, this.onLevelUpdated, this));
  }
  destroy() {
    this.unregisterListeners(), this.hls = null;
  }
  startLoad(t) {
  }
  stopLoad() {
    this.playlistError = 0;
  }
  getVariantLevelIndex(t) {
    return (t == null ? void 0 : t.type) === K.MAIN ? t.level : this.getVariantIndex();
  }
  getVariantIndex() {
    var t;
    const e = this.hls, i = e.currentLevel;
    return (t = e.loadLevelObj) != null && t.details || i === -1 ? e.loadLevel : i;
  }
  variantHasKey(t, e) {
    if (t) {
      var i;
      if ((i = t.details) != null && i.hasKey(e))
        return !0;
      const s = t.audioGroups;
      if (s)
        return this.hls.allAudioTracks.filter((a) => s.indexOf(a.groupId) >= 0).some((a) => {
          var o;
          return (o = a.details) == null ? void 0 : o.hasKey(e);
        });
    }
    return !1;
  }
  onManifestLoading() {
    this.playlistError = 0;
  }
  onLevelUpdated() {
    this.playlistError = 0;
  }
  onError(t, e) {
    var i;
    if (e.fatal)
      return;
    const s = this.hls, r = e.context;
    switch (e.details) {
      case L.FRAG_LOAD_ERROR:
      case L.FRAG_LOAD_TIMEOUT:
      case L.KEY_LOAD_ERROR:
      case L.KEY_LOAD_TIMEOUT:
        e.errorAction = this.getFragRetryOrSwitchAction(e);
        return;
      case L.FRAG_PARSING_ERROR:
        if ((i = e.frag) != null && i.gap) {
          e.errorAction = We();
          return;
        }
      // falls through
      case L.FRAG_GAP:
      case L.FRAG_DECRYPT_ERROR: {
        e.errorAction = this.getFragRetryOrSwitchAction(e), e.errorAction.action = xt.SendAlternateToPenaltyBox;
        return;
      }
      case L.LEVEL_EMPTY_ERROR:
      case L.LEVEL_PARSING_ERROR:
        {
          var a;
          const c = e.parent === K.MAIN ? e.level : s.loadLevel;
          e.details === L.LEVEL_EMPTY_ERROR && ((a = e.context) != null && (a = a.levelDetails) != null && a.live) ? e.errorAction = this.getPlaylistRetryOrSwitchAction(e, c) : (e.levelRetry = !1, e.errorAction = this.getLevelSwitchAction(e, c));
        }
        return;
      case L.LEVEL_LOAD_ERROR:
      case L.LEVEL_LOAD_TIMEOUT:
        typeof (r == null ? void 0 : r.level) == "number" && (e.errorAction = this.getPlaylistRetryOrSwitchAction(e, r.level));
        return;
      case L.AUDIO_TRACK_LOAD_ERROR:
      case L.AUDIO_TRACK_LOAD_TIMEOUT:
      case L.SUBTITLE_LOAD_ERROR:
      case L.SUBTITLE_TRACK_LOAD_TIMEOUT:
        if (r) {
          const c = s.loadLevelObj;
          if (c && (r.type === tt.AUDIO_TRACK && c.hasAudioGroup(r.groupId) || r.type === tt.SUBTITLE_TRACK && c.hasSubtitleGroup(r.groupId))) {
            e.errorAction = this.getPlaylistRetryOrSwitchAction(e, s.loadLevel), e.errorAction.action = xt.SendAlternateToPenaltyBox, e.errorAction.flags = kt.MoveAllAlternatesMatchingHost;
            return;
          }
        }
        return;
      case L.KEY_SYSTEM_STATUS_OUTPUT_RESTRICTED:
        e.errorAction = {
          action: xt.SendAlternateToPenaltyBox,
          flags: kt.MoveAllAlternatesMatchingHDCP
        };
        return;
      case L.KEY_SYSTEM_SESSION_UPDATE_FAILED:
      case L.KEY_SYSTEM_STATUS_INTERNAL_ERROR:
      case L.KEY_SYSTEM_NO_SESSION:
        e.errorAction = {
          action: xt.SendAlternateToPenaltyBox,
          flags: kt.MoveAllAlternatesMatchingKey
        };
        return;
      case L.BUFFER_ADD_CODEC_ERROR:
      case L.REMUX_ALLOC_ERROR:
      case L.BUFFER_APPEND_ERROR:
        if (!e.errorAction) {
          var o;
          e.errorAction = this.getLevelSwitchAction(e, (o = e.level) != null ? o : s.loadLevel);
        }
        return;
      case L.INTERNAL_EXCEPTION:
      case L.BUFFER_APPENDING_ERROR:
      case L.BUFFER_FULL_ERROR:
      case L.LEVEL_SWITCH_ERROR:
      case L.BUFFER_STALLED_ERROR:
      case L.BUFFER_SEEK_OVER_HOLE:
      case L.BUFFER_NUDGE_ON_STALL:
        e.errorAction = We();
        return;
    }
    e.type === Y.KEY_SYSTEM_ERROR && (e.levelRetry = !1, e.errorAction = We());
  }
  getPlaylistRetryOrSwitchAction(t, e) {
    const i = this.hls, s = cn(i.config.playlistLoadPolicy, t), r = this.playlistError++;
    if (is(s, r, es(t), t.response))
      return {
        action: xt.RetryRequest,
        flags: kt.None,
        retryConfig: s,
        retryCount: r
      };
    const o = this.getLevelSwitchAction(t, e);
    return s && (o.retryConfig = s, o.retryCount = r), o;
  }
  getFragRetryOrSwitchAction(t) {
    const e = this.hls, i = this.getVariantLevelIndex(t.frag), s = e.levels[i], {
      fragLoadPolicy: r,
      keyLoadPolicy: a
    } = e.config, o = cn(Fa(t) ? a : r, t), c = e.levels.reduce((h, d) => h + d.fragmentError, 0);
    if (s && (t.details !== L.FRAG_GAP && s.fragmentError++, !$a(t) && is(o, c, es(t), t.response)))
      return {
        action: xt.RetryRequest,
        flags: kt.None,
        retryConfig: o,
        retryCount: c
      };
    const l = this.getLevelSwitchAction(t, i);
    return o && (l.retryConfig = o, l.retryCount = c), l;
  }
  getLevelSwitchAction(t, e) {
    const i = this.hls;
    e == null && (e = i.loadLevel);
    const s = this.hls.levels[e];
    if (s) {
      var r, a;
      const l = t.details;
      s.loadError++, l === L.BUFFER_APPEND_ERROR && s.fragmentError++;
      let h = -1;
      const {
        levels: d,
        loadLevel: u,
        minAutoLevel: f,
        maxAutoLevel: g
      } = i;
      !i.autoLevelEnabled && !i.config.preserveManualLevelOnError && (i.loadLevel = -1);
      const v = (r = t.frag) == null ? void 0 : r.type, y = (v === K.AUDIO && l === L.FRAG_PARSING_ERROR || t.sourceBufferName === "audio" && (l === L.BUFFER_ADD_CODEC_ERROR || l === L.BUFFER_APPEND_ERROR)) && d.some(({
        audioCodec: D
      }) => s.audioCodec !== D), T = t.sourceBufferName === "video" && (l === L.BUFFER_ADD_CODEC_ERROR || l === L.BUFFER_APPEND_ERROR) && d.some(({
        codecSet: D,
        audioCodec: A
      }) => s.codecSet !== D && s.audioCodec === A), {
        type: S,
        groupId: x
      } = (a = t.context) != null ? a : {};
      for (let D = d.length; D--; ) {
        const A = (D + u) % d.length;
        if (A !== u && A >= f && A <= g && d[A].loadError === 0) {
          var o, c;
          const _ = d[A];
          if (l === L.FRAG_GAP && v === K.MAIN && t.frag) {
            const R = d[A].details;
            if (R) {
              const b = De(t.frag, R.fragments, t.frag.start);
              if (b != null && b.gap)
                continue;
            }
          } else {
            if (S === tt.AUDIO_TRACK && _.hasAudioGroup(x) || S === tt.SUBTITLE_TRACK && _.hasSubtitleGroup(x))
              continue;
            if (v === K.AUDIO && (o = s.audioGroups) != null && o.some((R) => _.hasAudioGroup(R)) || v === K.SUBTITLE && (c = s.subtitleGroups) != null && c.some((R) => _.hasSubtitleGroup(R)) || y && s.audioCodec === _.audioCodec || T && s.codecSet === _.codecSet || !y && s.codecSet !== _.codecSet)
              continue;
          }
          h = A;
          break;
        }
      }
      if (h > -1 && i.loadLevel !== h)
        return t.levelRetry = !0, this.playlistError = 0, {
          action: xt.SendAlternateToPenaltyBox,
          flags: kt.None,
          nextAutoLevel: h
        };
    }
    return {
      action: xt.SendAlternateToPenaltyBox,
      flags: kt.MoveAllAlternatesMatchingHost
    };
  }
  onErrorOut(t, e) {
    var i;
    switch ((i = e.errorAction) == null ? void 0 : i.action) {
      case xt.DoNothing:
        break;
      case xt.SendAlternateToPenaltyBox:
        this.sendAlternateToPenaltyBox(e), !e.errorAction.resolved && e.details !== L.FRAG_GAP ? e.fatal = !0 : /MediaSource readyState: ended/.test(e.error.message) && (this.warn(`MediaSource ended after "${e.sourceBufferName}" sourceBuffer append error. Attempting to recover from media error.`), this.hls.recoverMediaError());
        break;
    }
    if (e.fatal) {
      this.hls.stopLoad();
      return;
    }
  }
  sendAlternateToPenaltyBox(t) {
    const e = this.hls, i = t.errorAction;
    if (!i)
      return;
    const {
      flags: s
    } = i, r = i.nextAutoLevel;
    switch (s) {
      case kt.None:
        this.switchLevel(t, r);
        break;
      case kt.MoveAllAlternatesMatchingHDCP: {
        const c = this.getVariantLevelIndex(t.frag), l = e.levels[c], h = l == null ? void 0 : l.attrs["HDCP-LEVEL"];
        if (i.hdcpLevel = h, h === "NONE")
          this.warn("HDCP policy resticted output with HDCP-LEVEL=NONE");
        else if (h) {
          e.maxHdcpLevel = Zs[Zs.indexOf(h) - 1], i.resolved = !0, this.warn(`Restricting playback to HDCP-LEVEL of "${e.maxHdcpLevel}" or lower`);
          break;
        }
      }
      // eslint-disable-next-line no-fallthrough
      case kt.MoveAllAlternatesMatchingKey: {
        const c = t.decryptdata;
        if (c) {
          const l = this.hls.levels, h = l.length;
          for (let u = h; u--; )
            if (this.variantHasKey(l[u], c)) {
              var a, o;
              this.log(`Banned key found in level ${u} (${l[u].bitrate}bps) or audio group "${(a = l[u].audioGroups) == null ? void 0 : a.join(",")}" (${(o = t.frag) == null ? void 0 : o.type} fragment) ${At(c.keyId || [])}`), l[u].fragmentError++, l[u].loadError++, this.log(`Removing level ${u} with key error (${t.error})`), this.hls.removeLevel(u);
            }
          const d = t.frag;
          if (this.hls.levels.length < h)
            i.resolved = !0;
          else if (d && d.type !== K.MAIN) {
            const u = d.decryptdata;
            u && !c.matches(u) && (i.resolved = !0);
          }
        }
        break;
      }
    }
    i.resolved || this.switchLevel(t, r);
  }
  switchLevel(t, e) {
    if (e !== void 0 && t.errorAction && (this.warn(`switching to level ${e} after ${t.details}`), this.hls.nextAutoLevel = e, t.errorAction.resolved = !0, this.hls.nextLoadLevel = this.hls.nextAutoLevel, t.details === L.BUFFER_ADD_CODEC_ERROR && t.mimeType && t.sourceBufferName !== "audiovideo")) {
      const i = Qs(t.mimeType), s = this.hls.levels;
      for (let r = s.length; r--; )
        s[r][`${t.sourceBufferName}Codec`] === i && (this.log(`Removing level ${r} for ${t.details} ("${i}" not supported)`), this.hls.removeLevel(r));
    }
  }
}
function We(n) {
  const t = {
    action: xt.DoNothing,
    flags: kt.None
  };
  return n && (t.resolved = !0), t;
}
var yt = {
  NOT_LOADED: "NOT_LOADED",
  APPENDING: "APPENDING",
  PARTIAL: "PARTIAL",
  OK: "OK"
};
class Dc {
  constructor(t) {
    this.activePartLists = /* @__PURE__ */ Object.create(null), this.endListFragments = /* @__PURE__ */ Object.create(null), this.fragments = /* @__PURE__ */ Object.create(null), this.timeRanges = /* @__PURE__ */ Object.create(null), this.bufferPadding = 0.2, this.hls = void 0, this.hasGaps = !1, this.hls = t, this._registerListeners();
  }
  _registerListeners() {
    const {
      hls: t
    } = this;
    t && (t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.BUFFER_APPENDED, this.onBufferAppended, this), t.on(m.FRAG_BUFFERED, this.onFragBuffered, this), t.on(m.FRAG_LOADED, this.onFragLoaded, this));
  }
  _unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.BUFFER_APPENDED, this.onBufferAppended, this), t.off(m.FRAG_BUFFERED, this.onFragBuffered, this), t.off(m.FRAG_LOADED, this.onFragLoaded, this));
  }
  destroy() {
    this._unregisterListeners(), this.hls = // @ts-ignore
    this.fragments = // @ts-ignore
    this.activePartLists = // @ts-ignore
    this.endListFragments = this.timeRanges = null;
  }
  /**
   * Return a Fragment or Part with an appended range that matches the position and levelType
   * Otherwise, return null
   */
  getAppendedFrag(t, e) {
    const i = this.activePartLists[e];
    if (i)
      for (let s = i.length; s--; ) {
        const r = i[s];
        if (!r)
          break;
        if (r.start <= t && t <= r.end && r.loaded)
          return r;
      }
    return this.getBufferedFrag(t, e);
  }
  /**
   * Return a buffered Fragment that matches the position and levelType.
   * A buffered Fragment is one whose loading, parsing and appending is done (completed or "partial" meaning aborted).
   * If not found any Fragment, return null
   */
  getBufferedFrag(t, e) {
    return this.getFragAtPos(t, e, !0);
  }
  getFragAtPos(t, e, i) {
    const {
      fragments: s
    } = this, r = Object.keys(s);
    for (let a = r.length; a--; ) {
      const o = s[r[a]];
      if ((o == null ? void 0 : o.body.type) === e && (!i || o.buffered)) {
        const c = o.body;
        if (c.start <= t && t <= c.end)
          return c;
      }
    }
    return null;
  }
  /**
   * Partial fragments effected by coded frame eviction will be removed
   * The browser will unload parts of the buffer to free up memory for new buffer data
   * Fragments will need to be reloaded when the buffer is freed up, removing partial fragments will allow them to reload(since there might be parts that are still playable)
   */
  detectEvictedFragments(t, e, i, s, r) {
    this.timeRanges && (this.timeRanges[t] = e);
    const a = (s == null ? void 0 : s.fragment.sn) || -1;
    Object.keys(this.fragments).forEach((o) => {
      const c = this.fragments[o];
      if (!c || a >= c.body.sn)
        return;
      if (!c.buffered && (!c.loaded || r)) {
        c.body.type === i && this.removeFragment(c.body);
        return;
      }
      const l = c.range[t];
      if (l) {
        if (l.time.length === 0) {
          this.removeFragment(c.body);
          return;
        }
        l.time.some((h) => {
          const d = !this.isTimeBuffered(h.startPTS, h.endPTS, e);
          return d && this.removeFragment(c.body), d;
        });
      }
    });
  }
  /**
   * Checks if the fragment passed in is loaded in the buffer properly
   * Partially loaded fragments will be registered as a partial fragment
   */
  detectPartialFragments(t) {
    const e = this.timeRanges;
    if (!e || t.frag.sn === "initSegment")
      return;
    const i = t.frag, s = Be(i), r = this.fragments[s];
    if (!r || r.buffered && i.gap)
      return;
    const a = !i.relurl;
    Object.keys(e).forEach((o) => {
      const c = i.elementaryStreams[o];
      if (!c)
        return;
      const l = e[o], h = a || c.partial === !0;
      r.range[o] = this.getBufferedTimes(i, t.part, h, l);
    }), r.loaded = null, Object.keys(r.range).length ? (this.bufferedEnd(r, i), _i(r) || this.removeParts(i.sn - 1, i.type)) : this.removeFragment(r.body);
  }
  bufferedEnd(t, e) {
    t.buffered = !0, (t.body.endList = e.endList || t.body.endList) && (this.endListFragments[t.body.type] = t);
  }
  removeParts(t, e) {
    const i = this.activePartLists[e];
    i && (this.activePartLists[e] = dn(i, (s) => s.fragment.sn >= t));
  }
  fragBuffered(t, e) {
    const i = Be(t);
    let s = this.fragments[i];
    !s && e && (s = this.fragments[i] = {
      body: t,
      appendedPTS: null,
      loaded: null,
      buffered: !1,
      range: /* @__PURE__ */ Object.create(null)
    }, t.gap && (this.hasGaps = !0)), s && (s.loaded = null, this.bufferedEnd(s, t));
  }
  getBufferedTimes(t, e, i, s) {
    const r = {
      time: [],
      partial: i
    }, a = t.start, o = t.end, c = t.minEndPTS || o, l = t.maxStartPTS || a;
    for (let h = 0; h < s.length; h++) {
      const d = s.start(h) - this.bufferPadding, u = s.end(h) + this.bufferPadding;
      if (l >= d && c <= u) {
        r.time.push({
          startPTS: Math.max(a, s.start(h)),
          endPTS: Math.min(o, s.end(h))
        });
        break;
      } else if (a < u && o > d) {
        const f = Math.max(a, s.start(h)), g = Math.min(o, s.end(h));
        g > f && (r.partial = !0, r.time.push({
          startPTS: f,
          endPTS: g
        }));
      } else if (o <= d)
        break;
    }
    return r;
  }
  /**
   * Gets the partial fragment for a certain time
   */
  getPartialFragment(t) {
    let e = null, i, s, r, a = 0;
    const {
      bufferPadding: o,
      fragments: c
    } = this;
    return Object.keys(c).forEach((l) => {
      const h = c[l];
      h && _i(h) && (s = h.body.start - o, r = h.body.end + o, t >= s && t <= r && (i = Math.min(t - s, r - t), a <= i && (e = h.body, a = i)));
    }), e;
  }
  isEndListAppended(t) {
    const e = this.endListFragments[t];
    return e !== void 0 && (e.buffered || _i(e));
  }
  getState(t) {
    const e = Be(t), i = this.fragments[e];
    return i ? i.buffered ? _i(i) ? yt.PARTIAL : yt.OK : yt.APPENDING : yt.NOT_LOADED;
  }
  isTimeBuffered(t, e, i) {
    let s, r;
    for (let a = 0; a < i.length; a++) {
      if (s = i.start(a) - this.bufferPadding, r = i.end(a) + this.bufferPadding, t >= s && e <= r)
        return !0;
      if (e <= s)
        return !1;
    }
    return !1;
  }
  onManifestLoading() {
    this.removeAllFragments();
  }
  onFragLoaded(t, e) {
    if (e.frag.sn === "initSegment" || e.frag.bitrateTest)
      return;
    const i = e.frag, s = e.part ? null : e, r = Be(i);
    this.fragments[r] = {
      body: i,
      appendedPTS: null,
      loaded: s,
      buffered: !1,
      range: /* @__PURE__ */ Object.create(null)
    };
  }
  onBufferAppended(t, e) {
    const {
      frag: i,
      part: s,
      timeRanges: r,
      type: a
    } = e;
    if (i.sn === "initSegment")
      return;
    const o = i.type;
    if (s) {
      let l = this.activePartLists[o];
      l || (this.activePartLists[o] = l = []), l.push(s);
    }
    this.timeRanges = r;
    const c = r[a];
    this.detectEvictedFragments(a, c, o, s);
  }
  onFragBuffered(t, e) {
    this.detectPartialFragments(e);
  }
  hasFragment(t) {
    const e = Be(t);
    return !!this.fragments[e];
  }
  hasFragments(t) {
    const {
      fragments: e
    } = this, i = Object.keys(e);
    if (!t)
      return i.length > 0;
    for (let s = i.length; s--; ) {
      const r = e[i[s]];
      if ((r == null ? void 0 : r.body.type) === t)
        return !0;
    }
    return !1;
  }
  hasParts(t) {
    var e;
    return !!((e = this.activePartLists[t]) != null && e.length);
  }
  removeFragmentsInRange(t, e, i, s, r) {
    s && !this.hasGaps || Object.keys(this.fragments).forEach((a) => {
      const o = this.fragments[a];
      if (!o)
        return;
      const c = o.body;
      c.type !== i || s && !c.gap || c.start < e && c.end > t && (o.buffered || r) && this.removeFragment(c);
    });
  }
  removeFragment(t) {
    const e = Be(t);
    t.clearElementaryStreamInfo();
    const i = this.activePartLists[t.type];
    if (i) {
      const s = t.sn;
      this.activePartLists[t.type] = dn(i, (r) => r.fragment.sn !== s);
    }
    delete this.fragments[e], t.endList && delete this.endListFragments[t.type];
  }
  removeAllFragments() {
    var t;
    this.fragments = /* @__PURE__ */ Object.create(null), this.endListFragments = /* @__PURE__ */ Object.create(null), this.activePartLists = /* @__PURE__ */ Object.create(null), this.hasGaps = !1;
    const e = (t = this.hls) == null || (t = t.latestLevelDetails) == null ? void 0 : t.partList;
    e && e.forEach((i) => i.clearElementaryStreamInfo());
  }
}
function _i(n) {
  var t, e, i;
  return n.buffered && !!(n.body.gap || (t = n.range.video) != null && t.partial || (e = n.range.audio) != null && e.partial || (i = n.range.audiovideo) != null && i.partial);
}
function Be(n) {
  return `${n.type}_${n.level}_${n.sn}`;
}
function dn(n, t) {
  return n.filter((e) => {
    const i = t(e);
    return i || e.clearElementaryStreamInfo(), i;
  });
}
var me = {
  cbc: 0,
  ctr: 1
};
class wc {
  constructor(t, e, i) {
    this.subtle = void 0, this.aesIV = void 0, this.aesMode = void 0, this.subtle = t, this.aesIV = e, this.aesMode = i;
  }
  decrypt(t, e) {
    switch (this.aesMode) {
      case me.cbc:
        return this.subtle.decrypt({
          name: "AES-CBC",
          iv: this.aesIV
        }, e, t);
      case me.ctr:
        return this.subtle.decrypt(
          {
            name: "AES-CTR",
            counter: this.aesIV,
            length: 64
          },
          //64 : NIST SP800-38A standard suggests that the counter should occupy half of the counter block
          e,
          t
        );
      default:
        throw new Error(`[AESCrypto] invalid aes mode ${this.aesMode}`);
    }
  }
}
function Cc(n) {
  const t = n.byteLength, e = t && new DataView(n.buffer).getUint8(t - 1);
  return e ? n.slice(0, t - e) : n;
}
class Pc {
  constructor() {
    this.rcon = [0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54], this.subMix = [new Uint32Array(256), new Uint32Array(256), new Uint32Array(256), new Uint32Array(256)], this.invSubMix = [new Uint32Array(256), new Uint32Array(256), new Uint32Array(256), new Uint32Array(256)], this.sBox = new Uint32Array(256), this.invSBox = new Uint32Array(256), this.key = new Uint32Array(0), this.ksRows = 0, this.keySize = 0, this.keySchedule = void 0, this.invKeySchedule = void 0, this.initTable();
  }
  // Using view.getUint32() also swaps the byte order.
  uint8ArrayToUint32Array_(t) {
    const e = new DataView(t), i = new Uint32Array(4);
    for (let s = 0; s < 4; s++)
      i[s] = e.getUint32(s * 4);
    return i;
  }
  initTable() {
    const t = this.sBox, e = this.invSBox, i = this.subMix, s = i[0], r = i[1], a = i[2], o = i[3], c = this.invSubMix, l = c[0], h = c[1], d = c[2], u = c[3], f = new Uint32Array(256);
    let g = 0, v = 0, p = 0;
    for (p = 0; p < 256; p++)
      p < 128 ? f[p] = p << 1 : f[p] = p << 1 ^ 283;
    for (p = 0; p < 256; p++) {
      let y = v ^ v << 1 ^ v << 2 ^ v << 3 ^ v << 4;
      y = y >>> 8 ^ y & 255 ^ 99, t[g] = y, e[y] = g;
      const E = f[g], T = f[E], S = f[T];
      let x = f[y] * 257 ^ y * 16843008;
      s[g] = x << 24 | x >>> 8, r[g] = x << 16 | x >>> 16, a[g] = x << 8 | x >>> 24, o[g] = x, x = S * 16843009 ^ T * 65537 ^ E * 257 ^ g * 16843008, l[y] = x << 24 | x >>> 8, h[y] = x << 16 | x >>> 16, d[y] = x << 8 | x >>> 24, u[y] = x, g ? (g = E ^ f[f[f[S ^ E]]], v ^= f[f[v]]) : g = v = 1;
    }
  }
  expandKey(t) {
    const e = this.uint8ArrayToUint32Array_(t);
    let i = !0, s = 0;
    for (; s < e.length && i; )
      i = e[s] === this.key[s], s++;
    if (i)
      return;
    this.key = e;
    const r = this.keySize = e.length;
    if (r !== 4 && r !== 6 && r !== 8)
      throw new Error("Invalid aes key size=" + r);
    const a = this.ksRows = (r + 6 + 1) * 4;
    let o, c;
    const l = this.keySchedule = new Uint32Array(a), h = this.invKeySchedule = new Uint32Array(a), d = this.sBox, u = this.rcon, f = this.invSubMix, g = f[0], v = f[1], p = f[2], y = f[3];
    let E, T;
    for (o = 0; o < a; o++) {
      if (o < r) {
        E = l[o] = e[o];
        continue;
      }
      T = E, o % r === 0 ? (T = T << 8 | T >>> 24, T = d[T >>> 24] << 24 | d[T >>> 16 & 255] << 16 | d[T >>> 8 & 255] << 8 | d[T & 255], T ^= u[o / r | 0] << 24) : r > 6 && o % r === 4 && (T = d[T >>> 24] << 24 | d[T >>> 16 & 255] << 16 | d[T >>> 8 & 255] << 8 | d[T & 255]), l[o] = E = (l[o - r] ^ T) >>> 0;
    }
    for (c = 0; c < a; c++)
      o = a - c, c & 3 ? T = l[o] : T = l[o - 4], c < 4 || o <= 4 ? h[c] = T : h[c] = g[d[T >>> 24]] ^ v[d[T >>> 16 & 255]] ^ p[d[T >>> 8 & 255]] ^ y[d[T & 255]], h[c] = h[c] >>> 0;
  }
  // Adding this as a method greatly improves performance.
  networkToHostOrderSwap(t) {
    return t << 24 | (t & 65280) << 8 | (t & 16711680) >> 8 | t >>> 24;
  }
  decrypt(t, e, i) {
    const s = this.keySize + 6, r = this.invKeySchedule, a = this.invSBox, o = this.invSubMix, c = o[0], l = o[1], h = o[2], d = o[3], u = this.uint8ArrayToUint32Array_(i);
    let f = u[0], g = u[1], v = u[2], p = u[3];
    const y = new Int32Array(t), E = new Int32Array(y.length);
    let T, S, x, D, A, _, R, b, C, F, U, W, G, k;
    const H = this.networkToHostOrderSwap;
    for (; e < y.length; ) {
      for (C = H(y[e]), F = H(y[e + 1]), U = H(y[e + 2]), W = H(y[e + 3]), A = C ^ r[0], _ = W ^ r[1], R = U ^ r[2], b = F ^ r[3], G = 4, k = 1; k < s; k++)
        T = c[A >>> 24] ^ l[_ >> 16 & 255] ^ h[R >> 8 & 255] ^ d[b & 255] ^ r[G], S = c[_ >>> 24] ^ l[R >> 16 & 255] ^ h[b >> 8 & 255] ^ d[A & 255] ^ r[G + 1], x = c[R >>> 24] ^ l[b >> 16 & 255] ^ h[A >> 8 & 255] ^ d[_ & 255] ^ r[G + 2], D = c[b >>> 24] ^ l[A >> 16 & 255] ^ h[_ >> 8 & 255] ^ d[R & 255] ^ r[G + 3], A = T, _ = S, R = x, b = D, G = G + 4;
      T = a[A >>> 24] << 24 ^ a[_ >> 16 & 255] << 16 ^ a[R >> 8 & 255] << 8 ^ a[b & 255] ^ r[G], S = a[_ >>> 24] << 24 ^ a[R >> 16 & 255] << 16 ^ a[b >> 8 & 255] << 8 ^ a[A & 255] ^ r[G + 1], x = a[R >>> 24] << 24 ^ a[b >> 16 & 255] << 16 ^ a[A >> 8 & 255] << 8 ^ a[_ & 255] ^ r[G + 2], D = a[b >>> 24] << 24 ^ a[A >> 16 & 255] << 16 ^ a[_ >> 8 & 255] << 8 ^ a[R & 255] ^ r[G + 3], E[e] = H(T ^ f), E[e + 1] = H(D ^ g), E[e + 2] = H(x ^ v), E[e + 3] = H(S ^ p), f = C, g = F, v = U, p = W, e = e + 4;
    }
    return E.buffer;
  }
}
class kc {
  constructor(t, e, i) {
    this.subtle = void 0, this.key = void 0, this.aesMode = void 0, this.subtle = t, this.key = e, this.aesMode = i;
  }
  expandKey() {
    const t = Oc(this.aesMode);
    return this.subtle.importKey("raw", this.key, {
      name: t
    }, !1, ["encrypt", "decrypt"]);
  }
}
function Oc(n) {
  switch (n) {
    case me.cbc:
      return "AES-CBC";
    case me.ctr:
      return "AES-CTR";
    default:
      throw new Error(`[FastAESKey] invalid aes mode ${n}`);
  }
}
const Mc = 16;
class Ar {
  constructor(t, {
    removePKCS7Padding: e = !0
  } = {}) {
    if (this.logEnabled = !0, this.removePKCS7Padding = void 0, this.subtle = null, this.softwareDecrypter = null, this.key = null, this.fastAesKey = null, this.remainderData = null, this.currentIV = null, this.currentResult = null, this.useSoftware = void 0, this.enableSoftwareAES = void 0, this.enableSoftwareAES = t.enableSoftwareAES, this.removePKCS7Padding = e, e)
      try {
        const i = self.crypto;
        i && (this.subtle = i.subtle || i.webkitSubtle);
      } catch {
      }
    this.useSoftware = !this.subtle;
  }
  destroy() {
    this.subtle = null, this.softwareDecrypter = null, this.key = null, this.fastAesKey = null, this.remainderData = null, this.currentIV = null, this.currentResult = null;
  }
  isSync() {
    return this.useSoftware;
  }
  flush() {
    const {
      currentResult: t,
      remainderData: e
    } = this;
    if (!t || e)
      return this.reset(), null;
    const i = new Uint8Array(t);
    return this.reset(), this.removePKCS7Padding ? Cc(i) : i;
  }
  reset() {
    this.currentResult = null, this.currentIV = null, this.remainderData = null, this.softwareDecrypter && (this.softwareDecrypter = null);
  }
  decrypt(t, e, i, s) {
    return this.useSoftware ? new Promise((r, a) => {
      const o = ArrayBuffer.isView(t) ? t : new Uint8Array(t);
      this.softwareDecrypt(o, e, i, s);
      const c = this.flush();
      c ? r(c.buffer) : a(new Error("[softwareDecrypt] Failed to decrypt data"));
    }) : this.webCryptoDecrypt(new Uint8Array(t), e, i, s);
  }
  // Software decryption is progressive. Progressive decryption may not return a result on each call. Any cached
  // data is handled in the flush() call
  softwareDecrypt(t, e, i, s) {
    const {
      currentIV: r,
      currentResult: a,
      remainderData: o
    } = this;
    if (s !== me.cbc || e.byteLength !== 16)
      return rt.warn("SoftwareDecrypt: can only handle AES-128-CBC"), null;
    this.logOnce("JS AES decrypt"), o && (t = Nt(o, t), this.remainderData = null);
    const c = this.getValidChunk(t);
    if (!c.length)
      return null;
    r && (i = r);
    let l = this.softwareDecrypter;
    l || (l = this.softwareDecrypter = new Pc()), l.expandKey(e);
    const h = a;
    return this.currentResult = l.decrypt(c.buffer, 0, i), this.currentIV = c.slice(-16).buffer, h || null;
  }
  webCryptoDecrypt(t, e, i, s) {
    if (this.key !== e || !this.fastAesKey) {
      if (!this.subtle)
        return Promise.resolve(this.onWebCryptoError(t, e, i, s));
      this.key = e, this.fastAesKey = new kc(this.subtle, e, s);
    }
    return this.fastAesKey.expandKey().then((r) => this.subtle ? (this.logOnce("WebCrypto AES decrypt"), new wc(this.subtle, new Uint8Array(i), s).decrypt(t.buffer, r)) : Promise.reject(new Error("web crypto not initialized"))).catch((r) => (rt.warn(`[decrypter]: WebCrypto Error, disable WebCrypto API, ${r.name}: ${r.message}`), this.onWebCryptoError(t, e, i, s)));
  }
  onWebCryptoError(t, e, i, s) {
    const r = this.enableSoftwareAES;
    if (r) {
      this.useSoftware = !0, this.logEnabled = !0, this.softwareDecrypt(t, e, i, s);
      const a = this.flush();
      if (a)
        return a.buffer;
    }
    throw new Error("WebCrypto" + (r ? " and softwareDecrypt" : "") + ": failed to decrypt data");
  }
  getValidChunk(t) {
    let e = t;
    const i = t.length - t.length % Mc;
    return i !== t.length && (e = t.slice(0, i), this.remainderData = t.slice(i)), e;
  }
  logOnce(t) {
    this.logEnabled && (rt.log(`[decrypter]: ${t}`), this.logEnabled = !1);
  }
}
const un = Math.pow(2, 17);
class Fc {
  constructor(t) {
    this.config = void 0, this.loader = null, this.partLoadTimeout = -1, this.config = t;
  }
  destroy() {
    this.loader && (this.loader.destroy(), this.loader = null);
  }
  abort() {
    this.loader && this.loader.abort();
  }
  load(t, e) {
    const i = t.url;
    if (!i)
      return Promise.reject(new se({
        type: Y.NETWORK_ERROR,
        details: L.FRAG_LOAD_ERROR,
        fatal: !1,
        frag: t,
        error: new Error(`Fragment does not have a ${i ? "part list" : "url"}`),
        networkDetails: null
      }));
    this.abort();
    const s = this.config, r = s.fLoader, a = s.loader;
    return new Promise((o, c) => {
      if (this.loader && this.loader.destroy(), t.gap)
        if (t.tagList.some((g) => g[0] === "GAP")) {
          c(gn(t));
          return;
        } else
          t.gap = !1;
      const l = this.loader = r ? new r(s) : new a(s), h = fn(t);
      t.loader = l;
      const d = hn(s.fragLoadPolicy.default), u = {
        loadPolicy: d,
        timeout: d.maxLoadTimeMs,
        maxRetry: 0,
        retryDelay: 0,
        maxRetryDelay: 0,
        highWaterMark: t.sn === "initSegment" ? 1 / 0 : un
      };
      t.stats = l.stats;
      const f = {
        onSuccess: (g, v, p, y) => {
          this.resetLoader(t, l);
          let E = g.data;
          p.resetIV && t.decryptdata && (t.decryptdata.iv = new Uint8Array(E.slice(0, 16)), E = E.slice(16)), o({
            frag: t,
            part: null,
            payload: E,
            networkDetails: y
          });
        },
        onError: (g, v, p, y) => {
          this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.FRAG_LOAD_ERROR,
            fatal: !1,
            frag: t,
            response: st({
              url: i,
              data: void 0
            }, g),
            error: new Error(`HTTP Error ${g.code} ${g.text}`),
            networkDetails: p,
            stats: y
          }));
        },
        onAbort: (g, v, p) => {
          this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.INTERNAL_ABORTED,
            fatal: !1,
            frag: t,
            error: new Error("Aborted"),
            networkDetails: p,
            stats: g
          }));
        },
        onTimeout: (g, v, p) => {
          this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.FRAG_LOAD_TIMEOUT,
            fatal: !1,
            frag: t,
            error: new Error(`Timeout after ${u.timeout}ms`),
            networkDetails: p,
            stats: g
          }));
        }
      };
      e && (f.onProgress = (g, v, p, y) => e({
        frag: t,
        part: null,
        payload: p,
        networkDetails: y
      })), l.load(h, u, f);
    });
  }
  loadPart(t, e, i) {
    this.abort();
    const s = this.config, r = s.fLoader, a = s.loader;
    return new Promise((o, c) => {
      if (this.loader && this.loader.destroy(), t.gap || e.gap) {
        c(gn(t, e));
        return;
      }
      const l = this.loader = r ? new r(s) : new a(s), h = fn(t, e);
      t.loader = l;
      const d = hn(s.fragLoadPolicy.default), u = {
        loadPolicy: d,
        timeout: d.maxLoadTimeMs,
        maxRetry: 0,
        retryDelay: 0,
        maxRetryDelay: 0,
        highWaterMark: un
      };
      e.stats = l.stats, l.load(h, u, {
        onSuccess: (f, g, v, p) => {
          this.resetLoader(t, l), this.updateStatsFromPart(t, e);
          const y = {
            frag: t,
            part: e,
            payload: f.data,
            networkDetails: p
          };
          i(y), o(y);
        },
        onError: (f, g, v, p) => {
          this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.FRAG_LOAD_ERROR,
            fatal: !1,
            frag: t,
            part: e,
            response: st({
              url: h.url,
              data: void 0
            }, f),
            error: new Error(`HTTP Error ${f.code} ${f.text}`),
            networkDetails: v,
            stats: p
          }));
        },
        onAbort: (f, g, v) => {
          t.stats.aborted = e.stats.aborted, this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.INTERNAL_ABORTED,
            fatal: !1,
            frag: t,
            part: e,
            error: new Error("Aborted"),
            networkDetails: v,
            stats: f
          }));
        },
        onTimeout: (f, g, v) => {
          this.resetLoader(t, l), c(new se({
            type: Y.NETWORK_ERROR,
            details: L.FRAG_LOAD_TIMEOUT,
            fatal: !1,
            frag: t,
            part: e,
            error: new Error(`Timeout after ${u.timeout}ms`),
            networkDetails: v,
            stats: f
          }));
        }
      });
    });
  }
  updateStatsFromPart(t, e) {
    const i = t.stats, s = e.stats, r = s.total;
    if (i.loaded += s.loaded, r) {
      const c = Math.round(t.duration / e.duration), l = Math.min(Math.round(i.loaded / r), c), d = (c - l) * Math.round(i.loaded / l);
      i.total = i.loaded + d;
    } else
      i.total = Math.max(i.loaded, i.total);
    const a = i.loading, o = s.loading;
    a.start ? a.first += o.first - o.start : (a.start = o.start, a.first = o.first), a.end = o.end;
  }
  resetLoader(t, e) {
    t.loader = null, this.loader === e && (self.clearTimeout(this.partLoadTimeout), this.loader = null), e.destroy();
  }
}
function fn(n, t = null) {
  const e = t || n, i = {
    frag: n,
    part: t,
    responseType: "arraybuffer",
    url: e.url,
    headers: {},
    rangeStart: 0,
    rangeEnd: 0
  }, s = e.byteRangeStartOffset, r = e.byteRangeEndOffset;
  if (B(s) && B(r)) {
    var a;
    let o = s, c = r;
    if (n.sn === "initSegment" && $c((a = n.decryptdata) == null ? void 0 : a.method)) {
      const l = r - s;
      l % 16 && (c = r + (16 - l % 16)), s !== 0 && (i.resetIV = !0, o = s - 16);
    }
    i.rangeStart = o, i.rangeEnd = c;
  }
  return i;
}
function gn(n, t) {
  const e = new Error(`GAP ${n.gap ? "tag" : "attribute"} found`), i = {
    type: Y.MEDIA_ERROR,
    details: L.FRAG_GAP,
    fatal: !1,
    frag: n,
    error: e,
    networkDetails: null
  };
  return t && (i.part = t), (t || n).stats.aborted = !0, new se(i);
}
function $c(n) {
  return n === "AES-128" || n === "AES-256";
}
class se extends Error {
  constructor(t) {
    super(t.error.message), this.data = void 0, this.data = t;
  }
}
class Na extends Bt {
  constructor(t, e) {
    super(t, e), this._boundTick = void 0, this._tickTimer = null, this._tickInterval = null, this._tickCallCount = 0, this._boundTick = this.tick.bind(this);
  }
  destroy() {
    this.onHandlerDestroying(), this.onHandlerDestroyed();
  }
  onHandlerDestroying() {
    this.clearNextTick(), this.clearInterval();
  }
  onHandlerDestroyed() {
  }
  hasInterval() {
    return !!this._tickInterval;
  }
  hasNextTick() {
    return !!this._tickTimer;
  }
  /**
   * @param millis - Interval time (ms)
   * @eturns True when interval has been scheduled, false when already scheduled (no effect)
   */
  setInterval(t) {
    return this._tickInterval ? !1 : (this._tickCallCount = 0, this._tickInterval = self.setInterval(this._boundTick, t), !0);
  }
  /**
   * @returns True when interval was cleared, false when none was set (no effect)
   */
  clearInterval() {
    return this._tickInterval ? (self.clearInterval(this._tickInterval), this._tickInterval = null, !0) : !1;
  }
  /**
   * @returns True when timeout was cleared, false when none was set (no effect)
   */
  clearNextTick() {
    return this._tickTimer ? (self.clearTimeout(this._tickTimer), this._tickTimer = null, !0) : !1;
  }
  /**
   * Will call the subclass doTick implementation in this main loop tick
   * or in the next one (via setTimeout(,0)) in case it has already been called
   * in this tick (in case this is a re-entrant call).
   */
  tick() {
    this._tickCallCount++, this._tickCallCount === 1 && (this.doTick(), this._tickCallCount > 1 && this.tickImmediate(), this._tickCallCount = 0);
  }
  tickImmediate() {
    this.clearNextTick(), this._tickTimer = self.setTimeout(this._boundTick, 0);
  }
  /**
   * For subclass to implement task logic
   * @abstract
   */
  doTick() {
  }
}
class br {
  constructor(t, e, i, s = 0, r = -1, a = !1) {
    this.level = void 0, this.sn = void 0, this.part = void 0, this.id = void 0, this.size = void 0, this.partial = void 0, this.transmuxing = Di(), this.buffering = {
      audio: Di(),
      video: Di(),
      audiovideo: Di()
    }, this.level = t, this.sn = e, this.id = i, this.size = s, this.part = r, this.partial = a;
  }
}
function Di() {
  return {
    start: 0,
    executeStart: 0,
    executeEnd: 0,
    end: 0
  };
}
const mn = {
  length: 0,
  start: () => 0,
  end: () => 0
};
class q {
  /**
   * Return true if `media`'s buffered include `position`
   */
  static isBuffered(t, e) {
    if (t) {
      const i = q.getBuffered(t);
      for (let s = i.length; s--; )
        if (e >= i.start(s) && e <= i.end(s))
          return !0;
    }
    return !1;
  }
  static bufferedRanges(t) {
    if (t) {
      const e = q.getBuffered(t);
      return q.timeRangesToArray(e);
    }
    return [];
  }
  static timeRangesToArray(t) {
    const e = [];
    for (let i = 0; i < t.length; i++)
      e.push({
        start: t.start(i),
        end: t.end(i)
      });
    return e;
  }
  static bufferInfo(t, e, i) {
    if (t) {
      const s = q.bufferedRanges(t);
      if (s.length)
        return q.bufferedInfo(s, e, i);
    }
    return {
      len: 0,
      start: e,
      end: e,
      bufferedIndex: -1
    };
  }
  static bufferedInfo(t, e, i) {
    e = Math.max(0, e), t.length > 1 && t.sort((h, d) => h.start - d.start || d.end - h.end);
    let s = -1, r = [];
    if (i)
      for (let h = 0; h < t.length; h++) {
        e >= t[h].start && e <= t[h].end && (s = h);
        const d = r.length;
        if (d) {
          const u = r[d - 1].end;
          t[h].start - u < i ? t[h].end > u && (r[d - 1].end = t[h].end) : r.push(t[h]);
        } else
          r.push(t[h]);
      }
    else
      r = t;
    let a = 0, o, c = e, l = e;
    for (let h = 0; h < r.length; h++) {
      const d = r[h].start, u = r[h].end;
      if (s === -1 && e >= d && e <= u && (s = h), e + i >= d && e < u)
        c = d, l = u, a = l - e;
      else if (e + i < d) {
        o = d;
        break;
      }
    }
    return {
      len: a,
      start: c || 0,
      end: l || 0,
      nextStart: o,
      buffered: t,
      bufferedIndex: s
    };
  }
  /**
   * Safe method to get buffered property.
   * SourceBuffer.buffered may throw if SourceBuffer is removed from it's MediaSource
   */
  static getBuffered(t) {
    try {
      return t.buffered || mn;
    } catch (e) {
      return rt.log("failed to get media.buffered", e), mn;
    }
  }
}
const Ba = /\{\$([a-zA-Z0-9-_]+)\}/g;
function pn(n) {
  return Ba.test(n);
}
function tr(n, t) {
  if (n.variableList !== null || n.hasVariableRefs) {
    const e = n.variableList;
    return t.replace(Ba, (i) => {
      const s = i.substring(2, i.length - 1), r = e == null ? void 0 : e[s];
      return r === void 0 ? (n.playlistParsingError || (n.playlistParsingError = new Error(`Missing preceding EXT-X-DEFINE tag for Variable Reference: "${s}"`)), i) : r;
    });
  }
  return t;
}
function vn(n, t, e) {
  let i = n.variableList;
  i || (n.variableList = i = {});
  let s, r;
  if ("QUERYPARAM" in t) {
    s = t.QUERYPARAM;
    try {
      const a = new self.URL(e).searchParams;
      if (a.has(s))
        r = a.get(s);
      else
        throw new Error(`"${s}" does not match any query parameter in URI: "${e}"`);
    } catch (a) {
      n.playlistParsingError || (n.playlistParsingError = new Error(`EXT-X-DEFINE QUERYPARAM: ${a.message}`));
    }
  } else
    s = t.NAME, r = t.VALUE;
  s in i ? n.playlistParsingError || (n.playlistParsingError = new Error(`EXT-X-DEFINE duplicate Variable Name declarations: "${s}"`)) : i[s] = r || "";
}
function Nc(n, t, e) {
  const i = t.IMPORT;
  if (e && i in e) {
    let s = n.variableList;
    s || (n.variableList = s = {}), s[i] = e[i];
  } else
    n.playlistParsingError || (n.playlistParsingError = new Error(`EXT-X-DEFINE IMPORT attribute not found in Multivariant Playlist: "${i}"`));
}
const Bc = /^(\d+)x(\d+)$/, yn = /(.+?)=(".*?"|.*?)(?:,|$)/g;
class lt {
  constructor(t, e) {
    typeof t == "string" && (t = lt.parseAttrList(t, e)), nt(this, t);
  }
  get clientAttrs() {
    return Object.keys(this).filter((t) => t.substring(0, 2) === "X-");
  }
  decimalInteger(t) {
    const e = parseInt(this[t], 10);
    return e > Number.MAX_SAFE_INTEGER ? 1 / 0 : e;
  }
  hexadecimalInteger(t) {
    if (this[t]) {
      let e = (this[t] || "0x").slice(2);
      e = (e.length & 1 ? "0" : "") + e;
      const i = new Uint8Array(e.length / 2);
      for (let s = 0; s < e.length / 2; s++)
        i[s] = parseInt(e.slice(s * 2, s * 2 + 2), 16);
      return i;
    }
    return null;
  }
  hexadecimalIntegerAsNumber(t) {
    const e = parseInt(this[t], 16);
    return e > Number.MAX_SAFE_INTEGER ? 1 / 0 : e;
  }
  decimalFloatingPoint(t) {
    return parseFloat(this[t]);
  }
  optionalFloat(t, e) {
    const i = this[t];
    return i ? parseFloat(i) : e;
  }
  enumeratedString(t) {
    return this[t];
  }
  enumeratedStringList(t, e) {
    const i = this[t];
    return (i ? i.split(/[ ,]+/) : []).reduce((s, r) => (s[r.toLowerCase()] = !0, s), e);
  }
  bool(t) {
    return this[t] === "YES";
  }
  decimalResolution(t) {
    const e = Bc.exec(this[t]);
    if (e !== null)
      return {
        width: parseInt(e[1], 10),
        height: parseInt(e[2], 10)
      };
  }
  static parseAttrList(t, e) {
    let i;
    const s = {};
    for (yn.lastIndex = 0; (i = yn.exec(t)) !== null; ) {
      const a = i[1].trim();
      let o = i[2];
      const c = o.indexOf('"') === 0 && o.lastIndexOf('"') === o.length - 1;
      let l = !1;
      if (c)
        o = o.slice(1, -1);
      else
        switch (a) {
          case "IV":
          case "SCTE35-CMD":
          case "SCTE35-IN":
          case "SCTE35-OUT":
            l = !0;
        }
      if (e && (c || l))
        o = tr(e, o);
      else if (!l && !c)
        switch (a) {
          case "CLOSED-CAPTIONS":
            if (o === "NONE")
              break;
          // falls through
          case "ALLOWED-CPC":
          case "CLASS":
          case "ASSOC-LANGUAGE":
          case "AUDIO":
          case "BYTERANGE":
          case "CHANNELS":
          case "CHARACTERISTICS":
          case "CODECS":
          case "DATA-ID":
          case "END-DATE":
          case "GROUP-ID":
          case "ID":
          case "IMPORT":
          case "INSTREAM-ID":
          case "KEYFORMAT":
          case "KEYFORMATVERSIONS":
          case "LANGUAGE":
          case "NAME":
          case "PATHWAY-ID":
          case "QUERYPARAM":
          case "RECENTLY-REMOVED-DATERANGES":
          case "SERVER-URI":
          case "STABLE-RENDITION-ID":
          case "STABLE-VARIANT-ID":
          case "START-DATE":
          case "SUBTITLES":
          case "SUPPLEMENTAL-CODECS":
          case "URI":
          case "VALUE":
          case "VIDEO":
          case "X-ASSET-LIST":
          case "X-ASSET-URI":
            rt.warn(`${t}: attribute ${a} is missing quotes`);
        }
      s[a] = o;
    }
    return s;
  }
}
const Uc = "com.apple.hls.interstitial";
function Gc(n) {
  return n !== "ID" && n !== "CLASS" && n !== "CUE" && n !== "START-DATE" && n !== "DURATION" && n !== "END-DATE" && n !== "END-ON-NEXT";
}
function Kc(n) {
  return n === "SCTE35-OUT" || n === "SCTE35-IN" || n === "SCTE35-CMD";
}
class Ua {
  constructor(t, e, i = 0) {
    var s;
    if (this.attr = void 0, this.tagAnchor = void 0, this.tagOrder = void 0, this._startDate = void 0, this._endDate = void 0, this._dateAtEnd = void 0, this._cue = void 0, this._badValueForSameId = void 0, this.tagAnchor = (e == null ? void 0 : e.tagAnchor) || null, this.tagOrder = (s = e == null ? void 0 : e.tagOrder) != null ? s : i, e) {
      const r = e.attr;
      for (const a in r)
        if (Object.prototype.hasOwnProperty.call(t, a) && t[a] !== r[a]) {
          rt.warn(`DATERANGE tag attribute: "${a}" does not match for tags with ID: "${t.ID}"`), this._badValueForSameId = a;
          break;
        }
      t = nt(new lt({}), r, t);
    }
    if (this.attr = t, e ? (this._startDate = e._startDate, this._cue = e._cue, this._endDate = e._endDate, this._dateAtEnd = e._dateAtEnd) : this._startDate = new Date(t["START-DATE"]), "END-DATE" in this.attr) {
      const r = (e == null ? void 0 : e.endDate) || new Date(this.attr["END-DATE"]);
      B(r.getTime()) && (this._endDate = r);
    }
  }
  get id() {
    return this.attr.ID;
  }
  get class() {
    return this.attr.CLASS;
  }
  get cue() {
    const t = this._cue;
    return t === void 0 ? this._cue = this.attr.enumeratedStringList(this.attr.CUE ? "CUE" : "X-CUE", {
      pre: !1,
      post: !1,
      once: !1
    }) : t;
  }
  get startTime() {
    const {
      tagAnchor: t
    } = this;
    return t === null || t.programDateTime === null ? (rt.warn(`Expected tagAnchor Fragment with PDT set for DateRange "${this.id}": ${t}`), NaN) : t.start + (this.startDate.getTime() - t.programDateTime) / 1e3;
  }
  get startDate() {
    return this._startDate;
  }
  get endDate() {
    const t = this._endDate || this._dateAtEnd;
    if (t)
      return t;
    const e = this.duration;
    return e !== null ? this._dateAtEnd = new Date(this._startDate.getTime() + e * 1e3) : null;
  }
  get duration() {
    if ("DURATION" in this.attr) {
      const t = this.attr.decimalFloatingPoint("DURATION");
      if (B(t))
        return t;
    } else if (this._endDate)
      return (this._endDate.getTime() - this._startDate.getTime()) / 1e3;
    return null;
  }
  get plannedDuration() {
    return "PLANNED-DURATION" in this.attr ? this.attr.decimalFloatingPoint("PLANNED-DURATION") : null;
  }
  get endOnNext() {
    return this.attr.bool("END-ON-NEXT");
  }
  get isInterstitial() {
    return this.class === Uc;
  }
  get isValid() {
    return !!this.id && !this._badValueForSameId && B(this.startDate.getTime()) && (this.duration === null || this.duration >= 0) && (!this.endOnNext || !!this.class) && (!this.attr.CUE || !this.cue.pre && !this.cue.post || this.cue.pre !== this.cue.post) && (!this.isInterstitial || "X-ASSET-URI" in this.attr || "X-ASSET-LIST" in this.attr);
  }
}
const Hc = 10;
class Vc {
  constructor(t) {
    this.PTSKnown = !1, this.alignedSliding = !1, this.averagetargetduration = void 0, this.endCC = 0, this.endSN = 0, this.fragments = void 0, this.fragmentHint = void 0, this.partList = null, this.dateRanges = void 0, this.dateRangeTagCount = 0, this.live = !0, this.requestScheduled = -1, this.ageHeader = 0, this.advancedDateTime = void 0, this.updated = !0, this.advanced = !0, this.misses = 0, this.startCC = 0, this.startSN = 0, this.startTimeOffset = null, this.targetduration = 0, this.totalduration = 0, this.type = null, this.url = void 0, this.m3u8 = "", this.version = null, this.canBlockReload = !1, this.canSkipUntil = 0, this.canSkipDateRanges = !1, this.skippedSegments = 0, this.recentlyRemovedDateranges = void 0, this.partHoldBack = 0, this.holdBack = 0, this.partTarget = 0, this.preloadHint = void 0, this.renditionReports = void 0, this.tuneInGoal = 0, this.deltaUpdateFailed = void 0, this.driftStartTime = 0, this.driftEndTime = 0, this.driftStart = 0, this.driftEnd = 0, this.encryptedFragments = void 0, this.playlistParsingError = null, this.variableList = null, this.hasVariableRefs = !1, this.appliedTimelineOffset = void 0, this.fragments = [], this.encryptedFragments = [], this.dateRanges = {}, this.url = t;
  }
  reloaded(t) {
    if (!t) {
      this.advanced = !0, this.updated = !0;
      return;
    }
    const e = this.lastPartSn - t.lastPartSn, i = this.lastPartIndex - t.lastPartIndex;
    this.updated = this.endSN !== t.endSN || !!i || !!e || !this.live, this.advanced = this.endSN > t.endSN || e > 0 || e === 0 && i > 0, this.updated || this.advanced ? this.misses = Math.floor(t.misses * 0.6) : this.misses = t.misses + 1;
  }
  hasKey(t) {
    return this.encryptedFragments.some((e) => {
      let i = e.decryptdata;
      return i || (e.setKeyFormat(t.keyFormat), i = e.decryptdata), !!i && t.matches(i);
    });
  }
  get hasProgramDateTime() {
    return this.fragments.length ? B(this.fragments[this.fragments.length - 1].programDateTime) : !1;
  }
  get levelTargetDuration() {
    return this.averagetargetduration || this.targetduration || Hc;
  }
  get drift() {
    const t = this.driftEndTime - this.driftStartTime;
    return t > 0 ? (this.driftEnd - this.driftStart) * 1e3 / t : 1;
  }
  get edge() {
    return this.partEnd || this.fragmentEnd;
  }
  get partEnd() {
    var t;
    return (t = this.partList) != null && t.length ? this.partList[this.partList.length - 1].end : this.fragmentEnd;
  }
  get fragmentEnd() {
    return this.fragments.length ? this.fragments[this.fragments.length - 1].end : 0;
  }
  get fragmentStart() {
    return this.fragments.length ? this.fragments[0].start : 0;
  }
  get age() {
    return this.advancedDateTime ? Math.max(Date.now() - this.advancedDateTime, 0) / 1e3 : 0;
  }
  get lastPartIndex() {
    var t;
    return (t = this.partList) != null && t.length ? this.partList[this.partList.length - 1].index : -1;
  }
  get maxPartIndex() {
    const t = this.partList;
    if (t) {
      const e = this.lastPartIndex;
      if (e !== -1) {
        for (let i = t.length; i--; )
          if (t[i].index > e)
            return t[i].index;
        return e;
      }
    }
    return 0;
  }
  get lastPartSn() {
    var t;
    return (t = this.partList) != null && t.length ? this.partList[this.partList.length - 1].fragment.sn : this.endSN;
  }
  get expired() {
    if (this.live && this.age && this.misses < 3) {
      const t = this.partEnd - this.fragmentStart;
      return this.age > Math.max(t, this.totalduration) + this.levelTargetDuration;
    }
    return !1;
  }
}
function ss(n, t) {
  return n.length === t.length ? !n.some((e, i) => e !== t[i]) : !1;
}
function En(n, t) {
  return !n && !t ? !0 : !n || !t ? !1 : ss(n, t);
}
function Ye(n) {
  return n === "AES-128" || n === "AES-256" || n === "AES-256-CTR";
}
function Ir(n) {
  switch (n) {
    case "AES-128":
    case "AES-256":
      return me.cbc;
    case "AES-256-CTR":
      return me.ctr;
    default:
      throw new Error(`invalid full segment method ${n}`);
  }
}
function Lr(n) {
  return Uint8Array.from(atob(n), (t) => t.charCodeAt(0));
}
function er(n) {
  return Uint8Array.from(unescape(encodeURIComponent(n)), (t) => t.charCodeAt(0));
}
function Wc(n) {
  const t = er(n).subarray(0, 16), e = new Uint8Array(16);
  return e.set(t, 16 - t.length), e;
}
function Ga(n) {
  const t = function(i, s, r) {
    const a = i[s];
    i[s] = i[r], i[r] = a;
  };
  t(n, 0, 3), t(n, 1, 2), t(n, 4, 5), t(n, 6, 7);
}
function Ka(n) {
  const t = n.split(":");
  let e = null;
  if (t[0] === "data" && t.length === 2) {
    const i = t[1].split(";"), s = i[i.length - 1].split(",");
    if (s.length === 2) {
      const r = s[0] === "base64", a = s[1];
      r ? (i.splice(-1, 1), e = Lr(a)) : e = Wc(a);
    }
  }
  return e;
}
const rs = typeof self < "u" ? self : void 0;
var ct = {
  CLEARKEY: "org.w3.clearkey",
  FAIRPLAY: "com.apple.fps",
  PLAYREADY: "com.microsoft.playready",
  WIDEVINE: "com.widevine.alpha"
}, bt = {
  CLEARKEY: "org.w3.clearkey",
  FAIRPLAY: "com.apple.streamingkeydelivery",
  PLAYREADY: "com.microsoft.playready",
  WIDEVINE: "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"
};
function Hi(n) {
  switch (n) {
    case bt.FAIRPLAY:
      return ct.FAIRPLAY;
    case bt.PLAYREADY:
      return ct.PLAYREADY;
    case bt.WIDEVINE:
      return ct.WIDEVINE;
    case bt.CLEARKEY:
      return ct.CLEARKEY;
  }
}
function bs(n) {
  switch (n) {
    case ct.FAIRPLAY:
      return bt.FAIRPLAY;
    case ct.PLAYREADY:
      return bt.PLAYREADY;
    case ct.WIDEVINE:
      return bt.WIDEVINE;
    case ct.CLEARKEY:
      return bt.CLEARKEY;
  }
}
function hi(n) {
  const {
    drmSystems: t,
    widevineLicenseUrl: e
  } = n, i = t ? [ct.FAIRPLAY, ct.WIDEVINE, ct.PLAYREADY, ct.CLEARKEY].filter((s) => !!t[s]) : [];
  return !i[ct.WIDEVINE] && e && i.push(ct.WIDEVINE), i;
}
const Ha = (function(n) {
  return rs != null && (n = rs.navigator) != null && n.requestMediaKeySystemAccess ? self.navigator.requestMediaKeySystemAccess.bind(self.navigator) : null;
})();
function Yc(n, t, e, i) {
  let s;
  switch (n) {
    case ct.FAIRPLAY:
      s = ["cenc", "sinf"];
      break;
    case ct.WIDEVINE:
    case ct.PLAYREADY:
      s = ["cenc"];
      break;
    case ct.CLEARKEY:
      s = ["cenc", "keyids"];
      break;
    default:
      throw new Error(`Unknown key-system: ${n}`);
  }
  return zc(s, t, e, i);
}
function zc(n, t, e, i) {
  return [{
    initDataTypes: n,
    persistentState: i.persistentState || "optional",
    distinctiveIdentifier: i.distinctiveIdentifier || "optional",
    sessionTypes: i.sessionTypes || [i.sessionType || "temporary"],
    audioCapabilities: t.map((r) => ({
      contentType: `audio/mp4; codecs=${r}`,
      robustness: i.audioRobustness || "",
      encryptionScheme: i.audioEncryptionScheme || null
    })),
    videoCapabilities: e.map((r) => ({
      contentType: `video/mp4; codecs=${r}`,
      robustness: i.videoRobustness || "",
      encryptionScheme: i.videoEncryptionScheme || null
    }))
  }];
}
function jc(n) {
  var t;
  return !!n && (n.sessionType === "persistent-license" || !!((t = n.sessionTypes) != null && t.some((e) => e === "persistent-license")));
}
function Va(n) {
  const t = new Uint16Array(n.buffer, n.byteOffset, n.byteLength / 2), e = String.fromCharCode.apply(null, Array.from(t)), i = e.substring(e.indexOf("<"), e.length), a = new DOMParser().parseFromString(i, "text/xml").getElementsByTagName("KID")[0];
  if (a) {
    const o = a.childNodes[0] ? a.childNodes[0].nodeValue : a.getAttribute("VALUE");
    if (o) {
      const c = Lr(o).subarray(0, 16);
      return Ga(c), c;
    }
  }
  return null;
}
let Ue = {};
class ue {
  static clearKeyUriToKeyIdMap() {
    Ue = {};
  }
  static setKeyIdForUri(t, e) {
    Ue[t] = e;
  }
  static addKeyIdForUri(t) {
    const e = Object.keys(Ue).length % Number.MAX_SAFE_INTEGER, i = new Uint8Array(16);
    return new DataView(i.buffer, 12, 4).setUint32(0, e), Ue[t] = i, i;
  }
  constructor(t, e, i, s = [1], r = null, a) {
    this.uri = void 0, this.method = void 0, this.keyFormat = void 0, this.keyFormatVersions = void 0, this.encrypted = void 0, this.isCommonEncryption = void 0, this.iv = null, this.key = null, this.keyId = null, this.pssh = null, this.method = t, this.uri = e, this.keyFormat = i, this.keyFormatVersions = s, this.iv = r, this.encrypted = t ? t !== "NONE" : !1, this.isCommonEncryption = this.encrypted && !Ye(t), a != null && a.startsWith("0x") && (this.keyId = new Uint8Array(ya(a)));
  }
  matches(t) {
    return t.uri === this.uri && t.method === this.method && t.encrypted === this.encrypted && t.keyFormat === this.keyFormat && ss(t.keyFormatVersions, this.keyFormatVersions) && En(t.iv, this.iv) && En(t.keyId, this.keyId);
  }
  isSupported() {
    if (this.method) {
      if (Ye(this.method) || this.method === "NONE")
        return !0;
      if (this.keyFormat === "identity")
        return this.method === "SAMPLE-AES";
      switch (this.keyFormat) {
        case bt.FAIRPLAY:
        case bt.WIDEVINE:
        case bt.PLAYREADY:
        case bt.CLEARKEY:
          return ["SAMPLE-AES", "SAMPLE-AES-CENC", "SAMPLE-AES-CTR"].indexOf(this.method) !== -1;
      }
    }
    return !1;
  }
  getDecryptData(t, e) {
    if (!this.encrypted || !this.uri)
      return null;
    if (Ye(this.method)) {
      let r = this.iv;
      return r || (typeof t != "number" && (rt.warn(`missing IV for initialization segment with method="${this.method}" - compliance issue`), t = 0), r = Xc(t)), new ue(this.method, this.uri, "identity", this.keyFormatVersions, r);
    }
    if (this.keyId) {
      const r = Ue[this.uri];
      if (r && !ss(this.keyId, r) && ue.setKeyIdForUri(this.uri, this.keyId), this.pssh)
        return this;
    }
    const i = Ka(this.uri);
    if (i)
      switch (this.keyFormat) {
        case bt.WIDEVINE:
          if (this.pssh = i, !this.keyId) {
            const r = Jl(i.buffer);
            if (r.length) {
              var s;
              const a = r[0];
              this.keyId = (s = a.kids) != null && s.length ? a.kids[0] : null;
            }
          }
          this.keyId || (this.keyId = Tn(e));
          break;
        case bt.PLAYREADY: {
          const r = new Uint8Array([154, 4, 240, 121, 152, 64, 66, 134, 171, 146, 230, 91, 224, 136, 95, 149]);
          this.pssh = Zl(r, null, i), this.keyId = Va(i);
          break;
        }
        default: {
          let r = i.subarray(0, 16);
          if (r.length !== 16) {
            const a = new Uint8Array(16);
            a.set(r, 16 - r.length), r = a;
          }
          this.keyId = r;
          break;
        }
      }
    if (!this.keyId || this.keyId.byteLength !== 16) {
      let r;
      r = qc(e), r || (r = Tn(e), r || (r = Ue[this.uri])), r && (this.keyId = r, ue.setKeyIdForUri(this.uri, r));
    }
    return this;
  }
}
function qc(n) {
  const t = n == null ? void 0 : n[bt.WIDEVINE];
  return t ? t.keyId : null;
}
function Tn(n) {
  const t = n == null ? void 0 : n[bt.PLAYREADY];
  if (t) {
    const e = Ka(t.uri);
    if (e)
      return Va(e);
  }
  return null;
}
function Xc(n) {
  const t = new Uint8Array(16);
  for (let e = 12; e < 16; e++)
    t[e] = n >> 8 * (15 - e) & 255;
  return t;
}
const Sn = /#EXT-X-STREAM-INF:([^\r\n]*)(?:[\r\n](?:#[^\r\n]*)?)*([^\r\n]+)|#EXT-X-(SESSION-DATA|SESSION-KEY|DEFINE|CONTENT-STEERING|START):([^\r\n]*)[\r\n]+/g, xn = /#EXT-X-MEDIA:(.*)/g, Qc = /^#EXT(?:INF|-X-TARGETDURATION):/m, Is = new RegExp([
  /#EXTINF:\s*(\d*(?:\.\d+)?)(?:,(.*)\s+)?/.source,
  // duration (#EXTINF:<duration>,<title>), group 1 => duration, group 2 => title
  /(?!#) *(\S[^\r\n]*)/.source,
  // segment URI, group 3 => the URI (note newline is not eaten)
  /#.*/.source
  // All other non-segment oriented tags will match with all groups empty
].join("|"), "g"), Zc = new RegExp([/#EXT-X-(PROGRAM-DATE-TIME|BYTERANGE|DATERANGE|DEFINE|KEY|MAP|PART|PART-INF|PLAYLIST-TYPE|PRELOAD-HINT|RENDITION-REPORT|SERVER-CONTROL|SKIP|START):(.+)/.source, /#EXT-X-(BITRATE|DISCONTINUITY-SEQUENCE|MEDIA-SEQUENCE|TARGETDURATION|VERSION): *(\d+)/.source, /#EXT-X-(DISCONTINUITY|ENDLIST|GAP|INDEPENDENT-SEGMENTS)/.source, /(#)([^:]*):(.*)/.source, /(#)(.*)(?:.*)\r?\n?/.source].join("|"));
class Qt {
  static findGroup(t, e) {
    for (let i = 0; i < t.length; i++) {
      const s = t[i];
      if (s.id === e)
        return s;
    }
  }
  static resolve(t, e) {
    return vr.buildAbsoluteURL(e, t, {
      alwaysNormalize: !0
    });
  }
  static isMediaPlaylist(t) {
    return Qc.test(t);
  }
  static parseMasterPlaylist(t, e) {
    const i = pn(t), s = {
      contentSteering: null,
      levels: [],
      playlistParsingError: null,
      sessionData: null,
      sessionKeys: null,
      startTimeOffset: null,
      variableList: null,
      hasVariableRefs: i
    }, r = [];
    if (Sn.lastIndex = 0, !t.startsWith("#EXTM3U"))
      return s.playlistParsingError = new Error("no EXTM3U delimiter"), s;
    let a;
    for (; (a = Sn.exec(t)) != null; )
      if (a[1]) {
        var o;
        const l = new lt(a[1], s), h = tr(s, a[2]), d = {
          attrs: l,
          bitrate: l.decimalInteger("BANDWIDTH") || l.decimalInteger("AVERAGE-BANDWIDTH"),
          name: l.NAME,
          url: Qt.resolve(h, e)
        }, u = l.decimalResolution("RESOLUTION");
        u && (d.width = u.width, d.height = u.height), In(l.CODECS, d);
        const f = l["SUPPLEMENTAL-CODECS"];
        f && (d.supplemental = {}, In(f, d.supplemental)), (o = d.unknownCodecs) != null && o.length || r.push(d), s.levels.push(d);
      } else if (a[3]) {
        const l = a[3], h = a[4];
        switch (l) {
          case "SESSION-DATA": {
            const d = new lt(h, s), u = d["DATA-ID"];
            u && (s.sessionData === null && (s.sessionData = {}), s.sessionData[u] = d);
            break;
          }
          case "SESSION-KEY": {
            const d = An(h, e, s);
            d.encrypted && d.isSupported() ? (s.sessionKeys === null && (s.sessionKeys = []), s.sessionKeys.push(d)) : rt.warn(`[Keys] Ignoring invalid EXT-X-SESSION-KEY tag: "${h}"`);
            break;
          }
          case "DEFINE": {
            {
              const d = new lt(h, s);
              vn(s, d, e);
            }
            break;
          }
          case "CONTENT-STEERING": {
            const d = new lt(h, s);
            s.contentSteering = {
              uri: Qt.resolve(d["SERVER-URI"], e),
              pathwayId: d["PATHWAY-ID"] || "."
            };
            break;
          }
          case "START": {
            s.startTimeOffset = bn(h);
            break;
          }
        }
      }
    const c = r.length > 0 && r.length < s.levels.length;
    return s.levels = c ? r : s.levels, s.levels.length === 0 && (s.playlistParsingError = new Error("no levels found in manifest")), s;
  }
  static parseMasterPlaylistMedia(t, e, i) {
    let s;
    const r = {}, a = i.levels, o = {
      AUDIO: a.map((l) => ({
        id: l.attrs.AUDIO,
        audioCodec: l.audioCodec
      })),
      SUBTITLES: a.map((l) => ({
        id: l.attrs.SUBTITLES,
        textCodec: l.textCodec
      })),
      "CLOSED-CAPTIONS": []
    };
    let c = 0;
    for (xn.lastIndex = 0; (s = xn.exec(t)) !== null; ) {
      const l = new lt(s[1], i), h = l.TYPE;
      if (h) {
        const d = o[h], u = r[h] || [];
        r[h] = u;
        const f = l.LANGUAGE, g = l["ASSOC-LANGUAGE"], v = l.CHANNELS, p = l.CHARACTERISTICS, y = l["INSTREAM-ID"], E = {
          attrs: l,
          bitrate: 0,
          id: c++,
          groupId: l["GROUP-ID"] || "",
          name: l.NAME || f || "",
          type: h,
          default: l.bool("DEFAULT"),
          autoselect: l.bool("AUTOSELECT"),
          forced: l.bool("FORCED"),
          lang: f,
          url: l.URI ? Qt.resolve(l.URI, e) : ""
        };
        if (g && (E.assocLang = g), v && (E.channels = v), p && (E.characteristics = p), y && (E.instreamId = y), d != null && d.length) {
          const T = Qt.findGroup(d, E.groupId) || d[0];
          Ln(E, T, "audioCodec"), Ln(E, T, "textCodec");
        }
        u.push(E);
      }
    }
    return r;
  }
  static parseLevelPlaylist(t, e, i, s, r, a) {
    var o;
    const c = {
      url: e
    }, l = new Vc(e), h = l.fragments, d = [];
    let u = null, f = 0, g = 0, v = 0, p = 0, y = 0, E = null, T = new Ss(s, c), S, x, D, A = -1, _ = !1, R = null, b;
    if (Is.lastIndex = 0, l.m3u8 = t, l.hasVariableRefs = pn(t), ((o = Is.exec(t)) == null ? void 0 : o[0]) !== "#EXTM3U")
      return l.playlistParsingError = new Error("Missing format identifier #EXTM3U"), l;
    for (; (S = Is.exec(t)) !== null; ) {
      _ && (_ = !1, T = new Ss(s, c), T.playlistOffset = v, T.setStart(v), T.sn = f, T.cc = p, y && (T.bitrate = y), T.level = i, u && (T.initSegment = u, u.rawProgramDateTime && (T.rawProgramDateTime = u.rawProgramDateTime, u.rawProgramDateTime = null), R && (T.setByteRange(R), R = null)));
      const W = S[1];
      if (W) {
        T.duration = parseFloat(W);
        const G = (" " + S[2]).slice(1);
        T.title = G || null, T.tagList.push(G ? ["INF", W, G] : ["INF", W]);
      } else if (S[3]) {
        if (B(T.duration)) {
          T.playlistOffset = v, T.setStart(v), D && _n(T, D, l), T.sn = f, T.level = i, T.cc = p, h.push(T);
          const G = (" " + S[3]).slice(1);
          T.relurl = tr(l, G), ir(T, E, d), E = T, v += T.duration, f++, g = 0, _ = !0;
        }
      } else {
        if (S = S[0].match(Zc), !S) {
          rt.warn("No matches on slow regex match for level playlist!");
          continue;
        }
        for (x = 1; x < S.length && S[x] === void 0; x++)
          ;
        const G = (" " + S[x]).slice(1), k = (" " + S[x + 1]).slice(1), H = S[x + 2] ? (" " + S[x + 2]).slice(1) : null;
        switch (G) {
          case "BYTERANGE":
            E ? T.setByteRange(k, E) : T.setByteRange(k);
            break;
          case "PROGRAM-DATE-TIME":
            T.rawProgramDateTime = k, T.tagList.push(["PROGRAM-DATE-TIME", k]), A === -1 && (A = h.length);
            break;
          case "PLAYLIST-TYPE":
            l.type && ee(l, G, S), l.type = k.toUpperCase();
            break;
          case "MEDIA-SEQUENCE":
            l.startSN !== 0 ? ee(l, G, S) : h.length > 0 && Dn(l, G, S), f = l.startSN = parseInt(k);
            break;
          case "SKIP": {
            l.skippedSegments && ee(l, G, S);
            const $ = new lt(k, l), V = $.decimalInteger("SKIPPED-SEGMENTS");
            if (B(V)) {
              l.skippedSegments += V;
              for (let O = V; O--; )
                h.push(null);
              f += V;
            }
            const z = $.enumeratedString("RECENTLY-REMOVED-DATERANGES");
            z && (l.recentlyRemovedDateranges = (l.recentlyRemovedDateranges || []).concat(z.split("	")));
            break;
          }
          case "TARGETDURATION":
            l.targetduration !== 0 && ee(l, G, S), l.targetduration = Math.max(parseInt(k), 1);
            break;
          case "VERSION":
            l.version !== null && ee(l, G, S), l.version = parseInt(k);
            break;
          case "INDEPENDENT-SEGMENTS":
            break;
          case "ENDLIST":
            l.live || ee(l, G, S), l.live = !1;
            break;
          case "#":
            (k || H) && T.tagList.push(H ? [k, H] : [k]);
            break;
          case "DISCONTINUITY":
            p++, T.tagList.push(["DIS"]);
            break;
          case "GAP":
            T.gap = !0, T.tagList.push([G]);
            break;
          case "BITRATE":
            T.tagList.push([G, k]), y = parseInt(k) * 1e3, B(y) ? T.bitrate = y : y = 0;
            break;
          case "DATERANGE": {
            const $ = new lt(k, l), V = new Ua($, l.dateRanges[$.ID], l.dateRangeTagCount);
            l.dateRangeTagCount++, V.isValid || l.skippedSegments ? l.dateRanges[V.id] = V : rt.warn(`Ignoring invalid DATERANGE tag: "${k}"`), T.tagList.push(["EXT-X-DATERANGE", k]);
            break;
          }
          case "DEFINE": {
            {
              const $ = new lt(k, l);
              "IMPORT" in $ ? Nc(l, $, a) : vn(l, $, e);
            }
            break;
          }
          case "DISCONTINUITY-SEQUENCE":
            l.startCC !== 0 ? ee(l, G, S) : h.length > 0 && Dn(l, G, S), l.startCC = p = parseInt(k);
            break;
          case "KEY": {
            const $ = An(k, e, l);
            if ($.isSupported()) {
              if ($.method === "NONE") {
                D = void 0;
                break;
              }
              D || (D = {});
              const V = D[$.keyFormat];
              V != null && V.matches($) || (V && (D = nt({}, D)), D[$.keyFormat] = $);
            } else
              rt.warn(`[Keys] Ignoring unsupported EXT-X-KEY tag: "${k}"`);
            break;
          }
          case "START":
            l.startTimeOffset = bn(k);
            break;
          case "MAP": {
            const $ = new lt(k, l);
            if (T.duration) {
              const V = new Ss(s, c);
              Rn(V, $, i, D), u = V, T.initSegment = u, u.rawProgramDateTime && !T.rawProgramDateTime && (T.rawProgramDateTime = u.rawProgramDateTime);
            } else {
              const V = T.byteRangeEndOffset;
              if (V) {
                const z = T.byteRangeStartOffset;
                R = `${V - z}@${z}`;
              } else
                R = null;
              Rn(T, $, i, D), u = T, _ = !0;
            }
            u.cc = p;
            break;
          }
          case "SERVER-CONTROL": {
            b && ee(l, G, S), b = new lt(k), l.canBlockReload = b.bool("CAN-BLOCK-RELOAD"), l.canSkipUntil = b.optionalFloat("CAN-SKIP-UNTIL", 0), l.canSkipDateRanges = l.canSkipUntil > 0 && b.bool("CAN-SKIP-DATERANGES"), l.partHoldBack = b.optionalFloat("PART-HOLD-BACK", 0), l.holdBack = b.optionalFloat("HOLD-BACK", 0);
            break;
          }
          case "PART-INF": {
            l.partTarget && ee(l, G, S);
            const $ = new lt(k);
            l.partTarget = $.decimalFloatingPoint("PART-TARGET");
            break;
          }
          case "PART": {
            let $ = l.partList;
            $ || ($ = l.partList = []);
            const V = g > 0 ? $[$.length - 1] : void 0, z = g++, O = new lt(k, l), M = new Nl(O, T, c, z, V);
            $.push(M), T.duration += M.duration;
            break;
          }
          case "PRELOAD-HINT": {
            const $ = new lt(k, l);
            l.preloadHint = $;
            break;
          }
          case "RENDITION-REPORT": {
            const $ = new lt(k, l);
            l.renditionReports = l.renditionReports || [], l.renditionReports.push($);
            break;
          }
          default:
            rt.warn(`line parsed but not handled: ${S}`);
            break;
        }
      }
    }
    E && !E.relurl ? (h.pop(), v -= E.duration, l.partList && (l.fragmentHint = E)) : l.partList && (ir(T, E, d), T.cc = p, l.fragmentHint = T, D && _n(T, D, l)), l.targetduration || (l.playlistParsingError = new Error("Missing Target Duration"));
    const C = h.length, F = h[0], U = h[C - 1];
    if (v += l.skippedSegments * l.targetduration, v > 0 && C && U) {
      l.averagetargetduration = v / C;
      const W = U.sn;
      l.endSN = W !== "initSegment" ? W : 0, l.live || (U.endList = !0), A > 0 && (th(h, A), F && d.unshift(F));
    }
    return l.fragmentHint && (v += l.fragmentHint.duration), l.totalduration = v, d.length && l.dateRangeTagCount && F && Wa(d, l), l.endCC = p, l;
  }
}
function Wa(n, t) {
  let e = n.length;
  if (!e)
    if (t.hasProgramDateTime) {
      const o = t.fragments[t.fragments.length - 1];
      n.push(o), e++;
    } else
      return;
  const i = n[e - 1], s = t.live ? 1 / 0 : t.totalduration, r = Object.keys(t.dateRanges);
  for (let o = r.length; o--; ) {
    const c = t.dateRanges[r[o]], l = c.startDate.getTime();
    c.tagAnchor = i.ref;
    for (let h = e; h--; ) {
      var a;
      if (((a = n[h]) == null ? void 0 : a.sn) < t.startSN)
        break;
      const d = Jc(t, l, n, h, s);
      if (d !== -1) {
        c.tagAnchor = t.fragments[d].ref;
        break;
      }
    }
  }
}
function Jc(n, t, e, i, s) {
  const r = e[i];
  if (r) {
    const o = r.programDateTime;
    if (t >= o || i === 0) {
      var a;
      const c = (((a = e[i + 1]) == null ? void 0 : a.start) || s) - r.start;
      if (t <= o + c * 1e3) {
        const l = e[i].sn - n.startSN;
        if (l < 0)
          return -1;
        const h = n.fragments;
        if (h.length > e.length) {
          const u = (e[i + 1] || h[h.length - 1]).sn - n.startSN;
          for (let f = u; f > l; f--) {
            const g = h[f].programDateTime;
            if (t >= g && t < g + h[f].duration * 1e3)
              return f;
          }
        }
        return l;
      }
    }
  }
  return -1;
}
function An(n, t, e) {
  var i, s;
  const r = new lt(n, e), a = (i = r.METHOD) != null ? i : "", o = r.URI, c = r.hexadecimalInteger("IV"), l = r.KEYFORMATVERSIONS, h = (s = r.KEYFORMAT) != null ? s : "identity";
  o && r.IV && !c && rt.error(`Invalid IV: ${r.IV}`);
  const d = o ? Qt.resolve(o, t) : "", u = (l || "1").split("/").map(Number).filter(Number.isFinite);
  return new ue(a, d, h, u, c, r.KEYID);
}
function bn(n) {
  const e = new lt(n).decimalFloatingPoint("TIME-OFFSET");
  return B(e) ? e : null;
}
function In(n, t) {
  let e = (n || "").split(/[ ,]+/).filter((i) => i);
  ["video", "audio", "text"].forEach((i) => {
    const s = e.filter((r) => Tr(r, i));
    s.length && (t[`${i}Codec`] = s.map((r) => r.split("/")[0]).join(","), e = e.filter((r) => s.indexOf(r) === -1));
  }), t.unknownCodecs = e;
}
function Ln(n, t, e) {
  const i = t[e];
  i && (n[e] = i);
}
function th(n, t) {
  let e = n[t];
  for (let i = t; i--; ) {
    const s = n[i];
    if (!s)
      return;
    s.programDateTime = e.programDateTime - s.duration * 1e3, e = s;
  }
}
function ir(n, t, e) {
  n.rawProgramDateTime ? e.push(n) : t != null && t.programDateTime && (n.programDateTime = t.endProgramDateTime);
}
function Rn(n, t, e, i) {
  n.relurl = t.URI, t.BYTERANGE && n.setByteRange(t.BYTERANGE), n.level = e, n.sn = "initSegment", i && (n.levelkeys = i), n.initSegment = null;
}
function _n(n, t, e) {
  n.levelkeys = t;
  const {
    encryptedFragments: i
  } = e;
  (!i.length || i[i.length - 1].levelkeys !== t) && Object.keys(t).some((s) => t[s].isCommonEncryption) && i.push(n);
}
function ee(n, t, e) {
  n.playlistParsingError = new Error(`#EXT-X-${t} must not appear more than once (${e[0]})`);
}
function Dn(n, t, e) {
  n.playlistParsingError = new Error(`#EXT-X-${t} must appear before the first Media Segment (${e[0]})`);
}
function Ls(n, t) {
  const e = t.startPTS;
  if (B(e)) {
    let i = 0, s;
    t.sn > n.sn ? (i = e - n.start, s = n) : (i = n.start - e, s = t), s.duration !== i && s.setDuration(i);
  } else t.sn > n.sn ? n.cc === t.cc && n.minEndPTS ? t.setStart(n.start + (n.minEndPTS - n.start)) : t.setStart(n.start + n.duration) : t.setStart(Math.max(n.start - t.duration, 0));
}
function Ya(n, t, e, i, s, r, a) {
  i - e <= 0 && (a.warn("Fragment should have a positive duration", t), i = e + t.duration, r = s + t.duration);
  let c = e, l = i;
  const h = t.startPTS, d = t.endPTS;
  if (B(h)) {
    const y = Math.abs(h - e);
    n && y > n.totalduration ? a.warn(`media timestamps and playlist times differ by ${y}s for level ${t.level} ${n.url}`) : B(t.deltaPTS) ? t.deltaPTS = Math.max(y, t.deltaPTS) : t.deltaPTS = y, c = Math.max(e, h), e = Math.min(e, h), s = t.startDTS !== void 0 ? Math.min(s, t.startDTS) : s, l = Math.min(i, d), i = Math.max(i, d), r = t.endDTS !== void 0 ? Math.max(r, t.endDTS) : r;
  }
  const u = e - t.start;
  t.start !== 0 && t.setStart(e), t.setDuration(i - t.start), t.startPTS = e, t.maxStartPTS = c, t.startDTS = s, t.endPTS = i, t.minEndPTS = l, t.endDTS = r;
  const f = t.sn;
  if (!n || f < n.startSN || f > n.endSN)
    return 0;
  let g;
  const v = f - n.startSN, p = n.fragments;
  for (p[v] = t, g = v; g > 0; g--)
    Ls(p[g], p[g - 1]);
  for (g = v; g < p.length - 1; g++)
    Ls(p[g], p[g + 1]);
  return n.fragmentHint && Ls(p[p.length - 1], n.fragmentHint), n.PTSKnown = n.alignedSliding = !0, u;
}
function eh(n, t, e) {
  if (n === t)
    return;
  let i = null;
  const s = n.fragments;
  for (let h = s.length - 1; h >= 0; h--) {
    const d = s[h].initSegment;
    if (d) {
      i = d;
      break;
    }
  }
  n.fragmentHint && delete n.fragmentHint.endPTS;
  let r;
  rh(n, t, (h, d, u, f) => {
    if ((!t.startCC || t.skippedSegments) && d.cc !== h.cc) {
      const g = h.cc - d.cc;
      for (let v = u; v < f.length; v++)
        f[v].cc += g;
      t.endCC = f[f.length - 1].cc;
    }
    B(h.startPTS) && B(h.endPTS) && (d.setStart(d.startPTS = h.startPTS), d.startDTS = h.startDTS, d.maxStartPTS = h.maxStartPTS, d.endPTS = h.endPTS, d.endDTS = h.endDTS, d.minEndPTS = h.minEndPTS, d.setDuration(h.endPTS - h.startPTS), d.duration && (r = d), t.PTSKnown = t.alignedSliding = !0), h.hasStreams && (d.elementaryStreams = h.elementaryStreams), d.loader = h.loader, h.hasStats && (d.stats = h.stats), h.initSegment && (d.initSegment = h.initSegment, i = h.initSegment);
  });
  const a = t.fragments, o = t.fragmentHint ? a.concat(t.fragmentHint) : a;
  if (i && o.forEach((h) => {
    var d;
    h && (!h.initSegment || h.initSegment.relurl === ((d = i) == null ? void 0 : d.relurl)) && (h.initSegment = i);
  }), t.skippedSegments) {
    if (t.deltaUpdateFailed = a.some((h) => !h), t.deltaUpdateFailed) {
      e.warn("[level-helper] Previous playlist missing segments skipped in delta playlist");
      for (let h = t.skippedSegments; h--; )
        a.shift();
      t.startSN = a[0].sn;
    } else {
      t.canSkipDateRanges && (t.dateRanges = ih(n.dateRanges, t, e));
      const h = n.fragments.filter((d) => d.rawProgramDateTime);
      if (n.hasProgramDateTime && !t.hasProgramDateTime)
        for (let d = 1; d < o.length; d++)
          o[d].programDateTime === null && ir(o[d], o[d - 1], h);
      Wa(h, t);
    }
    t.endCC = a[a.length - 1].cc;
  }
  if (!t.startCC) {
    var c;
    const h = qa(n, t.startSN - 1);
    t.startCC = (c = h == null ? void 0 : h.cc) != null ? c : a[0].cc;
  }
  sh(n.partList, t.partList, (h, d) => {
    d.elementaryStreams = h.elementaryStreams, d.stats = h.stats;
  }), r ? Ya(t, r, r.startPTS, r.endPTS, r.startDTS, r.endDTS, e) : za(n, t), a.length && (t.totalduration = t.edge - a[0].start), t.driftStartTime = n.driftStartTime, t.driftStart = n.driftStart;
  const l = t.advancedDateTime;
  if (t.advanced && l) {
    const h = t.edge;
    t.driftStart || (t.driftStartTime = l, t.driftStart = h), t.driftEndTime = l, t.driftEnd = h;
  } else
    t.driftEndTime = n.driftEndTime, t.driftEnd = n.driftEnd, t.advancedDateTime = n.advancedDateTime;
  t.requestScheduled === -1 && (t.requestScheduled = n.requestScheduled);
}
function ih(n, t, e) {
  const {
    dateRanges: i,
    recentlyRemovedDateranges: s
  } = t, r = nt({}, n);
  s && s.forEach((c) => {
    delete r[c];
  });
  const o = Object.keys(r).length;
  return o ? (Object.keys(i).forEach((c) => {
    const l = r[c], h = new Ua(i[c].attr, l);
    h.isValid ? (r[c] = h, l || (h.tagOrder += o)) : e.warn(`Ignoring invalid Playlist Delta Update DATERANGE tag: "${ot(i[c].attr)}"`);
  }), r) : i;
}
function sh(n, t, e) {
  if (n && t) {
    let i = 0;
    for (let s = 0, r = n.length; s <= r; s++) {
      const a = n[s], o = t[s + i];
      a && o && a.index === o.index && a.fragment.sn === o.fragment.sn ? e(a, o) : i--;
    }
  }
}
function rh(n, t, e) {
  const i = t.skippedSegments, s = Math.max(n.startSN, t.startSN) - t.startSN, r = (n.fragmentHint ? 1 : 0) + (i ? t.endSN : Math.min(n.endSN, t.endSN)) - t.startSN, a = t.startSN - n.startSN, o = t.fragmentHint ? t.fragments.concat(t.fragmentHint) : t.fragments, c = n.fragmentHint ? n.fragments.concat(n.fragmentHint) : n.fragments;
  for (let l = s; l <= r; l++) {
    const h = c[a + l];
    let d = o[l];
    if (i && !d && h && (d = t.fragments[l] = h), h && d) {
      e(h, d, l, o);
      const u = h.relurl, f = d.relurl;
      if (u && nh(u, f)) {
        t.playlistParsingError = wn(`media sequence mismatch ${d.sn}:`, n, t, h, d);
        return;
      } else if (h.cc !== d.cc) {
        t.playlistParsingError = wn(`discontinuity sequence mismatch (${h.cc}!=${d.cc})`, n, t, h, d);
        return;
      }
    }
  }
}
function wn(n, t, e, i, s) {
  return new Error(`${n} ${s.url}
Playlist starting @${t.startSN}
${t.m3u8}

Playlist starting @${e.startSN}
${e.m3u8}`);
}
function za(n, t, e = !0) {
  const i = t.startSN + t.skippedSegments - n.startSN, s = n.fragments, r = i >= 0;
  let a = 0;
  if (r && i < s.length)
    a = s[i].start;
  else if (r && t.startSN === n.endSN + 1)
    a = n.fragmentEnd;
  else if (r && e)
    a = n.fragmentStart + i * t.levelTargetDuration;
  else if (!t.skippedSegments && t.fragmentStart === 0)
    a = n.fragmentStart;
  else
    return;
  sr(t, a);
}
function sr(n, t) {
  if (t) {
    const e = n.fragments;
    for (let i = n.skippedSegments; i < e.length; i++)
      e[i].addStart(t);
    n.fragmentHint && n.fragmentHint.addStart(t);
  }
}
function ja(n, t = 1 / 0) {
  let e = 1e3 * n.targetduration;
  if (n.updated) {
    const i = n.fragments;
    if (i.length && e * 4 > t) {
      const r = i[i.length - 1].duration * 1e3;
      r < e && (e = r);
    }
  } else
    e /= 2;
  return Math.round(e);
}
function qa(n, t, e) {
  if (!n)
    return null;
  let i = n.fragments[t - n.startSN];
  return i || (i = n.fragmentHint, i && i.sn === t) ? i : t < n.startSN && e && e.sn === t ? e : null;
}
function Cn(n, t, e) {
  return n ? Xa(n.partList, t, e) : null;
}
function Xa(n, t, e) {
  if (n)
    for (let i = n.length; i--; ) {
      const s = n[i];
      if (s.index === e && s.fragment.sn === t)
        return s;
    }
  return null;
}
function Qa(n) {
  n.forEach((t, e) => {
    var i;
    (i = t.details) == null || i.fragments.forEach((s) => {
      s.level = e, s.initSegment && (s.initSegment.level = e);
    });
  });
}
function nh(n, t) {
  return n !== t && t ? Pn(n) !== Pn(t) : !1;
}
function Pn(n) {
  return n.replace(/\?[^?]*$/, "");
}
function di(n, t) {
  for (let i = 0, s = n.length; i < s; i++) {
    var e;
    if (((e = n[i]) == null ? void 0 : e.cc) === t)
      return n[i];
  }
  return null;
}
function ah(n, t) {
  return !!(n && t.startCC < n.endCC && t.endCC > n.startCC);
}
function kn(n, t) {
  const e = n.start + t;
  n.startPTS = e, n.setStart(e), n.endPTS = e + n.duration;
}
function Za(n, t) {
  const e = t.fragments;
  for (let i = 0, s = e.length; i < s; i++)
    kn(e[i], n);
  t.fragmentHint && kn(t.fragmentHint, n), t.alignedSliding = !0;
}
function oh(n, t) {
  n && (Ja(t, n), t.alignedSliding || ns(t, n), !t.alignedSliding && !t.skippedSegments && za(n, t, !1));
}
function Ja(n, t) {
  if (!ah(t, n))
    return;
  const e = Math.min(t.endCC, n.endCC), i = di(t.fragments, e), s = di(n.fragments, e);
  if (!i || !s)
    return;
  rt.log(`Aligning playlist at start of dicontinuity sequence ${e}`);
  const r = i.start - s.start;
  Za(r, n);
}
function ns(n, t) {
  if (!n.hasProgramDateTime || !t.hasProgramDateTime)
    return;
  const e = n.fragments, i = t.fragments;
  if (!e.length || !i.length)
    return;
  let s, r;
  const a = Math.min(t.endCC, n.endCC);
  t.startCC < a && n.startCC < a && (s = di(i, a), r = di(e, a)), (!s || !r) && (s = i[Math.floor(i.length / 2)], r = di(e, s.cc) || e[Math.floor(e.length / 2)]);
  const o = s.programDateTime, c = r.programDateTime;
  if (!o || !c)
    return;
  const l = (c - o) / 1e3 - (r.start - s.start);
  Za(l, n);
}
function _t(n, t, e) {
  wt(n, t, e), n.addEventListener(t, e);
}
function wt(n, t, e) {
  n.removeEventListener(t, e);
}
const lh = {
  toString: function(n) {
    let t = "";
    const e = n.length;
    for (let i = 0; i < e; i++)
      t += `[${n.start(i).toFixed(3)}-${n.end(i).toFixed(3)}]`;
    return t;
  }
}, w = {
  STOPPED: "STOPPED",
  IDLE: "IDLE",
  KEY_LOADING: "KEY_LOADING",
  FRAG_LOADING: "FRAG_LOADING",
  FRAG_LOADING_WAITING_RETRY: "FRAG_LOADING_WAITING_RETRY",
  WAITING_TRACK: "WAITING_TRACK",
  PARSING: "PARSING",
  PARSED: "PARSED",
  ENDED: "ENDED",
  ERROR: "ERROR",
  WAITING_INIT_PTS: "WAITING_INIT_PTS",
  WAITING_LEVEL: "WAITING_LEVEL"
};
class Rr extends Na {
  constructor(t, e, i, s, r) {
    super(s, t.logger), this.hls = void 0, this.fragPrevious = null, this.fragCurrent = null, this.fragmentTracker = void 0, this.transmuxer = null, this._state = w.STOPPED, this.playlistType = void 0, this.media = null, this.mediaBuffer = null, this.config = void 0, this.bitrateTest = !1, this.lastCurrentTime = 0, this.nextLoadPosition = 0, this.startPosition = 0, this.startTimeOffset = null, this.retryDate = 0, this.levels = null, this.fragmentLoader = void 0, this.keyLoader = void 0, this.levelLastLoaded = null, this.startFragRequested = !1, this.decrypter = void 0, this.initPTS = [], this.buffering = !0, this.loadingParts = !1, this.loopSn = void 0, this.onMediaSeeking = () => {
      const {
        config: a,
        fragCurrent: o,
        media: c,
        mediaBuffer: l,
        state: h
      } = this, d = c ? c.currentTime : 0, u = q.bufferInfo(l || c, d, a.maxBufferHole), f = !u.len;
      if (this.log(`Media seeking to ${B(d) ? d.toFixed(3) : d}, state: ${h}, ${f ? "out of" : "in"} buffer`), this.state === w.ENDED)
        this.resetLoadingState();
      else if (o) {
        const g = a.maxFragLookUpTolerance, v = o.start - g, p = o.start + o.duration + g;
        if (f || p < u.start || v > u.end) {
          const y = d > p;
          (d < v || y) && (y && o.loader && (this.log(`Cancelling fragment load for seek (sn: ${o.sn})`), o.abortRequests(), this.resetLoadingState()), this.fragPrevious = null);
        }
      }
      if (c) {
        this.fragmentTracker.removeFragmentsInRange(d, 1 / 0, this.playlistType, !0);
        const g = this.lastCurrentTime;
        if (d > g && (this.lastCurrentTime = d), !this.loadingParts) {
          const v = Math.max(u.end, d), p = this.shouldLoadParts(this.getLevelDetails(), v);
          p && (this.log(`LL-Part loading ON after seeking to ${d.toFixed(2)} with buffer @${v.toFixed(2)}`), this.loadingParts = p);
        }
      }
      this.hls.hasEnoughToStart || (this.log(`Setting ${f ? "startPosition" : "nextLoadPosition"} to ${d} for seek without enough to start`), this.nextLoadPosition = d, f && (this.startPosition = d)), f && this.state === w.IDLE && this.tickImmediate();
    }, this.onMediaEnded = () => {
      this.log("setting startPosition to 0 because media ended"), this.startPosition = this.lastCurrentTime = 0;
    }, this.playlistType = r, this.hls = t, this.fragmentLoader = new Fc(t.config), this.keyLoader = i, this.fragmentTracker = e, this.config = t.config, this.decrypter = new Ar(t.config);
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.off(m.ERROR, this.onError, this);
  }
  doTick() {
    this.onTickEnd();
  }
  onTickEnd() {
  }
  startLoad(t) {
  }
  stopLoad() {
    if (this.state === w.STOPPED)
      return;
    this.fragmentLoader.abort(), this.keyLoader.abort(this.playlistType);
    const t = this.fragCurrent;
    t != null && t.loader && (t.abortRequests(), this.fragmentTracker.removeFragment(t)), this.resetTransmuxer(), this.fragCurrent = null, this.fragPrevious = null, this.clearInterval(), this.clearNextTick(), this.state = w.STOPPED;
  }
  get startPositionValue() {
    const {
      nextLoadPosition: t,
      startPosition: e
    } = this;
    return e === -1 && t ? t : e;
  }
  get bufferingEnabled() {
    return this.buffering;
  }
  pauseBuffering() {
    this.buffering = !1;
  }
  resumeBuffering() {
    this.buffering = !0;
  }
  get inFlightFrag() {
    return {
      frag: this.fragCurrent,
      state: this.state
    };
  }
  _streamEnded(t, e) {
    if (e.live || !this.media)
      return !1;
    const i = t.end || 0, s = this.config.timelineOffset || 0;
    if (i <= s)
      return !1;
    const r = t.buffered;
    this.config.maxBufferHole && r && r.length > 1 && (t = q.bufferedInfo(r, t.start, 0));
    const a = t.nextStart;
    if (a && a > s && a < e.edge || this.media.currentTime < t.start)
      return !1;
    const c = e.partList;
    if (c != null && c.length) {
      const h = c[c.length - 1];
      return q.isBuffered(this.media, h.start + h.duration / 2);
    }
    const l = e.fragments[e.fragments.length - 1].type;
    return this.fragmentTracker.isEndListAppended(l);
  }
  getLevelDetails() {
    if (this.levels && this.levelLastLoaded !== null)
      return this.levelLastLoaded.details;
  }
  get timelineOffset() {
    const t = this.config.timelineOffset;
    if (t) {
      var e;
      return ((e = this.getLevelDetails()) == null ? void 0 : e.appliedTimelineOffset) || t;
    }
    return 0;
  }
  onMediaAttached(t, e) {
    const i = this.media = this.mediaBuffer = e.media;
    _t(i, "seeking", this.onMediaSeeking), _t(i, "ended", this.onMediaEnded);
    const s = this.config;
    this.levels && s.autoStartLoad && this.state === w.STOPPED && this.startLoad(s.startPosition);
  }
  onMediaDetaching(t, e) {
    const i = !!e.transferMedia, s = this.media;
    if (s !== null) {
      if (s.ended && (this.log("MSE detaching and video ended, reset startPosition"), this.startPosition = this.lastCurrentTime = 0), wt(s, "seeking", this.onMediaSeeking), wt(s, "ended", this.onMediaEnded), this.keyLoader && !i && this.keyLoader.detach(), this.media = this.mediaBuffer = null, this.loopSn = void 0, i) {
        this.resetLoadingState(), this.resetTransmuxer();
        return;
      }
      this.loadingParts = !1, this.fragmentTracker.removeAllFragments(), this.stopLoad();
    }
  }
  onManifestLoading() {
    this.initPTS = [], this.levels = this.levelLastLoaded = this.fragCurrent = null, this.lastCurrentTime = this.startPosition = 0, this.startFragRequested = !1;
  }
  onError(t, e) {
  }
  onManifestLoaded(t, e) {
    this.startTimeOffset = e.startTimeOffset;
  }
  onHandlerDestroying() {
    this.stopLoad(), this.transmuxer && (this.transmuxer.destroy(), this.transmuxer = null), super.onHandlerDestroying(), this.hls = this.onMediaSeeking = this.onMediaEnded = null;
  }
  onHandlerDestroyed() {
    this.state = w.STOPPED, this.fragmentLoader && this.fragmentLoader.destroy(), this.keyLoader && this.keyLoader.destroy(), this.decrypter && this.decrypter.destroy(), this.hls = this.log = this.warn = this.decrypter = this.keyLoader = this.fragmentLoader = this.fragmentTracker = null, super.onHandlerDestroyed();
  }
  loadFragment(t, e, i) {
    this.startFragRequested = !0, this._loadFragForPlayback(t, e, i);
  }
  _loadFragForPlayback(t, e, i) {
    const s = (r) => {
      const a = r.frag;
      if (this.fragContextChanged(a)) {
        this.warn(`${a.type} sn: ${a.sn}${r.part ? " part: " + r.part.index : ""} of ${this.fragInfo(a, !1, r.part)}) was dropped during download.`), this.fragmentTracker.removeFragment(a);
        return;
      }
      a.stats.chunkCount++, this._handleFragmentLoadProgress(r);
    };
    this._doFragLoad(t, e, i, s).then((r) => {
      if (!r)
        return;
      const a = this.state, o = r.frag;
      if (this.fragContextChanged(o)) {
        (a === w.FRAG_LOADING || !this.fragCurrent && a === w.PARSING) && (this.fragmentTracker.removeFragment(o), this.state = w.IDLE);
        return;
      }
      "payload" in r && (this.log(`Loaded ${o.type} sn: ${o.sn} of ${this.playlistLabel()} ${o.level}`), this.hls.trigger(m.FRAG_LOADED, r)), this._handleFragmentLoadComplete(r);
    }).catch((r) => {
      this.state === w.STOPPED || this.state === w.ERROR || (this.warn(`Frag error: ${(r == null ? void 0 : r.message) || r}`), this.resetFragmentLoading(t));
    });
  }
  clearTrackerIfNeeded(t) {
    var e;
    const {
      fragmentTracker: i
    } = this;
    if (i.getState(t) === yt.APPENDING) {
      const r = t.type, a = this.getFwdBufferInfo(this.mediaBuffer, r), o = Math.max(t.duration, a ? a.len : this.config.maxBufferLength), c = this.backtrackFragment;
      ((c ? t.sn - c.sn : 0) === 1 || this.reduceMaxBufferLength(o, t.duration)) && i.removeFragment(t);
    } else ((e = this.mediaBuffer) == null ? void 0 : e.buffered.length) === 0 ? i.removeAllFragments() : i.hasParts(t.type) && (i.detectPartialFragments({
      frag: t,
      part: null,
      stats: t.stats,
      id: t.type
    }), i.getState(t) === yt.PARTIAL && i.removeFragment(t));
  }
  checkLiveUpdate(t) {
    if (t.updated && !t.live) {
      const e = t.fragments[t.fragments.length - 1];
      this.fragmentTracker.detectPartialFragments({
        frag: e,
        part: null,
        stats: e.stats,
        id: e.type
      });
    }
    t.fragments[0] || (t.deltaUpdateFailed = !0);
  }
  waitForLive(t) {
    const e = t.details;
    return (e == null ? void 0 : e.live) && e.type !== "EVENT" && (this.levelLastLoaded !== t || e.expired);
  }
  flushMainBuffer(t, e, i = null) {
    if (!(t - e))
      return;
    const s = {
      startOffset: t,
      endOffset: e,
      type: i
    };
    this.hls.trigger(m.BUFFER_FLUSHING, s);
  }
  _loadInitSegment(t, e) {
    this._doFragLoad(t, e).then((i) => {
      const s = i == null ? void 0 : i.frag;
      if (!s || this.fragContextChanged(s) || !this.levels)
        throw new Error("init load aborted");
      return i;
    }).then((i) => {
      const {
        hls: s
      } = this, {
        frag: r,
        payload: a
      } = i, o = r.decryptdata;
      if (a && a.byteLength > 0 && o != null && o.key && o.iv && Ye(o.method)) {
        const c = self.performance.now();
        return this.decrypter.decrypt(new Uint8Array(a), o.key.buffer, o.iv.buffer, Ir(o.method)).catch((l) => {
          throw s.trigger(m.ERROR, {
            type: Y.MEDIA_ERROR,
            details: L.FRAG_DECRYPT_ERROR,
            fatal: !1,
            error: l,
            reason: l.message,
            frag: r
          }), l;
        }).then((l) => {
          const h = self.performance.now();
          return s.trigger(m.FRAG_DECRYPTED, {
            frag: r,
            payload: l,
            stats: {
              tstart: c,
              tdecrypt: h
            }
          }), i.payload = l, this.completeInitSegmentLoad(i);
        });
      }
      return this.completeInitSegmentLoad(i);
    }).catch((i) => {
      this.state === w.STOPPED || this.state === w.ERROR || (this.warn(i), this.resetFragmentLoading(t));
    });
  }
  completeInitSegmentLoad(t) {
    const {
      levels: e
    } = this;
    if (!e)
      throw new Error("init load aborted, missing levels");
    const i = t.frag.stats;
    this.state !== w.STOPPED && (this.state = w.IDLE), t.frag.data = new Uint8Array(t.payload), i.parsing.start = i.buffering.start = self.performance.now(), i.parsing.end = i.buffering.end = self.performance.now(), this.tick();
  }
  unhandledEncryptionError(t, e) {
    var i, s;
    const r = t.tracks;
    if (r && !e.encrypted && ((i = r.audio) != null && i.encrypted || (s = r.video) != null && s.encrypted) && (!this.config.emeEnabled || !this.keyLoader.emeController)) {
      const a = this.media, o = new Error(`Encrypted track with no key in ${this.fragInfo(e)} (media ${a ? "attached mediaKeys: " + a.mediaKeys : "detached"})`);
      return this.warn(o.message), !a || a.mediaKeys ? !1 : (this.hls.trigger(m.ERROR, {
        type: Y.KEY_SYSTEM_ERROR,
        details: L.KEY_SYSTEM_NO_KEYS,
        fatal: !1,
        error: o,
        frag: e
      }), this.resetTransmuxer(), !0);
    }
    return !1;
  }
  fragContextChanged(t) {
    const {
      fragCurrent: e
    } = this;
    return !t || !e || t.sn !== e.sn || t.level !== e.level;
  }
  fragBufferedComplete(t, e) {
    const i = this.mediaBuffer ? this.mediaBuffer : this.media;
    if (this.log(`Buffered ${t.type} sn: ${t.sn}${e ? " part: " + e.index : ""} of ${this.fragInfo(t, !1, e)} > buffer:${i ? lh.toString(q.getBuffered(i)) : "(detached)"})`), ut(t)) {
      var s;
      if (t.type !== K.SUBTITLE) {
        const a = t.elementaryStreams;
        if (!Object.keys(a).some((o) => !!a[o])) {
          this.state = w.IDLE;
          return;
        }
      }
      const r = (s = this.levels) == null ? void 0 : s[t.level];
      r != null && r.fragmentError && (this.log(`Resetting level fragment error count of ${r.fragmentError} on frag buffered`), r.fragmentError = 0);
    }
    this.state = w.IDLE;
  }
  _handleFragmentLoadComplete(t) {
    const {
      transmuxer: e
    } = this;
    if (!e)
      return;
    const {
      frag: i,
      part: s,
      partsLoaded: r
    } = t, a = !r || r.length === 0 || r.some((c) => !c), o = new br(i.level, i.sn, i.stats.chunkCount + 1, 0, s ? s.index : -1, !a);
    e.flush(o);
  }
  _handleFragmentLoadProgress(t) {
  }
  _doFragLoad(t, e, i = null, s) {
    var r;
    this.fragCurrent = t;
    const a = e.details;
    if (!this.levels || !a)
      throw new Error(`frag load aborted, missing level${a ? "" : " detail"}s`);
    let o = null;
    if (t.encrypted && !((r = t.decryptdata) != null && r.key)) {
      if (this.log(`Loading key for ${t.sn} of [${a.startSN}-${a.endSN}], ${this.playlistLabel()} ${t.level}`), this.state = w.KEY_LOADING, this.fragCurrent = t, o = this.keyLoader.load(t).then((u) => {
        if (!this.fragContextChanged(u.frag))
          return this.hls.trigger(m.KEY_LOADED, u), this.state === w.KEY_LOADING && (this.state = w.IDLE), u;
      }), this.hls.trigger(m.KEY_LOADING, {
        frag: t
      }), this.fragCurrent === null)
        return this.log("context changed in KEY_LOADING"), Promise.resolve(null);
    } else t.encrypted || (o = this.keyLoader.loadClear(t, a.encryptedFragments, this.startFragRequested), o && this.log("[eme] blocking frag load until media-keys acquired"));
    const c = this.fragPrevious;
    if (ut(t) && (!c || t.sn !== c.sn)) {
      const u = this.shouldLoadParts(e.details, t.end);
      u !== this.loadingParts && (this.log(`LL-Part loading ${u ? "ON" : "OFF"} loading sn ${c == null ? void 0 : c.sn}->${t.sn}`), this.loadingParts = u);
    }
    if (i = Math.max(t.start, i || 0), this.loadingParts && ut(t)) {
      const u = a.partList;
      if (u && s) {
        i > a.fragmentEnd && a.fragmentHint && (t = a.fragmentHint);
        const f = this.getNextPart(u, t, i);
        if (f > -1) {
          const g = u[f];
          t = this.fragCurrent = g.fragment, this.log(`Loading ${t.type} sn: ${t.sn} part: ${g.index} (${f}/${u.length - 1}) of ${this.fragInfo(t, !1, g)}) cc: ${t.cc} [${a.startSN}-${a.endSN}], target: ${parseFloat(i.toFixed(3))}`), this.nextLoadPosition = g.start + g.duration, this.state = w.FRAG_LOADING;
          let v;
          return o ? v = o.then((p) => !p || this.fragContextChanged(p.frag) ? null : this.doFragPartsLoad(t, g, e, s)).catch((p) => this.handleFragLoadError(p)) : v = this.doFragPartsLoad(t, g, e, s).catch((p) => this.handleFragLoadError(p)), this.hls.trigger(m.FRAG_LOADING, {
            frag: t,
            part: g,
            targetBufferTime: i
          }), this.fragCurrent === null ? Promise.reject(new Error("frag load aborted, context changed in FRAG_LOADING parts")) : v;
        } else if (!t.url || this.loadedEndOfParts(u, i))
          return Promise.resolve(null);
      }
    }
    if (ut(t) && this.loadingParts) {
      var l;
      this.log(`LL-Part loading OFF after next part miss @${i.toFixed(2)} Check buffer at sn: ${t.sn} loaded parts: ${(l = a.partList) == null ? void 0 : l.filter((u) => u.loaded).map((u) => `[${u.start}-${u.end}]`)}`), this.loadingParts = !1;
    } else if (!t.url)
      return Promise.resolve(null);
    this.log(`Loading ${t.type} sn: ${t.sn} of ${this.fragInfo(t, !1)}) cc: ${t.cc} ${"[" + a.startSN + "-" + a.endSN + "]"}, target: ${parseFloat(i.toFixed(3))}`), B(t.sn) && !this.bitrateTest && (this.nextLoadPosition = t.start + t.duration), this.state = w.FRAG_LOADING;
    const h = this.config.progressive && t.type !== K.SUBTITLE;
    let d;
    return h && o ? d = o.then((u) => !u || this.fragContextChanged(u.frag) ? null : this.fragmentLoader.load(t, s)).catch((u) => this.handleFragLoadError(u)) : d = Promise.all([this.fragmentLoader.load(t, h ? s : void 0), o]).then(([u]) => (!h && s && s(u), u)).catch((u) => this.handleFragLoadError(u)), this.hls.trigger(m.FRAG_LOADING, {
      frag: t,
      targetBufferTime: i
    }), this.fragCurrent === null ? Promise.reject(new Error("frag load aborted, context changed in FRAG_LOADING")) : d;
  }
  doFragPartsLoad(t, e, i, s) {
    return new Promise((r, a) => {
      var o;
      const c = [], l = (o = i.details) == null ? void 0 : o.partList, h = (d) => {
        this.fragmentLoader.loadPart(t, d, s).then((u) => {
          c[d.index] = u;
          const f = u.part;
          this.hls.trigger(m.FRAG_LOADED, u);
          const g = Cn(i.details, t.sn, d.index + 1) || Xa(l, t.sn, d.index + 1);
          if (g)
            h(g);
          else
            return r({
              frag: t,
              part: f,
              partsLoaded: c
            });
        }).catch(a);
      };
      h(e);
    });
  }
  handleFragLoadError(t) {
    if ("data" in t) {
      const e = t.data;
      e.frag && e.details === L.INTERNAL_ABORTED ? this.handleFragLoadAborted(e.frag, e.part) : e.frag && e.type === Y.KEY_SYSTEM_ERROR ? (e.frag.abortRequests(), this.resetStartWhenNotLoaded(), this.resetFragmentLoading(e.frag)) : this.hls.trigger(m.ERROR, e);
    } else
      this.hls.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.INTERNAL_EXCEPTION,
        err: t,
        error: t,
        fatal: !0
      });
    return null;
  }
  _handleTransmuxerFlush(t) {
    const e = this.getCurrentContext(t);
    if (!e || this.state !== w.PARSING) {
      !this.fragCurrent && this.state !== w.STOPPED && this.state !== w.ERROR && (this.state = w.IDLE);
      return;
    }
    const {
      frag: i,
      part: s,
      level: r
    } = e, a = self.performance.now();
    i.stats.parsing.end = a, s && (s.stats.parsing.end = a);
    const o = this.getLevelDetails(), l = o && i.sn > o.endSN || this.shouldLoadParts(o, i.end);
    l !== this.loadingParts && (this.log(`LL-Part loading ${l ? "ON" : "OFF"} after parsing segment ending @${i.end.toFixed(2)}`), this.loadingParts = l), this.updateLevelTiming(i, s, r, t.partial);
  }
  shouldLoadParts(t, e) {
    if (this.config.lowLatencyMode) {
      if (!t)
        return this.loadingParts;
      if (t.partList) {
        var i;
        const r = t.partList[0];
        if (r.fragment.type === K.SUBTITLE)
          return !1;
        const a = r.end + (((i = t.fragmentHint) == null ? void 0 : i.duration) || 0);
        if (e >= a) {
          var s;
          if ((this.hls.hasEnoughToStart ? ((s = this.media) == null ? void 0 : s.currentTime) || this.lastCurrentTime : this.getLoadPosition()) > r.start - r.fragment.duration)
            return !0;
        }
      }
    }
    return !1;
  }
  getCurrentContext(t) {
    const {
      levels: e,
      fragCurrent: i
    } = this, {
      level: s,
      sn: r,
      part: a
    } = t;
    if (!(e != null && e[s]))
      return this.warn(`Levels object was unset while buffering fragment ${r} of ${this.playlistLabel()} ${s}. The current chunk will not be buffered.`), null;
    const o = e[s], c = o.details, l = a > -1 ? Cn(c, r, a) : null, h = l ? l.fragment : qa(c, r, i);
    return h ? (i && i !== h && (h.stats = i.stats), {
      frag: h,
      part: l,
      level: o
    }) : null;
  }
  bufferFragmentData(t, e, i, s, r) {
    if (this.state !== w.PARSING)
      return;
    const {
      data1: a,
      data2: o
    } = t;
    let c = a;
    if (o && (c = Nt(a, o)), !c.length)
      return;
    const l = this.initPTS[e.cc], h = l ? -l.baseTime / l.timescale : void 0, d = {
      type: t.type,
      frag: e,
      part: i,
      chunkMeta: s,
      offset: h,
      parent: e.type,
      data: c
    };
    if (this.hls.trigger(m.BUFFER_APPENDING, d), t.dropped && t.independent && !i) {
      if (r)
        return;
      this.flushBufferGap(e);
    }
  }
  flushBufferGap(t) {
    const e = this.media;
    if (!e)
      return;
    if (!q.isBuffered(e, e.currentTime)) {
      this.flushMainBuffer(0, t.start);
      return;
    }
    const i = e.currentTime, s = q.bufferInfo(e, i, 0), r = t.duration, a = Math.min(this.config.maxFragLookUpTolerance * 2, r * 0.25), o = Math.max(Math.min(t.start - a, s.end - a), i + a);
    t.start - o > a && this.flushMainBuffer(o, t.start);
  }
  getFwdBufferInfo(t, e) {
    var i;
    const s = this.getLoadPosition();
    if (!B(s))
      return null;
    const a = this.lastCurrentTime > s || (i = this.media) != null && i.paused ? 0 : this.config.maxBufferHole;
    return this.getFwdBufferInfoAtPos(t, s, e, a);
  }
  getFwdBufferInfoAtPos(t, e, i, s) {
    const r = q.bufferInfo(t, e, s);
    if (r.len === 0 && r.nextStart !== void 0) {
      const a = this.fragmentTracker.getBufferedFrag(e, i);
      if (a && (r.nextStart <= a.end || a.gap)) {
        const o = Math.max(Math.min(r.nextStart, a.end) - e, s);
        return q.bufferInfo(t, e, o);
      }
    }
    return r;
  }
  getMaxBufferLength(t) {
    const {
      config: e
    } = this;
    let i;
    return t ? i = Math.max(8 * e.maxBufferSize / t, e.maxBufferLength) : i = e.maxBufferLength, Math.min(i, e.maxMaxBufferLength);
  }
  reduceMaxBufferLength(t, e) {
    const i = this.config, s = Math.max(Math.min(t - e, i.maxBufferLength), e), r = Math.max(t - e * 3, i.maxMaxBufferLength / 2, s);
    return r >= s ? (i.maxMaxBufferLength = r, this.warn(`Reduce max buffer length to ${r}s`), !0) : !1;
  }
  getAppendedFrag(t, e = K.MAIN) {
    const i = this.fragmentTracker ? this.fragmentTracker.getAppendedFrag(t, e) : null;
    return i && "fragment" in i ? i.fragment : i;
  }
  getNextFragment(t, e) {
    const i = e.fragments, s = i.length;
    if (!s)
      return null;
    const {
      config: r
    } = this, a = i[0].start, o = r.lowLatencyMode && !!e.partList;
    let c = null;
    if (e.live) {
      const d = r.initialLiveManifestSize;
      if (s < d)
        return this.warn(`Not enough fragments to start playback (have: ${s}, need: ${d})`), null;
      if (!e.PTSKnown && !this.startFragRequested && this.startPosition === -1 || t < a) {
        var l;
        o && !this.loadingParts && (this.log("LL-Part loading ON for initial live fragment"), this.loadingParts = !0), c = this.getInitialLiveFragment(e);
        const u = this.hls.startPosition, f = this.hls.liveSyncPosition, g = c ? (u !== -1 && u >= a ? u : f) || c.start : t;
        this.log(`Setting startPosition to ${g} to match start frag at live edge. mainStart: ${u} liveSyncPosition: ${f} frag.start: ${(l = c) == null ? void 0 : l.start}`), this.startPosition = this.nextLoadPosition = g;
      }
    } else t <= a && (c = i[0]);
    if (!c) {
      const d = this.loadingParts ? e.partEnd : e.fragmentEnd;
      c = this.getFragmentAtPosition(t, d, e);
    }
    let h = this.filterReplacedPrimary(c, e);
    if (!h && c) {
      const d = c.sn - e.startSN;
      h = this.filterReplacedPrimary(i[d + 1] || null, e);
    }
    return this.mapToInitFragWhenRequired(h);
  }
  isLoopLoading(t, e) {
    const i = this.fragmentTracker.getState(t);
    return (i === yt.OK || i === yt.PARTIAL && !!t.gap) && this.nextLoadPosition > e;
  }
  getNextFragmentLoopLoading(t, e, i, s, r) {
    let a = null;
    if (t.gap && (a = this.getNextFragment(this.nextLoadPosition, e), a && !a.gap && i.nextStart)) {
      const o = this.getFwdBufferInfoAtPos(this.mediaBuffer ? this.mediaBuffer : this.media, i.nextStart, s, 0);
      if (o !== null && i.len + o.len >= r) {
        const c = a.sn;
        return this.loopSn !== c && (this.log(`buffer full after gaps in "${s}" playlist starting at sn: ${c}`), this.loopSn = c), null;
      }
    }
    return this.loopSn = void 0, a;
  }
  get primaryPrefetch() {
    if (On(this.config)) {
      var t;
      if ((t = this.hls.interstitialsManager) == null || (t = t.playingItem) == null ? void 0 : t.event)
        return !0;
    }
    return !1;
  }
  filterReplacedPrimary(t, e) {
    if (!t)
      return t;
    if (On(this.config) && t.type !== K.SUBTITLE) {
      const i = this.hls.interstitialsManager, s = i == null ? void 0 : i.bufferingItem;
      if (s) {
        const a = s.event;
        if (a) {
          if (a.appendInPlace || Math.abs(t.start - s.start) > 1 || s.start === 0)
            return null;
        } else if (t.end <= s.start && (e == null ? void 0 : e.live) === !1 || t.start > s.end && s.nextEvent && (s.nextEvent.appendInPlace || t.start - s.end > 1))
          return null;
      }
      const r = i == null ? void 0 : i.playerQueue;
      if (r)
        for (let a = r.length; a--; ) {
          const o = r[a].interstitial;
          if (o.appendInPlace && t.start >= o.startTime && t.end <= o.resumeTime)
            return null;
        }
    }
    return t;
  }
  mapToInitFragWhenRequired(t) {
    return t != null && t.initSegment && !t.initSegment.data && !this.bitrateTest ? t.initSegment : t;
  }
  getNextPart(t, e, i) {
    let s = -1, r = !1, a = !0;
    for (let o = 0, c = t.length; o < c; o++) {
      const l = t[o];
      if (a = a && !l.independent, s > -1 && i < l.start)
        break;
      const h = l.loaded;
      h ? s = -1 : (r || (l.independent || a) && l.fragment === e) && (l.fragment !== e && this.warn(`Need buffer at ${i} but next unloaded part starts at ${l.start}`), s = o), r = h;
    }
    return s;
  }
  loadedEndOfParts(t, e) {
    let i;
    for (let s = t.length; s--; ) {
      if (i = t[s], !i.loaded)
        return !1;
      if (e > i.start)
        return !0;
    }
    return !1;
  }
  /*
   This method is used find the best matching first fragment for a live playlist. This fragment is used to calculate the
   "sliding" of the playlist, which is its offset from the start of playback. After sliding we can compute the real
   start and end times for each fragment in the playlist (after which this method will not need to be called).
  */
  getInitialLiveFragment(t) {
    const e = t.fragments, i = this.fragPrevious;
    let s = null;
    if (i) {
      if (t.hasProgramDateTime && (this.log(`Live playlist, switching playlist, load frag with same PDT: ${i.programDateTime}`), s = bc(e, i.endProgramDateTime, this.config.maxFragLookUpTolerance)), !s) {
        const r = i.sn + 1;
        if (r >= t.startSN && r <= t.endSN) {
          const a = e[r - t.startSN];
          i.cc === a.cc && (s = a, this.log(`Live playlist, switching playlist, load frag with next SN: ${s.sn}`));
        }
        s || (s = Ma(t, i.cc, i.end), s && this.log(`Live playlist, switching playlist, load frag with same CC: ${s.sn}`));
      }
    } else {
      const r = this.hls.liveSyncPosition;
      r !== null && (s = this.getFragmentAtPosition(r, this.bitrateTest ? t.fragmentEnd : t.edge, t));
    }
    return s;
  }
  /*
  This method finds the best matching fragment given the provided position.
   */
  getFragmentAtPosition(t, e, i) {
    const {
      config: s
    } = this;
    let {
      fragPrevious: r
    } = this, {
      fragments: a,
      endSN: o
    } = i;
    const {
      fragmentHint: c
    } = i, {
      maxFragLookUpTolerance: l
    } = s, h = i.partList, d = !!(this.loadingParts && h != null && h.length && c);
    d && !this.bitrateTest && h[h.length - 1].fragment.sn === c.sn && (a = a.concat(c), o = c.sn);
    let u;
    if (t < e) {
      var f;
      const v = t < this.lastCurrentTime || t > e - l || (f = this.media) != null && f.paused || !this.startFragRequested ? 0 : l;
      u = De(r, a, t, v);
    } else
      u = a[a.length - 1];
    if (u) {
      const g = u.sn - i.startSN, v = this.fragmentTracker.getState(u);
      if ((v === yt.OK || v === yt.PARTIAL && u.gap) && (r = u), r && u.sn === r.sn && (!d || h[0].fragment.sn > u.sn || !i.live) && u.level === r.level) {
        const y = a[g + 1];
        u.sn < o && this.fragmentTracker.getState(y) !== yt.OK ? u = y : u = null;
      }
    }
    return u;
  }
  alignPlaylists(t, e, i) {
    const s = t.fragments.length;
    if (!s)
      return this.warn("No fragments in live playlist"), 0;
    const r = t.fragmentStart, a = !e, o = t.alignedSliding && B(r);
    if (a || !o && !r) {
      oh(i, t);
      const c = t.fragmentStart;
      return this.log(`Live playlist sliding: ${c.toFixed(2)} start-sn: ${e ? e.startSN : "na"}->${t.startSN} fragments: ${s}`), c;
    }
    return r;
  }
  waitForCdnTuneIn(t) {
    return t.live && t.canBlockReload && t.partTarget && t.tuneInGoal > Math.max(t.partHoldBack, t.partTarget * 3);
  }
  setStartPosition(t, e) {
    let i = this.startPosition;
    i < e && (i = -1);
    const s = this.timelineOffset;
    if (i === -1) {
      const r = this.startTimeOffset !== null, a = r ? this.startTimeOffset : t.startTimeOffset;
      a !== null && B(a) ? (i = e + a, a < 0 && (i += t.edge), i = Math.min(Math.max(e, i), e + t.totalduration), this.log(`Setting startPosition to ${i} for start time offset ${a} found in ${r ? "multivariant" : "media"} playlist`), this.startPosition = i) : t.live ? (i = this.hls.liveSyncPosition || e, this.log(`Setting startPosition to -1 to start at live edge ${i}`), this.startPosition = -1) : (this.log("setting startPosition to 0 by default"), this.startPosition = i = 0), this.lastCurrentTime = i + s;
    }
    this.nextLoadPosition = i + s;
  }
  getLoadPosition() {
    var t;
    const {
      media: e
    } = this;
    let i = 0;
    return (t = this.hls) != null && t.hasEnoughToStart && e ? i = e.currentTime : this.nextLoadPosition >= 0 && (i = this.nextLoadPosition), i;
  }
  handleFragLoadAborted(t, e) {
    this.transmuxer && t.type === this.playlistType && ut(t) && t.stats.aborted && (this.log(`Fragment ${t.sn}${e ? " part " + e.index : ""} of ${this.playlistLabel()} ${t.level} was aborted`), this.resetFragmentLoading(t));
  }
  resetFragmentLoading(t) {
    (!this.fragCurrent || !this.fragContextChanged(t) && this.state !== w.FRAG_LOADING_WAITING_RETRY) && (this.state = w.IDLE);
  }
  onFragmentOrKeyLoadError(t, e) {
    var i;
    if (e.chunkMeta && !e.frag) {
      const y = this.getCurrentContext(e.chunkMeta);
      y && (e.frag = y.frag);
    }
    const s = e.frag;
    if (!s || s.type !== t || !this.levels)
      return;
    if (this.fragContextChanged(s)) {
      var r;
      this.warn(`Frag load error must match current frag to retry ${s.url} > ${(r = this.fragCurrent) == null ? void 0 : r.url}`);
      return;
    }
    const a = e.details === L.FRAG_GAP;
    a && this.fragmentTracker.fragBuffered(s, !0);
    const o = e.errorAction;
    if (!o) {
      this.state = w.ERROR;
      return;
    }
    const {
      action: c,
      flags: l,
      retryCount: h = 0,
      retryConfig: d
    } = o, u = !!d, f = u && c === xt.RetryRequest, g = u && !o.resolved && l === kt.MoveAllAlternatesMatchingHost, v = (i = this.hls.latestLevelDetails) == null ? void 0 : i.live;
    if (!f && g && ut(s) && !s.endList && v && !$a(e))
      this.resetFragmentErrors(t), this.treatAsGap(s), o.resolved = !0;
    else if ((f || g) && h < d.maxNumRetry) {
      var p;
      const y = Js((p = e.response) == null ? void 0 : p.code), E = xr(d, h);
      if (this.resetStartWhenNotLoaded(), this.retryDate = self.performance.now() + E, this.state = w.FRAG_LOADING_WAITING_RETRY, o.resolved = !0, y) {
        this.log("Waiting for connection (offline)"), this.retryDate = 1 / 0, e.reason = "offline";
        return;
      }
      this.warn(`Fragment ${s.sn} of ${t} ${s.level} errored with ${e.details}, retrying loading ${h + 1}/${d.maxNumRetry} in ${E}ms`);
    } else if (d)
      if (this.resetFragmentErrors(t), h < d.maxNumRetry)
        !a && c !== xt.RemoveAlternatePermanently && (o.resolved = !0);
      else {
        this.warn(`${e.details} reached or exceeded max retry (${h})`);
        return;
      }
    else c === xt.SendAlternateToPenaltyBox ? this.state = w.WAITING_LEVEL : this.state = w.ERROR;
    this.tickImmediate();
  }
  checkRetryDate() {
    const t = self.performance.now(), e = this.retryDate, i = e === 1 / 0;
    (!e || t >= e || i && !Js(0)) && (i && this.log("Connection restored (online)"), this.resetStartWhenNotLoaded(), this.state = w.IDLE);
  }
  reduceLengthAndFlushBuffer(t) {
    if (this.state === w.PARSING || this.state === w.PARSED) {
      const e = t.frag, i = t.parent, s = this.getFwdBufferInfo(this.mediaBuffer, i), r = s && s.len > 0.5;
      r && this.reduceMaxBufferLength(s.len, (e == null ? void 0 : e.duration) || 10);
      const a = !r;
      return a && this.warn(`Buffer full error while media.currentTime (${this.getLoadPosition()}) is not buffered, flush ${i} buffer`), e && (this.fragmentTracker.removeFragment(e), this.nextLoadPosition = e.start), this.resetLoadingState(), a;
    }
    return !1;
  }
  resetFragmentErrors(t) {
    t === K.AUDIO && (this.fragCurrent = null), this.hls.hasEnoughToStart || (this.startFragRequested = !1), this.state !== w.STOPPED && (this.state = w.IDLE);
  }
  afterBufferFlushed(t, e, i) {
    if (!t)
      return;
    const s = q.getBuffered(t);
    this.fragmentTracker.detectEvictedFragments(e, s, i), this.state === w.ENDED && this.resetLoadingState();
  }
  resetLoadingState() {
    this.log("Reset loading state"), this.fragCurrent = null, this.fragPrevious = null, this.state !== w.STOPPED && (this.state = w.IDLE);
  }
  resetStartWhenNotLoaded() {
    if (!this.hls.hasEnoughToStart) {
      this.startFragRequested = !1;
      const t = this.levelLastLoaded, e = t ? t.details : null;
      e != null && e.live ? (this.log("resetting startPosition for live start"), this.startPosition = -1, this.setStartPosition(e, e.fragmentStart), this.resetLoadingState()) : this.nextLoadPosition = this.startPosition;
    }
  }
  resetWhenMissingContext(t) {
    this.log(`Loading context changed while buffering sn ${t.sn} of ${this.playlistLabel()} ${t.level === -1 ? "<removed>" : t.level}. This chunk will not be buffered.`), this.removeUnbufferedFrags(), this.resetStartWhenNotLoaded(), this.resetLoadingState();
  }
  removeUnbufferedFrags(t = 0) {
    this.fragmentTracker.removeFragmentsInRange(t, 1 / 0, this.playlistType, !1, !0);
  }
  updateLevelTiming(t, e, i, s) {
    const r = i.details;
    if (!r) {
      this.warn("level.details undefined");
      return;
    }
    if (!Object.keys(t.elementaryStreams).reduce((c, l) => {
      const h = t.elementaryStreams[l];
      if (h) {
        const d = h.endPTS - h.startPTS;
        if (d <= 0)
          return this.warn(`Could not parse fragment ${t.sn} ${l} duration reliably (${d})`), c || !1;
        const u = s ? 0 : Ya(r, t, h.startPTS, h.endPTS, h.startDTS, h.endDTS, this);
        return this.hls.trigger(m.LEVEL_PTS_UPDATED, {
          details: r,
          level: i,
          drift: u,
          type: l,
          frag: t,
          start: h.startPTS,
          end: h.endPTS
        }), !0;
      }
      return c;
    }, !1)) {
      var o;
      const c = ((o = this.transmuxer) == null ? void 0 : o.error) === null;
      if ((i.fragmentError === 0 || c && (i.fragmentError < 2 || t.endList)) && this.treatAsGap(t, i), c) {
        const l = new Error(`Found no media in fragment ${t.sn} of ${this.playlistLabel()} ${t.level} resetting transmuxer to fallback to playlist timing`);
        if (this.warn(l.message), this.hls.trigger(m.ERROR, {
          type: Y.MEDIA_ERROR,
          details: L.FRAG_PARSING_ERROR,
          fatal: !1,
          error: l,
          frag: t,
          reason: `Found no media in msn ${t.sn} of ${this.playlistLabel()} "${i.url}"`
        }), !this.hls)
          return;
        this.resetTransmuxer();
      }
    }
    this.state = w.PARSED, this.log(`Parsed ${t.type} sn: ${t.sn}${e ? " part: " + e.index : ""} of ${this.fragInfo(t, !1, e)})`), this.hls.trigger(m.FRAG_PARSED, {
      frag: t,
      part: e
    });
  }
  playlistLabel() {
    return this.playlistType === K.MAIN ? "level" : "track";
  }
  fragInfo(t, e = !0, i) {
    var s, r;
    return `${this.playlistLabel()} ${t.level} (${i ? "part" : "frag"}:[${((s = e && !i ? t.startPTS : (i || t).start) != null ? s : NaN).toFixed(3)}-${((r = e && !i ? t.endPTS : (i || t).end) != null ? r : NaN).toFixed(3)}]${i && t.type === "main" ? "INDEPENDENT=" + (i.independent ? "YES" : "NO") : ""}`;
  }
  treatAsGap(t, e) {
    e && e.fragmentError++, t.gap = !0, this.fragmentTracker.removeFragment(t), this.fragmentTracker.fragBuffered(t, !0);
  }
  resetTransmuxer() {
    var t;
    (t = this.transmuxer) == null || t.reset();
  }
  recoverWorkerError(t) {
    t.event === "demuxerWorker" && (this.fragmentTracker.removeAllFragments(), this.transmuxer && (this.transmuxer.destroy(), this.transmuxer = null), this.resetStartWhenNotLoaded(), this.resetLoadingState());
  }
  set state(t) {
    const e = this._state;
    e !== t && (this._state = t, this.log(`${e}->${t}`));
  }
  get state() {
    return this._state;
  }
}
function On(n) {
  return !!n.interstitialsController && n.enableInterstitialPlayback !== !1;
}
class to {
  constructor() {
    this.chunks = [], this.dataLength = 0;
  }
  push(t) {
    this.chunks.push(t), this.dataLength += t.length;
  }
  flush() {
    const {
      chunks: t,
      dataLength: e
    } = this;
    let i;
    if (t.length)
      t.length === 1 ? i = t[0] : i = ch(t, e);
    else return new Uint8Array(0);
    return this.reset(), i;
  }
  reset() {
    this.chunks.length = 0, this.dataLength = 0;
  }
}
function ch(n, t) {
  const e = new Uint8Array(t);
  let i = 0;
  for (let s = 0; s < n.length; s++) {
    const r = n[s];
    e.set(r, i), i += r.length;
  }
  return e;
}
var Rs = { exports: {} }, Mn;
function hh() {
  return Mn || (Mn = 1, (function(n) {
    var t = Object.prototype.hasOwnProperty, e = "~";
    function i() {
    }
    Object.create && (i.prototype = /* @__PURE__ */ Object.create(null), new i().__proto__ || (e = !1));
    function s(c, l, h) {
      this.fn = c, this.context = l, this.once = h || !1;
    }
    function r(c, l, h, d, u) {
      if (typeof h != "function")
        throw new TypeError("The listener must be a function");
      var f = new s(h, d || c, u), g = e ? e + l : l;
      return c._events[g] ? c._events[g].fn ? c._events[g] = [c._events[g], f] : c._events[g].push(f) : (c._events[g] = f, c._eventsCount++), c;
    }
    function a(c, l) {
      --c._eventsCount === 0 ? c._events = new i() : delete c._events[l];
    }
    function o() {
      this._events = new i(), this._eventsCount = 0;
    }
    o.prototype.eventNames = function() {
      var l = [], h, d;
      if (this._eventsCount === 0) return l;
      for (d in h = this._events)
        t.call(h, d) && l.push(e ? d.slice(1) : d);
      return Object.getOwnPropertySymbols ? l.concat(Object.getOwnPropertySymbols(h)) : l;
    }, o.prototype.listeners = function(l) {
      var h = e ? e + l : l, d = this._events[h];
      if (!d) return [];
      if (d.fn) return [d.fn];
      for (var u = 0, f = d.length, g = new Array(f); u < f; u++)
        g[u] = d[u].fn;
      return g;
    }, o.prototype.listenerCount = function(l) {
      var h = e ? e + l : l, d = this._events[h];
      return d ? d.fn ? 1 : d.length : 0;
    }, o.prototype.emit = function(l, h, d, u, f, g) {
      var v = e ? e + l : l;
      if (!this._events[v]) return !1;
      var p = this._events[v], y = arguments.length, E, T;
      if (p.fn) {
        switch (p.once && this.removeListener(l, p.fn, void 0, !0), y) {
          case 1:
            return p.fn.call(p.context), !0;
          case 2:
            return p.fn.call(p.context, h), !0;
          case 3:
            return p.fn.call(p.context, h, d), !0;
          case 4:
            return p.fn.call(p.context, h, d, u), !0;
          case 5:
            return p.fn.call(p.context, h, d, u, f), !0;
          case 6:
            return p.fn.call(p.context, h, d, u, f, g), !0;
        }
        for (T = 1, E = new Array(y - 1); T < y; T++)
          E[T - 1] = arguments[T];
        p.fn.apply(p.context, E);
      } else {
        var S = p.length, x;
        for (T = 0; T < S; T++)
          switch (p[T].once && this.removeListener(l, p[T].fn, void 0, !0), y) {
            case 1:
              p[T].fn.call(p[T].context);
              break;
            case 2:
              p[T].fn.call(p[T].context, h);
              break;
            case 3:
              p[T].fn.call(p[T].context, h, d);
              break;
            case 4:
              p[T].fn.call(p[T].context, h, d, u);
              break;
            default:
              if (!E) for (x = 1, E = new Array(y - 1); x < y; x++)
                E[x - 1] = arguments[x];
              p[T].fn.apply(p[T].context, E);
          }
      }
      return !0;
    }, o.prototype.on = function(l, h, d) {
      return r(this, l, h, d, !1);
    }, o.prototype.once = function(l, h, d) {
      return r(this, l, h, d, !0);
    }, o.prototype.removeListener = function(l, h, d, u) {
      var f = e ? e + l : l;
      if (!this._events[f]) return this;
      if (!h)
        return a(this, f), this;
      var g = this._events[f];
      if (g.fn)
        g.fn === h && (!u || g.once) && (!d || g.context === d) && a(this, f);
      else {
        for (var v = 0, p = [], y = g.length; v < y; v++)
          (g[v].fn !== h || u && !g[v].once || d && g[v].context !== d) && p.push(g[v]);
        p.length ? this._events[f] = p.length === 1 ? p[0] : p : a(this, f);
      }
      return this;
    }, o.prototype.removeAllListeners = function(l) {
      var h;
      return l ? (h = e ? e + l : l, this._events[h] && a(this, h)) : (this._events = new i(), this._eventsCount = 0), this;
    }, o.prototype.off = o.prototype.removeListener, o.prototype.addListener = o.prototype.on, o.prefixed = e, o.EventEmitter = o, n.exports = o;
  })(Rs)), Rs.exports;
}
var dh = hh(), _r = /* @__PURE__ */ Fl(dh);
const vi = "1.6.15", Qe = {};
function uh() {
  return typeof __HLS_WORKER_BUNDLE__ == "function";
}
function fh() {
  const n = Qe[vi];
  if (n)
    return n.clientCount++, n;
  const t = new self.Blob([`var exports={};var module={exports:exports};function define(f){f()};define.amd=true;(${__HLS_WORKER_BUNDLE__.toString()})(true);`], {
    type: "text/javascript"
  }), e = self.URL.createObjectURL(t), s = {
    worker: new self.Worker(e),
    objectURL: e,
    clientCount: 1
  };
  return Qe[vi] = s, s;
}
function gh(n) {
  const t = Qe[n];
  if (t)
    return t.clientCount++, t;
  const e = new self.URL(n, self.location.href).href, s = {
    worker: new self.Worker(e),
    scriptURL: e,
    clientCount: 1
  };
  return Qe[n] = s, s;
}
function mh(n) {
  const t = Qe[n || vi];
  if (t && t.clientCount-- === 1) {
    const {
      worker: i,
      objectURL: s
    } = t;
    delete Qe[n || vi], s && self.URL.revokeObjectURL(s), i.terminate();
  }
}
function eo(n, t) {
  return t + 10 <= n.length && n[t] === 51 && n[t + 1] === 68 && n[t + 2] === 73 && n[t + 3] < 255 && n[t + 4] < 255 && n[t + 6] < 128 && n[t + 7] < 128 && n[t + 8] < 128 && n[t + 9] < 128;
}
function Dr(n, t) {
  return t + 10 <= n.length && n[t] === 73 && n[t + 1] === 68 && n[t + 2] === 51 && n[t + 3] < 255 && n[t + 4] < 255 && n[t + 6] < 128 && n[t + 7] < 128 && n[t + 8] < 128 && n[t + 9] < 128;
}
function fs(n, t) {
  let e = 0;
  return e = (n[t] & 127) << 21, e |= (n[t + 1] & 127) << 14, e |= (n[t + 2] & 127) << 7, e |= n[t + 3] & 127, e;
}
function yi(n, t) {
  const e = t;
  let i = 0;
  for (; Dr(n, t); ) {
    i += 10;
    const s = fs(n, t + 6);
    i += s, eo(n, t + 10) && (i += 10), t += i;
  }
  if (i > 0)
    return n.subarray(e, e + i);
}
function ph(n, t, e, i) {
  const s = [96e3, 88200, 64e3, 48e3, 44100, 32e3, 24e3, 22050, 16e3, 12e3, 11025, 8e3, 7350], r = t[e + 2], a = r >> 2 & 15;
  if (a > 12) {
    const f = new Error(`invalid ADTS sampling index:${a}`);
    n.emit(m.ERROR, m.ERROR, {
      type: Y.MEDIA_ERROR,
      details: L.FRAG_PARSING_ERROR,
      fatal: !0,
      error: f,
      reason: f.message
    });
    return;
  }
  const o = (r >> 6 & 3) + 1, c = t[e + 3] >> 6 & 3 | (r & 1) << 2, l = "mp4a.40." + o, h = s[a];
  let d = a;
  (o === 5 || o === 29) && (d -= 3);
  const u = [o << 3 | (d & 14) >> 1, (d & 1) << 7 | c << 3];
  return rt.log(`manifest codec:${i}, parsed codec:${l}, channels:${c}, rate:${h} (ADTS object type:${o} sampling index:${a})`), {
    config: u,
    samplerate: h,
    channelCount: c,
    codec: l,
    parsedCodec: l,
    manifestCodec: i
  };
}
function io(n, t) {
  return n[t] === 255 && (n[t + 1] & 246) === 240;
}
function so(n, t) {
  return n[t + 1] & 1 ? 7 : 9;
}
function wr(n, t) {
  return (n[t + 3] & 3) << 11 | n[t + 4] << 3 | (n[t + 5] & 224) >>> 5;
}
function vh(n, t) {
  return t + 5 < n.length;
}
function as(n, t) {
  return t + 1 < n.length && io(n, t);
}
function yh(n, t) {
  return vh(n, t) && io(n, t) && wr(n, t) <= n.length - t;
}
function Eh(n, t) {
  if (as(n, t)) {
    const e = so(n, t);
    if (t + e >= n.length)
      return !1;
    const i = wr(n, t);
    if (i <= e)
      return !1;
    const s = t + i;
    return s === n.length || as(n, s);
  }
  return !1;
}
function ro(n, t, e, i, s) {
  if (!n.samplerate) {
    const r = ph(t, e, i, s);
    if (!r)
      return;
    nt(n, r);
  }
}
function no(n) {
  return 1024 * 9e4 / n;
}
function Th(n, t) {
  const e = so(n, t);
  if (t + e <= n.length) {
    const i = wr(n, t) - e;
    if (i > 0)
      return {
        headerLength: e,
        frameLength: i
      };
  }
}
function ao(n, t, e, i, s) {
  const r = no(n.samplerate), a = i + s * r, o = Th(t, e);
  let c;
  if (o) {
    const {
      frameLength: d,
      headerLength: u
    } = o, f = u + d, g = Math.max(0, e + f - t.length);
    g ? (c = new Uint8Array(f - u), c.set(t.subarray(e + u, t.length), 0)) : c = t.subarray(e + u, e + f);
    const v = {
      unit: c,
      pts: a
    };
    return g || n.samples.push(v), {
      sample: v,
      length: f,
      missing: g
    };
  }
  const l = t.length - e;
  return c = new Uint8Array(l), c.set(t.subarray(e, t.length), 0), {
    sample: {
      unit: c,
      pts: a
    },
    length: l,
    missing: -1
  };
}
function Sh(n, t) {
  return Dr(n, t) && fs(n, t + 6) + 10 <= n.length - t;
}
function xh(n) {
  return n instanceof ArrayBuffer ? n : n.byteOffset == 0 && n.byteLength == n.buffer.byteLength ? n.buffer : new Uint8Array(n).buffer;
}
function _s(n, t = 0, e = 1 / 0) {
  return Ah(n, t, e, Uint8Array);
}
function Ah(n, t, e, i) {
  const s = bh(n);
  let r = 1;
  "BYTES_PER_ELEMENT" in i && (r = i.BYTES_PER_ELEMENT);
  const a = Ih(n) ? n.byteOffset : 0, o = (a + n.byteLength) / r, c = (a + t) / r, l = Math.floor(Math.max(0, Math.min(c, o))), h = Math.floor(Math.min(l + Math.max(e, 0), o));
  return new i(s, l, h - l);
}
function bh(n) {
  return n instanceof ArrayBuffer ? n : n.buffer;
}
function Ih(n) {
  return n && n.buffer instanceof ArrayBuffer && n.byteLength !== void 0 && n.byteOffset !== void 0;
}
function Lh(n) {
  const t = {
    key: n.type,
    description: "",
    data: "",
    mimeType: null,
    pictureType: null
  }, e = 3;
  if (n.size < 2)
    return;
  if (n.data[0] !== e) {
    console.log("Ignore frame with unrecognized character encoding");
    return;
  }
  const i = n.data.subarray(1).indexOf(0);
  if (i === -1)
    return;
  const s = Ft(_s(n.data, 1, i)), r = n.data[2 + i], a = n.data.subarray(3 + i).indexOf(0);
  if (a === -1)
    return;
  const o = Ft(_s(n.data, 3 + i, a));
  let c;
  return s === "-->" ? c = Ft(_s(n.data, 4 + i + a)) : c = xh(n.data.subarray(4 + i + a)), t.mimeType = s, t.pictureType = r, t.description = o, t.data = c, t;
}
function Rh(n) {
  if (n.size < 2)
    return;
  const t = Ft(n.data, !0), e = new Uint8Array(n.data.subarray(t.length + 1));
  return {
    key: n.type,
    info: t,
    data: e.buffer
  };
}
function _h(n) {
  if (n.size < 2)
    return;
  if (n.type === "TXXX") {
    let e = 1;
    const i = Ft(n.data.subarray(e), !0);
    e += i.length + 1;
    const s = Ft(n.data.subarray(e));
    return {
      key: n.type,
      info: i,
      data: s
    };
  }
  const t = Ft(n.data.subarray(1));
  return {
    key: n.type,
    info: "",
    data: t
  };
}
function Dh(n) {
  if (n.type === "WXXX") {
    if (n.size < 2)
      return;
    let e = 1;
    const i = Ft(n.data.subarray(e), !0);
    e += i.length + 1;
    const s = Ft(n.data.subarray(e));
    return {
      key: n.type,
      info: i,
      data: s
    };
  }
  const t = Ft(n.data);
  return {
    key: n.type,
    info: "",
    data: t
  };
}
function wh(n) {
  return n.type === "PRIV" ? Rh(n) : n.type[0] === "W" ? Dh(n) : n.type === "APIC" ? Lh(n) : _h(n);
}
function Ch(n) {
  const t = String.fromCharCode(n[0], n[1], n[2], n[3]), e = fs(n, 4), i = 10;
  return {
    type: t,
    size: e,
    data: n.subarray(i, i + e)
  };
}
const wi = 10, Ph = 10;
function oo(n) {
  let t = 0;
  const e = [];
  for (; Dr(n, t); ) {
    const i = fs(n, t + 6);
    n[t + 5] >> 6 & 1 && (t += wi), t += wi;
    const s = t + i;
    for (; t + Ph < s; ) {
      const r = Ch(n.subarray(t)), a = wh(r);
      a && e.push(a), t += r.size + wi;
    }
    eo(n, t) && (t += wi);
  }
  return e;
}
function lo(n) {
  return n && n.key === "PRIV" && n.info === "com.apple.streaming.transportStreamTimestamp";
}
function kh(n) {
  if (n.data.byteLength === 8) {
    const t = new Uint8Array(n.data), e = t[3] & 1;
    let i = (t[4] << 23) + (t[5] << 15) + (t[6] << 7) + t[7];
    return i /= 45, e && (i += 4772185884e-2), Math.round(i);
  }
}
function Cr(n) {
  const t = oo(n);
  for (let e = 0; e < t.length; e++) {
    const i = t[e];
    if (lo(i))
      return kh(i);
  }
}
let Mt = /* @__PURE__ */ (function(n) {
  return n.audioId3 = "org.id3", n.dateRange = "com.apple.quicktime.HLS", n.emsg = "https://aomedia.org/emsg/ID3", n.misbklv = "urn:misb:KLV:bin:1910.1", n;
})({});
function qt(n = "", t = 9e4) {
  return {
    type: n,
    id: -1,
    pid: -1,
    inputTimeScale: t,
    sequenceNumber: -1,
    samples: [],
    dropped: 0
  };
}
class Pr {
  constructor() {
    this._audioTrack = void 0, this._id3Track = void 0, this.frameIndex = 0, this.cachedData = null, this.basePTS = null, this.initPTS = null, this.lastPTS = null;
  }
  resetInitSegment(t, e, i, s) {
    this._id3Track = {
      type: "id3",
      id: 3,
      pid: -1,
      inputTimeScale: 9e4,
      sequenceNumber: 0,
      samples: [],
      dropped: 0
    };
  }
  resetTimeStamp(t) {
    this.initPTS = t, this.resetContiguity();
  }
  resetContiguity() {
    this.basePTS = null, this.lastPTS = null, this.frameIndex = 0;
  }
  canParse(t, e) {
    return !1;
  }
  appendFrame(t, e, i) {
  }
  // feed incoming data to the front of the parsing pipeline
  demux(t, e) {
    this.cachedData && (t = Nt(this.cachedData, t), this.cachedData = null);
    let i = yi(t, 0), s = i ? i.length : 0, r;
    const a = this._audioTrack, o = this._id3Track, c = i ? Cr(i) : void 0, l = t.length;
    for ((this.basePTS === null || this.frameIndex === 0 && B(c)) && (this.basePTS = Oh(c, e, this.initPTS), this.lastPTS = this.basePTS), this.lastPTS === null && (this.lastPTS = this.basePTS), i && i.length > 0 && o.samples.push({
      pts: this.lastPTS,
      dts: this.lastPTS,
      data: i,
      type: Mt.audioId3,
      duration: Number.POSITIVE_INFINITY
    }); s < l; ) {
      if (this.canParse(t, s)) {
        const h = this.appendFrame(a, t, s);
        h ? (this.frameIndex++, this.lastPTS = h.sample.pts, s += h.length, r = s) : s = l;
      } else Sh(t, s) ? (i = yi(t, s), o.samples.push({
        pts: this.lastPTS,
        dts: this.lastPTS,
        data: i,
        type: Mt.audioId3,
        duration: Number.POSITIVE_INFINITY
      }), s += i.length, r = s) : s++;
      if (s === l && r !== l) {
        const h = t.slice(r);
        this.cachedData ? this.cachedData = Nt(this.cachedData, h) : this.cachedData = h;
      }
    }
    return {
      audioTrack: a,
      videoTrack: qt(),
      id3Track: o,
      textTrack: qt()
    };
  }
  demuxSampleAes(t, e, i) {
    return Promise.reject(new Error(`[${this}] This demuxer does not support Sample-AES decryption`));
  }
  flush(t) {
    const e = this.cachedData;
    return e && (this.cachedData = null, this.demux(e, 0)), {
      audioTrack: this._audioTrack,
      videoTrack: qt(),
      id3Track: this._id3Track,
      textTrack: qt()
    };
  }
  destroy() {
    this.cachedData = null, this._audioTrack = this._id3Track = void 0;
  }
}
const Oh = (n, t, e) => {
  if (B(n))
    return n * 90;
  const i = e ? e.baseTime * 9e4 / e.timescale : 0;
  return t * 9e4 + i;
};
let Ci = null;
const Mh = [32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160], Fh = [44100, 48e3, 32e3, 22050, 24e3, 16e3, 11025, 12e3, 8e3], $h = [
  // MPEG 2.5
  [
    0,
    // Reserved
    72,
    // Layer3
    144,
    // Layer2
    12
    // Layer1
  ],
  // Reserved
  [
    0,
    // Reserved
    0,
    // Layer3
    0,
    // Layer2
    0
    // Layer1
  ],
  // MPEG 2
  [
    0,
    // Reserved
    72,
    // Layer3
    144,
    // Layer2
    12
    // Layer1
  ],
  // MPEG 1
  [
    0,
    // Reserved
    144,
    // Layer3
    144,
    // Layer2
    12
    // Layer1
  ]
], Nh = [
  0,
  // Reserved
  1,
  // Layer3
  1,
  // Layer2
  4
  // Layer1
];
function co(n, t, e, i, s) {
  if (e + 24 > t.length)
    return;
  const r = ho(t, e);
  if (r && e + r.frameLength <= t.length) {
    const a = r.samplesPerFrame * 9e4 / r.sampleRate, o = i + s * a, c = {
      unit: t.subarray(e, e + r.frameLength),
      pts: o,
      dts: o
    };
    return n.config = [], n.channelCount = r.channelCount, n.samplerate = r.sampleRate, n.samples.push(c), {
      sample: c,
      length: r.frameLength,
      missing: 0
    };
  }
}
function ho(n, t) {
  const e = n[t + 1] >> 3 & 3, i = n[t + 1] >> 1 & 3, s = n[t + 2] >> 4 & 15, r = n[t + 2] >> 2 & 3;
  if (e !== 1 && s !== 0 && s !== 15 && r !== 3) {
    const a = n[t + 2] >> 1 & 1, o = n[t + 3] >> 6, c = e === 3 ? 3 - i : i === 3 ? 3 : 4, l = Mh[c * 14 + s - 1] * 1e3, d = Fh[(e === 3 ? 0 : e === 2 ? 1 : 2) * 3 + r], u = o === 3 ? 1 : 2, f = $h[e][i], g = Nh[i], v = f * 8 * g, p = Math.floor(f * l / d + a) * g;
    if (Ci === null) {
      const T = (navigator.userAgent || "").match(/Chrome\/(\d+)/i);
      Ci = T ? parseInt(T[1]) : 0;
    }
    return !!Ci && Ci <= 87 && i === 2 && l >= 224e3 && o === 0 && (n[t + 3] = n[t + 3] | 128), {
      sampleRate: d,
      channelCount: u,
      frameLength: p,
      samplesPerFrame: v
    };
  }
}
function kr(n, t) {
  return n[t] === 255 && (n[t + 1] & 224) === 224 && (n[t + 1] & 6) !== 0;
}
function uo(n, t) {
  return t + 1 < n.length && kr(n, t);
}
function Bh(n, t) {
  return kr(n, t) && 4 <= n.length - t;
}
function fo(n, t) {
  if (t + 1 < n.length && kr(n, t)) {
    const i = ho(n, t);
    let s = 4;
    i != null && i.frameLength && (s = i.frameLength);
    const r = t + s;
    return r === n.length || uo(n, r);
  }
  return !1;
}
class Uh extends Pr {
  constructor(t, e) {
    super(), this.observer = void 0, this.config = void 0, this.observer = t, this.config = e;
  }
  resetInitSegment(t, e, i, s) {
    super.resetInitSegment(t, e, i, s), this._audioTrack = {
      container: "audio/adts",
      type: "audio",
      id: 2,
      pid: -1,
      sequenceNumber: 0,
      segmentCodec: "aac",
      samples: [],
      manifestCodec: e,
      duration: s,
      inputTimeScale: 9e4,
      dropped: 0
    };
  }
  // Source for probe info - https://wiki.multimedia.cx/index.php?title=ADTS
  static probe(t, e) {
    if (!t)
      return !1;
    const i = yi(t, 0);
    let s = (i == null ? void 0 : i.length) || 0;
    if (fo(t, s))
      return !1;
    for (let r = t.length; s < r; s++)
      if (Eh(t, s))
        return e.log("ADTS sync word found !"), !0;
    return !1;
  }
  canParse(t, e) {
    return yh(t, e);
  }
  appendFrame(t, e, i) {
    ro(t, this.observer, e, i, t.manifestCodec);
    const s = ao(t, e, i, this.basePTS, this.frameIndex);
    if (s && s.missing === 0)
      return s;
  }
}
const go = (n, t) => {
  let e = 0, i = 5;
  t += i;
  const s = new Uint32Array(1), r = new Uint32Array(1), a = new Uint8Array(1);
  for (; i > 0; ) {
    a[0] = n[t];
    const o = Math.min(i, 8), c = 8 - o;
    r[0] = 4278190080 >>> 24 + c << c, s[0] = (a[0] & r[0]) >> c, e = e ? e << o | s[0] : s[0], t += 1, i -= o;
  }
  return e;
};
class Gh extends Pr {
  constructor(t) {
    super(), this.observer = void 0, this.observer = t;
  }
  resetInitSegment(t, e, i, s) {
    super.resetInitSegment(t, e, i, s), this._audioTrack = {
      container: "audio/ac-3",
      type: "audio",
      id: 2,
      pid: -1,
      sequenceNumber: 0,
      segmentCodec: "ac3",
      samples: [],
      manifestCodec: e,
      duration: s,
      inputTimeScale: 9e4,
      dropped: 0
    };
  }
  canParse(t, e) {
    return e + 64 < t.length;
  }
  appendFrame(t, e, i) {
    const s = mo(t, e, i, this.basePTS, this.frameIndex);
    if (s !== -1)
      return {
        sample: t.samples[t.samples.length - 1],
        length: s,
        missing: 0
      };
  }
  static probe(t) {
    if (!t)
      return !1;
    const e = yi(t, 0);
    if (!e)
      return !1;
    const i = e.length;
    return t[i] === 11 && t[i + 1] === 119 && Cr(e) !== void 0 && // check the bsid to confirm ac-3
    go(t, i) < 16;
  }
}
function mo(n, t, e, i, s) {
  if (e + 8 > t.length || t[e] !== 11 || t[e + 1] !== 119)
    return -1;
  const r = t[e + 4] >> 6;
  if (r >= 3)
    return -1;
  const o = [48e3, 44100, 32e3][r], c = t[e + 4] & 63, h = [64, 69, 96, 64, 70, 96, 80, 87, 120, 80, 88, 120, 96, 104, 144, 96, 105, 144, 112, 121, 168, 112, 122, 168, 128, 139, 192, 128, 140, 192, 160, 174, 240, 160, 175, 240, 192, 208, 288, 192, 209, 288, 224, 243, 336, 224, 244, 336, 256, 278, 384, 256, 279, 384, 320, 348, 480, 320, 349, 480, 384, 417, 576, 384, 418, 576, 448, 487, 672, 448, 488, 672, 512, 557, 768, 512, 558, 768, 640, 696, 960, 640, 697, 960, 768, 835, 1152, 768, 836, 1152, 896, 975, 1344, 896, 976, 1344, 1024, 1114, 1536, 1024, 1115, 1536, 1152, 1253, 1728, 1152, 1254, 1728, 1280, 1393, 1920, 1280, 1394, 1920][c * 3 + r] * 2;
  if (e + h > t.length)
    return -1;
  const d = t[e + 6] >> 5;
  let u = 0;
  d === 2 ? u += 2 : (d & 1 && d !== 1 && (u += 2), d & 4 && (u += 2));
  const f = (t[e + 6] << 8 | t[e + 7]) >> 12 - u & 1, v = [2, 1, 2, 3, 3, 4, 4, 5][d] + f, p = t[e + 5] >> 3, y = t[e + 5] & 7, E = new Uint8Array([r << 6 | p << 1 | y >> 2, (y & 3) << 6 | d << 3 | f << 2 | c >> 4, c << 4 & 224]), T = 1536 / o * 9e4, S = i + s * T, x = t.subarray(e, e + h);
  return n.config = E, n.channelCount = v, n.samplerate = o, n.samples.push({
    unit: x,
    pts: S
  }), h;
}
class Kh extends Pr {
  resetInitSegment(t, e, i, s) {
    super.resetInitSegment(t, e, i, s), this._audioTrack = {
      container: "audio/mpeg",
      type: "audio",
      id: 2,
      pid: -1,
      sequenceNumber: 0,
      segmentCodec: "mp3",
      samples: [],
      manifestCodec: e,
      duration: s,
      inputTimeScale: 9e4,
      dropped: 0
    };
  }
  static probe(t) {
    if (!t)
      return !1;
    const e = yi(t, 0);
    let i = (e == null ? void 0 : e.length) || 0;
    if (e && t[i] === 11 && t[i + 1] === 119 && Cr(e) !== void 0 && // check the bsid to confirm ac-3 or ec-3 (not mp3)
    go(t, i) <= 16)
      return !1;
    for (let s = t.length; i < s; i++)
      if (fo(t, i))
        return rt.log("MPEG Audio sync word found !"), !0;
    return !1;
  }
  canParse(t, e) {
    return Bh(t, e);
  }
  appendFrame(t, e, i) {
    if (this.basePTS !== null)
      return co(t, e, i, this.basePTS, this.frameIndex);
  }
}
const Hh = /\/emsg[-/]ID3/i;
class Vh {
  constructor(t, e) {
    this.remainderData = null, this.timeOffset = 0, this.config = void 0, this.videoTrack = void 0, this.audioTrack = void 0, this.id3Track = void 0, this.txtTrack = void 0, this.config = e;
  }
  resetTimeStamp() {
  }
  resetInitSegment(t, e, i, s) {
    const r = this.videoTrack = qt("video", 1), a = this.audioTrack = qt("audio", 1), o = this.txtTrack = qt("text", 1);
    if (this.id3Track = qt("id3", 1), this.timeOffset = 0, !(t != null && t.byteLength))
      return;
    const c = ba(t);
    if (c.video) {
      const {
        id: l,
        timescale: h,
        codec: d,
        supplemental: u
      } = c.video;
      r.id = l, r.timescale = o.timescale = h, r.codec = d, r.supplemental = u;
    }
    if (c.audio) {
      const {
        id: l,
        timescale: h,
        codec: d
      } = c.audio;
      a.id = l, a.timescale = h, a.codec = d;
    }
    o.id = Sa.text, r.sampleDuration = 0, r.duration = a.duration = s;
  }
  resetContiguity() {
    this.remainderData = null;
  }
  static probe(t) {
    return Gl(t);
  }
  demux(t, e) {
    this.timeOffset = e;
    let i = t;
    const s = this.videoTrack, r = this.txtTrack;
    if (this.config.progressive) {
      this.remainderData && (i = Nt(this.remainderData, t));
      const o = jl(i);
      this.remainderData = o.remainder, s.samples = o.valid || new Uint8Array();
    } else
      s.samples = i;
    const a = this.extractID3Track(s, e);
    return r.samples = Zr(e, s), {
      videoTrack: s,
      audioTrack: this.audioTrack,
      id3Track: a,
      textTrack: this.txtTrack
    };
  }
  flush() {
    const t = this.timeOffset, e = this.videoTrack, i = this.txtTrack;
    e.samples = this.remainderData || new Uint8Array(), this.remainderData = null;
    const s = this.extractID3Track(e, this.timeOffset);
    return i.samples = Zr(t, e), {
      videoTrack: e,
      audioTrack: qt(),
      id3Track: s,
      textTrack: qt()
    };
  }
  extractID3Track(t, e) {
    const i = this.id3Track;
    if (t.samples.length) {
      const s = Z(t.samples, ["emsg"]);
      s && s.forEach((r) => {
        const a = Xl(r);
        if (Hh.test(a.schemeIdUri)) {
          const o = Fn(a, e);
          let c = a.eventDuration === 4294967295 ? Number.POSITIVE_INFINITY : a.eventDuration / a.timeScale;
          c <= 1e-3 && (c = Number.POSITIVE_INFINITY);
          const l = a.payload;
          i.samples.push({
            data: l,
            len: l.byteLength,
            dts: o,
            pts: o,
            type: Mt.emsg,
            duration: c
          });
        } else if (this.config.enableEmsgKLVMetadata && a.schemeIdUri.startsWith("urn:misb:KLV:bin:1910.1")) {
          const o = Fn(a, e);
          i.samples.push({
            data: a.payload,
            len: a.payload.byteLength,
            dts: o,
            pts: o,
            type: Mt.misbklv,
            duration: Number.POSITIVE_INFINITY
          });
        }
      });
    }
    return i;
  }
  demuxSampleAes(t, e, i) {
    return Promise.reject(new Error("The MP4 demuxer does not support SAMPLE-AES decryption"));
  }
  destroy() {
    this.config = null, this.remainderData = null, this.videoTrack = this.audioTrack = this.id3Track = this.txtTrack = void 0;
  }
}
function Fn(n, t) {
  return B(n.presentationTime) ? n.presentationTime / n.timeScale : t + n.presentationTimeDelta / n.timeScale;
}
class Wh {
  constructor(t, e, i) {
    this.keyData = void 0, this.decrypter = void 0, this.keyData = i, this.decrypter = new Ar(e, {
      removePKCS7Padding: !1
    });
  }
  decryptBuffer(t) {
    return this.decrypter.decrypt(t, this.keyData.key.buffer, this.keyData.iv.buffer, me.cbc);
  }
  // AAC - encrypt all full 16 bytes blocks starting from offset 16
  decryptAacSample(t, e, i) {
    const s = t[e].unit;
    if (s.length <= 16)
      return;
    const r = s.subarray(16, s.length - s.length % 16), a = r.buffer.slice(r.byteOffset, r.byteOffset + r.length);
    this.decryptBuffer(a).then((o) => {
      const c = new Uint8Array(o);
      s.set(c, 16), this.decrypter.isSync() || this.decryptAacSamples(t, e + 1, i);
    }).catch(i);
  }
  decryptAacSamples(t, e, i) {
    for (; ; e++) {
      if (e >= t.length) {
        i();
        return;
      }
      if (!(t[e].unit.length < 32) && (this.decryptAacSample(t, e, i), !this.decrypter.isSync()))
        return;
    }
  }
  // AVC - encrypt one 16 bytes block out of ten, starting from offset 32
  getAvcEncryptedData(t) {
    const e = Math.floor((t.length - 48) / 160) * 16 + 16, i = new Int8Array(e);
    let s = 0;
    for (let r = 32; r < t.length - 16; r += 160, s += 16)
      i.set(t.subarray(r, r + 16), s);
    return i;
  }
  getAvcDecryptedUnit(t, e) {
    const i = new Uint8Array(e);
    let s = 0;
    for (let r = 32; r < t.length - 16; r += 160, s += 16)
      t.set(i.subarray(s, s + 16), r);
    return t;
  }
  decryptAvcSample(t, e, i, s, r) {
    const a = Ra(r.data), o = this.getAvcEncryptedData(a);
    this.decryptBuffer(o.buffer).then((c) => {
      r.data = this.getAvcDecryptedUnit(a, c), this.decrypter.isSync() || this.decryptAvcSamples(t, e, i + 1, s);
    }).catch(s);
  }
  decryptAvcSamples(t, e, i, s) {
    if (t instanceof Uint8Array)
      throw new Error("Cannot decrypt samples of type Uint8Array");
    for (; ; e++, i = 0) {
      if (e >= t.length) {
        s();
        return;
      }
      const r = t[e].units;
      for (; !(i >= r.length); i++) {
        const a = r[i];
        if (!(a.data.length <= 48 || a.type !== 1 && a.type !== 5) && (this.decryptAvcSample(t, e, i, s, a), !this.decrypter.isSync()))
          return;
      }
    }
  }
}
class po {
  constructor() {
    this.VideoSample = null;
  }
  createVideoSample(t, e, i) {
    return {
      key: t,
      frame: !1,
      pts: e,
      dts: i,
      units: [],
      length: 0
    };
  }
  getLastNalUnit(t) {
    var e;
    let i = this.VideoSample, s;
    if ((!i || i.units.length === 0) && (i = t[t.length - 1]), (e = i) != null && e.units) {
      const r = i.units;
      s = r[r.length - 1];
    }
    return s;
  }
  pushAccessUnit(t, e) {
    if (t.units.length && t.frame) {
      if (t.pts === void 0) {
        const i = e.samples, s = i.length;
        if (s) {
          const r = i[s - 1];
          t.pts = r.pts, t.dts = r.dts;
        } else {
          e.dropped++;
          return;
        }
      }
      e.samples.push(t);
    }
  }
  parseNALu(t, e, i) {
    const s = e.byteLength;
    let r = t.naluState || 0;
    const a = r, o = [];
    let c = 0, l, h, d, u = -1, f = 0;
    for (r === -1 && (u = 0, f = this.getNALuType(e, 0), r = 0, c = 1); c < s; ) {
      if (l = e[c++], !r) {
        r = l ? 0 : 1;
        continue;
      }
      if (r === 1) {
        r = l ? 0 : 2;
        continue;
      }
      if (!l)
        r = 3;
      else if (l === 1) {
        if (h = c - r - 1, u >= 0) {
          const g = {
            data: e.subarray(u, h),
            type: f
          };
          o.push(g);
        } else {
          const g = this.getLastNalUnit(t.samples);
          g && (a && c <= 4 - a && g.state && (g.data = g.data.subarray(0, g.data.byteLength - a)), h > 0 && (g.data = Nt(g.data, e.subarray(0, h)), g.state = 0));
        }
        c < s ? (d = this.getNALuType(e, c), u = c, f = d, r = 0) : r = -1;
      } else
        r = 0;
    }
    if (u >= 0 && r >= 0) {
      const g = {
        data: e.subarray(u, s),
        type: f,
        state: r
      };
      o.push(g);
    }
    if (o.length === 0) {
      const g = this.getLastNalUnit(t.samples);
      g && (g.data = Nt(g.data, e));
    }
    return t.naluState = r, o;
  }
}
class ui {
  constructor(t) {
    this.data = void 0, this.bytesAvailable = void 0, this.word = void 0, this.bitsAvailable = void 0, this.data = t, this.bytesAvailable = t.byteLength, this.word = 0, this.bitsAvailable = 0;
  }
  // ():void
  loadWord() {
    const t = this.data, e = this.bytesAvailable, i = t.byteLength - e, s = new Uint8Array(4), r = Math.min(4, e);
    if (r === 0)
      throw new Error("no bytes available");
    s.set(t.subarray(i, i + r)), this.word = new DataView(s.buffer).getUint32(0), this.bitsAvailable = r * 8, this.bytesAvailable -= r;
  }
  // (count:int):void
  skipBits(t) {
    let e;
    t = Math.min(t, this.bytesAvailable * 8 + this.bitsAvailable), this.bitsAvailable > t ? (this.word <<= t, this.bitsAvailable -= t) : (t -= this.bitsAvailable, e = t >> 3, t -= e << 3, this.bytesAvailable -= e, this.loadWord(), this.word <<= t, this.bitsAvailable -= t);
  }
  // (size:int):uint
  readBits(t) {
    let e = Math.min(this.bitsAvailable, t);
    const i = this.word >>> 32 - e;
    if (t > 32 && rt.error("Cannot read more than 32 bits at a time"), this.bitsAvailable -= e, this.bitsAvailable > 0)
      this.word <<= e;
    else if (this.bytesAvailable > 0)
      this.loadWord();
    else
      throw new Error("no bits available");
    return e = t - e, e > 0 && this.bitsAvailable ? i << e | this.readBits(e) : i;
  }
  // ():uint
  skipLZ() {
    let t;
    for (t = 0; t < this.bitsAvailable; ++t)
      if ((this.word & 2147483648 >>> t) !== 0)
        return this.word <<= t, this.bitsAvailable -= t, t;
    return this.loadWord(), t + this.skipLZ();
  }
  // ():void
  skipUEG() {
    this.skipBits(1 + this.skipLZ());
  }
  // ():void
  skipEG() {
    this.skipBits(1 + this.skipLZ());
  }
  // ():uint
  readUEG() {
    const t = this.skipLZ();
    return this.readBits(t + 1) - 1;
  }
  // ():int
  readEG() {
    const t = this.readUEG();
    return 1 & t ? 1 + t >>> 1 : -1 * (t >>> 1);
  }
  // Some convenience functions
  // :Boolean
  readBoolean() {
    return this.readBits(1) === 1;
  }
  // ():int
  readUByte() {
    return this.readBits(8);
  }
  // ():int
  readUShort() {
    return this.readBits(16);
  }
  // ():int
  readUInt() {
    return this.readBits(32);
  }
}
class Yh extends po {
  parsePES(t, e, i, s) {
    const r = this.parseNALu(t, i.data, s);
    let a = this.VideoSample, o, c = !1;
    i.data = null, a && r.length && !t.audFound && (this.pushAccessUnit(a, t), a = this.VideoSample = this.createVideoSample(!1, i.pts, i.dts)), r.forEach((l) => {
      var h, d;
      switch (l.type) {
        // NDR
        case 1: {
          let v = !1;
          o = !0;
          const p = l.data;
          if (c && p.length > 4) {
            const y = this.readSliceType(p);
            (y === 2 || y === 4 || y === 7 || y === 9) && (v = !0);
          }
          if (v) {
            var u;
            (u = a) != null && u.frame && !a.key && (this.pushAccessUnit(a, t), a = this.VideoSample = null);
          }
          a || (a = this.VideoSample = this.createVideoSample(!0, i.pts, i.dts)), a.frame = !0, a.key = v;
          break;
        }
        case 5:
          o = !0, (h = a) != null && h.frame && !a.key && (this.pushAccessUnit(a, t), a = this.VideoSample = null), a || (a = this.VideoSample = this.createVideoSample(!0, i.pts, i.dts)), a.key = !0, a.frame = !0;
          break;
        // SEI
        case 6: {
          o = !0, Er(l.data, 1, i.pts, e.samples);
          break;
        }
        case 7: {
          var f, g;
          o = !0, c = !0;
          const v = l.data, p = this.readSPS(v);
          if (!t.sps || t.width !== p.width || t.height !== p.height || ((f = t.pixelRatio) == null ? void 0 : f[0]) !== p.pixelRatio[0] || ((g = t.pixelRatio) == null ? void 0 : g[1]) !== p.pixelRatio[1]) {
            t.width = p.width, t.height = p.height, t.pixelRatio = p.pixelRatio, t.sps = [v];
            const y = v.subarray(1, 4);
            let E = "avc1.";
            for (let T = 0; T < 3; T++) {
              let S = y[T].toString(16);
              S.length < 2 && (S = "0" + S), E += S;
            }
            t.codec = E;
          }
          break;
        }
        // PPS
        case 8:
          o = !0, t.pps = [l.data];
          break;
        // AUD
        case 9:
          o = !0, t.audFound = !0, (d = a) != null && d.frame && (this.pushAccessUnit(a, t), a = null), a || (a = this.VideoSample = this.createVideoSample(!1, i.pts, i.dts));
          break;
        // Filler Data
        case 12:
          o = !0;
          break;
        default:
          o = !1;
          break;
      }
      a && o && a.units.push(l);
    }), s && a && (this.pushAccessUnit(a, t), this.VideoSample = null);
  }
  getNALuType(t, e) {
    return t[e] & 31;
  }
  readSliceType(t) {
    const e = new ui(t);
    return e.readUByte(), e.readUEG(), e.readUEG();
  }
  /**
   * The scaling list is optionally transmitted as part of a sequence parameter
   * set and is not relevant to transmuxing.
   * @param count the number of entries in this scaling list
   * @see Recommendation ITU-T H.264, Section 7.3.2.1.1.1
   */
  skipScalingList(t, e) {
    let i = 8, s = 8, r;
    for (let a = 0; a < t; a++)
      s !== 0 && (r = e.readEG(), s = (i + r + 256) % 256), i = s === 0 ? i : s;
  }
  /**
   * Read a sequence parameter set and return some interesting video
   * properties. A sequence parameter set is the H264 metadata that
   * describes the properties of upcoming video frames.
   * @returns an object with configuration parsed from the
   * sequence parameter set, including the dimensions of the
   * associated video frames.
   */
  readSPS(t) {
    const e = new ui(t);
    let i = 0, s = 0, r = 0, a = 0, o, c, l;
    const h = e.readUByte.bind(e), d = e.readBits.bind(e), u = e.readUEG.bind(e), f = e.readBoolean.bind(e), g = e.skipBits.bind(e), v = e.skipEG.bind(e), p = e.skipUEG.bind(e), y = this.skipScalingList.bind(this);
    h();
    const E = h();
    if (d(5), g(3), h(), p(), E === 100 || E === 110 || E === 122 || E === 244 || E === 44 || E === 83 || E === 86 || E === 118 || E === 128) {
      const _ = u();
      if (_ === 3 && g(1), p(), p(), g(1), f())
        for (c = _ !== 3 ? 8 : 12, l = 0; l < c; l++)
          f() && (l < 6 ? y(16, e) : y(64, e));
    }
    p();
    const T = u();
    if (T === 0)
      u();
    else if (T === 1)
      for (g(1), v(), v(), o = u(), l = 0; l < o; l++)
        v();
    p(), g(1);
    const S = u(), x = u(), D = d(1);
    D === 0 && g(1), g(1), f() && (i = u(), s = u(), r = u(), a = u());
    let A = [1, 1];
    if (f() && f())
      switch (h()) {
        case 1:
          A = [1, 1];
          break;
        case 2:
          A = [12, 11];
          break;
        case 3:
          A = [10, 11];
          break;
        case 4:
          A = [16, 11];
          break;
        case 5:
          A = [40, 33];
          break;
        case 6:
          A = [24, 11];
          break;
        case 7:
          A = [20, 11];
          break;
        case 8:
          A = [32, 11];
          break;
        case 9:
          A = [80, 33];
          break;
        case 10:
          A = [18, 11];
          break;
        case 11:
          A = [15, 11];
          break;
        case 12:
          A = [64, 33];
          break;
        case 13:
          A = [160, 99];
          break;
        case 14:
          A = [4, 3];
          break;
        case 15:
          A = [3, 2];
          break;
        case 16:
          A = [2, 1];
          break;
        case 255: {
          A = [h() << 8 | h(), h() << 8 | h()];
          break;
        }
      }
    return {
      width: Math.ceil((S + 1) * 16 - i * 2 - s * 2),
      height: (2 - D) * (x + 1) * 16 - (D ? 2 : 4) * (r + a),
      pixelRatio: A
    };
  }
}
class zh extends po {
  constructor(...t) {
    super(...t), this.initVPS = null;
  }
  parsePES(t, e, i, s) {
    const r = this.parseNALu(t, i.data, s);
    let a = this.VideoSample, o, c = !1;
    i.data = null, a && r.length && !t.audFound && (this.pushAccessUnit(a, t), a = this.VideoSample = this.createVideoSample(!1, i.pts, i.dts)), r.forEach((l) => {
      var h, d;
      switch (l.type) {
        // NON-IDR, NON RANDOM ACCESS SLICE
        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
        case 9:
          a || (a = this.VideoSample = this.createVideoSample(!1, i.pts, i.dts)), a.frame = !0, o = !0;
          break;
        // CRA, BLA (random access picture)
        case 16:
        case 17:
        case 18:
        case 21:
          if (o = !0, c) {
            var u;
            (u = a) != null && u.frame && !a.key && (this.pushAccessUnit(a, t), a = this.VideoSample = null);
          }
          a || (a = this.VideoSample = this.createVideoSample(!0, i.pts, i.dts)), a.key = !0, a.frame = !0;
          break;
        // IDR
        case 19:
        case 20:
          o = !0, (h = a) != null && h.frame && !a.key && (this.pushAccessUnit(a, t), a = this.VideoSample = null), a || (a = this.VideoSample = this.createVideoSample(!0, i.pts, i.dts)), a.key = !0, a.frame = !0;
          break;
        // SEI
        case 39:
          o = !0, Er(
            l.data,
            2,
            // NALu header size
            i.pts,
            e.samples
          );
          break;
        // VPS
        case 32:
          o = !0, t.vps || (typeof t.params != "object" && (t.params = {}), t.params = nt(t.params, this.readVPS(l.data)), this.initVPS = l.data), t.vps = [l.data];
          break;
        // SPS
        case 33:
          if (o = !0, c = !0, t.vps !== void 0 && t.vps[0] !== this.initVPS && t.sps !== void 0 && !this.matchSPS(t.sps[0], l.data) && (this.initVPS = t.vps[0], t.sps = t.pps = void 0), !t.sps) {
            const f = this.readSPS(l.data);
            t.width = f.width, t.height = f.height, t.pixelRatio = f.pixelRatio, t.codec = f.codecString, t.sps = [], typeof t.params != "object" && (t.params = {});
            for (const g in f.params)
              t.params[g] = f.params[g];
          }
          this.pushParameterSet(t.sps, l.data, t.vps), a || (a = this.VideoSample = this.createVideoSample(!0, i.pts, i.dts)), a.key = !0;
          break;
        // PPS
        case 34:
          if (o = !0, typeof t.params == "object") {
            if (!t.pps) {
              t.pps = [];
              const f = this.readPPS(l.data);
              for (const g in f)
                t.params[g] = f[g];
            }
            this.pushParameterSet(t.pps, l.data, t.vps);
          }
          break;
        // ACCESS UNIT DELIMITER
        case 35:
          o = !0, t.audFound = !0, (d = a) != null && d.frame && (this.pushAccessUnit(a, t), a = null), a || (a = this.VideoSample = this.createVideoSample(!1, i.pts, i.dts));
          break;
        default:
          o = !1;
          break;
      }
      a && o && a.units.push(l);
    }), s && a && (this.pushAccessUnit(a, t), this.VideoSample = null);
  }
  pushParameterSet(t, e, i) {
    (i && i[0] === this.initVPS || !i && !t.length) && t.push(e);
  }
  getNALuType(t, e) {
    return (t[e] & 126) >>> 1;
  }
  ebsp2rbsp(t) {
    const e = new Uint8Array(t.byteLength);
    let i = 0;
    for (let s = 0; s < t.byteLength; s++)
      s >= 2 && t[s] === 3 && t[s - 1] === 0 && t[s - 2] === 0 || (e[i] = t[s], i++);
    return new Uint8Array(e.buffer, 0, i);
  }
  pushAccessUnit(t, e) {
    super.pushAccessUnit(t, e), this.initVPS && (this.initVPS = null);
  }
  readVPS(t) {
    const e = new ui(t);
    e.readUByte(), e.readUByte(), e.readBits(4), e.skipBits(2), e.readBits(6);
    const i = e.readBits(3), s = e.readBoolean();
    return {
      numTemporalLayers: i + 1,
      temporalIdNested: s
    };
  }
  readSPS(t) {
    const e = new ui(this.ebsp2rbsp(t));
    e.readUByte(), e.readUByte(), e.readBits(4);
    const i = e.readBits(3);
    e.readBoolean();
    const s = e.readBits(2), r = e.readBoolean(), a = e.readBits(5), o = e.readUByte(), c = e.readUByte(), l = e.readUByte(), h = e.readUByte(), d = e.readUByte(), u = e.readUByte(), f = e.readUByte(), g = e.readUByte(), v = e.readUByte(), p = e.readUByte(), y = e.readUByte(), E = [], T = [];
    for (let it = 0; it < i; it++)
      E.push(e.readBoolean()), T.push(e.readBoolean());
    if (i > 0)
      for (let it = i; it < 8; it++)
        e.readBits(2);
    for (let it = 0; it < i; it++)
      E[it] && (e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte(), e.readUByte()), T[it] && e.readUByte();
    e.readUEG();
    const S = e.readUEG();
    S == 3 && e.skipBits(1);
    const x = e.readUEG(), D = e.readUEG(), A = e.readBoolean();
    let _ = 0, R = 0, b = 0, C = 0;
    A && (_ += e.readUEG(), R += e.readUEG(), b += e.readUEG(), C += e.readUEG());
    const F = e.readUEG(), U = e.readUEG(), W = e.readUEG(), G = e.readBoolean();
    for (let it = G ? 0 : i; it <= i; it++)
      e.skipUEG(), e.skipUEG(), e.skipUEG();
    if (e.skipUEG(), e.skipUEG(), e.skipUEG(), e.skipUEG(), e.skipUEG(), e.skipUEG(), e.readBoolean() && e.readBoolean())
      for (let It = 0; It < 4; It++)
        for (let $t = 0; $t < (It === 3 ? 2 : 6); $t++)
          if (!e.readBoolean())
            e.readUEG();
          else {
            const Gt = Math.min(64, 1 << 4 + (It << 1));
            It > 1 && e.readEG();
            for (let $e = 0; $e < Gt; $e++)
              e.readEG();
          }
    e.readBoolean(), e.readBoolean(), e.readBoolean() && (e.readUByte(), e.skipUEG(), e.skipUEG(), e.readBoolean());
    const $ = e.readUEG();
    let V = 0;
    for (let it = 0; it < $; it++) {
      let It = !1;
      if (it !== 0 && (It = e.readBoolean()), It) {
        it === $ && e.readUEG(), e.readBoolean(), e.readUEG();
        let $t = 0;
        for (let Se = 0; Se <= V; Se++) {
          const Gt = e.readBoolean();
          let $e = !1;
          Gt || ($e = e.readBoolean()), (Gt || $e) && $t++;
        }
        V = $t;
      } else {
        const $t = e.readUEG(), Se = e.readUEG();
        V = $t + Se;
        for (let Gt = 0; Gt < $t; Gt++)
          e.readUEG(), e.readBoolean();
        for (let Gt = 0; Gt < Se; Gt++)
          e.readUEG(), e.readBoolean();
      }
    }
    if (e.readBoolean()) {
      const it = e.readUEG();
      for (let It = 0; It < it; It++) {
        for (let $t = 0; $t < W + 4; $t++)
          e.readBits(1);
        e.readBits(1);
      }
    }
    let O = 0, M = 1, X = 1, et = !0, Q = 1, J = 0;
    e.readBoolean(), e.readBoolean();
    let pt = !1;
    if (e.readBoolean()) {
      if (e.readBoolean()) {
        const xe = e.readUByte(), Kr = [1, 12, 10, 16, 40, 24, 20, 32, 80, 18, 15, 64, 160, 4, 3, 2], Ii = [1, 11, 11, 11, 33, 11, 11, 11, 33, 11, 11, 33, 99, 3, 2, 1];
        xe > 0 && xe < 16 ? (M = Kr[xe - 1], X = Ii[xe - 1]) : xe === 255 && (M = e.readBits(16), X = e.readBits(16));
      }
      if (e.readBoolean() && e.readBoolean(), e.readBoolean() && (e.readBits(3), e.readBoolean(), e.readBoolean() && (e.readUByte(), e.readUByte(), e.readUByte())), e.readBoolean() && (e.readUEG(), e.readUEG()), e.readBoolean(), e.readBoolean(), e.readBoolean(), pt = e.readBoolean(), pt && (e.skipUEG(), e.skipUEG(), e.skipUEG(), e.skipUEG()), e.readBoolean() && (Q = e.readBits(32), J = e.readBits(32), e.readBoolean() && e.readUEG(), e.readBoolean())) {
        const Ii = e.readBoolean(), Hr = e.readBoolean();
        let oi = !1;
        (Ii || Hr) && (oi = e.readBoolean(), oi && (e.readUByte(), e.readBits(5), e.readBoolean(), e.readBits(5)), e.readBits(4), e.readBits(4), oi && e.readBits(4), e.readBits(5), e.readBits(5), e.readBits(5));
        for (let Vr = 0; Vr <= i; Vr++) {
          et = e.readBoolean();
          const el = et || e.readBoolean();
          let Wr = !1;
          el ? e.readEG() : Wr = e.readBoolean();
          const Yr = Wr ? 1 : e.readUEG() + 1;
          if (Ii)
            for (let li = 0; li < Yr; li++)
              e.readUEG(), e.readUEG(), oi && (e.readUEG(), e.readUEG()), e.skipBits(1);
          if (Hr)
            for (let li = 0; li < Yr; li++)
              e.readUEG(), e.readUEG(), oi && (e.readUEG(), e.readUEG()), e.skipBits(1);
        }
      }
      e.readBoolean() && (e.readBoolean(), e.readBoolean(), e.readBoolean(), O = e.readUEG());
    }
    let Rt = x, Wt = D;
    if (A) {
      let it = 1, It = 1;
      S === 1 ? it = It = 2 : S == 2 && (it = 2), Rt = x - it * R - it * _, Wt = D - It * C - It * b;
    }
    const Te = s ? ["A", "B", "C"][s] : "", tl = o << 24 | c << 16 | l << 8 | h;
    let ys = 0;
    for (let it = 0; it < 32; it++)
      ys = (ys | (tl >> it & 1) << 31 - it) >>> 0;
    let Es = ys.toString(16);
    return a === 1 && Es === "2" && (Es = "6"), {
      codecString: `hvc1.${Te}${a}.${Es}.${r ? "H" : "L"}${y}.B0`,
      params: {
        general_tier_flag: r,
        general_profile_idc: a,
        general_profile_space: s,
        general_profile_compatibility_flags: [o, c, l, h],
        general_constraint_indicator_flags: [d, u, f, g, v, p],
        general_level_idc: y,
        bit_depth: F + 8,
        bit_depth_luma_minus8: F,
        bit_depth_chroma_minus8: U,
        min_spatial_segmentation_idc: O,
        chroma_format_idc: S,
        frame_rate: {
          fixed: et,
          fps: J / Q
        }
      },
      width: Rt,
      height: Wt,
      pixelRatio: [M, X]
    };
  }
  readPPS(t) {
    const e = new ui(this.ebsp2rbsp(t));
    e.readUByte(), e.readUByte(), e.skipUEG(), e.skipUEG(), e.skipBits(2), e.skipBits(3), e.skipBits(2), e.skipUEG(), e.skipUEG(), e.skipEG(), e.skipBits(2), e.readBoolean() && e.skipUEG(), e.skipEG(), e.skipEG(), e.skipBits(4);
    const s = e.readBoolean(), r = e.readBoolean();
    let a = 1;
    return r && s ? a = 0 : r ? a = 3 : s && (a = 2), {
      parallelismType: a
    };
  }
  matchSPS(t, e) {
    return String.fromCharCode.apply(null, t).substr(3) === String.fromCharCode.apply(null, e).substr(3);
  }
}
const Et = 188;
class he {
  constructor(t, e, i, s) {
    this.logger = void 0, this.observer = void 0, this.config = void 0, this.typeSupported = void 0, this.sampleAes = null, this.pmtParsed = !1, this.audioCodec = void 0, this.videoCodec = void 0, this._pmtId = -1, this._videoTrack = void 0, this._audioTrack = void 0, this._id3Track = void 0, this._txtTrack = void 0, this.aacOverFlow = null, this.remainderData = null, this.videoParser = void 0, this.observer = t, this.config = e, this.typeSupported = i, this.logger = s, this.videoParser = null;
  }
  static probe(t, e) {
    const i = he.syncOffset(t);
    return i > 0 && e.warn(`MPEG2-TS detected but first sync word found @ offset ${i}`), i !== -1;
  }
  static syncOffset(t) {
    const e = t.length;
    let i = Math.min(Et * 5, e - Et) + 1, s = 0;
    for (; s < i; ) {
      let r = !1, a = -1, o = 0;
      for (let c = s; c < e; c += Et)
        if (t[c] === 71 && (e - c === Et || t[c + Et] === 71)) {
          if (o++, a === -1 && (a = c, a !== 0 && (i = Math.min(a + Et * 99, t.length - Et) + 1)), r || (r = rr(t, c) === 0), r && o > 1 && (a === 0 && o > 2 || c + Et > i))
            return a;
        } else {
          if (o)
            return -1;
          break;
        }
      s++;
    }
    return -1;
  }
  /**
   * Creates a track model internal to demuxer used to drive remuxing input
   */
  static createTrack(t, e) {
    return {
      container: t === "video" || t === "audio" ? "video/mp2t" : void 0,
      type: t,
      id: Sa[t],
      pid: -1,
      inputTimeScale: 9e4,
      sequenceNumber: 0,
      samples: [],
      dropped: 0,
      duration: t === "audio" ? e : void 0
    };
  }
  /**
   * Initializes a new init segment on the demuxer/remuxer interface. Needed for discontinuities/track-switches (or at stream start)
   * Resets all internal track instances of the demuxer.
   */
  resetInitSegment(t, e, i, s) {
    this.pmtParsed = !1, this._pmtId = -1, this._videoTrack = he.createTrack("video"), this._videoTrack.duration = s, this._audioTrack = he.createTrack("audio", s), this._id3Track = he.createTrack("id3"), this._txtTrack = he.createTrack("text"), this._audioTrack.segmentCodec = "aac", this.videoParser = null, this.aacOverFlow = null, this.remainderData = null, this.audioCodec = e, this.videoCodec = i;
  }
  resetTimeStamp() {
  }
  resetContiguity() {
    const {
      _audioTrack: t,
      _videoTrack: e,
      _id3Track: i
    } = this;
    t && (t.pesData = null), e && (e.pesData = null), i && (i.pesData = null), this.aacOverFlow = null, this.remainderData = null;
  }
  demux(t, e, i = !1, s = !1) {
    i || (this.sampleAes = null);
    let r;
    const a = this._videoTrack, o = this._audioTrack, c = this._id3Track, l = this._txtTrack;
    let h = a.pid, d = a.pesData, u = o.pid, f = c.pid, g = o.pesData, v = c.pesData, p = null, y = this.pmtParsed, E = this._pmtId, T = t.length;
    if (this.remainderData && (t = Nt(this.remainderData, t), T = t.length, this.remainderData = null), T < Et && !s)
      return this.remainderData = t, {
        audioTrack: o,
        videoTrack: a,
        id3Track: c,
        textTrack: l
      };
    const S = Math.max(0, he.syncOffset(t));
    T -= (T - S) % Et, T < t.byteLength && !s && (this.remainderData = new Uint8Array(t.buffer, T, t.buffer.byteLength - T));
    let x = 0;
    for (let A = S; A < T; A += Et)
      if (t[A] === 71) {
        const _ = !!(t[A + 1] & 64), R = rr(t, A), b = (t[A + 3] & 48) >> 4;
        let C;
        if (b > 1) {
          if (C = A + 5 + t[A + 4], C === A + Et)
            continue;
        } else
          C = A + 4;
        switch (R) {
          case h:
            _ && (d && (r = Ge(d, this.logger)) && (this.readyVideoParser(a.segmentCodec), this.videoParser !== null && this.videoParser.parsePES(a, l, r, !1)), d = {
              data: [],
              size: 0
            }), d && (d.data.push(t.subarray(C, A + Et)), d.size += A + Et - C);
            break;
          case u:
            if (_) {
              if (g && (r = Ge(g, this.logger)))
                switch (o.segmentCodec) {
                  case "aac":
                    this.parseAACPES(o, r);
                    break;
                  case "mp3":
                    this.parseMPEGPES(o, r);
                    break;
                  case "ac3":
                    this.parseAC3PES(o, r);
                    break;
                }
              g = {
                data: [],
                size: 0
              };
            }
            g && (g.data.push(t.subarray(C, A + Et)), g.size += A + Et - C);
            break;
          case f:
            _ && (v && (r = Ge(v, this.logger)) && this.parseID3PES(c, r), v = {
              data: [],
              size: 0
            }), v && (v.data.push(t.subarray(C, A + Et)), v.size += A + Et - C);
            break;
          case 0:
            _ && (C += t[C] + 1), E = this._pmtId = jh(t, C);
            break;
          case E: {
            _ && (C += t[C] + 1);
            const F = qh(t, C, this.typeSupported, i, this.observer, this.logger);
            h = F.videoPid, h > 0 && (a.pid = h, a.segmentCodec = F.segmentVideoCodec), u = F.audioPid, u > 0 && (o.pid = u, o.segmentCodec = F.segmentAudioCodec), f = F.id3Pid, f > 0 && (c.pid = f), p !== null && !y && (this.logger.warn(`MPEG-TS PMT found at ${A} after unknown PID '${p}'. Backtracking to sync byte @${S} to parse all TS packets.`), p = null, A = S - 188), y = this.pmtParsed = !0;
            break;
          }
          case 17:
          case 8191:
            break;
          default:
            p = R;
            break;
        }
      } else
        x++;
    x > 0 && nr(this.observer, new Error(`Found ${x} TS packet/s that do not start with 0x47`), void 0, this.logger), a.pesData = d, o.pesData = g, c.pesData = v;
    const D = {
      audioTrack: o,
      videoTrack: a,
      id3Track: c,
      textTrack: l
    };
    return s && this.extractRemainingSamples(D), D;
  }
  flush() {
    const {
      remainderData: t
    } = this;
    this.remainderData = null;
    let e;
    return t ? e = this.demux(t, -1, !1, !0) : e = {
      videoTrack: this._videoTrack,
      audioTrack: this._audioTrack,
      id3Track: this._id3Track,
      textTrack: this._txtTrack
    }, this.extractRemainingSamples(e), this.sampleAes ? this.decrypt(e, this.sampleAes) : e;
  }
  extractRemainingSamples(t) {
    const {
      audioTrack: e,
      videoTrack: i,
      id3Track: s,
      textTrack: r
    } = t, a = i.pesData, o = e.pesData, c = s.pesData;
    let l;
    if (a && (l = Ge(a, this.logger)) ? (this.readyVideoParser(i.segmentCodec), this.videoParser !== null && (this.videoParser.parsePES(i, r, l, !0), i.pesData = null)) : i.pesData = a, o && (l = Ge(o, this.logger))) {
      switch (e.segmentCodec) {
        case "aac":
          this.parseAACPES(e, l);
          break;
        case "mp3":
          this.parseMPEGPES(e, l);
          break;
        case "ac3":
          this.parseAC3PES(e, l);
          break;
      }
      e.pesData = null;
    } else
      o != null && o.size && this.logger.log("last AAC PES packet truncated,might overlap between fragments"), e.pesData = o;
    c && (l = Ge(c, this.logger)) ? (this.parseID3PES(s, l), s.pesData = null) : s.pesData = c;
  }
  demuxSampleAes(t, e, i) {
    const s = this.demux(t, i, !0, !this.config.progressive), r = this.sampleAes = new Wh(this.observer, this.config, e);
    return this.decrypt(s, r);
  }
  readyVideoParser(t) {
    this.videoParser === null && (t === "avc" ? this.videoParser = new Yh() : t === "hevc" && (this.videoParser = new zh()));
  }
  decrypt(t, e) {
    return new Promise((i) => {
      const {
        audioTrack: s,
        videoTrack: r
      } = t;
      s.samples && s.segmentCodec === "aac" ? e.decryptAacSamples(s.samples, 0, () => {
        r.samples ? e.decryptAvcSamples(r.samples, 0, 0, () => {
          i(t);
        }) : i(t);
      }) : r.samples && e.decryptAvcSamples(r.samples, 0, 0, () => {
        i(t);
      });
    });
  }
  destroy() {
    this.observer && this.observer.removeAllListeners(), this.config = this.logger = this.observer = null, this.aacOverFlow = this.videoParser = this.remainderData = this.sampleAes = null, this._videoTrack = this._audioTrack = this._id3Track = this._txtTrack = void 0;
  }
  parseAACPES(t, e) {
    let i = 0;
    const s = this.aacOverFlow;
    let r = e.data;
    if (s) {
      this.aacOverFlow = null;
      const d = s.missing, u = s.sample.unit.byteLength;
      if (d === -1)
        r = Nt(s.sample.unit, r);
      else {
        const f = u - d;
        s.sample.unit.set(r.subarray(0, d), f), t.samples.push(s.sample), i = s.missing;
      }
    }
    let a, o;
    for (a = i, o = r.length; a < o - 1 && !as(r, a); a++)
      ;
    if (a !== i) {
      let d;
      const u = a < o - 1;
      if (u ? d = `AAC PES did not start with ADTS header,offset:${a}` : d = "No ADTS header found in AAC PES", nr(this.observer, new Error(d), u, this.logger), !u)
        return;
    }
    ro(t, this.observer, r, a, this.audioCodec);
    let c;
    if (e.pts !== void 0)
      c = e.pts;
    else if (s) {
      const d = no(t.samplerate);
      c = s.sample.pts + d;
    } else {
      this.logger.warn("[tsdemuxer]: AAC PES unknown PTS");
      return;
    }
    let l = 0, h;
    for (; a < o; )
      if (h = ao(t, r, a, c, l), a += h.length, h.missing) {
        this.aacOverFlow = h;
        break;
      } else
        for (l++; a < o - 1 && !as(r, a); a++)
          ;
  }
  parseMPEGPES(t, e) {
    const i = e.data, s = i.length;
    let r = 0, a = 0;
    const o = e.pts;
    if (o === void 0) {
      this.logger.warn("[tsdemuxer]: MPEG PES unknown PTS");
      return;
    }
    for (; a < s; )
      if (uo(i, a)) {
        const c = co(t, i, a, o, r);
        if (c)
          a += c.length, r++;
        else
          break;
      } else
        a++;
  }
  parseAC3PES(t, e) {
    {
      const i = e.data, s = e.pts;
      if (s === void 0) {
        this.logger.warn("[tsdemuxer]: AC3 PES unknown PTS");
        return;
      }
      const r = i.length;
      let a = 0, o = 0, c;
      for (; o < r && (c = mo(t, i, o, s, a++)) > 0; )
        o += c;
    }
  }
  parseID3PES(t, e) {
    if (e.pts === void 0) {
      this.logger.warn("[tsdemuxer]: ID3 PES unknown PTS");
      return;
    }
    const i = nt({}, e, {
      type: this._videoTrack ? Mt.emsg : Mt.audioId3,
      duration: Number.POSITIVE_INFINITY
    });
    t.samples.push(i);
  }
}
function rr(n, t) {
  return ((n[t + 1] & 31) << 8) + n[t + 2];
}
function jh(n, t) {
  return (n[t + 10] & 31) << 8 | n[t + 11];
}
function qh(n, t, e, i, s, r) {
  const a = {
    audioPid: -1,
    videoPid: -1,
    id3Pid: -1,
    segmentVideoCodec: "avc",
    segmentAudioCodec: "aac"
  }, o = (n[t + 1] & 15) << 8 | n[t + 2], c = t + 3 + o - 4, l = (n[t + 10] & 15) << 8 | n[t + 11];
  for (t += 12 + l; t < c; ) {
    const h = rr(n, t), d = (n[t + 3] & 15) << 8 | n[t + 4];
    switch (n[t]) {
      case 207:
        if (!i) {
          Ds("ADTS AAC", r);
          break;
        }
      /* falls through */
      case 15:
        a.audioPid === -1 && (a.audioPid = h);
        break;
      // Packetized metadata (ID3)
      case 21:
        a.id3Pid === -1 && (a.id3Pid = h);
        break;
      case 219:
        if (!i) {
          Ds("H.264", r);
          break;
        }
      /* falls through */
      case 27:
        a.videoPid === -1 && (a.videoPid = h);
        break;
      // ISO/IEC 11172-3 (MPEG-1 audio)
      // or ISO/IEC 13818-3 (MPEG-2 halved sample rate audio)
      case 3:
      case 4:
        !e.mpeg && !e.mp3 ? r.log("MPEG audio found, not supported in this browser") : a.audioPid === -1 && (a.audioPid = h, a.segmentAudioCodec = "mp3");
        break;
      case 193:
        if (!i) {
          Ds("AC-3", r);
          break;
        }
      /* falls through */
      case 129:
        e.ac3 ? a.audioPid === -1 && (a.audioPid = h, a.segmentAudioCodec = "ac3") : r.log("AC-3 audio found, not supported in this browser");
        break;
      case 6:
        if (a.audioPid === -1 && d > 0) {
          let u = t + 5, f = d;
          for (; f > 2; ) {
            switch (n[u]) {
              case 106:
                e.ac3 !== !0 ? r.log("AC-3 audio found, not supported in this browser for now") : (a.audioPid = h, a.segmentAudioCodec = "ac3");
                break;
            }
            const v = n[u + 1] + 2;
            u += v, f -= v;
          }
        }
        break;
      case 194:
      // SAMPLE-AES EC3
      /* falls through */
      case 135:
        return nr(s, new Error("Unsupported EC-3 in M2TS found"), void 0, r), a;
      case 36:
        a.videoPid === -1 && (a.videoPid = h, a.segmentVideoCodec = "hevc", r.log("HEVC in M2TS found"));
        break;
    }
    t += d + 5;
  }
  return a;
}
function nr(n, t, e, i) {
  i.warn(`parsing error: ${t.message}`), n.emit(m.ERROR, m.ERROR, {
    type: Y.MEDIA_ERROR,
    details: L.FRAG_PARSING_ERROR,
    fatal: !1,
    levelRetry: e,
    error: t,
    reason: t.message
  });
}
function Ds(n, t) {
  t.log(`${n} with AES-128-CBC encryption found in unencrypted stream`);
}
function Ge(n, t) {
  let e = 0, i, s, r, a, o;
  const c = n.data;
  if (!n || n.size === 0)
    return null;
  for (; c[0].length < 19 && c.length > 1; )
    c[0] = Nt(c[0], c[1]), c.splice(1, 1);
  if (i = c[0], (i[0] << 16) + (i[1] << 8) + i[2] === 1) {
    if (s = (i[4] << 8) + i[5], s && s > n.size - 6)
      return null;
    const h = i[7];
    h & 192 && (a = (i[9] & 14) * 536870912 + // 1 << 29
    (i[10] & 255) * 4194304 + // 1 << 22
    (i[11] & 254) * 16384 + // 1 << 14
    (i[12] & 255) * 128 + // 1 << 7
    (i[13] & 254) / 2, h & 64 ? (o = (i[14] & 14) * 536870912 + // 1 << 29
    (i[15] & 255) * 4194304 + // 1 << 22
    (i[16] & 254) * 16384 + // 1 << 14
    (i[17] & 255) * 128 + // 1 << 7
    (i[18] & 254) / 2, a - o > 60 * 9e4 && (t.warn(`${Math.round((a - o) / 9e4)}s delta between PTS and DTS, align them`), a = o)) : o = a), r = i[8];
    let d = r + 9;
    if (n.size <= d)
      return null;
    n.size -= d;
    const u = new Uint8Array(n.size);
    for (let f = 0, g = c.length; f < g; f++) {
      i = c[f];
      let v = i.byteLength;
      if (d)
        if (d > v) {
          d -= v;
          continue;
        } else
          i = i.subarray(d), v -= d, d = 0;
      u.set(i, e), e += v;
    }
    return s && (s -= r + 3), {
      data: u,
      pts: a,
      dts: o,
      len: s
    };
  }
  return null;
}
class Xh {
  static getSilentFrame(t, e) {
    switch (t) {
      case "mp4a.40.2":
        if (e === 1)
          return new Uint8Array([0, 200, 0, 128, 35, 128]);
        if (e === 2)
          return new Uint8Array([33, 0, 73, 144, 2, 25, 0, 35, 128]);
        if (e === 3)
          return new Uint8Array([0, 200, 0, 128, 32, 132, 1, 38, 64, 8, 100, 0, 142]);
        if (e === 4)
          return new Uint8Array([0, 200, 0, 128, 32, 132, 1, 38, 64, 8, 100, 0, 128, 44, 128, 8, 2, 56]);
        if (e === 5)
          return new Uint8Array([0, 200, 0, 128, 32, 132, 1, 38, 64, 8, 100, 0, 130, 48, 4, 153, 0, 33, 144, 2, 56]);
        if (e === 6)
          return new Uint8Array([0, 200, 0, 128, 32, 132, 1, 38, 64, 8, 100, 0, 130, 48, 4, 153, 0, 33, 144, 2, 0, 178, 0, 32, 8, 224]);
        break;
      // handle HE-AAC below (mp4a.40.5 / mp4a.40.29)
      default:
        if (e === 1)
          return new Uint8Array([1, 64, 34, 128, 163, 78, 230, 128, 186, 8, 0, 0, 0, 28, 6, 241, 193, 10, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 94]);
        if (e === 2)
          return new Uint8Array([1, 64, 34, 128, 163, 94, 230, 128, 186, 8, 0, 0, 0, 0, 149, 0, 6, 241, 161, 10, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 94]);
        if (e === 3)
          return new Uint8Array([1, 64, 34, 128, 163, 94, 230, 128, 186, 8, 0, 0, 0, 0, 149, 0, 6, 241, 161, 10, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 94]);
        break;
    }
  }
}
const oe = Math.pow(2, 32) - 1;
class I {
  static init() {
    I.types = {
      avc1: [],
      // codingname
      avcC: [],
      hvc1: [],
      hvcC: [],
      btrt: [],
      dinf: [],
      dref: [],
      esds: [],
      ftyp: [],
      hdlr: [],
      mdat: [],
      mdhd: [],
      mdia: [],
      mfhd: [],
      minf: [],
      moof: [],
      moov: [],
      mp4a: [],
      ".mp3": [],
      dac3: [],
      "ac-3": [],
      mvex: [],
      mvhd: [],
      pasp: [],
      sdtp: [],
      stbl: [],
      stco: [],
      stsc: [],
      stsd: [],
      stsz: [],
      stts: [],
      tfdt: [],
      tfhd: [],
      traf: [],
      trak: [],
      trun: [],
      trex: [],
      tkhd: [],
      vmhd: [],
      smhd: []
    };
    let t;
    for (t in I.types)
      I.types.hasOwnProperty(t) && (I.types[t] = [t.charCodeAt(0), t.charCodeAt(1), t.charCodeAt(2), t.charCodeAt(3)]);
    const e = new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0,
      // pre_defined
      118,
      105,
      100,
      101,
      // handler_type: 'vide'
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      86,
      105,
      100,
      101,
      111,
      72,
      97,
      110,
      100,
      108,
      101,
      114,
      0
      // name: 'VideoHandler'
    ]), i = new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0,
      // pre_defined
      115,
      111,
      117,
      110,
      // handler_type: 'soun'
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      83,
      111,
      117,
      110,
      100,
      72,
      97,
      110,
      100,
      108,
      101,
      114,
      0
      // name: 'SoundHandler'
    ]);
    I.HDLR_TYPES = {
      video: e,
      audio: i
    };
    const s = new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      1,
      // entry_count
      0,
      0,
      0,
      12,
      // entry_size
      117,
      114,
      108,
      32,
      // 'url' type
      0,
      // version 0
      0,
      0,
      1
      // entry_flags
    ]), r = new Uint8Array([
      0,
      // version
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0
      // entry_count
    ]);
    I.STTS = I.STSC = I.STCO = r, I.STSZ = new Uint8Array([
      0,
      // version
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0,
      // sample_size
      0,
      0,
      0,
      0
      // sample_count
    ]), I.VMHD = new Uint8Array([
      0,
      // version
      0,
      0,
      1,
      // flags
      0,
      0,
      // graphicsmode
      0,
      0,
      0,
      0,
      0,
      0
      // opcolor
    ]), I.SMHD = new Uint8Array([
      0,
      // version
      0,
      0,
      0,
      // flags
      0,
      0,
      // balance
      0,
      0
      // reserved
    ]), I.STSD = new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      1
    ]);
    const a = new Uint8Array([105, 115, 111, 109]), o = new Uint8Array([97, 118, 99, 49]), c = new Uint8Array([0, 0, 0, 1]);
    I.FTYP = I.box(I.types.ftyp, a, c, a, o), I.DINF = I.box(I.types.dinf, I.box(I.types.dref, s));
  }
  static box(t, ...e) {
    let i = 8, s = e.length;
    const r = s;
    for (; s--; )
      i += e[s].byteLength;
    const a = new Uint8Array(i);
    for (a[0] = i >> 24 & 255, a[1] = i >> 16 & 255, a[2] = i >> 8 & 255, a[3] = i & 255, a.set(t, 4), s = 0, i = 8; s < r; s++)
      a.set(e[s], i), i += e[s].byteLength;
    return a;
  }
  static hdlr(t) {
    return I.box(I.types.hdlr, I.HDLR_TYPES[t]);
  }
  static mdat(t) {
    return I.box(I.types.mdat, t);
  }
  static mdhd(t, e) {
    e *= t;
    const i = Math.floor(e / (oe + 1)), s = Math.floor(e % (oe + 1));
    return I.box(I.types.mdhd, new Uint8Array([
      1,
      // version 1
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      2,
      // creation_time
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      3,
      // modification_time
      t >> 24 & 255,
      t >> 16 & 255,
      t >> 8 & 255,
      t & 255,
      // timescale
      i >> 24,
      i >> 16 & 255,
      i >> 8 & 255,
      i & 255,
      s >> 24,
      s >> 16 & 255,
      s >> 8 & 255,
      s & 255,
      85,
      196,
      // 'und' language (undetermined)
      0,
      0
    ]));
  }
  static mdia(t) {
    return I.box(I.types.mdia, I.mdhd(t.timescale || 0, t.duration || 0), I.hdlr(t.type), I.minf(t));
  }
  static mfhd(t) {
    return I.box(I.types.mfhd, new Uint8Array([
      0,
      0,
      0,
      0,
      // flags
      t >> 24,
      t >> 16 & 255,
      t >> 8 & 255,
      t & 255
      // sequence_number
    ]));
  }
  static minf(t) {
    return t.type === "audio" ? I.box(I.types.minf, I.box(I.types.smhd, I.SMHD), I.DINF, I.stbl(t)) : I.box(I.types.minf, I.box(I.types.vmhd, I.VMHD), I.DINF, I.stbl(t));
  }
  static moof(t, e, i) {
    return I.box(I.types.moof, I.mfhd(t), I.traf(i, e));
  }
  static moov(t) {
    let e = t.length;
    const i = [];
    for (; e--; )
      i[e] = I.trak(t[e]);
    return I.box.apply(null, [I.types.moov, I.mvhd(t[0].timescale || 0, t[0].duration || 0)].concat(i).concat(I.mvex(t)));
  }
  static mvex(t) {
    let e = t.length;
    const i = [];
    for (; e--; )
      i[e] = I.trex(t[e]);
    return I.box.apply(null, [I.types.mvex, ...i]);
  }
  static mvhd(t, e) {
    e *= t;
    const i = Math.floor(e / (oe + 1)), s = Math.floor(e % (oe + 1)), r = new Uint8Array([
      1,
      // version 1
      0,
      0,
      0,
      // flags
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      2,
      // creation_time
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      3,
      // modification_time
      t >> 24 & 255,
      t >> 16 & 255,
      t >> 8 & 255,
      t & 255,
      // timescale
      i >> 24,
      i >> 16 & 255,
      i >> 8 & 255,
      i & 255,
      s >> 24,
      s >> 16 & 255,
      s >> 8 & 255,
      s & 255,
      0,
      1,
      0,
      0,
      // 1.0 rate
      1,
      0,
      // 1.0 volume
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      0,
      // reserved
      0,
      1,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      1,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      64,
      0,
      0,
      0,
      // transformation: unity matrix
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      // pre_defined
      255,
      255,
      255,
      255
      // next_track_ID
    ]);
    return I.box(I.types.mvhd, r);
  }
  static sdtp(t) {
    const e = t.samples || [], i = new Uint8Array(4 + e.length);
    let s, r;
    for (s = 0; s < e.length; s++)
      r = e[s].flags, i[s + 4] = r.dependsOn << 4 | r.isDependedOn << 2 | r.hasRedundancy;
    return I.box(I.types.sdtp, i);
  }
  static stbl(t) {
    return I.box(I.types.stbl, I.stsd(t), I.box(I.types.stts, I.STTS), I.box(I.types.stsc, I.STSC), I.box(I.types.stsz, I.STSZ), I.box(I.types.stco, I.STCO));
  }
  static avc1(t) {
    let e = [], i = [], s, r, a;
    for (s = 0; s < t.sps.length; s++)
      r = t.sps[s], a = r.byteLength, e.push(a >>> 8 & 255), e.push(a & 255), e = e.concat(Array.prototype.slice.call(r));
    for (s = 0; s < t.pps.length; s++)
      r = t.pps[s], a = r.byteLength, i.push(a >>> 8 & 255), i.push(a & 255), i = i.concat(Array.prototype.slice.call(r));
    const o = I.box(I.types.avcC, new Uint8Array([
      1,
      // version
      e[3],
      // profile
      e[4],
      // profile compat
      e[5],
      // level
      255,
      // lengthSizeMinusOne, hard-coded to 4 bytes
      224 | t.sps.length
      // 3bit reserved (111) + numOfSequenceParameterSets
    ].concat(e).concat([
      t.pps.length
      // numOfPictureParameterSets
    ]).concat(i))), c = t.width, l = t.height, h = t.pixelRatio[0], d = t.pixelRatio[1];
    return I.box(
      I.types.avc1,
      new Uint8Array([
        0,
        0,
        0,
        // reserved
        0,
        0,
        0,
        // reserved
        0,
        1,
        // data_reference_index
        0,
        0,
        // pre_defined
        0,
        0,
        // reserved
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        // pre_defined
        c >> 8 & 255,
        c & 255,
        // width
        l >> 8 & 255,
        l & 255,
        // height
        0,
        72,
        0,
        0,
        // horizresolution
        0,
        72,
        0,
        0,
        // vertresolution
        0,
        0,
        0,
        0,
        // reserved
        0,
        1,
        // frame_count
        18,
        100,
        97,
        105,
        108,
        // dailymotion/hls.js
        121,
        109,
        111,
        116,
        105,
        111,
        110,
        47,
        104,
        108,
        115,
        46,
        106,
        115,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        // compressorname
        0,
        24,
        // depth = 24
        17,
        17
      ]),
      // pre_defined = -1
      o,
      I.box(I.types.btrt, new Uint8Array([
        0,
        28,
        156,
        128,
        // bufferSizeDB
        0,
        45,
        198,
        192,
        // maxBitrate
        0,
        45,
        198,
        192
      ])),
      // avgBitrate
      I.box(I.types.pasp, new Uint8Array([
        h >> 24,
        // hSpacing
        h >> 16 & 255,
        h >> 8 & 255,
        h & 255,
        d >> 24,
        // vSpacing
        d >> 16 & 255,
        d >> 8 & 255,
        d & 255
      ]))
    );
  }
  static esds(t) {
    const e = t.config;
    return new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      3,
      // descriptor_type
      25,
      // length
      0,
      1,
      // es_id
      0,
      // stream_priority
      4,
      // descriptor_type
      17,
      // length
      64,
      // codec : mpeg4_audio
      21,
      // stream_type
      0,
      0,
      0,
      // buffer_size
      0,
      0,
      0,
      0,
      // maxBitrate
      0,
      0,
      0,
      0,
      // avgBitrate
      5,
      // descriptor_type
      2,
      // length
      ...e,
      6,
      1,
      2
      // GASpecificConfig)); // length + audio config descriptor
    ]);
  }
  static audioStsd(t) {
    const e = t.samplerate || 0;
    return new Uint8Array([
      0,
      0,
      0,
      // reserved
      0,
      0,
      0,
      // reserved
      0,
      1,
      // data_reference_index
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      // reserved
      0,
      t.channelCount || 0,
      // channelcount
      0,
      16,
      // sampleSize:16bits
      0,
      0,
      0,
      0,
      // reserved2
      e >> 8 & 255,
      e & 255,
      //
      0,
      0
    ]);
  }
  static mp4a(t) {
    return I.box(I.types.mp4a, I.audioStsd(t), I.box(I.types.esds, I.esds(t)));
  }
  static mp3(t) {
    return I.box(I.types[".mp3"], I.audioStsd(t));
  }
  static ac3(t) {
    return I.box(I.types["ac-3"], I.audioStsd(t), I.box(I.types.dac3, t.config));
  }
  static stsd(t) {
    const {
      segmentCodec: e
    } = t;
    if (t.type === "audio") {
      if (e === "aac")
        return I.box(I.types.stsd, I.STSD, I.mp4a(t));
      if (e === "ac3" && t.config)
        return I.box(I.types.stsd, I.STSD, I.ac3(t));
      if (e === "mp3" && t.codec === "mp3")
        return I.box(I.types.stsd, I.STSD, I.mp3(t));
    } else if (t.pps && t.sps) {
      if (e === "avc")
        return I.box(I.types.stsd, I.STSD, I.avc1(t));
      if (e === "hevc" && t.vps)
        return I.box(I.types.stsd, I.STSD, I.hvc1(t));
    } else
      throw new Error("video track missing pps or sps");
    throw new Error(`unsupported ${t.type} segment codec (${e}/${t.codec})`);
  }
  static tkhd(t) {
    const e = t.id, i = (t.duration || 0) * (t.timescale || 0), s = t.width || 0, r = t.height || 0, a = Math.floor(i / (oe + 1)), o = Math.floor(i % (oe + 1));
    return I.box(I.types.tkhd, new Uint8Array([
      1,
      // version 1
      0,
      0,
      7,
      // flags
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      2,
      // creation_time
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      3,
      // modification_time
      e >> 24 & 255,
      e >> 16 & 255,
      e >> 8 & 255,
      e & 255,
      // track_ID
      0,
      0,
      0,
      0,
      // reserved
      a >> 24,
      a >> 16 & 255,
      a >> 8 & 255,
      a & 255,
      o >> 24,
      o >> 16 & 255,
      o >> 8 & 255,
      o & 255,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      // reserved
      0,
      0,
      // layer
      0,
      0,
      // alternate_group
      0,
      0,
      // non-audio track volume
      0,
      0,
      // reserved
      0,
      1,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      1,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      0,
      64,
      0,
      0,
      0,
      // transformation: unity matrix
      s >> 8 & 255,
      s & 255,
      0,
      0,
      // width
      r >> 8 & 255,
      r & 255,
      0,
      0
      // height
    ]));
  }
  static traf(t, e) {
    const i = I.sdtp(t), s = t.id, r = Math.floor(e / (oe + 1)), a = Math.floor(e % (oe + 1));
    return I.box(
      I.types.traf,
      I.box(I.types.tfhd, new Uint8Array([
        0,
        // version 0
        0,
        0,
        0,
        // flags
        s >> 24,
        s >> 16 & 255,
        s >> 8 & 255,
        s & 255
        // track_ID
      ])),
      I.box(I.types.tfdt, new Uint8Array([
        1,
        // version 1
        0,
        0,
        0,
        // flags
        r >> 24,
        r >> 16 & 255,
        r >> 8 & 255,
        r & 255,
        a >> 24,
        a >> 16 & 255,
        a >> 8 & 255,
        a & 255
      ])),
      I.trun(t, i.length + 16 + // tfhd
      20 + // tfdt
      8 + // traf header
      16 + // mfhd
      8 + // moof header
      8),
      // mdat header
      i
    );
  }
  /**
   * Generate a track box.
   * @param track a track definition
   */
  static trak(t) {
    return t.duration = t.duration || 4294967295, I.box(I.types.trak, I.tkhd(t), I.mdia(t));
  }
  static trex(t) {
    const e = t.id;
    return I.box(I.types.trex, new Uint8Array([
      0,
      // version 0
      0,
      0,
      0,
      // flags
      e >> 24,
      e >> 16 & 255,
      e >> 8 & 255,
      e & 255,
      // track_ID
      0,
      0,
      0,
      1,
      // default_sample_description_index
      0,
      0,
      0,
      0,
      // default_sample_duration
      0,
      0,
      0,
      0,
      // default_sample_size
      0,
      1,
      0,
      1
      // default_sample_flags
    ]));
  }
  static trun(t, e) {
    const i = t.samples || [], s = i.length, r = 12 + 16 * s, a = new Uint8Array(r);
    let o, c, l, h, d, u;
    for (e += 8 + r, a.set([
      t.type === "video" ? 1 : 0,
      // version 1 for video with signed-int sample_composition_time_offset
      0,
      15,
      1,
      // flags
      s >>> 24 & 255,
      s >>> 16 & 255,
      s >>> 8 & 255,
      s & 255,
      // sample_count
      e >>> 24 & 255,
      e >>> 16 & 255,
      e >>> 8 & 255,
      e & 255
      // data_offset
    ], 0), o = 0; o < s; o++)
      c = i[o], l = c.duration, h = c.size, d = c.flags, u = c.cts, a.set([
        l >>> 24 & 255,
        l >>> 16 & 255,
        l >>> 8 & 255,
        l & 255,
        // sample_duration
        h >>> 24 & 255,
        h >>> 16 & 255,
        h >>> 8 & 255,
        h & 255,
        // sample_size
        d.isLeading << 2 | d.dependsOn,
        d.isDependedOn << 6 | d.hasRedundancy << 4 | d.paddingValue << 1 | d.isNonSync,
        d.degradPrio & 61440,
        d.degradPrio & 15,
        // sample_flags
        u >>> 24 & 255,
        u >>> 16 & 255,
        u >>> 8 & 255,
        u & 255
        // sample_composition_time_offset
      ], 12 + 16 * o);
    return I.box(I.types.trun, a);
  }
  static initSegment(t) {
    I.types || I.init();
    const e = I.moov(t);
    return Nt(I.FTYP, e);
  }
  static hvc1(t) {
    const e = t.params, i = [t.vps, t.sps, t.pps], s = 4, r = new Uint8Array([1, e.general_profile_space << 6 | (e.general_tier_flag ? 32 : 0) | e.general_profile_idc, e.general_profile_compatibility_flags[0], e.general_profile_compatibility_flags[1], e.general_profile_compatibility_flags[2], e.general_profile_compatibility_flags[3], e.general_constraint_indicator_flags[0], e.general_constraint_indicator_flags[1], e.general_constraint_indicator_flags[2], e.general_constraint_indicator_flags[3], e.general_constraint_indicator_flags[4], e.general_constraint_indicator_flags[5], e.general_level_idc, 240 | e.min_spatial_segmentation_idc >> 8, 255 & e.min_spatial_segmentation_idc, 252 | e.parallelismType, 252 | e.chroma_format_idc, 248 | e.bit_depth_luma_minus8, 248 | e.bit_depth_chroma_minus8, 0, parseInt(e.frame_rate.fps), s - 1 | e.temporal_id_nested << 2 | e.num_temporal_layers << 3 | (e.frame_rate.fixed ? 64 : 0), i.length]);
    let a = r.length;
    for (let g = 0; g < i.length; g += 1) {
      a += 3;
      for (let v = 0; v < i[g].length; v += 1)
        a += 2 + i[g][v].length;
    }
    const o = new Uint8Array(a);
    o.set(r, 0), a = r.length;
    const c = i.length - 1;
    for (let g = 0; g < i.length; g += 1) {
      o.set(new Uint8Array([32 + g | (g === c ? 128 : 0), 0, i[g].length]), a), a += 3;
      for (let v = 0; v < i[g].length; v += 1)
        o.set(new Uint8Array([i[g][v].length >> 8, i[g][v].length & 255]), a), a += 2, o.set(i[g][v], a), a += i[g][v].length;
    }
    const l = I.box(I.types.hvcC, o), h = t.width, d = t.height, u = t.pixelRatio[0], f = t.pixelRatio[1];
    return I.box(
      I.types.hvc1,
      new Uint8Array([
        0,
        0,
        0,
        // reserved
        0,
        0,
        0,
        // reserved
        0,
        1,
        // data_reference_index
        0,
        0,
        // pre_defined
        0,
        0,
        // reserved
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        // pre_defined
        h >> 8 & 255,
        h & 255,
        // width
        d >> 8 & 255,
        d & 255,
        // height
        0,
        72,
        0,
        0,
        // horizresolution
        0,
        72,
        0,
        0,
        // vertresolution
        0,
        0,
        0,
        0,
        // reserved
        0,
        1,
        // frame_count
        18,
        100,
        97,
        105,
        108,
        // dailymotion/hls.js
        121,
        109,
        111,
        116,
        105,
        111,
        110,
        47,
        104,
        108,
        115,
        46,
        106,
        115,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        // compressorname
        0,
        24,
        // depth = 24
        17,
        17
      ]),
      // pre_defined = -1
      l,
      I.box(I.types.btrt, new Uint8Array([
        0,
        28,
        156,
        128,
        // bufferSizeDB
        0,
        45,
        198,
        192,
        // maxBitrate
        0,
        45,
        198,
        192
      ])),
      // avgBitrate
      I.box(I.types.pasp, new Uint8Array([
        u >> 24,
        // hSpacing
        u >> 16 & 255,
        u >> 8 & 255,
        u & 255,
        f >> 24,
        // vSpacing
        f >> 16 & 255,
        f >> 8 & 255,
        f & 255
      ]))
    );
  }
}
I.types = void 0;
I.HDLR_TYPES = void 0;
I.STTS = void 0;
I.STSC = void 0;
I.STCO = void 0;
I.STSZ = void 0;
I.VMHD = void 0;
I.SMHD = void 0;
I.STSD = void 0;
I.FTYP = void 0;
I.DINF = void 0;
const vo = 9e4;
function Or(n, t, e = 1, i = !1) {
  const s = n * t * e;
  return i ? Math.round(s) : s;
}
function Qh(n, t, e = 1, i = !1) {
  return Or(n, t, 1 / e, i);
}
function ci(n, t = !1) {
  return Or(n, 1e3, 1 / vo, t);
}
function Zh(n, t = 1) {
  return Or(n, vo, 1 / t);
}
function $n(n) {
  const {
    baseTime: t,
    timescale: e,
    trackId: i
  } = n;
  return `${t / e} (${t}/${e}) trackId: ${i}`;
}
const Jh = 10 * 1e3, td = 1024, ed = 1152, id = 1536;
let Ke = null, ws = null;
function Nn(n, t, e, i) {
  return {
    duration: t,
    size: e,
    cts: i,
    flags: {
      isLeading: 0,
      isDependedOn: 0,
      hasRedundancy: 0,
      degradPrio: 0,
      dependsOn: n ? 2 : 1,
      isNonSync: n ? 0 : 1
    }
  };
}
class Vi extends Bt {
  constructor(t, e, i, s) {
    if (super("mp4-remuxer", s), this.observer = void 0, this.config = void 0, this.typeSupported = void 0, this.ISGenerated = !1, this._initPTS = null, this._initDTS = null, this.nextVideoTs = null, this.nextAudioTs = null, this.videoSampleDuration = null, this.isAudioContiguous = !1, this.isVideoContiguous = !1, this.videoTrackConfig = void 0, this.observer = t, this.config = e, this.typeSupported = i, this.ISGenerated = !1, Ke === null) {
      const a = (navigator.userAgent || "").match(/Chrome\/(\d+)/i);
      Ke = a ? parseInt(a[1]) : 0;
    }
    if (ws === null) {
      const r = navigator.userAgent.match(/Safari\/(\d+)/i);
      ws = r ? parseInt(r[1]) : 0;
    }
  }
  destroy() {
    this.config = this.videoTrackConfig = this._initPTS = this._initDTS = null;
  }
  resetTimeStamp(t) {
    const e = this._initPTS;
    (!e || !t || t.trackId !== e.trackId || t.baseTime !== e.baseTime || t.timescale !== e.timescale) && this.log(`Reset initPTS: ${e && $n(e)} > ${t && $n(t)}`), this._initPTS = this._initDTS = t;
  }
  resetNextTimestamp() {
    this.log("reset next timestamp"), this.isVideoContiguous = !1, this.isAudioContiguous = !1;
  }
  resetInitSegment() {
    this.log("ISGenerated flag reset"), this.ISGenerated = !1, this.videoTrackConfig = void 0;
  }
  getVideoStartPts(t) {
    let e = !1;
    const i = t[0].pts, s = t.reduce((r, a) => {
      let o = a.pts, c = o - r;
      return c < -4294967296 && (e = !0, o = Ot(o, i), c = o - r), c > 0 ? r : o;
    }, i);
    return e && this.debug("PTS rollover detected"), s;
  }
  remux(t, e, i, s, r, a, o, c) {
    let l, h, d, u, f, g, v = r, p = r;
    const y = t.pid > -1, E = e.pid > -1, T = e.samples.length, S = t.samples.length > 0, x = o && T > 0 || T > 1;
    if ((!y || S) && (!E || x) || this.ISGenerated || o) {
      if (this.ISGenerated) {
        var A, _, R, b;
        const W = this.videoTrackConfig;
        (W && (e.width !== W.width || e.height !== W.height || ((A = e.pixelRatio) == null ? void 0 : A[0]) !== ((_ = W.pixelRatio) == null ? void 0 : _[0]) || ((R = e.pixelRatio) == null ? void 0 : R[1]) !== ((b = W.pixelRatio) == null ? void 0 : b[1])) || !W && x || this.nextAudioTs === null && S) && this.resetInitSegment();
      }
      this.ISGenerated || (d = this.generateIS(t, e, r, a));
      const C = this.isVideoContiguous;
      let F = -1, U;
      if (x && (F = sd(e.samples), !C && this.config.forceKeyFrameOnDiscontinuity))
        if (g = !0, F > 0) {
          this.warn(`Dropped ${F} out of ${T} video samples due to a missing keyframe`);
          const W = this.getVideoStartPts(e.samples);
          e.samples = e.samples.slice(F), e.dropped += F, p += (e.samples[0].pts - W) / e.inputTimeScale, U = p;
        } else F === -1 && (this.warn(`No keyframe found out of ${T} video samples`), g = !1);
      if (this.ISGenerated) {
        if (S && x) {
          const W = this.getVideoStartPts(e.samples), k = (Ot(t.samples[0].pts, W) - W) / e.inputTimeScale;
          v += Math.max(0, k), p += Math.max(0, -k);
        }
        if (S) {
          if (t.samplerate || (this.warn("regenerate InitSegment as audio detected"), d = this.generateIS(t, e, r, a)), h = this.remuxAudio(t, v, this.isAudioContiguous, a, E || x || c === K.AUDIO ? p : void 0), x) {
            const W = h ? h.endPTS - h.startPTS : 0;
            e.inputTimeScale || (this.warn("regenerate InitSegment as video detected"), d = this.generateIS(t, e, r, a)), l = this.remuxVideo(e, p, C, W);
          }
        } else x && (l = this.remuxVideo(e, p, C, 0));
        l && (l.firstKeyFrame = F, l.independent = F !== -1, l.firstKeyFramePTS = U);
      }
    }
    return this.ISGenerated && this._initPTS && this._initDTS && (i.samples.length && (f = yo(i, r, this._initPTS, this._initDTS)), s.samples.length && (u = Eo(s, r, this._initPTS))), {
      audio: h,
      video: l,
      initSegment: d,
      independent: g,
      text: u,
      id3: f
    };
  }
  computeInitPts(t, e, i, s) {
    const r = Math.round(i * e);
    let a = Ot(t, r);
    if (a < r + e)
      for (this.log(`Adjusting PTS for rollover in timeline near ${(r - a) / e} ${s}`); a < r + e; )
        a += 8589934592;
    return a - r;
  }
  generateIS(t, e, i, s) {
    const r = t.samples, a = e.samples, o = this.typeSupported, c = {}, l = this._initPTS;
    let h = !l || s, d = "audio/mp4", u, f, g, v = -1;
    if (h && (u = f = 1 / 0), t.config && r.length) {
      switch (t.timescale = t.samplerate, t.segmentCodec) {
        case "mp3":
          o.mpeg ? (d = "audio/mpeg", t.codec = "") : o.mp3 && (t.codec = "mp3");
          break;
        case "ac3":
          t.codec = "ac-3";
          break;
      }
      c.audio = {
        id: "audio",
        container: d,
        codec: t.codec,
        initSegment: t.segmentCodec === "mp3" && o.mpeg ? new Uint8Array(0) : I.initSegment([t]),
        metadata: {
          channelCount: t.channelCount
        }
      }, h && (v = t.id, g = t.inputTimeScale, !l || g !== l.timescale ? u = f = this.computeInitPts(r[0].pts, g, i, "audio") : h = !1);
    }
    if (e.sps && e.pps && a.length) {
      if (e.timescale = e.inputTimeScale, c.video = {
        id: "main",
        container: "video/mp4",
        codec: e.codec,
        initSegment: I.initSegment([e]),
        metadata: {
          width: e.width,
          height: e.height
        }
      }, h)
        if (v = e.id, g = e.inputTimeScale, !l || g !== l.timescale) {
          const p = this.getVideoStartPts(a), y = Ot(a[0].dts, p), E = this.computeInitPts(y, g, i, "video"), T = this.computeInitPts(p, g, i, "video");
          f = Math.min(f, E), u = Math.min(u, T);
        } else
          h = !1;
      this.videoTrackConfig = {
        width: e.width,
        height: e.height,
        pixelRatio: e.pixelRatio
      };
    }
    if (Object.keys(c).length)
      return this.ISGenerated = !0, h ? (l && this.warn(`Timestamps at playlist time: ${s ? "" : "~"}${i} ${u / g} != initPTS: ${l.baseTime / l.timescale} (${l.baseTime}/${l.timescale}) trackId: ${l.trackId}`), this.log(`Found initPTS at playlist time: ${i} offset: ${u / g} (${u}/${g}) trackId: ${v}`), this._initPTS = {
        baseTime: u,
        timescale: g,
        trackId: v
      }, this._initDTS = {
        baseTime: f,
        timescale: g,
        trackId: v
      }) : u = g = void 0, {
        tracks: c,
        initPTS: u,
        timescale: g,
        trackId: v
      };
  }
  remuxVideo(t, e, i, s) {
    const r = t.inputTimeScale, a = t.samples, o = [], c = a.length, l = this._initPTS, h = l.baseTime * r / l.timescale;
    let d = this.nextVideoTs, u = 8, f = this.videoSampleDuration, g, v, p = Number.POSITIVE_INFINITY, y = Number.NEGATIVE_INFINITY, E = !1;
    if (!i || d === null) {
      const O = h + e * r, M = a[0].pts - Ot(a[0].dts, a[0].pts);
      Ke && d !== null && Math.abs(O - M - (d + h)) < 15e3 ? i = !0 : d = O - M - h;
    }
    const T = d + h;
    for (let O = 0; O < c; O++) {
      const M = a[O];
      M.pts = Ot(M.pts, T), M.dts = Ot(M.dts, T), M.dts < a[O > 0 ? O - 1 : O].dts && (E = !0);
    }
    E && a.sort(function(O, M) {
      const X = O.dts - M.dts, et = O.pts - M.pts;
      return X || et;
    }), g = a[0].dts, v = a[a.length - 1].dts;
    const S = v - g, x = S ? Math.round(S / (c - 1)) : f || t.inputTimeScale / 30;
    if (i) {
      const O = g - T, M = O > x, X = O < -1;
      if ((M || X) && (M ? this.warn(`${(t.segmentCodec || "").toUpperCase()}: ${ci(O, !0)} ms (${O}dts) hole between fragments detected at ${e.toFixed(3)}`) : this.warn(`${(t.segmentCodec || "").toUpperCase()}: ${ci(-O, !0)} ms (${O}dts) overlapping between fragments detected at ${e.toFixed(3)}`), !X || T >= a[0].pts || Ke)) {
        g = T;
        const et = a[0].pts - O;
        if (M)
          a[0].dts = g, a[0].pts = et;
        else {
          let Q = !0;
          for (let J = 0; J < a.length && !(a[J].dts > et && Q); J++) {
            const pt = a[J].pts;
            if (a[J].dts -= O, a[J].pts -= O, J < a.length - 1) {
              const mt = a[J + 1].pts, Rt = a[J].pts, Wt = mt <= Rt, Te = mt <= pt;
              Q = Wt == Te;
            }
          }
        }
        this.log(`Video: Initial PTS/DTS adjusted: ${ci(et, !0)}/${ci(g, !0)}, delta: ${ci(O, !0)} ms`);
      }
    }
    g = Math.max(0, g);
    let D = 0, A = 0, _ = g;
    for (let O = 0; O < c; O++) {
      const M = a[O], X = M.units, et = X.length;
      let Q = 0;
      for (let J = 0; J < et; J++)
        Q += X[J].data.length;
      A += Q, D += et, M.length = Q, M.dts < _ ? (M.dts = _, _ += x / 4 | 0 || 1) : _ = M.dts, p = Math.min(M.pts, p), y = Math.max(M.pts, y);
    }
    v = a[c - 1].dts;
    const R = A + 4 * D + 8;
    let b;
    try {
      b = new Uint8Array(R);
    } catch (O) {
      this.observer.emit(m.ERROR, m.ERROR, {
        type: Y.MUX_ERROR,
        details: L.REMUX_ALLOC_ERROR,
        fatal: !1,
        error: O,
        bytes: R,
        reason: `fail allocating video mdat ${R}`
      });
      return;
    }
    const C = new DataView(b.buffer);
    C.setUint32(0, R), b.set(I.types.mdat, 4);
    let F = !1, U = Number.POSITIVE_INFINITY, W = Number.POSITIVE_INFINITY, G = Number.NEGATIVE_INFINITY, k = Number.NEGATIVE_INFINITY;
    for (let O = 0; O < c; O++) {
      const M = a[O], X = M.units;
      let et = 0;
      for (let pt = 0, mt = X.length; pt < mt; pt++) {
        const Rt = X[pt], Wt = Rt.data, Te = Rt.data.byteLength;
        C.setUint32(u, Te), u += 4, b.set(Wt, u), u += Te, et += 4 + Te;
      }
      let Q;
      if (O < c - 1)
        f = a[O + 1].dts - M.dts, Q = a[O + 1].pts - M.pts;
      else {
        const pt = this.config, mt = O > 0 ? M.dts - a[O - 1].dts : x;
        if (Q = O > 0 ? M.pts - a[O - 1].pts : x, pt.stretchShortVideoTrack && this.nextAudioTs !== null) {
          const Rt = Math.floor(pt.maxBufferHole * r), Wt = (s ? p + s * r : this.nextAudioTs + h) - M.pts;
          Wt > Rt ? (f = Wt - mt, f < 0 ? f = mt : F = !0, this.log(`It is approximately ${Wt / 90} ms to the next segment; using duration ${f / 90} ms for the last video frame.`)) : f = mt;
        } else
          f = mt;
      }
      const J = Math.round(M.pts - M.dts);
      U = Math.min(U, f), G = Math.max(G, f), W = Math.min(W, Q), k = Math.max(k, Q), o.push(Nn(M.key, f, et, J));
    }
    if (o.length) {
      if (Ke) {
        if (Ke < 70) {
          const O = o[0].flags;
          O.dependsOn = 2, O.isNonSync = 0;
        }
      } else if (ws && k - W < G - U && x / G < 0.025 && o[0].cts === 0) {
        this.warn("Found irregular gaps in sample duration. Using PTS instead of DTS to determine MP4 sample duration.");
        let O = g;
        for (let M = 0, X = o.length; M < X; M++) {
          const et = O + o[M].duration, Q = O + o[M].cts;
          if (M < X - 1) {
            const J = et + o[M + 1].cts;
            o[M].duration = J - Q;
          } else
            o[M].duration = M ? o[M - 1].duration : x;
          o[M].cts = 0, O = et;
        }
      }
    }
    f = F || !f ? x : f;
    const H = v + f;
    this.nextVideoTs = d = H - h, this.videoSampleDuration = f, this.isVideoContiguous = !0;
    const z = {
      data1: I.moof(t.sequenceNumber++, g, nt(t, {
        samples: o
      })),
      data2: b,
      startPTS: (p - h) / r,
      endPTS: (y + f - h) / r,
      startDTS: (g - h) / r,
      endDTS: d / r,
      type: "video",
      hasAudio: !1,
      hasVideo: !0,
      nb: o.length,
      dropped: t.dropped
    };
    return t.samples = [], t.dropped = 0, z;
  }
  getSamplesPerFrame(t) {
    switch (t.segmentCodec) {
      case "mp3":
        return ed;
      case "ac3":
        return id;
      default:
        return td;
    }
  }
  remuxAudio(t, e, i, s, r) {
    const a = t.inputTimeScale, o = t.samplerate ? t.samplerate : a, c = a / o, l = this.getSamplesPerFrame(t), h = l * c, d = this._initPTS, u = t.segmentCodec === "mp3" && this.typeSupported.mpeg, f = [], g = r !== void 0;
    let v = t.samples, p = u ? 0 : 8, y = this.nextAudioTs || -1;
    const E = d.baseTime * a / d.timescale, T = E + e * a;
    if (this.isAudioContiguous = i = i || v.length && y > 0 && (s && Math.abs(T - (y + E)) < 9e3 || Math.abs(Ot(v[0].pts, T) - (y + E)) < 20 * h), v.forEach(function(k) {
      k.pts = Ot(k.pts, T);
    }), !i || y < 0) {
      const k = v.length;
      if (v = v.filter((H) => H.pts >= 0), k !== v.length && this.warn(`Removed ${v.length - k} of ${k} samples (initPTS ${E} / ${a})`), !v.length)
        return;
      r === 0 ? y = 0 : s && !g ? y = Math.max(0, T - E) : y = v[0].pts - E;
    }
    if (t.segmentCodec === "aac") {
      const k = this.config.maxAudioFramesDrift;
      for (let H = 0, $ = y + E; H < v.length; H++) {
        const V = v[H], z = V.pts, O = z - $, M = Math.abs(1e3 * O / a);
        if (O <= -k * h && g)
          H === 0 && (this.warn(`Audio frame @ ${(z / a).toFixed(3)}s overlaps marker by ${Math.round(1e3 * O / a)} ms.`), this.nextAudioTs = y = z - E, $ = z);
        else if (O >= k * h && M < Jh && g) {
          let X = Math.round(O / h);
          for ($ = z - X * h; $ < 0 && X && h; )
            X--, $ += h;
          H === 0 && (this.nextAudioTs = y = $ - E), this.warn(`Injecting ${X} audio frames @ ${(($ - E) / a).toFixed(3)}s due to ${Math.round(1e3 * O / a)} ms gap.`);
          for (let et = 0; et < X; et++) {
            let Q = Xh.getSilentFrame(t.parsedCodec || t.manifestCodec || t.codec, t.channelCount);
            Q || (this.log("Unable to get silent frame for given audio codec; duplicating last frame instead."), Q = V.unit.subarray()), v.splice(H, 0, {
              unit: Q,
              pts: $
            }), $ += h, H++;
          }
        }
        V.pts = $, $ += h;
      }
    }
    let S = null, x = null, D, A = 0, _ = v.length;
    for (; _--; )
      A += v[_].unit.byteLength;
    for (let k = 0, H = v.length; k < H; k++) {
      const $ = v[k], V = $.unit;
      let z = $.pts;
      if (x !== null) {
        const M = f[k - 1];
        M.duration = Math.round((z - x) / c);
      } else if (i && t.segmentCodec === "aac" && (z = y + E), S = z, A > 0) {
        A += p;
        try {
          D = new Uint8Array(A);
        } catch (M) {
          this.observer.emit(m.ERROR, m.ERROR, {
            type: Y.MUX_ERROR,
            details: L.REMUX_ALLOC_ERROR,
            fatal: !1,
            error: M,
            bytes: A,
            reason: `fail allocating audio mdat ${A}`
          });
          return;
        }
        u || (new DataView(D.buffer).setUint32(0, A), D.set(I.types.mdat, 4));
      } else
        return;
      D.set(V, p);
      const O = V.byteLength;
      p += O, f.push(Nn(!0, l, O, 0)), x = z;
    }
    const R = f.length;
    if (!R)
      return;
    const b = f[f.length - 1];
    y = x - E, this.nextAudioTs = y + c * b.duration;
    const C = u ? new Uint8Array(0) : I.moof(t.sequenceNumber++, S / c, nt({}, t, {
      samples: f
    }));
    t.samples = [];
    const F = (S - E) / a, U = this.nextAudioTs / a, G = {
      data1: C,
      data2: D,
      startPTS: F,
      endPTS: U,
      startDTS: F,
      endDTS: U,
      type: "audio",
      hasAudio: !0,
      hasVideo: !1,
      nb: R
    };
    return this.isAudioContiguous = !0, G;
  }
}
function Ot(n, t) {
  let e;
  if (t === null)
    return n;
  for (t < n ? e = -8589934592 : e = 8589934592; Math.abs(n - t) > 4294967296; )
    n += e;
  return n;
}
function sd(n) {
  for (let t = 0; t < n.length; t++)
    if (n[t].key)
      return t;
  return -1;
}
function yo(n, t, e, i) {
  const s = n.samples.length;
  if (!s)
    return;
  const r = n.inputTimeScale;
  for (let o = 0; o < s; o++) {
    const c = n.samples[o];
    c.pts = Ot(c.pts - e.baseTime * r / e.timescale, t * r) / r, c.dts = Ot(c.dts - i.baseTime * r / i.timescale, t * r) / r;
  }
  const a = n.samples;
  return n.samples = [], {
    samples: a
  };
}
function Eo(n, t, e) {
  const i = n.samples.length;
  if (!i)
    return;
  const s = n.inputTimeScale;
  for (let a = 0; a < i; a++) {
    const o = n.samples[a];
    o.pts = Ot(o.pts - e.baseTime * s / e.timescale, t * s) / s;
  }
  n.samples.sort((a, o) => a.pts - o.pts);
  const r = n.samples;
  return n.samples = [], {
    samples: r
  };
}
class rd extends Bt {
  constructor(t, e, i, s) {
    super("passthrough-remuxer", s), this.emitInitSegment = !1, this.audioCodec = void 0, this.videoCodec = void 0, this.initData = void 0, this.initPTS = null, this.initTracks = void 0, this.lastEndTime = null, this.isVideoContiguous = !1;
  }
  destroy() {
  }
  resetTimeStamp(t) {
    this.lastEndTime = null;
    const e = this.initPTS;
    e && t && e.baseTime === t.baseTime && e.timescale === t.timescale || (this.initPTS = t);
  }
  resetNextTimestamp() {
    this.isVideoContiguous = !1, this.lastEndTime = null;
  }
  resetInitSegment(t, e, i, s) {
    this.audioCodec = e, this.videoCodec = i, this.generateInitSegment(t, s), this.emitInitSegment = !0;
  }
  generateInitSegment(t, e) {
    let {
      audioCodec: i,
      videoCodec: s
    } = this;
    if (!(t != null && t.byteLength)) {
      this.initTracks = void 0, this.initData = void 0;
      return;
    }
    const {
      audio: r,
      video: a
    } = this.initData = ba(t);
    if (e)
      Wl(t, e);
    else {
      const c = r || a;
      c != null && c.encrypted && this.warn(`Init segment with encrypted track with has no key ("${c.codec}")!`);
    }
    r && (i = Bn(r, at.AUDIO, this)), a && (s = Bn(a, at.VIDEO, this));
    const o = {};
    r && a ? o.audiovideo = {
      container: "video/mp4",
      codec: i + "," + s,
      supplemental: a.supplemental,
      encrypted: a.encrypted,
      initSegment: t,
      id: "main"
    } : r ? o.audio = {
      container: "audio/mp4",
      codec: i,
      encrypted: r.encrypted,
      initSegment: t,
      id: "audio"
    } : a ? o.video = {
      container: "video/mp4",
      codec: s,
      supplemental: a.supplemental,
      encrypted: a.encrypted,
      initSegment: t,
      id: "main"
    } : this.warn("initSegment does not contain moov or trak boxes."), this.initTracks = o;
  }
  remux(t, e, i, s, r, a) {
    var o, c;
    let {
      initPTS: l,
      lastEndTime: h
    } = this;
    const d = {
      audio: void 0,
      video: void 0,
      text: s,
      id3: i,
      initSegment: void 0
    };
    B(h) || (h = this.lastEndTime = r || 0);
    const u = e.samples;
    if (!u.length)
      return d;
    const f = {
      initPTS: void 0,
      timescale: void 0,
      trackId: void 0
    };
    let g = this.initData;
    if ((o = g) != null && o.length || (this.generateInitSegment(u), g = this.initData), !((c = g) != null && c.length))
      return this.warn("Failed to generate initSegment."), d;
    this.emitInitSegment && (f.tracks = this.initTracks, this.emitInitSegment = !1);
    const v = zl(u, g, this), p = g.audio ? v[g.audio.id] : null, y = g.video ? v[g.video.id] : null, E = Pi(y, 1 / 0), T = Pi(p, 1 / 0), S = Pi(y, 0, !0), x = Pi(p, 0, !0);
    let D = r, A = 0;
    const _ = p && (!y || !l && T < E || l && l.trackId === g.audio.id), R = _ ? p : y;
    if (R) {
      const $ = R.timescale, V = R.start - r * $, z = _ ? g.audio.id : g.video.id;
      D = R.start / $, A = _ ? x - T : S - E, (a || !l) && (nd(l, D, r, A) || $ !== l.timescale) && (l && this.warn(`Timestamps at playlist time: ${a ? "" : "~"}${r} ${V / $} != initPTS: ${l.baseTime / l.timescale} (${l.baseTime}/${l.timescale}) trackId: ${l.trackId}`), this.log(`Found initPTS at playlist time: ${r} offset: ${D - r} (${V}/${$}) trackId: ${z}`), l = null, f.initPTS = V, f.timescale = $, f.trackId = z);
    } else
      this.warn(`No audio or video samples found for initPTS at playlist time: ${r}`);
    l ? (f.initPTS = l.baseTime, f.timescale = l.timescale, f.trackId = l.trackId) : ((!f.timescale || f.trackId === void 0 || f.initPTS === void 0) && (this.warn("Could not set initPTS"), f.initPTS = D, f.timescale = 1, f.trackId = -1), this.initPTS = l = {
      baseTime: f.initPTS,
      timescale: f.timescale,
      trackId: f.trackId
    });
    const b = D - l.baseTime / l.timescale, C = b + A;
    A > 0 ? this.lastEndTime = C : (this.warn("Duration parsed from mp4 should be greater than zero"), this.resetNextTimestamp());
    const F = !!g.audio, U = !!g.video;
    let W = "";
    F && (W += "audio"), U && (W += "video");
    const G = (g.audio ? g.audio.encrypted : !1) || (g.video ? g.video.encrypted : !1), k = {
      data1: u,
      startPTS: b,
      startDTS: b,
      endPTS: C,
      endDTS: C,
      type: W,
      hasAudio: F,
      hasVideo: U,
      nb: 1,
      dropped: 0,
      encrypted: G
    };
    d.audio = F && !U ? k : void 0, d.video = U ? k : void 0;
    const H = y == null ? void 0 : y.sampleCount;
    if (H) {
      const $ = y.keyFrameIndex, V = $ !== -1;
      k.nb = H, k.dropped = $ === 0 || this.isVideoContiguous ? 0 : V ? $ : H, k.independent = V, k.firstKeyFrame = $, V && y.keyFrameStart && (k.firstKeyFramePTS = (y.keyFrameStart - l.baseTime) / l.timescale), this.isVideoContiguous || (d.independent = V), this.isVideoContiguous || (this.isVideoContiguous = V), k.dropped && this.warn(`fmp4 does not start with IDR: firstIDR ${$}/${H} dropped: ${k.dropped} start: ${k.firstKeyFramePTS || "NA"}`);
    }
    return d.initSegment = f, d.id3 = yo(i, r, l, l), s.samples.length && (d.text = Eo(s, r, l)), d;
  }
}
function Pi(n, t, e = !1) {
  return (n == null ? void 0 : n.start) !== void 0 ? (n.start + (e ? n.duration : 0)) / n.timescale : t;
}
function nd(n, t, e, i) {
  if (n === null)
    return !0;
  const s = Math.max(i, 1), r = t - n.baseTime / n.timescale;
  return Math.abs(r - e) > s;
}
function Bn(n, t, e) {
  const i = n.codec;
  return i && i.length > 4 ? i : t === at.AUDIO ? i === "ec-3" || i === "ac-3" || i === "alac" ? i : i === "fLaC" || i === "Opus" ? Zi(i, !1) : (e.warn(`Unhandled audio codec "${i}" in mp4 MAP`), i || "mp4a") : (e.warn(`Unhandled video codec "${i}" in mp4 MAP`), i || "avc1");
}
let re;
try {
  re = self.performance.now.bind(self.performance);
} catch {
  re = Date.now;
}
const Wi = [{
  demux: Vh,
  remux: rd
}, {
  demux: he,
  remux: Vi
}, {
  demux: Uh,
  remux: Vi
}, {
  demux: Kh,
  remux: Vi
}];
Wi.splice(2, 0, {
  demux: Gh,
  remux: Vi
});
class Un {
  constructor(t, e, i, s, r, a) {
    this.asyncResult = !1, this.logger = void 0, this.observer = void 0, this.typeSupported = void 0, this.config = void 0, this.id = void 0, this.demuxer = void 0, this.remuxer = void 0, this.decrypter = void 0, this.probe = void 0, this.decryptionPromise = null, this.transmuxConfig = void 0, this.currentTransmuxState = void 0, this.observer = t, this.typeSupported = e, this.config = i, this.id = r, this.logger = a;
  }
  configure(t) {
    this.transmuxConfig = t, this.decrypter && this.decrypter.reset();
  }
  push(t, e, i, s) {
    const r = i.transmuxing;
    r.executeStart = re();
    let a = new Uint8Array(t);
    const {
      currentTransmuxState: o,
      transmuxConfig: c
    } = this;
    s && (this.currentTransmuxState = s);
    const {
      contiguous: l,
      discontinuity: h,
      trackSwitch: d,
      accurateTimeOffset: u,
      timeOffset: f,
      initSegmentChange: g
    } = s || o, {
      audioCodec: v,
      videoCodec: p,
      defaultInitPts: y,
      duration: E,
      initSegmentData: T
    } = c, S = ad(a, e);
    if (S && Ye(S.method)) {
      const _ = this.getDecrypter(), R = Ir(S.method);
      if (_.isSync()) {
        let b = _.softwareDecrypt(a, S.key.buffer, S.iv.buffer, R);
        if (i.part > -1) {
          const F = _.flush();
          b = F && F.buffer;
        }
        if (!b)
          return r.executeEnd = re(), Cs(i);
        a = new Uint8Array(b);
      } else
        return this.asyncResult = !0, this.decryptionPromise = _.webCryptoDecrypt(a, S.key.buffer, S.iv.buffer, R).then((b) => {
          const C = this.push(b, null, i);
          return this.decryptionPromise = null, C;
        }), this.decryptionPromise;
    }
    const x = this.needsProbing(h, d);
    if (x) {
      const _ = this.configureTransmuxer(a);
      if (_)
        return this.logger.warn(`[transmuxer] ${_.message}`), this.observer.emit(m.ERROR, m.ERROR, {
          type: Y.MEDIA_ERROR,
          details: L.FRAG_PARSING_ERROR,
          fatal: !1,
          error: _,
          reason: _.message
        }), r.executeEnd = re(), Cs(i);
    }
    (h || d || g || x) && this.resetInitSegment(T, v, p, E, e), (h || g || x) && this.resetInitialTimestamp(y), l || this.resetContiguity();
    const D = this.transmux(a, S, f, u, i);
    this.asyncResult = Ei(D);
    const A = this.currentTransmuxState;
    return A.contiguous = !0, A.discontinuity = !1, A.trackSwitch = !1, r.executeEnd = re(), D;
  }
  // Due to data caching, flush calls can produce more than one TransmuxerResult (hence the Array type)
  flush(t) {
    const e = t.transmuxing;
    e.executeStart = re();
    const {
      decrypter: i,
      currentTransmuxState: s,
      decryptionPromise: r
    } = this;
    if (r)
      return this.asyncResult = !0, r.then(() => this.flush(t));
    const a = [], {
      timeOffset: o
    } = s;
    if (i) {
      const d = i.flush();
      d && a.push(this.push(d.buffer, null, t));
    }
    const {
      demuxer: c,
      remuxer: l
    } = this;
    if (!c || !l) {
      e.executeEnd = re();
      const d = [Cs(t)];
      return this.asyncResult ? Promise.resolve(d) : d;
    }
    const h = c.flush(o);
    return Ei(h) ? (this.asyncResult = !0, h.then((d) => (this.flushRemux(a, d, t), a))) : (this.flushRemux(a, h, t), this.asyncResult ? Promise.resolve(a) : a);
  }
  flushRemux(t, e, i) {
    const {
      audioTrack: s,
      videoTrack: r,
      id3Track: a,
      textTrack: o
    } = e, {
      accurateTimeOffset: c,
      timeOffset: l
    } = this.currentTransmuxState;
    this.logger.log(`[transmuxer.ts]: Flushed ${this.id} sn: ${i.sn}${i.part > -1 ? " part: " + i.part : ""} of ${this.id === K.MAIN ? "level" : "track"} ${i.level}`);
    const h = this.remuxer.remux(s, r, a, o, l, c, !0, this.id);
    t.push({
      remuxResult: h,
      chunkMeta: i
    }), i.transmuxing.executeEnd = re();
  }
  resetInitialTimestamp(t) {
    const {
      demuxer: e,
      remuxer: i
    } = this;
    !e || !i || (e.resetTimeStamp(t), i.resetTimeStamp(t));
  }
  resetContiguity() {
    const {
      demuxer: t,
      remuxer: e
    } = this;
    !t || !e || (t.resetContiguity(), e.resetNextTimestamp());
  }
  resetInitSegment(t, e, i, s, r) {
    const {
      demuxer: a,
      remuxer: o
    } = this;
    !a || !o || (a.resetInitSegment(t, e, i, s), o.resetInitSegment(t, e, i, r));
  }
  destroy() {
    this.demuxer && (this.demuxer.destroy(), this.demuxer = void 0), this.remuxer && (this.remuxer.destroy(), this.remuxer = void 0);
  }
  transmux(t, e, i, s, r) {
    let a;
    return e && e.method === "SAMPLE-AES" ? a = this.transmuxSampleAes(t, e, i, s, r) : a = this.transmuxUnencrypted(t, i, s, r), a;
  }
  transmuxUnencrypted(t, e, i, s) {
    const {
      audioTrack: r,
      videoTrack: a,
      id3Track: o,
      textTrack: c
    } = this.demuxer.demux(t, e, !1, !this.config.progressive);
    return {
      remuxResult: this.remuxer.remux(r, a, o, c, e, i, !1, this.id),
      chunkMeta: s
    };
  }
  transmuxSampleAes(t, e, i, s, r) {
    return this.demuxer.demuxSampleAes(t, e, i).then((a) => ({
      remuxResult: this.remuxer.remux(a.audioTrack, a.videoTrack, a.id3Track, a.textTrack, i, s, !1, this.id),
      chunkMeta: r
    }));
  }
  configureTransmuxer(t) {
    const {
      config: e,
      observer: i,
      typeSupported: s
    } = this;
    let r;
    for (let d = 0, u = Wi.length; d < u; d++) {
      var a;
      if ((a = Wi[d].demux) != null && a.probe(t, this.logger)) {
        r = Wi[d];
        break;
      }
    }
    if (!r)
      return new Error("Failed to find demuxer by probing fragment data");
    const o = this.demuxer, c = this.remuxer, l = r.remux, h = r.demux;
    (!c || !(c instanceof l)) && (this.remuxer = new l(i, e, s, this.logger)), (!o || !(o instanceof h)) && (this.demuxer = new h(i, e, s, this.logger), this.probe = h.probe);
  }
  needsProbing(t, e) {
    return !this.demuxer || !this.remuxer || t || e;
  }
  getDecrypter() {
    let t = this.decrypter;
    return t || (t = this.decrypter = new Ar(this.config)), t;
  }
}
function ad(n, t) {
  let e = null;
  return n.byteLength > 0 && (t == null ? void 0 : t.key) != null && t.iv !== null && t.method != null && (e = t), e;
}
const Cs = (n) => ({
  remuxResult: {},
  chunkMeta: n
});
function Ei(n) {
  return "then" in n && n.then instanceof Function;
}
class od {
  constructor(t, e, i, s, r) {
    this.audioCodec = void 0, this.videoCodec = void 0, this.initSegmentData = void 0, this.duration = void 0, this.defaultInitPts = void 0, this.audioCodec = t, this.videoCodec = e, this.initSegmentData = i, this.duration = s, this.defaultInitPts = r || null;
  }
}
class ld {
  constructor(t, e, i, s, r, a) {
    this.discontinuity = void 0, this.contiguous = void 0, this.accurateTimeOffset = void 0, this.trackSwitch = void 0, this.timeOffset = void 0, this.initSegmentChange = void 0, this.discontinuity = t, this.contiguous = e, this.accurateTimeOffset = i, this.trackSwitch = s, this.timeOffset = r, this.initSegmentChange = a;
  }
}
let Gn = 0;
class To {
  constructor(t, e, i, s) {
    this.error = null, this.hls = void 0, this.id = void 0, this.instanceNo = Gn++, this.observer = void 0, this.frag = null, this.part = null, this.useWorker = void 0, this.workerContext = null, this.transmuxer = null, this.onTransmuxComplete = void 0, this.onFlush = void 0, this.onWorkerMessage = (c) => {
      const l = c.data, h = this.hls;
      if (!(!h || !(l != null && l.event) || l.instanceNo !== this.instanceNo))
        switch (l.event) {
          case "init": {
            var d;
            const u = (d = this.workerContext) == null ? void 0 : d.objectURL;
            u && self.URL.revokeObjectURL(u);
            break;
          }
          case "transmuxComplete": {
            this.handleTransmuxComplete(l.data);
            break;
          }
          case "flush": {
            this.onFlush(l.data);
            break;
          }
          // pass logs from the worker thread to the main logger
          case "workerLog": {
            h.logger[l.data.logType] && h.logger[l.data.logType](l.data.message);
            break;
          }
          default: {
            l.data = l.data || {}, l.data.frag = this.frag, l.data.part = this.part, l.data.id = this.id, h.trigger(l.event, l.data);
            break;
          }
        }
    }, this.onWorkerError = (c) => {
      if (!this.hls)
        return;
      const l = new Error(`${c.message}  (${c.filename}:${c.lineno})`);
      this.hls.config.enableWorker = !1, this.hls.logger.warn(`Error in "${this.id}" Web Worker, fallback to inline`), this.hls.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.INTERNAL_EXCEPTION,
        fatal: !1,
        event: "demuxerWorker",
        error: l
      });
    };
    const r = t.config;
    this.hls = t, this.id = e, this.useWorker = !!r.enableWorker, this.onTransmuxComplete = i, this.onFlush = s;
    const a = (c, l) => {
      l = l || {}, l.frag = this.frag || void 0, c === m.ERROR && (l = l, l.parent = this.id, l.part = this.part, this.error = l.error), this.hls.trigger(c, l);
    };
    this.observer = new _r(), this.observer.on(m.FRAG_DECRYPTED, a), this.observer.on(m.ERROR, a);
    const o = en(r.preferManagedMediaSource);
    if (this.useWorker && typeof Worker < "u") {
      const c = this.hls.logger;
      if (r.workerPath || uh()) {
        try {
          r.workerPath ? (c.log(`loading Web Worker ${r.workerPath} for "${e}"`), this.workerContext = gh(r.workerPath)) : (c.log(`injecting Web Worker for "${e}"`), this.workerContext = fh());
          const {
            worker: h
          } = this.workerContext;
          h.addEventListener("message", this.onWorkerMessage), h.addEventListener("error", this.onWorkerError), h.postMessage({
            instanceNo: this.instanceNo,
            cmd: "init",
            typeSupported: o,
            id: e,
            config: ot(r)
          });
        } catch (h) {
          c.warn(`Error setting up "${e}" Web Worker, fallback to inline`, h), this.terminateWorker(), this.error = null, this.transmuxer = new Un(this.observer, o, r, "", e, t.logger);
        }
        return;
      }
    }
    this.transmuxer = new Un(this.observer, o, r, "", e, t.logger);
  }
  reset() {
    if (this.frag = null, this.part = null, this.workerContext) {
      const t = this.instanceNo;
      this.instanceNo = Gn++;
      const e = this.hls.config, i = en(e.preferManagedMediaSource);
      this.workerContext.worker.postMessage({
        instanceNo: this.instanceNo,
        cmd: "reset",
        resetNo: t,
        typeSupported: i,
        id: this.id,
        config: ot(e)
      });
    }
  }
  terminateWorker() {
    if (this.workerContext) {
      const {
        worker: t
      } = this.workerContext;
      this.workerContext = null, t.removeEventListener("message", this.onWorkerMessage), t.removeEventListener("error", this.onWorkerError), mh(this.hls.config.workerPath);
    }
  }
  destroy() {
    if (this.workerContext)
      this.terminateWorker(), this.onWorkerMessage = this.onWorkerError = null;
    else {
      const e = this.transmuxer;
      e && (e.destroy(), this.transmuxer = null);
    }
    const t = this.observer;
    t && t.removeAllListeners(), this.frag = null, this.part = null, this.observer = null, this.hls = null;
  }
  push(t, e, i, s, r, a, o, c, l, h) {
    var d, u;
    l.transmuxing.start = self.performance.now();
    const {
      instanceNo: f,
      transmuxer: g
    } = this, v = a ? a.start : r.start, p = r.decryptdata, y = this.frag, E = !(y && r.cc === y.cc), T = !(y && l.level === y.level), S = y ? l.sn - y.sn : -1, x = this.part ? l.part - this.part.index : -1, D = S === 0 && l.id > 1 && l.id === (y == null ? void 0 : y.stats.chunkCount), A = !T && (S === 1 || S === 0 && (x === 1 || D && x <= 0)), _ = self.performance.now();
    (T || S || r.stats.parsing.start === 0) && (r.stats.parsing.start = _), a && (x || !A) && (a.stats.parsing.start = _);
    const R = !(y && ((d = r.initSegment) == null ? void 0 : d.url) === ((u = y.initSegment) == null ? void 0 : u.url)), b = new ld(E, A, c, T, v, R);
    if (!A || E || R) {
      this.hls.logger.log(`[transmuxer-interface]: Starting new transmux session for ${r.type} sn: ${l.sn}${l.part > -1 ? " part: " + l.part : ""} ${this.id === K.MAIN ? "level" : "track"}: ${l.level} id: ${l.id}
        discontinuity: ${E}
        trackSwitch: ${T}
        contiguous: ${A}
        accurateTimeOffset: ${c}
        timeOffset: ${v}
        initSegmentChange: ${R}`);
      const C = new od(i, s, e, o, h);
      this.configureTransmuxer(C);
    }
    if (this.frag = r, this.part = a, this.workerContext)
      this.workerContext.worker.postMessage({
        instanceNo: f,
        cmd: "demux",
        data: t,
        decryptdata: p,
        chunkMeta: l,
        state: b
      }, t instanceof ArrayBuffer ? [t] : []);
    else if (g) {
      const C = g.push(t, p, l, b);
      Ei(C) ? C.then((F) => {
        this.handleTransmuxComplete(F);
      }).catch((F) => {
        this.transmuxerError(F, l, "transmuxer-interface push error");
      }) : this.handleTransmuxComplete(C);
    }
  }
  flush(t) {
    t.transmuxing.start = self.performance.now();
    const {
      instanceNo: e,
      transmuxer: i
    } = this;
    if (this.workerContext)
      this.workerContext.worker.postMessage({
        instanceNo: e,
        cmd: "flush",
        chunkMeta: t
      });
    else if (i) {
      const s = i.flush(t);
      Ei(s) ? s.then((r) => {
        this.handleFlushResult(r, t);
      }).catch((r) => {
        this.transmuxerError(r, t, "transmuxer-interface flush error");
      }) : this.handleFlushResult(s, t);
    }
  }
  transmuxerError(t, e, i) {
    this.hls && (this.error = t, this.hls.trigger(m.ERROR, {
      type: Y.MEDIA_ERROR,
      details: L.FRAG_PARSING_ERROR,
      chunkMeta: e,
      frag: this.frag || void 0,
      part: this.part || void 0,
      fatal: !1,
      error: t,
      err: t,
      reason: i
    }));
  }
  handleFlushResult(t, e) {
    t.forEach((i) => {
      this.handleTransmuxComplete(i);
    }), this.onFlush(e);
  }
  configureTransmuxer(t) {
    const {
      instanceNo: e,
      transmuxer: i
    } = this;
    this.workerContext ? this.workerContext.worker.postMessage({
      instanceNo: e,
      cmd: "configure",
      config: t
    }) : i && i.configure(t);
  }
  handleTransmuxComplete(t) {
    t.chunkMeta.transmuxing.end = self.performance.now(), this.onTransmuxComplete(t);
  }
}
const Kn = 100;
class cd extends Rr {
  constructor(t, e, i) {
    super(t, e, i, "audio-stream-controller", K.AUDIO), this.mainAnchor = null, this.mainFragLoading = null, this.audioOnly = !1, this.bufferedTrack = null, this.switchingTrack = null, this.trackId = -1, this.waitingData = null, this.mainDetails = null, this.flushing = !1, this.bufferFlushed = !1, this.cachedTrackLoadedData = null, this.registerListeners();
  }
  onHandlerDestroying() {
    this.unregisterListeners(), super.onHandlerDestroying(), this.resetItem();
  }
  resetItem() {
    this.mainDetails = this.mainAnchor = this.mainFragLoading = this.bufferedTrack = this.switchingTrack = this.waitingData = this.cachedTrackLoadedData = null;
  }
  registerListeners() {
    super.registerListeners();
    const {
      hls: t
    } = this;
    t.on(m.LEVEL_LOADED, this.onLevelLoaded, this), t.on(m.AUDIO_TRACKS_UPDATED, this.onAudioTracksUpdated, this), t.on(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.on(m.AUDIO_TRACK_LOADED, this.onAudioTrackLoaded, this), t.on(m.BUFFER_RESET, this.onBufferReset, this), t.on(m.BUFFER_CREATED, this.onBufferCreated, this), t.on(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.on(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.on(m.INIT_PTS_FOUND, this.onInitPtsFound, this), t.on(m.FRAG_LOADING, this.onFragLoading, this), t.on(m.FRAG_BUFFERED, this.onFragBuffered, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (super.unregisterListeners(), t.off(m.LEVEL_LOADED, this.onLevelLoaded, this), t.off(m.AUDIO_TRACKS_UPDATED, this.onAudioTracksUpdated, this), t.off(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.off(m.AUDIO_TRACK_LOADED, this.onAudioTrackLoaded, this), t.off(m.BUFFER_RESET, this.onBufferReset, this), t.off(m.BUFFER_CREATED, this.onBufferCreated, this), t.off(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.off(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.off(m.INIT_PTS_FOUND, this.onInitPtsFound, this), t.off(m.FRAG_LOADING, this.onFragLoading, this), t.off(m.FRAG_BUFFERED, this.onFragBuffered, this));
  }
  // INIT_PTS_FOUND is triggered when the video track parsed in the stream-controller has a new PTS value
  onInitPtsFound(t, {
    frag: e,
    id: i,
    initPTS: s,
    timescale: r,
    trackId: a
  }) {
    if (i === K.MAIN) {
      const o = e.cc, c = this.fragCurrent;
      if (this.initPTS[o] = {
        baseTime: s,
        timescale: r,
        trackId: a
      }, this.log(`InitPTS for cc: ${o} found from main: ${s / r} (${s}/${r}) trackId: ${a}`), this.mainAnchor = e, this.state === w.WAITING_INIT_PTS) {
        const l = this.waitingData;
        (!l && !this.loadingParts || l && l.frag.cc !== o) && this.syncWithAnchor(e, l == null ? void 0 : l.frag);
      } else !this.hls.hasEnoughToStart && c && c.cc !== o ? (c.abortRequests(), this.syncWithAnchor(e, c)) : this.state === w.IDLE && this.tick();
    }
  }
  getLoadPosition() {
    return !this.startFragRequested && this.nextLoadPosition >= 0 ? this.nextLoadPosition : super.getLoadPosition();
  }
  syncWithAnchor(t, e) {
    var i;
    const s = ((i = this.mainFragLoading) == null ? void 0 : i.frag) || null;
    if (e && (s == null ? void 0 : s.cc) === e.cc)
      return;
    const r = (s || t).cc, a = this.getLevelDetails(), o = this.getLoadPosition(), c = Ma(a, r, o);
    c && (this.log(`Syncing with main frag at ${c.start} cc ${c.cc}`), this.startFragRequested = !1, this.nextLoadPosition = c.start, this.resetLoadingState(), this.state === w.IDLE && this.doTickIdle());
  }
  startLoad(t, e) {
    if (!this.levels) {
      this.startPosition = t, this.state = w.STOPPED;
      return;
    }
    const i = this.lastCurrentTime;
    this.stopLoad(), this.setInterval(Kn), i > 0 && t === -1 ? (this.log(`Override startPosition with lastCurrentTime @${i.toFixed(3)}`), t = i, this.state = w.IDLE) : this.state = w.WAITING_TRACK, this.nextLoadPosition = this.lastCurrentTime = t + this.timelineOffset, this.startPosition = e ? -1 : t, this.tick();
  }
  doTick() {
    switch (this.state) {
      case w.IDLE:
        this.doTickIdle();
        break;
      case w.WAITING_TRACK: {
        const {
          levels: t,
          trackId: e
        } = this, i = t == null ? void 0 : t[e], s = i == null ? void 0 : i.details;
        if (s && !this.waitForLive(i)) {
          if (this.waitForCdnTuneIn(s))
            break;
          this.state = w.WAITING_INIT_PTS;
        }
        break;
      }
      case w.FRAG_LOADING_WAITING_RETRY: {
        this.checkRetryDate();
        break;
      }
      case w.WAITING_INIT_PTS: {
        const t = this.waitingData;
        if (t) {
          const {
            frag: e,
            part: i,
            cache: s,
            complete: r
          } = t, a = this.mainAnchor;
          if (this.initPTS[e.cc] !== void 0) {
            this.waitingData = null, this.state = w.FRAG_LOADING;
            const o = s.flush().buffer, c = {
              frag: e,
              part: i,
              payload: o,
              networkDetails: null
            };
            this._handleFragmentLoadProgress(c), r && super._handleFragmentLoadComplete(c);
          } else a && a.cc !== t.frag.cc && this.syncWithAnchor(a, t.frag);
        } else
          this.state = w.IDLE;
      }
    }
    this.onTickEnd();
  }
  resetLoadingState() {
    const t = this.waitingData;
    t && (this.fragmentTracker.removeFragment(t.frag), this.waitingData = null), super.resetLoadingState();
  }
  onTickEnd() {
    const {
      media: t
    } = this;
    t != null && t.readyState && (this.lastCurrentTime = t.currentTime);
  }
  doTickIdle() {
    var t;
    const {
      hls: e,
      levels: i,
      media: s,
      trackId: r
    } = this, a = e.config;
    if (!this.buffering || !s && !this.primaryPrefetch && (this.startFragRequested || !a.startFragPrefetch) || !(i != null && i[r]))
      return;
    const o = i[r], c = o.details;
    if (!c || this.waitForLive(o) || this.waitForCdnTuneIn(c)) {
      this.state = w.WAITING_TRACK, this.startFragRequested = !1;
      return;
    }
    const l = this.mediaBuffer ? this.mediaBuffer : this.media;
    this.bufferFlushed && l && (this.bufferFlushed = !1, this.afterBufferFlushed(l, at.AUDIO, K.AUDIO));
    const h = this.getFwdBufferInfo(l, K.AUDIO);
    if (h === null)
      return;
    if (!this.switchingTrack && this._streamEnded(h, c)) {
      e.trigger(m.BUFFER_EOS, {
        type: "audio"
      }), this.state = w.ENDED;
      return;
    }
    const d = h.len, u = e.maxBufferLength, f = c.fragments, g = f[0].start, v = this.getLoadPosition(), p = this.flushing ? v : h.end;
    if (this.switchingTrack && s) {
      const T = v;
      c.PTSKnown && T < g && (h.end > g || h.nextStart) && (this.log("Alt audio track ahead of main track, seek to start of alt audio track"), s.currentTime = g + 0.05);
    }
    if (d >= u && !this.switchingTrack && p < f[f.length - 1].start)
      return;
    let y = this.getNextFragment(p, c);
    if (y && this.isLoopLoading(y, p) && (y = this.getNextFragmentLoopLoading(y, c, h, K.MAIN, u)), !y) {
      this.bufferFlushed = !0;
      return;
    }
    let E = ((t = this.mainFragLoading) == null ? void 0 : t.frag) || null;
    if (!this.audioOnly && this.startFragRequested && E && ut(y) && !y.endList && (!c.live || !this.loadingParts && p < this.hls.liveSyncPosition) && (this.fragmentTracker.getState(E) === yt.OK && (this.mainFragLoading = E = null), E && ut(E))) {
      if (y.start > E.end) {
        const S = this.fragmentTracker.getFragAtPos(p, K.MAIN);
        S && S.end > E.end && (E = S, this.mainFragLoading = {
          frag: S,
          targetBufferTime: null
        });
      }
      if (y.start > E.end)
        return;
    }
    this.loadFragment(y, o, p);
  }
  onMediaDetaching(t, e) {
    this.bufferFlushed = this.flushing = !1, super.onMediaDetaching(t, e);
  }
  onAudioTracksUpdated(t, {
    audioTracks: e
  }) {
    this.resetTransmuxer(), this.levels = e.map((i) => new pi(i));
  }
  onAudioTrackSwitching(t, e) {
    const i = !!e.url;
    this.trackId = e.id;
    const {
      fragCurrent: s
    } = this;
    s && (s.abortRequests(), this.removeUnbufferedFrags(s.start)), this.resetLoadingState(), i ? (this.switchingTrack = e, this.flushAudioIfNeeded(e), this.state !== w.STOPPED && (this.setInterval(Kn), this.state = w.IDLE, this.tick())) : (this.resetTransmuxer(), this.switchingTrack = null, this.bufferedTrack = e, this.clearInterval());
  }
  onManifestLoading() {
    super.onManifestLoading(), this.bufferFlushed = this.flushing = this.audioOnly = !1, this.resetItem(), this.trackId = -1;
  }
  onLevelLoaded(t, e) {
    this.mainDetails = e.details;
    const i = this.cachedTrackLoadedData;
    i && (this.cachedTrackLoadedData = null, this.onAudioTrackLoaded(m.AUDIO_TRACK_LOADED, i));
  }
  onAudioTrackLoaded(t, e) {
    var i;
    const {
      levels: s
    } = this, {
      details: r,
      id: a,
      groupId: o,
      track: c
    } = e;
    if (!s) {
      this.warn(`Audio tracks reset while loading track ${a} "${c.name}" of "${o}"`);
      return;
    }
    const l = this.mainDetails;
    if (!l || r.endCC > l.endCC || l.expired) {
      this.cachedTrackLoadedData = e, this.state !== w.STOPPED && (this.state = w.WAITING_TRACK);
      return;
    }
    this.cachedTrackLoadedData = null, this.log(`Audio track ${a} "${c.name}" of "${o}" loaded [${r.startSN},${r.endSN}]${r.lastPartSn ? `[part-${r.lastPartSn}-${r.lastPartIndex}]` : ""},duration:${r.totalduration}`);
    const h = s[a];
    let d = 0;
    if (r.live || (i = h.details) != null && i.live) {
      if (this.checkLiveUpdate(r), r.deltaUpdateFailed)
        return;
      if (h.details) {
        var u;
        d = this.alignPlaylists(r, h.details, (u = this.levelLastLoaded) == null ? void 0 : u.details);
      }
      r.alignedSliding || (Ja(r, l), r.alignedSliding || ns(r, l), d = r.fragmentStart);
    }
    h.details = r, this.levelLastLoaded = h, this.startFragRequested || this.setStartPosition(l, d), this.hls.trigger(m.AUDIO_TRACK_UPDATED, {
      details: r,
      id: a,
      groupId: e.groupId
    }), this.state === w.WAITING_TRACK && !this.waitForCdnTuneIn(r) && (this.state = w.IDLE), this.tick();
  }
  _handleFragmentLoadProgress(t) {
    var e;
    const i = t.frag, {
      part: s,
      payload: r
    } = t, {
      config: a,
      trackId: o,
      levels: c
    } = this;
    if (!c) {
      this.warn(`Audio tracks were reset while fragment load was in progress. Fragment ${i.sn} of level ${i.level} will not be buffered`);
      return;
    }
    const l = c[o];
    if (!l) {
      this.warn("Audio track is undefined on fragment load progress");
      return;
    }
    const h = l.details;
    if (!h) {
      this.warn("Audio track details undefined on fragment load progress"), this.removeUnbufferedFrags(i.start);
      return;
    }
    const d = a.defaultAudioCodec || l.audioCodec || "mp4a.40.2";
    let u = this.transmuxer;
    u || (u = this.transmuxer = new To(this.hls, K.AUDIO, this._handleTransmuxComplete.bind(this), this._handleTransmuxerFlush.bind(this)));
    const f = this.initPTS[i.cc], g = (e = i.initSegment) == null ? void 0 : e.data;
    if (f !== void 0) {
      const p = s ? s.index : -1, y = p !== -1, E = new br(i.level, i.sn, i.stats.chunkCount, r.byteLength, p, y);
      u.push(r, g, d, "", i, s, h.totalduration, !1, E, f);
    } else {
      this.log(`Unknown video PTS for cc ${i.cc}, waiting for video PTS before demuxing audio frag ${i.sn} of [${h.startSN} ,${h.endSN}],track ${o}`);
      const {
        cache: v
      } = this.waitingData = this.waitingData || {
        frag: i,
        part: s,
        cache: new to(),
        complete: !1
      };
      v.push(new Uint8Array(r)), this.state !== w.STOPPED && (this.state = w.WAITING_INIT_PTS);
    }
  }
  _handleFragmentLoadComplete(t) {
    if (this.waitingData) {
      this.waitingData.complete = !0;
      return;
    }
    super._handleFragmentLoadComplete(t);
  }
  onBufferReset() {
    this.mediaBuffer = null;
  }
  onBufferCreated(t, e) {
    this.bufferFlushed = this.flushing = !1;
    const i = e.tracks.audio;
    i && (this.mediaBuffer = i.buffer || null);
  }
  onFragLoading(t, e) {
    !this.audioOnly && e.frag.type === K.MAIN && ut(e.frag) && (this.mainFragLoading = e, this.state === w.IDLE && this.tick());
  }
  onFragBuffered(t, e) {
    const {
      frag: i,
      part: s
    } = e;
    if (i.type !== K.AUDIO) {
      !this.audioOnly && i.type === K.MAIN && !i.elementaryStreams.video && !i.elementaryStreams.audiovideo && (this.audioOnly = !0, this.mainFragLoading = null);
      return;
    }
    if (this.fragContextChanged(i)) {
      this.warn(`Fragment ${i.sn}${s ? " p: " + s.index : ""} of level ${i.level} finished buffering, but was aborted. state: ${this.state}, audioSwitch: ${this.switchingTrack ? this.switchingTrack.name : "false"}`);
      return;
    }
    if (ut(i)) {
      this.fragPrevious = i;
      const r = this.switchingTrack;
      r && (this.bufferedTrack = r, this.switchingTrack = null, this.hls.trigger(m.AUDIO_TRACK_SWITCHED, st({}, r)));
    }
    this.fragBufferedComplete(i, s), this.media && this.tick();
  }
  onError(t, e) {
    var i;
    if (e.fatal) {
      this.state = w.ERROR;
      return;
    }
    switch (e.details) {
      case L.FRAG_GAP:
      case L.FRAG_PARSING_ERROR:
      case L.FRAG_DECRYPT_ERROR:
      case L.FRAG_LOAD_ERROR:
      case L.FRAG_LOAD_TIMEOUT:
      case L.KEY_LOAD_ERROR:
      case L.KEY_LOAD_TIMEOUT:
        this.onFragmentOrKeyLoadError(K.AUDIO, e);
        break;
      case L.AUDIO_TRACK_LOAD_ERROR:
      case L.AUDIO_TRACK_LOAD_TIMEOUT:
      case L.LEVEL_PARSING_ERROR:
        !e.levelRetry && this.state === w.WAITING_TRACK && ((i = e.context) == null ? void 0 : i.type) === tt.AUDIO_TRACK && (this.state = w.IDLE);
        break;
      case L.BUFFER_ADD_CODEC_ERROR:
      case L.BUFFER_APPEND_ERROR:
        if (e.parent !== "audio")
          return;
        this.reduceLengthAndFlushBuffer(e) || this.resetLoadingState();
        break;
      case L.BUFFER_FULL_ERROR:
        if (e.parent !== "audio")
          return;
        this.reduceLengthAndFlushBuffer(e) && (this.bufferedTrack = null, super.flushMainBuffer(0, Number.POSITIVE_INFINITY, "audio"));
        break;
      case L.INTERNAL_EXCEPTION:
        this.recoverWorkerError(e);
        break;
    }
  }
  onBufferFlushing(t, {
    type: e
  }) {
    e !== at.VIDEO && (this.flushing = !0);
  }
  onBufferFlushed(t, {
    type: e
  }) {
    if (e !== at.VIDEO) {
      this.flushing = !1, this.bufferFlushed = !0, this.state === w.ENDED && (this.state = w.IDLE);
      const i = this.mediaBuffer || this.media;
      i && (this.afterBufferFlushed(i, e, K.AUDIO), this.tick());
    }
  }
  _handleTransmuxComplete(t) {
    var e;
    const i = "audio", {
      hls: s
    } = this, {
      remuxResult: r,
      chunkMeta: a
    } = t, o = this.getCurrentContext(a);
    if (!o) {
      this.resetWhenMissingContext(a);
      return;
    }
    const {
      frag: c,
      part: l,
      level: h
    } = o, {
      details: d
    } = h, {
      audio: u,
      text: f,
      id3: g,
      initSegment: v
    } = r;
    if (this.fragContextChanged(c) || !d) {
      this.fragmentTracker.removeFragment(c);
      return;
    }
    if (this.state = w.PARSING, this.switchingTrack && u && this.completeAudioSwitch(this.switchingTrack), v != null && v.tracks) {
      const p = c.initSegment || c;
      if (this.unhandledEncryptionError(v, c))
        return;
      this._bufferInitSegment(h, v.tracks, p, a), s.trigger(m.FRAG_PARSING_INIT_SEGMENT, {
        frag: p,
        id: i,
        tracks: v.tracks
      });
    }
    if (u) {
      const {
        startPTS: p,
        endPTS: y,
        startDTS: E,
        endDTS: T
      } = u;
      l && (l.elementaryStreams[at.AUDIO] = {
        startPTS: p,
        endPTS: y,
        startDTS: E,
        endDTS: T
      }), c.setElementaryStreamInfo(at.AUDIO, p, y, E, T), this.bufferFragmentData(u, c, l, a);
    }
    if (g != null && (e = g.samples) != null && e.length) {
      const p = nt({
        id: i,
        frag: c,
        details: d
      }, g);
      s.trigger(m.FRAG_PARSING_METADATA, p);
    }
    if (f) {
      const p = nt({
        id: i,
        frag: c,
        details: d
      }, f);
      s.trigger(m.FRAG_PARSING_USERDATA, p);
    }
  }
  _bufferInitSegment(t, e, i, s) {
    if (this.state !== w.PARSING || (e.video && delete e.video, e.audiovideo && delete e.audiovideo, !e.audio))
      return;
    const r = e.audio;
    r.id = K.AUDIO;
    const a = t.audioCodec;
    this.log(`Init audio buffer, container:${r.container}, codecs[level/parsed]=[${a}/${r.codec}]`), a && a.split(",").length === 1 && (r.levelCodec = a), this.hls.trigger(m.BUFFER_CODECS, e);
    const o = r.initSegment;
    if (o != null && o.byteLength) {
      const c = {
        type: "audio",
        frag: i,
        part: null,
        chunkMeta: s,
        parent: i.type,
        data: o
      };
      this.hls.trigger(m.BUFFER_APPENDING, c);
    }
    this.tickImmediate();
  }
  loadFragment(t, e, i) {
    const s = this.fragmentTracker.getState(t);
    if (this.switchingTrack || s === yt.NOT_LOADED || s === yt.PARTIAL) {
      var r;
      if (!ut(t))
        this._loadInitSegment(t, e);
      else if ((r = e.details) != null && r.live && !this.initPTS[t.cc]) {
        this.log(`Waiting for video PTS in continuity counter ${t.cc} of live stream before loading audio fragment ${t.sn} of level ${this.trackId}`), this.state = w.WAITING_INIT_PTS;
        const a = this.mainDetails;
        a && a.fragmentStart !== e.details.fragmentStart && ns(e.details, a);
      } else
        super.loadFragment(t, e, i);
    } else
      this.clearTrackerIfNeeded(t);
  }
  flushAudioIfNeeded(t) {
    if (this.media && this.bufferedTrack) {
      const {
        name: e,
        lang: i,
        assocLang: s,
        characteristics: r,
        audioCodec: a,
        channels: o
      } = this.bufferedTrack;
      _e({
        name: e,
        lang: i,
        assocLang: s,
        characteristics: r,
        audioCodec: a,
        channels: o
      }, t, Ie) || (ts(t.url, this.hls) ? (this.log("Switching audio track : flushing all audio"), super.flushMainBuffer(0, Number.POSITIVE_INFINITY, "audio"), this.bufferedTrack = null) : this.bufferedTrack = t);
    }
  }
  completeAudioSwitch(t) {
    const {
      hls: e
    } = this;
    this.flushAudioIfNeeded(t), this.bufferedTrack = t, this.switchingTrack = null, e.trigger(m.AUDIO_TRACK_SWITCHED, st({}, t));
  }
}
class Mr extends Bt {
  constructor(t, e) {
    super(e, t.logger), this.hls = void 0, this.canLoad = !1, this.timer = -1, this.hls = t;
  }
  destroy() {
    this.clearTimer(), this.hls = this.log = this.warn = null;
  }
  clearTimer() {
    this.timer !== -1 && (self.clearTimeout(this.timer), this.timer = -1);
  }
  startLoad() {
    this.canLoad = !0, this.loadPlaylist();
  }
  stopLoad() {
    this.canLoad = !1, this.clearTimer();
  }
  switchParams(t, e, i) {
    const s = e == null ? void 0 : e.renditionReports;
    if (s) {
      let r = -1;
      for (let a = 0; a < s.length; a++) {
        const o = s[a];
        let c;
        try {
          c = new self.URL(o.URI, e.url).href;
        } catch (l) {
          this.warn(`Could not construct new URL for Rendition Report: ${l}`), c = o.URI || "";
        }
        if (c === t) {
          r = a;
          break;
        } else c === t.substring(0, c.length) && (r = a);
      }
      if (r !== -1) {
        const a = s[r], o = parseInt(a["LAST-MSN"]) || e.lastPartSn;
        let c = parseInt(a["LAST-PART"]) || e.lastPartIndex;
        if (this.hls.config.lowLatencyMode) {
          const h = Math.min(e.age - e.partTarget, e.targetduration);
          c >= 0 && h > e.partTarget && (c += 1);
        }
        const l = i && sn(i);
        return new rn(o, c >= 0 ? c : void 0, l);
      }
    }
  }
  loadPlaylist(t) {
    this.clearTimer();
  }
  loadingPlaylist(t, e) {
    this.clearTimer();
  }
  shouldLoadPlaylist(t) {
    return this.canLoad && !!t && !!t.url && (!t.details || t.details.live);
  }
  getUrlWithDirectives(t, e) {
    if (e)
      try {
        return e.addDirectives(t);
      } catch (i) {
        this.warn(`Could not construct new URL with HLS Delivery Directives: ${i}`);
      }
    return t;
  }
  playlistLoaded(t, e, i) {
    const {
      details: s,
      stats: r
    } = e, a = self.performance.now(), o = r.loading.first ? Math.max(0, a - r.loading.first) : 0;
    s.advancedDateTime = Date.now() - o;
    const c = this.hls.config.timelineOffset;
    if (c !== s.appliedTimelineOffset) {
      const h = Math.max(c || 0, 0);
      s.appliedTimelineOffset = h, s.fragments.forEach((d) => {
        d.setStart(d.playlistOffset + h);
      });
    }
    if (s.live || i != null && i.live) {
      const h = "levelInfo" in e ? e.levelInfo : e.track;
      if (s.reloaded(i), i && s.fragments.length > 0) {
        eh(i, s, this);
        const E = s.playlistParsingError;
        if (E) {
          this.warn(E);
          const T = this.hls;
          if (!T.config.ignorePlaylistParsingErrors) {
            var l;
            const {
              networkDetails: S
            } = e;
            T.trigger(m.ERROR, {
              type: Y.NETWORK_ERROR,
              details: L.LEVEL_PARSING_ERROR,
              fatal: !1,
              url: s.url,
              error: E,
              reason: E.message,
              level: e.level || void 0,
              parent: (l = s.fragments[0]) == null ? void 0 : l.type,
              networkDetails: S,
              stats: r
            });
            return;
          }
          s.playlistParsingError = null;
        }
      }
      s.requestScheduled === -1 && (s.requestScheduled = r.loading.start);
      const d = this.hls.mainForwardBufferInfo, u = d ? d.end - d.len : 0, f = (s.edge - u) * 1e3, g = ja(s, f);
      if (s.requestScheduled + g < a ? s.requestScheduled = a : s.requestScheduled += g, this.log(`live playlist ${t} ${s.advanced ? "REFRESHED " + s.lastPartSn + "-" + s.lastPartIndex : s.updated ? "UPDATED" : "MISSED"}`), !this.canLoad || !s.live)
        return;
      let v, p, y;
      if (s.canBlockReload && s.endSN && s.advanced) {
        const E = this.hls.config.lowLatencyMode, T = s.lastPartSn, S = s.endSN, x = s.lastPartIndex, D = x !== -1, A = T === S;
        D ? A ? (p = S + 1, y = E ? 0 : x) : (p = T, y = E ? x + 1 : s.maxPartIndex) : p = S + 1;
        const _ = s.age, R = _ + s.ageHeader;
        let b = Math.min(R - s.partTarget, s.targetduration * 1.5);
        if (b > 0) {
          if (R > s.targetduration * 3)
            this.log(`Playlist last advanced ${_.toFixed(2)}s ago. Omitting segment and part directives.`), p = void 0, y = void 0;
          else if (i != null && i.tuneInGoal && R - s.partTarget > i.tuneInGoal)
            this.warn(`CDN Tune-in goal increased from: ${i.tuneInGoal} to: ${b} with playlist age: ${s.age}`), b = 0;
          else {
            const C = Math.floor(b / s.targetduration);
            if (p += C, y !== void 0) {
              const F = Math.round(b % s.targetduration / s.partTarget);
              y += F;
            }
            this.log(`CDN Tune-in age: ${s.ageHeader}s last advanced ${_.toFixed(2)}s goal: ${b} skip sn ${C} to part ${y}`);
          }
          s.tuneInGoal = b;
        }
        if (v = this.getDeliveryDirectives(s, e.deliveryDirectives, p, y), E || !A) {
          s.requestScheduled = a, this.loadingPlaylist(h, v);
          return;
        }
      } else (s.canBlockReload || s.canSkipUntil) && (v = this.getDeliveryDirectives(s, e.deliveryDirectives, p, y));
      v && p !== void 0 && s.canBlockReload && (s.requestScheduled = r.loading.first + Math.max(g - o * 2, g / 2)), this.scheduleLoading(h, v, s);
    } else
      this.clearTimer();
  }
  scheduleLoading(t, e, i) {
    const s = i || t.details;
    if (!s) {
      this.loadingPlaylist(t, e);
      return;
    }
    const r = self.performance.now(), a = s.requestScheduled;
    if (r >= a) {
      this.loadingPlaylist(t, e);
      return;
    }
    const o = a - r;
    this.log(`reload live playlist ${t.name || t.bitrate + "bps"} in ${Math.round(o)} ms`), this.clearTimer(), this.timer = self.setTimeout(() => this.loadingPlaylist(t, e), o);
  }
  getDeliveryDirectives(t, e, i, s) {
    let r = sn(t);
    return e != null && e.skip && t.deltaUpdateFailed && (i = e.msn, s = e.part, r = Ki.No), new rn(i, s, r);
  }
  checkRetry(t) {
    const e = t.details, i = es(t), s = t.errorAction, {
      action: r,
      retryCount: a = 0,
      retryConfig: o
    } = s || {}, c = !!s && !!o && (r === xt.RetryRequest || !s.resolved && r === xt.SendAlternateToPenaltyBox);
    if (c) {
      var l;
      if (a >= o.maxNumRetry)
        return !1;
      if (i && (l = t.context) != null && l.deliveryDirectives)
        this.warn(`Retrying playlist loading ${a + 1}/${o.maxNumRetry} after "${e}" without delivery-directives`), this.loadPlaylist();
      else {
        const h = xr(o, a);
        this.clearTimer(), this.timer = self.setTimeout(() => this.loadPlaylist(), h), this.warn(`Retrying playlist loading ${a + 1}/${o.maxNumRetry} after "${e}" in ${h}ms`);
      }
      t.levelRetry = !0, s.resolved = !0;
    }
    return c;
  }
}
function So(n, t) {
  if (n.length !== t.length)
    return !1;
  for (let e = 0; e < n.length; e++)
    if (!Ti(n[e].attrs, t[e].attrs))
      return !1;
  return !0;
}
function Ti(n, t, e) {
  const i = n["STABLE-RENDITION-ID"];
  return i && !e ? i === t["STABLE-RENDITION-ID"] : !(e || ["LANGUAGE", "NAME", "CHARACTERISTICS", "AUTOSELECT", "DEFAULT", "FORCED", "ASSOC-LANGUAGE"]).some((s) => n[s] !== t[s]);
}
function ar(n, t) {
  return t.label.toLowerCase() === n.name.toLowerCase() && (!t.language || t.language.toLowerCase() === (n.lang || "").toLowerCase());
}
class hd extends Mr {
  constructor(t) {
    super(t, "audio-track-controller"), this.tracks = [], this.groupIds = null, this.tracksInGroup = [], this.trackId = -1, this.currentTrack = null, this.selectDefaultTrack = !0, this.registerListeners();
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.LEVEL_LOADING, this.onLevelLoading, this), t.on(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.on(m.AUDIO_TRACK_LOADED, this.onAudioTrackLoaded, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.LEVEL_LOADING, this.onLevelLoading, this), t.off(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.off(m.AUDIO_TRACK_LOADED, this.onAudioTrackLoaded, this), t.off(m.ERROR, this.onError, this);
  }
  destroy() {
    this.unregisterListeners(), this.tracks.length = 0, this.tracksInGroup.length = 0, this.currentTrack = null, super.destroy();
  }
  onManifestLoading() {
    this.tracks = [], this.tracksInGroup = [], this.groupIds = null, this.currentTrack = null, this.trackId = -1, this.selectDefaultTrack = !0;
  }
  onManifestParsed(t, e) {
    this.tracks = e.audioTracks || [];
  }
  onAudioTrackLoaded(t, e) {
    const {
      id: i,
      groupId: s,
      details: r
    } = e, a = this.tracksInGroup[i];
    if (!a || a.groupId !== s) {
      this.warn(`Audio track with id:${i} and group:${s} not found in active group ${a == null ? void 0 : a.groupId}`);
      return;
    }
    const o = a.details;
    a.details = e.details, this.log(`Audio track ${i} "${a.name}" lang:${a.lang} group:${s} loaded [${r.startSN}-${r.endSN}]`), i === this.trackId && this.playlistLoaded(i, e, o);
  }
  onLevelLoading(t, e) {
    this.switchLevel(e.level);
  }
  onLevelSwitching(t, e) {
    this.switchLevel(e.level);
  }
  switchLevel(t) {
    const e = this.hls.levels[t];
    if (!e)
      return;
    const i = e.audioGroups || null, s = this.groupIds;
    let r = this.currentTrack;
    if (!i || (s == null ? void 0 : s.length) !== (i == null ? void 0 : i.length) || i != null && i.some((o) => (s == null ? void 0 : s.indexOf(o)) === -1)) {
      this.groupIds = i, this.trackId = -1, this.currentTrack = null;
      const o = this.tracks.filter((u) => !i || i.indexOf(u.groupId) !== -1);
      if (o.length)
        this.selectDefaultTrack && !o.some((u) => u.default) && (this.selectDefaultTrack = !1), o.forEach((u, f) => {
          u.id = f;
        });
      else if (!r && !this.tracksInGroup.length)
        return;
      this.tracksInGroup = o;
      const c = this.hls.config.audioPreference;
      if (!r && c) {
        const u = Xt(c, o, Ie);
        if (u > -1)
          r = o[u];
        else {
          const f = Xt(c, this.tracks);
          r = this.tracks[f];
        }
      }
      let l = this.findTrackId(r);
      l === -1 && r && (l = this.findTrackId(null));
      const h = {
        audioTracks: o
      };
      this.log(`Updating audio tracks, ${o.length} track(s) found in group(s): ${i == null ? void 0 : i.join(",")}`), this.hls.trigger(m.AUDIO_TRACKS_UPDATED, h);
      const d = this.trackId;
      if (l !== -1 && d === -1)
        this.setAudioTrack(l);
      else if (o.length && d === -1) {
        var a;
        const u = new Error(`No audio track selected for current audio group-ID(s): ${(a = this.groupIds) == null ? void 0 : a.join(",")} track count: ${o.length}`);
        this.warn(u.message), this.hls.trigger(m.ERROR, {
          type: Y.MEDIA_ERROR,
          details: L.AUDIO_TRACK_LOAD_ERROR,
          fatal: !0,
          error: u
        });
      }
    }
  }
  onError(t, e) {
    e.fatal || !e.context || e.context.type === tt.AUDIO_TRACK && e.context.id === this.trackId && (!this.groupIds || this.groupIds.indexOf(e.context.groupId) !== -1) && this.checkRetry(e);
  }
  get allAudioTracks() {
    return this.tracks;
  }
  get audioTracks() {
    return this.tracksInGroup;
  }
  get audioTrack() {
    return this.trackId;
  }
  set audioTrack(t) {
    this.selectDefaultTrack = !1, this.setAudioTrack(t);
  }
  setAudioOption(t) {
    const e = this.hls;
    if (e.config.audioPreference = t, t) {
      const i = this.allAudioTracks;
      if (this.selectDefaultTrack = !1, i.length) {
        const s = this.currentTrack;
        if (s && _e(t, s, Ie))
          return s;
        const r = Xt(t, this.tracksInGroup, Ie);
        if (r > -1) {
          const a = this.tracksInGroup[r];
          return this.setAudioTrack(r), a;
        } else if (s) {
          let a = e.loadLevel;
          a === -1 && (a = e.firstAutoLevel);
          const o = xc(t, e.levels, i, a, Ie);
          if (o === -1)
            return null;
          e.nextLoadLevel = o;
        }
        if (t.channels || t.audioCodec) {
          const a = Xt(t, i);
          if (a > -1)
            return i[a];
        }
      }
    }
    return null;
  }
  setAudioTrack(t) {
    const e = this.tracksInGroup;
    if (t < 0 || t >= e.length) {
      this.warn(`Invalid audio track id: ${t}`);
      return;
    }
    this.selectDefaultTrack = !1;
    const i = this.currentTrack, s = e[t], r = s.details && !s.details.live;
    if (t === this.trackId && s === i && r || (this.log(`Switching to audio-track ${t} "${s.name}" lang:${s.lang} group:${s.groupId} channels:${s.channels}`), this.trackId = t, this.currentTrack = s, this.hls.trigger(m.AUDIO_TRACK_SWITCHING, st({}, s)), r))
      return;
    const a = this.switchParams(s.url, i == null ? void 0 : i.details, s.details);
    this.loadPlaylist(a);
  }
  findTrackId(t) {
    const e = this.tracksInGroup;
    for (let i = 0; i < e.length; i++) {
      const s = e[i];
      if (!(this.selectDefaultTrack && !s.default) && (!t || _e(t, s, Ie)))
        return i;
    }
    if (t) {
      const {
        name: i,
        lang: s,
        assocLang: r,
        characteristics: a,
        audioCodec: o,
        channels: c
      } = t;
      for (let l = 0; l < e.length; l++) {
        const h = e[l];
        if (_e({
          name: i,
          lang: s,
          assocLang: r,
          characteristics: a,
          audioCodec: o,
          channels: c
        }, h, Ie))
          return l;
      }
      for (let l = 0; l < e.length; l++) {
        const h = e[l];
        if (Ti(t.attrs, h.attrs, ["LANGUAGE", "ASSOC-LANGUAGE", "CHARACTERISTICS"]))
          return l;
      }
      for (let l = 0; l < e.length; l++) {
        const h = e[l];
        if (Ti(t.attrs, h.attrs, ["LANGUAGE"]))
          return l;
      }
    }
    return -1;
  }
  loadPlaylist(t) {
    super.loadPlaylist();
    const e = this.currentTrack;
    this.shouldLoadPlaylist(e) && ts(e.url, this.hls) && this.scheduleLoading(e, t);
  }
  loadingPlaylist(t, e) {
    super.loadingPlaylist(t, e);
    const i = t.id, s = t.groupId, r = this.getUrlWithDirectives(t.url, e), a = t.details, o = a == null ? void 0 : a.age;
    this.log(`Loading audio-track ${i} "${t.name}" lang:${t.lang} group:${s}${(e == null ? void 0 : e.msn) !== void 0 ? " at sn " + e.msn + " part " + e.part : ""}${o && a.live ? " age " + o.toFixed(1) + (a.type && " " + a.type || "") : ""} ${r}`), this.hls.trigger(m.AUDIO_TRACK_LOADING, {
      url: r,
      id: i,
      groupId: s,
      deliveryDirectives: e || null,
      track: t
    });
  }
}
class dd {
  constructor(t) {
    this.tracks = void 0, this.queues = {
      video: [],
      audio: [],
      audiovideo: []
    }, this.tracks = t;
  }
  destroy() {
    this.tracks = this.queues = null;
  }
  append(t, e, i) {
    if (this.queues === null || this.tracks === null)
      return;
    const s = this.queues[e];
    s.push(t), s.length === 1 && !i && this.executeNext(e);
  }
  appendBlocker(t) {
    return new Promise((e) => {
      const i = {
        label: "async-blocker",
        execute: e,
        onStart: () => {
        },
        onComplete: () => {
        },
        onError: () => {
        }
      };
      this.append(i, t);
    });
  }
  prependBlocker(t) {
    return new Promise((e) => {
      if (this.queues) {
        const i = {
          label: "async-blocker-prepend",
          execute: e,
          onStart: () => {
          },
          onComplete: () => {
          },
          onError: () => {
          }
        };
        this.queues[t].unshift(i);
      }
    });
  }
  removeBlockers() {
    this.queues !== null && [this.queues.video, this.queues.audio, this.queues.audiovideo].forEach((t) => {
      var e;
      const i = (e = t[0]) == null ? void 0 : e.label;
      (i === "async-blocker" || i === "async-blocker-prepend") && (t[0].execute(), t.splice(0, 1));
    });
  }
  unblockAudio(t) {
    if (this.queues === null)
      return;
    this.queues.audio[0] === t && this.shiftAndExecuteNext("audio");
  }
  executeNext(t) {
    if (this.queues === null || this.tracks === null)
      return;
    const e = this.queues[t];
    if (e.length) {
      const s = e[0];
      try {
        s.execute();
      } catch (r) {
        var i;
        if (s.onError(r), this.queues === null || this.tracks === null)
          return;
        const a = (i = this.tracks[t]) == null ? void 0 : i.buffer;
        a != null && a.updating || this.shiftAndExecuteNext(t);
      }
    }
  }
  shiftAndExecuteNext(t) {
    this.queues !== null && (this.queues[t].shift(), this.executeNext(t));
  }
  current(t) {
    var e;
    return ((e = this.queues) == null ? void 0 : e[t][0]) || null;
  }
  toString() {
    const {
      queues: t,
      tracks: e
    } = this;
    return t === null || e === null ? "<destroyed>" : `
${this.list("video")}
${this.list("audio")}
${this.list("audiovideo")}}`;
  }
  list(t) {
    var e, i;
    return (e = this.queues) != null && e[t] || (i = this.tracks) != null && i[t] ? `${t}: (${this.listSbInfo(t)}) ${this.listOps(t)}` : "";
  }
  listSbInfo(t) {
    var e;
    const i = (e = this.tracks) == null ? void 0 : e[t], s = i == null ? void 0 : i.buffer;
    return s ? `SourceBuffer${s.updating ? " updating" : ""}${i.ended ? " ended" : ""}${i.ending ? " ending" : ""}` : "none";
  }
  listOps(t) {
    var e;
    return ((e = this.queues) == null ? void 0 : e[t].map((i) => i.label).join(", ")) || "";
  }
}
const Hn = /(avc[1234]|hvc1|hev1|dvh[1e]|vp09|av01)(?:\.[^.,]+)+/, xo = "HlsJsTrackRemovedError";
class ud extends Error {
  constructor(t) {
    super(t), this.name = xo;
  }
}
class fd extends Bt {
  constructor(t, e) {
    super("buffer-controller", t.logger), this.hls = void 0, this.fragmentTracker = void 0, this.details = null, this._objectUrl = null, this.operationQueue = null, this.bufferCodecEventsTotal = 0, this.media = null, this.mediaSource = null, this.lastMpegAudioChunk = null, this.blockedAudioAppend = null, this.lastVideoAppendEnd = 0, this.appendSource = void 0, this.transferData = void 0, this.overrides = void 0, this.appendErrors = {
      audio: 0,
      video: 0,
      audiovideo: 0
    }, this.tracks = {}, this.sourceBuffers = [[null, null], [null, null]], this._onEndStreaming = (i) => {
      var s;
      this.hls && ((s = this.mediaSource) == null ? void 0 : s.readyState) === "open" && this.hls.pauseBuffering();
    }, this._onStartStreaming = (i) => {
      this.hls && this.hls.resumeBuffering();
    }, this._onMediaSourceOpen = (i) => {
      const {
        media: s,
        mediaSource: r
      } = this;
      i && this.log("Media source opened"), !(!s || !r) && (r.removeEventListener("sourceopen", this._onMediaSourceOpen), s.removeEventListener("emptied", this._onMediaEmptied), this.updateDuration(), this.hls.trigger(m.MEDIA_ATTACHED, {
        media: s,
        mediaSource: r
      }), this.mediaSource !== null && this.checkPendingTracks());
    }, this._onMediaSourceClose = () => {
      this.log("Media source closed");
    }, this._onMediaSourceEnded = () => {
      this.log("Media source ended");
    }, this._onMediaEmptied = () => {
      const {
        mediaSrc: i,
        _objectUrl: s
      } = this;
      i !== s && this.error(`Media element src was set while attaching MediaSource (${s} > ${i})`);
    }, this.hls = t, this.fragmentTracker = e, this.appendSource = Ml(ge(t.config.preferManagedMediaSource)), this.initTracks(), this.registerListeners();
  }
  hasSourceTypes() {
    return Object.keys(this.tracks).length > 0;
  }
  destroy() {
    this.unregisterListeners(), this.details = null, this.lastMpegAudioChunk = this.blockedAudioAppend = null, this.transferData = this.overrides = void 0, this.operationQueue && (this.operationQueue.destroy(), this.operationQueue = null), this.hls = this.fragmentTracker = null, this._onMediaSourceOpen = this._onMediaSourceClose = null, this._onMediaSourceEnded = null, this._onStartStreaming = this._onEndStreaming = null;
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.BUFFER_RESET, this.onBufferReset, this), t.on(m.BUFFER_APPENDING, this.onBufferAppending, this), t.on(m.BUFFER_CODECS, this.onBufferCodecs, this), t.on(m.BUFFER_EOS, this.onBufferEos, this), t.on(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.on(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.on(m.FRAG_PARSED, this.onFragParsed, this), t.on(m.FRAG_CHANGED, this.onFragChanged, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.BUFFER_RESET, this.onBufferReset, this), t.off(m.BUFFER_APPENDING, this.onBufferAppending, this), t.off(m.BUFFER_CODECS, this.onBufferCodecs, this), t.off(m.BUFFER_EOS, this.onBufferEos, this), t.off(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.off(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.off(m.FRAG_PARSED, this.onFragParsed, this), t.off(m.FRAG_CHANGED, this.onFragChanged, this), t.off(m.ERROR, this.onError, this);
  }
  transferMedia() {
    const {
      media: t,
      mediaSource: e
    } = this;
    if (!t)
      return null;
    const i = {};
    if (this.operationQueue) {
      const r = this.isUpdating();
      r || this.operationQueue.removeBlockers();
      const a = this.isQueued();
      (r || a) && this.warn(`Transfering MediaSource with${a ? " operations in queue" : ""}${r ? " updating SourceBuffer(s)" : ""} ${this.operationQueue}`), this.operationQueue.destroy();
    }
    const s = this.transferData;
    return !this.sourceBufferCount && s && s.mediaSource === e ? nt(i, s.tracks) : this.sourceBuffers.forEach((r) => {
      const [a] = r;
      a && (i[a] = nt({}, this.tracks[a]), this.removeBuffer(a)), r[0] = r[1] = null;
    }), {
      media: t,
      mediaSource: e,
      tracks: i
    };
  }
  initTracks() {
    const t = {};
    this.sourceBuffers = [[null, null], [null, null]], this.tracks = t, this.resetQueue(), this.resetAppendErrors(), this.lastMpegAudioChunk = this.blockedAudioAppend = null, this.lastVideoAppendEnd = 0;
  }
  onManifestLoading() {
    this.bufferCodecEventsTotal = 0, this.details = null;
  }
  onManifestParsed(t, e) {
    var i;
    let s = 2;
    (e.audio && !e.video || !e.altAudio) && (s = 1), this.bufferCodecEventsTotal = s, this.log(`${s} bufferCodec event(s) expected.`), (i = this.transferData) != null && i.mediaSource && this.sourceBufferCount && s && this.bufferCreated();
  }
  onMediaAttaching(t, e) {
    const i = this.media = e.media;
    this.transferData = this.overrides = void 0;
    const s = ge(this.appendSource);
    if (s) {
      const r = !!e.mediaSource;
      (r || e.overrides) && (this.transferData = e, this.overrides = e.overrides);
      const a = this.mediaSource = e.mediaSource || new s();
      if (this.assignMediaSource(a), r)
        this._objectUrl = i.src, this.attachTransferred();
      else {
        const o = this._objectUrl = self.URL.createObjectURL(a);
        if (this.appendSource)
          try {
            i.removeAttribute("src");
            const c = self.ManagedMediaSource;
            i.disableRemotePlayback = i.disableRemotePlayback || c && a instanceof c, Vn(i), gd(i, o), i.load();
          } catch {
            i.src = o;
          }
        else
          i.src = o;
      }
      i.addEventListener("emptied", this._onMediaEmptied);
    }
  }
  assignMediaSource(t) {
    var e, i;
    this.log(`${((e = this.transferData) == null ? void 0 : e.mediaSource) === t ? "transferred" : "created"} media source: ${(i = t.constructor) == null ? void 0 : i.name}`), t.addEventListener("sourceopen", this._onMediaSourceOpen), t.addEventListener("sourceended", this._onMediaSourceEnded), t.addEventListener("sourceclose", this._onMediaSourceClose), this.appendSource && (t.addEventListener("startstreaming", this._onStartStreaming), t.addEventListener("endstreaming", this._onEndStreaming));
  }
  attachTransferred() {
    const t = this.media, e = this.transferData;
    if (!e || !t)
      return;
    const i = this.tracks, s = e.tracks, r = s ? Object.keys(s) : null, a = r ? r.length : 0, o = () => {
      Promise.resolve().then(() => {
        this.media && this.mediaSourceOpenOrEnded && this._onMediaSourceOpen();
      });
    };
    if (s && r && a) {
      if (!this.tracksReady) {
        this.hls.config.startFragPrefetch = !0, this.log("attachTransferred: waiting for SourceBuffer track info");
        return;
      }
      if (this.log(`attachTransferred: (bufferCodecEventsTotal ${this.bufferCodecEventsTotal})
required tracks: ${ot(i, (c, l) => c === "initSegment" ? void 0 : l)};
transfer tracks: ${ot(s, (c, l) => c === "initSegment" ? void 0 : l)}}`), !va(s, i)) {
        e.mediaSource = null, e.tracks = void 0;
        const c = t.currentTime, l = this.details, h = Math.max(c, (l == null ? void 0 : l.fragments[0].start) || 0);
        if (h - c > 1) {
          this.log(`attachTransferred: waiting for playback to reach new tracks start time ${c} -> ${h}`);
          return;
        }
        this.warn(`attachTransferred: resetting MediaSource for incompatible tracks ("${Object.keys(s)}"->"${Object.keys(i)}") start time: ${h} currentTime: ${c}`), this.onMediaDetaching(m.MEDIA_DETACHING, {}), this.onMediaAttaching(m.MEDIA_ATTACHING, e), t.currentTime = h;
        return;
      }
      this.transferData = void 0, r.forEach((c) => {
        const l = c, h = s[l];
        if (h) {
          const d = h.buffer;
          if (d) {
            const u = this.fragmentTracker, f = h.id;
            if (u.hasFragments(f) || u.hasParts(f)) {
              const p = q.getBuffered(d);
              u.detectEvictedFragments(l, p, f, null, !0);
            }
            const g = Ps(l), v = [l, d];
            this.sourceBuffers[g] = v, d.updating && this.operationQueue && this.operationQueue.prependBlocker(l), this.trackSourceBuffer(l, h);
          }
        }
      }), o(), this.bufferCreated();
    } else
      this.log("attachTransferred: MediaSource w/o SourceBuffers"), o();
  }
  get mediaSourceOpenOrEnded() {
    var t;
    const e = (t = this.mediaSource) == null ? void 0 : t.readyState;
    return e === "open" || e === "ended";
  }
  onMediaDetaching(t, e) {
    const i = !!e.transferMedia;
    this.transferData = this.overrides = void 0;
    const {
      media: s,
      mediaSource: r,
      _objectUrl: a
    } = this;
    if (r) {
      if (this.log(`media source ${i ? "transferring" : "detaching"}`), i)
        this.sourceBuffers.forEach(([o]) => {
          o && this.removeBuffer(o);
        }), this.resetQueue();
      else {
        if (this.mediaSourceOpenOrEnded) {
          const o = r.readyState === "open";
          try {
            const c = r.sourceBuffers;
            for (let l = c.length; l--; )
              o && c[l].abort(), r.removeSourceBuffer(c[l]);
            o && r.endOfStream();
          } catch (c) {
            this.warn(`onMediaDetaching: ${c.message} while calling endOfStream`);
          }
        }
        this.sourceBufferCount && this.onBufferReset();
      }
      r.removeEventListener("sourceopen", this._onMediaSourceOpen), r.removeEventListener("sourceended", this._onMediaSourceEnded), r.removeEventListener("sourceclose", this._onMediaSourceClose), this.appendSource && (r.removeEventListener("startstreaming", this._onStartStreaming), r.removeEventListener("endstreaming", this._onEndStreaming)), this.mediaSource = null, this._objectUrl = null;
    }
    s && (s.removeEventListener("emptied", this._onMediaEmptied), i || (a && self.URL.revokeObjectURL(a), this.mediaSrc === a ? (s.removeAttribute("src"), this.appendSource && Vn(s), s.load()) : this.warn("media|source.src was changed by a third party - skip cleanup")), this.media = null), this.hls.trigger(m.MEDIA_DETACHED, e);
  }
  onBufferReset() {
    this.sourceBuffers.forEach(([t]) => {
      t && this.resetBuffer(t);
    }), this.initTracks();
  }
  resetBuffer(t) {
    var e;
    const i = (e = this.tracks[t]) == null ? void 0 : e.buffer;
    if (this.removeBuffer(t), i)
      try {
        var s;
        (s = this.mediaSource) != null && s.sourceBuffers.length && this.mediaSource.removeSourceBuffer(i);
      } catch (r) {
        this.warn(`onBufferReset ${t}`, r);
      }
    delete this.tracks[t];
  }
  removeBuffer(t) {
    this.removeBufferListeners(t), this.sourceBuffers[Ps(t)] = [null, null];
    const e = this.tracks[t];
    e && (e.buffer = void 0);
  }
  resetQueue() {
    this.operationQueue && this.operationQueue.destroy(), this.operationQueue = new dd(this.tracks);
  }
  onBufferCodecs(t, e) {
    var i;
    const s = this.tracks, r = Object.keys(e);
    this.log(`BUFFER_CODECS: "${r}" (current SB count ${this.sourceBufferCount})`);
    const a = "audiovideo" in e && (s.audio || s.video) || s.audiovideo && ("audio" in e || "video" in e), o = !a && this.sourceBufferCount && this.media && r.some((c) => !s[c]);
    if (a || o) {
      this.warn(`Unsupported transition between "${Object.keys(s)}" and "${r}" SourceBuffers`);
      return;
    }
    r.forEach((c) => {
      var l, h;
      const d = e[c], {
        id: u,
        codec: f,
        levelCodec: g,
        container: v,
        metadata: p,
        supplemental: y
      } = d;
      let E = s[c];
      const T = (l = this.transferData) == null || (l = l.tracks) == null ? void 0 : l[c], S = T != null && T.buffer ? T : E, x = (S == null ? void 0 : S.pendingCodec) || (S == null ? void 0 : S.codec), D = S == null ? void 0 : S.levelCodec;
      E || (E = s[c] = {
        buffer: void 0,
        listeners: [],
        codec: f,
        supplemental: y,
        container: v,
        levelCodec: g,
        metadata: p,
        id: u
      });
      const A = Gi(x, D), _ = A == null ? void 0 : A.replace(Hn, "$1");
      let R = Gi(f, g);
      const b = (h = R) == null ? void 0 : h.replace(Hn, "$1");
      R && A && _ !== b && (c.slice(0, 5) === "audio" && (R = Zi(R, this.appendSource)), this.log(`switching codec ${x} to ${R}`), R !== (E.pendingCodec || E.codec) && (E.pendingCodec = R), E.container = v, this.appendChangeType(c, v, R));
    }), (this.tracksReady || this.sourceBufferCount) && (e.tracks = this.sourceBufferTracks), !this.sourceBufferCount && (this.bufferCodecEventsTotal > 1 && !this.tracks.video && !e.video && ((i = e.audio) == null ? void 0 : i.id) === "main" && (this.log("Main audio-only"), this.bufferCodecEventsTotal = 1), this.mediaSourceOpenOrEnded && this.checkPendingTracks());
  }
  get sourceBufferTracks() {
    return Object.keys(this.tracks).reduce((t, e) => {
      const i = this.tracks[e];
      return t[e] = {
        id: i.id,
        container: i.container,
        codec: i.codec,
        levelCodec: i.levelCodec
      }, t;
    }, {});
  }
  appendChangeType(t, e, i) {
    const s = `${e};codecs=${i}`, r = {
      label: `change-type=${s}`,
      execute: () => {
        const a = this.tracks[t];
        if (a) {
          const o = a.buffer;
          o != null && o.changeType && (this.log(`changing ${t} sourceBuffer type to ${s}`), o.changeType(s), a.codec = i, a.container = e);
        }
        this.shiftAndExecuteNext(t);
      },
      onStart: () => {
      },
      onComplete: () => {
      },
      onError: (a) => {
        this.warn(`Failed to change ${t} SourceBuffer type`, a);
      }
    };
    this.append(r, t, this.isPending(this.tracks[t]));
  }
  blockAudio(t) {
    var e;
    const i = t.start, s = i + t.duration * 0.05;
    if (((e = this.fragmentTracker.getAppendedFrag(i, K.MAIN)) == null ? void 0 : e.gap) === !0)
      return;
    const a = {
      label: "block-audio",
      execute: () => {
        var o;
        const c = this.tracks.video;
        (this.lastVideoAppendEnd > s || c != null && c.buffer && q.isBuffered(c.buffer, s) || ((o = this.fragmentTracker.getAppendedFrag(s, K.MAIN)) == null ? void 0 : o.gap) === !0) && (this.blockedAudioAppend = null, this.shiftAndExecuteNext("audio"));
      },
      onStart: () => {
      },
      onComplete: () => {
      },
      onError: (o) => {
        this.warn("Error executing block-audio operation", o);
      }
    };
    this.blockedAudioAppend = {
      op: a,
      frag: t
    }, this.append(a, "audio", !0);
  }
  unblockAudio() {
    const {
      blockedAudioAppend: t,
      operationQueue: e
    } = this;
    t && e && (this.blockedAudioAppend = null, e.unblockAudio(t.op));
  }
  onBufferAppending(t, e) {
    const {
      tracks: i
    } = this, {
      data: s,
      type: r,
      parent: a,
      frag: o,
      part: c,
      chunkMeta: l,
      offset: h
    } = e, d = l.buffering[r], {
      sn: u,
      cc: f
    } = o, g = self.performance.now();
    d.start = g;
    const v = o.stats.buffering, p = c ? c.stats.buffering : null;
    v.start === 0 && (v.start = g), p && p.start === 0 && (p.start = g);
    const y = i.audio;
    let E = !1;
    r === "audio" && (y == null ? void 0 : y.container) === "audio/mpeg" && (E = !this.lastMpegAudioChunk || l.id === 1 || this.lastMpegAudioChunk.sn !== l.sn, this.lastMpegAudioChunk = l);
    const T = i.video, S = T == null ? void 0 : T.buffer;
    if (S && u !== "initSegment") {
      const A = c || o, _ = this.blockedAudioAppend;
      if (r === "audio" && a !== "main" && !this.blockedAudioAppend && !(T.ending || T.ended)) {
        const b = A.start + A.duration * 0.05, C = S.buffered, F = this.currentOp("video");
        !C.length && !F ? this.blockAudio(A) : !F && !q.isBuffered(S, b) && this.lastVideoAppendEnd < b && this.blockAudio(A);
      } else if (r === "video") {
        const R = A.end;
        if (_) {
          const b = _.frag.start;
          (R > b || R < this.lastVideoAppendEnd || q.isBuffered(S, b)) && this.unblockAudio();
        }
        this.lastVideoAppendEnd = R;
      }
    }
    const x = (c || o).start, D = {
      label: `append-${r}`,
      execute: () => {
        var A;
        d.executeStart = self.performance.now();
        const _ = (A = this.tracks[r]) == null ? void 0 : A.buffer;
        _ && (E ? this.updateTimestampOffset(_, x, 0.1, r, u, f) : h !== void 0 && B(h) && this.updateTimestampOffset(_, h, 1e-6, r, u, f)), this.appendExecutor(s, r);
      },
      onStart: () => {
      },
      onComplete: () => {
        const A = self.performance.now();
        d.executeEnd = d.end = A, v.first === 0 && (v.first = A), p && p.first === 0 && (p.first = A);
        const _ = {};
        this.sourceBuffers.forEach(([R, b]) => {
          R && (_[R] = q.getBuffered(b));
        }), this.appendErrors[r] = 0, r === "audio" || r === "video" ? this.appendErrors.audiovideo = 0 : (this.appendErrors.audio = 0, this.appendErrors.video = 0), this.hls.trigger(m.BUFFER_APPENDED, {
          type: r,
          frag: o,
          part: c,
          chunkMeta: l,
          parent: o.type,
          timeRanges: _
        });
      },
      onError: (A) => {
        var _;
        const R = {
          type: Y.MEDIA_ERROR,
          parent: o.type,
          details: L.BUFFER_APPEND_ERROR,
          sourceBufferName: r,
          frag: o,
          part: c,
          chunkMeta: l,
          error: A,
          err: A,
          fatal: !1
        }, b = (_ = this.media) == null ? void 0 : _.error;
        if (A.code === DOMException.QUOTA_EXCEEDED_ERR || A.name == "QuotaExceededError" || "quota" in A)
          R.details = L.BUFFER_FULL_ERROR;
        else if (A.code === DOMException.INVALID_STATE_ERR && this.mediaSourceOpenOrEnded && !b)
          R.errorAction = We(!0);
        else if (A.name === xo && this.sourceBufferCount === 0)
          R.errorAction = We(!0);
        else {
          const C = ++this.appendErrors[r];
          this.warn(`Failed ${C}/${this.hls.config.appendErrorMaxRetry} times to append segment in "${r}" sourceBuffer (${b || "no media error"})`), (C >= this.hls.config.appendErrorMaxRetry || b) && (R.fatal = !0);
        }
        this.hls.trigger(m.ERROR, R);
      }
    };
    this.log(`queuing "${r}" append sn: ${u}${c ? " p: " + c.index : ""} of ${o.type === K.MAIN ? "level" : "track"} ${o.level} cc: ${f}`), this.append(D, r, this.isPending(this.tracks[r]));
  }
  getFlushOp(t, e, i) {
    return this.log(`queuing "${t}" remove ${e}-${i}`), {
      label: "remove",
      execute: () => {
        this.removeExecutor(t, e, i);
      },
      onStart: () => {
      },
      onComplete: () => {
        this.hls.trigger(m.BUFFER_FLUSHED, {
          type: t
        });
      },
      onError: (s) => {
        this.warn(`Failed to remove ${e}-${i} from "${t}" SourceBuffer`, s);
      }
    };
  }
  onBufferFlushing(t, e) {
    const {
      type: i,
      startOffset: s,
      endOffset: r
    } = e;
    i ? this.append(this.getFlushOp(i, s, r), i) : this.sourceBuffers.forEach(([a]) => {
      a && this.append(this.getFlushOp(a, s, r), a);
    });
  }
  onFragParsed(t, e) {
    const {
      frag: i,
      part: s
    } = e, r = [], a = s ? s.elementaryStreams : i.elementaryStreams;
    a[at.AUDIOVIDEO] ? r.push("audiovideo") : (a[at.AUDIO] && r.push("audio"), a[at.VIDEO] && r.push("video"));
    const o = () => {
      const c = self.performance.now();
      i.stats.buffering.end = c, s && (s.stats.buffering.end = c);
      const l = s ? s.stats : i.stats;
      this.hls.trigger(m.FRAG_BUFFERED, {
        frag: i,
        part: s,
        stats: l,
        id: i.type
      });
    };
    r.length === 0 && this.warn(`Fragments must have at least one ElementaryStreamType set. type: ${i.type} level: ${i.level} sn: ${i.sn}`), this.blockBuffers(o, r).catch((c) => {
      this.warn(`Fragment buffered callback ${c}`), this.stepOperationQueue(this.sourceBufferTypes);
    });
  }
  onFragChanged(t, e) {
    this.trimBuffers();
  }
  get bufferedToEnd() {
    return this.sourceBufferCount > 0 && !this.sourceBuffers.some(([t]) => {
      if (t) {
        const e = this.tracks[t];
        if (e)
          return !e.ended || e.ending;
      }
      return !1;
    });
  }
  // on BUFFER_EOS mark matching sourcebuffer(s) as "ending" and "ended" and queue endOfStream after remaining operations(s)
  // an undefined data.type will mark all buffers as EOS.
  onBufferEos(t, e) {
    var i;
    this.sourceBuffers.forEach(([a]) => {
      if (a) {
        const o = this.tracks[a];
        (!e.type || e.type === a) && (o.ending = !0, o.ended || (o.ended = !0, this.log(`${a} buffer reached EOS`)));
      }
    });
    const s = ((i = this.overrides) == null ? void 0 : i.endOfStream) !== !1;
    this.sourceBufferCount > 0 && !this.sourceBuffers.some(([a]) => {
      var o;
      return a && !((o = this.tracks[a]) != null && o.ended);
    }) ? s ? (this.log("Queueing EOS"), this.blockUntilOpen(() => {
      this.tracksEnded();
      const {
        mediaSource: a
      } = this;
      if (!a || a.readyState !== "open") {
        a && this.log(`Could not call mediaSource.endOfStream(). mediaSource.readyState: ${a.readyState}`);
        return;
      }
      this.log("Calling mediaSource.endOfStream()"), a.endOfStream(), this.hls.trigger(m.BUFFERED_TO_END, void 0);
    })) : (this.tracksEnded(), this.hls.trigger(m.BUFFERED_TO_END, void 0)) : e.type === "video" && this.unblockAudio();
  }
  tracksEnded() {
    this.sourceBuffers.forEach(([t]) => {
      if (t !== null) {
        const e = this.tracks[t];
        e && (e.ending = !1);
      }
    });
  }
  onLevelUpdated(t, {
    details: e
  }) {
    e.fragments.length && (this.details = e, this.updateDuration());
  }
  updateDuration() {
    this.blockUntilOpen(() => {
      const t = this.getDurationAndRange();
      t && this.updateMediaSource(t);
    });
  }
  onError(t, e) {
    if (e.details === L.BUFFER_APPEND_ERROR && e.frag) {
      var i;
      const s = (i = e.errorAction) == null ? void 0 : i.nextAutoLevel;
      B(s) && s !== e.frag.level && this.resetAppendErrors();
    }
  }
  resetAppendErrors() {
    this.appendErrors = {
      audio: 0,
      video: 0,
      audiovideo: 0
    };
  }
  trimBuffers() {
    const {
      hls: t,
      details: e,
      media: i
    } = this;
    if (!i || e === null || !this.sourceBufferCount)
      return;
    const s = t.config, r = i.currentTime, a = e.levelTargetDuration, o = e.live && s.liveBackBufferLength !== null ? s.liveBackBufferLength : s.backBufferLength;
    if (B(o) && o >= 0) {
      const l = Math.max(o, a), h = Math.floor(r / a) * a - l;
      this.flushBackBuffer(r, a, h);
    }
    const c = s.frontBufferFlushThreshold;
    if (B(c) && c > 0) {
      const l = Math.max(s.maxBufferLength, c), h = Math.max(l, a), d = Math.floor(r / a) * a + h;
      this.flushFrontBuffer(r, a, d);
    }
  }
  flushBackBuffer(t, e, i) {
    this.sourceBuffers.forEach(([s, r]) => {
      if (r) {
        const o = q.getBuffered(r);
        if (o.length > 0 && i > o.start(0)) {
          var a;
          this.hls.trigger(m.BACK_BUFFER_REACHED, {
            bufferEnd: i
          });
          const c = this.tracks[s];
          if ((a = this.details) != null && a.live)
            this.hls.trigger(m.LIVE_BACK_BUFFER_REACHED, {
              bufferEnd: i
            });
          else if (c != null && c.ended) {
            this.log(`Cannot flush ${s} back buffer while SourceBuffer is in ended state`);
            return;
          }
          this.hls.trigger(m.BUFFER_FLUSHING, {
            startOffset: 0,
            endOffset: i,
            type: s
          });
        }
      }
    });
  }
  flushFrontBuffer(t, e, i) {
    this.sourceBuffers.forEach(([s, r]) => {
      if (r) {
        const a = q.getBuffered(r), o = a.length;
        if (o < 2)
          return;
        const c = a.start(o - 1), l = a.end(o - 1);
        if (i > c || t >= c && t <= l)
          return;
        this.hls.trigger(m.BUFFER_FLUSHING, {
          startOffset: c,
          endOffset: 1 / 0,
          type: s
        });
      }
    });
  }
  /**
   * Update Media Source duration to current level duration or override to Infinity if configuration parameter
   * 'liveDurationInfinity` is set to `true`
   * More details: https://github.com/video-dev/hls.js/issues/355
   */
  getDurationAndRange() {
    var t;
    const {
      details: e,
      mediaSource: i
    } = this;
    if (!e || !this.media || (i == null ? void 0 : i.readyState) !== "open")
      return null;
    const s = e.edge;
    if (e.live && this.hls.config.liveDurationInfinity) {
      if (e.fragments.length && i.setLiveSeekableRange) {
        const l = Math.max(0, e.fragmentStart), h = Math.max(l, s);
        return {
          duration: 1 / 0,
          start: l,
          end: h
        };
      }
      return {
        duration: 1 / 0
      };
    }
    const r = (t = this.overrides) == null ? void 0 : t.duration;
    if (r)
      return B(r) ? {
        duration: r
      } : null;
    const a = this.media.duration, o = B(i.duration) ? i.duration : 0;
    return s > o && s > a || !B(a) ? {
      duration: s
    } : null;
  }
  updateMediaSource({
    duration: t,
    start: e,
    end: i
  }) {
    const s = this.mediaSource;
    !this.media || !s || s.readyState !== "open" || (s.duration !== t && (B(t) && this.log(`Updating MediaSource duration to ${t.toFixed(3)}`), s.duration = t), e !== void 0 && i !== void 0 && (this.log(`MediaSource duration is set to ${s.duration}. Setting seekable range to ${e}-${i}.`), s.setLiveSeekableRange(e, i)));
  }
  get tracksReady() {
    const t = this.pendingTrackCount;
    return t > 0 && (t >= this.bufferCodecEventsTotal || this.isPending(this.tracks.audiovideo));
  }
  checkPendingTracks() {
    const {
      bufferCodecEventsTotal: t,
      pendingTrackCount: e,
      tracks: i
    } = this;
    if (this.log(`checkPendingTracks (pending: ${e} codec events expected: ${t}) ${ot(i)}`), this.tracksReady) {
      var s;
      const r = (s = this.transferData) == null ? void 0 : s.tracks;
      r && Object.keys(r).length ? this.attachTransferred() : this.createSourceBuffers();
    }
  }
  bufferCreated() {
    if (this.sourceBufferCount) {
      const t = {};
      this.sourceBuffers.forEach(([e, i]) => {
        if (e) {
          const s = this.tracks[e];
          t[e] = {
            buffer: i,
            container: s.container,
            codec: s.codec,
            supplemental: s.supplemental,
            levelCodec: s.levelCodec,
            id: s.id,
            metadata: s.metadata
          };
        }
      }), this.hls.trigger(m.BUFFER_CREATED, {
        tracks: t
      }), this.log(`SourceBuffers created. Running queue: ${this.operationQueue}`), this.sourceBuffers.forEach(([e]) => {
        this.executeNext(e);
      });
    } else {
      const t = new Error("could not create source buffer for media codec(s)");
      this.hls.trigger(m.ERROR, {
        type: Y.MEDIA_ERROR,
        details: L.BUFFER_INCOMPATIBLE_CODECS_ERROR,
        fatal: !0,
        error: t,
        reason: t.message
      });
    }
  }
  createSourceBuffers() {
    const {
      tracks: t,
      sourceBuffers: e,
      mediaSource: i
    } = this;
    if (!i)
      throw new Error("createSourceBuffers called when mediaSource was null");
    for (const r in t) {
      const a = r, o = t[a];
      if (this.isPending(o)) {
        const c = this.getTrackCodec(o, a), l = `${o.container};codecs=${c}`;
        o.codec = c, this.log(`creating sourceBuffer(${l})${this.currentOp(a) ? " Queued" : ""} ${ot(o)}`);
        try {
          const h = i.addSourceBuffer(l), d = Ps(a), u = [a, h];
          e[d] = u, o.buffer = h;
        } catch (h) {
          var s;
          this.error(`error while trying to add sourceBuffer: ${h.message}`), this.shiftAndExecuteNext(a), (s = this.operationQueue) == null || s.removeBlockers(), delete this.tracks[a], this.hls.trigger(m.ERROR, {
            type: Y.MEDIA_ERROR,
            details: L.BUFFER_ADD_CODEC_ERROR,
            fatal: !1,
            error: h,
            sourceBufferName: a,
            mimeType: l,
            parent: o.id
          });
          return;
        }
        this.trackSourceBuffer(a, o);
      }
    }
    this.bufferCreated();
  }
  getTrackCodec(t, e) {
    const i = t.supplemental;
    let s = t.codec;
    i && (e === "video" || e === "audiovideo") && gi(i, "video") && (s = sc(s, i));
    const r = Gi(s, t.levelCodec);
    return r ? e.slice(0, 5) === "audio" ? Zi(r, this.appendSource) : r : "";
  }
  trackSourceBuffer(t, e) {
    const i = e.buffer;
    if (!i)
      return;
    const s = this.getTrackCodec(e, t);
    this.tracks[t] = {
      buffer: i,
      codec: s,
      container: e.container,
      levelCodec: e.levelCodec,
      supplemental: e.supplemental,
      metadata: e.metadata,
      id: e.id,
      listeners: []
    }, this.removeBufferListeners(t), this.addBufferListener(t, "updatestart", this.onSBUpdateStart), this.addBufferListener(t, "updateend", this.onSBUpdateEnd), this.addBufferListener(t, "error", this.onSBUpdateError), this.appendSource && this.addBufferListener(t, "bufferedchange", (r, a) => {
      const o = a.removedRanges;
      o != null && o.length && this.hls.trigger(m.BUFFER_FLUSHED, {
        type: r
      });
    });
  }
  get mediaSrc() {
    var t, e;
    const i = ((t = this.media) == null || (e = t.querySelector) == null ? void 0 : e.call(t, "source")) || this.media;
    return i == null ? void 0 : i.src;
  }
  onSBUpdateStart(t) {
    const e = this.currentOp(t);
    e && e.onStart();
  }
  onSBUpdateEnd(t) {
    var e;
    if (((e = this.mediaSource) == null ? void 0 : e.readyState) === "closed") {
      this.resetBuffer(t);
      return;
    }
    const i = this.currentOp(t);
    i && (i.onComplete(), this.shiftAndExecuteNext(t));
  }
  onSBUpdateError(t, e) {
    var i;
    const s = new Error(`${t} SourceBuffer error. MediaSource readyState: ${(i = this.mediaSource) == null ? void 0 : i.readyState}`);
    this.error(`${s}`, e), this.hls.trigger(m.ERROR, {
      type: Y.MEDIA_ERROR,
      details: L.BUFFER_APPENDING_ERROR,
      sourceBufferName: t,
      error: s,
      fatal: !1
    });
    const r = this.currentOp(t);
    r && r.onError(s);
  }
  updateTimestampOffset(t, e, i, s, r, a) {
    const o = e - t.timestampOffset;
    Math.abs(o) >= i && (this.log(`Updating ${s} SourceBuffer timestampOffset to ${e} (sn: ${r} cc: ${a})`), t.timestampOffset = e);
  }
  // This method must result in an updateend event; if remove is not called, onSBUpdateEnd must be called manually
  removeExecutor(t, e, i) {
    const {
      media: s,
      mediaSource: r
    } = this, a = this.tracks[t], o = a == null ? void 0 : a.buffer;
    if (!s || !r || !o) {
      this.warn(`Attempting to remove from the ${t} SourceBuffer, but it does not exist`), this.shiftAndExecuteNext(t);
      return;
    }
    const c = B(s.duration) ? s.duration : 1 / 0, l = B(r.duration) ? r.duration : 1 / 0, h = Math.max(0, e), d = Math.min(i, c, l);
    d > h && (!a.ending || a.ended) ? (a.ended = !1, this.log(`Removing [${h},${d}] from the ${t} SourceBuffer`), o.remove(h, d)) : this.shiftAndExecuteNext(t);
  }
  // This method must result in an updateend event; if append is not called, onSBUpdateEnd must be called manually
  appendExecutor(t, e) {
    const i = this.tracks[e], s = i == null ? void 0 : i.buffer;
    if (!s)
      throw new ud(`Attempting to append to the ${e} SourceBuffer, but it does not exist`);
    i.ending = !1, i.ended = !1, s.appendBuffer(t);
  }
  blockUntilOpen(t) {
    if (this.isUpdating() || this.isQueued())
      this.blockBuffers(t).catch((e) => {
        this.warn(`SourceBuffer blocked callback ${e}`), this.stepOperationQueue(this.sourceBufferTypes);
      });
    else
      try {
        t();
      } catch (e) {
        this.warn(`Callback run without blocking ${this.operationQueue} ${e}`);
      }
  }
  isUpdating() {
    return this.sourceBuffers.some(([t, e]) => t && e.updating);
  }
  isQueued() {
    return this.sourceBuffers.some(([t]) => t && !!this.currentOp(t));
  }
  isPending(t) {
    return !!t && !t.buffer;
  }
  // Enqueues an operation to each SourceBuffer queue which, upon execution, resolves a promise. When all promises
  // resolve, the onUnblocked function is executed. Functions calling this method do not need to unblock the queue
  // upon completion, since we already do it here
  blockBuffers(t, e = this.sourceBufferTypes) {
    if (!e.length)
      return this.log("Blocking operation requested, but no SourceBuffers exist"), Promise.resolve().then(t);
    const {
      operationQueue: i
    } = this, s = e.map((a) => this.appendBlocker(a));
    return e.length > 1 && !!this.blockedAudioAppend && this.unblockAudio(), Promise.all(s).then((a) => {
      i === this.operationQueue && (t(), this.stepOperationQueue(this.sourceBufferTypes));
    });
  }
  stepOperationQueue(t) {
    t.forEach((e) => {
      var i;
      const s = (i = this.tracks[e]) == null ? void 0 : i.buffer;
      !s || s.updating || this.shiftAndExecuteNext(e);
    });
  }
  append(t, e, i) {
    this.operationQueue && this.operationQueue.append(t, e, i);
  }
  appendBlocker(t) {
    if (this.operationQueue)
      return this.operationQueue.appendBlocker(t);
  }
  currentOp(t) {
    return this.operationQueue ? this.operationQueue.current(t) : null;
  }
  executeNext(t) {
    t && this.operationQueue && this.operationQueue.executeNext(t);
  }
  shiftAndExecuteNext(t) {
    this.operationQueue && this.operationQueue.shiftAndExecuteNext(t);
  }
  get pendingTrackCount() {
    return Object.keys(this.tracks).reduce((t, e) => t + (this.isPending(this.tracks[e]) ? 1 : 0), 0);
  }
  get sourceBufferCount() {
    return this.sourceBuffers.reduce((t, [e]) => t + (e ? 1 : 0), 0);
  }
  get sourceBufferTypes() {
    return this.sourceBuffers.map(([t]) => t).filter((t) => !!t);
  }
  addBufferListener(t, e, i) {
    const s = this.tracks[t];
    if (!s)
      return;
    const r = s.buffer;
    if (!r)
      return;
    const a = i.bind(this, t);
    s.listeners.push({
      event: e,
      listener: a
    }), r.addEventListener(e, a);
  }
  removeBufferListeners(t) {
    const e = this.tracks[t];
    if (!e)
      return;
    const i = e.buffer;
    i && (e.listeners.forEach((s) => {
      i.removeEventListener(s.event, s.listener);
    }), e.listeners.length = 0);
  }
}
function Vn(n) {
  const t = n.querySelectorAll("source");
  [].slice.call(t).forEach((e) => {
    n.removeChild(e);
  });
}
function gd(n, t) {
  const e = self.document.createElement("source");
  e.type = "video/mp4", e.src = t, n.appendChild(e);
}
function Ps(n) {
  return n === "audio" ? 1 : 0;
}
class Fr {
  constructor(t) {
    this.hls = void 0, this.autoLevelCapping = void 0, this.firstLevel = void 0, this.media = void 0, this.restrictedLevels = void 0, this.timer = void 0, this.clientRect = void 0, this.streamController = void 0, this.hls = t, this.autoLevelCapping = Number.POSITIVE_INFINITY, this.firstLevel = -1, this.media = null, this.restrictedLevels = [], this.timer = void 0, this.clientRect = null, this.registerListeners();
  }
  setStreamController(t) {
    this.streamController = t;
  }
  destroy() {
    this.hls && this.unregisterListener(), this.timer && this.stopCapping(), this.media = null, this.clientRect = null, this.hls = this.streamController = null;
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.FPS_DROP_LEVEL_CAPPING, this.onFpsDropLevelCapping, this), t.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.on(m.BUFFER_CODECS, this.onBufferCodecs, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this);
  }
  unregisterListener() {
    const {
      hls: t
    } = this;
    t.off(m.FPS_DROP_LEVEL_CAPPING, this.onFpsDropLevelCapping, this), t.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.off(m.BUFFER_CODECS, this.onBufferCodecs, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this);
  }
  onFpsDropLevelCapping(t, e) {
    const i = this.hls.levels[e.droppedLevel];
    this.isLevelAllowed(i) && this.restrictedLevels.push({
      bitrate: i.bitrate,
      height: i.height,
      width: i.width
    });
  }
  onMediaAttaching(t, e) {
    this.media = e.media instanceof HTMLVideoElement ? e.media : null, this.clientRect = null, this.timer && this.hls.levels.length && this.detectPlayerSize();
  }
  onManifestParsed(t, e) {
    const i = this.hls;
    this.restrictedLevels = [], this.firstLevel = e.firstLevel, i.config.capLevelToPlayerSize && e.video && this.startCapping();
  }
  onLevelsUpdated(t, e) {
    this.timer && B(this.autoLevelCapping) && this.detectPlayerSize();
  }
  // Only activate capping when playing a video stream; otherwise, multi-bitrate audio-only streams will be restricted
  // to the first level
  onBufferCodecs(t, e) {
    this.hls.config.capLevelToPlayerSize && e.video && this.startCapping();
  }
  onMediaDetaching() {
    this.stopCapping(), this.media = null;
  }
  detectPlayerSize() {
    if (this.media) {
      if (this.mediaHeight <= 0 || this.mediaWidth <= 0) {
        this.clientRect = null;
        return;
      }
      const t = this.hls.levels;
      if (t.length) {
        const e = this.hls, i = this.getMaxLevel(t.length - 1);
        i !== this.autoLevelCapping && e.logger.log(`Setting autoLevelCapping to ${i}: ${t[i].height}p@${t[i].bitrate} for media ${this.mediaWidth}x${this.mediaHeight}`), e.autoLevelCapping = i, e.autoLevelEnabled && e.autoLevelCapping > this.autoLevelCapping && this.streamController && this.streamController.nextLevelSwitch(), this.autoLevelCapping = e.autoLevelCapping;
      }
    }
  }
  /*
   * returns level should be the one with the dimensions equal or greater than the media (player) dimensions (so the video will be downscaled)
   */
  getMaxLevel(t) {
    const e = this.hls.levels;
    if (!e.length)
      return -1;
    const i = e.filter((s, r) => this.isLevelAllowed(s) && r <= t);
    return this.clientRect = null, Fr.getMaxLevelByMediaSize(i, this.mediaWidth, this.mediaHeight);
  }
  startCapping() {
    this.timer || (this.autoLevelCapping = Number.POSITIVE_INFINITY, self.clearInterval(this.timer), this.timer = self.setInterval(this.detectPlayerSize.bind(this), 1e3), this.detectPlayerSize());
  }
  stopCapping() {
    this.restrictedLevels = [], this.firstLevel = -1, this.autoLevelCapping = Number.POSITIVE_INFINITY, this.timer && (self.clearInterval(this.timer), this.timer = void 0);
  }
  getDimensions() {
    if (this.clientRect)
      return this.clientRect;
    const t = this.media, e = {
      width: 0,
      height: 0
    };
    if (t) {
      const i = t.getBoundingClientRect();
      e.width = i.width, e.height = i.height, !e.width && !e.height && (e.width = i.right - i.left || t.width || 0, e.height = i.bottom - i.top || t.height || 0);
    }
    return this.clientRect = e, e;
  }
  get mediaWidth() {
    return this.getDimensions().width * this.contentScaleFactor;
  }
  get mediaHeight() {
    return this.getDimensions().height * this.contentScaleFactor;
  }
  get contentScaleFactor() {
    let t = 1;
    if (!this.hls.config.ignoreDevicePixelRatio)
      try {
        t = self.devicePixelRatio;
      } catch {
      }
    return Math.min(t, this.hls.config.maxDevicePixelRatio);
  }
  isLevelAllowed(t) {
    return !this.restrictedLevels.some((i) => t.bitrate === i.bitrate && t.width === i.width && t.height === i.height);
  }
  static getMaxLevelByMediaSize(t, e, i) {
    if (!(t != null && t.length))
      return -1;
    const s = (o, c) => c ? o.width !== c.width || o.height !== c.height : !0;
    let r = t.length - 1;
    const a = Math.max(e, i);
    for (let o = 0; o < t.length; o += 1) {
      const c = t[o];
      if ((c.width >= a || c.height >= a) && s(c, t[o + 1])) {
        r = o;
        break;
      }
    }
    return r;
  }
}
const md = {
  /**
   * text file, such as a manifest or playlist
   */
  MANIFEST: "m",
  /**
   * audio only
   */
  AUDIO: "a",
  /**
   * video only
   */
  VIDEO: "v",
  /**
   * muxed audio and video
   */
  MUXED: "av",
  /**
   * init segment
   */
  INIT: "i",
  /**
   * caption or subtitle
   */
  CAPTION: "c",
  /**
   * ISOBMFF timed text track
   */
  TIMED_TEXT: "tt",
  /**
   * cryptographic key, license or certificate.
   */
  KEY: "k",
  /**
   * other
   */
  OTHER: "o"
}, Dt = md, pd = {
  /**
   * HTTP Live Streaming (HLS)
   */
  HLS: "h"
}, vd = pd;
class Jt {
  constructor(t, e) {
    Array.isArray(t) && (t = t.map((i) => i instanceof Jt ? i : new Jt(i))), this.value = t, this.params = e;
  }
}
const yd = "Dict";
function Ed(n) {
  return Array.isArray(n) ? JSON.stringify(n) : n instanceof Map ? "Map{}" : n instanceof Set ? "Set{}" : typeof n == "object" ? JSON.stringify(n) : String(n);
}
function Td(n, t, e, i) {
  return new Error(`failed to ${n} "${Ed(t)}" as ${e}`, {
    cause: i
  });
}
function te(n, t, e) {
  return Td("serialize", n, t, e);
}
class Ao {
  constructor(t) {
    this.description = t;
  }
}
const Wn = "Bare Item", Sd = "Boolean";
function xd(n) {
  if (typeof n != "boolean")
    throw te(n, Sd);
  return n ? "?1" : "?0";
}
function Ad(n) {
  return btoa(String.fromCharCode(...n));
}
const bd = "Byte Sequence";
function Id(n) {
  if (ArrayBuffer.isView(n) === !1)
    throw te(n, bd);
  return `:${Ad(n)}:`;
}
const Ld = "Integer";
function Rd(n) {
  return n < -999999999999999 || 999999999999999 < n;
}
function bo(n) {
  if (Rd(n))
    throw te(n, Ld);
  return n.toString();
}
function _d(n) {
  return `@${bo(n.getTime() / 1e3)}`;
}
function Io(n, t) {
  if (n < 0)
    return -Io(-n, t);
  const e = Math.pow(10, t);
  if (Math.abs(n * e % 1 - 0.5) < Number.EPSILON) {
    const s = Math.floor(n * e);
    return (s % 2 === 0 ? s : s + 1) / e;
  } else
    return Math.round(n * e) / e;
}
const Dd = "Decimal";
function wd(n) {
  const t = Io(n, 3);
  if (Math.floor(Math.abs(t)).toString().length > 12)
    throw te(n, Dd);
  const e = t.toString();
  return e.includes(".") ? e : `${e}.0`;
}
const Cd = "String", Pd = /[\x00-\x1f\x7f]+/;
function kd(n) {
  if (Pd.test(n))
    throw te(n, Cd);
  return `"${n.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
}
function Od(n) {
  return n.description || n.toString().slice(7, -1);
}
const Md = "Token";
function Yn(n) {
  const t = Od(n);
  if (/^([a-zA-Z*])([!#$%&'*+\-.^_`|~\w:/]*)$/.test(t) === !1)
    throw te(t, Md);
  return t;
}
function or(n) {
  switch (typeof n) {
    case "number":
      if (!B(n))
        throw te(n, Wn);
      return Number.isInteger(n) ? bo(n) : wd(n);
    case "string":
      return kd(n);
    case "symbol":
      return Yn(n);
    case "boolean":
      return xd(n);
    case "object":
      if (n instanceof Date)
        return _d(n);
      if (n instanceof Uint8Array)
        return Id(n);
      if (n instanceof Ao)
        return Yn(n);
    default:
      throw te(n, Wn);
  }
}
const Fd = "Key";
function lr(n) {
  if (/^[a-z*][a-z0-9\-_.*]*$/.test(n) === !1)
    throw te(n, Fd);
  return n;
}
function $r(n) {
  return n == null ? "" : Object.entries(n).map(([t, e]) => e === !0 ? `;${lr(t)}` : `;${lr(t)}=${or(e)}`).join("");
}
function Lo(n) {
  return n instanceof Jt ? `${or(n.value)}${$r(n.params)}` : or(n);
}
function $d(n) {
  return `(${n.value.map(Lo).join(" ")})${$r(n.params)}`;
}
function Nd(n, t = {
  whitespace: !0
}) {
  if (typeof n != "object" || n == null)
    throw te(n, yd);
  const e = n instanceof Map ? n.entries() : Object.entries(n), i = t != null && t.whitespace ? " " : "";
  return Array.from(e).map(([s, r]) => {
    r instanceof Jt || (r = new Jt(r));
    let a = lr(s);
    return r.value === !0 ? a += $r(r.params) : (a += "=", Array.isArray(r.value) ? a += $d(r) : a += Lo(r)), a;
  }).join(`,${i}`);
}
function Ro(n, t) {
  return Nd(n, t);
}
const zt = "CMCD-Object", ht = "CMCD-Request", Ae = "CMCD-Session", le = "CMCD-Status", Bd = {
  // Object
  br: zt,
  ab: zt,
  d: zt,
  ot: zt,
  tb: zt,
  tpb: zt,
  lb: zt,
  tab: zt,
  lab: zt,
  url: zt,
  // Request
  pb: ht,
  bl: ht,
  tbl: ht,
  dl: ht,
  ltc: ht,
  mtp: ht,
  nor: ht,
  nrr: ht,
  rc: ht,
  sn: ht,
  sta: ht,
  su: ht,
  ttfb: ht,
  ttfbb: ht,
  ttlb: ht,
  cmsdd: ht,
  cmsds: ht,
  smrt: ht,
  df: ht,
  cs: ht,
  // TODO: Which header to put the `ts` field is not defined yet.
  ts: ht,
  // Session
  cid: Ae,
  pr: Ae,
  sf: Ae,
  sid: Ae,
  st: Ae,
  v: Ae,
  msd: Ae,
  // Status
  bs: le,
  bsd: le,
  cdn: le,
  rtp: le,
  bg: le,
  pt: le,
  ec: le,
  e: le
}, Ud = {
  /**
   * keys whose values vary with each request.
   */
  REQUEST: ht
};
function Gd(n) {
  return Object.keys(n).reduce((t, e) => {
    var i;
    return (i = n[e]) === null || i === void 0 || i.forEach((s) => t[s] = e), t;
  }, {});
}
function Kd(n, t) {
  const e = {};
  if (!n)
    return e;
  const i = Object.keys(n), s = t ? Gd(t) : {};
  return i.reduce((r, a) => {
    var o;
    const c = Bd[a] || s[a] || Ud.REQUEST, l = (o = r[c]) !== null && o !== void 0 ? o : r[c] = {};
    return l[a] = n[a], r;
  }, e);
}
function Hd(n) {
  return ["ot", "sf", "st", "e", "sta"].includes(n);
}
function Vd(n) {
  return typeof n == "number" ? B(n) : n != null && n !== "" && n !== !1;
}
const _o = "event";
function Wd(n, t) {
  const e = new URL(n), i = new URL(t);
  if (e.origin !== i.origin)
    return n;
  const s = e.pathname.split("/").slice(1), r = i.pathname.split("/").slice(1, -1);
  for (; s[0] === r[0]; )
    s.shift(), r.shift();
  for (; r.length; )
    r.shift(), s.unshift("..");
  return s.join("/") + e.search + e.hash;
}
const Yi = (n) => Math.round(n), cr = (n, t) => Array.isArray(n) ? n.map((e) => cr(e, t)) : n instanceof Jt && typeof n.value == "string" ? new Jt(cr(n.value, t), n.params) : (t.baseUrl && (n = Wd(n, t.baseUrl)), t.version === 1 ? encodeURIComponent(n) : n), ki = (n) => Yi(n / 100) * 100, Yd = (n, t) => {
  let e = n;
  return t.version >= 2 && (n instanceof Jt && typeof n.value == "string" ? e = new Jt([n]) : typeof n == "string" && (e = [n])), cr(e, t);
}, zd = {
  /**
   * Bitrate (kbps) rounded integer
   */
  br: Yi,
  /**
   * Duration (milliseconds) rounded integer
   */
  d: Yi,
  /**
   * Buffer Length (milliseconds) rounded nearest 100ms
   */
  bl: ki,
  /**
   * Deadline (milliseconds) rounded nearest 100ms
   */
  dl: ki,
  /**
   * Measured Throughput (kbps) rounded nearest 100kbps
   */
  mtp: ki,
  /**
   * Next Object Request URL encoded
   */
  nor: Yd,
  /**
   * Requested maximum throughput (kbps) rounded nearest 100kbps
   */
  rtp: ki,
  /**
   * Top Bitrate (kbps) rounded integer
   */
  tb: Yi
}, Do = "request", wo = "response", Nr = ["ab", "bg", "bl", "br", "bs", "bsd", "cdn", "cid", "cs", "df", "ec", "lab", "lb", "ltc", "msd", "mtp", "pb", "pr", "pt", "sf", "sid", "sn", "st", "sta", "tab", "tb", "tbl", "tpb", "ts", "v"], jd = ["e"], qd = /^[a-zA-Z0-9-.]+-[a-zA-Z0-9-.]+$/;
function gs(n) {
  return qd.test(n);
}
function Xd(n) {
  return Nr.includes(n) || jd.includes(n) || gs(n);
}
const Co = ["d", "dl", "nor", "ot", "rtp", "su"];
function Qd(n) {
  return Nr.includes(n) || Co.includes(n) || gs(n);
}
const Zd = ["cmsdd", "cmsds", "rc", "smrt", "ttfb", "ttfbb", "ttlb", "url"];
function Jd(n) {
  return Nr.includes(n) || Co.includes(n) || Zd.includes(n) || gs(n);
}
const tu = ["bl", "br", "bs", "cid", "d", "dl", "mtp", "nor", "nrr", "ot", "pr", "rtp", "sf", "sid", "st", "su", "tb", "v"];
function eu(n) {
  return tu.includes(n) || gs(n);
}
const iu = {
  [wo]: Jd,
  [_o]: Xd,
  [Do]: Qd
};
function Po(n, t = {}) {
  const e = {};
  if (n == null || typeof n != "object")
    return e;
  const i = t.version || n.v || 1, s = t.reportingMode || Do, r = i === 1 ? eu : iu[s];
  let a = Object.keys(n).filter(r);
  const o = t.filter;
  typeof o == "function" && (a = a.filter(o));
  const c = s === wo || s === _o;
  c && !a.includes("ts") && a.push("ts"), i > 1 && !a.includes("v") && a.push("v");
  const l = nt({}, zd, t.formatters), h = {
    version: i,
    reportingMode: s,
    baseUrl: t.baseUrl
  };
  return a.sort().forEach((d) => {
    let u = n[d];
    const f = l[d];
    if (typeof f == "function" && (u = f(u, h)), d === "v") {
      if (i === 1)
        return;
      u = i;
    }
    d == "pr" && u === 1 || (c && d === "ts" && !B(u) && (u = Date.now()), Vd(u) && (Hd(d) && typeof u == "string" && (u = new Ao(u)), e[d] = u));
  }), e;
}
function su(n, t = {}) {
  const e = {};
  if (!n)
    return e;
  const i = Po(n, t), s = Kd(i, t == null ? void 0 : t.customHeaderMap);
  return Object.entries(s).reduce((r, [a, o]) => {
    const c = Ro(o, {
      whitespace: !1
    });
    return c && (r[a] = c), r;
  }, e);
}
function ru(n, t, e) {
  return nt(n, su(t, e));
}
const nu = "CMCD";
function au(n, t = {}) {
  return n ? Ro(Po(n, t), {
    whitespace: !1
  }) : "";
}
function ou(n, t = {}) {
  if (!n)
    return "";
  const e = au(n, t);
  return encodeURIComponent(e);
}
function lu(n, t = {}) {
  if (!n)
    return "";
  const e = ou(n, t);
  return `${nu}=${e}`;
}
const zn = /CMCD=[^&#]+/;
function cu(n, t, e) {
  const i = lu(t, e);
  if (!i)
    return n;
  if (zn.test(n))
    return n.replace(zn, i);
  const s = n.includes("?") ? "&" : "?";
  return `${n}${s}${i}`;
}
class hu {
  constructor(t) {
    this.hls = void 0, this.config = void 0, this.media = void 0, this.sid = void 0, this.cid = void 0, this.useHeaders = !1, this.includeKeys = void 0, this.initialized = !1, this.starved = !1, this.buffering = !0, this.audioBuffer = void 0, this.videoBuffer = void 0, this.onWaiting = () => {
      this.initialized && (this.starved = !0), this.buffering = !0;
    }, this.onPlaying = () => {
      this.initialized || (this.initialized = !0), this.buffering = !1;
    }, this.applyPlaylistData = (s) => {
      try {
        this.apply(s, {
          ot: Dt.MANIFEST,
          su: !this.initialized
        });
      } catch (r) {
        this.hls.logger.warn("Could not generate manifest CMCD data.", r);
      }
    }, this.applyFragmentData = (s) => {
      try {
        const {
          frag: r,
          part: a
        } = s, o = this.hls.levels[r.level], c = this.getObjectType(r), l = {
          d: (a || r).duration * 1e3,
          ot: c
        };
        (c === Dt.VIDEO || c === Dt.AUDIO || c == Dt.MUXED) && (l.br = o.bitrate / 1e3, l.tb = this.getTopBandwidth(c) / 1e3, l.bl = this.getBufferLength(c));
        const h = a ? this.getNextPart(a) : this.getNextFrag(r);
        h != null && h.url && h.url !== r.url && (l.nor = h.url), this.apply(s, l);
      } catch (r) {
        this.hls.logger.warn("Could not generate segment CMCD data.", r);
      }
    }, this.hls = t;
    const e = this.config = t.config, {
      cmcd: i
    } = e;
    i != null && (e.pLoader = this.createPlaylistLoader(), e.fLoader = this.createFragmentLoader(), this.sid = i.sessionId || t.sessionId, this.cid = i.contentId, this.useHeaders = i.useHeaders === !0, this.includeKeys = i.includeKeys, this.registerListeners());
  }
  registerListeners() {
    const t = this.hls;
    t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHED, this.onMediaDetached, this), t.on(m.BUFFER_CREATED, this.onBufferCreated, this);
  }
  unregisterListeners() {
    const t = this.hls;
    t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHED, this.onMediaDetached, this), t.off(m.BUFFER_CREATED, this.onBufferCreated, this);
  }
  destroy() {
    this.unregisterListeners(), this.onMediaDetached(), this.hls = this.config = this.audioBuffer = this.videoBuffer = null, this.onWaiting = this.onPlaying = this.media = null;
  }
  onMediaAttached(t, e) {
    this.media = e.media, this.media.addEventListener("waiting", this.onWaiting), this.media.addEventListener("playing", this.onPlaying);
  }
  onMediaDetached() {
    this.media && (this.media.removeEventListener("waiting", this.onWaiting), this.media.removeEventListener("playing", this.onPlaying), this.media = null);
  }
  onBufferCreated(t, e) {
    var i, s;
    this.audioBuffer = (i = e.tracks.audio) == null ? void 0 : i.buffer, this.videoBuffer = (s = e.tracks.video) == null ? void 0 : s.buffer;
  }
  /**
   * Create baseline CMCD data
   */
  createData() {
    var t;
    return {
      v: 1,
      sf: vd.HLS,
      sid: this.sid,
      cid: this.cid,
      pr: (t = this.media) == null ? void 0 : t.playbackRate,
      mtp: this.hls.bandwidthEstimate / 1e3
    };
  }
  /**
   * Apply CMCD data to a request.
   */
  apply(t, e = {}) {
    nt(e, this.createData());
    const i = e.ot === Dt.INIT || e.ot === Dt.VIDEO || e.ot === Dt.MUXED;
    this.starved && i && (e.bs = !0, e.su = !0, this.starved = !1), e.su == null && (e.su = this.buffering);
    const {
      includeKeys: s
    } = this;
    s && (e = Object.keys(e).reduce((a, o) => (s.includes(o) && (a[o] = e[o]), a), {}));
    const r = {
      baseUrl: t.url
    };
    this.useHeaders ? (t.headers || (t.headers = {}), ru(t.headers, e, r)) : t.url = cu(t.url, e, r);
  }
  getNextFrag(t) {
    var e;
    const i = (e = this.hls.levels[t.level]) == null ? void 0 : e.details;
    if (i) {
      const s = t.sn - i.startSN;
      return i.fragments[s + 1];
    }
  }
  getNextPart(t) {
    var e;
    const {
      index: i,
      fragment: s
    } = t, r = (e = this.hls.levels[s.level]) == null || (e = e.details) == null ? void 0 : e.partList;
    if (r) {
      const {
        sn: a
      } = s;
      for (let o = r.length - 1; o >= 0; o--) {
        const c = r[o];
        if (c.index === i && c.fragment.sn === a)
          return r[o + 1];
      }
    }
  }
  /**
   * The CMCD object type.
   */
  getObjectType(t) {
    const {
      type: e
    } = t;
    if (e === "subtitle")
      return Dt.TIMED_TEXT;
    if (t.sn === "initSegment")
      return Dt.INIT;
    if (e === "audio")
      return Dt.AUDIO;
    if (e === "main")
      return this.hls.audioTracks.length ? Dt.VIDEO : Dt.MUXED;
  }
  /**
   * Get the highest bitrate.
   */
  getTopBandwidth(t) {
    let e = 0, i;
    const s = this.hls;
    if (t === Dt.AUDIO)
      i = s.audioTracks;
    else {
      const r = s.maxAutoLevel, a = r > -1 ? r + 1 : s.levels.length;
      i = s.levels.slice(0, a);
    }
    return i.forEach((r) => {
      r.bitrate > e && (e = r.bitrate);
    }), e > 0 ? e : NaN;
  }
  /**
   * Get the buffer length for a media type in milliseconds
   */
  getBufferLength(t) {
    const e = this.media, i = t === Dt.AUDIO ? this.audioBuffer : this.videoBuffer;
    return !i || !e ? NaN : q.bufferInfo(i, e.currentTime, this.config.maxBufferHole).len * 1e3;
  }
  /**
   * Create a playlist loader
   */
  createPlaylistLoader() {
    const {
      pLoader: t
    } = this.config, e = this.applyPlaylistData, i = t || this.config.loader;
    return class {
      constructor(r) {
        this.loader = void 0, this.loader = new i(r);
      }
      get stats() {
        return this.loader.stats;
      }
      get context() {
        return this.loader.context;
      }
      destroy() {
        this.loader.destroy();
      }
      abort() {
        this.loader.abort();
      }
      load(r, a, o) {
        e(r), this.loader.load(r, a, o);
      }
    };
  }
  /**
   * Create a playlist loader
   */
  createFragmentLoader() {
    const {
      fLoader: t
    } = this.config, e = this.applyFragmentData, i = t || this.config.loader;
    return class {
      constructor(r) {
        this.loader = void 0, this.loader = new i(r);
      }
      get stats() {
        return this.loader.stats;
      }
      get context() {
        return this.loader.context;
      }
      destroy() {
        this.loader.destroy();
      }
      abort() {
        this.loader.abort();
      }
      load(r, a, o) {
        e(r), this.loader.load(r, a, o);
      }
    };
  }
}
const du = 3e5;
class uu extends Bt {
  constructor(t) {
    super("content-steering", t.logger), this.hls = void 0, this.loader = null, this.uri = null, this.pathwayId = ".", this._pathwayPriority = null, this.timeToLoad = 300, this.reloadTimer = -1, this.updated = 0, this.started = !1, this.enabled = !0, this.levels = null, this.audioTracks = null, this.subtitleTracks = null, this.penalizedPathways = {}, this.hls = t, this.registerListeners();
  }
  registerListeners() {
    const t = this.hls;
    t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const t = this.hls;
    t && (t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.ERROR, this.onError, this));
  }
  pathways() {
    return (this.levels || []).reduce((t, e) => (t.indexOf(e.pathwayId) === -1 && t.push(e.pathwayId), t), []);
  }
  get pathwayPriority() {
    return this._pathwayPriority;
  }
  set pathwayPriority(t) {
    this.updatePathwayPriority(t);
  }
  startLoad() {
    if (this.started = !0, this.clearTimeout(), this.enabled && this.uri) {
      if (this.updated) {
        const t = this.timeToLoad * 1e3 - (performance.now() - this.updated);
        if (t > 0) {
          this.scheduleRefresh(this.uri, t);
          return;
        }
      }
      this.loadSteeringManifest(this.uri);
    }
  }
  stopLoad() {
    this.started = !1, this.loader && (this.loader.destroy(), this.loader = null), this.clearTimeout();
  }
  clearTimeout() {
    this.reloadTimer !== -1 && (self.clearTimeout(this.reloadTimer), this.reloadTimer = -1);
  }
  destroy() {
    this.unregisterListeners(), this.stopLoad(), this.hls = null, this.levels = this.audioTracks = this.subtitleTracks = null;
  }
  removeLevel(t) {
    const e = this.levels;
    e && (this.levels = e.filter((i) => i !== t));
  }
  onManifestLoading() {
    this.stopLoad(), this.enabled = !0, this.timeToLoad = 300, this.updated = 0, this.uri = null, this.pathwayId = ".", this.levels = this.audioTracks = this.subtitleTracks = null;
  }
  onManifestLoaded(t, e) {
    const {
      contentSteering: i
    } = e;
    i !== null && (this.pathwayId = i.pathwayId, this.uri = i.uri, this.started && this.startLoad());
  }
  onManifestParsed(t, e) {
    this.audioTracks = e.audioTracks, this.subtitleTracks = e.subtitleTracks;
  }
  onError(t, e) {
    const {
      errorAction: i
    } = e;
    if ((i == null ? void 0 : i.action) === xt.SendAlternateToPenaltyBox && i.flags === kt.MoveAllAlternatesMatchingHost) {
      const s = this.levels;
      let r = this._pathwayPriority, a = this.pathwayId;
      if (e.context) {
        const {
          groupId: o,
          pathwayId: c,
          type: l
        } = e.context;
        o && s ? a = this.getPathwayForGroupId(o, l, a) : c && (a = c);
      }
      a in this.penalizedPathways || (this.penalizedPathways[a] = performance.now()), !r && s && (r = this.pathways()), r && r.length > 1 && (this.updatePathwayPriority(r), i.resolved = this.pathwayId !== a), e.details === L.BUFFER_APPEND_ERROR && !e.fatal ? i.resolved = !0 : i.resolved || this.warn(`Could not resolve ${e.details} ("${e.error.message}") with content-steering for Pathway: ${a} levels: ${s && s.length} priorities: ${ot(r)} penalized: ${ot(this.penalizedPathways)}`);
    }
  }
  filterParsedLevels(t) {
    this.levels = t;
    let e = this.getLevelsForPathway(this.pathwayId);
    if (e.length === 0) {
      const i = t[0].pathwayId;
      this.log(`No levels found in Pathway ${this.pathwayId}. Setting initial Pathway to "${i}"`), e = this.getLevelsForPathway(i), this.pathwayId = i;
    }
    return e.length !== t.length && this.log(`Found ${e.length}/${t.length} levels in Pathway "${this.pathwayId}"`), e;
  }
  getLevelsForPathway(t) {
    return this.levels === null ? [] : this.levels.filter((e) => t === e.pathwayId);
  }
  updatePathwayPriority(t) {
    this._pathwayPriority = t;
    let e;
    const i = this.penalizedPathways, s = performance.now();
    Object.keys(i).forEach((r) => {
      s - i[r] > du && delete i[r];
    });
    for (let r = 0; r < t.length; r++) {
      const a = t[r];
      if (a in i)
        continue;
      if (a === this.pathwayId)
        return;
      const o = this.hls.nextLoadLevel, c = this.hls.levels[o];
      if (e = this.getLevelsForPathway(a), e.length > 0) {
        this.log(`Setting Pathway to "${a}"`), this.pathwayId = a, Qa(e), this.hls.trigger(m.LEVELS_UPDATED, {
          levels: e
        });
        const l = this.hls.levels[o];
        c && l && this.levels && (l.attrs["STABLE-VARIANT-ID"] !== c.attrs["STABLE-VARIANT-ID"] && l.bitrate !== c.bitrate && this.log(`Unstable Pathways change from bitrate ${c.bitrate} to ${l.bitrate}`), this.hls.nextLoadLevel = o);
        break;
      }
    }
  }
  getPathwayForGroupId(t, e, i) {
    const s = this.getLevelsForPathway(i).concat(this.levels || []);
    for (let r = 0; r < s.length; r++)
      if (e === tt.AUDIO_TRACK && s[r].hasAudioGroup(t) || e === tt.SUBTITLE_TRACK && s[r].hasSubtitleGroup(t))
        return s[r].pathwayId;
    return i;
  }
  clonePathways(t) {
    const e = this.levels;
    if (!e)
      return;
    const i = {}, s = {};
    t.forEach((r) => {
      const {
        ID: a,
        "BASE-ID": o,
        "URI-REPLACEMENT": c
      } = r;
      if (e.some((h) => h.pathwayId === a))
        return;
      const l = this.getLevelsForPathway(o).map((h) => {
        const d = new lt(h.attrs);
        d["PATHWAY-ID"] = a;
        const u = d.AUDIO && `${d.AUDIO}_clone_${a}`, f = d.SUBTITLES && `${d.SUBTITLES}_clone_${a}`;
        u && (i[d.AUDIO] = u, d.AUDIO = u), f && (s[d.SUBTITLES] = f, d.SUBTITLES = f);
        const g = ko(h.uri, d["STABLE-VARIANT-ID"], "PER-VARIANT-URIS", c), v = new pi({
          attrs: d,
          audioCodec: h.audioCodec,
          bitrate: h.bitrate,
          height: h.height,
          name: h.name,
          url: g,
          videoCodec: h.videoCodec,
          width: h.width
        });
        if (h.audioGroups)
          for (let p = 1; p < h.audioGroups.length; p++)
            v.addGroupId("audio", `${h.audioGroups[p]}_clone_${a}`);
        if (h.subtitleGroups)
          for (let p = 1; p < h.subtitleGroups.length; p++)
            v.addGroupId("text", `${h.subtitleGroups[p]}_clone_${a}`);
        return v;
      });
      e.push(...l), jn(this.audioTracks, i, c, a), jn(this.subtitleTracks, s, c, a);
    });
  }
  loadSteeringManifest(t) {
    const e = this.hls.config, i = e.loader;
    this.loader && this.loader.destroy(), this.loader = new i(e);
    let s;
    try {
      s = new self.URL(t);
    } catch {
      this.enabled = !1, this.log(`Failed to parse Steering Manifest URI: ${t}`);
      return;
    }
    if (s.protocol !== "data:") {
      const h = (this.hls.bandwidthEstimate || e.abrEwmaDefaultEstimate) | 0;
      s.searchParams.set("_HLS_pathway", this.pathwayId), s.searchParams.set("_HLS_throughput", "" + h);
    }
    const r = {
      responseType: "json",
      url: s.href
    }, a = e.steeringManifestLoadPolicy.default, o = a.errorRetry || a.timeoutRetry || {}, c = {
      loadPolicy: a,
      timeout: a.maxLoadTimeMs,
      maxRetry: o.maxNumRetry || 0,
      retryDelay: o.retryDelayMs || 0,
      maxRetryDelay: o.maxRetryDelayMs || 0
    }, l = {
      onSuccess: (h, d, u, f) => {
        this.log(`Loaded steering manifest: "${s}"`);
        const g = h.data;
        if ((g == null ? void 0 : g.VERSION) !== 1) {
          this.log(`Steering VERSION ${g.VERSION} not supported!`);
          return;
        }
        this.updated = performance.now(), this.timeToLoad = g.TTL;
        const {
          "RELOAD-URI": v,
          "PATHWAY-CLONES": p,
          "PATHWAY-PRIORITY": y
        } = g;
        if (v)
          try {
            this.uri = new self.URL(v, s).href;
          } catch {
            this.enabled = !1, this.log(`Failed to parse Steering Manifest RELOAD-URI: ${v}`);
            return;
          }
        this.scheduleRefresh(this.uri || u.url), p && this.clonePathways(p);
        const E = {
          steeringManifest: g,
          url: s.toString()
        };
        this.hls.trigger(m.STEERING_MANIFEST_LOADED, E), y && this.updatePathwayPriority(y);
      },
      onError: (h, d, u, f) => {
        if (this.log(`Error loading steering manifest: ${h.code} ${h.text} (${d.url})`), this.stopLoad(), h.code === 410) {
          this.enabled = !1, this.log(`Steering manifest ${d.url} no longer available`);
          return;
        }
        let g = this.timeToLoad * 1e3;
        if (h.code === 429) {
          const v = this.loader;
          if (typeof (v == null ? void 0 : v.getResponseHeader) == "function") {
            const p = v.getResponseHeader("Retry-After");
            p && (g = parseFloat(p) * 1e3);
          }
          this.log(`Steering manifest ${d.url} rate limited`);
          return;
        }
        this.scheduleRefresh(this.uri || d.url, g);
      },
      onTimeout: (h, d, u) => {
        this.log(`Timeout loading steering manifest (${d.url})`), this.scheduleRefresh(this.uri || d.url);
      }
    };
    this.log(`Requesting steering manifest: ${s}`), this.loader.load(r, c, l);
  }
  scheduleRefresh(t, e = this.timeToLoad * 1e3) {
    this.clearTimeout(), this.reloadTimer = self.setTimeout(() => {
      var i;
      const s = (i = this.hls) == null ? void 0 : i.media;
      if (s && !s.ended) {
        this.loadSteeringManifest(t);
        return;
      }
      this.scheduleRefresh(t, this.timeToLoad * 1e3);
    }, e);
  }
}
function jn(n, t, e, i) {
  n && Object.keys(t).forEach((s) => {
    const r = n.filter((a) => a.groupId === s).map((a) => {
      const o = nt({}, a);
      return o.details = void 0, o.attrs = new lt(o.attrs), o.url = o.attrs.URI = ko(a.url, a.attrs["STABLE-RENDITION-ID"], "PER-RENDITION-URIS", e), o.groupId = o.attrs["GROUP-ID"] = t[s], o.attrs["PATHWAY-ID"] = i, o;
    });
    n.push(...r);
  });
}
function ko(n, t, e, i) {
  const {
    HOST: s,
    PARAMS: r,
    [e]: a
  } = i;
  let o;
  t && (o = a == null ? void 0 : a[t], o && (n = o));
  const c = new self.URL(n);
  return s && !o && (c.host = s), r && Object.keys(r).sort().forEach((l) => {
    l && c.searchParams.set(l, r[l]);
  }), c.href;
}
class ze extends Bt {
  constructor(t) {
    super("eme", t.logger), this.hls = void 0, this.config = void 0, this.media = null, this.mediaResolved = void 0, this.keyFormatPromise = null, this.keySystemAccessPromises = {}, this._requestLicenseFailureCount = 0, this.mediaKeySessions = [], this.keyIdToKeySessionPromise = {}, this.mediaKeys = null, this.setMediaKeysQueue = ze.CDMCleanupPromise ? [ze.CDMCleanupPromise] : [], this.bannedKeyIds = {}, this.onMediaEncrypted = (e) => {
      const {
        initDataType: i,
        initData: s
      } = e, r = `"${e.type}" event: init data type: "${i}"`;
      if (this.debug(r), s !== null) {
        if (!this.keyFormatPromise) {
          let a = Object.keys(this.keySystemAccessPromises);
          a.length || (a = hi(this.config));
          const o = a.map(bs).filter((c) => !!c);
          this.keyFormatPromise = this.getKeyFormatPromise(o);
        }
        this.keyFormatPromise.then((a) => {
          const o = Hi(a);
          if (i !== "sinf" || o !== ct.FAIRPLAY) {
            this.log(`Ignoring "${e.type}" event with init data type: "${i}" for selected key-system ${o}`);
            return;
          }
          let c;
          try {
            const f = vt(new Uint8Array(s)), g = Lr(JSON.parse(f).sinf), v = La(g);
            if (!v)
              throw new Error("'schm' box missing or not cbcs/cenc with schi > tenc");
            c = new Uint8Array(v.subarray(8, 24));
          } catch (f) {
            this.warn(`${r} Failed to parse sinf: ${f}`);
            return;
          }
          const l = At(c), {
            keyIdToKeySessionPromise: h,
            mediaKeySessions: d
          } = this;
          let u = h[l];
          for (let f = 0; f < d.length; f++) {
            const g = d[f], v = g.decryptdata;
            if (!v.keyId)
              continue;
            const p = At(v.keyId);
            if (ss(c, v.keyId) || v.uri.replace(/-/g, "").indexOf(l) !== -1) {
              if (u = h[p], !u)
                continue;
              if (v.pssh)
                break;
              delete h[p], v.pssh = new Uint8Array(s), v.keyId = c, u = h[l] = u.then(() => this.generateRequestWithPreferredKeySession(g, i, s, "encrypted-event-key-match")), u.catch((y) => this.handleError(y));
              break;
            }
          }
          u || this.handleError(new Error(`Key ID ${l} not encountered in playlist. Key-system sessions ${d.length}.`));
        }).catch((a) => this.handleError(a));
      }
    }, this.onWaitingForKey = (e) => {
      this.log(`"${e.type}" event`);
    }, this.hls = t, this.config = t.config, this.registerListeners();
  }
  destroy() {
    this.onDestroying(), this.onMediaDetached();
    const t = this.config;
    t.requestMediaKeySystemAccessFunc = null, t.licenseXhrSetup = t.licenseResponseCallback = void 0, t.drmSystems = t.drmSystemOptions = {}, this.hls = this.config = this.keyIdToKeySessionPromise = null, this.onMediaEncrypted = this.onWaitingForKey = null;
  }
  registerListeners() {
    this.hls.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), this.hls.on(m.MEDIA_DETACHED, this.onMediaDetached, this), this.hls.on(m.MANIFEST_LOADING, this.onManifestLoading, this), this.hls.on(m.MANIFEST_LOADED, this.onManifestLoaded, this), this.hls.on(m.DESTROYING, this.onDestroying, this);
  }
  unregisterListeners() {
    this.hls.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), this.hls.off(m.MEDIA_DETACHED, this.onMediaDetached, this), this.hls.off(m.MANIFEST_LOADING, this.onManifestLoading, this), this.hls.off(m.MANIFEST_LOADED, this.onManifestLoaded, this), this.hls.off(m.DESTROYING, this.onDestroying, this);
  }
  getLicenseServerUrl(t) {
    const {
      drmSystems: e,
      widevineLicenseUrl: i
    } = this.config, s = e == null ? void 0 : e[t];
    if (s)
      return s.licenseUrl;
    if (t === ct.WIDEVINE && i)
      return i;
  }
  getLicenseServerUrlOrThrow(t) {
    const e = this.getLicenseServerUrl(t);
    if (e === void 0)
      throw new Error(`no license server URL configured for key-system "${t}"`);
    return e;
  }
  getServerCertificateUrl(t) {
    const {
      drmSystems: e
    } = this.config, i = e == null ? void 0 : e[t];
    if (i)
      return i.serverCertificateUrl;
    this.log(`No Server Certificate in config.drmSystems["${t}"]`);
  }
  attemptKeySystemAccess(t) {
    const e = this.hls.levels, i = (a, o, c) => !!a && c.indexOf(a) === o, s = e.map((a) => a.audioCodec).filter(i), r = e.map((a) => a.videoCodec).filter(i);
    return s.length + r.length === 0 && r.push("avc1.42e01e"), new Promise((a, o) => {
      const c = (l) => {
        const h = l.shift();
        this.getMediaKeysPromise(h, s, r).then((d) => a({
          keySystem: h,
          mediaKeys: d
        })).catch((d) => {
          l.length ? c(l) : d instanceof Pt ? o(d) : o(new Pt({
            type: Y.KEY_SYSTEM_ERROR,
            details: L.KEY_SYSTEM_NO_ACCESS,
            error: d,
            fatal: !0
          }, d.message));
        });
      };
      c(t);
    });
  }
  requestMediaKeySystemAccess(t, e) {
    const {
      requestMediaKeySystemAccessFunc: i
    } = this.config;
    if (typeof i != "function") {
      let s = `Configured requestMediaKeySystemAccess is not a function ${i}`;
      return Ha === null && self.location.protocol === "http:" && (s = `navigator.requestMediaKeySystemAccess is not available over insecure protocol ${location.protocol}`), Promise.reject(new Error(s));
    }
    return i(t, e);
  }
  getMediaKeysPromise(t, e, i) {
    var s;
    const r = Yc(t, e, i, this.config.drmSystemOptions || {});
    let a = this.keySystemAccessPromises[t], o = (s = a) == null ? void 0 : s.keySystemAccess;
    if (!o) {
      this.log(`Requesting encrypted media "${t}" key-system access with config: ${ot(r)}`), o = this.requestMediaKeySystemAccess(t, r);
      const c = a = this.keySystemAccessPromises[t] = {
        keySystemAccess: o
      };
      return o.catch((l) => {
        this.log(`Failed to obtain access to key-system "${t}": ${l}`);
      }), o.then((l) => {
        this.log(`Access for key-system "${l.keySystem}" obtained`);
        const h = this.fetchServerCertificate(t);
        this.log(`Create media-keys for "${t}"`);
        const d = c.mediaKeys = l.createMediaKeys().then((u) => (this.log(`Media-keys created for "${t}"`), c.hasMediaKeys = !0, h.then((f) => f ? this.setMediaKeysServerCertificate(u, t, f) : u)));
        return d.catch((u) => {
          this.error(`Failed to create media-keys for "${t}"}: ${u}`);
        }), d;
      });
    }
    return o.then(() => a.mediaKeys);
  }
  createMediaKeySessionContext({
    decryptdata: t,
    keySystem: e,
    mediaKeys: i
  }) {
    this.log(`Creating key-system session "${e}" keyId: ${At(t.keyId || [])} keyUri: ${t.uri}`);
    const s = i.createSession(), r = {
      decryptdata: t,
      keySystem: e,
      mediaKeys: i,
      mediaKeysSession: s,
      keyStatus: "status-pending"
    };
    return this.mediaKeySessions.push(r), r;
  }
  renewKeySession(t) {
    const e = t.decryptdata;
    if (e.pssh) {
      const i = this.createMediaKeySessionContext(t), s = Oi(e), r = "cenc";
      this.keyIdToKeySessionPromise[s] = this.generateRequestWithPreferredKeySession(i, r, e.pssh.buffer, "expired");
    } else
      this.warn("Could not renew expired session. Missing pssh initData.");
    this.removeSession(t);
  }
  updateKeySession(t, e) {
    const i = t.mediaKeysSession;
    return this.log(`Updating key-session "${i.sessionId}" for keyId ${At(t.decryptdata.keyId || [])}
      } (data length: ${e.byteLength})`), i.update(e);
  }
  getSelectedKeySystemFormats() {
    return Object.keys(this.keySystemAccessPromises).map((t) => ({
      keySystem: t,
      hasMediaKeys: this.keySystemAccessPromises[t].hasMediaKeys
    })).filter(({
      hasMediaKeys: t
    }) => !!t).map(({
      keySystem: t
    }) => bs(t)).filter((t) => !!t);
  }
  getKeySystemAccess(t) {
    return this.getKeySystemSelectionPromise(t).then(({
      keySystem: e,
      mediaKeys: i
    }) => this.attemptSetMediaKeys(e, i));
  }
  selectKeySystem(t) {
    return new Promise((e, i) => {
      this.getKeySystemSelectionPromise(t).then(({
        keySystem: s
      }) => {
        const r = bs(s);
        r ? e(r) : i(new Error(`Unable to find format for key-system "${s}"`));
      }).catch(i);
    });
  }
  selectKeySystemFormat(t) {
    const e = Object.keys(t.levelkeys || {});
    return this.keyFormatPromise || (this.log(`Selecting key-system from fragment (sn: ${t.sn} ${t.type}: ${t.level}) key formats ${e.join(", ")}`), this.keyFormatPromise = this.getKeyFormatPromise(e)), this.keyFormatPromise;
  }
  getKeyFormatPromise(t) {
    const e = hi(this.config), i = t.map(Hi).filter((s) => !!s && e.indexOf(s) !== -1);
    return this.selectKeySystem(i);
  }
  getKeyStatus(t) {
    const {
      mediaKeySessions: e
    } = this;
    for (let i = 0; i < e.length; i++) {
      const s = fu(t, e[i]);
      if (s)
        return s;
    }
  }
  loadKey(t) {
    const e = t.keyInfo.decryptdata, i = Oi(e), s = this.bannedKeyIds[i];
    if (s || this.getKeyStatus(e) === "internal-error") {
      const o = qn(s || "internal-error", e);
      return this.handleError(o, t.frag), Promise.reject(o);
    }
    const r = `(keyId: ${i} format: "${e.keyFormat}" method: ${e.method} uri: ${e.uri})`;
    this.log(`Starting session for key ${r}`);
    const a = this.keyIdToKeySessionPromise[i];
    if (!a) {
      const o = this.getKeySystemForKeyPromise(e).then(({
        keySystem: c,
        mediaKeys: l
      }) => (this.throwIfDestroyed(), this.log(`Handle encrypted media sn: ${t.frag.sn} ${t.frag.type}: ${t.frag.level} using key ${r}`), this.attemptSetMediaKeys(c, l).then(() => (this.throwIfDestroyed(), this.createMediaKeySessionContext({
        keySystem: c,
        mediaKeys: l,
        decryptdata: e
      }))))).then((c) => {
        const l = "cenc", h = e.pssh ? e.pssh.buffer : null;
        return this.generateRequestWithPreferredKeySession(c, l, h, "playlist-key");
      });
      return o.catch((c) => this.handleError(c, t.frag)), this.keyIdToKeySessionPromise[i] = o, o;
    }
    return a.catch((o) => {
      if (o instanceof Pt) {
        const c = st({}, o.data);
        this.getKeyStatus(e) === "internal-error" && (c.decryptdata = e);
        const l = new Pt(c, o.message);
        this.handleError(l, t.frag);
      }
    }), a;
  }
  throwIfDestroyed(t = "Invalid state") {
    if (!this.hls)
      throw new Error("invalid state");
  }
  handleError(t, e) {
    if (this.hls)
      if (t instanceof Pt) {
        e && (t.data.frag = e);
        const i = t.data.decryptdata;
        this.error(`${t.message}${i ? ` (${At(i.keyId || [])})` : ""}`), this.hls.trigger(m.ERROR, t.data);
      } else
        this.error(t.message), this.hls.trigger(m.ERROR, {
          type: Y.KEY_SYSTEM_ERROR,
          details: L.KEY_SYSTEM_NO_KEYS,
          error: t,
          fatal: !0
        });
  }
  getKeySystemForKeyPromise(t) {
    const e = Oi(t), i = this.keyIdToKeySessionPromise[e];
    if (!i) {
      const s = Hi(t.keyFormat), r = s ? [s] : hi(this.config);
      return this.attemptKeySystemAccess(r);
    }
    return i;
  }
  getKeySystemSelectionPromise(t) {
    if (t.length || (t = hi(this.config)), t.length === 0)
      throw new Pt({
        type: Y.KEY_SYSTEM_ERROR,
        details: L.KEY_SYSTEM_NO_CONFIGURED_LICENSE,
        fatal: !0
      }, `Missing key-system license configuration options ${ot({
        drmSystems: this.config.drmSystems
      })}`);
    return this.attemptKeySystemAccess(t);
  }
  attemptSetMediaKeys(t, e) {
    if (this.mediaResolved = void 0, this.mediaKeys === e)
      return Promise.resolve();
    const i = this.setMediaKeysQueue.slice();
    this.log(`Setting media-keys for "${t}"`);
    const s = Promise.all(i).then(() => this.media ? this.media.setMediaKeys(e) : new Promise((r, a) => {
      this.mediaResolved = () => {
        if (this.mediaResolved = void 0, !this.media)
          return a(new Error("Attempted to set mediaKeys without media element attached"));
        this.mediaKeys = e, this.media.setMediaKeys(e).then(r).catch(a);
      };
    }));
    return this.mediaKeys = e, this.setMediaKeysQueue.push(s), s.then(() => {
      this.log(`Media-keys set for "${t}"`), i.push(s), this.setMediaKeysQueue = this.setMediaKeysQueue.filter((r) => i.indexOf(r) === -1);
    });
  }
  generateRequestWithPreferredKeySession(t, e, i, s) {
    var r;
    const a = (r = this.config.drmSystems) == null || (r = r[t.keySystem]) == null ? void 0 : r.generateRequest;
    if (a)
      try {
        const g = a.call(this.hls, e, i, t);
        if (!g)
          throw new Error("Invalid response from configured generateRequest filter");
        e = g.initDataType, i = g.initData ? g.initData : null, t.decryptdata.pssh = i ? new Uint8Array(i) : null;
      } catch (g) {
        if (this.warn(g.message), this.hls && this.hls.config.debug)
          throw g;
      }
    if (i === null)
      return this.log(`Skipping key-session request for "${s}" (no initData)`), Promise.resolve(t);
    const o = Oi(t.decryptdata), c = t.decryptdata.uri;
    this.log(`Generating key-session request for "${s}" keyId: ${o} URI: ${c} (init data type: ${e} length: ${i.byteLength})`);
    const l = new _r(), h = t._onmessage = (g) => {
      const v = t.mediaKeysSession;
      if (!v) {
        l.emit("error", new Error("invalid state"));
        return;
      }
      const {
        messageType: p,
        message: y
      } = g;
      this.log(`"${p}" message event for session "${v.sessionId}" message size: ${y.byteLength}`), p === "license-request" || p === "license-renewal" ? this.renewLicense(t, y).catch((E) => {
        l.eventNames().length ? l.emit("error", E) : this.handleError(E);
      }) : p === "license-release" ? t.keySystem === ct.FAIRPLAY && this.updateKeySession(t, er("acknowledged")).then(() => this.removeSession(t)).catch((E) => this.handleError(E)) : this.warn(`unhandled media key message type "${p}"`);
    }, d = (g, v) => {
      v.keyStatus = g;
      let p;
      g.startsWith("usable") ? l.emit("resolved") : g === "internal-error" || g === "output-restricted" || g === "output-downscaled" ? p = qn(g, v.decryptdata) : g === "expired" ? p = new Error(`key expired (keyId: ${o})`) : g === "released" ? p = new Error("key released") : g === "status-pending" || this.warn(`unhandled key status change "${g}" (keyId: ${o})`), p && (l.eventNames().length ? l.emit("error", p) : this.handleError(p));
    }, u = t._onkeystatuseschange = (g) => {
      if (!t.mediaKeysSession) {
        l.emit("error", new Error("invalid state"));
        return;
      }
      const p = this.getKeyStatuses(t);
      if (!Object.keys(p).some((S) => p[S] !== "status-pending"))
        return;
      if (p[o] === "expired") {
        this.log(`Expired key ${ot(p)} in key-session "${t.mediaKeysSession.sessionId}"`), this.renewKeySession(t);
        return;
      }
      let E = p[o];
      if (E)
        d(E, t);
      else {
        var T;
        t.keyStatusTimeouts || (t.keyStatusTimeouts = {}), (T = t.keyStatusTimeouts)[o] || (T[o] = self.setTimeout(() => {
          if (!t.mediaKeysSession || !this.mediaKeys)
            return;
          const x = this.getKeyStatus(t.decryptdata);
          if (x && x !== "status-pending")
            return this.log(`No status for keyId ${o} in key-session "${t.mediaKeysSession.sessionId}". Using session key-status ${x} from other session.`), d(x, t);
          this.log(`key status for ${o} in key-session "${t.mediaKeysSession.sessionId}" timed out after 1000ms`), E = "internal-error", d(E, t);
        }, 1e3)), this.log(`No status for keyId ${o} (${ot(p)}).`);
      }
    };
    _t(t.mediaKeysSession, "message", h), _t(t.mediaKeysSession, "keystatuseschange", u);
    const f = new Promise((g, v) => {
      l.on("error", v), l.on("resolved", g);
    });
    return t.mediaKeysSession.generateRequest(e, i).then(() => {
      this.log(`Request generated for key-session "${t.mediaKeysSession.sessionId}" keyId: ${o} URI: ${c}`);
    }).catch((g) => {
      throw new Pt({
        type: Y.KEY_SYSTEM_ERROR,
        details: L.KEY_SYSTEM_NO_SESSION,
        error: g,
        decryptdata: t.decryptdata,
        fatal: !1
      }, `Error generating key-session request: ${g}`);
    }).then(() => f).catch((g) => (l.removeAllListeners(), this.removeSession(t).then(() => {
      throw g;
    }))).then(() => (l.removeAllListeners(), t));
  }
  getKeyStatuses(t) {
    const e = {};
    return t.mediaKeysSession.keyStatuses.forEach((i, s) => {
      if (typeof s == "string" && typeof i == "object") {
        const o = s;
        s = i, i = o;
      }
      const r = "buffer" in s ? new Uint8Array(s.buffer, s.byteOffset, s.byteLength) : new Uint8Array(s);
      if (t.keySystem === ct.PLAYREADY && r.length === 16) {
        const o = At(r);
        e[o] = i, Ga(r);
      }
      const a = At(r);
      i === "internal-error" && (this.bannedKeyIds[a] = i), this.log(`key status change "${i}" for keyStatuses keyId: ${a} key-session "${t.mediaKeysSession.sessionId}"`), e[a] = i;
    }), e;
  }
  fetchServerCertificate(t) {
    const e = this.config, i = e.loader, s = new i(e), r = this.getServerCertificateUrl(t);
    return r ? (this.log(`Fetching server certificate for "${t}"`), new Promise((a, o) => {
      const c = {
        responseType: "arraybuffer",
        url: r
      }, l = e.certLoadPolicy.default, h = {
        loadPolicy: l,
        timeout: l.maxLoadTimeMs,
        maxRetry: 0,
        retryDelay: 0,
        maxRetryDelay: 0
      }, d = {
        onSuccess: (u, f, g, v) => {
          a(u.data);
        },
        onError: (u, f, g, v) => {
          o(new Pt({
            type: Y.KEY_SYSTEM_ERROR,
            details: L.KEY_SYSTEM_SERVER_CERTIFICATE_REQUEST_FAILED,
            fatal: !0,
            networkDetails: g,
            response: st({
              url: c.url,
              data: void 0
            }, u)
          }, `"${t}" certificate request failed (${r}). Status: ${u.code} (${u.text})`));
        },
        onTimeout: (u, f, g) => {
          o(new Pt({
            type: Y.KEY_SYSTEM_ERROR,
            details: L.KEY_SYSTEM_SERVER_CERTIFICATE_REQUEST_FAILED,
            fatal: !0,
            networkDetails: g,
            response: {
              url: c.url,
              data: void 0
            }
          }, `"${t}" certificate request timed out (${r})`));
        },
        onAbort: (u, f, g) => {
          o(new Error("aborted"));
        }
      };
      s.load(c, h, d);
    })) : Promise.resolve();
  }
  setMediaKeysServerCertificate(t, e, i) {
    return new Promise((s, r) => {
      t.setServerCertificate(i).then((a) => {
        this.log(`setServerCertificate ${a ? "success" : "not supported by CDM"} (${i.byteLength}) on "${e}"`), s(t);
      }).catch((a) => {
        r(new Pt({
          type: Y.KEY_SYSTEM_ERROR,
          details: L.KEY_SYSTEM_SERVER_CERTIFICATE_UPDATE_FAILED,
          error: a,
          fatal: !0
        }, a.message));
      });
    });
  }
  renewLicense(t, e) {
    return this.requestLicense(t, new Uint8Array(e)).then((i) => this.updateKeySession(t, new Uint8Array(i)).catch((s) => {
      throw new Pt({
        type: Y.KEY_SYSTEM_ERROR,
        details: L.KEY_SYSTEM_SESSION_UPDATE_FAILED,
        decryptdata: t.decryptdata,
        error: s,
        fatal: !1
      }, s.message);
    }));
  }
  unpackPlayReadyKeyMessage(t, e) {
    const i = String.fromCharCode.apply(null, new Uint16Array(e.buffer));
    if (!i.includes("PlayReadyKeyMessage"))
      return t.setRequestHeader("Content-Type", "text/xml; charset=utf-8"), e;
    const s = new DOMParser().parseFromString(i, "application/xml"), r = s.querySelectorAll("HttpHeader");
    if (r.length > 0) {
      let h;
      for (let d = 0, u = r.length; d < u; d++) {
        var a, o;
        h = r[d];
        const f = (a = h.querySelector("name")) == null ? void 0 : a.textContent, g = (o = h.querySelector("value")) == null ? void 0 : o.textContent;
        f && g && t.setRequestHeader(f, g);
      }
    }
    const c = s.querySelector("Challenge"), l = c == null ? void 0 : c.textContent;
    if (!l)
      throw new Error("Cannot find <Challenge> in key message");
    return er(atob(l));
  }
  setupLicenseXHR(t, e, i, s) {
    const r = this.config.licenseXhrSetup;
    return r ? Promise.resolve().then(() => {
      if (!i.decryptdata)
        throw new Error("Key removed");
      return r.call(this.hls, t, e, i, s);
    }).catch((a) => {
      if (!i.decryptdata)
        throw a;
      return t.open("POST", e, !0), r.call(this.hls, t, e, i, s);
    }).then((a) => (t.readyState || t.open("POST", e, !0), {
      xhr: t,
      licenseChallenge: a || s
    })) : (t.open("POST", e, !0), Promise.resolve({
      xhr: t,
      licenseChallenge: s
    }));
  }
  requestLicense(t, e) {
    const i = this.config.keyLoadPolicy.default;
    return new Promise((s, r) => {
      const a = this.getLicenseServerUrlOrThrow(t.keySystem);
      this.log(`Sending license request to URL: ${a}`);
      const o = new XMLHttpRequest();
      o.responseType = "arraybuffer", o.onreadystatechange = () => {
        if (!this.hls || !t.mediaKeysSession)
          return r(new Error("invalid state"));
        if (o.readyState === 4)
          if (o.status === 200) {
            this._requestLicenseFailureCount = 0;
            let c = o.response;
            this.log(`License received ${c instanceof ArrayBuffer ? c.byteLength : c}`);
            const l = this.config.licenseResponseCallback;
            if (l)
              try {
                c = l.call(this.hls, o, a, t);
              } catch (h) {
                this.error(h);
              }
            s(c);
          } else {
            const c = i.errorRetry, l = c ? c.maxNumRetry : 0;
            if (this._requestLicenseFailureCount++, this._requestLicenseFailureCount > l || o.status >= 400 && o.status < 500)
              r(new Pt({
                type: Y.KEY_SYSTEM_ERROR,
                details: L.KEY_SYSTEM_LICENSE_REQUEST_FAILED,
                decryptdata: t.decryptdata,
                fatal: !0,
                networkDetails: o,
                response: {
                  url: a,
                  data: void 0,
                  code: o.status,
                  text: o.statusText
                }
              }, `License Request XHR failed (${a}). Status: ${o.status} (${o.statusText})`));
            else {
              const h = l - this._requestLicenseFailureCount + 1;
              this.warn(`Retrying license request, ${h} attempts left`), this.requestLicense(t, e).then(s, r);
            }
          }
      }, t.licenseXhr && t.licenseXhr.readyState !== XMLHttpRequest.DONE && t.licenseXhr.abort(), t.licenseXhr = o, this.setupLicenseXHR(o, a, t, e).then(({
        xhr: c,
        licenseChallenge: l
      }) => {
        t.keySystem == ct.PLAYREADY && (l = this.unpackPlayReadyKeyMessage(c, l)), c.send(l);
      }).catch(r);
    });
  }
  onDestroying() {
    this.unregisterListeners(), this._clear();
  }
  onMediaAttached(t, e) {
    if (!this.config.emeEnabled)
      return;
    const i = e.media;
    this.media = i, _t(i, "encrypted", this.onMediaEncrypted), _t(i, "waitingforkey", this.onWaitingForKey);
    const s = this.mediaResolved;
    s ? s() : this.mediaKeys = i.mediaKeys;
  }
  onMediaDetached() {
    const t = this.media;
    t && (wt(t, "encrypted", this.onMediaEncrypted), wt(t, "waitingforkey", this.onWaitingForKey), this.media = null, this.mediaKeys = null);
  }
  _clear() {
    var t;
    this._requestLicenseFailureCount = 0, this.keyIdToKeySessionPromise = {}, this.bannedKeyIds = {};
    const e = this.mediaResolved;
    if (e && e(), !this.mediaKeys && !this.mediaKeySessions.length)
      return;
    const i = this.media, s = this.mediaKeySessions.slice();
    this.mediaKeySessions = [], this.mediaKeys = null, ue.clearKeyUriToKeyIdMap();
    const r = s.length;
    ze.CDMCleanupPromise = Promise.all(s.map((a) => this.removeSession(a)).concat((i == null || (t = i.setMediaKeys(null)) == null ? void 0 : t.catch((a) => {
      this.log(`Could not clear media keys: ${a}`), this.hls && this.hls.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.KEY_SYSTEM_DESTROY_MEDIA_KEYS_ERROR,
        fatal: !1,
        error: new Error(`Could not clear media keys: ${a}`)
      });
    })) || Promise.resolve())).catch((a) => {
      this.log(`Could not close sessions and clear media keys: ${a}`), this.hls && this.hls.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.KEY_SYSTEM_DESTROY_CLOSE_SESSION_ERROR,
        fatal: !1,
        error: new Error(`Could not close sessions and clear media keys: ${a}`)
      });
    }).then(() => {
      r && this.log("finished closing key sessions and clearing media keys");
    });
  }
  onManifestLoading() {
    this._clear();
  }
  onManifestLoaded(t, {
    sessionKeys: e
  }) {
    if (!(!e || !this.config.emeEnabled) && !this.keyFormatPromise) {
      const i = e.reduce((s, r) => (s.indexOf(r.keyFormat) === -1 && s.push(r.keyFormat), s), []);
      this.log(`Selecting key-system from session-keys ${i.join(", ")}`), this.keyFormatPromise = this.getKeyFormatPromise(i);
    }
  }
  removeSession(t) {
    const {
      mediaKeysSession: e,
      licenseXhr: i,
      decryptdata: s
    } = t;
    if (e) {
      this.log(`Remove licenses and keys and close session "${e.sessionId}" keyId: ${At((s == null ? void 0 : s.keyId) || [])}`), t._onmessage && (e.removeEventListener("message", t._onmessage), t._onmessage = void 0), t._onkeystatuseschange && (e.removeEventListener("keystatuseschange", t._onkeystatuseschange), t._onkeystatuseschange = void 0), i && i.readyState !== XMLHttpRequest.DONE && i.abort(), t.mediaKeysSession = t.decryptdata = t.licenseXhr = void 0;
      const r = this.mediaKeySessions.indexOf(t);
      r > -1 && this.mediaKeySessions.splice(r, 1);
      const {
        keyStatusTimeouts: a
      } = t;
      a && Object.keys(a).forEach((l) => self.clearTimeout(a[l]));
      const {
        drmSystemOptions: o
      } = this.config;
      return (jc(o) ? new Promise((l, h) => {
        self.setTimeout(() => h(new Error("MediaKeySession.remove() timeout")), 8e3), e.remove().then(l).catch(h);
      }) : Promise.resolve()).catch((l) => {
        this.log(`Could not remove session: ${l}`), this.hls && this.hls.trigger(m.ERROR, {
          type: Y.OTHER_ERROR,
          details: L.KEY_SYSTEM_DESTROY_REMOVE_SESSION_ERROR,
          fatal: !1,
          error: new Error(`Could not remove session: ${l}`)
        });
      }).then(() => e.close()).catch((l) => {
        this.log(`Could not close session: ${l}`), this.hls && this.hls.trigger(m.ERROR, {
          type: Y.OTHER_ERROR,
          details: L.KEY_SYSTEM_DESTROY_CLOSE_SESSION_ERROR,
          fatal: !1,
          error: new Error(`Could not close session: ${l}`)
        });
      });
    }
    return Promise.resolve();
  }
}
ze.CDMCleanupPromise = void 0;
function Oi(n) {
  if (!n)
    throw new Error("Could not read keyId of undefined decryptdata");
  if (n.keyId === null)
    throw new Error("keyId is null");
  return At(n.keyId);
}
function fu(n, t) {
  if (n.keyId && t.mediaKeysSession.keyStatuses.has(n.keyId))
    return t.mediaKeysSession.keyStatuses.get(n.keyId);
  if (n.matches(t.decryptdata))
    return t.keyStatus;
}
class Pt extends Error {
  constructor(t, e) {
    super(e), this.data = void 0, t.error || (t.error = new Error(e)), this.data = t, t.err = t.error;
  }
}
function qn(n, t) {
  const e = n === "output-restricted", i = e ? L.KEY_SYSTEM_STATUS_OUTPUT_RESTRICTED : L.KEY_SYSTEM_STATUS_INTERNAL_ERROR;
  return new Pt({
    type: Y.KEY_SYSTEM_ERROR,
    details: i,
    fatal: !1,
    decryptdata: t
  }, e ? "HDCP level output restricted" : `key status changed to "${n}"`);
}
class gu {
  constructor(t) {
    this.hls = void 0, this.isVideoPlaybackQualityAvailable = !1, this.timer = void 0, this.media = null, this.lastTime = void 0, this.lastDroppedFrames = 0, this.lastDecodedFrames = 0, this.streamController = void 0, this.hls = t, this.registerListeners();
  }
  setStreamController(t) {
    this.streamController = t;
  }
  registerListeners() {
    this.hls.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), this.hls.on(m.MEDIA_DETACHING, this.onMediaDetaching, this);
  }
  unregisterListeners() {
    this.hls.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), this.hls.off(m.MEDIA_DETACHING, this.onMediaDetaching, this);
  }
  destroy() {
    this.timer && clearInterval(this.timer), this.unregisterListeners(), this.isVideoPlaybackQualityAvailable = !1, this.media = null;
  }
  onMediaAttaching(t, e) {
    const i = this.hls.config;
    if (i.capLevelOnFPSDrop) {
      const s = e.media instanceof self.HTMLVideoElement ? e.media : null;
      this.media = s, s && typeof s.getVideoPlaybackQuality == "function" && (this.isVideoPlaybackQualityAvailable = !0), self.clearInterval(this.timer), this.timer = self.setInterval(this.checkFPSInterval.bind(this), i.fpsDroppedMonitoringPeriod);
    }
  }
  onMediaDetaching() {
    this.media = null;
  }
  checkFPS(t, e, i) {
    const s = performance.now();
    if (e) {
      if (this.lastTime) {
        const r = s - this.lastTime, a = i - this.lastDroppedFrames, o = e - this.lastDecodedFrames, c = 1e3 * a / r, l = this.hls;
        if (l.trigger(m.FPS_DROP, {
          currentDropped: a,
          currentDecoded: o,
          totalDroppedFrames: i
        }), c > 0 && a > l.config.fpsDroppedMonitoringThreshold * o) {
          let h = l.currentLevel;
          l.logger.warn("drop FPS ratio greater than max allowed value for currentLevel: " + h), h > 0 && (l.autoLevelCapping === -1 || l.autoLevelCapping >= h) && (h = h - 1, l.trigger(m.FPS_DROP_LEVEL_CAPPING, {
            level: h,
            droppedLevel: l.currentLevel
          }), l.autoLevelCapping = h, this.streamController.nextLevelSwitch());
        }
      }
      this.lastTime = s, this.lastDroppedFrames = i, this.lastDecodedFrames = e;
    }
  }
  checkFPSInterval() {
    const t = this.media;
    if (t)
      if (this.isVideoPlaybackQualityAvailable) {
        const e = t.getVideoPlaybackQuality();
        this.checkFPS(t, e.totalVideoFrames, e.droppedVideoFrames);
      } else
        this.checkFPS(t, t.webkitDecodedFrameCount, t.webkitDroppedFrameCount);
  }
}
function Oo(n, t) {
  let e;
  try {
    e = new Event("addtrack");
  } catch {
    e = document.createEvent("Event"), e.initEvent("addtrack", !1, !1);
  }
  e.track = n, t.dispatchEvent(e);
}
function Mo(n, t) {
  const e = n.mode;
  if (e === "disabled" && (n.mode = "hidden"), n.cues && !n.cues.getCueById(t.id))
    try {
      if (n.addCue(t), !n.cues.getCueById(t.id))
        throw new Error(`addCue is failed for: ${t}`);
    } catch (i) {
      rt.debug(`[texttrack-utils]: ${i}`);
      try {
        const s = new self.TextTrackCue(t.startTime, t.endTime, t.text);
        s.id = t.id, n.addCue(s);
      } catch (s) {
        rt.debug(`[texttrack-utils]: Legacy TextTrackCue fallback failed: ${s}`);
      }
    }
  e === "disabled" && (n.mode = e);
}
function Ve(n, t) {
  const e = n.mode;
  if (e === "disabled" && (n.mode = "hidden"), n.cues)
    for (let i = n.cues.length; i--; )
      t && n.cues[i].removeEventListener("enter", t), n.removeCue(n.cues[i]);
  e === "disabled" && (n.mode = e);
}
function hr(n, t, e, i) {
  const s = n.mode;
  if (s === "disabled" && (n.mode = "hidden"), n.cues && n.cues.length > 0) {
    const r = pu(n.cues, t, e);
    for (let a = 0; a < r.length; a++)
      (!i || i(r[a])) && n.removeCue(r[a]);
  }
  s === "disabled" && (n.mode = s);
}
function mu(n, t) {
  if (t <= n[0].startTime)
    return 0;
  const e = n.length - 1;
  if (t > n[e].endTime)
    return -1;
  let i = 0, s = e, r;
  for (; i <= s; )
    if (r = Math.floor((s + i) / 2), t < n[r].startTime)
      s = r - 1;
    else if (t > n[r].startTime && i < e)
      i = r + 1;
    else
      return r;
  return n[i].startTime - t < t - n[s].startTime ? i : s;
}
function pu(n, t, e) {
  const i = [], s = mu(n, t);
  if (s > -1)
    for (let r = s, a = n.length; r < a; r++) {
      const o = n[r];
      if (o.startTime >= t && o.endTime <= e)
        i.push(o);
      else if (o.startTime > e)
        return i;
    }
  return i;
}
function zi(n) {
  const t = [];
  for (let e = 0; e < n.length; e++) {
    const i = n[e];
    (i.kind === "subtitles" || i.kind === "captions") && i.label && t.push(n[e]);
  }
  return t;
}
class vu extends Mr {
  constructor(t) {
    super(t, "subtitle-track-controller"), this.media = null, this.tracks = [], this.groupIds = null, this.tracksInGroup = [], this.trackId = -1, this.currentTrack = null, this.selectDefaultTrack = !0, this.queuedDefaultTrack = -1, this.useTextTrackPolling = !1, this.subtitlePollingInterval = -1, this._subtitleDisplay = !0, this.asyncPollTrackChange = () => this.pollTrackChange(0), this.onTextTracksChanged = () => {
      if (this.useTextTrackPolling || self.clearInterval(this.subtitlePollingInterval), !this.media || !this.hls.config.renderTextTracksNatively)
        return;
      let e = null;
      const i = zi(this.media.textTracks);
      for (let r = 0; r < i.length; r++)
        if (i[r].mode === "hidden")
          e = i[r];
        else if (i[r].mode === "showing") {
          e = i[r];
          break;
        }
      const s = this.findTrackForTextTrack(e);
      this.subtitleTrack !== s && this.setSubtitleTrack(s);
    }, this.registerListeners();
  }
  destroy() {
    this.unregisterListeners(), this.tracks.length = 0, this.tracksInGroup.length = 0, this.currentTrack = null, this.onTextTracksChanged = this.asyncPollTrackChange = null, super.destroy();
  }
  get subtitleDisplay() {
    return this._subtitleDisplay;
  }
  set subtitleDisplay(t) {
    this._subtitleDisplay = t, this.trackId > -1 && this.toggleTrackModes();
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.LEVEL_LOADING, this.onLevelLoading, this), t.on(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.on(m.SUBTITLE_TRACK_LOADED, this.onSubtitleTrackLoaded, this), t.on(m.ERROR, this.onError, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.LEVEL_LOADING, this.onLevelLoading, this), t.off(m.LEVEL_SWITCHING, this.onLevelSwitching, this), t.off(m.SUBTITLE_TRACK_LOADED, this.onSubtitleTrackLoaded, this), t.off(m.ERROR, this.onError, this);
  }
  // Listen for subtitle track change, then extract the current track ID.
  onMediaAttached(t, e) {
    this.media = e.media, this.media && (this.queuedDefaultTrack > -1 && (this.subtitleTrack = this.queuedDefaultTrack, this.queuedDefaultTrack = -1), this.useTextTrackPolling = !(this.media.textTracks && "onchange" in this.media.textTracks), this.useTextTrackPolling ? this.pollTrackChange(500) : this.media.textTracks.addEventListener("change", this.asyncPollTrackChange));
  }
  pollTrackChange(t) {
    self.clearInterval(this.subtitlePollingInterval), this.subtitlePollingInterval = self.setInterval(this.onTextTracksChanged, t);
  }
  onMediaDetaching(t, e) {
    const i = this.media;
    if (!i)
      return;
    const s = !!e.transferMedia;
    if (self.clearInterval(this.subtitlePollingInterval), this.useTextTrackPolling || i.textTracks.removeEventListener("change", this.asyncPollTrackChange), this.trackId > -1 && (this.queuedDefaultTrack = this.trackId), this.subtitleTrack = -1, this.media = null, s)
      return;
    zi(i.textTracks).forEach((a) => {
      Ve(a);
    });
  }
  onManifestLoading() {
    this.tracks = [], this.groupIds = null, this.tracksInGroup = [], this.trackId = -1, this.currentTrack = null, this.selectDefaultTrack = !0;
  }
  // Fired whenever a new manifest is loaded.
  onManifestParsed(t, e) {
    this.tracks = e.subtitleTracks;
  }
  onSubtitleTrackLoaded(t, e) {
    const {
      id: i,
      groupId: s,
      details: r
    } = e, a = this.tracksInGroup[i];
    if (!a || a.groupId !== s) {
      this.warn(`Subtitle track with id:${i} and group:${s} not found in active group ${a == null ? void 0 : a.groupId}`);
      return;
    }
    const o = a.details;
    a.details = e.details, this.log(`Subtitle track ${i} "${a.name}" lang:${a.lang} group:${s} loaded [${r.startSN}-${r.endSN}]`), i === this.trackId && this.playlistLoaded(i, e, o);
  }
  onLevelLoading(t, e) {
    this.switchLevel(e.level);
  }
  onLevelSwitching(t, e) {
    this.switchLevel(e.level);
  }
  switchLevel(t) {
    const e = this.hls.levels[t];
    if (!e)
      return;
    const i = e.subtitleGroups || null, s = this.groupIds;
    let r = this.currentTrack;
    if (!i || (s == null ? void 0 : s.length) !== (i == null ? void 0 : i.length) || i != null && i.some((a) => (s == null ? void 0 : s.indexOf(a)) === -1)) {
      this.groupIds = i, this.trackId = -1, this.currentTrack = null;
      const a = this.tracks.filter((h) => !i || i.indexOf(h.groupId) !== -1);
      if (a.length)
        this.selectDefaultTrack && !a.some((h) => h.default) && (this.selectDefaultTrack = !1), a.forEach((h, d) => {
          h.id = d;
        });
      else if (!r && !this.tracksInGroup.length)
        return;
      this.tracksInGroup = a;
      const o = this.hls.config.subtitlePreference;
      if (!r && o) {
        this.selectDefaultTrack = !1;
        const h = Xt(o, a);
        if (h > -1)
          r = a[h];
        else {
          const d = Xt(o, this.tracks);
          r = this.tracks[d];
        }
      }
      let c = this.findTrackId(r);
      c === -1 && r && (c = this.findTrackId(null));
      const l = {
        subtitleTracks: a
      };
      this.log(`Updating subtitle tracks, ${a.length} track(s) found in "${i == null ? void 0 : i.join(",")}" group-id`), this.hls.trigger(m.SUBTITLE_TRACKS_UPDATED, l), c !== -1 && this.trackId === -1 && this.setSubtitleTrack(c);
    }
  }
  findTrackId(t) {
    const e = this.tracksInGroup, i = this.selectDefaultTrack;
    for (let s = 0; s < e.length; s++) {
      const r = e[s];
      if (!(i && !r.default || !i && !t) && (!t || _e(r, t)))
        return s;
    }
    if (t) {
      for (let s = 0; s < e.length; s++) {
        const r = e[s];
        if (Ti(t.attrs, r.attrs, ["LANGUAGE", "ASSOC-LANGUAGE", "CHARACTERISTICS"]))
          return s;
      }
      for (let s = 0; s < e.length; s++) {
        const r = e[s];
        if (Ti(t.attrs, r.attrs, ["LANGUAGE"]))
          return s;
      }
    }
    return -1;
  }
  findTrackForTextTrack(t) {
    if (t) {
      const e = this.tracksInGroup;
      for (let i = 0; i < e.length; i++) {
        const s = e[i];
        if (ar(s, t))
          return i;
      }
    }
    return -1;
  }
  onError(t, e) {
    e.fatal || !e.context || e.context.type === tt.SUBTITLE_TRACK && e.context.id === this.trackId && (!this.groupIds || this.groupIds.indexOf(e.context.groupId) !== -1) && this.checkRetry(e);
  }
  get allSubtitleTracks() {
    return this.tracks;
  }
  /** get alternate subtitle tracks list from playlist **/
  get subtitleTracks() {
    return this.tracksInGroup;
  }
  /** get/set index of the selected subtitle track (based on index in subtitle track lists) **/
  get subtitleTrack() {
    return this.trackId;
  }
  set subtitleTrack(t) {
    this.selectDefaultTrack = !1, this.setSubtitleTrack(t);
  }
  setSubtitleOption(t) {
    if (this.hls.config.subtitlePreference = t, t) {
      if (t.id === -1)
        return this.setSubtitleTrack(-1), null;
      const e = this.allSubtitleTracks;
      if (this.selectDefaultTrack = !1, e.length) {
        const i = this.currentTrack;
        if (i && _e(t, i))
          return i;
        const s = Xt(t, this.tracksInGroup);
        if (s > -1) {
          const r = this.tracksInGroup[s];
          return this.setSubtitleTrack(s), r;
        } else {
          if (i)
            return null;
          {
            const r = Xt(t, e);
            if (r > -1)
              return e[r];
          }
        }
      }
    }
    return null;
  }
  loadPlaylist(t) {
    super.loadPlaylist(), this.shouldLoadPlaylist(this.currentTrack) && this.scheduleLoading(this.currentTrack, t);
  }
  loadingPlaylist(t, e) {
    super.loadingPlaylist(t, e);
    const i = t.id, s = t.groupId, r = this.getUrlWithDirectives(t.url, e), a = t.details, o = a == null ? void 0 : a.age;
    this.log(`Loading subtitle ${i} "${t.name}" lang:${t.lang} group:${s}${(e == null ? void 0 : e.msn) !== void 0 ? " at sn " + e.msn + " part " + e.part : ""}${o && a.live ? " age " + o.toFixed(1) + (a.type && " " + a.type || "") : ""} ${r}`), this.hls.trigger(m.SUBTITLE_TRACK_LOADING, {
      url: r,
      id: i,
      groupId: s,
      deliveryDirectives: e || null,
      track: t
    });
  }
  /**
   * Disables the old subtitleTrack and sets current mode on the next subtitleTrack.
   * This operates on the DOM textTracks.
   * A value of -1 will disable all subtitle tracks.
   */
  toggleTrackModes() {
    const {
      media: t
    } = this;
    if (!t)
      return;
    const e = zi(t.textTracks), i = this.currentTrack;
    let s;
    if (i && (s = e.filter((r) => ar(i, r))[0], s || this.warn(`Unable to find subtitle TextTrack with name "${i.name}" and language "${i.lang}"`)), [].slice.call(e).forEach((r) => {
      r.mode !== "disabled" && r !== s && (r.mode = "disabled");
    }), s) {
      const r = this.subtitleDisplay ? "showing" : "hidden";
      s.mode !== r && (s.mode = r);
    }
  }
  /**
   * This method is responsible for validating the subtitle index and periodically reloading if live.
   * Dispatches the SUBTITLE_TRACK_SWITCH event, which instructs the subtitle-stream-controller to load the selected track.
   */
  setSubtitleTrack(t) {
    const e = this.tracksInGroup;
    if (!this.media) {
      this.queuedDefaultTrack = t;
      return;
    }
    if (t < -1 || t >= e.length || !B(t)) {
      this.warn(`Invalid subtitle track id: ${t}`);
      return;
    }
    this.selectDefaultTrack = !1;
    const i = this.currentTrack, s = e[t] || null;
    if (this.trackId = t, this.currentTrack = s, this.toggleTrackModes(), !s) {
      this.hls.trigger(m.SUBTITLE_TRACK_SWITCH, {
        id: t
      });
      return;
    }
    const r = !!s.details && !s.details.live;
    if (t === this.trackId && s === i && r)
      return;
    this.log(`Switching to subtitle-track ${t}` + (s ? ` "${s.name}" lang:${s.lang} group:${s.groupId}` : ""));
    const {
      id: a,
      groupId: o = "",
      name: c,
      type: l,
      url: h
    } = s;
    this.hls.trigger(m.SUBTITLE_TRACK_SWITCH, {
      id: a,
      groupId: o,
      name: c,
      type: l,
      url: h
    });
    const d = this.switchParams(s.url, i == null ? void 0 : i.details, s.details);
    this.loadPlaylist(d);
  }
}
function yu() {
  try {
    return crypto.randomUUID();
  } catch {
    try {
      const t = URL.createObjectURL(new Blob()), e = t.toString();
      return URL.revokeObjectURL(t), e.slice(e.lastIndexOf("/") + 1);
    } catch {
      let e = (/* @__PURE__ */ new Date()).getTime();
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (s) => {
        const r = (e + Math.random() * 16) % 16 | 0;
        return e = Math.floor(e / 16), (s == "x" ? r : r & 3 | 8).toString(16);
      });
    }
  }
}
function fi(n) {
  let t = 5381, e = n.length;
  for (; e; )
    t = t * 33 ^ n.charCodeAt(--e);
  return (t >>> 0).toString();
}
const je = 0.025;
let os = /* @__PURE__ */ (function(n) {
  return n[n.Point = 0] = "Point", n[n.Range = 1] = "Range", n;
})({});
function Eu(n, t, e) {
  return `${n.identifier}-${e + 1}-${fi(t)}`;
}
class Tu {
  constructor(t, e) {
    this.base = void 0, this._duration = null, this._timelineStart = null, this.appendInPlaceDisabled = void 0, this.appendInPlaceStarted = void 0, this.dateRange = void 0, this.hasPlayed = !1, this.cumulativeDuration = 0, this.resumeOffset = NaN, this.playoutLimit = NaN, this.restrictions = {
      skip: !1,
      jump: !1
    }, this.snapOptions = {
      out: !1,
      in: !1
    }, this.assetList = [], this.assetListLoader = void 0, this.assetListResponse = null, this.resumeAnchor = void 0, this.error = void 0, this.resetOnResume = void 0, this.base = e, this.dateRange = t, this.setDateRange(t);
  }
  setDateRange(t) {
    this.dateRange = t, this.resumeOffset = t.attr.optionalFloat("X-RESUME-OFFSET", this.resumeOffset), this.playoutLimit = t.attr.optionalFloat("X-PLAYOUT-LIMIT", this.playoutLimit), this.restrictions = t.attr.enumeratedStringList("X-RESTRICT", this.restrictions), this.snapOptions = t.attr.enumeratedStringList("X-SNAP", this.snapOptions);
  }
  reset() {
    var t;
    this.appendInPlaceStarted = !1, (t = this.assetListLoader) == null || t.destroy(), this.assetListLoader = void 0, this.supplementsPrimary || (this.assetListResponse = null, this.assetList = [], this._duration = null);
  }
  isAssetPastPlayoutLimit(t) {
    var e;
    if (t > 0 && t >= this.assetList.length)
      return !0;
    const i = this.playoutLimit;
    return t <= 0 || isNaN(i) ? !1 : i === 0 ? !0 : (((e = this.assetList[t]) == null ? void 0 : e.startOffset) || 0) > i;
  }
  findAssetIndex(t) {
    return this.assetList.indexOf(t);
  }
  get identifier() {
    return this.dateRange.id;
  }
  get startDate() {
    return this.dateRange.startDate;
  }
  get startTime() {
    const t = this.dateRange.startTime;
    if (this.snapOptions.out) {
      const e = this.dateRange.tagAnchor;
      if (e)
        return ks(t, e);
    }
    return t;
  }
  get startOffset() {
    return this.cue.pre ? 0 : this.startTime;
  }
  get startIsAligned() {
    if (this.startTime === 0 || this.snapOptions.out)
      return !0;
    const t = this.dateRange.tagAnchor;
    if (t) {
      const e = this.dateRange.startTime, i = ks(e, t);
      return e - i < 0.1;
    }
    return !1;
  }
  get resumptionOffset() {
    const t = this.resumeOffset, e = B(t) ? t : this.duration;
    return this.cumulativeDuration + e;
  }
  get resumeTime() {
    const t = this.startOffset + this.resumptionOffset;
    if (this.snapOptions.in) {
      const e = this.resumeAnchor;
      if (e)
        return ks(t, e);
    }
    return t;
  }
  get appendInPlace() {
    return this.appendInPlaceStarted ? !0 : this.appendInPlaceDisabled ? !1 : !!(!this.cue.once && !this.cue.pre && // preroll starts at startPosition before startPosition is known (live)
    this.startIsAligned && (isNaN(this.playoutLimit) && isNaN(this.resumeOffset) || this.resumeOffset && this.duration && Math.abs(this.resumeOffset - this.duration) < je));
  }
  set appendInPlace(t) {
    if (this.appendInPlaceStarted) {
      this.resetOnResume = !t;
      return;
    }
    this.appendInPlaceDisabled = !t;
  }
  // Extended timeline start time
  get timelineStart() {
    return this._timelineStart !== null ? this._timelineStart : this.startTime;
  }
  set timelineStart(t) {
    this._timelineStart = t;
  }
  get duration() {
    const t = this.playoutLimit;
    let e;
    return this._duration !== null ? e = this._duration : this.dateRange.duration ? e = this.dateRange.duration : e = this.dateRange.plannedDuration || 0, !isNaN(t) && t < e && (e = t), e;
  }
  set duration(t) {
    this._duration = t;
  }
  get cue() {
    return this.dateRange.cue;
  }
  get timelineOccupancy() {
    return this.dateRange.attr["X-TIMELINE-OCCUPIES"] === "RANGE" ? os.Range : os.Point;
  }
  get supplementsPrimary() {
    return this.dateRange.attr["X-TIMELINE-STYLE"] === "PRIMARY";
  }
  get contentMayVary() {
    return this.dateRange.attr["X-CONTENT-MAY-VARY"] !== "NO";
  }
  get assetUrl() {
    return this.dateRange.attr["X-ASSET-URI"];
  }
  get assetListUrl() {
    return this.dateRange.attr["X-ASSET-LIST"];
  }
  get baseUrl() {
    return this.base.url;
  }
  get assetListLoaded() {
    return this.assetList.length > 0 || this.assetListResponse !== null;
  }
  toString() {
    return Su(this);
  }
}
function ks(n, t) {
  return n - t.start < t.duration / 2 && !(Math.abs(n - (t.start + t.duration)) < je) ? t.start : t.start + t.duration;
}
function Fo(n, t, e) {
  const i = new self.URL(n, e);
  return i.protocol !== "data:" && i.searchParams.set("_HLS_primary_id", t), i;
}
function Os(n, t) {
  for (; (e = n.assetList[++t]) != null && e.error; )
    var e;
  return t;
}
function Su(n) {
  return `["${n.identifier}" ${n.cue.pre ? "<pre>" : n.cue.post ? "<post>" : ""}${n.timelineStart.toFixed(2)}-${n.resumeTime.toFixed(2)}]`;
}
function He(n) {
  const t = n.timelineStart, e = n.duration || 0;
  return `["${n.identifier}" ${t.toFixed(2)}-${(t + e).toFixed(2)}]`;
}
class xu {
  constructor(t, e, i, s) {
    this.hls = void 0, this.interstitial = void 0, this.assetItem = void 0, this.tracks = null, this.hasDetails = !1, this.mediaAttached = null, this._currentTime = void 0, this._bufferedEosTime = void 0, this.checkPlayout = () => {
      this.reachedPlayout(this.currentTime) && this.hls && this.hls.trigger(m.PLAYOUT_LIMIT_REACHED, {});
    };
    const r = this.hls = new t(e);
    this.interstitial = i, this.assetItem = s;
    const a = () => {
      this.hasDetails = !0;
    };
    r.once(m.LEVEL_LOADED, a), r.once(m.AUDIO_TRACK_LOADED, a), r.once(m.SUBTITLE_TRACK_LOADED, a), r.on(m.MEDIA_ATTACHING, (o, {
      media: c
    }) => {
      this.removeMediaListeners(), this.mediaAttached = c, this.interstitial.playoutLimit && (c.addEventListener("timeupdate", this.checkPlayout), this.appendInPlace && r.on(m.BUFFER_APPENDED, () => {
        const h = this.bufferedEnd;
        this.reachedPlayout(h) && (this._bufferedEosTime = h, r.trigger(m.BUFFERED_TO_END, void 0));
      }));
    });
  }
  get appendInPlace() {
    return this.interstitial.appendInPlace;
  }
  loadSource() {
    const t = this.hls;
    if (t)
      if (t.url)
        t.levels.length && !t.started && t.startLoad(-1, !0);
      else {
        let e = this.assetItem.uri;
        try {
          e = Fo(e, t.config.primarySessionId || "").href;
        } catch {
        }
        t.loadSource(e);
      }
  }
  bufferedInPlaceToEnd(t) {
    var e;
    if (!this.appendInPlace)
      return !1;
    if ((e = this.hls) != null && e.bufferedToEnd)
      return !0;
    if (!t)
      return !1;
    const i = Math.min(this._bufferedEosTime || 1 / 0, this.duration), s = this.timelineOffset, r = q.bufferInfo(t, s, 0);
    return this.getAssetTime(r.end) >= i - 0.02;
  }
  reachedPlayout(t) {
    const i = this.interstitial.playoutLimit;
    return this.startOffset + t >= i;
  }
  get destroyed() {
    var t;
    return !((t = this.hls) != null && t.userConfig);
  }
  get assetId() {
    return this.assetItem.identifier;
  }
  get interstitialId() {
    return this.assetItem.parentIdentifier;
  }
  get media() {
    var t;
    return ((t = this.hls) == null ? void 0 : t.media) || null;
  }
  get bufferedEnd() {
    const t = this.media || this.mediaAttached;
    if (!t)
      return this._bufferedEosTime ? this._bufferedEosTime : this.currentTime;
    const e = q.bufferInfo(t, t.currentTime, 1e-3);
    return this.getAssetTime(e.end);
  }
  get currentTime() {
    const t = this.media || this.mediaAttached;
    return t ? this.getAssetTime(t.currentTime) : this._currentTime || 0;
  }
  get duration() {
    const t = this.assetItem.duration;
    if (!t)
      return 0;
    const e = this.interstitial.playoutLimit;
    if (e) {
      const i = e - this.startOffset;
      if (i > 0 && i < t)
        return i;
    }
    return t;
  }
  get remaining() {
    const t = this.duration;
    return t ? Math.max(0, t - this.currentTime) : 0;
  }
  get startOffset() {
    return this.assetItem.startOffset;
  }
  get timelineOffset() {
    var t;
    return ((t = this.hls) == null ? void 0 : t.config.timelineOffset) || 0;
  }
  set timelineOffset(t) {
    const e = this.timelineOffset;
    if (t !== e) {
      const i = t - e;
      if (Math.abs(i) > 1 / 9e4 && this.hls) {
        if (this.hasDetails)
          throw new Error("Cannot set timelineOffset after playlists are loaded");
        this.hls.config.timelineOffset = t;
      }
    }
  }
  getAssetTime(t) {
    const e = this.timelineOffset, i = this.duration;
    return Math.min(Math.max(0, t - e), i);
  }
  removeMediaListeners() {
    const t = this.mediaAttached;
    t && (this._currentTime = t.currentTime, this.bufferSnapShot(), t.removeEventListener("timeupdate", this.checkPlayout));
  }
  bufferSnapShot() {
    if (this.mediaAttached) {
      var t;
      (t = this.hls) != null && t.bufferedToEnd && (this._bufferedEosTime = this.bufferedEnd);
    }
  }
  destroy() {
    this.removeMediaListeners(), this.hls && this.hls.destroy(), this.hls = null, this.tracks = this.mediaAttached = this.checkPlayout = null;
  }
  attachMedia(t) {
    var e;
    this.loadSource(), (e = this.hls) == null || e.attachMedia(t);
  }
  detachMedia() {
    var t;
    this.removeMediaListeners(), this.mediaAttached = null, (t = this.hls) == null || t.detachMedia();
  }
  resumeBuffering() {
    var t;
    (t = this.hls) == null || t.resumeBuffering();
  }
  pauseBuffering() {
    var t;
    (t = this.hls) == null || t.pauseBuffering();
  }
  transferMedia() {
    var t;
    return this.bufferSnapShot(), ((t = this.hls) == null ? void 0 : t.transferMedia()) || null;
  }
  resetDetails() {
    const t = this.hls;
    if (t && this.hasDetails) {
      t.stopLoad();
      const e = (i) => delete i.details;
      t.levels.forEach(e), t.allAudioTracks.forEach(e), t.allSubtitleTracks.forEach(e), this.hasDetails = !1;
    }
  }
  on(t, e, i) {
    var s;
    (s = this.hls) == null || s.on(t, e);
  }
  once(t, e, i) {
    var s;
    (s = this.hls) == null || s.once(t, e);
  }
  off(t, e, i) {
    var s;
    (s = this.hls) == null || s.off(t, e);
  }
  toString() {
    var t;
    return `HlsAssetPlayer: ${He(this.assetItem)} ${(t = this.hls) == null ? void 0 : t.sessionId} ${this.appendInPlace ? "append-in-place" : ""}`;
  }
}
const Xn = 0.033;
class Au extends Bt {
  constructor(t, e) {
    super("interstitials-sched", e), this.onScheduleUpdate = void 0, this.eventMap = {}, this.events = null, this.items = null, this.durations = {
      primary: 0,
      playout: 0,
      integrated: 0
    }, this.onScheduleUpdate = t;
  }
  destroy() {
    this.reset(), this.onScheduleUpdate = null;
  }
  reset() {
    this.eventMap = {}, this.setDurations(0, 0, 0), this.events && this.events.forEach((t) => t.reset()), this.events = this.items = null;
  }
  resetErrorsInRange(t, e) {
    return this.events ? this.events.reduce((i, s) => t <= s.startOffset && e > s.startOffset ? (delete s.error, i + 1) : i, 0) : 0;
  }
  get duration() {
    const t = this.items;
    return t ? t[t.length - 1].end : 0;
  }
  get length() {
    return this.items ? this.items.length : 0;
  }
  getEvent(t) {
    return t && this.eventMap[t] || null;
  }
  hasEvent(t) {
    return t in this.eventMap;
  }
  findItemIndex(t, e) {
    if (t.event)
      return this.findEventIndex(t.event.identifier);
    let i = -1;
    t.nextEvent ? i = this.findEventIndex(t.nextEvent.identifier) - 1 : t.previousEvent && (i = this.findEventIndex(t.previousEvent.identifier) + 1);
    const s = this.items;
    if (s)
      for (s[i] || (e === void 0 && (e = t.start), i = this.findItemIndexAtTime(e)); i >= 0 && (r = s[i]) != null && r.event; ) {
        var r;
        i--;
      }
    return i;
  }
  findItemIndexAtTime(t, e) {
    const i = this.items;
    if (i)
      for (let s = 0; s < i.length; s++) {
        let r = i[s];
        if (e && e !== "primary" && (r = r[e]), t === r.start || t > r.start && t < r.end)
          return s;
      }
    return -1;
  }
  findJumpRestrictedIndex(t, e) {
    const i = this.items;
    if (i)
      for (let s = t; s <= e && i[s]; s++) {
        const r = i[s].event;
        if (r != null && r.restrictions.jump && !r.appendInPlace)
          return s;
      }
    return -1;
  }
  findEventIndex(t) {
    const e = this.items;
    if (e)
      for (let s = e.length; s--; ) {
        var i;
        if (((i = e[s].event) == null ? void 0 : i.identifier) === t)
          return s;
      }
    return -1;
  }
  findAssetIndex(t, e) {
    const i = t.assetList, s = i.length;
    if (s > 1)
      for (let r = 0; r < s; r++) {
        const a = i[r];
        if (!a.error) {
          const o = a.timelineStart;
          if (e === o || e > o && (e < o + (a.duration || 0) || r === s - 1))
            return r;
        }
      }
    return 0;
  }
  get assetIdAtEnd() {
    var t;
    const e = (t = this.items) == null || (t = t[this.length - 1]) == null ? void 0 : t.event;
    if (e) {
      const i = e.assetList, s = i[i.length - 1];
      if (s)
        return s.identifier;
    }
    return null;
  }
  parseInterstitialDateRanges(t, e) {
    const i = t.main.details, {
      dateRanges: s
    } = i, r = this.events, a = this.parseDateRanges(s, {
      url: i.url
    }, e), o = Object.keys(s), c = r ? r.filter((l) => !o.includes(l.identifier)) : [];
    a.length && a.sort((l, h) => {
      const d = l.cue.pre, u = l.cue.post, f = h.cue.pre, g = h.cue.post;
      if (d && !f)
        return -1;
      if (f && !d || u && !g)
        return 1;
      if (g && !u)
        return -1;
      if (!d && !f && !u && !g) {
        const v = l.startTime, p = h.startTime;
        if (v !== p)
          return v - p;
      }
      return l.dateRange.tagOrder - h.dateRange.tagOrder;
    }), this.events = a, c.forEach((l) => {
      this.removeEvent(l);
    }), this.updateSchedule(t, c);
  }
  updateSchedule(t, e = [], i = !1) {
    const s = this.events || [];
    if (s.length || e.length || this.length < 2) {
      const r = this.items, a = this.parseSchedule(s, t);
      (i || e.length || (r == null ? void 0 : r.length) !== a.length || a.some((c, l) => Math.abs(c.playout.start - r[l].playout.start) > 5e-3 || Math.abs(c.playout.end - r[l].playout.end) > 5e-3)) && (this.items = a, this.onScheduleUpdate(e, r));
    }
  }
  parseDateRanges(t, e, i) {
    const s = [], r = Object.keys(t);
    for (let a = 0; a < r.length; a++) {
      const o = r[a], c = t[o];
      if (c.isInterstitial) {
        let l = this.eventMap[o];
        l ? l.setDateRange(c) : (l = new Tu(c, e), this.eventMap[o] = l, i === !1 && (l.appendInPlace = i)), s.push(l);
      }
    }
    return s;
  }
  parseSchedule(t, e) {
    const i = [], s = e.main.details, r = s.live ? 1 / 0 : s.edge;
    let a = 0;
    if (t = t.filter((c) => !c.error && !(c.cue.once && c.hasPlayed)), t.length) {
      this.resolveOffsets(t, e);
      let c = 0, l = 0;
      if (t.forEach((h, d) => {
        const u = h.cue.pre, f = h.cue.post, g = t[d - 1] || null, v = h.appendInPlace, p = f ? r : h.startOffset, y = h.duration, E = h.timelineOccupancy === os.Range ? y : 0, T = h.resumptionOffset, S = (g == null ? void 0 : g.startTime) === p, x = p + h.cumulativeDuration;
        let D = v ? x + y : p + T;
        if (u || !f && p <= 0) {
          const _ = l;
          l += E, h.timelineStart = x;
          const R = a;
          a += y, i.push({
            event: h,
            start: x,
            end: D,
            playout: {
              start: R,
              end: a
            },
            integrated: {
              start: _,
              end: l
            }
          });
        } else if (p <= r) {
          if (!S) {
            const b = p - c;
            if (b > Xn) {
              const C = c, F = l;
              l += b;
              const U = a;
              a += b;
              const W = {
                previousEvent: t[d - 1] || null,
                nextEvent: h,
                start: C,
                end: C + b,
                playout: {
                  start: U,
                  end: a
                },
                integrated: {
                  start: F,
                  end: l
                }
              };
              i.push(W);
            } else b > 0 && g && (g.cumulativeDuration += b, i[i.length - 1].end = p);
          }
          f && (D = x), h.timelineStart = x;
          const _ = l;
          l += E;
          const R = a;
          a += y, i.push({
            event: h,
            start: x,
            end: D,
            playout: {
              start: R,
              end: a
            },
            integrated: {
              start: _,
              end: l
            }
          });
        } else
          return;
        const A = h.resumeTime;
        f || A > r ? c = r : c = A;
      }), c < r) {
        var o;
        const h = c, d = l, u = r - c;
        l += u;
        const f = a;
        a += u, i.push({
          previousEvent: ((o = i[i.length - 1]) == null ? void 0 : o.event) || null,
          nextEvent: null,
          start: c,
          end: h + u,
          playout: {
            start: f,
            end: a
          },
          integrated: {
            start: d,
            end: l
          }
        });
      }
      this.setDurations(r, a, l);
    } else
      i.push({
        previousEvent: null,
        nextEvent: null,
        start: 0,
        end: r,
        playout: {
          start: 0,
          end: r
        },
        integrated: {
          start: 0,
          end: r
        }
      }), this.setDurations(r, r, r);
    return i;
  }
  setDurations(t, e, i) {
    this.durations = {
      primary: t,
      playout: e,
      integrated: i
    };
  }
  resolveOffsets(t, e) {
    const i = e.main.details, s = i.live ? 1 / 0 : i.edge;
    let r = 0, a = -1;
    t.forEach((o, c) => {
      const l = o.cue.pre, h = o.cue.post, d = l ? 0 : h ? s : o.startTime;
      this.updateAssetDurations(o), a === d ? o.cumulativeDuration = r : (r = 0, a = d), !h && o.snapOptions.in && (o.resumeAnchor = De(null, i.fragments, o.startOffset + o.resumptionOffset, 0, 0) || void 0), o.appendInPlace && !o.appendInPlaceStarted && (this.primaryCanResumeInPlaceAt(o, e) || (o.appendInPlace = !1)), !o.appendInPlace && c + 1 < t.length && t[c + 1].startTime - t[c].resumeTime < Xn && (t[c + 1].appendInPlace = !1, t[c + 1].appendInPlace && this.warn(`Could not change append strategy for abutting event ${o}`));
      const f = B(o.resumeOffset) ? o.resumeOffset : o.duration;
      r += f;
    });
  }
  primaryCanResumeInPlaceAt(t, e) {
    const i = t.resumeTime, s = t.startTime + t.resumptionOffset;
    return Math.abs(i - s) > je ? (this.log(`"${t.identifier}" resumption ${i} not aligned with estimated timeline end ${s}`), !1) : !Object.keys(e).some((a) => {
      const o = e[a].details, c = o.edge;
      if (i >= c)
        return this.log(`"${t.identifier}" resumption ${i} past ${a} playlist end ${c}`), !1;
      const l = De(null, o.fragments, i);
      if (!l)
        return this.log(`"${t.identifier}" resumption ${i} does not align with any fragments in ${a} playlist (${o.fragStart}-${o.fragmentEnd})`), !0;
      const h = a === "audio" ? 0.175 : 0;
      return Math.abs(l.start - i) < je + h || Math.abs(l.end - i) < je + h ? !1 : (this.log(`"${t.identifier}" resumption ${i} not aligned with ${a} fragment bounds (${l.start}-${l.end} sn: ${l.sn} cc: ${l.cc})`), !0);
    });
  }
  updateAssetDurations(t) {
    if (!t.assetListLoaded)
      return;
    const e = t.timelineStart;
    let i = 0, s = !1, r = !1;
    for (let a = 0; a < t.assetList.length; a++) {
      const o = t.assetList[a], c = e + i;
      o.startOffset = i, o.timelineStart = c, s || (s = o.duration === null), r || (r = !!o.error);
      const l = o.error ? 0 : o.duration || 0;
      i += l;
    }
    s && !r ? t.duration = Math.max(i, t.duration) : t.duration = i;
  }
  removeEvent(t) {
    t.reset(), delete this.eventMap[t.identifier];
  }
}
function Kt(n) {
  return `[${n.event ? '"' + n.event.identifier + '"' : "primary"}: ${n.start.toFixed(2)}-${n.end.toFixed(2)}]`;
}
class bu {
  constructor(t) {
    this.hls = void 0, this.hls = t;
  }
  destroy() {
    this.hls = null;
  }
  loadAssetList(t, e) {
    const i = t.assetListUrl;
    let s;
    try {
      s = Fo(i, this.hls.sessionId, t.baseUrl);
    } catch (u) {
      const f = this.assignAssetListError(t, L.ASSET_LIST_LOAD_ERROR, u, i);
      this.hls.trigger(m.ERROR, f);
      return;
    }
    e && s.protocol !== "data:" && s.searchParams.set("_HLS_start_offset", "" + e);
    const r = this.hls.config, a = r.loader, o = new a(r), c = {
      responseType: "json",
      url: s.href
    }, l = r.interstitialAssetListLoadPolicy.default, h = {
      loadPolicy: l,
      timeout: l.maxLoadTimeMs,
      maxRetry: 0,
      retryDelay: 0,
      maxRetryDelay: 0
    }, d = {
      onSuccess: (u, f, g, v) => {
        const p = u.data, y = p == null ? void 0 : p.ASSETS;
        if (!Array.isArray(y)) {
          const E = this.assignAssetListError(t, L.ASSET_LIST_PARSING_ERROR, new Error("Invalid interstitial asset list"), g.url, f, v);
          this.hls.trigger(m.ERROR, E);
          return;
        }
        t.assetListResponse = p, this.hls.trigger(m.ASSET_LIST_LOADED, {
          event: t,
          assetListResponse: p,
          networkDetails: v
        });
      },
      onError: (u, f, g, v) => {
        const p = this.assignAssetListError(t, L.ASSET_LIST_LOAD_ERROR, new Error(`Error loading X-ASSET-LIST: HTTP status ${u.code} ${u.text} (${f.url})`), f.url, v, g);
        this.hls.trigger(m.ERROR, p);
      },
      onTimeout: (u, f, g) => {
        const v = this.assignAssetListError(t, L.ASSET_LIST_LOAD_TIMEOUT, new Error(`Timeout loading X-ASSET-LIST (${f.url})`), f.url, u, g);
        this.hls.trigger(m.ERROR, v);
      }
    };
    return o.load(c, h, d), this.hls.trigger(m.ASSET_LIST_LOADING, {
      event: t
    }), o;
  }
  assignAssetListError(t, e, i, s, r, a) {
    return t.error = i, {
      type: Y.NETWORK_ERROR,
      details: e,
      fatal: !1,
      interstitial: t,
      url: s,
      error: i,
      networkDetails: a,
      stats: r
    };
  }
}
function Qn(n) {
  var t;
  n == null || (t = n.play()) == null || t.catch(() => {
  });
}
function Mi(n, t) {
  return `[${n}] Advancing timeline position to ${t}`;
}
class Iu extends Bt {
  constructor(t, e) {
    super("interstitials", t.logger), this.HlsPlayerClass = void 0, this.hls = void 0, this.assetListLoader = void 0, this.mediaSelection = null, this.altSelection = null, this.media = null, this.detachedData = null, this.requiredTracks = null, this.manager = null, this.playerQueue = [], this.bufferedPos = -1, this.timelinePos = -1, this.schedule = void 0, this.playingItem = null, this.bufferingItem = null, this.waitingItem = null, this.endedItem = null, this.playingAsset = null, this.endedAsset = null, this.bufferingAsset = null, this.shouldPlay = !1, this.onPlay = () => {
      this.shouldPlay = !0;
    }, this.onPause = () => {
      this.shouldPlay = !1;
    }, this.onSeeking = () => {
      const i = this.currentTime;
      if (i === void 0 || this.playbackDisabled || !this.schedule)
        return;
      const s = i - this.timelinePos;
      if (Math.abs(s) < 1 / 7056e5)
        return;
      const a = s <= -0.01;
      this.timelinePos = i, this.bufferedPos = i;
      const o = this.playingItem;
      if (!o) {
        this.checkBuffer();
        return;
      }
      if (a && this.schedule.resetErrorsInRange(i, i - s) && this.updateSchedule(!0), this.checkBuffer(), a && i < o.start || i >= o.end) {
        var c;
        const f = this.findItemIndex(o);
        let g = this.schedule.findItemIndexAtTime(i);
        if (g === -1 && (g = f + (a ? -1 : 1), this.log(`seeked ${a ? "back " : ""}to position not covered by schedule ${i} (resolving from ${f} to ${g})`)), !this.isInterstitial(o) && (c = this.media) != null && c.paused && (this.shouldPlay = !1), !a && g > f) {
          const v = this.schedule.findJumpRestrictedIndex(f + 1, g);
          if (v > f) {
            this.setSchedulePosition(v);
            return;
          }
        }
        this.setSchedulePosition(g);
        return;
      }
      const l = this.playingAsset;
      if (!l) {
        if (this.playingLastItem && this.isInterstitial(o)) {
          const f = o.event.assetList[0];
          f && (this.endedItem = this.playingItem, this.playingItem = null, this.setScheduleToAssetAtTime(i, f));
        }
        return;
      }
      const h = l.timelineStart, d = l.duration || 0;
      if (a && i < h || i >= h + d) {
        var u;
        (u = o.event) != null && u.appendInPlace && (this.clearAssetPlayers(o.event, o), this.flushFrontBuffer(i)), this.setScheduleToAssetAtTime(i, l);
      }
    }, this.onTimeupdate = () => {
      const i = this.currentTime;
      if (i === void 0 || this.playbackDisabled)
        return;
      if (i > this.timelinePos)
        this.timelinePos = i, i > this.bufferedPos && this.checkBuffer();
      else
        return;
      const s = this.playingItem;
      if (!s || this.playingLastItem)
        return;
      if (i >= s.end) {
        this.timelinePos = s.end;
        const o = this.findItemIndex(s);
        this.setSchedulePosition(o + 1);
      }
      const r = this.playingAsset;
      if (!r)
        return;
      const a = r.timelineStart + (r.duration || 0);
      i >= a && this.setScheduleToAssetAtTime(i, r);
    }, this.onScheduleUpdate = (i, s) => {
      const r = this.schedule;
      if (!r)
        return;
      const a = this.playingItem, o = r.events || [], c = r.items || [], l = r.durations, h = i.map((v) => v.identifier), d = !!(o.length || h.length);
      (d || s) && this.log(`INTERSTITIALS_UPDATED (${o.length}): ${o}
Schedule: ${c.map((v) => Kt(v))} pos: ${this.timelinePos}`), h.length && this.log(`Removed events ${h}`);
      let u = null, f = null;
      a && (u = this.updateItem(a, this.timelinePos), this.itemsMatch(a, u) ? this.playingItem = u : this.waitingItem = this.endedItem = null), this.waitingItem = this.updateItem(this.waitingItem), this.endedItem = this.updateItem(this.endedItem);
      const g = this.bufferingItem;
      if (g && (f = this.updateItem(g, this.bufferedPos), this.itemsMatch(g, f) ? this.bufferingItem = f : g.event && (this.bufferingItem = this.playingItem, this.clearInterstitial(g.event, null))), i.forEach((v) => {
        v.assetList.forEach((p) => {
          this.clearAssetPlayer(p.identifier, null);
        });
      }), this.playerQueue.forEach((v) => {
        if (v.interstitial.appendInPlace) {
          const p = v.assetItem.timelineStart, y = v.timelineOffset - p;
          if (y)
            try {
              v.timelineOffset = p;
            } catch (E) {
              Math.abs(y) > je && this.warn(`${E} ("${v.assetId}" ${v.timelineOffset}->${p})`);
            }
        }
      }), d || s) {
        if (this.hls.trigger(m.INTERSTITIALS_UPDATED, {
          events: o.slice(0),
          schedule: c.slice(0),
          durations: l,
          removedIds: h
        }), this.isInterstitial(a) && h.includes(a.event.identifier)) {
          this.warn(`Interstitial "${a.event.identifier}" removed while playing`), this.primaryFallback(a.event);
          return;
        }
        a && this.trimInPlace(u, a), g && f !== u && this.trimInPlace(f, g), this.checkBuffer();
      }
    }, this.hls = t, this.HlsPlayerClass = e, this.assetListLoader = new bu(t), this.schedule = new Au(this.onScheduleUpdate, t.logger), this.registerListeners();
  }
  registerListeners() {
    const t = this.hls;
    t && (t.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.on(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.on(m.AUDIO_TRACK_UPDATED, this.onAudioTrackUpdated, this), t.on(m.SUBTITLE_TRACK_SWITCH, this.onSubtitleTrackSwitch, this), t.on(m.SUBTITLE_TRACK_UPDATED, this.onSubtitleTrackUpdated, this), t.on(m.EVENT_CUE_ENTER, this.onInterstitialCueEnter, this), t.on(m.ASSET_LIST_LOADED, this.onAssetListLoaded, this), t.on(m.BUFFER_APPENDED, this.onBufferAppended, this), t.on(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.on(m.BUFFERED_TO_END, this.onBufferedToEnd, this), t.on(m.MEDIA_ENDED, this.onMediaEnded, this), t.on(m.ERROR, this.onError, this), t.on(m.DESTROYING, this.onDestroying, this));
  }
  unregisterListeners() {
    const t = this.hls;
    t && (t.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.off(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.off(m.AUDIO_TRACK_UPDATED, this.onAudioTrackUpdated, this), t.off(m.SUBTITLE_TRACK_SWITCH, this.onSubtitleTrackSwitch, this), t.off(m.SUBTITLE_TRACK_UPDATED, this.onSubtitleTrackUpdated, this), t.off(m.EVENT_CUE_ENTER, this.onInterstitialCueEnter, this), t.off(m.ASSET_LIST_LOADED, this.onAssetListLoaded, this), t.off(m.BUFFER_CODECS, this.onBufferCodecs, this), t.off(m.BUFFER_APPENDED, this.onBufferAppended, this), t.off(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.off(m.BUFFERED_TO_END, this.onBufferedToEnd, this), t.off(m.MEDIA_ENDED, this.onMediaEnded, this), t.off(m.ERROR, this.onError, this), t.off(m.DESTROYING, this.onDestroying, this));
  }
  startLoad() {
    this.resumeBuffering();
  }
  stopLoad() {
    this.pauseBuffering();
  }
  resumeBuffering() {
    var t;
    (t = this.getBufferingPlayer()) == null || t.resumeBuffering();
  }
  pauseBuffering() {
    var t;
    (t = this.getBufferingPlayer()) == null || t.pauseBuffering();
  }
  destroy() {
    this.unregisterListeners(), this.stopLoad(), this.assetListLoader && this.assetListLoader.destroy(), this.emptyPlayerQueue(), this.clearScheduleState(), this.schedule && this.schedule.destroy(), this.media = this.detachedData = this.mediaSelection = this.requiredTracks = this.altSelection = this.schedule = this.manager = null, this.hls = this.HlsPlayerClass = this.log = null, this.assetListLoader = null, this.onPlay = this.onPause = this.onSeeking = this.onTimeupdate = null, this.onScheduleUpdate = null;
  }
  onDestroying() {
    const t = this.primaryMedia || this.media;
    t && this.removeMediaListeners(t);
  }
  removeMediaListeners(t) {
    wt(t, "play", this.onPlay), wt(t, "pause", this.onPause), wt(t, "seeking", this.onSeeking), wt(t, "timeupdate", this.onTimeupdate);
  }
  onMediaAttaching(t, e) {
    const i = this.media = e.media;
    _t(i, "seeking", this.onSeeking), _t(i, "timeupdate", this.onTimeupdate), _t(i, "play", this.onPlay), _t(i, "pause", this.onPause);
  }
  onMediaAttached(t, e) {
    const i = this.effectivePlayingItem, s = this.detachedData;
    if (this.detachedData = null, i === null)
      this.checkStart();
    else if (!s) {
      this.clearScheduleState();
      const r = this.findItemIndex(i);
      this.setSchedulePosition(r);
    }
  }
  clearScheduleState() {
    this.log("clear schedule state"), this.playingItem = this.bufferingItem = this.waitingItem = this.endedItem = this.playingAsset = this.endedAsset = this.bufferingAsset = null;
  }
  onMediaDetaching(t, e) {
    const i = !!e.transferMedia, s = this.media;
    if (this.media = null, !i && (s && this.removeMediaListeners(s), this.detachedData)) {
      const r = this.getBufferingPlayer();
      r && (this.log(`Removing schedule state for detachedData and ${r}`), this.playingAsset = this.endedAsset = this.bufferingAsset = this.bufferingItem = this.waitingItem = this.detachedData = null, r.detachMedia()), this.shouldPlay = !1;
    }
  }
  get interstitialsManager() {
    if (!this.hls)
      return null;
    if (this.manager)
      return this.manager;
    const t = this, e = () => t.bufferingItem || t.waitingItem, i = (d) => d && t.getAssetPlayer(d.identifier), s = (d, u, f, g, v) => {
      if (d) {
        let p = d[u].start;
        const y = d.event;
        if (y) {
          if (u === "playout" || y.timelineOccupancy !== os.Point) {
            const E = i(f);
            (E == null ? void 0 : E.interstitial) === y && (p += E.assetItem.startOffset + E[v]);
          }
        } else {
          const E = g === "bufferedPos" ? a() : t[g];
          p += E - d.start;
        }
        return p;
      }
      return 0;
    }, r = (d, u) => {
      var f;
      if (d !== 0 && u !== "primary" && (f = t.schedule) != null && f.length) {
        var g;
        const v = t.schedule.findItemIndexAtTime(d), p = (g = t.schedule.items) == null ? void 0 : g[v];
        if (p) {
          const y = p[u].start - p.start;
          return d + y;
        }
      }
      return d;
    }, a = () => {
      const d = t.bufferedPos;
      return d === Number.MAX_VALUE ? o("primary") : Math.max(d, 0);
    }, o = (d) => {
      var u, f;
      return (u = t.primaryDetails) != null && u.live ? t.primaryDetails.edge : ((f = t.schedule) == null ? void 0 : f.durations[d]) || 0;
    }, c = (d, u) => {
      var f, g;
      const v = t.effectivePlayingItem;
      if (v != null && (f = v.event) != null && f.restrictions.skip || !t.schedule)
        return;
      t.log(`seek to ${d} "${u}"`);
      const p = t.effectivePlayingItem, y = t.schedule.findItemIndexAtTime(d, u), E = (g = t.schedule.items) == null ? void 0 : g[y], T = t.getBufferingPlayer(), S = T == null ? void 0 : T.interstitial, x = S == null ? void 0 : S.appendInPlace, D = p && t.itemsMatch(p, E);
      if (p && (x || D)) {
        const A = i(t.playingAsset), _ = (A == null ? void 0 : A.media) || t.primaryMedia;
        if (_) {
          const R = u === "primary" ? _.currentTime : s(p, u, t.playingAsset, "timelinePos", "currentTime"), b = d - R, C = (x ? R : _.currentTime) + b;
          if (C >= 0 && (!A || x || C <= A.duration)) {
            _.currentTime = C;
            return;
          }
        }
      }
      if (E) {
        let A = d;
        if (u !== "primary") {
          const R = E[u].start, b = d - R;
          A = E.start + b;
        }
        const _ = !t.isInterstitial(E);
        if ((!t.isInterstitial(p) || p.event.appendInPlace) && (_ || E.event.appendInPlace)) {
          const R = t.media || (x ? T == null ? void 0 : T.media : null);
          R && (R.currentTime = A);
        } else if (p) {
          const R = t.findItemIndex(p);
          if (y > R) {
            const C = t.schedule.findJumpRestrictedIndex(R + 1, y);
            if (C > R) {
              t.setSchedulePosition(C);
              return;
            }
          }
          let b = 0;
          if (_)
            t.timelinePos = A, t.checkBuffer();
          else {
            const C = E.event.assetList, F = d - (E[u] || E).start;
            for (let U = C.length; U--; ) {
              const W = C[U];
              if (W.duration && F >= W.startOffset && F < W.startOffset + W.duration) {
                b = U;
                break;
              }
            }
          }
          t.setSchedulePosition(y, b);
        }
      }
    }, l = () => {
      const d = t.effectivePlayingItem;
      if (t.isInterstitial(d))
        return d;
      const u = e();
      return t.isInterstitial(u) ? u : null;
    }, h = {
      get bufferedEnd() {
        const d = e(), u = t.bufferingItem;
        if (u && u === d) {
          var f;
          return s(u, "playout", t.bufferingAsset, "bufferedPos", "bufferedEnd") - u.playout.start || ((f = t.bufferingAsset) == null ? void 0 : f.startOffset) || 0;
        }
        return 0;
      },
      get currentTime() {
        const d = l(), u = t.effectivePlayingItem;
        return u && u === d ? s(u, "playout", t.effectivePlayingAsset, "timelinePos", "currentTime") - u.playout.start : 0;
      },
      set currentTime(d) {
        const u = l(), f = t.effectivePlayingItem;
        f && f === u && c(d + f.playout.start, "playout");
      },
      get duration() {
        const d = l();
        return d ? d.playout.end - d.playout.start : 0;
      },
      get assetPlayers() {
        var d;
        const u = (d = l()) == null ? void 0 : d.event.assetList;
        return u ? u.map((f) => t.getAssetPlayer(f.identifier)) : [];
      },
      get playingIndex() {
        var d;
        const u = (d = l()) == null ? void 0 : d.event;
        return u && t.effectivePlayingAsset ? u.findAssetIndex(t.effectivePlayingAsset) : -1;
      },
      get scheduleItem() {
        return l();
      }
    };
    return this.manager = {
      get events() {
        var d;
        return ((d = t.schedule) == null || (d = d.events) == null ? void 0 : d.slice(0)) || [];
      },
      get schedule() {
        var d;
        return ((d = t.schedule) == null || (d = d.items) == null ? void 0 : d.slice(0)) || [];
      },
      get interstitialPlayer() {
        return l() ? h : null;
      },
      get playerQueue() {
        return t.playerQueue.slice(0);
      },
      get bufferingAsset() {
        return t.bufferingAsset;
      },
      get bufferingItem() {
        return e();
      },
      get bufferingIndex() {
        const d = e();
        return t.findItemIndex(d);
      },
      get playingAsset() {
        return t.effectivePlayingAsset;
      },
      get playingItem() {
        return t.effectivePlayingItem;
      },
      get playingIndex() {
        const d = t.effectivePlayingItem;
        return t.findItemIndex(d);
      },
      primary: {
        get bufferedEnd() {
          return a();
        },
        get currentTime() {
          const d = t.timelinePos;
          return d > 0 ? d : 0;
        },
        set currentTime(d) {
          c(d, "primary");
        },
        get duration() {
          return o("primary");
        },
        get seekableStart() {
          var d;
          return ((d = t.primaryDetails) == null ? void 0 : d.fragmentStart) || 0;
        }
      },
      integrated: {
        get bufferedEnd() {
          return s(e(), "integrated", t.bufferingAsset, "bufferedPos", "bufferedEnd");
        },
        get currentTime() {
          return s(t.effectivePlayingItem, "integrated", t.effectivePlayingAsset, "timelinePos", "currentTime");
        },
        set currentTime(d) {
          c(d, "integrated");
        },
        get duration() {
          return o("integrated");
        },
        get seekableStart() {
          var d;
          return r(((d = t.primaryDetails) == null ? void 0 : d.fragmentStart) || 0, "integrated");
        }
      },
      skip: () => {
        const d = t.effectivePlayingItem, u = d == null ? void 0 : d.event;
        if (u && !u.restrictions.skip) {
          const f = t.findItemIndex(d);
          if (u.appendInPlace) {
            const g = d.playout.start + d.event.duration;
            c(g + 1e-3, "playout");
          } else
            t.advanceAfterAssetEnded(u, f, 1 / 0);
        }
      }
    };
  }
  // Schedule getters
  get effectivePlayingItem() {
    return this.waitingItem || this.playingItem || this.endedItem;
  }
  get effectivePlayingAsset() {
    return this.playingAsset || this.endedAsset;
  }
  get playingLastItem() {
    var t;
    const e = this.playingItem, i = (t = this.schedule) == null ? void 0 : t.items;
    return !this.playbackStarted || !e || !i ? !1 : this.findItemIndex(e) === i.length - 1;
  }
  get playbackStarted() {
    return this.effectivePlayingItem !== null;
  }
  // Media getters and event callbacks
  get currentTime() {
    var t, e;
    if (this.mediaSelection === null)
      return;
    const i = this.waitingItem || this.playingItem;
    if (this.isInterstitial(i) && !i.event.appendInPlace)
      return;
    let s = this.media;
    !s && (t = this.bufferingItem) != null && (t = t.event) != null && t.appendInPlace && (s = this.primaryMedia);
    const r = (e = s) == null ? void 0 : e.currentTime;
    if (!(r === void 0 || !B(r)))
      return r;
  }
  get primaryMedia() {
    var t;
    return this.media || ((t = this.detachedData) == null ? void 0 : t.media) || null;
  }
  isInterstitial(t) {
    return !!(t != null && t.event);
  }
  retreiveMediaSource(t, e) {
    const i = this.getAssetPlayer(t);
    i && this.transferMediaFromPlayer(i, e);
  }
  transferMediaFromPlayer(t, e) {
    const i = t.interstitial.appendInPlace, s = t.media;
    if (i && s === this.primaryMedia) {
      if (this.bufferingAsset = null, (!e || this.isInterstitial(e) && !e.event.appendInPlace) && e && s) {
        this.detachedData = {
          media: s
        };
        return;
      }
      const r = t.transferMedia();
      this.log(`transfer MediaSource from ${t} ${ot(r)}`), this.detachedData = r;
    } else e && s && (this.shouldPlay || (this.shouldPlay = !s.paused));
  }
  transferMediaTo(t, e) {
    var i, s;
    if (t.media === e)
      return;
    let r = null;
    const a = this.hls, o = t !== a, c = o && t.interstitial.appendInPlace, l = (i = this.detachedData) == null ? void 0 : i.mediaSource;
    let h;
    if (a.media)
      c && (r = a.transferMedia(), this.detachedData = r), h = "Primary";
    else if (l) {
      const g = this.getBufferingPlayer();
      g ? (r = g.transferMedia(), h = `${g}`) : h = "detached MediaSource";
    } else
      h = "detached media";
    if (!r) {
      if (l)
        r = this.detachedData, this.log(`using detachedData: MediaSource ${ot(r)}`);
      else if (!this.detachedData || a.media === e) {
        const g = this.playerQueue;
        g.length > 1 && g.forEach((v) => {
          if (o && v.interstitial.appendInPlace !== c) {
            const p = v.interstitial;
            this.clearInterstitial(v.interstitial, null), p.appendInPlace = !1, p.appendInPlace && this.warn(`Could not change append strategy for queued assets ${p}`);
          }
        }), this.hls.detachMedia(), this.detachedData = {
          media: e
        };
      }
    }
    const d = r && "mediaSource" in r && ((s = r.mediaSource) == null ? void 0 : s.readyState) !== "closed", u = d && r ? r : e;
    this.log(`${d ? "transfering MediaSource" : "attaching media"} to ${o ? t : "Primary"} from ${h} (media.currentTime: ${e.currentTime})`);
    const f = this.schedule;
    if (u === r && f) {
      const g = o && t.assetId === f.assetIdAtEnd;
      u.overrides = {
        duration: f.duration,
        endOfStream: !o || g,
        cueRemoval: !o
      };
    }
    t.attachMedia(u);
  }
  onInterstitialCueEnter() {
    this.onTimeupdate();
  }
  // Scheduling methods
  checkStart() {
    const t = this.schedule, e = t == null ? void 0 : t.events;
    if (!e || this.playbackDisabled || !this.media)
      return;
    this.bufferedPos === -1 && (this.bufferedPos = 0);
    const i = this.timelinePos, s = this.effectivePlayingItem;
    if (i === -1) {
      const r = this.hls.startPosition;
      if (this.log(Mi("checkStart", r)), this.timelinePos = r, e.length && e[0].cue.pre) {
        const a = t.findEventIndex(e[0].identifier);
        this.setSchedulePosition(a);
      } else if (r >= 0 || !this.primaryLive) {
        const a = this.timelinePos = r > 0 ? r : 0, o = t.findItemIndexAtTime(a);
        this.setSchedulePosition(o);
      }
    } else if (s && !this.playingItem) {
      const r = t.findItemIndex(s);
      this.setSchedulePosition(r);
    }
  }
  advanceAssetBuffering(t, e) {
    const i = t.event, s = i.findAssetIndex(e), r = Os(i, s);
    if (!i.isAssetPastPlayoutLimit(r))
      this.bufferedToEvent(t, r);
    else if (this.schedule) {
      var a;
      const o = (a = this.schedule.items) == null ? void 0 : a[this.findItemIndex(t) + 1];
      o && this.bufferedToItem(o);
    }
  }
  advanceAfterAssetEnded(t, e, i) {
    const s = Os(t, i);
    if (t.isAssetPastPlayoutLimit(s)) {
      if (this.schedule) {
        const r = this.schedule.items;
        if (r) {
          const a = e + 1, o = r.length;
          if (a >= o) {
            this.setSchedulePosition(-1);
            return;
          }
          const c = t.resumeTime;
          this.timelinePos < c && (this.log(Mi("advanceAfterAssetEnded", c)), this.timelinePos = c, t.appendInPlace && this.advanceInPlace(c), this.checkBuffer(this.bufferedPos < c)), this.setSchedulePosition(a);
        }
      }
    } else {
      if (t.appendInPlace) {
        const r = t.assetList[s];
        r && this.advanceInPlace(r.timelineStart);
      }
      this.setSchedulePosition(e, s);
    }
  }
  setScheduleToAssetAtTime(t, e) {
    const i = this.schedule;
    if (!i)
      return;
    const s = e.parentIdentifier, r = i.getEvent(s);
    if (r) {
      const a = i.findEventIndex(s), o = i.findAssetIndex(r, t);
      this.advanceAfterAssetEnded(r, a, o - 1);
    }
  }
  setSchedulePosition(t, e) {
    var i;
    const s = (i = this.schedule) == null ? void 0 : i.items;
    if (!s || this.playbackDisabled)
      return;
    const r = t >= 0 ? s[t] : null;
    this.log(`setSchedulePosition ${t}, ${e} (${r && Kt(r)}) pos: ${this.timelinePos}`);
    const a = this.waitingItem || this.playingItem, o = this.playingLastItem;
    if (this.isInterstitial(a)) {
      const h = a.event, d = this.playingAsset, u = d == null ? void 0 : d.identifier, f = u ? this.getAssetPlayer(u) : null;
      if (f && u && (!this.eventItemsMatch(a, r) || e !== void 0 && u !== h.assetList[e].identifier)) {
        var c;
        const g = h.findAssetIndex(d);
        if (this.log(`INTERSTITIAL_ASSET_ENDED ${g + 1}/${h.assetList.length} ${He(d)}`), this.endedAsset = d, this.playingAsset = null, this.hls.trigger(m.INTERSTITIAL_ASSET_ENDED, {
          asset: d,
          assetListIndex: g,
          event: h,
          schedule: s.slice(0),
          scheduleIndex: t,
          player: f
        }), a !== this.playingItem) {
          this.itemsMatch(a, this.playingItem) && // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
          !this.playingAsset && this.advanceAfterAssetEnded(h, this.findItemIndex(this.playingItem), g);
          return;
        }
        this.retreiveMediaSource(u, r), f.media && !((c = this.detachedData) != null && c.mediaSource) && f.detachMedia();
      }
      if (!this.eventItemsMatch(a, r) && (this.endedItem = a, this.playingItem = null, this.log(`INTERSTITIAL_ENDED ${h} ${Kt(a)}`), h.hasPlayed = !0, this.hls.trigger(m.INTERSTITIAL_ENDED, {
        event: h,
        schedule: s.slice(0),
        scheduleIndex: t
      }), h.cue.once)) {
        var l;
        this.updateSchedule();
        const g = (l = this.schedule) == null ? void 0 : l.items;
        if (r && g) {
          const v = this.findItemIndex(r);
          this.advanceSchedule(v, g, e, a, o);
        }
        return;
      }
    }
    this.advanceSchedule(t, s, e, a, o);
  }
  advanceSchedule(t, e, i, s, r) {
    const a = this.schedule;
    if (!a)
      return;
    const o = e[t] || null, c = this.primaryMedia, l = this.playerQueue;
    if (l.length && l.forEach((h) => {
      const d = h.interstitial, u = a.findEventIndex(d.identifier);
      (u < t || u > t + 1) && this.clearInterstitial(d, o);
    }), this.isInterstitial(o)) {
      this.timelinePos = Math.min(Math.max(this.timelinePos, o.start), o.end);
      const h = o.event;
      if (i === void 0) {
        i = a.findAssetIndex(h, this.timelinePos);
        const g = Os(h, i - 1);
        if (h.isAssetPastPlayoutLimit(g) || h.appendInPlace && this.timelinePos === o.end) {
          this.advanceAfterAssetEnded(h, t, i);
          return;
        }
        i = g;
      }
      const d = this.waitingItem;
      this.assetsBuffered(o, c) || this.setBufferingItem(o);
      let u = this.preloadAssets(h, i);
      if (this.eventItemsMatch(o, d || s) || (this.waitingItem = o, this.log(`INTERSTITIAL_STARTED ${Kt(o)} ${h.appendInPlace ? "append in place" : ""}`), this.hls.trigger(m.INTERSTITIAL_STARTED, {
        event: h,
        schedule: e.slice(0),
        scheduleIndex: t
      })), !h.assetListLoaded) {
        this.log(`Waiting for ASSET-LIST to complete loading ${h}`);
        return;
      }
      if (h.assetListLoader && (h.assetListLoader.destroy(), h.assetListLoader = void 0), !c) {
        this.log(`Waiting for attachMedia to start Interstitial ${h}`);
        return;
      }
      this.waitingItem = this.endedItem = null, this.playingItem = o;
      const f = h.assetList[i];
      if (!f) {
        this.advanceAfterAssetEnded(h, t, i || 0);
        return;
      }
      if (u || (u = this.getAssetPlayer(f.identifier)), u === null || u.destroyed) {
        const g = h.assetList.length;
        this.warn(`asset ${i + 1}/${g} player destroyed ${h}`), u = this.createAssetPlayer(h, f, i), u.loadSource();
      }
      if (!this.eventItemsMatch(o, this.bufferingItem) && h.appendInPlace && this.isAssetBuffered(f))
        return;
      this.startAssetPlayer(u, i, e, t, c), this.shouldPlay && Qn(u.media);
    } else o ? (this.resumePrimary(o, t, s), this.shouldPlay && Qn(this.hls.media)) : r && this.isInterstitial(s) && (this.endedItem = null, this.playingItem = s, s.event.appendInPlace || this.attachPrimary(a.durations.primary, null));
  }
  get playbackDisabled() {
    return this.hls.config.enableInterstitialPlayback === !1;
  }
  get primaryDetails() {
    var t;
    return (t = this.mediaSelection) == null ? void 0 : t.main.details;
  }
  get primaryLive() {
    var t;
    return !!((t = this.primaryDetails) != null && t.live);
  }
  resumePrimary(t, e, i) {
    var s, r;
    if (this.playingItem = t, this.playingAsset = this.endedAsset = null, this.waitingItem = this.endedItem = null, this.bufferedToItem(t), this.log(`resuming ${Kt(t)}`), !((s = this.detachedData) != null && s.mediaSource)) {
      let o = this.timelinePos;
      (o < t.start || o >= t.end) && (o = this.getPrimaryResumption(t, e), this.log(Mi("resumePrimary", o)), this.timelinePos = o), this.attachPrimary(o, t);
    }
    if (!i)
      return;
    const a = (r = this.schedule) == null ? void 0 : r.items;
    a && (this.log(`INTERSTITIALS_PRIMARY_RESUMED ${Kt(t)}`), this.hls.trigger(m.INTERSTITIALS_PRIMARY_RESUMED, {
      schedule: a.slice(0),
      scheduleIndex: e
    }), this.checkBuffer());
  }
  getPrimaryResumption(t, e) {
    const i = t.start;
    if (this.primaryLive) {
      const s = this.primaryDetails;
      if (e === 0)
        return this.hls.startPosition;
      if (s && (i < s.fragmentStart || i > s.edge))
        return this.hls.liveSyncPosition || -1;
    }
    return i;
  }
  isAssetBuffered(t) {
    const e = this.getAssetPlayer(t.identifier);
    return e != null && e.hls ? e.hls.bufferedToEnd : q.bufferInfo(this.primaryMedia, this.timelinePos, 0).end + 1 >= t.timelineStart + (t.duration || 0);
  }
  attachPrimary(t, e, i) {
    e ? this.setBufferingItem(e) : this.bufferingItem = this.playingItem, this.bufferingAsset = null;
    const s = this.primaryMedia;
    if (!s)
      return;
    const r = this.hls;
    r.media ? this.checkBuffer() : (this.transferMediaTo(r, s), i && this.startLoadingPrimaryAt(t, i)), i || (this.log(Mi("attachPrimary", t)), this.timelinePos = t, this.startLoadingPrimaryAt(t, i));
  }
  startLoadingPrimaryAt(t, e) {
    var i;
    const s = this.hls;
    !s.loadingEnabled || !s.media || Math.abs((((i = s.mainForwardBufferInfo) == null ? void 0 : i.start) || s.media.currentTime) - t) > 0.5 ? s.startLoad(t, e) : s.bufferingEnabled || s.resumeBuffering();
  }
  // HLS.js event callbacks
  onManifestLoading() {
    var t;
    this.stopLoad(), (t = this.schedule) == null || t.reset(), this.emptyPlayerQueue(), this.clearScheduleState(), this.shouldPlay = !1, this.bufferedPos = this.timelinePos = -1, this.mediaSelection = this.altSelection = this.manager = this.requiredTracks = null, this.hls.off(m.BUFFER_CODECS, this.onBufferCodecs, this), this.hls.on(m.BUFFER_CODECS, this.onBufferCodecs, this);
  }
  onLevelUpdated(t, e) {
    if (e.level === -1 || !this.schedule)
      return;
    const i = this.hls.levels[e.level];
    if (!i.details)
      return;
    const s = st(st({}, this.mediaSelection || this.altSelection), {}, {
      main: i
    });
    this.mediaSelection = s, this.schedule.parseInterstitialDateRanges(s, this.hls.config.interstitialAppendInPlace), !this.effectivePlayingItem && this.schedule.items && this.checkStart();
  }
  onAudioTrackUpdated(t, e) {
    const i = this.hls.audioTracks[e.id], s = this.mediaSelection;
    if (!s) {
      this.altSelection = st(st({}, this.altSelection), {}, {
        audio: i
      });
      return;
    }
    const r = st(st({}, s), {}, {
      audio: i
    });
    this.mediaSelection = r;
  }
  onSubtitleTrackUpdated(t, e) {
    const i = this.hls.subtitleTracks[e.id], s = this.mediaSelection;
    if (!s) {
      this.altSelection = st(st({}, this.altSelection), {}, {
        subtitles: i
      });
      return;
    }
    const r = st(st({}, s), {}, {
      subtitles: i
    });
    this.mediaSelection = r;
  }
  onAudioTrackSwitching(t, e) {
    const i = an(e);
    this.playerQueue.forEach(({
      hls: s
    }) => s && (s.setAudioOption(e) || s.setAudioOption(i)));
  }
  onSubtitleTrackSwitch(t, e) {
    const i = an(e);
    this.playerQueue.forEach(({
      hls: s
    }) => s && (s.setSubtitleOption(e) || e.id !== -1 && s.setSubtitleOption(i)));
  }
  onBufferCodecs(t, e) {
    const i = e.tracks;
    i && (this.requiredTracks = i);
  }
  onBufferAppended(t, e) {
    this.checkBuffer();
  }
  onBufferFlushed(t, e) {
    const i = this.playingItem;
    if (i && !this.itemsMatch(i, this.bufferingItem) && !this.isInterstitial(i)) {
      const s = this.timelinePos;
      this.bufferedPos = s, this.checkBuffer();
    }
  }
  onBufferedToEnd(t) {
    if (!this.schedule)
      return;
    const e = this.schedule.events;
    if (this.bufferedPos < Number.MAX_VALUE && e) {
      for (let s = 0; s < e.length; s++) {
        const r = e[s];
        if (r.cue.post) {
          var i;
          const a = this.schedule.findEventIndex(r.identifier), o = (i = this.schedule.items) == null ? void 0 : i[a];
          this.isInterstitial(o) && this.eventItemsMatch(o, this.bufferingItem) && this.bufferedToItem(o, 0);
          break;
        }
      }
      this.bufferedPos = Number.MAX_VALUE;
    }
  }
  onMediaEnded(t) {
    const e = this.playingItem;
    if (!this.playingLastItem && e) {
      const i = this.findItemIndex(e);
      this.setSchedulePosition(i + 1);
    } else
      this.shouldPlay = !1;
  }
  updateItem(t, e) {
    var i;
    const s = (i = this.schedule) == null ? void 0 : i.items;
    if (t && s) {
      const r = this.findItemIndex(t, e);
      return s[r] || null;
    }
    return null;
  }
  trimInPlace(t, e) {
    if (this.isInterstitial(t) && t.event.appendInPlace && e.end - t.end > 0.25) {
      t.event.assetList.forEach((r, a) => {
        t.event.isAssetPastPlayoutLimit(a) && this.clearAssetPlayer(r.identifier, null);
      });
      const i = t.end + 0.25, s = q.bufferInfo(this.primaryMedia, i, 0);
      (s.end > i || (s.nextStart || 0) > i) && (this.log(`trim buffered interstitial ${Kt(t)} (was ${Kt(e)})`), this.attachPrimary(i, null, !0), this.flushFrontBuffer(i));
    }
  }
  itemsMatch(t, e) {
    return !!e && (t === e || t.event && e.event && this.eventItemsMatch(t, e) || !t.event && !e.event && this.findItemIndex(t) === this.findItemIndex(e));
  }
  eventItemsMatch(t, e) {
    var i;
    return !!e && (t === e || t.event.identifier === ((i = e.event) == null ? void 0 : i.identifier));
  }
  findItemIndex(t, e) {
    return t && this.schedule ? this.schedule.findItemIndex(t, e) : -1;
  }
  updateSchedule(t = !1) {
    var e;
    const i = this.mediaSelection;
    i && ((e = this.schedule) == null || e.updateSchedule(i, [], t));
  }
  // Schedule buffer control
  checkBuffer(t) {
    var e;
    const i = (e = this.schedule) == null ? void 0 : e.items;
    if (!i)
      return;
    const s = q.bufferInfo(this.primaryMedia, this.timelinePos, 0);
    t && (this.bufferedPos = this.timelinePos), t || (t = s.len < 1), this.updateBufferedPos(s.end, i, t);
  }
  updateBufferedPos(t, e, i) {
    const s = this.schedule, r = this.bufferingItem;
    if (this.bufferedPos > t || !s)
      return;
    if (e.length === 1 && this.itemsMatch(e[0], r)) {
      this.bufferedPos = t;
      return;
    }
    const a = this.playingItem, o = this.findItemIndex(a);
    let c = s.findItemIndexAtTime(t);
    if (this.bufferedPos < t) {
      var l;
      const h = this.findItemIndex(r), d = Math.min(h + 1, e.length - 1), u = e[d];
      if ((c === -1 && r && t >= r.end || (l = u.event) != null && l.appendInPlace && t + 0.01 >= u.start) && (c = d), this.isInterstitial(r)) {
        const f = r.event;
        if (d - o > 1 && f.appendInPlace === !1 || f.assetList.length === 0 && f.assetListLoader)
          return;
      }
      if (this.bufferedPos = t, c > h && c > o)
        this.bufferedToItem(u);
      else {
        const f = this.primaryDetails;
        this.primaryLive && f && t > f.edge - f.targetduration && u.start < f.edge + this.hls.config.interstitialLiveLookAhead && this.isInterstitial(u) && this.preloadAssets(u.event, 0);
      }
    } else i && a && !this.itemsMatch(a, r) && (c === o ? this.bufferedToItem(a) : c === o + 1 && this.bufferedToItem(e[c]));
  }
  assetsBuffered(t, e) {
    return t.event.assetList.length === 0 ? !1 : !t.event.assetList.some((s) => {
      const r = this.getAssetPlayer(s.identifier);
      return !(r != null && r.bufferedInPlaceToEnd(e));
    });
  }
  setBufferingItem(t) {
    const e = this.bufferingItem, i = this.schedule;
    if (!this.itemsMatch(t, e) && i) {
      const {
        items: s,
        events: r
      } = i;
      if (!s || !r)
        return e;
      const a = this.isInterstitial(t), o = this.getBufferingPlayer();
      this.bufferingItem = t, this.bufferedPos = Math.max(t.start, Math.min(t.end, this.timelinePos));
      const c = o ? o.remaining : e ? e.end - this.timelinePos : 0;
      if (this.log(`INTERSTITIALS_BUFFERED_TO_BOUNDARY ${Kt(t)}` + (e ? ` (${c.toFixed(2)} remaining)` : "")), !this.playbackDisabled)
        if (a) {
          const l = i.findAssetIndex(t.event, this.bufferedPos);
          t.event.assetList.forEach((h, d) => {
            const u = this.getAssetPlayer(h.identifier);
            u && (d === l && u.loadSource(), u.resumeBuffering());
          });
        } else
          this.hls.resumeBuffering(), this.playerQueue.forEach((l) => l.pauseBuffering());
      this.hls.trigger(m.INTERSTITIALS_BUFFERED_TO_BOUNDARY, {
        events: r.slice(0),
        schedule: s.slice(0),
        bufferingIndex: this.findItemIndex(t),
        playingIndex: this.findItemIndex(this.playingItem)
      });
    } else this.bufferingItem !== t && (this.bufferingItem = t);
    return e;
  }
  bufferedToItem(t, e = 0) {
    const i = this.setBufferingItem(t);
    if (!this.playbackDisabled) {
      if (this.isInterstitial(t))
        this.bufferedToEvent(t, e);
      else if (i !== null) {
        this.bufferingAsset = null;
        const s = this.detachedData;
        s ? s.mediaSource ? this.attachPrimary(t.start, t, !0) : this.preloadPrimary(t) : this.preloadPrimary(t);
      }
    }
  }
  preloadPrimary(t) {
    const e = this.findItemIndex(t), i = this.getPrimaryResumption(t, e);
    this.startLoadingPrimaryAt(i);
  }
  bufferedToEvent(t, e) {
    const i = t.event, s = i.assetList.length === 0 && !i.assetListLoader, r = i.cue.once;
    if (s || !r) {
      const a = this.preloadAssets(i, e);
      if (a != null && a.interstitial.appendInPlace) {
        const o = this.primaryMedia;
        o && this.bufferAssetPlayer(a, o);
      }
    }
  }
  preloadAssets(t, e) {
    const i = t.assetUrl, s = t.assetList.length, r = s === 0 && !t.assetListLoader, a = t.cue.once;
    if (r) {
      const c = t.timelineStart;
      if (t.appendInPlace) {
        var o;
        const u = this.playingItem;
        !this.isInterstitial(u) && (u == null || (o = u.nextEvent) == null ? void 0 : o.identifier) === t.identifier && this.flushFrontBuffer(c + 0.25);
      }
      let l, h = 0;
      if (!this.playingItem && this.primaryLive && (h = this.hls.startPosition, h === -1 && (h = this.hls.liveSyncPosition || 0)), h && !(t.cue.pre || t.cue.post)) {
        const u = h - c;
        u > 0 && (l = Math.round(u * 1e3) / 1e3);
      }
      if (this.log(`Load interstitial asset ${e + 1}/${i ? 1 : s} ${t}${l ? ` live-start: ${h} start-offset: ${l}` : ""}`), i)
        return this.createAsset(t, 0, 0, c, t.duration, i);
      const d = this.assetListLoader.loadAssetList(t, l);
      d && (t.assetListLoader = d);
    } else if (!a && s) {
      for (let l = e; l < s; l++) {
        const h = t.assetList[l], d = this.getAssetPlayerQueueIndex(h.identifier);
        (d === -1 || this.playerQueue[d].destroyed) && !h.error && this.createAssetPlayer(t, h, l);
      }
      const c = t.assetList[e];
      if (c) {
        const l = this.getAssetPlayer(c.identifier);
        return l && l.loadSource(), l;
      }
    }
    return null;
  }
  flushFrontBuffer(t) {
    const e = this.requiredTracks;
    if (!e)
      return;
    this.log(`Removing front buffer starting at ${t}`), Object.keys(e).forEach((s) => {
      this.hls.trigger(m.BUFFER_FLUSHING, {
        startOffset: t,
        endOffset: 1 / 0,
        type: s
      });
    });
  }
  // Interstitial Asset Player control
  getAssetPlayerQueueIndex(t) {
    const e = this.playerQueue;
    for (let i = 0; i < e.length; i++)
      if (t === e[i].assetId)
        return i;
    return -1;
  }
  getAssetPlayer(t) {
    const e = this.getAssetPlayerQueueIndex(t);
    return this.playerQueue[e] || null;
  }
  getBufferingPlayer() {
    const {
      playerQueue: t,
      primaryMedia: e
    } = this;
    if (e) {
      for (let i = 0; i < t.length; i++)
        if (t[i].media === e)
          return t[i];
    }
    return null;
  }
  createAsset(t, e, i, s, r, a) {
    const o = {
      parentIdentifier: t.identifier,
      identifier: Eu(t, a, e),
      duration: r,
      startOffset: i,
      timelineStart: s,
      uri: a
    };
    return this.createAssetPlayer(t, o, e);
  }
  createAssetPlayer(t, e, i) {
    const s = this.hls, r = s.userConfig;
    let a = r.videoPreference;
    const o = s.loadLevelObj || s.levels[s.currentLevel];
    (a || o) && (a = nt({}, a), o.videoCodec && (a.videoCodec = o.videoCodec), o.videoRange && (a.allowedVideoRanges = [o.videoRange]));
    const c = s.audioTracks[s.audioTrack], l = s.subtitleTracks[s.subtitleTrack];
    let h = 0;
    if (this.primaryLive || t.appendInPlace) {
      const S = this.timelinePos - e.timelineStart;
      if (S > 1) {
        const x = e.duration;
        x && S < x && (h = S);
      }
    }
    const d = e.identifier, u = st(st({}, r), {}, {
      maxMaxBufferLength: Math.min(180, s.config.maxMaxBufferLength),
      autoStartLoad: !0,
      startFragPrefetch: !0,
      primarySessionId: s.sessionId,
      assetPlayerId: d,
      abrEwmaDefaultEstimate: s.bandwidthEstimate,
      interstitialsController: void 0,
      startPosition: h,
      liveDurationInfinity: !1,
      testBandwidth: !1,
      videoPreference: a,
      audioPreference: c || r.audioPreference,
      subtitlePreference: l || r.subtitlePreference
    });
    t.appendInPlace && (t.appendInPlaceStarted = !0, e.timelineStart && (u.timelineOffset = e.timelineStart));
    const f = u.cmcd;
    f != null && f.sessionId && f.contentId && (u.cmcd = nt({}, f, {
      contentId: fi(e.uri)
    })), this.getAssetPlayer(d) && this.warn(`Duplicate date range identifier ${t} and asset ${d}`);
    const g = new xu(this.HlsPlayerClass, u, t, e);
    this.playerQueue.push(g), t.assetList[i] = e;
    let v = !0;
    const p = (S) => {
      if (S.live) {
        var x;
        const _ = new Error(`Interstitials MUST be VOD assets ${t}`), R = {
          fatal: !0,
          type: Y.OTHER_ERROR,
          details: L.INTERSTITIAL_ASSET_ITEM_ERROR,
          error: _
        }, b = ((x = this.schedule) == null ? void 0 : x.findEventIndex(t.identifier)) || -1;
        this.handleAssetItemError(R, t, b, i, _.message);
        return;
      }
      const D = S.edge - S.fragmentStart, A = e.duration;
      (v || A === null || D > A) && (v = !1, this.log(`Interstitial asset "${d}" duration change ${A} > ${D}`), e.duration = D, this.updateSchedule());
    };
    g.on(m.LEVEL_UPDATED, (S, {
      details: x
    }) => p(x)), g.on(m.LEVEL_PTS_UPDATED, (S, {
      details: x
    }) => p(x)), g.on(m.EVENT_CUE_ENTER, () => this.onInterstitialCueEnter());
    const y = (S, x) => {
      const D = this.getAssetPlayer(d);
      if (D && x.tracks) {
        D.off(m.BUFFER_CODECS, y), D.tracks = x.tracks;
        const A = this.primaryMedia;
        this.bufferingAsset === D.assetItem && A && !D.media && this.bufferAssetPlayer(D, A);
      }
    };
    g.on(m.BUFFER_CODECS, y);
    const E = () => {
      var S;
      const x = this.getAssetPlayer(d);
      if (this.log(`buffered to end of asset ${x}`), !x || !this.schedule)
        return;
      const D = this.schedule.findEventIndex(t.identifier), A = (S = this.schedule.items) == null ? void 0 : S[D];
      this.isInterstitial(A) && this.advanceAssetBuffering(A, e);
    };
    g.on(m.BUFFERED_TO_END, E);
    const T = (S) => () => {
      if (!this.getAssetPlayer(d) || !this.schedule)
        return;
      this.shouldPlay = !0;
      const D = this.schedule.findEventIndex(t.identifier);
      this.advanceAfterAssetEnded(t, D, S);
    };
    return g.once(m.MEDIA_ENDED, T(i)), g.once(m.PLAYOUT_LIMIT_REACHED, T(1 / 0)), g.on(m.ERROR, (S, x) => {
      if (!this.schedule)
        return;
      const D = this.getAssetPlayer(d);
      if (x.details === L.BUFFER_STALLED_ERROR) {
        if (D != null && D.appendInPlace) {
          this.handleInPlaceStall(t);
          return;
        }
        this.onTimeupdate(), this.checkBuffer(!0);
        return;
      }
      this.handleAssetItemError(x, t, this.schedule.findEventIndex(t.identifier), i, `Asset player error ${x.error} ${t}`);
    }), g.on(m.DESTROYING, () => {
      if (!this.getAssetPlayer(d) || !this.schedule)
        return;
      const x = new Error(`Asset player destroyed unexpectedly ${d}`), D = {
        fatal: !0,
        type: Y.OTHER_ERROR,
        details: L.INTERSTITIAL_ASSET_ITEM_ERROR,
        error: x
      };
      this.handleAssetItemError(D, t, this.schedule.findEventIndex(t.identifier), i, x.message);
    }), this.log(`INTERSTITIAL_ASSET_PLAYER_CREATED ${He(e)}`), this.hls.trigger(m.INTERSTITIAL_ASSET_PLAYER_CREATED, {
      asset: e,
      assetListIndex: i,
      event: t,
      player: g
    }), g;
  }
  clearInterstitial(t, e) {
    this.clearAssetPlayers(t, e), t.reset();
  }
  clearAssetPlayers(t, e) {
    t.assetList.forEach((i) => {
      this.clearAssetPlayer(i.identifier, e);
    });
  }
  resetAssetPlayer(t) {
    const e = this.getAssetPlayerQueueIndex(t);
    if (e !== -1) {
      this.log(`reset asset player "${t}" after error`);
      const i = this.playerQueue[e];
      this.transferMediaFromPlayer(i, null), i.resetDetails();
    }
  }
  clearAssetPlayer(t, e) {
    const i = this.getAssetPlayerQueueIndex(t);
    if (i !== -1) {
      const s = this.playerQueue[i];
      this.log(`clear ${s} toSegment: ${e && Kt(e)}`), this.transferMediaFromPlayer(s, e), this.playerQueue.splice(i, 1), s.destroy();
    }
  }
  emptyPlayerQueue() {
    let t;
    for (; t = this.playerQueue.pop(); )
      t.destroy();
    this.playerQueue = [];
  }
  startAssetPlayer(t, e, i, s, r) {
    const {
      interstitial: a,
      assetItem: o,
      assetId: c
    } = t, l = a.assetList.length, h = this.playingAsset;
    this.endedAsset = null, this.playingAsset = o, (!h || h.identifier !== c) && (h && (this.clearAssetPlayer(h.identifier, i[s]), delete h.error), this.log(`INTERSTITIAL_ASSET_STARTED ${e + 1}/${l} ${He(o)}`), this.hls.trigger(m.INTERSTITIAL_ASSET_STARTED, {
      asset: o,
      assetListIndex: e,
      event: a,
      schedule: i.slice(0),
      scheduleIndex: s,
      player: t
    })), this.bufferAssetPlayer(t, r);
  }
  bufferAssetPlayer(t, e) {
    var i, s;
    if (!this.schedule)
      return;
    const {
      interstitial: r,
      assetItem: a
    } = t, o = this.schedule.findEventIndex(r.identifier), c = (i = this.schedule.items) == null ? void 0 : i[o];
    if (!c)
      return;
    t.loadSource(), this.setBufferingItem(c), this.bufferingAsset = a;
    const l = this.getBufferingPlayer();
    if (l === t)
      return;
    const h = r.appendInPlace;
    if (h && (l == null ? void 0 : l.interstitial.appendInPlace) === !1)
      return;
    const d = (l == null ? void 0 : l.tracks) || ((s = this.detachedData) == null ? void 0 : s.tracks) || this.requiredTracks;
    if (h && a !== this.playingAsset) {
      if (!t.tracks) {
        this.log(`Waiting for track info before buffering ${t}`);
        return;
      }
      if (d && !va(d, t.tracks)) {
        const u = new Error(`Asset ${He(a)} SourceBuffer tracks ('${Object.keys(t.tracks)}') are not compatible with primary content tracks ('${Object.keys(d)}')`), f = {
          fatal: !0,
          type: Y.OTHER_ERROR,
          details: L.INTERSTITIAL_ASSET_ITEM_ERROR,
          error: u
        }, g = r.findAssetIndex(a);
        this.handleAssetItemError(f, r, o, g, u.message);
        return;
      }
    }
    this.transferMediaTo(t, e);
  }
  handleInPlaceStall(t) {
    const e = this.schedule, i = this.primaryMedia;
    if (!e || !i)
      return;
    const s = i.currentTime, r = e.findAssetIndex(t, s), a = t.assetList[r];
    if (a) {
      const o = this.getAssetPlayer(a.identifier);
      if (o) {
        const c = o.currentTime || s - a.timelineStart, l = o.duration - c;
        if (this.warn(`Stalled at ${c} of ${c + l} in ${o} ${t} (media.currentTime: ${s})`), c && (l / i.playbackRate < 0.5 || o.bufferedInPlaceToEnd(i)) && o.hls) {
          const h = e.findEventIndex(t.identifier);
          this.advanceAfterAssetEnded(t, h, r);
        }
      }
    }
  }
  advanceInPlace(t) {
    const e = this.primaryMedia;
    e && e.currentTime < t && (e.currentTime = t);
  }
  handleAssetItemError(t, e, i, s, r) {
    if (t.details === L.BUFFER_STALLED_ERROR)
      return;
    const a = e.assetList[s] || null;
    if (this.warn(`INTERSTITIAL_ASSET_ERROR ${a && He(a)} ${t.error}`), !this.schedule)
      return;
    const o = (a == null ? void 0 : a.identifier) || "", c = this.getAssetPlayerQueueIndex(o), l = this.playerQueue[c] || null, h = this.schedule.items, d = nt({}, t, {
      fatal: !1,
      errorAction: We(!0),
      asset: a,
      assetListIndex: s,
      event: e,
      schedule: h,
      scheduleIndex: i,
      player: l
    });
    if (this.hls.trigger(m.INTERSTITIAL_ASSET_ERROR, d), !t.fatal)
      return;
    const u = this.playingAsset, f = this.bufferingAsset, g = new Error(r);
    if (a && (this.clearAssetPlayer(o, null), a.error = g), !e.assetList.some((v) => !v.error))
      e.error = g;
    else
      for (let v = s; v < e.assetList.length; v++)
        this.resetAssetPlayer(e.assetList[v].identifier);
    this.updateSchedule(!0), e.error ? this.primaryFallback(e) : u && u.identifier === o ? this.advanceAfterAssetEnded(e, i, s) : f && f.identifier === o && this.isInterstitial(this.bufferingItem) && this.advanceAssetBuffering(this.bufferingItem, f);
  }
  primaryFallback(t) {
    const e = t.timelineStart, i = this.effectivePlayingItem;
    let s = this.timelinePos;
    if (i) {
      this.log(`Fallback to primary from event "${t.identifier}" start: ${e} pos: ${s} playing: ${Kt(i)} error: ${t.error}`), s === -1 && (s = this.hls.startPosition);
      const a = this.updateItem(i, s);
      this.itemsMatch(i, a) && this.clearInterstitial(t, null), t.appendInPlace && (this.attachPrimary(e, null), this.flushFrontBuffer(e));
    } else if (s === -1) {
      this.checkStart();
      return;
    }
    if (!this.schedule)
      return;
    const r = this.schedule.findItemIndexAtTime(s);
    this.setSchedulePosition(r);
  }
  // Asset List loading
  onAssetListLoaded(t, e) {
    var i, s;
    const r = e.event, a = r.identifier, o = e.assetListResponse.ASSETS;
    if (!((i = this.schedule) != null && i.hasEvent(a)))
      return;
    const c = r.timelineStart, l = r.duration;
    let h = 0;
    o.forEach((v, p) => {
      const y = parseFloat(v.DURATION);
      this.createAsset(r, p, h, c + h, y, v.URI), h += y;
    }), r.duration = h, this.log(`Loaded asset-list with duration: ${h} (was: ${l}) ${r}`);
    const d = this.waitingItem, u = (d == null ? void 0 : d.event.identifier) === a;
    this.updateSchedule();
    const f = (s = this.bufferingItem) == null ? void 0 : s.event;
    if (u) {
      var g;
      const v = this.schedule.findEventIndex(a), p = (g = this.schedule.items) == null ? void 0 : g[v];
      if (p) {
        if (!this.playingItem && this.timelinePos > p.end && this.schedule.findItemIndexAtTime(this.timelinePos) !== v) {
          r.error = new Error(`Interstitial ${o.length ? "no longer within playback range" : "asset-list is empty"} ${this.timelinePos} ${r}`), this.log(r.error.message), this.updateSchedule(!0), this.primaryFallback(r);
          return;
        }
        this.setBufferingItem(p);
      }
      this.setSchedulePosition(v);
    } else if ((f == null ? void 0 : f.identifier) === a) {
      const v = r.assetList[0];
      if (v) {
        const p = this.getAssetPlayer(v.identifier);
        if (f.appendInPlace) {
          const y = this.primaryMedia;
          p && y && this.bufferAssetPlayer(p, y);
        } else p && p.loadSource();
      }
    }
  }
  onError(t, e) {
    if (this.schedule)
      switch (e.details) {
        case L.ASSET_LIST_PARSING_ERROR:
        case L.ASSET_LIST_LOAD_ERROR:
        case L.ASSET_LIST_LOAD_TIMEOUT: {
          const i = e.interstitial;
          i && (this.updateSchedule(!0), this.primaryFallback(i));
          break;
        }
        case L.BUFFER_STALLED_ERROR: {
          const i = this.endedItem || this.waitingItem || this.playingItem;
          if (this.isInterstitial(i) && i.event.appendInPlace) {
            this.handleInPlaceStall(i.event);
            return;
          }
          this.log(`Primary player stall @${this.timelinePos} bufferedPos: ${this.bufferedPos}`), this.onTimeupdate(), this.checkBuffer(!0);
          break;
        }
      }
  }
}
const Zn = 500;
class Lu extends Rr {
  constructor(t, e, i) {
    super(t, e, i, "subtitle-stream-controller", K.SUBTITLE), this.currentTrackId = -1, this.tracksBuffered = [], this.mainDetails = null, this.registerListeners();
  }
  onHandlerDestroying() {
    this.unregisterListeners(), super.onHandlerDestroying(), this.mainDetails = null;
  }
  registerListeners() {
    super.registerListeners();
    const {
      hls: t
    } = this;
    t.on(m.LEVEL_LOADED, this.onLevelLoaded, this), t.on(m.SUBTITLE_TRACKS_UPDATED, this.onSubtitleTracksUpdated, this), t.on(m.SUBTITLE_TRACK_SWITCH, this.onSubtitleTrackSwitch, this), t.on(m.SUBTITLE_TRACK_LOADED, this.onSubtitleTrackLoaded, this), t.on(m.SUBTITLE_FRAG_PROCESSED, this.onSubtitleFragProcessed, this), t.on(m.BUFFER_FLUSHING, this.onBufferFlushing, this);
  }
  unregisterListeners() {
    super.unregisterListeners();
    const {
      hls: t
    } = this;
    t.off(m.LEVEL_LOADED, this.onLevelLoaded, this), t.off(m.SUBTITLE_TRACKS_UPDATED, this.onSubtitleTracksUpdated, this), t.off(m.SUBTITLE_TRACK_SWITCH, this.onSubtitleTrackSwitch, this), t.off(m.SUBTITLE_TRACK_LOADED, this.onSubtitleTrackLoaded, this), t.off(m.SUBTITLE_FRAG_PROCESSED, this.onSubtitleFragProcessed, this), t.off(m.BUFFER_FLUSHING, this.onBufferFlushing, this);
  }
  startLoad(t, e) {
    this.stopLoad(), this.state = w.IDLE, this.setInterval(Zn), this.nextLoadPosition = this.lastCurrentTime = t + this.timelineOffset, this.startPosition = e ? -1 : t, this.tick();
  }
  onManifestLoading() {
    super.onManifestLoading(), this.mainDetails = null;
  }
  onMediaDetaching(t, e) {
    this.tracksBuffered = [], super.onMediaDetaching(t, e);
  }
  onLevelLoaded(t, e) {
    this.mainDetails = e.details;
  }
  onSubtitleFragProcessed(t, e) {
    const {
      frag: i,
      success: s
    } = e;
    if (this.fragContextChanged(i) || (ut(i) && (this.fragPrevious = i), this.state = w.IDLE), !s)
      return;
    const r = this.tracksBuffered[this.currentTrackId];
    if (!r)
      return;
    let a;
    const o = i.start;
    for (let l = 0; l < r.length; l++)
      if (o >= r[l].start && o <= r[l].end) {
        a = r[l];
        break;
      }
    const c = i.start + i.duration;
    a ? a.end = c : (a = {
      start: o,
      end: c
    }, r.push(a)), this.fragmentTracker.fragBuffered(i), this.fragBufferedComplete(i, null), this.media && this.tick();
  }
  onBufferFlushing(t, e) {
    const {
      startOffset: i,
      endOffset: s
    } = e;
    if (i === 0 && s !== Number.POSITIVE_INFINITY) {
      const r = s - 1;
      if (r <= 0)
        return;
      e.endOffsetSubtitles = Math.max(0, r), this.tracksBuffered.forEach((a) => {
        for (let o = 0; o < a.length; ) {
          if (a[o].end <= r) {
            a.shift();
            continue;
          } else if (a[o].start < r)
            a[o].start = r;
          else
            break;
          o++;
        }
      }), this.fragmentTracker.removeFragmentsInRange(i, r, K.SUBTITLE);
    }
  }
  // If something goes wrong, proceed to next frag, if we were processing one.
  onError(t, e) {
    const i = e.frag;
    (i == null ? void 0 : i.type) === K.SUBTITLE && (e.details === L.FRAG_GAP && this.fragmentTracker.fragBuffered(i, !0), this.fragCurrent && this.fragCurrent.abortRequests(), this.state !== w.STOPPED && (this.state = w.IDLE));
  }
  // Got all new subtitle levels.
  onSubtitleTracksUpdated(t, {
    subtitleTracks: e
  }) {
    if (this.levels && So(this.levels, e)) {
      this.levels = e.map((i) => new pi(i));
      return;
    }
    this.tracksBuffered = [], this.levels = e.map((i) => {
      const s = new pi(i);
      return this.tracksBuffered[s.id] = [], s;
    }), this.fragmentTracker.removeFragmentsInRange(0, Number.POSITIVE_INFINITY, K.SUBTITLE), this.fragPrevious = null, this.mediaBuffer = null;
  }
  onSubtitleTrackSwitch(t, e) {
    var i;
    if (this.currentTrackId = e.id, !((i = this.levels) != null && i.length) || this.currentTrackId === -1) {
      this.clearInterval();
      return;
    }
    const s = this.levels[this.currentTrackId];
    s != null && s.details ? this.mediaBuffer = this.mediaBufferTimeRanges : this.mediaBuffer = null, s && this.state !== w.STOPPED && this.setInterval(Zn);
  }
  // Got a new set of subtitle fragments.
  onSubtitleTrackLoaded(t, e) {
    var i;
    const {
      currentTrackId: s,
      levels: r
    } = this, {
      details: a,
      id: o
    } = e;
    if (!r) {
      this.warn(`Subtitle tracks were reset while loading level ${o}`);
      return;
    }
    const c = r[o];
    if (o >= r.length || !c)
      return;
    this.log(`Subtitle track ${o} loaded [${a.startSN},${a.endSN}]${a.lastPartSn ? `[part-${a.lastPartSn}-${a.lastPartIndex}]` : ""},duration:${a.totalduration}`), this.mediaBuffer = this.mediaBufferTimeRanges;
    let l = 0;
    if (a.live || (i = c.details) != null && i.live) {
      if (a.deltaUpdateFailed)
        return;
      const d = this.mainDetails;
      if (!d) {
        this.startFragRequested = !1;
        return;
      }
      const u = d.fragments[0];
      if (!c.details)
        a.hasProgramDateTime && d.hasProgramDateTime ? (ns(a, d), l = a.fragmentStart) : u && (l = u.start, sr(a, l));
      else {
        var h;
        l = this.alignPlaylists(a, c.details, (h = this.levelLastLoaded) == null ? void 0 : h.details), l === 0 && u && (l = u.start, sr(a, l));
      }
      d && !this.startFragRequested && this.setStartPosition(d, l);
    }
    c.details = a, this.levelLastLoaded = c, o === s && (this.hls.trigger(m.SUBTITLE_TRACK_UPDATED, {
      details: a,
      id: o,
      groupId: e.groupId
    }), this.tick(), a.live && !this.fragCurrent && this.media && this.state === w.IDLE && (De(null, a.fragments, this.media.currentTime, 0) || (this.warn("Subtitle playlist not aligned with playback"), c.details = void 0)));
  }
  _handleFragmentLoadComplete(t) {
    const {
      frag: e,
      payload: i
    } = t, s = e.decryptdata, r = this.hls;
    if (!this.fragContextChanged(e) && i && i.byteLength > 0 && s != null && s.key && s.iv && Ye(s.method)) {
      const a = performance.now();
      this.decrypter.decrypt(new Uint8Array(i), s.key.buffer, s.iv.buffer, Ir(s.method)).catch((o) => {
        throw r.trigger(m.ERROR, {
          type: Y.MEDIA_ERROR,
          details: L.FRAG_DECRYPT_ERROR,
          fatal: !1,
          error: o,
          reason: o.message,
          frag: e
        }), o;
      }).then((o) => {
        const c = performance.now();
        r.trigger(m.FRAG_DECRYPTED, {
          frag: e,
          payload: o,
          stats: {
            tstart: a,
            tdecrypt: c
          }
        });
      }).catch((o) => {
        this.warn(`${o.name}: ${o.message}`), this.state = w.IDLE;
      });
    }
  }
  doTick() {
    if (!this.media) {
      this.state = w.IDLE;
      return;
    }
    if (this.state === w.IDLE) {
      const {
        currentTrackId: t,
        levels: e
      } = this, i = e == null ? void 0 : e[t];
      if (!i || !e.length || !i.details || this.waitForLive(i))
        return;
      const {
        config: s
      } = this, r = this.getLoadPosition(), a = q.bufferedInfo(this.tracksBuffered[this.currentTrackId] || [], r, s.maxBufferHole), {
        end: o,
        len: c
      } = a, l = i.details, h = this.hls.maxBufferLength + l.levelTargetDuration;
      if (c > h)
        return;
      const d = l.fragments, u = d.length, f = l.edge;
      let g = null;
      const v = this.fragPrevious;
      if (o < f) {
        const E = s.maxFragLookUpTolerance, T = o > f - E ? 0 : E;
        g = De(v, d, Math.max(d[0].start, o), T), !g && v && v.start < d[0].start && (g = d[0]);
      } else
        g = d[u - 1];
      if (g = this.filterReplacedPrimary(g, i.details), !g)
        return;
      const p = g.sn - l.startSN, y = d[p - 1];
      if (y && y.cc === g.cc && this.fragmentTracker.getState(y) === yt.NOT_LOADED && (g = y), this.fragmentTracker.getState(g) === yt.NOT_LOADED) {
        const E = this.mapToInitFragWhenRequired(g);
        E && this.loadFragment(E, i, o);
      }
    }
  }
  loadFragment(t, e, i) {
    ut(t) ? super.loadFragment(t, e, i) : this._loadInitSegment(t, e);
  }
  get mediaBufferTimeRanges() {
    return new Ru(this.tracksBuffered[this.currentTrackId] || []);
  }
}
class Ru {
  constructor(t) {
    this.buffered = void 0;
    const e = (i, s, r) => {
      if (s = s >>> 0, s > r - 1)
        throw new DOMException(`Failed to execute '${i}' on 'TimeRanges': The index provided (${s}) is greater than the maximum bound (${r})`);
      return t[s][i];
    };
    this.buffered = {
      get length() {
        return t.length;
      },
      end(i) {
        return e("end", i, t.length);
      },
      start(i) {
        return e("start", i, t.length);
      }
    };
  }
}
const _u = {
  42: 225,
  // lowercase a, acute accent
  92: 233,
  // lowercase e, acute accent
  94: 237,
  // lowercase i, acute accent
  95: 243,
  // lowercase o, acute accent
  96: 250,
  // lowercase u, acute accent
  123: 231,
  // lowercase c with cedilla
  124: 247,
  // division symbol
  125: 209,
  // uppercase N tilde
  126: 241,
  // lowercase n tilde
  127: 9608,
  // Full block
  // THIS BLOCK INCLUDES THE 16 EXTENDED (TWO-BYTE) LINE 21 CHARACTERS
  // THAT COME FROM HI BYTE=0x11 AND LOW BETWEEN 0x30 AND 0x3F
  // THIS MEANS THAT \x50 MUST BE ADDED TO THE VALUES
  128: 174,
  // Registered symbol (R)
  129: 176,
  // degree sign
  130: 189,
  // 1/2 symbol
  131: 191,
  // Inverted (open) question mark
  132: 8482,
  // Trademark symbol (TM)
  133: 162,
  // Cents symbol
  134: 163,
  // Pounds sterling
  135: 9834,
  // Music 8'th note
  136: 224,
  // lowercase a, grave accent
  137: 32,
  // transparent space (regular)
  138: 232,
  // lowercase e, grave accent
  139: 226,
  // lowercase a, circumflex accent
  140: 234,
  // lowercase e, circumflex accent
  141: 238,
  // lowercase i, circumflex accent
  142: 244,
  // lowercase o, circumflex accent
  143: 251,
  // lowercase u, circumflex accent
  // THIS BLOCK INCLUDES THE 32 EXTENDED (TWO-BYTE) LINE 21 CHARACTERS
  // THAT COME FROM HI BYTE=0x12 AND LOW BETWEEN 0x20 AND 0x3F
  144: 193,
  // capital letter A with acute
  145: 201,
  // capital letter E with acute
  146: 211,
  // capital letter O with acute
  147: 218,
  // capital letter U with acute
  148: 220,
  // capital letter U with diaresis
  149: 252,
  // lowercase letter U with diaeresis
  150: 8216,
  // opening single quote
  151: 161,
  // inverted exclamation mark
  152: 42,
  // asterisk
  153: 8217,
  // closing single quote
  154: 9473,
  // box drawings heavy horizontal
  155: 169,
  // copyright sign
  156: 8480,
  // Service mark
  157: 8226,
  // (round) bullet
  158: 8220,
  // Left double quotation mark
  159: 8221,
  // Right double quotation mark
  160: 192,
  // uppercase A, grave accent
  161: 194,
  // uppercase A, circumflex
  162: 199,
  // uppercase C with cedilla
  163: 200,
  // uppercase E, grave accent
  164: 202,
  // uppercase E, circumflex
  165: 203,
  // capital letter E with diaresis
  166: 235,
  // lowercase letter e with diaresis
  167: 206,
  // uppercase I, circumflex
  168: 207,
  // uppercase I, with diaresis
  169: 239,
  // lowercase i, with diaresis
  170: 212,
  // uppercase O, circumflex
  171: 217,
  // uppercase U, grave accent
  172: 249,
  // lowercase u, grave accent
  173: 219,
  // uppercase U, circumflex
  174: 171,
  // left-pointing double angle quotation mark
  175: 187,
  // right-pointing double angle quotation mark
  // THIS BLOCK INCLUDES THE 32 EXTENDED (TWO-BYTE) LINE 21 CHARACTERS
  // THAT COME FROM HI BYTE=0x13 AND LOW BETWEEN 0x20 AND 0x3F
  176: 195,
  // Uppercase A, tilde
  177: 227,
  // Lowercase a, tilde
  178: 205,
  // Uppercase I, acute accent
  179: 204,
  // Uppercase I, grave accent
  180: 236,
  // Lowercase i, grave accent
  181: 210,
  // Uppercase O, grave accent
  182: 242,
  // Lowercase o, grave accent
  183: 213,
  // Uppercase O, tilde
  184: 245,
  // Lowercase o, tilde
  185: 123,
  // Open curly brace
  186: 125,
  // Closing curly brace
  187: 92,
  // Backslash
  188: 94,
  // Caret
  189: 95,
  // Underscore
  190: 124,
  // Pipe (vertical line)
  191: 8764,
  // Tilde operator
  192: 196,
  // Uppercase A, umlaut
  193: 228,
  // Lowercase A, umlaut
  194: 214,
  // Uppercase O, umlaut
  195: 246,
  // Lowercase o, umlaut
  196: 223,
  // Esszett (sharp S)
  197: 165,
  // Yen symbol
  198: 164,
  // Generic currency sign
  199: 9475,
  // Box drawings heavy vertical
  200: 197,
  // Uppercase A, ring
  201: 229,
  // Lowercase A, ring
  202: 216,
  // Uppercase O, stroke
  203: 248,
  // Lowercase o, strok
  204: 9487,
  // Box drawings heavy down and right
  205: 9491,
  // Box drawings heavy down and left
  206: 9495,
  // Box drawings heavy up and right
  207: 9499
  // Box drawings heavy up and left
}, $o = (n) => String.fromCharCode(_u[n] || n), Ht = 15, ie = 100, Du = {
  17: 1,
  18: 3,
  21: 5,
  22: 7,
  23: 9,
  16: 11,
  19: 12,
  20: 14
}, wu = {
  17: 2,
  18: 4,
  21: 6,
  22: 8,
  23: 10,
  19: 13,
  20: 15
}, Cu = {
  25: 1,
  26: 3,
  29: 5,
  30: 7,
  31: 9,
  24: 11,
  27: 12,
  28: 14
}, Pu = {
  25: 2,
  26: 4,
  29: 6,
  30: 8,
  31: 10,
  27: 13,
  28: 15
}, ku = ["white", "green", "blue", "cyan", "red", "yellow", "magenta", "black", "transparent"];
class Ou {
  constructor() {
    this.time = null, this.verboseLevel = 0;
  }
  log(t, e) {
    if (this.verboseLevel >= t) {
      const i = typeof e == "function" ? e() : e;
      rt.log(`${this.time} [${t}] ${i}`);
    }
  }
}
const be = function(t) {
  const e = [];
  for (let i = 0; i < t.length; i++)
    e.push(t[i].toString(16));
  return e;
};
class No {
  constructor() {
    this.foreground = "white", this.underline = !1, this.italics = !1, this.background = "black", this.flash = !1;
  }
  reset() {
    this.foreground = "white", this.underline = !1, this.italics = !1, this.background = "black", this.flash = !1;
  }
  setStyles(t) {
    const e = ["foreground", "underline", "italics", "background", "flash"];
    for (let i = 0; i < e.length; i++) {
      const s = e[i];
      t.hasOwnProperty(s) && (this[s] = t[s]);
    }
  }
  isDefault() {
    return this.foreground === "white" && !this.underline && !this.italics && this.background === "black" && !this.flash;
  }
  equals(t) {
    return this.foreground === t.foreground && this.underline === t.underline && this.italics === t.italics && this.background === t.background && this.flash === t.flash;
  }
  copy(t) {
    this.foreground = t.foreground, this.underline = t.underline, this.italics = t.italics, this.background = t.background, this.flash = t.flash;
  }
  toString() {
    return "color=" + this.foreground + ", underline=" + this.underline + ", italics=" + this.italics + ", background=" + this.background + ", flash=" + this.flash;
  }
}
class Mu {
  constructor() {
    this.uchar = " ", this.penState = new No();
  }
  reset() {
    this.uchar = " ", this.penState.reset();
  }
  setChar(t, e) {
    this.uchar = t, this.penState.copy(e);
  }
  setPenState(t) {
    this.penState.copy(t);
  }
  equals(t) {
    return this.uchar === t.uchar && this.penState.equals(t.penState);
  }
  copy(t) {
    this.uchar = t.uchar, this.penState.copy(t.penState);
  }
  isEmpty() {
    return this.uchar === " " && this.penState.isDefault();
  }
}
class Fu {
  constructor(t) {
    this.chars = [], this.pos = 0, this.currPenState = new No(), this.cueStartTime = null, this.logger = void 0;
    for (let e = 0; e < ie; e++)
      this.chars.push(new Mu());
    this.logger = t;
  }
  equals(t) {
    for (let e = 0; e < ie; e++)
      if (!this.chars[e].equals(t.chars[e]))
        return !1;
    return !0;
  }
  copy(t) {
    for (let e = 0; e < ie; e++)
      this.chars[e].copy(t.chars[e]);
  }
  isEmpty() {
    let t = !0;
    for (let e = 0; e < ie; e++)
      if (!this.chars[e].isEmpty()) {
        t = !1;
        break;
      }
    return t;
  }
  /**
   *  Set the cursor to a valid column.
   */
  setCursor(t) {
    this.pos !== t && (this.pos = t), this.pos < 0 ? (this.logger.log(3, "Negative cursor position " + this.pos), this.pos = 0) : this.pos > ie && (this.logger.log(3, "Too large cursor position " + this.pos), this.pos = ie);
  }
  /**
   * Move the cursor relative to current position.
   */
  moveCursor(t) {
    const e = this.pos + t;
    if (t > 1)
      for (let i = this.pos + 1; i < e + 1; i++)
        this.chars[i].setPenState(this.currPenState);
    this.setCursor(e);
  }
  /**
   * Backspace, move one step back and clear character.
   */
  backSpace() {
    this.moveCursor(-1), this.chars[this.pos].setChar(" ", this.currPenState);
  }
  insertChar(t) {
    t >= 144 && this.backSpace();
    const e = $o(t);
    if (this.pos >= ie) {
      this.logger.log(0, () => "Cannot insert " + t.toString(16) + " (" + e + ") at position " + this.pos + ". Skipping it!");
      return;
    }
    this.chars[this.pos].setChar(e, this.currPenState), this.moveCursor(1);
  }
  clearFromPos(t) {
    let e;
    for (e = t; e < ie; e++)
      this.chars[e].reset();
  }
  clear() {
    this.clearFromPos(0), this.pos = 0, this.currPenState.reset();
  }
  clearToEndOfRow() {
    this.clearFromPos(this.pos);
  }
  getTextString() {
    const t = [];
    let e = !0;
    for (let i = 0; i < ie; i++) {
      const s = this.chars[i].uchar;
      s !== " " && (e = !1), t.push(s);
    }
    return e ? "" : t.join("");
  }
  setPenStyles(t) {
    this.currPenState.setStyles(t), this.chars[this.pos].setPenState(this.currPenState);
  }
}
class Ms {
  constructor(t) {
    this.rows = [], this.currRow = Ht - 1, this.nrRollUpRows = null, this.lastOutputScreen = null, this.logger = void 0;
    for (let e = 0; e < Ht; e++)
      this.rows.push(new Fu(t));
    this.logger = t;
  }
  reset() {
    for (let t = 0; t < Ht; t++)
      this.rows[t].clear();
    this.currRow = Ht - 1;
  }
  equals(t) {
    let e = !0;
    for (let i = 0; i < Ht; i++)
      if (!this.rows[i].equals(t.rows[i])) {
        e = !1;
        break;
      }
    return e;
  }
  copy(t) {
    for (let e = 0; e < Ht; e++)
      this.rows[e].copy(t.rows[e]);
  }
  isEmpty() {
    let t = !0;
    for (let e = 0; e < Ht; e++)
      if (!this.rows[e].isEmpty()) {
        t = !1;
        break;
      }
    return t;
  }
  backSpace() {
    this.rows[this.currRow].backSpace();
  }
  clearToEndOfRow() {
    this.rows[this.currRow].clearToEndOfRow();
  }
  /**
   * Insert a character (without styling) in the current row.
   */
  insertChar(t) {
    this.rows[this.currRow].insertChar(t);
  }
  setPen(t) {
    this.rows[this.currRow].setPenStyles(t);
  }
  moveCursor(t) {
    this.rows[this.currRow].moveCursor(t);
  }
  setCursor(t) {
    this.logger.log(2, "setCursor: " + t), this.rows[this.currRow].setCursor(t);
  }
  setPAC(t) {
    this.logger.log(2, () => "pacData = " + ot(t));
    let e = t.row - 1;
    if (this.nrRollUpRows && e < this.nrRollUpRows - 1 && (e = this.nrRollUpRows - 1), this.nrRollUpRows && this.currRow !== e) {
      for (let o = 0; o < Ht; o++)
        this.rows[o].clear();
      const r = this.currRow + 1 - this.nrRollUpRows, a = this.lastOutputScreen;
      if (a) {
        const o = a.rows[r].cueStartTime, c = this.logger.time;
        if (o !== null && c !== null && o < c)
          for (let l = 0; l < this.nrRollUpRows; l++)
            this.rows[e - this.nrRollUpRows + l + 1].copy(a.rows[r + l]);
      }
    }
    this.currRow = e;
    const i = this.rows[this.currRow];
    if (t.indent !== null) {
      const r = t.indent, a = Math.max(r - 1, 0);
      i.setCursor(t.indent), t.color = i.chars[a].penState.foreground;
    }
    const s = {
      foreground: t.color,
      underline: t.underline,
      italics: t.italics,
      background: "black",
      flash: !1
    };
    this.setPen(s);
  }
  /**
   * Set background/extra foreground, but first do back_space, and then insert space (backwards compatibility).
   */
  setBkgData(t) {
    this.logger.log(2, () => "bkgData = " + ot(t)), this.backSpace(), this.setPen(t), this.insertChar(32);
  }
  setRollUpRows(t) {
    this.nrRollUpRows = t;
  }
  rollUp() {
    if (this.nrRollUpRows === null) {
      this.logger.log(3, "roll_up but nrRollUpRows not set yet");
      return;
    }
    this.logger.log(1, () => this.getDisplayText());
    const t = this.currRow + 1 - this.nrRollUpRows, e = this.rows.splice(t, 1)[0];
    e.clear(), this.rows.splice(this.currRow, 0, e), this.logger.log(2, "Rolling up");
  }
  /**
   * Get all non-empty rows with as unicode text.
   */
  getDisplayText(t) {
    t = t || !1;
    const e = [];
    let i = "", s = -1;
    for (let r = 0; r < Ht; r++) {
      const a = this.rows[r].getTextString();
      a && (s = r + 1, t ? e.push("Row " + s + ": '" + a + "'") : e.push(a.trim()));
    }
    return e.length > 0 && (t ? i = "[" + e.join(" | ") + "]" : i = e.join(`
`)), i;
  }
  getTextAndFormat() {
    return this.rows;
  }
}
class Jn {
  constructor(t, e, i) {
    this.chNr = void 0, this.outputFilter = void 0, this.mode = void 0, this.verbose = void 0, this.displayedMemory = void 0, this.nonDisplayedMemory = void 0, this.lastOutputScreen = void 0, this.currRollUpRow = void 0, this.writeScreen = void 0, this.cueStartTime = void 0, this.logger = void 0, this.chNr = t, this.outputFilter = e, this.mode = null, this.verbose = 0, this.displayedMemory = new Ms(i), this.nonDisplayedMemory = new Ms(i), this.lastOutputScreen = new Ms(i), this.currRollUpRow = this.displayedMemory.rows[Ht - 1], this.writeScreen = this.displayedMemory, this.mode = null, this.cueStartTime = null, this.logger = i;
  }
  reset() {
    this.mode = null, this.displayedMemory.reset(), this.nonDisplayedMemory.reset(), this.lastOutputScreen.reset(), this.outputFilter.reset(), this.currRollUpRow = this.displayedMemory.rows[Ht - 1], this.writeScreen = this.displayedMemory, this.mode = null, this.cueStartTime = null;
  }
  getHandler() {
    return this.outputFilter;
  }
  setHandler(t) {
    this.outputFilter = t;
  }
  setPAC(t) {
    this.writeScreen.setPAC(t);
  }
  setBkgData(t) {
    this.writeScreen.setBkgData(t);
  }
  setMode(t) {
    t !== this.mode && (this.mode = t, this.logger.log(2, () => "MODE=" + t), this.mode === "MODE_POP-ON" ? this.writeScreen = this.nonDisplayedMemory : (this.writeScreen = this.displayedMemory, this.writeScreen.reset()), this.mode !== "MODE_ROLL-UP" && (this.displayedMemory.nrRollUpRows = null, this.nonDisplayedMemory.nrRollUpRows = null), this.mode = t);
  }
  insertChars(t) {
    for (let i = 0; i < t.length; i++)
      this.writeScreen.insertChar(t[i]);
    const e = this.writeScreen === this.displayedMemory ? "DISP" : "NON_DISP";
    this.logger.log(2, () => e + ": " + this.writeScreen.getDisplayText(!0)), (this.mode === "MODE_PAINT-ON" || this.mode === "MODE_ROLL-UP") && (this.logger.log(1, () => "DISPLAYED: " + this.displayedMemory.getDisplayText(!0)), this.outputDataUpdate());
  }
  ccRCL() {
    this.logger.log(2, "RCL - Resume Caption Loading"), this.setMode("MODE_POP-ON");
  }
  ccBS() {
    this.logger.log(2, "BS - BackSpace"), this.mode !== "MODE_TEXT" && (this.writeScreen.backSpace(), this.writeScreen === this.displayedMemory && this.outputDataUpdate());
  }
  ccAOF() {
  }
  ccAON() {
  }
  ccDER() {
    this.logger.log(2, "DER- Delete to End of Row"), this.writeScreen.clearToEndOfRow(), this.outputDataUpdate();
  }
  ccRU(t) {
    this.logger.log(2, "RU(" + t + ") - Roll Up"), this.writeScreen = this.displayedMemory, this.setMode("MODE_ROLL-UP"), this.writeScreen.setRollUpRows(t);
  }
  ccFON() {
    this.logger.log(2, "FON - Flash On"), this.writeScreen.setPen({
      flash: !0
    });
  }
  ccRDC() {
    this.logger.log(2, "RDC - Resume Direct Captioning"), this.setMode("MODE_PAINT-ON");
  }
  ccTR() {
    this.logger.log(2, "TR"), this.setMode("MODE_TEXT");
  }
  ccRTD() {
    this.logger.log(2, "RTD"), this.setMode("MODE_TEXT");
  }
  ccEDM() {
    this.logger.log(2, "EDM - Erase Displayed Memory"), this.displayedMemory.reset(), this.outputDataUpdate(!0);
  }
  ccCR() {
    this.logger.log(2, "CR - Carriage Return"), this.writeScreen.rollUp(), this.outputDataUpdate(!0);
  }
  ccENM() {
    this.logger.log(2, "ENM - Erase Non-displayed Memory"), this.nonDisplayedMemory.reset();
  }
  ccEOC() {
    if (this.logger.log(2, "EOC - End Of Caption"), this.mode === "MODE_POP-ON") {
      const t = this.displayedMemory;
      this.displayedMemory = this.nonDisplayedMemory, this.nonDisplayedMemory = t, this.writeScreen = this.nonDisplayedMemory, this.logger.log(1, () => "DISP: " + this.displayedMemory.getDisplayText());
    }
    this.outputDataUpdate(!0);
  }
  ccTO(t) {
    this.logger.log(2, "TO(" + t + ") - Tab Offset"), this.writeScreen.moveCursor(t);
  }
  ccMIDROW(t) {
    const e = {
      flash: !1
    };
    if (e.underline = t % 2 === 1, e.italics = t >= 46, e.italics)
      e.foreground = "white";
    else {
      const i = Math.floor(t / 2) - 16, s = ["white", "green", "blue", "cyan", "red", "yellow", "magenta"];
      e.foreground = s[i];
    }
    this.logger.log(2, "MIDROW: " + ot(e)), this.writeScreen.setPen(e);
  }
  outputDataUpdate(t = !1) {
    const e = this.logger.time;
    e !== null && this.outputFilter && (this.cueStartTime === null && !this.displayedMemory.isEmpty() ? this.cueStartTime = e : this.displayedMemory.equals(this.lastOutputScreen) || (this.outputFilter.newCue(this.cueStartTime, e, this.lastOutputScreen), t && this.outputFilter.dispatchCue && this.outputFilter.dispatchCue(), this.cueStartTime = this.displayedMemory.isEmpty() ? null : e), this.lastOutputScreen.copy(this.displayedMemory));
  }
  cueSplitAtTime(t) {
    this.outputFilter && (this.displayedMemory.isEmpty() || (this.outputFilter.newCue && this.outputFilter.newCue(this.cueStartTime, t, this.displayedMemory), this.cueStartTime = t));
  }
}
class ta {
  constructor(t, e, i) {
    this.channels = void 0, this.currentChannel = 0, this.cmdHistory = Nu(), this.logger = void 0;
    const s = this.logger = new Ou();
    this.channels = [null, new Jn(t, e, s), new Jn(t + 1, i, s)];
  }
  getHandler(t) {
    return this.channels[t].getHandler();
  }
  setHandler(t, e) {
    this.channels[t].setHandler(e);
  }
  /**
   * Add data for time t in forms of list of bytes (unsigned ints). The bytes are treated as pairs.
   */
  addData(t, e) {
    this.logger.time = t;
    for (let i = 0; i < e.length; i += 2) {
      const s = e[i] & 127, r = e[i + 1] & 127;
      let a = !1, o = null;
      if (s === 0 && r === 0)
        continue;
      this.logger.log(3, () => "[" + be([e[i], e[i + 1]]) + "] -> (" + be([s, r]) + ")");
      const c = this.cmdHistory;
      if (s >= 16 && s <= 31) {
        if ($u(s, r, c)) {
          Fi(null, null, c), this.logger.log(3, () => "Repeated command (" + be([s, r]) + ") is dropped");
          continue;
        }
        Fi(s, r, this.cmdHistory), a = this.parseCmd(s, r), a || (a = this.parseMidrow(s, r)), a || (a = this.parsePAC(s, r)), a || (a = this.parseBackgroundAttributes(s, r));
      } else
        Fi(null, null, c);
      if (!a && (o = this.parseChars(s, r), o)) {
        const h = this.currentChannel;
        h && h > 0 ? this.channels[h].insertChars(o) : this.logger.log(2, "No channel found yet. TEXT-MODE?");
      }
      !a && !o && this.logger.log(2, () => "Couldn't parse cleaned data " + be([s, r]) + " orig: " + be([e[i], e[i + 1]]));
    }
  }
  /**
   * Parse Command.
   * @returns True if a command was found
   */
  parseCmd(t, e) {
    const i = (t === 20 || t === 28 || t === 21 || t === 29) && e >= 32 && e <= 47, s = (t === 23 || t === 31) && e >= 33 && e <= 35;
    if (!(i || s))
      return !1;
    const r = t === 20 || t === 21 || t === 23 ? 1 : 2, a = this.channels[r];
    return t === 20 || t === 21 || t === 28 || t === 29 ? e === 32 ? a.ccRCL() : e === 33 ? a.ccBS() : e === 34 ? a.ccAOF() : e === 35 ? a.ccAON() : e === 36 ? a.ccDER() : e === 37 ? a.ccRU(2) : e === 38 ? a.ccRU(3) : e === 39 ? a.ccRU(4) : e === 40 ? a.ccFON() : e === 41 ? a.ccRDC() : e === 42 ? a.ccTR() : e === 43 ? a.ccRTD() : e === 44 ? a.ccEDM() : e === 45 ? a.ccCR() : e === 46 ? a.ccENM() : e === 47 && a.ccEOC() : a.ccTO(e - 32), this.currentChannel = r, !0;
  }
  /**
   * Parse midrow styling command
   */
  parseMidrow(t, e) {
    let i = 0;
    if ((t === 17 || t === 25) && e >= 32 && e <= 47) {
      if (t === 17 ? i = 1 : i = 2, i !== this.currentChannel)
        return this.logger.log(0, "Mismatch channel in midrow parsing"), !1;
      const s = this.channels[i];
      return s ? (s.ccMIDROW(e), this.logger.log(3, () => "MIDROW (" + be([t, e]) + ")"), !0) : !1;
    }
    return !1;
  }
  /**
   * Parse Preable Access Codes (Table 53).
   * @returns {Boolean} Tells if PAC found
   */
  parsePAC(t, e) {
    let i;
    const s = (t >= 17 && t <= 23 || t >= 25 && t <= 31) && e >= 64 && e <= 127, r = (t === 16 || t === 24) && e >= 64 && e <= 95;
    if (!(s || r))
      return !1;
    const a = t <= 23 ? 1 : 2;
    e >= 64 && e <= 95 ? i = a === 1 ? Du[t] : Cu[t] : i = a === 1 ? wu[t] : Pu[t];
    const o = this.channels[a];
    return o ? (o.setPAC(this.interpretPAC(i, e)), this.currentChannel = a, !0) : !1;
  }
  /**
   * Interpret the second byte of the pac, and return the information.
   * @returns pacData with style parameters
   */
  interpretPAC(t, e) {
    let i;
    const s = {
      color: null,
      italics: !1,
      indent: null,
      underline: !1,
      row: t
    };
    return e > 95 ? i = e - 96 : i = e - 64, s.underline = (i & 1) === 1, i <= 13 ? s.color = ["white", "green", "blue", "cyan", "red", "yellow", "magenta", "white"][Math.floor(i / 2)] : i <= 15 ? (s.italics = !0, s.color = "white") : s.indent = Math.floor((i - 16) / 2) * 4, s;
  }
  /**
   * Parse characters.
   * @returns An array with 1 to 2 codes corresponding to chars, if found. null otherwise.
   */
  parseChars(t, e) {
    let i, s = null, r = null;
    if (t >= 25 ? (i = 2, r = t - 8) : (i = 1, r = t), r >= 17 && r <= 19) {
      let a;
      r === 17 ? a = e + 80 : r === 18 ? a = e + 112 : a = e + 144, this.logger.log(2, () => "Special char '" + $o(a) + "' in channel " + i), s = [a];
    } else t >= 32 && t <= 127 && (s = e === 0 ? [t] : [t, e]);
    return s && this.logger.log(3, () => "Char codes =  " + be(s).join(",")), s;
  }
  /**
   * Parse extended background attributes as well as new foreground color black.
   * @returns True if background attributes are found
   */
  parseBackgroundAttributes(t, e) {
    const i = (t === 16 || t === 24) && e >= 32 && e <= 47, s = (t === 23 || t === 31) && e >= 45 && e <= 47;
    if (!(i || s))
      return !1;
    let r;
    const a = {};
    t === 16 || t === 24 ? (r = Math.floor((e - 32) / 2), a.background = ku[r], e % 2 === 1 && (a.background = a.background + "_semi")) : e === 45 ? a.background = "transparent" : (a.foreground = "black", e === 47 && (a.underline = !0));
    const o = t <= 23 ? 1 : 2;
    return this.channels[o].setBkgData(a), !0;
  }
  /**
   * Reset state of parser and its channels.
   */
  reset() {
    for (let t = 0; t < Object.keys(this.channels).length; t++) {
      const e = this.channels[t];
      e && e.reset();
    }
    Fi(null, null, this.cmdHistory);
  }
  /**
   * Trigger the generation of a cue, and the start of a new one if displayScreens are not empty.
   */
  cueSplitAtTime(t) {
    for (let e = 0; e < this.channels.length; e++) {
      const i = this.channels[e];
      i && i.cueSplitAtTime(t);
    }
  }
}
function Fi(n, t, e) {
  e.a = n, e.b = t;
}
function $u(n, t, e) {
  return e.a === n && e.b === t;
}
function Nu() {
  return {
    a: null,
    b: null
  };
}
var Br = (function() {
  if (rs != null && rs.VTTCue)
    return self.VTTCue;
  const n = ["", "lr", "rl"], t = ["start", "middle", "end", "left", "right"];
  function e(o, c) {
    if (typeof c != "string" || !Array.isArray(o))
      return !1;
    const l = c.toLowerCase();
    return ~o.indexOf(l) ? l : !1;
  }
  function i(o) {
    return e(n, o);
  }
  function s(o) {
    return e(t, o);
  }
  function r(o, ...c) {
    let l = 1;
    for (; l < arguments.length; l++) {
      const h = arguments[l];
      for (const d in h)
        o[d] = h[d];
    }
    return o;
  }
  function a(o, c, l) {
    const h = this, d = {
      enumerable: !0
    };
    h.hasBeenReset = !1;
    let u = "", f = !1, g = o, v = c, p = l, y = null, E = "", T = !0, S = "auto", x = "start", D = 50, A = "middle", _ = 50, R = "middle";
    Object.defineProperty(h, "id", r({}, d, {
      get: function() {
        return u;
      },
      set: function(b) {
        u = "" + b;
      }
    })), Object.defineProperty(h, "pauseOnExit", r({}, d, {
      get: function() {
        return f;
      },
      set: function(b) {
        f = !!b;
      }
    })), Object.defineProperty(h, "startTime", r({}, d, {
      get: function() {
        return g;
      },
      set: function(b) {
        if (typeof b != "number")
          throw new TypeError("Start time must be set to a number.");
        g = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "endTime", r({}, d, {
      get: function() {
        return v;
      },
      set: function(b) {
        if (typeof b != "number")
          throw new TypeError("End time must be set to a number.");
        v = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "text", r({}, d, {
      get: function() {
        return p;
      },
      set: function(b) {
        p = "" + b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "region", r({}, d, {
      get: function() {
        return y;
      },
      set: function(b) {
        y = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "vertical", r({}, d, {
      get: function() {
        return E;
      },
      set: function(b) {
        const C = i(b);
        if (C === !1)
          throw new SyntaxError("An invalid or illegal string was specified.");
        E = C, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "snapToLines", r({}, d, {
      get: function() {
        return T;
      },
      set: function(b) {
        T = !!b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "line", r({}, d, {
      get: function() {
        return S;
      },
      set: function(b) {
        if (typeof b != "number" && b !== "auto")
          throw new SyntaxError("An invalid number or illegal string was specified.");
        S = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "lineAlign", r({}, d, {
      get: function() {
        return x;
      },
      set: function(b) {
        const C = s(b);
        if (!C)
          throw new SyntaxError("An invalid or illegal string was specified.");
        x = C, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "position", r({}, d, {
      get: function() {
        return D;
      },
      set: function(b) {
        if (b < 0 || b > 100)
          throw new Error("Position must be between 0 and 100.");
        D = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "positionAlign", r({}, d, {
      get: function() {
        return A;
      },
      set: function(b) {
        const C = s(b);
        if (!C)
          throw new SyntaxError("An invalid or illegal string was specified.");
        A = C, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "size", r({}, d, {
      get: function() {
        return _;
      },
      set: function(b) {
        if (b < 0 || b > 100)
          throw new Error("Size must be between 0 and 100.");
        _ = b, this.hasBeenReset = !0;
      }
    })), Object.defineProperty(h, "align", r({}, d, {
      get: function() {
        return R;
      },
      set: function(b) {
        const C = s(b);
        if (!C)
          throw new SyntaxError("An invalid or illegal string was specified.");
        R = C, this.hasBeenReset = !0;
      }
    })), h.displayState = void 0;
  }
  return a.prototype.getCueAsHTML = function() {
    return self.WebVTT.convertCueToDOMTree(self, this.text);
  }, a;
})();
class Bu {
  decode(t, e) {
    if (!t)
      return "";
    if (typeof t != "string")
      throw new Error("Error - expected string data.");
    return decodeURIComponent(encodeURIComponent(t));
  }
}
function Bo(n) {
  function t(i, s, r, a) {
    return (i | 0) * 3600 + (s | 0) * 60 + (r | 0) + parseFloat(a || 0);
  }
  const e = n.match(/^(?:(\d+):)?(\d{2}):(\d{2})(\.\d+)?/);
  return e ? parseFloat(e[2]) > 59 ? t(e[2], e[3], 0, e[4]) : t(e[1], e[2], e[3], e[4]) : null;
}
class Uu {
  constructor() {
    this.values = /* @__PURE__ */ Object.create(null);
  }
  // Only accept the first assignment to any key.
  set(t, e) {
    !this.get(t) && e !== "" && (this.values[t] = e);
  }
  // Return the value for a key, or a default value.
  // If 'defaultKey' is passed then 'dflt' is assumed to be an object with
  // a number of possible default values as properties where 'defaultKey' is
  // the key of the property that will be chosen; otherwise it's assumed to be
  // a single value.
  get(t, e, i) {
    return i ? this.has(t) ? this.values[t] : e[i] : this.has(t) ? this.values[t] : e;
  }
  // Check whether we have a value for a key.
  has(t) {
    return t in this.values;
  }
  // Accept a setting if its one of the given alternatives.
  alt(t, e, i) {
    for (let s = 0; s < i.length; ++s)
      if (e === i[s]) {
        this.set(t, e);
        break;
      }
  }
  // Accept a setting if its a valid (signed) integer.
  integer(t, e) {
    /^-?\d+$/.test(e) && this.set(t, parseInt(e, 10));
  }
  // Accept a setting if its a valid percentage.
  percent(t, e) {
    if (/^([\d]{1,3})(\.[\d]*)?%$/.test(e)) {
      const i = parseFloat(e);
      if (i >= 0 && i <= 100)
        return this.set(t, i), !0;
    }
    return !1;
  }
}
function Uo(n, t, e, i) {
  const s = i ? n.split(i) : [n];
  for (const r in s) {
    if (typeof s[r] != "string")
      continue;
    const a = s[r].split(e);
    if (a.length !== 2)
      continue;
    const o = a[0], c = a[1];
    t(o, c);
  }
}
const dr = new Br(0, 0, ""), $i = dr.align === "middle" ? "middle" : "center";
function Gu(n, t, e) {
  const i = n;
  function s() {
    const o = Bo(n);
    if (o === null)
      throw new Error("Malformed timestamp: " + i);
    return n = n.replace(/^[^\sa-zA-Z-]+/, ""), o;
  }
  function r(o, c) {
    const l = new Uu();
    Uo(o, function(u, f) {
      let g;
      switch (u) {
        case "region":
          for (let v = e.length - 1; v >= 0; v--)
            if (e[v].id === f) {
              l.set(u, e[v].region);
              break;
            }
          break;
        case "vertical":
          l.alt(u, f, ["rl", "lr"]);
          break;
        case "line":
          g = f.split(","), l.integer(u, g[0]), l.percent(u, g[0]) && l.set("snapToLines", !1), l.alt(u, g[0], ["auto"]), g.length === 2 && l.alt("lineAlign", g[1], ["start", $i, "end"]);
          break;
        case "position":
          g = f.split(","), l.percent(u, g[0]), g.length === 2 && l.alt("positionAlign", g[1], ["start", $i, "end", "line-left", "line-right", "auto"]);
          break;
        case "size":
          l.percent(u, f);
          break;
        case "align":
          l.alt(u, f, ["start", $i, "end", "left", "right"]);
          break;
      }
    }, /:/, /\s/), c.region = l.get("region", null), c.vertical = l.get("vertical", "");
    let h = l.get("line", "auto");
    h === "auto" && dr.line === -1 && (h = -1), c.line = h, c.lineAlign = l.get("lineAlign", "start"), c.snapToLines = l.get("snapToLines", !0), c.size = l.get("size", 100), c.align = l.get("align", $i);
    let d = l.get("position", "auto");
    d === "auto" && dr.position === 50 && (d = c.align === "start" || c.align === "left" ? 0 : c.align === "end" || c.align === "right" ? 100 : 50), c.position = d;
  }
  function a() {
    n = n.replace(/^\s+/, "");
  }
  if (a(), t.startTime = s(), a(), n.slice(0, 3) !== "-->")
    throw new Error("Malformed time stamp (time stamps must be separated by '-->'): " + i);
  n = n.slice(3), a(), t.endTime = s(), a(), r(n, t);
}
function Go(n) {
  return n.replace(/<br(?: \/)?>/gi, `
`);
}
class Ku {
  constructor() {
    this.state = "INITIAL", this.buffer = "", this.decoder = new Bu(), this.regionList = [], this.cue = null, this.oncue = void 0, this.onparsingerror = void 0, this.onflush = void 0;
  }
  parse(t) {
    const e = this;
    t && (e.buffer += e.decoder.decode(t, {
      stream: !0
    }));
    function i() {
      let r = e.buffer, a = 0;
      for (r = Go(r); a < r.length && r[a] !== "\r" && r[a] !== `
`; )
        ++a;
      const o = r.slice(0, a);
      return r[a] === "\r" && ++a, r[a] === `
` && ++a, e.buffer = r.slice(a), o;
    }
    function s(r) {
      Uo(r, function(a, o) {
      }, /:/);
    }
    try {
      let r = "";
      if (e.state === "INITIAL") {
        if (!/\r\n|\n/.test(e.buffer))
          return this;
        r = i();
        const o = r.match(/^(ï»¿)?WEBVTT([ \t].*)?$/);
        if (!(o != null && o[0]))
          throw new Error("Malformed WebVTT signature.");
        e.state = "HEADER";
      }
      let a = !1;
      for (; e.buffer; ) {
        if (!/\r\n|\n/.test(e.buffer))
          return this;
        switch (a ? a = !1 : r = i(), e.state) {
          case "HEADER":
            /:/.test(r) ? s(r) : r || (e.state = "ID");
            continue;
          case "NOTE":
            r || (e.state = "ID");
            continue;
          case "ID":
            if (/^NOTE($|[ \t])/.test(r)) {
              e.state = "NOTE";
              break;
            }
            if (!r)
              continue;
            if (e.cue = new Br(0, 0, ""), e.state = "CUE", r.indexOf("-->") === -1) {
              e.cue.id = r;
              continue;
            }
          // Process line as start of a cue.
          /* falls through */
          case "CUE":
            if (!e.cue) {
              e.state = "BADCUE";
              continue;
            }
            try {
              Gu(r, e.cue, e.regionList);
            } catch {
              e.cue = null, e.state = "BADCUE";
              continue;
            }
            e.state = "CUETEXT";
            continue;
          case "CUETEXT":
            {
              const o = r.indexOf("-->") !== -1;
              if (!r || o && (a = !0)) {
                e.oncue && e.cue && e.oncue(e.cue), e.cue = null, e.state = "ID";
                continue;
              }
              if (e.cue === null)
                continue;
              e.cue.text && (e.cue.text += `
`), e.cue.text += r;
            }
            continue;
          case "BADCUE":
            r || (e.state = "ID");
        }
      }
    } catch {
      e.state === "CUETEXT" && e.cue && e.oncue && e.oncue(e.cue), e.cue = null, e.state = e.state === "INITIAL" ? "BADWEBVTT" : "BADCUE";
    }
    return this;
  }
  flush() {
    const t = this;
    try {
      if ((t.cue || t.state === "HEADER") && (t.buffer += `

`, t.parse()), t.state === "INITIAL" || t.state === "BADWEBVTT")
        throw new Error("Malformed WebVTT signature.");
    } catch (e) {
      t.onparsingerror && t.onparsingerror(e);
    }
    return t.onflush && t.onflush(), this;
  }
}
const Hu = /\r\n|\n\r|\n|\r/g, Fs = function(t, e, i = 0) {
  return t.slice(i, i + e.length) === e;
}, Vu = function(t) {
  let e = parseInt(t.slice(-3));
  const i = parseInt(t.slice(-6, -4)), s = parseInt(t.slice(-9, -7)), r = t.length > 9 ? parseInt(t.substring(0, t.indexOf(":"))) : 0;
  if (!B(e) || !B(i) || !B(s) || !B(r))
    throw Error(`Malformed X-TIMESTAMP-MAP: Local:${t}`);
  return e += 1e3 * i, e += 60 * 1e3 * s, e += 3600 * 1e3 * r, e;
};
function Ur(n, t, e) {
  return fi(n.toString()) + fi(t.toString()) + fi(e);
}
const Wu = function(t, e, i) {
  let s = t[e], r = t[s.prevCC];
  if (!r || !r.new && s.new) {
    t.ccOffset = t.presentationOffset = s.start, s.new = !1;
    return;
  }
  for (; (a = r) != null && a.new; ) {
    var a;
    t.ccOffset += s.start - r.start, s.new = !1, s = r, r = t[s.prevCC];
  }
  t.presentationOffset = i;
};
function Yu(n, t, e, i, s, r, a) {
  const o = new Ku(), c = Ft(new Uint8Array(n)).trim().replace(Hu, `
`).split(`
`), l = [], h = t ? Zh(t.baseTime, t.timescale) : 0;
  let d = "00:00.000", u = 0, f = 0, g, v = !0;
  o.oncue = function(p) {
    const y = e[i];
    let E = e.ccOffset;
    const T = (u - h) / 9e4;
    if (y != null && y.new && (f !== void 0 ? E = e.ccOffset = y.start : Wu(e, i, T)), T) {
      if (!t) {
        g = new Error("Missing initPTS for VTT MPEGTS");
        return;
      }
      E = T - e.presentationOffset;
    }
    const S = p.endTime - p.startTime, x = Ot((p.startTime + E - f) * 9e4, s * 9e4) / 9e4;
    p.startTime = Math.max(x, 0), p.endTime = Math.max(x + S, 0);
    const D = p.text.trim();
    p.text = decodeURIComponent(encodeURIComponent(D)), p.id || (p.id = Ur(p.startTime, p.endTime, D)), p.endTime > 0 && l.push(p);
  }, o.onparsingerror = function(p) {
    g = p;
  }, o.onflush = function() {
    if (g) {
      a(g);
      return;
    }
    r(l);
  }, c.forEach((p) => {
    if (v)
      if (Fs(p, "X-TIMESTAMP-MAP=")) {
        v = !1, p.slice(16).split(",").forEach((y) => {
          Fs(y, "LOCAL:") ? d = y.slice(6) : Fs(y, "MPEGTS:") && (u = parseInt(y.slice(7)));
        });
        try {
          f = Vu(d) / 1e3;
        } catch (y) {
          g = y;
        }
        return;
      } else p === "" && (v = !1);
    o.parse(p + `
`);
  }), o.flush();
}
const $s = "stpp.ttml.im1t", Ko = /^(\d{2,}):(\d{2}):(\d{2}):(\d{2})\.?(\d+)?$/, Ho = /^(\d*(?:\.\d*)?)(h|m|s|ms|f|t)$/, zu = {
  left: "start",
  center: "center",
  right: "end",
  start: "start",
  end: "end"
};
function ea(n, t, e, i) {
  const s = Z(new Uint8Array(n), ["mdat"]);
  if (s.length === 0) {
    i(new Error("Could not parse IMSC1 mdat"));
    return;
  }
  const r = s.map((o) => Ft(o)), a = Qh(t.baseTime, 1, t.timescale);
  try {
    r.forEach((o) => e(ju(o, a)));
  } catch (o) {
    i(o);
  }
}
function ju(n, t) {
  const s = new DOMParser().parseFromString(n, "text/xml").getElementsByTagName("tt")[0];
  if (!s)
    throw new Error("Invalid ttml");
  const r = {
    frameRate: 30,
    subFrameRate: 1,
    frameRateMultiplier: 0,
    tickRate: 0
  }, a = Object.keys(r).reduce((d, u) => (d[u] = s.getAttribute(`ttp:${u}`) || r[u], d), {}), o = s.getAttribute("xml:space") !== "preserve", c = ia(Ns(s, "styling", "style")), l = ia(Ns(s, "layout", "region")), h = Ns(s, "body", "[begin]");
  return [].map.call(h, (d) => {
    const u = Vo(d, o);
    if (!u || !d.hasAttribute("begin"))
      return null;
    const f = Us(d.getAttribute("begin"), a), g = Us(d.getAttribute("dur"), a);
    let v = Us(d.getAttribute("end"), a);
    if (f === null)
      throw sa(d);
    if (v === null) {
      if (g === null)
        throw sa(d);
      v = f + g;
    }
    const p = new Br(f - t, v - t, u);
    p.id = Ur(p.startTime, p.endTime, p.text);
    const y = l[d.getAttribute("region")], E = c[d.getAttribute("style")], T = qu(y, E, c), {
      textAlign: S
    } = T;
    if (S) {
      const x = zu[S];
      x && (p.lineAlign = x), p.align = S;
    }
    return nt(p, T), p;
  }).filter((d) => d !== null);
}
function Ns(n, t, e) {
  const i = n.getElementsByTagName(t)[0];
  return i ? [].slice.call(i.querySelectorAll(e)) : [];
}
function ia(n) {
  return n.reduce((t, e) => {
    const i = e.getAttribute("xml:id");
    return i && (t[i] = e), t;
  }, {});
}
function Vo(n, t) {
  return [].slice.call(n.childNodes).reduce((e, i, s) => {
    var r;
    return i.nodeName === "br" && s ? e + `
` : (r = i.childNodes) != null && r.length ? Vo(i, t) : t ? e + i.textContent.trim().replace(/\s+/g, " ") : e + i.textContent;
  }, "");
}
function qu(n, t, e) {
  const i = "http://www.w3.org/ns/ttml#styling";
  let s = null;
  const r = [
    "displayAlign",
    "textAlign",
    "color",
    "backgroundColor",
    "fontSize",
    "fontFamily"
    // 'fontWeight',
    // 'lineHeight',
    // 'wrapOption',
    // 'fontStyle',
    // 'direction',
    // 'writingMode'
  ], a = n != null && n.hasAttribute("style") ? n.getAttribute("style") : null;
  return a && e.hasOwnProperty(a) && (s = e[a]), r.reduce((o, c) => {
    const l = Bs(t, i, c) || Bs(n, i, c) || Bs(s, i, c);
    return l && (o[c] = l), o;
  }, {});
}
function Bs(n, t, e) {
  return n && n.hasAttributeNS(t, e) ? n.getAttributeNS(t, e) : null;
}
function sa(n) {
  return new Error(`Could not parse ttml timestamp ${n}`);
}
function Us(n, t) {
  if (!n)
    return null;
  let e = Bo(n);
  return e === null && (Ko.test(n) ? e = Xu(n, t) : Ho.test(n) && (e = Qu(n, t))), e;
}
function Xu(n, t) {
  const e = Ko.exec(n), i = (e[4] | 0) + (e[5] | 0) / t.subFrameRate;
  return (e[1] | 0) * 3600 + (e[2] | 0) * 60 + (e[3] | 0) + i / t.frameRate;
}
function Qu(n, t) {
  const e = Ho.exec(n), i = Number(e[1]);
  switch (e[2]) {
    case "h":
      return i * 3600;
    case "m":
      return i * 60;
    case "ms":
      return i * 1e3;
    case "f":
      return i / t.frameRate;
    case "t":
      return i / t.tickRate;
  }
  return i;
}
class Ni {
  constructor(t, e) {
    this.timelineController = void 0, this.cueRanges = [], this.trackName = void 0, this.startTime = null, this.endTime = null, this.screen = null, this.timelineController = t, this.trackName = e;
  }
  dispatchCue() {
    this.startTime !== null && (this.timelineController.addCues(this.trackName, this.startTime, this.endTime, this.screen, this.cueRanges), this.startTime = null);
  }
  newCue(t, e, i) {
    (this.startTime === null || this.startTime > t) && (this.startTime = t), this.endTime = e, this.screen = i, this.timelineController.createCaptionsTrack(this.trackName);
  }
  reset() {
    this.cueRanges = [], this.startTime = null;
  }
}
class Zu {
  constructor(t) {
    this.hls = void 0, this.media = null, this.config = void 0, this.enabled = !0, this.Cues = void 0, this.textTracks = [], this.tracks = [], this.initPTS = [], this.unparsedVttFrags = [], this.captionsTracks = {}, this.nonNativeCaptionsTracks = {}, this.cea608Parser1 = void 0, this.cea608Parser2 = void 0, this.lastCc = -1, this.lastSn = -1, this.lastPartIndex = -1, this.prevCC = -1, this.vttCCs = na(), this.captionsProperties = void 0, this.hls = t, this.config = t.config, this.Cues = t.config.cueHandler, this.captionsProperties = {
      textTrack1: {
        label: this.config.captionsTextTrack1Label,
        languageCode: this.config.captionsTextTrack1LanguageCode
      },
      textTrack2: {
        label: this.config.captionsTextTrack2Label,
        languageCode: this.config.captionsTextTrack2LanguageCode
      },
      textTrack3: {
        label: this.config.captionsTextTrack3Label,
        languageCode: this.config.captionsTextTrack3LanguageCode
      },
      textTrack4: {
        label: this.config.captionsTextTrack4Label,
        languageCode: this.config.captionsTextTrack4LanguageCode
      }
    }, t.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.on(m.SUBTITLE_TRACKS_UPDATED, this.onSubtitleTracksUpdated, this), t.on(m.FRAG_LOADING, this.onFragLoading, this), t.on(m.FRAG_LOADED, this.onFragLoaded, this), t.on(m.FRAG_PARSING_USERDATA, this.onFragParsingUserdata, this), t.on(m.FRAG_DECRYPTED, this.onFragDecrypted, this), t.on(m.INIT_PTS_FOUND, this.onInitPtsFound, this), t.on(m.SUBTITLE_TRACKS_CLEARED, this.onSubtitleTracksCleared, this), t.on(m.BUFFER_FLUSHING, this.onBufferFlushing, this);
  }
  destroy() {
    const {
      hls: t
    } = this;
    t.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.off(m.SUBTITLE_TRACKS_UPDATED, this.onSubtitleTracksUpdated, this), t.off(m.FRAG_LOADING, this.onFragLoading, this), t.off(m.FRAG_LOADED, this.onFragLoaded, this), t.off(m.FRAG_PARSING_USERDATA, this.onFragParsingUserdata, this), t.off(m.FRAG_DECRYPTED, this.onFragDecrypted, this), t.off(m.INIT_PTS_FOUND, this.onInitPtsFound, this), t.off(m.SUBTITLE_TRACKS_CLEARED, this.onSubtitleTracksCleared, this), t.off(m.BUFFER_FLUSHING, this.onBufferFlushing, this), this.hls = this.config = this.media = null, this.cea608Parser1 = this.cea608Parser2 = void 0;
  }
  initCea608Parsers() {
    const t = new Ni(this, "textTrack1"), e = new Ni(this, "textTrack2"), i = new Ni(this, "textTrack3"), s = new Ni(this, "textTrack4");
    this.cea608Parser1 = new ta(1, t, e), this.cea608Parser2 = new ta(3, i, s);
  }
  addCues(t, e, i, s, r) {
    let a = !1;
    for (let o = r.length; o--; ) {
      const c = r[o], l = Ju(c[0], c[1], e, i);
      if (l >= 0 && (c[0] = Math.min(c[0], e), c[1] = Math.max(c[1], i), a = !0, l / (i - e) > 0.5))
        return;
    }
    if (a || r.push([e, i]), this.config.renderTextTracksNatively) {
      const o = this.captionsTracks[t];
      this.Cues.newCue(o, e, i, s);
    } else {
      const o = this.Cues.newCue(null, e, i, s);
      this.hls.trigger(m.CUES_PARSED, {
        type: "captions",
        cues: o,
        track: t
      });
    }
  }
  // Triggered when an initial PTS is found; used for synchronisation of WebVTT.
  onInitPtsFound(t, {
    frag: e,
    id: i,
    initPTS: s,
    timescale: r,
    trackId: a
  }) {
    const {
      unparsedVttFrags: o
    } = this;
    i === K.MAIN && (this.initPTS[e.cc] = {
      baseTime: s,
      timescale: r,
      trackId: a
    }), o.length && (this.unparsedVttFrags = [], o.forEach((c) => {
      this.initPTS[c.frag.cc] ? this.onFragLoaded(m.FRAG_LOADED, c) : this.hls.trigger(m.SUBTITLE_FRAG_PROCESSED, {
        success: !1,
        frag: c.frag,
        error: new Error("Subtitle discontinuity domain does not match main")
      });
    }));
  }
  getExistingTrack(t, e) {
    const {
      media: i
    } = this;
    if (i)
      for (let s = 0; s < i.textTracks.length; s++) {
        const r = i.textTracks[s];
        if (ra(r, {
          name: t,
          lang: e,
          characteristics: "transcribes-spoken-dialog,describes-music-and-sound"
        }))
          return r;
      }
    return null;
  }
  createCaptionsTrack(t) {
    this.config.renderTextTracksNatively ? this.createNativeTrack(t) : this.createNonNativeTrack(t);
  }
  createNativeTrack(t) {
    if (this.captionsTracks[t])
      return;
    const {
      captionsProperties: e,
      captionsTracks: i,
      media: s
    } = this, {
      label: r,
      languageCode: a
    } = e[t], o = this.getExistingTrack(r, a);
    if (o)
      i[t] = o, Ve(i[t]), Oo(i[t], s);
    else {
      const c = this.createTextTrack("captions", r, a);
      c && (c[t] = !0, i[t] = c);
    }
  }
  createNonNativeTrack(t) {
    if (this.nonNativeCaptionsTracks[t])
      return;
    const e = this.captionsProperties[t];
    if (!e)
      return;
    const i = e.label, s = {
      _id: t,
      label: i,
      kind: "captions",
      default: e.media ? !!e.media.default : !1,
      closedCaptions: e.media
    };
    this.nonNativeCaptionsTracks[t] = s, this.hls.trigger(m.NON_NATIVE_TEXT_TRACKS_FOUND, {
      tracks: [s]
    });
  }
  createTextTrack(t, e, i) {
    const s = this.media;
    if (s)
      return s.addTextTrack(t, e, i);
  }
  onMediaAttaching(t, e) {
    this.media = e.media, e.mediaSource || this._cleanTracks();
  }
  onMediaDetaching(t, e) {
    const i = !!e.transferMedia;
    if (this.media = null, i)
      return;
    const {
      captionsTracks: s
    } = this;
    Object.keys(s).forEach((r) => {
      Ve(s[r]), delete s[r];
    }), this.nonNativeCaptionsTracks = {};
  }
  onManifestLoading() {
    this.lastCc = -1, this.lastSn = -1, this.lastPartIndex = -1, this.prevCC = -1, this.vttCCs = na(), this._cleanTracks(), this.tracks = [], this.captionsTracks = {}, this.nonNativeCaptionsTracks = {}, this.textTracks = [], this.unparsedVttFrags = [], this.initPTS = [], this.cea608Parser1 && this.cea608Parser2 && (this.cea608Parser1.reset(), this.cea608Parser2.reset());
  }
  _cleanTracks() {
    const {
      media: t
    } = this;
    if (!t)
      return;
    const e = t.textTracks;
    if (e)
      for (let i = 0; i < e.length; i++)
        Ve(e[i]);
  }
  onSubtitleTracksUpdated(t, e) {
    const i = e.subtitleTracks || [], s = i.some((r) => r.textCodec === $s);
    if (this.config.enableWebVTT || s && this.config.enableIMSC1) {
      if (So(this.tracks, i)) {
        this.tracks = i;
        return;
      }
      if (this.textTracks = [], this.tracks = i, this.config.renderTextTracksNatively) {
        const a = this.media, o = a ? zi(a.textTracks) : null;
        if (this.tracks.forEach((c, l) => {
          let h;
          if (o) {
            let d = null;
            for (let u = 0; u < o.length; u++)
              if (o[u] && ra(o[u], c)) {
                d = o[u], o[u] = null;
                break;
              }
            d && (h = d);
          }
          if (h)
            Ve(h);
          else {
            const d = Wo(c);
            h = this.createTextTrack(d, c.name, c.lang), h && (h.mode = "disabled");
          }
          h && this.textTracks.push(h);
        }), o != null && o.length) {
          const c = o.filter((l) => l !== null).map((l) => l.label);
          c.length && this.hls.logger.warn(`Media element contains unused subtitle tracks: ${c.join(", ")}. Replace media element for each source to clear TextTracks and captions menu.`);
        }
      } else if (this.tracks.length) {
        const a = this.tracks.map((o) => ({
          label: o.name,
          kind: o.type.toLowerCase(),
          default: o.default,
          subtitleTrack: o
        }));
        this.hls.trigger(m.NON_NATIVE_TEXT_TRACKS_FOUND, {
          tracks: a
        });
      }
    }
  }
  onManifestLoaded(t, e) {
    this.config.enableCEA708Captions && e.captions && e.captions.forEach((i) => {
      const s = /(?:CC|SERVICE)([1-4])/.exec(i.instreamId);
      if (!s)
        return;
      const r = `textTrack${s[1]}`, a = this.captionsProperties[r];
      a && (a.label = i.name, i.lang && (a.languageCode = i.lang), a.media = i);
    });
  }
  closedCaptionsForLevel(t) {
    const e = this.hls.levels[t.level];
    return e == null ? void 0 : e.attrs["CLOSED-CAPTIONS"];
  }
  onFragLoading(t, e) {
    if (this.enabled && e.frag.type === K.MAIN) {
      var i, s;
      const {
        cea608Parser1: r,
        cea608Parser2: a,
        lastSn: o
      } = this, {
        cc: c,
        sn: l
      } = e.frag, h = (i = (s = e.part) == null ? void 0 : s.index) != null ? i : -1;
      r && a && (l !== o + 1 || l === o && h !== this.lastPartIndex + 1 || c !== this.lastCc) && (r.reset(), a.reset()), this.lastCc = c, this.lastSn = l, this.lastPartIndex = h;
    }
  }
  onFragLoaded(t, e) {
    const {
      frag: i,
      payload: s
    } = e;
    if (i.type === K.SUBTITLE)
      if (s.byteLength) {
        const r = i.decryptdata, a = "stats" in e;
        if (r == null || !r.encrypted || a) {
          const o = this.tracks[i.level], c = this.vttCCs;
          c[i.cc] || (c[i.cc] = {
            start: i.start,
            prevCC: this.prevCC,
            new: !0
          }, this.prevCC = i.cc), o && o.textCodec === $s ? this._parseIMSC1(i, s) : this._parseVTTs(e);
        }
      } else
        this.hls.trigger(m.SUBTITLE_FRAG_PROCESSED, {
          success: !1,
          frag: i,
          error: new Error("Empty subtitle payload")
        });
  }
  _parseIMSC1(t, e) {
    const i = this.hls;
    ea(e, this.initPTS[t.cc], (s) => {
      this._appendCues(s, t.level), i.trigger(m.SUBTITLE_FRAG_PROCESSED, {
        success: !0,
        frag: t
      });
    }, (s) => {
      i.logger.log(`Failed to parse IMSC1: ${s}`), i.trigger(m.SUBTITLE_FRAG_PROCESSED, {
        success: !1,
        frag: t,
        error: s
      });
    });
  }
  _parseVTTs(t) {
    var e;
    const {
      frag: i,
      payload: s
    } = t, {
      initPTS: r,
      unparsedVttFrags: a
    } = this, o = r.length - 1;
    if (!r[i.cc] && o === -1) {
      a.push(t);
      return;
    }
    const c = this.hls, l = (e = i.initSegment) != null && e.data ? Nt(i.initSegment.data, new Uint8Array(s)).buffer : s;
    Yu(l, this.initPTS[i.cc], this.vttCCs, i.cc, i.start, (h) => {
      this._appendCues(h, i.level), c.trigger(m.SUBTITLE_FRAG_PROCESSED, {
        success: !0,
        frag: i
      });
    }, (h) => {
      const d = h.message === "Missing initPTS for VTT MPEGTS";
      d ? a.push(t) : this._fallbackToIMSC1(i, s), c.logger.log(`Failed to parse VTT cue: ${h}`), !(d && o > i.cc) && c.trigger(m.SUBTITLE_FRAG_PROCESSED, {
        success: !1,
        frag: i,
        error: h
      });
    });
  }
  _fallbackToIMSC1(t, e) {
    const i = this.tracks[t.level];
    i.textCodec || ea(e, this.initPTS[t.cc], () => {
      i.textCodec = $s, this._parseIMSC1(t, e);
    }, () => {
      i.textCodec = "wvtt";
    });
  }
  _appendCues(t, e) {
    const i = this.hls;
    if (this.config.renderTextTracksNatively) {
      const s = this.textTracks[e];
      if (!s || s.mode === "disabled")
        return;
      t.forEach((r) => Mo(s, r));
    } else {
      const s = this.tracks[e];
      if (!s)
        return;
      const r = s.default ? "default" : "subtitles" + e;
      i.trigger(m.CUES_PARSED, {
        type: "subtitles",
        cues: t,
        track: r
      });
    }
  }
  onFragDecrypted(t, e) {
    const {
      frag: i
    } = e;
    i.type === K.SUBTITLE && this.onFragLoaded(m.FRAG_LOADED, e);
  }
  onSubtitleTracksCleared() {
    this.tracks = [], this.captionsTracks = {};
  }
  onFragParsingUserdata(t, e) {
    if (!this.enabled || !this.config.enableCEA708Captions)
      return;
    const {
      frag: i,
      samples: s
    } = e;
    if (!(i.type === K.MAIN && this.closedCaptionsForLevel(i) === "NONE"))
      for (let r = 0; r < s.length; r++) {
        const a = s[r].bytes;
        if (a) {
          this.cea608Parser1 || this.initCea608Parsers();
          const o = this.extractCea608Data(a);
          this.cea608Parser1.addData(s[r].pts, o[0]), this.cea608Parser2.addData(s[r].pts, o[1]);
        }
      }
  }
  onBufferFlushing(t, {
    startOffset: e,
    endOffset: i,
    endOffsetSubtitles: s,
    type: r
  }) {
    const {
      media: a
    } = this;
    if (!(!a || a.currentTime < i)) {
      if (!r || r === "video") {
        const {
          captionsTracks: o
        } = this;
        Object.keys(o).forEach((c) => hr(o[c], e, i));
      }
      if (this.config.renderTextTracksNatively && e === 0 && s !== void 0) {
        const {
          textTracks: o
        } = this;
        Object.keys(o).forEach((c) => hr(o[c], e, s));
      }
    }
  }
  extractCea608Data(t) {
    const e = [[], []], i = t[0] & 31;
    let s = 2;
    for (let r = 0; r < i; r++) {
      const a = t[s++], o = 127 & t[s++], c = 127 & t[s++];
      if (o === 0 && c === 0)
        continue;
      if ((4 & a) !== 0) {
        const h = 3 & a;
        (h === 0 || h === 1) && (e[h].push(o), e[h].push(c));
      }
    }
    return e;
  }
}
function Wo(n) {
  return n.characteristics && /transcribes-spoken-dialog/gi.test(n.characteristics) && /describes-music-and-sound/gi.test(n.characteristics) ? "captions" : "subtitles";
}
function ra(n, t) {
  return !!n && n.kind === Wo(t) && ar(t, n);
}
function Ju(n, t, e, i) {
  return Math.min(t, i) - Math.max(n, e);
}
function na() {
  return {
    ccOffset: 0,
    presentationOffset: 0,
    0: {
      start: 0,
      prevCC: -1,
      new: !0
    }
  };
}
const tf = /\s/, ef = {
  newCue(n, t, e, i) {
    const s = [];
    let r, a, o, c, l;
    const h = self.VTTCue || self.TextTrackCue;
    for (let u = 0; u < i.rows.length; u++)
      if (r = i.rows[u], o = !0, c = 0, l = "", !r.isEmpty()) {
        var d;
        for (let v = 0; v < r.chars.length; v++)
          tf.test(r.chars[v].uchar) && o ? c++ : (l += r.chars[v].uchar, o = !1);
        r.cueStartTime = t, t === e && (e += 1e-4), c >= 16 ? c-- : c++;
        const f = Go(l.trim()), g = Ur(t, e, f);
        n != null && (d = n.cues) != null && d.getCueById(g) || (a = new h(t, e, f), a.id = g, a.line = u + 1, a.align = "left", a.position = 10 + Math.min(80, Math.floor(c * 8 / 32) * 10), s.push(a));
      }
    return n && s.length && (s.sort((u, f) => u.line === "auto" || f.line === "auto" ? 0 : u.line > 8 && f.line > 8 ? f.line - u.line : u.line - f.line), s.forEach((u) => Mo(n, u))), s;
  }
};
function sf() {
  if (
    // @ts-ignore
    self.fetch && self.AbortController && self.ReadableStream && self.Request
  )
    try {
      return new self.ReadableStream({}), !0;
    } catch {
    }
  return !1;
}
const rf = /(\d+)-(\d+)\/(\d+)/;
class aa {
  constructor(t) {
    this.fetchSetup = void 0, this.requestTimeout = void 0, this.request = null, this.response = null, this.controller = void 0, this.context = null, this.config = null, this.callbacks = null, this.stats = void 0, this.loader = null, this.fetchSetup = t.fetchSetup || lf, this.controller = new self.AbortController(), this.stats = new yr();
  }
  destroy() {
    this.loader = this.callbacks = this.context = this.config = this.request = null, this.abortInternal(), this.response = null, this.fetchSetup = this.controller = this.stats = null;
  }
  abortInternal() {
    this.controller && !this.stats.loading.end && (this.stats.aborted = !0, this.controller.abort());
  }
  abort() {
    var t;
    this.abortInternal(), (t = this.callbacks) != null && t.onAbort && this.callbacks.onAbort(this.stats, this.context, this.response);
  }
  load(t, e, i) {
    const s = this.stats;
    if (s.loading.start)
      throw new Error("Loader can only be used once.");
    s.loading.start = self.performance.now();
    const r = nf(t, this.controller.signal), a = t.responseType === "arraybuffer", o = a ? "byteLength" : "length", {
      maxTimeToFirstByteMs: c,
      maxLoadTimeMs: l
    } = e.loadPolicy;
    this.context = t, this.config = e, this.callbacks = i, this.request = this.fetchSetup(t, r), self.clearTimeout(this.requestTimeout), e.timeout = c && B(c) ? c : l, this.requestTimeout = self.setTimeout(() => {
      this.callbacks && (this.abortInternal(), this.callbacks.onTimeout(s, t, this.response));
    }, e.timeout), (Ei(this.request) ? this.request.then(self.fetch) : self.fetch(this.request)).then((d) => {
      var u;
      this.response = this.loader = d;
      const f = Math.max(self.performance.now(), s.loading.start);
      if (self.clearTimeout(this.requestTimeout), e.timeout = l, this.requestTimeout = self.setTimeout(() => {
        this.callbacks && (this.abortInternal(), this.callbacks.onTimeout(s, t, this.response));
      }, l - (f - s.loading.start)), !d.ok) {
        const {
          status: v,
          statusText: p
        } = d;
        throw new cf(p || "fetch, bad network response", v, d);
      }
      s.loading.first = f, s.total = of(d.headers) || s.total;
      const g = (u = this.callbacks) == null ? void 0 : u.onProgress;
      return g && B(e.highWaterMark) ? this.loadProgressively(d, s, t, e.highWaterMark, g) : a ? d.arrayBuffer() : t.responseType === "json" ? d.json() : d.text();
    }).then((d) => {
      var u, f;
      const g = this.response;
      if (!g)
        throw new Error("loader destroyed");
      self.clearTimeout(this.requestTimeout), s.loading.end = Math.max(self.performance.now(), s.loading.first);
      const v = d[o];
      v && (s.loaded = s.total = v);
      const p = {
        url: g.url,
        data: d,
        code: g.status
      }, y = (u = this.callbacks) == null ? void 0 : u.onProgress;
      y && !B(e.highWaterMark) && y(s, t, d, g), (f = this.callbacks) == null || f.onSuccess(p, s, t, g);
    }).catch((d) => {
      var u;
      if (self.clearTimeout(this.requestTimeout), s.aborted)
        return;
      const f = d && d.code || 0, g = d ? d.message : null;
      (u = this.callbacks) == null || u.onError({
        code: f,
        text: g
      }, t, d ? d.details : null, s);
    });
  }
  getCacheAge() {
    let t = null;
    if (this.response) {
      const e = this.response.headers.get("age");
      t = e ? parseFloat(e) : null;
    }
    return t;
  }
  getResponseHeader(t) {
    return this.response ? this.response.headers.get(t) : null;
  }
  loadProgressively(t, e, i, s = 0, r) {
    const a = new to(), o = t.body.getReader(), c = () => o.read().then((l) => {
      if (l.done)
        return a.dataLength && r(e, i, a.flush().buffer, t), Promise.resolve(new ArrayBuffer(0));
      const h = l.value, d = h.length;
      return e.loaded += d, d < s || a.dataLength ? (a.push(h), a.dataLength >= s && r(e, i, a.flush().buffer, t)) : r(e, i, h.buffer, t), c();
    }).catch(() => Promise.reject());
    return c();
  }
}
function nf(n, t) {
  const e = {
    method: "GET",
    mode: "cors",
    credentials: "same-origin",
    signal: t,
    headers: new self.Headers(nt({}, n.headers))
  };
  return n.rangeEnd && e.headers.set("Range", "bytes=" + n.rangeStart + "-" + String(n.rangeEnd - 1)), e;
}
function af(n) {
  const t = rf.exec(n);
  if (t)
    return parseInt(t[2]) - parseInt(t[1]) + 1;
}
function of(n) {
  const t = n.get("Content-Range");
  if (t) {
    const i = af(t);
    if (B(i))
      return i;
  }
  const e = n.get("Content-Length");
  if (e)
    return parseInt(e);
}
function lf(n, t) {
  return new self.Request(n.url, t);
}
class cf extends Error {
  constructor(t, e, i) {
    super(t), this.code = void 0, this.details = void 0, this.code = e, this.details = i;
  }
}
const hf = /^age:\s*[\d.]+\s*$/im;
class Yo {
  constructor(t) {
    this.xhrSetup = void 0, this.requestTimeout = void 0, this.retryTimeout = void 0, this.retryDelay = void 0, this.config = null, this.callbacks = null, this.context = null, this.loader = null, this.stats = void 0, this.xhrSetup = t && t.xhrSetup || null, this.stats = new yr(), this.retryDelay = 0;
  }
  destroy() {
    this.callbacks = null, this.abortInternal(), this.loader = null, this.config = null, this.context = null, this.xhrSetup = null;
  }
  abortInternal() {
    const t = this.loader;
    self.clearTimeout(this.requestTimeout), self.clearTimeout(this.retryTimeout), t && (t.onreadystatechange = null, t.onprogress = null, t.readyState !== 4 && (this.stats.aborted = !0, t.abort()));
  }
  abort() {
    var t;
    this.abortInternal(), (t = this.callbacks) != null && t.onAbort && this.callbacks.onAbort(this.stats, this.context, this.loader);
  }
  load(t, e, i) {
    if (this.stats.loading.start)
      throw new Error("Loader can only be used once.");
    this.stats.loading.start = self.performance.now(), this.context = t, this.config = e, this.callbacks = i, this.loadInternal();
  }
  loadInternal() {
    const {
      config: t,
      context: e
    } = this;
    if (!t || !e)
      return;
    const i = this.loader = new self.XMLHttpRequest(), s = this.stats;
    s.loading.first = 0, s.loaded = 0, s.aborted = !1;
    const r = this.xhrSetup;
    r ? Promise.resolve().then(() => {
      if (!(this.loader !== i || this.stats.aborted))
        return r(i, e.url);
    }).catch((a) => {
      if (!(this.loader !== i || this.stats.aborted))
        return i.open("GET", e.url, !0), r(i, e.url);
    }).then(() => {
      this.loader !== i || this.stats.aborted || this.openAndSendXhr(i, e, t);
    }).catch((a) => {
      var o;
      (o = this.callbacks) == null || o.onError({
        code: i.status,
        text: a.message
      }, e, i, s);
    }) : this.openAndSendXhr(i, e, t);
  }
  openAndSendXhr(t, e, i) {
    t.readyState || t.open("GET", e.url, !0);
    const s = e.headers, {
      maxTimeToFirstByteMs: r,
      maxLoadTimeMs: a
    } = i.loadPolicy;
    if (s)
      for (const o in s)
        t.setRequestHeader(o, s[o]);
    e.rangeEnd && t.setRequestHeader("Range", "bytes=" + e.rangeStart + "-" + (e.rangeEnd - 1)), t.onreadystatechange = this.readystatechange.bind(this), t.onprogress = this.loadprogress.bind(this), t.responseType = e.responseType, self.clearTimeout(this.requestTimeout), i.timeout = r && B(r) ? r : a, this.requestTimeout = self.setTimeout(this.loadtimeout.bind(this), i.timeout), t.send();
  }
  readystatechange() {
    const {
      context: t,
      loader: e,
      stats: i
    } = this;
    if (!t || !e)
      return;
    const s = e.readyState, r = this.config;
    if (!i.aborted && s >= 2 && (i.loading.first === 0 && (i.loading.first = Math.max(self.performance.now(), i.loading.start), r.timeout !== r.loadPolicy.maxLoadTimeMs && (self.clearTimeout(this.requestTimeout), r.timeout = r.loadPolicy.maxLoadTimeMs, this.requestTimeout = self.setTimeout(this.loadtimeout.bind(this), r.loadPolicy.maxLoadTimeMs - (i.loading.first - i.loading.start)))), s === 4)) {
      self.clearTimeout(this.requestTimeout), e.onreadystatechange = null, e.onprogress = null;
      const l = e.status, h = e.responseType === "text" ? e.responseText : null;
      if (l >= 200 && l < 300) {
        const g = h ?? e.response;
        if (g != null) {
          var a, o;
          i.loading.end = Math.max(self.performance.now(), i.loading.first);
          const v = e.responseType === "arraybuffer" ? g.byteLength : g.length;
          i.loaded = i.total = v, i.bwEstimate = i.total * 8e3 / (i.loading.end - i.loading.first);
          const p = (a = this.callbacks) == null ? void 0 : a.onProgress;
          p && p(i, t, g, e);
          const y = {
            url: e.responseURL,
            data: g,
            code: l
          };
          (o = this.callbacks) == null || o.onSuccess(y, i, t, e);
          return;
        }
      }
      const d = r.loadPolicy.errorRetry, u = i.retry, f = {
        url: t.url,
        data: void 0,
        code: l
      };
      if (is(d, u, !1, f))
        this.retry(d);
      else {
        var c;
        rt.error(`${l} while loading ${t.url}`), (c = this.callbacks) == null || c.onError({
          code: l,
          text: e.statusText
        }, t, e, i);
      }
    }
  }
  loadtimeout() {
    if (!this.config) return;
    const t = this.config.loadPolicy.timeoutRetry, e = this.stats.retry;
    if (is(t, e, !0))
      this.retry(t);
    else {
      var i;
      rt.warn(`timeout while loading ${(i = this.context) == null ? void 0 : i.url}`);
      const s = this.callbacks;
      s && (this.abortInternal(), s.onTimeout(this.stats, this.context, this.loader));
    }
  }
  retry(t) {
    const {
      context: e,
      stats: i
    } = this;
    this.retryDelay = xr(t, i.retry), i.retry++, rt.warn(`${status ? "HTTP Status " + status : "Timeout"} while loading ${e == null ? void 0 : e.url}, retrying ${i.retry}/${t.maxNumRetry} in ${this.retryDelay}ms`), this.abortInternal(), this.loader = null, self.clearTimeout(this.retryTimeout), this.retryTimeout = self.setTimeout(this.loadInternal.bind(this), this.retryDelay);
  }
  loadprogress(t) {
    const e = this.stats;
    e.loaded = t.loaded, t.lengthComputable && (e.total = t.total);
  }
  getCacheAge() {
    let t = null;
    if (this.loader && hf.test(this.loader.getAllResponseHeaders())) {
      const e = this.loader.getResponseHeader("age");
      t = e ? parseFloat(e) : null;
    }
    return t;
  }
  getResponseHeader(t) {
    return this.loader && new RegExp(`^${t}:\\s*[\\d.]+\\s*$`, "im").test(this.loader.getAllResponseHeaders()) ? this.loader.getResponseHeader(t) : null;
  }
}
const df = {
  maxTimeToFirstByteMs: 8e3,
  maxLoadTimeMs: 2e4,
  timeoutRetry: null,
  errorRetry: null
}, uf = st(st({
  autoStartLoad: !0,
  // used by stream-controller
  startPosition: -1,
  // used by stream-controller
  defaultAudioCodec: void 0,
  // used by stream-controller
  debug: !1,
  // used by logger
  capLevelOnFPSDrop: !1,
  // used by fps-controller
  capLevelToPlayerSize: !1,
  // used by cap-level-controller
  ignoreDevicePixelRatio: !1,
  // used by cap-level-controller
  maxDevicePixelRatio: Number.POSITIVE_INFINITY,
  // used by cap-level-controller
  preferManagedMediaSource: !0,
  initialLiveManifestSize: 1,
  // used by stream-controller
  maxBufferLength: 30,
  // used by stream-controller
  backBufferLength: 1 / 0,
  // used by buffer-controller
  frontBufferFlushThreshold: 1 / 0,
  startOnSegmentBoundary: !1,
  // used by stream-controller
  maxBufferSize: 60 * 1e3 * 1e3,
  // used by stream-controller
  maxFragLookUpTolerance: 0.25,
  // used by stream-controller
  maxBufferHole: 0.1,
  // used by stream-controller and gap-controller
  detectStallWithCurrentTimeMs: 1250,
  // used by gap-controller
  highBufferWatchdogPeriod: 2,
  // used by gap-controller
  nudgeOffset: 0.1,
  // used by gap-controller
  nudgeMaxRetry: 3,
  // used by gap-controller
  nudgeOnVideoHole: !0,
  // used by gap-controller
  liveSyncMode: "edge",
  // used by stream-controller
  liveSyncDurationCount: 3,
  // used by latency-controller
  liveSyncOnStallIncrease: 1,
  // used by latency-controller
  liveMaxLatencyDurationCount: 1 / 0,
  // used by latency-controller
  liveSyncDuration: void 0,
  // used by latency-controller
  liveMaxLatencyDuration: void 0,
  // used by latency-controller
  maxLiveSyncPlaybackRate: 1,
  // used by latency-controller
  liveDurationInfinity: !1,
  // used by buffer-controller
  /**
   * @deprecated use backBufferLength
   */
  liveBackBufferLength: null,
  // used by buffer-controller
  maxMaxBufferLength: 600,
  // used by stream-controller
  enableWorker: !0,
  // used by transmuxer
  workerPath: null,
  // used by transmuxer
  enableSoftwareAES: !0,
  // used by decrypter
  startLevel: void 0,
  // used by level-controller
  startFragPrefetch: !1,
  // used by stream-controller
  fpsDroppedMonitoringPeriod: 5e3,
  // used by fps-controller
  fpsDroppedMonitoringThreshold: 0.2,
  // used by fps-controller
  appendErrorMaxRetry: 3,
  // used by buffer-controller
  ignorePlaylistParsingErrors: !1,
  loader: Yo,
  // loader: FetchLoader,
  fLoader: void 0,
  // used by fragment-loader
  pLoader: void 0,
  // used by playlist-loader
  xhrSetup: void 0,
  // used by xhr-loader
  licenseXhrSetup: void 0,
  // used by eme-controller
  licenseResponseCallback: void 0,
  // used by eme-controller
  abrController: Ac,
  bufferController: fd,
  capLevelController: Fr,
  errorController: _c,
  fpsController: gu,
  stretchShortVideoTrack: !1,
  // used by mp4-remuxer
  maxAudioFramesDrift: 1,
  // used by mp4-remuxer
  forceKeyFrameOnDiscontinuity: !0,
  // used by ts-demuxer
  abrEwmaFastLive: 3,
  // used by abr-controller
  abrEwmaSlowLive: 9,
  // used by abr-controller
  abrEwmaFastVoD: 3,
  // used by abr-controller
  abrEwmaSlowVoD: 9,
  // used by abr-controller
  abrEwmaDefaultEstimate: 5e5,
  // 500 kbps  // used by abr-controller
  abrEwmaDefaultEstimateMax: 5e6,
  // 5 mbps
  abrBandWidthFactor: 0.95,
  // used by abr-controller
  abrBandWidthUpFactor: 0.7,
  // used by abr-controller
  abrMaxWithRealBitrate: !1,
  // used by abr-controller
  maxStarvationDelay: 4,
  // used by abr-controller
  maxLoadingDelay: 4,
  // used by abr-controller
  minAutoBitrate: 0,
  // used by hls
  emeEnabled: !1,
  // used by eme-controller
  widevineLicenseUrl: void 0,
  // used by eme-controller
  drmSystems: {},
  // used by eme-controller
  drmSystemOptions: {},
  // used by eme-controller
  requestMediaKeySystemAccessFunc: Ha,
  // used by eme-controller
  requireKeySystemAccessOnStart: !1,
  // used by eme-controller
  testBandwidth: !0,
  progressive: !1,
  lowLatencyMode: !0,
  cmcd: void 0,
  enableDateRangeMetadataCues: !0,
  enableEmsgMetadataCues: !0,
  enableEmsgKLVMetadata: !1,
  enableID3MetadataCues: !0,
  enableInterstitialPlayback: !0,
  interstitialAppendInPlace: !0,
  interstitialLiveLookAhead: 10,
  useMediaCapabilities: !0,
  preserveManualLevelOnError: !1,
  certLoadPolicy: {
    default: df
  },
  keyLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 8e3,
      maxLoadTimeMs: 2e4,
      timeoutRetry: {
        maxNumRetry: 1,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 2e4,
        backoff: "linear"
      },
      errorRetry: {
        maxNumRetry: 8,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 2e4,
        backoff: "linear"
      }
    }
  },
  manifestLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 1 / 0,
      maxLoadTimeMs: 2e4,
      timeoutRetry: {
        maxNumRetry: 2,
        retryDelayMs: 0,
        maxRetryDelayMs: 0
      },
      errorRetry: {
        maxNumRetry: 1,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 8e3
      }
    }
  },
  playlistLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 1e4,
      maxLoadTimeMs: 2e4,
      timeoutRetry: {
        maxNumRetry: 2,
        retryDelayMs: 0,
        maxRetryDelayMs: 0
      },
      errorRetry: {
        maxNumRetry: 2,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 8e3
      }
    }
  },
  fragLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 1e4,
      maxLoadTimeMs: 12e4,
      timeoutRetry: {
        maxNumRetry: 4,
        retryDelayMs: 0,
        maxRetryDelayMs: 0
      },
      errorRetry: {
        maxNumRetry: 6,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 8e3
      }
    }
  },
  steeringManifestLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 1e4,
      maxLoadTimeMs: 2e4,
      timeoutRetry: {
        maxNumRetry: 2,
        retryDelayMs: 0,
        maxRetryDelayMs: 0
      },
      errorRetry: {
        maxNumRetry: 1,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 8e3
      }
    }
  },
  interstitialAssetListLoadPolicy: {
    default: {
      maxTimeToFirstByteMs: 1e4,
      maxLoadTimeMs: 3e4,
      timeoutRetry: {
        maxNumRetry: 0,
        retryDelayMs: 0,
        maxRetryDelayMs: 0
      },
      errorRetry: {
        maxNumRetry: 0,
        retryDelayMs: 1e3,
        maxRetryDelayMs: 8e3
      }
    }
  },
  // These default settings are deprecated in favor of the above policies
  // and are maintained for backwards compatibility
  manifestLoadingTimeOut: 1e4,
  manifestLoadingMaxRetry: 1,
  manifestLoadingRetryDelay: 1e3,
  manifestLoadingMaxRetryTimeout: 64e3,
  levelLoadingTimeOut: 1e4,
  levelLoadingMaxRetry: 4,
  levelLoadingRetryDelay: 1e3,
  levelLoadingMaxRetryTimeout: 64e3,
  fragLoadingTimeOut: 2e4,
  fragLoadingMaxRetry: 6,
  fragLoadingRetryDelay: 1e3,
  fragLoadingMaxRetryTimeout: 64e3
}, ff()), {}, {
  subtitleStreamController: Lu,
  subtitleTrackController: vu,
  timelineController: Zu,
  audioStreamController: cd,
  audioTrackController: hd,
  emeController: ze,
  cmcdController: hu,
  contentSteeringController: uu,
  interstitialsController: Iu
});
function ff() {
  return {
    cueHandler: ef,
    // used by timeline-controller
    enableWebVTT: !0,
    // used by timeline-controller
    enableIMSC1: !0,
    // used by timeline-controller
    enableCEA708Captions: !0,
    // used by timeline-controller
    captionsTextTrack1Label: "English",
    // used by timeline-controller
    captionsTextTrack1LanguageCode: "en",
    // used by timeline-controller
    captionsTextTrack2Label: "Spanish",
    // used by timeline-controller
    captionsTextTrack2LanguageCode: "es",
    // used by timeline-controller
    captionsTextTrack3Label: "Unknown CC",
    // used by timeline-controller
    captionsTextTrack3LanguageCode: "",
    // used by timeline-controller
    captionsTextTrack4Label: "Unknown CC",
    // used by timeline-controller
    captionsTextTrack4LanguageCode: "",
    // used by timeline-controller
    renderTextTracksNatively: !0
  };
}
function gf(n, t, e) {
  if ((t.liveSyncDurationCount || t.liveMaxLatencyDurationCount) && (t.liveSyncDuration || t.liveMaxLatencyDuration))
    throw new Error("Illegal hls.js config: don't mix up liveSyncDurationCount/liveMaxLatencyDurationCount and liveSyncDuration/liveMaxLatencyDuration");
  if (t.liveMaxLatencyDurationCount !== void 0 && (t.liveSyncDurationCount === void 0 || t.liveMaxLatencyDurationCount <= t.liveSyncDurationCount))
    throw new Error('Illegal hls.js config: "liveMaxLatencyDurationCount" must be greater than "liveSyncDurationCount"');
  if (t.liveMaxLatencyDuration !== void 0 && (t.liveSyncDuration === void 0 || t.liveMaxLatencyDuration <= t.liveSyncDuration))
    throw new Error('Illegal hls.js config: "liveMaxLatencyDuration" must be greater than "liveSyncDuration"');
  const i = ur(n), s = ["manifest", "level", "frag"], r = ["TimeOut", "MaxRetry", "RetryDelay", "MaxRetryTimeout"];
  return s.forEach((a) => {
    const o = `${a === "level" ? "playlist" : a}LoadPolicy`, c = t[o] === void 0, l = [];
    r.forEach((h) => {
      const d = `${a}Loading${h}`, u = t[d];
      if (u !== void 0 && c) {
        l.push(d);
        const f = i[o].default;
        switch (t[o] = {
          default: f
        }, h) {
          case "TimeOut":
            f.maxLoadTimeMs = u, f.maxTimeToFirstByteMs = u;
            break;
          case "MaxRetry":
            f.errorRetry.maxNumRetry = u, f.timeoutRetry.maxNumRetry = u;
            break;
          case "RetryDelay":
            f.errorRetry.retryDelayMs = u, f.timeoutRetry.retryDelayMs = u;
            break;
          case "MaxRetryTimeout":
            f.errorRetry.maxRetryDelayMs = u, f.timeoutRetry.maxRetryDelayMs = u;
            break;
        }
      }
    }), l.length && e.warn(`hls.js config: "${l.join('", "')}" setting(s) are deprecated, use "${o}": ${ot(t[o])}`);
  }), st(st({}, i), t);
}
function ur(n) {
  return n && typeof n == "object" ? Array.isArray(n) ? n.map(ur) : Object.keys(n).reduce((t, e) => (t[e] = ur(n[e]), t), {}) : n;
}
function mf(n, t) {
  const e = n.loader;
  e !== aa && e !== Yo ? (t.log("[config]: Custom loader detected, cannot enable progressive streaming"), n.progressive = !1) : sf() && (n.loader = aa, n.progressive = !0, n.enableSoftwareAES = !0, t.log("[config]: Progressive streaming enabled, using FetchLoader"));
}
const ji = 2, pf = 0.1, vf = 0.05, yf = 100;
class Ef extends Na {
  constructor(t, e) {
    super("gap-controller", t.logger), this.hls = void 0, this.fragmentTracker = void 0, this.media = null, this.mediaSource = void 0, this.nudgeRetry = 0, this.stallReported = !1, this.stalled = null, this.moved = !1, this.seeking = !1, this.buffered = {}, this.lastCurrentTime = 0, this.ended = 0, this.waiting = 0, this.onMediaPlaying = () => {
      this.ended = 0, this.waiting = 0;
    }, this.onMediaWaiting = () => {
      var i;
      (i = this.media) != null && i.seeking || (this.waiting = self.performance.now(), this.tick());
    }, this.onMediaEnded = () => {
      if (this.hls) {
        var i;
        this.ended = ((i = this.media) == null ? void 0 : i.currentTime) || 1, this.hls.trigger(m.MEDIA_ENDED, {
          stalled: !1
        });
      }
    }, this.hls = t, this.fragmentTracker = e, this.registerListeners();
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t && (t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.BUFFER_APPENDED, this.onBufferAppended, this));
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.BUFFER_APPENDED, this.onBufferAppended, this));
  }
  destroy() {
    super.destroy(), this.unregisterListeners(), this.media = this.hls = this.fragmentTracker = null, this.mediaSource = void 0;
  }
  onMediaAttached(t, e) {
    this.setInterval(yf), this.mediaSource = e.mediaSource;
    const i = this.media = e.media;
    _t(i, "playing", this.onMediaPlaying), _t(i, "waiting", this.onMediaWaiting), _t(i, "ended", this.onMediaEnded);
  }
  onMediaDetaching(t, e) {
    this.clearInterval();
    const {
      media: i
    } = this;
    i && (wt(i, "playing", this.onMediaPlaying), wt(i, "waiting", this.onMediaWaiting), wt(i, "ended", this.onMediaEnded), this.media = null), this.mediaSource = void 0;
  }
  onBufferAppended(t, e) {
    this.buffered = e.timeRanges;
  }
  get hasBuffered() {
    return Object.keys(this.buffered).length > 0;
  }
  tick() {
    var t;
    if (!((t = this.media) != null && t.readyState) || !this.hasBuffered)
      return;
    const e = this.media.currentTime;
    this.poll(e, this.lastCurrentTime), this.lastCurrentTime = e;
  }
  /**
   * Checks if the playhead is stuck within a gap, and if so, attempts to free it.
   * A gap is an unbuffered range between two buffered ranges (or the start and the first buffered range).
   *
   * @param lastCurrentTime - Previously read playhead position
   */
  poll(t, e) {
    var i, s;
    const r = (i = this.hls) == null ? void 0 : i.config;
    if (!r)
      return;
    const a = this.media;
    if (!a)
      return;
    const {
      seeking: o
    } = a, c = this.seeking && !o, l = !this.seeking && o, h = a.paused && !o || a.ended || a.playbackRate === 0;
    if (this.seeking = o, t !== e) {
      e && (this.ended = 0), this.moved = !0, o || (this.nudgeRetry = 0, r.nudgeOnVideoHole && !h && t > e && this.nudgeOnVideoHole(t, e)), this.waiting === 0 && this.stallResolved(t);
      return;
    }
    if (l || c) {
      c && this.stallResolved(t);
      return;
    }
    if (h) {
      this.nudgeRetry = 0, this.stallResolved(t), !this.ended && a.ended && this.hls && (this.ended = t || 1, this.hls.trigger(m.MEDIA_ENDED, {
        stalled: !1
      }));
      return;
    }
    if (!q.getBuffered(a).length) {
      this.nudgeRetry = 0;
      return;
    }
    const d = q.bufferInfo(a, t, 0), u = d.nextStart || 0, f = this.fragmentTracker;
    if (o && f && this.hls) {
      const D = oa(this.hls.inFlightFragments, t), A = d.len > ji, _ = !u || D || u - t > ji && !f.getPartialFragment(t);
      if (A || _)
        return;
      this.moved = !1;
    }
    const g = (s = this.hls) == null ? void 0 : s.latestLevelDetails;
    if (!this.moved && this.stalled !== null && f) {
      if (!(d.len > 0) && !u)
        return;
      const A = Math.max(u, d.start || 0) - t, R = !!(g != null && g.live) ? g.targetduration * 2 : ji, b = Bi(t, f);
      if (A > 0 && (A <= R || b)) {
        a.paused || this._trySkipBufferHole(b);
        return;
      }
    }
    const v = r.detectStallWithCurrentTimeMs, p = self.performance.now(), y = this.waiting;
    let E = this.stalled;
    if (E === null)
      if (y > 0 && p - y < v)
        E = this.stalled = y;
      else {
        this.stalled = p;
        return;
      }
    const T = p - E;
    if (!o && (T >= v || y) && this.hls) {
      var S;
      if (((S = this.mediaSource) == null ? void 0 : S.readyState) === "ended" && !(g != null && g.live) && Math.abs(t - ((g == null ? void 0 : g.edge) || 0)) < 1) {
        if (this.ended)
          return;
        this.ended = t || 1, this.hls.trigger(m.MEDIA_ENDED, {
          stalled: !0
        });
        return;
      }
      if (this._reportStall(d), !this.media || !this.hls)
        return;
    }
    const x = q.bufferInfo(a, t, r.maxBufferHole);
    this._tryFixBufferStall(x, T, t);
  }
  stallResolved(t) {
    const e = this.stalled;
    if (e && this.hls && (this.stalled = null, this.stallReported)) {
      const i = self.performance.now() - e;
      this.log(`playback not stuck anymore @${t}, after ${Math.round(i)}ms`), this.stallReported = !1, this.waiting = 0, this.hls.trigger(m.STALL_RESOLVED, {});
    }
  }
  nudgeOnVideoHole(t, e) {
    var i;
    const s = this.buffered.video;
    if (this.hls && this.media && this.fragmentTracker && (i = this.buffered.audio) != null && i.length && s && s.length > 1 && t > s.end(0)) {
      const r = q.bufferedInfo(q.timeRangesToArray(this.buffered.audio), t, 0);
      if (r.len > 1 && e >= r.start) {
        const a = q.timeRangesToArray(s), o = q.bufferedInfo(a, e, 0).bufferedIndex;
        if (o > -1 && o < a.length - 1) {
          const c = q.bufferedInfo(a, t, 0).bufferedIndex, l = a[o].end, h = a[o + 1].start;
          if ((c === -1 || c > o) && h - l < 1 && // `maxBufferHole` may be too small and setting it to 0 should not disable this feature
          t - l < 2) {
            const d = new Error(`nudging playhead to flush pipeline after video hole. currentTime: ${t} hole: ${l} -> ${h} buffered index: ${c}`);
            this.warn(d.message), this.media.currentTime += 1e-6;
            let u = Bi(t, this.fragmentTracker);
            u && "fragment" in u ? u = u.fragment : u || (u = void 0);
            const f = q.bufferInfo(this.media, t, 0);
            this.hls.trigger(m.ERROR, {
              type: Y.MEDIA_ERROR,
              details: L.BUFFER_SEEK_OVER_HOLE,
              fatal: !1,
              error: d,
              reason: d.message,
              frag: u,
              buffer: f.len,
              bufferInfo: f
            });
          }
        }
      }
    }
  }
  /**
   * Detects and attempts to fix known buffer stalling issues.
   * @param bufferInfo - The properties of the current buffer.
   * @param stalledDurationMs - The amount of time Hls.js has been stalling for.
   * @private
   */
  _tryFixBufferStall(t, e, i) {
    var s, r;
    const {
      fragmentTracker: a,
      media: o
    } = this, c = (s = this.hls) == null ? void 0 : s.config;
    if (!o || !a || !c)
      return;
    const l = (r = this.hls) == null ? void 0 : r.latestLevelDetails, h = Bi(i, a);
    if ((h || l != null && l.live && i < l.fragmentStart) && (this._trySkipBufferHole(h) || !this.media))
      return;
    const d = t.buffered, u = this.adjacentTraversal(t, i);
    (d && d.length > 1 && t.len > c.maxBufferHole || t.nextStart && (t.nextStart - i < c.maxBufferHole || u)) && (e > c.highBufferWatchdogPeriod * 1e3 || this.waiting) && (this.warn("Trying to nudge playhead over buffer-hole"), this._tryNudgeBuffer(t));
  }
  adjacentTraversal(t, e) {
    const i = this.fragmentTracker, s = t.nextStart;
    if (i && s) {
      const r = i.getFragAtPos(e, K.MAIN), a = i.getFragAtPos(s, K.MAIN);
      if (r && a)
        return a.sn - r.sn < 2;
    }
    return !1;
  }
  /**
   * Triggers a BUFFER_STALLED_ERROR event, but only once per stall period.
   * @param bufferLen - The playhead distance from the end of the current buffer segment.
   * @private
   */
  _reportStall(t) {
    const {
      hls: e,
      media: i,
      stallReported: s,
      stalled: r
    } = this;
    if (!s && r !== null && i && e) {
      this.stallReported = !0;
      const a = new Error(`Playback stalling at @${i.currentTime} due to low buffer (${ot(t)})`);
      this.warn(a.message), e.trigger(m.ERROR, {
        type: Y.MEDIA_ERROR,
        details: L.BUFFER_STALLED_ERROR,
        fatal: !1,
        error: a,
        buffer: t.len,
        bufferInfo: t,
        stalled: {
          start: r
        }
      });
    }
  }
  /**
   * Attempts to fix buffer stalls by jumping over known gaps caused by partial fragments
   * @param appended - The fragment or part found at the current time (where playback is stalling).
   * @private
   */
  _trySkipBufferHole(t) {
    var e;
    const {
      fragmentTracker: i,
      media: s
    } = this, r = (e = this.hls) == null ? void 0 : e.config;
    if (!s || !i || !r)
      return 0;
    const a = s.currentTime, o = q.bufferInfo(s, a, 0), c = a < o.start ? o.start : o.nextStart;
    if (c && this.hls) {
      const h = o.len <= r.maxBufferHole, d = o.len > 0 && o.len < 1 && s.readyState < 3, u = c - a;
      if (u > 0 && (h || d)) {
        if (u > r.maxBufferHole) {
          let g = !1;
          if (a === 0) {
            const v = i.getAppendedFrag(0, K.MAIN);
            v && c < v.end && (g = !0);
          }
          if (!g && t) {
            var l;
            if (!((l = this.hls.loadLevelObj) != null && l.details) || oa(this.hls.inFlightFragments, c))
              return 0;
            let p = !1, y = t.end;
            for (; y < c; ) {
              const E = Bi(y, i);
              if (E)
                y += E.duration;
              else {
                p = !0;
                break;
              }
            }
            if (p)
              return 0;
          }
        }
        const f = Math.max(c + vf, a + pf);
        if (this.warn(`skipping hole, adjusting currentTime from ${a} to ${f}`), this.moved = !0, s.currentTime = f, !(t != null && t.gap)) {
          const g = new Error(`fragment loaded with buffer holes, seeking from ${a} to ${f}`), v = {
            type: Y.MEDIA_ERROR,
            details: L.BUFFER_SEEK_OVER_HOLE,
            fatal: !1,
            error: g,
            reason: g.message,
            buffer: o.len,
            bufferInfo: o
          };
          t && ("fragment" in t ? v.part = t : v.frag = t), this.hls.trigger(m.ERROR, v);
        }
        return f;
      }
    }
    return 0;
  }
  /**
   * Attempts to fix buffer stalls by advancing the mediaElement's current time by a small amount.
   * @private
   */
  _tryNudgeBuffer(t) {
    const {
      hls: e,
      media: i,
      nudgeRetry: s
    } = this, r = e == null ? void 0 : e.config;
    if (!i || !r)
      return 0;
    const a = i.currentTime;
    if (this.nudgeRetry++, s < r.nudgeMaxRetry) {
      const o = a + (s + 1) * r.nudgeOffset, c = new Error(`Nudging 'currentTime' from ${a} to ${o}`);
      this.warn(c.message), i.currentTime = o, e.trigger(m.ERROR, {
        type: Y.MEDIA_ERROR,
        details: L.BUFFER_NUDGE_ON_STALL,
        error: c,
        fatal: !1,
        buffer: t.len,
        bufferInfo: t
      });
    } else {
      const o = new Error(`Playhead still not moving while enough data buffered @${a} after ${r.nudgeMaxRetry} nudges`);
      this.error(o.message), e.trigger(m.ERROR, {
        type: Y.MEDIA_ERROR,
        details: L.BUFFER_STALLED_ERROR,
        error: o,
        fatal: !0,
        buffer: t.len,
        bufferInfo: t
      });
    }
  }
}
function oa(n, t) {
  const e = la(n.main);
  if (e && e.start <= t)
    return e;
  const i = la(n.audio);
  return i && i.start <= t ? i : null;
}
function la(n) {
  if (!n)
    return null;
  switch (n.state) {
    case w.IDLE:
    case w.STOPPED:
    case w.ENDED:
    case w.ERROR:
      return null;
  }
  return n.frag;
}
function Bi(n, t) {
  return t.getAppendedFrag(n, K.MAIN) || t.getPartialFragment(n);
}
const Tf = 0.25;
function fr() {
  if (!(typeof self > "u"))
    return self.VTTCue || self.TextTrackCue;
}
function Gs(n, t, e, i, s) {
  let r = new n(t, e, "");
  try {
    r.value = i, s && (r.type = s);
  } catch {
    r = new n(t, e, ot(s ? st({
      type: s
    }, i) : i));
  }
  return r;
}
const Ui = (() => {
  const n = fr();
  try {
    n && new n(0, Number.POSITIVE_INFINITY, "");
  } catch {
    return Number.MAX_VALUE;
  }
  return Number.POSITIVE_INFINITY;
})();
class Sf {
  constructor(t) {
    this.hls = void 0, this.id3Track = null, this.media = null, this.dateRangeCuesAppended = {}, this.removeCues = !0, this.assetCue = void 0, this.onEventCueEnter = () => {
      this.hls && this.hls.trigger(m.EVENT_CUE_ENTER, {});
    }, this.hls = t, this._registerListeners();
  }
  destroy() {
    this._unregisterListeners(), this.id3Track = null, this.media = null, this.dateRangeCuesAppended = {}, this.hls = this.onEventCueEnter = null;
  }
  _registerListeners() {
    const {
      hls: t
    } = this;
    t && (t.on(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.FRAG_PARSING_METADATA, this.onFragParsingMetadata, this), t.on(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.on(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.on(m.LEVEL_PTS_UPDATED, this.onLevelPtsUpdated, this));
  }
  _unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (t.off(m.MEDIA_ATTACHING, this.onMediaAttaching, this), t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.FRAG_PARSING_METADATA, this.onFragParsingMetadata, this), t.off(m.BUFFER_FLUSHING, this.onBufferFlushing, this), t.off(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.off(m.LEVEL_PTS_UPDATED, this.onLevelPtsUpdated, this));
  }
  // Add ID3 metatadata text track.
  onMediaAttaching(t, e) {
    var i;
    this.media = e.media, ((i = e.overrides) == null ? void 0 : i.cueRemoval) === !1 && (this.removeCues = !1);
  }
  onMediaAttached() {
    var t;
    const e = (t = this.hls) == null ? void 0 : t.latestLevelDetails;
    e && this.updateDateRangeCues(e);
  }
  onMediaDetaching(t, e) {
    this.media = null, !e.transferMedia && (this.id3Track && (this.removeCues && Ve(this.id3Track, this.onEventCueEnter), this.id3Track = null), this.dateRangeCuesAppended = {});
  }
  onManifestLoading() {
    this.dateRangeCuesAppended = {};
  }
  createTrack(t) {
    const e = this.getID3Track(t.textTracks);
    return e.mode = "hidden", e;
  }
  getID3Track(t) {
    if (this.media) {
      for (let e = 0; e < t.length; e++) {
        const i = t[e];
        if (i.kind === "metadata" && i.label === "id3")
          return Oo(i, this.media), i;
      }
      return this.media.addTextTrack("metadata", "id3");
    }
  }
  onFragParsingMetadata(t, e) {
    if (!this.media || !this.hls)
      return;
    const {
      enableEmsgMetadataCues: i,
      enableID3MetadataCues: s
    } = this.hls.config;
    if (!i && !s)
      return;
    const {
      samples: r
    } = e;
    this.id3Track || (this.id3Track = this.createTrack(this.media));
    const a = fr();
    if (a)
      for (let o = 0; o < r.length; o++) {
        const c = r[o].type;
        if (c === Mt.emsg && !i || !s)
          continue;
        const l = oo(r[o].data), h = r[o].pts;
        let d = h + r[o].duration;
        d > Ui && (d = Ui), d - h <= 0 && (d = h + Tf);
        for (let f = 0; f < l.length; f++) {
          const g = l[f];
          if (!lo(g)) {
            this.updateId3CueEnds(h, c);
            const v = Gs(a, h, d, g, c);
            v && this.id3Track.addCue(v);
          }
        }
      }
  }
  updateId3CueEnds(t, e) {
    var i;
    const s = (i = this.id3Track) == null ? void 0 : i.cues;
    if (s)
      for (let r = s.length; r--; ) {
        const a = s[r];
        a.type === e && a.startTime < t && a.endTime === Ui && (a.endTime = t);
      }
  }
  onBufferFlushing(t, {
    startOffset: e,
    endOffset: i,
    type: s
  }) {
    const {
      id3Track: r,
      hls: a
    } = this;
    if (!a)
      return;
    const {
      config: {
        enableEmsgMetadataCues: o,
        enableID3MetadataCues: c
      }
    } = a;
    if (r && (o || c)) {
      let l;
      s === "audio" ? l = (h) => h.type === Mt.audioId3 && c : s === "video" ? l = (h) => h.type === Mt.emsg && o : l = (h) => h.type === Mt.audioId3 && c || h.type === Mt.emsg && o, hr(r, e, i, l);
    }
  }
  onLevelUpdated(t, {
    details: e
  }) {
    this.updateDateRangeCues(e, !0);
  }
  onLevelPtsUpdated(t, e) {
    Math.abs(e.drift) > 0.01 && this.updateDateRangeCues(e.details);
  }
  updateDateRangeCues(t, e) {
    if (!this.hls || !this.media)
      return;
    const {
      assetPlayerId: i,
      timelineOffset: s,
      enableDateRangeMetadataCues: r,
      interstitialsController: a
    } = this.hls.config;
    if (!r)
      return;
    const o = fr();
    if (i && s && !a) {
      const {
        fragmentStart: v,
        fragmentEnd: p
      } = t;
      let y = this.assetCue;
      y ? (y.startTime = v, y.endTime = p) : o && (y = this.assetCue = Gs(o, v, p, {
        assetPlayerId: this.hls.config.assetPlayerId
      }, "hlsjs.interstitial.asset"), y && (y.id = i, this.id3Track || (this.id3Track = this.createTrack(this.media)), this.id3Track.addCue(y), y.addEventListener("enter", this.onEventCueEnter)));
    }
    if (!t.hasProgramDateTime)
      return;
    const {
      id3Track: c
    } = this, {
      dateRanges: l
    } = t, h = Object.keys(l);
    let d = this.dateRangeCuesAppended;
    if (c && e) {
      var u;
      if ((u = c.cues) != null && u.length) {
        const v = Object.keys(d).filter((p) => !h.includes(p));
        for (let p = v.length; p--; ) {
          var f;
          const y = v[p], E = (f = d[y]) == null ? void 0 : f.cues;
          delete d[y], E && Object.keys(E).forEach((T) => {
            const S = E[T];
            if (S) {
              S.removeEventListener("enter", this.onEventCueEnter);
              try {
                c.removeCue(S);
              } catch {
              }
            }
          });
        }
      } else
        d = this.dateRangeCuesAppended = {};
    }
    const g = t.fragments[t.fragments.length - 1];
    if (!(h.length === 0 || !B(g == null ? void 0 : g.programDateTime))) {
      this.id3Track || (this.id3Track = this.createTrack(this.media));
      for (let v = 0; v < h.length; v++) {
        const p = h[v], y = l[p], E = y.startTime, T = d[p], S = (T == null ? void 0 : T.cues) || {};
        let x = (T == null ? void 0 : T.durationKnown) || !1, D = Ui;
        const {
          duration: A,
          endDate: _
        } = y;
        if (_ && A !== null)
          D = E + A, x = !0;
        else if (y.endOnNext && !x) {
          const b = h.reduce((C, F) => {
            if (F !== y.id) {
              const U = l[F];
              if (U.class === y.class && U.startDate > y.startDate && (!C || y.startDate < C.startDate))
                return U;
            }
            return C;
          }, null);
          b && (D = b.startTime, x = !0);
        }
        const R = Object.keys(y.attr);
        for (let b = 0; b < R.length; b++) {
          const C = R[b];
          if (!Gc(C))
            continue;
          const F = S[C];
          if (F)
            x && !(T != null && T.durationKnown) ? F.endTime = D : Math.abs(F.startTime - E) > 0.01 && (F.startTime = E, F.endTime = D);
          else if (o) {
            let U = y.attr[C];
            Kc(C) && (U = ya(U));
            const G = Gs(o, E, D, {
              key: C,
              data: U
            }, Mt.dateRange);
            G && (G.id = p, this.id3Track.addCue(G), S[C] = G, a && (C === "X-ASSET-LIST" || C === "X-ASSET-URL") && G.addEventListener("enter", this.onEventCueEnter));
          }
        }
        d[p] = {
          cues: S,
          dateRange: y,
          durationKnown: x
        };
      }
    }
  }
}
class xf {
  constructor(t) {
    this.hls = void 0, this.config = void 0, this.media = null, this.currentTime = 0, this.stallCount = 0, this._latency = null, this._targetLatencyUpdated = !1, this.onTimeupdate = () => {
      const {
        media: e
      } = this, i = this.levelDetails;
      if (!e || !i)
        return;
      this.currentTime = e.currentTime;
      const s = this.computeLatency();
      if (s === null)
        return;
      this._latency = s;
      const {
        lowLatencyMode: r,
        maxLiveSyncPlaybackRate: a
      } = this.config;
      if (!r || a === 1 || !i.live)
        return;
      const o = this.targetLatency;
      if (o === null)
        return;
      const c = s - o, l = Math.min(this.maxLatency, o + i.targetduration);
      if (c < l && c > 0.05 && this.forwardBufferLength > 1) {
        const d = Math.min(2, Math.max(1, a)), u = Math.round(2 / (1 + Math.exp(-0.75 * c - this.edgeStalled)) * 20) / 20, f = Math.min(d, Math.max(1, u));
        this.changeMediaPlaybackRate(e, f);
      } else e.playbackRate !== 1 && e.playbackRate !== 0 && this.changeMediaPlaybackRate(e, 1);
    }, this.hls = t, this.config = t.config, this.registerListeners();
  }
  get levelDetails() {
    var t;
    return ((t = this.hls) == null ? void 0 : t.latestLevelDetails) || null;
  }
  get latency() {
    return this._latency || 0;
  }
  get maxLatency() {
    const {
      config: t
    } = this;
    if (t.liveMaxLatencyDuration !== void 0)
      return t.liveMaxLatencyDuration;
    const e = this.levelDetails;
    return e ? t.liveMaxLatencyDurationCount * e.targetduration : 0;
  }
  get targetLatency() {
    const t = this.levelDetails;
    if (t === null || this.hls === null)
      return null;
    const {
      holdBack: e,
      partHoldBack: i,
      targetduration: s
    } = t, {
      liveSyncDuration: r,
      liveSyncDurationCount: a,
      lowLatencyMode: o
    } = this.config, c = this.hls.userConfig;
    let l = o && i || e;
    (this._targetLatencyUpdated || c.liveSyncDuration || c.liveSyncDurationCount || l === 0) && (l = r !== void 0 ? r : a * s);
    const h = s;
    return l + Math.min(this.stallCount * this.config.liveSyncOnStallIncrease, h);
  }
  set targetLatency(t) {
    this.stallCount = 0, this.config.liveSyncDuration = t, this._targetLatencyUpdated = !0;
  }
  get liveSyncPosition() {
    const t = this.estimateLiveEdge(), e = this.targetLatency;
    if (t === null || e === null)
      return null;
    const i = this.levelDetails;
    if (i === null)
      return null;
    const s = i.edge, r = t - e - this.edgeStalled, a = s - i.totalduration, o = s - (this.config.lowLatencyMode && i.partTarget || i.targetduration);
    return Math.min(Math.max(a, r), o);
  }
  get drift() {
    const t = this.levelDetails;
    return t === null ? 1 : t.drift;
  }
  get edgeStalled() {
    const t = this.levelDetails;
    if (t === null)
      return 0;
    const e = (this.config.lowLatencyMode && t.partTarget || t.targetduration) * 3;
    return Math.max(t.age - e, 0);
  }
  get forwardBufferLength() {
    const {
      media: t
    } = this, e = this.levelDetails;
    if (!t || !e)
      return 0;
    const i = t.buffered.length;
    return (i ? t.buffered.end(i - 1) : e.edge) - this.currentTime;
  }
  destroy() {
    this.unregisterListeners(), this.onMediaDetaching(), this.hls = null;
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t && (t.on(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.on(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.on(m.ERROR, this.onError, this));
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t && (t.off(m.MEDIA_ATTACHED, this.onMediaAttached, this), t.off(m.MEDIA_DETACHING, this.onMediaDetaching, this), t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.LEVEL_UPDATED, this.onLevelUpdated, this), t.off(m.ERROR, this.onError, this));
  }
  onMediaAttached(t, e) {
    this.media = e.media, this.media.addEventListener("timeupdate", this.onTimeupdate);
  }
  onMediaDetaching() {
    this.media && (this.media.removeEventListener("timeupdate", this.onTimeupdate), this.media = null);
  }
  onManifestLoading() {
    this._latency = null, this.stallCount = 0;
  }
  onLevelUpdated(t, {
    details: e
  }) {
    e.advanced && this.onTimeupdate(), !e.live && this.media && this.media.removeEventListener("timeupdate", this.onTimeupdate);
  }
  onError(t, e) {
    var i;
    e.details === L.BUFFER_STALLED_ERROR && (this.stallCount++, this.hls && (i = this.levelDetails) != null && i.live && this.hls.logger.warn("[latency-controller]: Stall detected, adjusting target latency"));
  }
  changeMediaPlaybackRate(t, e) {
    var i, s;
    t.playbackRate !== e && ((i = this.hls) == null || i.logger.debug(`[latency-controller]: latency=${this.latency.toFixed(3)}, targetLatency=${(s = this.targetLatency) == null ? void 0 : s.toFixed(3)}, forwardBufferLength=${this.forwardBufferLength.toFixed(3)}: adjusting playback rate from ${t.playbackRate} to ${e}`), t.playbackRate = e);
  }
  estimateLiveEdge() {
    const t = this.levelDetails;
    return t === null ? null : t.edge + t.age;
  }
  computeLatency() {
    const t = this.estimateLiveEdge();
    return t === null ? null : t - this.currentTime;
  }
}
class Af extends Mr {
  constructor(t, e) {
    super(t, "level-controller"), this._levels = [], this._firstLevel = -1, this._maxAutoLevel = -1, this._startLevel = void 0, this.currentLevel = null, this.currentLevelIndex = -1, this.manualLevelIndex = -1, this.steering = void 0, this.onParsedComplete = void 0, this.steering = e, this._registerListeners();
  }
  _registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.on(m.LEVEL_LOADED, this.onLevelLoaded, this), t.on(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.on(m.FRAG_BUFFERED, this.onFragBuffered, this), t.on(m.ERROR, this.onError, this);
  }
  _unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.MANIFEST_LOADED, this.onManifestLoaded, this), t.off(m.LEVEL_LOADED, this.onLevelLoaded, this), t.off(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.off(m.FRAG_BUFFERED, this.onFragBuffered, this), t.off(m.ERROR, this.onError, this);
  }
  destroy() {
    this._unregisterListeners(), this.steering = null, this.resetLevels(), super.destroy();
  }
  stopLoad() {
    this._levels.forEach((e) => {
      e.loadError = 0, e.fragmentError = 0;
    }), super.stopLoad();
  }
  resetLevels() {
    this._startLevel = void 0, this.manualLevelIndex = -1, this.currentLevelIndex = -1, this.currentLevel = null, this._levels = [], this._maxAutoLevel = -1;
  }
  onManifestLoading(t, e) {
    this.resetLevels();
  }
  onManifestLoaded(t, e) {
    const i = this.hls.config.preferManagedMediaSource, s = [], r = {}, a = {};
    let o = !1, c = !1, l = !1;
    e.levels.forEach((h) => {
      const d = h.attrs;
      let {
        audioCodec: u,
        videoCodec: f
      } = h;
      u && (h.audioCodec = u = Zi(u, i) || void 0), f && (f = h.videoCodec = rc(f));
      const {
        width: g,
        height: v,
        unknownCodecs: p
      } = h, y = (p == null ? void 0 : p.length) || 0;
      if (o || (o = !!(g && v)), c || (c = !!f), l || (l = !!u), y || u && !this.isAudioSupported(u) || f && !this.isVideoSupported(f)) {
        this.log(`Some or all CODECS not supported "${d.CODECS}"`);
        return;
      }
      const {
        CODECS: E,
        "FRAME-RATE": T,
        "HDCP-LEVEL": S,
        "PATHWAY-ID": x,
        RESOLUTION: D,
        "VIDEO-RANGE": A
      } = d, R = `${`${x || "."}-`}${h.bitrate}-${D}-${T}-${E}-${A}-${S}`;
      if (r[R])
        if (r[R].uri !== h.url && !h.attrs["PATHWAY-ID"]) {
          const b = a[R] += 1;
          h.attrs["PATHWAY-ID"] = new Array(b + 1).join(".");
          const C = this.createLevel(h);
          r[R] = C, s.push(C);
        } else
          r[R].addGroupId("audio", d.AUDIO), r[R].addGroupId("text", d.SUBTITLES);
      else {
        const b = this.createLevel(h);
        r[R] = b, a[R] = 1, s.push(b);
      }
    }), this.filterAndSortMediaOptions(s, e, o, c, l);
  }
  createLevel(t) {
    const e = new pi(t), i = t.supplemental;
    if (i != null && i.videoCodec && !this.isVideoSupported(i.videoCodec)) {
      const s = new Error(`SUPPLEMENTAL-CODECS not supported "${i.videoCodec}"`);
      this.log(s.message), e.supportedResult = wa(s, []);
    }
    return e;
  }
  isAudioSupported(t) {
    return gi(t, "audio", this.hls.config.preferManagedMediaSource);
  }
  isVideoSupported(t) {
    return gi(t, "video", this.hls.config.preferManagedMediaSource);
  }
  filterAndSortMediaOptions(t, e, i, s, r) {
    var a;
    let o = [], c = [], l = t;
    const h = ((a = e.stats) == null ? void 0 : a.parsing) || {};
    if ((i || s) && r && (l = l.filter(({
      videoCodec: E,
      videoRange: T,
      width: S,
      height: x
    }) => (!!E || !!(S && x)) && gc(T))), l.length === 0) {
      Promise.resolve().then(() => {
        if (this.hls) {
          let E = "no level with compatible codecs found in manifest", T = E;
          e.levels.length && (T = `one or more CODECS in variant not supported: ${ot(e.levels.map((x) => x.attrs.CODECS).filter((x, D, A) => A.indexOf(x) === D))}`, this.warn(T), E += ` (${T})`);
          const S = new Error(E);
          this.hls.trigger(m.ERROR, {
            type: Y.MEDIA_ERROR,
            details: L.MANIFEST_INCOMPATIBLE_CODECS_ERROR,
            fatal: !0,
            url: e.url,
            error: S,
            reason: T
          });
        }
      }), h.end = performance.now();
      return;
    }
    e.audioTracks && (o = e.audioTracks.filter((E) => !E.audioCodec || this.isAudioSupported(E.audioCodec)), ca(o)), e.subtitles && (c = e.subtitles, ca(c));
    const d = l.slice(0);
    l.sort((E, T) => {
      if (E.attrs["HDCP-LEVEL"] !== T.attrs["HDCP-LEVEL"])
        return (E.attrs["HDCP-LEVEL"] || "") > (T.attrs["HDCP-LEVEL"] || "") ? 1 : -1;
      if (i && E.height !== T.height)
        return E.height - T.height;
      if (E.frameRate !== T.frameRate)
        return E.frameRate - T.frameRate;
      if (E.videoRange !== T.videoRange)
        return Ji.indexOf(E.videoRange) - Ji.indexOf(T.videoRange);
      if (E.videoCodec !== T.videoCodec) {
        const S = Jr(E.videoCodec), x = Jr(T.videoCodec);
        if (S !== x)
          return x - S;
      }
      if (E.uri === T.uri && E.codecSet !== T.codecSet) {
        const S = Qi(E.codecSet), x = Qi(T.codecSet);
        if (S !== x)
          return x - S;
      }
      return E.averageBitrate !== T.averageBitrate ? E.averageBitrate - T.averageBitrate : 0;
    });
    let u = d[0];
    if (this.steering && (l = this.steering.filterParsedLevels(l), l.length !== d.length)) {
      for (let E = 0; E < d.length; E++)
        if (d[E].pathwayId === l[0].pathwayId) {
          u = d[E];
          break;
        }
    }
    this._levels = l;
    for (let E = 0; E < l.length; E++)
      if (l[E] === u) {
        var f;
        this._firstLevel = E;
        const T = u.bitrate, S = this.hls.bandwidthEstimate;
        if (this.log(`manifest loaded, ${l.length} level(s) found, first bitrate: ${T}`), ((f = this.hls.userConfig) == null ? void 0 : f.abrEwmaDefaultEstimate) === void 0) {
          const x = Math.min(T, this.hls.config.abrEwmaDefaultEstimateMax);
          x > S && S === this.hls.abrEwmaDefaultEstimate && (this.hls.bandwidthEstimate = x);
        }
        break;
      }
    const g = r && !s, v = this.hls.config, p = !!(v.audioStreamController && v.audioTrackController), y = {
      levels: l,
      audioTracks: o,
      subtitleTracks: c,
      sessionData: e.sessionData,
      sessionKeys: e.sessionKeys,
      firstLevel: this._firstLevel,
      stats: e.stats,
      audio: r,
      video: s,
      altAudio: p && !g && o.some((E) => !!E.url)
    };
    h.end = performance.now(), this.hls.trigger(m.MANIFEST_PARSED, y);
  }
  get levels() {
    return this._levels.length === 0 ? null : this._levels;
  }
  get loadLevelObj() {
    return this.currentLevel;
  }
  get level() {
    return this.currentLevelIndex;
  }
  set level(t) {
    const e = this._levels;
    if (e.length === 0)
      return;
    if (t < 0 || t >= e.length) {
      const h = new Error("invalid level idx"), d = t < 0;
      if (this.hls.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.LEVEL_SWITCH_ERROR,
        level: t,
        fatal: d,
        error: h,
        reason: h.message
      }), d)
        return;
      t = Math.min(t, e.length - 1);
    }
    const i = this.currentLevelIndex, s = this.currentLevel, r = s ? s.attrs["PATHWAY-ID"] : void 0, a = e[t], o = a.attrs["PATHWAY-ID"];
    if (this.currentLevelIndex = t, this.currentLevel = a, i === t && s && r === o)
      return;
    this.log(`Switching to level ${t} (${a.height ? a.height + "p " : ""}${a.videoRange ? a.videoRange + " " : ""}${a.codecSet ? a.codecSet + " " : ""}@${a.bitrate})${o ? " with Pathway " + o : ""} from level ${i}${r ? " with Pathway " + r : ""}`);
    const c = {
      level: t,
      attrs: a.attrs,
      details: a.details,
      bitrate: a.bitrate,
      averageBitrate: a.averageBitrate,
      maxBitrate: a.maxBitrate,
      realBitrate: a.realBitrate,
      width: a.width,
      height: a.height,
      codecSet: a.codecSet,
      audioCodec: a.audioCodec,
      videoCodec: a.videoCodec,
      audioGroups: a.audioGroups,
      subtitleGroups: a.subtitleGroups,
      loaded: a.loaded,
      loadError: a.loadError,
      fragmentError: a.fragmentError,
      name: a.name,
      id: a.id,
      uri: a.uri,
      url: a.url,
      urlId: 0,
      audioGroupIds: a.audioGroupIds,
      textGroupIds: a.textGroupIds
    };
    this.hls.trigger(m.LEVEL_SWITCHING, c);
    const l = a.details;
    if (!l || l.live) {
      const h = this.switchParams(a.uri, s == null ? void 0 : s.details, l);
      this.loadPlaylist(h);
    }
  }
  get manualLevel() {
    return this.manualLevelIndex;
  }
  set manualLevel(t) {
    this.manualLevelIndex = t, this._startLevel === void 0 && (this._startLevel = t), t !== -1 && (this.level = t);
  }
  get firstLevel() {
    return this._firstLevel;
  }
  set firstLevel(t) {
    this._firstLevel = t;
  }
  get startLevel() {
    if (this._startLevel === void 0) {
      const t = this.hls.config.startLevel;
      return t !== void 0 ? t : this.hls.firstAutoLevel;
    }
    return this._startLevel;
  }
  set startLevel(t) {
    this._startLevel = t;
  }
  get pathways() {
    return this.steering ? this.steering.pathways() : [];
  }
  get pathwayPriority() {
    return this.steering ? this.steering.pathwayPriority : null;
  }
  set pathwayPriority(t) {
    if (this.steering) {
      const e = this.steering.pathways(), i = t.filter((s) => e.indexOf(s) !== -1);
      if (t.length < 1) {
        this.warn(`pathwayPriority ${t} should contain at least one pathway from list: ${e}`);
        return;
      }
      this.steering.pathwayPriority = i;
    }
  }
  onError(t, e) {
    e.fatal || !e.context || e.context.type === tt.LEVEL && e.context.level === this.level && this.checkRetry(e);
  }
  // reset errors on the successful load of a fragment
  onFragBuffered(t, {
    frag: e
  }) {
    if (e !== void 0 && e.type === K.MAIN) {
      const i = e.elementaryStreams;
      if (!Object.keys(i).some((r) => !!i[r]))
        return;
      const s = this._levels[e.level];
      s != null && s.loadError && (this.log(`Resetting level error count of ${s.loadError} on frag buffered`), s.loadError = 0);
    }
  }
  onLevelLoaded(t, e) {
    var i;
    const {
      level: s,
      details: r
    } = e, a = e.levelInfo;
    if (!a) {
      var o;
      this.warn(`Invalid level index ${s}`), (o = e.deliveryDirectives) != null && o.skip && (r.deltaUpdateFailed = !0);
      return;
    }
    if (a === this.currentLevel || e.withoutMultiVariant) {
      a.fragmentError === 0 && (a.loadError = 0);
      let c = a.details;
      c === e.details && c.advanced && (c = void 0), this.playlistLoaded(s, e, c);
    } else (i = e.deliveryDirectives) != null && i.skip && (r.deltaUpdateFailed = !0);
  }
  loadPlaylist(t) {
    super.loadPlaylist(), this.shouldLoadPlaylist(this.currentLevel) && this.scheduleLoading(this.currentLevel, t);
  }
  loadingPlaylist(t, e) {
    super.loadingPlaylist(t, e);
    const i = this.getUrlWithDirectives(t.uri, e), s = this.currentLevelIndex, r = t.attrs["PATHWAY-ID"], a = t.details, o = a == null ? void 0 : a.age;
    this.log(`Loading level index ${s}${(e == null ? void 0 : e.msn) !== void 0 ? " at sn " + e.msn + " part " + e.part : ""}${r ? " Pathway " + r : ""}${o && a.live ? " age " + o.toFixed(1) + (a.type && " " + a.type || "") : ""} ${i}`), this.hls.trigger(m.LEVEL_LOADING, {
      url: i,
      level: s,
      levelInfo: t,
      pathwayId: t.attrs["PATHWAY-ID"],
      id: 0,
      // Deprecated Level urlId
      deliveryDirectives: e || null
    });
  }
  get nextLoadLevel() {
    return this.manualLevelIndex !== -1 ? this.manualLevelIndex : this.hls.nextAutoLevel;
  }
  set nextLoadLevel(t) {
    this.level = t, this.manualLevelIndex === -1 && (this.hls.nextAutoLevel = t);
  }
  removeLevel(t) {
    var e;
    if (this._levels.length === 1)
      return;
    const i = this._levels.filter((r, a) => a !== t ? !0 : (this.steering && this.steering.removeLevel(r), r === this.currentLevel && (this.currentLevel = null, this.currentLevelIndex = -1, r.details && r.details.fragments.forEach((o) => o.level = -1)), !1));
    Qa(i), this._levels = i, this.currentLevelIndex > -1 && (e = this.currentLevel) != null && e.details && (this.currentLevelIndex = this.currentLevel.details.fragments[0].level), this.manualLevelIndex > -1 && (this.manualLevelIndex = this.currentLevelIndex);
    const s = i.length - 1;
    this._firstLevel = Math.min(this._firstLevel, s), this._startLevel && (this._startLevel = Math.min(this._startLevel, s)), this.hls.trigger(m.LEVELS_UPDATED, {
      levels: i
    });
  }
  onLevelsUpdated(t, {
    levels: e
  }) {
    this._levels = e;
  }
  checkMaxAutoUpdated() {
    const {
      autoLevelCapping: t,
      maxAutoLevel: e,
      maxHdcpLevel: i
    } = this.hls;
    this._maxAutoLevel !== e && (this._maxAutoLevel = e, this.hls.trigger(m.MAX_AUTO_LEVEL_UPDATED, {
      autoLevelCapping: t,
      levels: this.levels,
      maxAutoLevel: e,
      minAutoLevel: this.hls.minAutoLevel,
      maxHdcpLevel: i
    }));
  }
}
function ca(n) {
  const t = {};
  n.forEach((e) => {
    const i = e.groupId || "";
    e.id = t[i] = t[i] || 0, t[i]++;
  });
}
function zo() {
  return self.SourceBuffer || self.WebKitSourceBuffer;
}
function jo() {
  if (!ge())
    return !1;
  const t = zo();
  return !t || t.prototype && typeof t.prototype.appendBuffer == "function" && typeof t.prototype.remove == "function";
}
function bf() {
  if (!jo())
    return !1;
  const n = ge();
  return typeof (n == null ? void 0 : n.isTypeSupported) == "function" && (["avc1.42E01E,mp4a.40.2", "av01.0.01M.08", "vp09.00.50.08"].some((t) => n.isTypeSupported(mi(t, "video"))) || ["mp4a.40.2", "fLaC"].some((t) => n.isTypeSupported(mi(t, "audio"))));
}
function If() {
  var n;
  const t = zo();
  return typeof (t == null || (n = t.prototype) == null ? void 0 : n.changeType) == "function";
}
const Lf = 100;
class Rf extends Rr {
  constructor(t, e, i) {
    super(t, e, i, "stream-controller", K.MAIN), this.audioCodecSwap = !1, this.level = -1, this._forceStartLoad = !1, this._hasEnoughToStart = !1, this.altAudio = 0, this.audioOnly = !1, this.fragPlaying = null, this.fragLastKbps = 0, this.couldBacktrack = !1, this.backtrackFragment = null, this.audioCodecSwitch = !1, this.videoBuffer = null, this.onMediaPlaying = () => {
      this.tick();
    }, this.onMediaSeeked = () => {
      const s = this.media, r = s ? s.currentTime : null;
      if (r === null || !B(r) || (this.log(`Media seeked to ${r.toFixed(3)}`), !this.getBufferedFrag(r)))
        return;
      const a = this.getFwdBufferInfoAtPos(s, r, K.MAIN, 0);
      if (a === null || a.len === 0) {
        this.warn(`Main forward buffer length at ${r} on "seeked" event ${a ? a.len : "empty"})`);
        return;
      }
      this.tick();
    }, this.registerListeners();
  }
  registerListeners() {
    super.registerListeners();
    const {
      hls: t
    } = this;
    t.on(m.MANIFEST_PARSED, this.onManifestParsed, this), t.on(m.LEVEL_LOADING, this.onLevelLoading, this), t.on(m.LEVEL_LOADED, this.onLevelLoaded, this), t.on(m.FRAG_LOAD_EMERGENCY_ABORTED, this.onFragLoadEmergencyAborted, this), t.on(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.on(m.AUDIO_TRACK_SWITCHED, this.onAudioTrackSwitched, this), t.on(m.BUFFER_CREATED, this.onBufferCreated, this), t.on(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.on(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.on(m.FRAG_BUFFERED, this.onFragBuffered, this);
  }
  unregisterListeners() {
    super.unregisterListeners();
    const {
      hls: t
    } = this;
    t.off(m.MANIFEST_PARSED, this.onManifestParsed, this), t.off(m.LEVEL_LOADED, this.onLevelLoaded, this), t.off(m.FRAG_LOAD_EMERGENCY_ABORTED, this.onFragLoadEmergencyAborted, this), t.off(m.AUDIO_TRACK_SWITCHING, this.onAudioTrackSwitching, this), t.off(m.AUDIO_TRACK_SWITCHED, this.onAudioTrackSwitched, this), t.off(m.BUFFER_CREATED, this.onBufferCreated, this), t.off(m.BUFFER_FLUSHED, this.onBufferFlushed, this), t.off(m.LEVELS_UPDATED, this.onLevelsUpdated, this), t.off(m.FRAG_BUFFERED, this.onFragBuffered, this);
  }
  onHandlerDestroying() {
    this.onMediaPlaying = this.onMediaSeeked = null, this.unregisterListeners(), super.onHandlerDestroying();
  }
  startLoad(t, e) {
    if (this.levels) {
      const {
        lastCurrentTime: i,
        hls: s
      } = this;
      if (this.stopLoad(), this.setInterval(Lf), this.level = -1, !this.startFragRequested) {
        let r = s.startLevel;
        r === -1 && (s.config.testBandwidth && this.levels.length > 1 ? (r = 0, this.bitrateTest = !0) : r = s.firstAutoLevel), s.nextLoadLevel = r, this.level = s.loadLevel, this._hasEnoughToStart = !!e;
      }
      i > 0 && t === -1 && !e && (this.log(`Override startPosition with lastCurrentTime @${i.toFixed(3)}`), t = i), this.state = w.IDLE, this.nextLoadPosition = this.lastCurrentTime = t + this.timelineOffset, this.startPosition = e ? -1 : t, this.tick();
    } else
      this._forceStartLoad = !0, this.state = w.STOPPED;
  }
  stopLoad() {
    this._forceStartLoad = !1, super.stopLoad();
  }
  doTick() {
    switch (this.state) {
      case w.WAITING_LEVEL: {
        const {
          levels: t,
          level: e
        } = this, i = t == null ? void 0 : t[e], s = i == null ? void 0 : i.details;
        if (s && (!s.live || this.levelLastLoaded === i && !this.waitForLive(i))) {
          if (this.waitForCdnTuneIn(s))
            break;
          this.state = w.IDLE;
          break;
        } else if (this.hls.nextLoadLevel !== this.level) {
          this.state = w.IDLE;
          break;
        }
        break;
      }
      case w.FRAG_LOADING_WAITING_RETRY:
        this.checkRetryDate();
        break;
    }
    this.state === w.IDLE && this.doTickIdle(), this.onTickEnd();
  }
  onTickEnd() {
    var t;
    super.onTickEnd(), (t = this.media) != null && t.readyState && this.media.seeking === !1 && (this.lastCurrentTime = this.media.currentTime), this.checkFragmentChanged();
  }
  doTickIdle() {
    const {
      hls: t,
      levelLastLoaded: e,
      levels: i,
      media: s
    } = this;
    if (e === null || !s && !this.primaryPrefetch && (this.startFragRequested || !t.config.startFragPrefetch) || this.altAudio && this.audioOnly)
      return;
    const r = this.buffering ? t.nextLoadLevel : t.loadLevel;
    if (!(i != null && i[r]))
      return;
    const a = i[r], o = this.getMainFwdBufferInfo();
    if (o === null)
      return;
    const c = this.getLevelDetails();
    if (c && this._streamEnded(o, c)) {
      const v = {};
      this.altAudio === 2 && (v.type = "video"), this.hls.trigger(m.BUFFER_EOS, v), this.state = w.ENDED;
      return;
    }
    if (!this.buffering)
      return;
    t.loadLevel !== r && t.manualLevel === -1 && this.log(`Adapting to level ${r} from level ${this.level}`), this.level = t.nextLoadLevel = r;
    const l = a.details;
    if (!l || this.state === w.WAITING_LEVEL || this.waitForLive(a)) {
      this.level = r, this.state = w.WAITING_LEVEL, this.startFragRequested = !1;
      return;
    }
    const h = o.len, d = this.getMaxBufferLength(a.maxBitrate);
    if (h >= d)
      return;
    this.backtrackFragment && this.backtrackFragment.start > o.end && (this.backtrackFragment = null);
    const u = this.backtrackFragment ? this.backtrackFragment.start : o.end;
    let f = this.getNextFragment(u, l);
    if (this.couldBacktrack && !this.fragPrevious && f && ut(f) && this.fragmentTracker.getState(f) !== yt.OK) {
      var g;
      const p = ((g = this.backtrackFragment) != null ? g : f).sn - l.startSN, y = l.fragments[p - 1];
      y && f.cc === y.cc && (f = y, this.fragmentTracker.removeFragment(y));
    } else this.backtrackFragment && o.len && (this.backtrackFragment = null);
    if (f && this.isLoopLoading(f, u)) {
      if (!f.gap) {
        const p = this.audioOnly && !this.altAudio ? at.AUDIO : at.VIDEO, y = (p === at.VIDEO ? this.videoBuffer : this.mediaBuffer) || this.media;
        y && this.afterBufferFlushed(y, p, K.MAIN);
      }
      f = this.getNextFragmentLoopLoading(f, l, o, K.MAIN, d);
    }
    f && (f.initSegment && !f.initSegment.data && !this.bitrateTest && (f = f.initSegment), this.loadFragment(f, a, u));
  }
  loadFragment(t, e, i) {
    const s = this.fragmentTracker.getState(t);
    s === yt.NOT_LOADED || s === yt.PARTIAL ? ut(t) ? this.bitrateTest ? (this.log(`Fragment ${t.sn} of level ${t.level} is being downloaded to test bitrate and will not be buffered`), this._loadBitrateTestFrag(t, e)) : super.loadFragment(t, e, i) : this._loadInitSegment(t, e) : this.clearTrackerIfNeeded(t);
  }
  getBufferedFrag(t) {
    return this.fragmentTracker.getBufferedFrag(t, K.MAIN);
  }
  followingBufferedFrag(t) {
    return t ? this.getBufferedFrag(t.end + 0.5) : null;
  }
  /*
    on immediate level switch :
     - pause playback if playing
     - cancel any pending load request
     - and trigger a buffer flush
  */
  immediateLevelSwitch() {
    this.abortCurrentFrag(), this.flushMainBuffer(0, Number.POSITIVE_INFINITY);
  }
  /**
   * try to switch ASAP without breaking video playback:
   * in order to ensure smooth but quick level switching,
   * we need to find the next flushable buffer range
   * we should take into account new segment fetch time
   */
  nextLevelSwitch() {
    const {
      levels: t,
      media: e
    } = this;
    if (e != null && e.readyState) {
      let i;
      const s = this.getAppendedFrag(e.currentTime);
      s && s.start > 1 && this.flushMainBuffer(0, s.start - 1);
      const r = this.getLevelDetails();
      if (r != null && r.live) {
        const o = this.getMainFwdBufferInfo();
        if (!o || o.len < r.targetduration * 2)
          return;
      }
      if (!e.paused && t) {
        const o = this.hls.nextLoadLevel, c = t[o], l = this.fragLastKbps;
        l && this.fragCurrent ? i = this.fragCurrent.duration * c.maxBitrate / (1e3 * l) + 1 : i = 0;
      } else
        i = 0;
      const a = this.getBufferedFrag(e.currentTime + i);
      if (a) {
        const o = this.followingBufferedFrag(a);
        if (o) {
          this.abortCurrentFrag();
          const c = o.maxStartPTS ? o.maxStartPTS : o.start, l = o.duration, h = Math.max(a.end, c + Math.min(Math.max(l - this.config.maxFragLookUpTolerance, l * (this.couldBacktrack ? 0.5 : 0.125)), l * (this.couldBacktrack ? 0.75 : 0.25)));
          this.flushMainBuffer(h, Number.POSITIVE_INFINITY);
        }
      }
    }
  }
  abortCurrentFrag() {
    const t = this.fragCurrent;
    switch (this.fragCurrent = null, this.backtrackFragment = null, t && (t.abortRequests(), this.fragmentTracker.removeFragment(t)), this.state) {
      case w.KEY_LOADING:
      case w.FRAG_LOADING:
      case w.FRAG_LOADING_WAITING_RETRY:
      case w.PARSING:
      case w.PARSED:
        this.state = w.IDLE;
        break;
    }
    this.nextLoadPosition = this.getLoadPosition();
  }
  flushMainBuffer(t, e) {
    super.flushMainBuffer(t, e, this.altAudio === 2 ? "video" : null);
  }
  onMediaAttached(t, e) {
    super.onMediaAttached(t, e);
    const i = e.media;
    _t(i, "playing", this.onMediaPlaying), _t(i, "seeked", this.onMediaSeeked);
  }
  onMediaDetaching(t, e) {
    const {
      media: i
    } = this;
    i && (wt(i, "playing", this.onMediaPlaying), wt(i, "seeked", this.onMediaSeeked)), this.videoBuffer = null, this.fragPlaying = null, super.onMediaDetaching(t, e), !e.transferMedia && (this._hasEnoughToStart = !1);
  }
  onManifestLoading() {
    super.onManifestLoading(), this.log("Trigger BUFFER_RESET"), this.hls.trigger(m.BUFFER_RESET, void 0), this.couldBacktrack = !1, this.fragLastKbps = 0, this.fragPlaying = this.backtrackFragment = null, this.altAudio = 0, this.audioOnly = !1;
  }
  onManifestParsed(t, e) {
    let i = !1, s = !1;
    for (let r = 0; r < e.levels.length; r++) {
      const a = e.levels[r].audioCodec;
      a && (i = i || a.indexOf("mp4a.40.2") !== -1, s = s || a.indexOf("mp4a.40.5") !== -1);
    }
    this.audioCodecSwitch = i && s && !If(), this.audioCodecSwitch && this.log("Both AAC/HE-AAC audio found in levels; declaring level codec as HE-AAC"), this.levels = e.levels, this.startFragRequested = !1;
  }
  onLevelLoading(t, e) {
    const {
      levels: i
    } = this;
    if (!i || this.state !== w.IDLE)
      return;
    const s = e.levelInfo;
    (!s.details || s.details.live && (this.levelLastLoaded !== s || s.details.expired) || this.waitForCdnTuneIn(s.details)) && (this.state = w.WAITING_LEVEL);
  }
  onLevelLoaded(t, e) {
    var i;
    const {
      levels: s,
      startFragRequested: r
    } = this, a = e.level, o = e.details, c = o.totalduration;
    if (!s) {
      this.warn(`Levels were reset while loading level ${a}`);
      return;
    }
    this.log(`Level ${a} loaded [${o.startSN},${o.endSN}]${o.lastPartSn ? `[part-${o.lastPartSn}-${o.lastPartIndex}]` : ""}, cc [${o.startCC}, ${o.endCC}] duration:${c}`);
    const l = e.levelInfo, h = this.fragCurrent;
    h && (this.state === w.FRAG_LOADING || this.state === w.FRAG_LOADING_WAITING_RETRY) && h.level !== e.level && h.loader && this.abortCurrentFrag();
    let d = 0;
    if (o.live || (i = l.details) != null && i.live) {
      var u;
      if (this.checkLiveUpdate(o), o.deltaUpdateFailed)
        return;
      d = this.alignPlaylists(o, l.details, (u = this.levelLastLoaded) == null ? void 0 : u.details);
    }
    if (l.details = o, this.levelLastLoaded = l, r || this.setStartPosition(o, d), this.hls.trigger(m.LEVEL_UPDATED, {
      details: o,
      level: a
    }), this.state === w.WAITING_LEVEL) {
      if (this.waitForCdnTuneIn(o))
        return;
      this.state = w.IDLE;
    }
    r && o.live && this.synchronizeToLiveEdge(o), this.tick();
  }
  synchronizeToLiveEdge(t) {
    const {
      config: e,
      media: i
    } = this;
    if (!i)
      return;
    const s = this.hls.liveSyncPosition, r = this.getLoadPosition(), a = t.fragmentStart, o = t.edge, c = r >= a - e.maxFragLookUpTolerance && r <= o;
    if (s !== null && i.duration > s && (r < s || !c)) {
      const h = e.liveMaxLatencyDuration !== void 0 ? e.liveMaxLatencyDuration : e.liveMaxLatencyDurationCount * t.targetduration;
      if ((!c && i.readyState < 4 || r < o - h) && (this._hasEnoughToStart || (this.nextLoadPosition = s), i.readyState))
        if (this.warn(`Playback: ${r.toFixed(3)} is located too far from the end of live sliding playlist: ${o}, reset currentTime to : ${s.toFixed(3)}`), this.config.liveSyncMode === "buffered") {
          var l;
          const d = q.bufferInfo(i, s, 0);
          if (!((l = d.buffered) != null && l.length)) {
            i.currentTime = s;
            return;
          }
          if (d.start <= r) {
            i.currentTime = s;
            return;
          }
          const {
            nextStart: f
          } = q.bufferedInfo(d.buffered, r, 0);
          f && (i.currentTime = f);
        } else
          i.currentTime = s;
    }
  }
  _handleFragmentLoadProgress(t) {
    var e;
    const i = t.frag, {
      part: s,
      payload: r
    } = t, {
      levels: a
    } = this;
    if (!a) {
      this.warn(`Levels were reset while fragment load was in progress. Fragment ${i.sn} of level ${i.level} will not be buffered`);
      return;
    }
    const o = a[i.level];
    if (!o) {
      this.warn(`Level ${i.level} not found on progress`);
      return;
    }
    const c = o.details;
    if (!c) {
      this.warn(`Dropping fragment ${i.sn} of level ${i.level} after level details were reset`), this.fragmentTracker.removeFragment(i);
      return;
    }
    const l = o.videoCodec, h = c.PTSKnown || !c.live, d = (e = i.initSegment) == null ? void 0 : e.data, u = this._getAudioCodec(o), f = this.transmuxer = this.transmuxer || new To(this.hls, K.MAIN, this._handleTransmuxComplete.bind(this), this._handleTransmuxerFlush.bind(this)), g = s ? s.index : -1, v = g !== -1, p = new br(i.level, i.sn, i.stats.chunkCount, r.byteLength, g, v), y = this.initPTS[i.cc];
    f.push(r, d, u, l, i, s, c.totalduration, h, p, y);
  }
  onAudioTrackSwitching(t, e) {
    const i = this.hls, s = this.altAudio !== 0;
    if (ts(e.url, i))
      this.altAudio = 1;
    else {
      if (this.mediaBuffer !== this.media) {
        this.log("Switching on main audio, use media.buffered to schedule main fragment loading"), this.mediaBuffer = this.media;
        const a = this.fragCurrent;
        a && (this.log("Switching to main audio track, cancel main fragment load"), a.abortRequests(), this.fragmentTracker.removeFragment(a)), this.resetTransmuxer(), this.resetLoadingState();
      } else this.audioOnly && this.resetTransmuxer();
      if (s) {
        this.altAudio = 0, this.fragmentTracker.removeAllFragments(), i.once(m.BUFFER_FLUSHED, () => {
          this.hls && this.hls.trigger(m.AUDIO_TRACK_SWITCHED, e);
        }), i.trigger(m.BUFFER_FLUSHING, {
          startOffset: 0,
          endOffset: Number.POSITIVE_INFINITY,
          type: null
        });
        return;
      }
      i.trigger(m.AUDIO_TRACK_SWITCHED, e);
    }
  }
  onAudioTrackSwitched(t, e) {
    const i = ts(e.url, this.hls);
    if (i) {
      const s = this.videoBuffer;
      s && this.mediaBuffer !== s && (this.log("Switching on alternate audio, use video.buffered to schedule main fragment loading"), this.mediaBuffer = s);
    }
    this.altAudio = i ? 2 : 0, this.tick();
  }
  onBufferCreated(t, e) {
    const i = e.tracks;
    let s, r, a = !1;
    for (const o in i) {
      const c = i[o];
      if (c.id === "main") {
        if (r = o, s = c, o === "video") {
          const l = i[o];
          l && (this.videoBuffer = l.buffer);
        }
      } else
        a = !0;
    }
    a && s ? (this.log(`Alternate track found, use ${r}.buffered to schedule main fragment loading`), this.mediaBuffer = s.buffer) : this.mediaBuffer = this.media;
  }
  onFragBuffered(t, e) {
    const {
      frag: i,
      part: s
    } = e, r = i.type === K.MAIN;
    if (r) {
      if (this.fragContextChanged(i)) {
        this.warn(`Fragment ${i.sn}${s ? " p: " + s.index : ""} of level ${i.level} finished buffering, but was aborted. state: ${this.state}`), this.state === w.PARSED && (this.state = w.IDLE);
        return;
      }
      const o = s ? s.stats : i.stats;
      this.fragLastKbps = Math.round(8 * o.total / (o.buffering.end - o.loading.first)), ut(i) && (this.fragPrevious = i), this.fragBufferedComplete(i, s);
    }
    const a = this.media;
    a && (!this._hasEnoughToStart && q.getBuffered(a).length && (this._hasEnoughToStart = !0, this.seekToStartPos()), r && this.tick());
  }
  get hasEnoughToStart() {
    return this._hasEnoughToStart;
  }
  onError(t, e) {
    var i;
    if (e.fatal) {
      this.state = w.ERROR;
      return;
    }
    switch (e.details) {
      case L.FRAG_GAP:
      case L.FRAG_PARSING_ERROR:
      case L.FRAG_DECRYPT_ERROR:
      case L.FRAG_LOAD_ERROR:
      case L.FRAG_LOAD_TIMEOUT:
      case L.KEY_LOAD_ERROR:
      case L.KEY_LOAD_TIMEOUT:
        this.onFragmentOrKeyLoadError(K.MAIN, e);
        break;
      case L.LEVEL_LOAD_ERROR:
      case L.LEVEL_LOAD_TIMEOUT:
      case L.LEVEL_PARSING_ERROR:
        !e.levelRetry && this.state === w.WAITING_LEVEL && ((i = e.context) == null ? void 0 : i.type) === tt.LEVEL && (this.state = w.IDLE);
        break;
      case L.BUFFER_ADD_CODEC_ERROR:
      case L.BUFFER_APPEND_ERROR:
        if (e.parent !== "main")
          return;
        this.reduceLengthAndFlushBuffer(e) && this.resetLoadingState();
        break;
      case L.BUFFER_FULL_ERROR:
        if (e.parent !== "main")
          return;
        this.reduceLengthAndFlushBuffer(e) && (!this.config.interstitialsController && this.config.assetPlayerId ? this._hasEnoughToStart = !0 : this.flushMainBuffer(0, Number.POSITIVE_INFINITY));
        break;
      case L.INTERNAL_EXCEPTION:
        this.recoverWorkerError(e);
        break;
    }
  }
  onFragLoadEmergencyAborted() {
    this.state = w.IDLE, this._hasEnoughToStart || (this.startFragRequested = !1, this.nextLoadPosition = this.lastCurrentTime), this.tickImmediate();
  }
  onBufferFlushed(t, {
    type: e
  }) {
    if (e !== at.AUDIO || !this.altAudio) {
      const i = (e === at.VIDEO ? this.videoBuffer : this.mediaBuffer) || this.media;
      i && (this.afterBufferFlushed(i, e, K.MAIN), this.tick());
    }
  }
  onLevelsUpdated(t, e) {
    this.level > -1 && this.fragCurrent && (this.level = this.fragCurrent.level, this.level === -1 && this.resetWhenMissingContext(this.fragCurrent)), this.levels = e.levels;
  }
  swapAudioCodec() {
    this.audioCodecSwap = !this.audioCodecSwap;
  }
  /**
   * Seeks to the set startPosition if not equal to the mediaElement's current time.
   */
  seekToStartPos() {
    const {
      media: t
    } = this;
    if (!t)
      return;
    const e = t.currentTime;
    let i = this.startPosition;
    if (i >= 0 && e < i) {
      if (t.seeking) {
        this.log(`could not seek to ${i}, already seeking at ${e}`);
        return;
      }
      const s = this.timelineOffset;
      s && i && (i += s);
      const r = this.getLevelDetails(), a = q.getBuffered(t), o = a.length ? a.start(0) : 0, c = o - i, l = Math.max(this.config.maxBufferHole, this.config.maxFragLookUpTolerance);
      (this.config.startOnSegmentBoundary || c > 0 && (c < l || this.loadingParts && c < 2 * ((r == null ? void 0 : r.partTarget) || 0))) && (this.log(`adjusting start position by ${c} to match buffer start`), i += c, this.startPosition = i), e < i && (this.log(`seek to target start position ${i} from current time ${e} buffer start ${o}`), t.currentTime = i);
    }
  }
  _getAudioCodec(t) {
    let e = this.config.defaultAudioCodec || t.audioCodec;
    return this.audioCodecSwap && e && (this.log("Swapping audio codec"), e.indexOf("mp4a.40.5") !== -1 ? e = "mp4a.40.2" : e = "mp4a.40.5"), e;
  }
  _loadBitrateTestFrag(t, e) {
    t.bitrateTest = !0, this._doFragLoad(t, e).then((i) => {
      const {
        hls: s
      } = this, r = i == null ? void 0 : i.frag;
      if (!r || this.fragContextChanged(r))
        return;
      e.fragmentError = 0, this.state = w.IDLE, this.startFragRequested = !1, this.bitrateTest = !1;
      const a = r.stats;
      a.parsing.start = a.parsing.end = a.buffering.start = a.buffering.end = self.performance.now(), s.trigger(m.FRAG_LOADED, i), r.bitrateTest = !1;
    }).catch((i) => {
      this.state === w.STOPPED || this.state === w.ERROR || (this.warn(i), this.resetFragmentLoading(t));
    });
  }
  _handleTransmuxComplete(t) {
    const e = this.playlistType, {
      hls: i
    } = this, {
      remuxResult: s,
      chunkMeta: r
    } = t, a = this.getCurrentContext(r);
    if (!a) {
      this.resetWhenMissingContext(r);
      return;
    }
    const {
      frag: o,
      part: c,
      level: l
    } = a, {
      video: h,
      text: d,
      id3: u,
      initSegment: f
    } = s, {
      details: g
    } = l, v = this.altAudio ? void 0 : s.audio;
    if (this.fragContextChanged(o)) {
      this.fragmentTracker.removeFragment(o);
      return;
    }
    if (this.state = w.PARSING, f) {
      const p = f.tracks;
      if (p) {
        const S = o.initSegment || o;
        if (this.unhandledEncryptionError(f, o))
          return;
        this._bufferInitSegment(l, p, S, r), i.trigger(m.FRAG_PARSING_INIT_SEGMENT, {
          frag: S,
          id: e,
          tracks: p
        });
      }
      const y = f.initPTS, E = f.timescale, T = this.initPTS[o.cc];
      if (B(y) && (!T || T.baseTime !== y || T.timescale !== E)) {
        const S = f.trackId;
        this.initPTS[o.cc] = {
          baseTime: y,
          timescale: E,
          trackId: S
        }, i.trigger(m.INIT_PTS_FOUND, {
          frag: o,
          id: e,
          initPTS: y,
          timescale: E,
          trackId: S
        });
      }
    }
    if (h && g) {
      v && h.type === "audiovideo" && this.logMuxedErr(o);
      const p = g.fragments[o.sn - 1 - g.startSN], y = o.sn === g.startSN, E = !p || o.cc > p.cc;
      if (s.independent !== !1) {
        const {
          startPTS: T,
          endPTS: S,
          startDTS: x,
          endDTS: D
        } = h;
        if (c)
          c.elementaryStreams[h.type] = {
            startPTS: T,
            endPTS: S,
            startDTS: x,
            endDTS: D
          };
        else if (h.firstKeyFrame && h.independent && r.id === 1 && !E && (this.couldBacktrack = !0), h.dropped && h.independent) {
          const A = this.getMainFwdBufferInfo(), _ = (A ? A.end : this.getLoadPosition()) + this.config.maxBufferHole, R = h.firstKeyFramePTS ? h.firstKeyFramePTS : T;
          if (!y && _ < R - this.config.maxBufferHole && !E) {
            this.backtrack(o);
            return;
          } else E && (o.gap = !0);
          o.setElementaryStreamInfo(h.type, o.start, S, o.start, D, !0);
        } else y && T - (g.appliedTimelineOffset || 0) > ji && (o.gap = !0);
        o.setElementaryStreamInfo(h.type, T, S, x, D), this.backtrackFragment && (this.backtrackFragment = o), this.bufferFragmentData(h, o, c, r, y || E);
      } else if (y || E)
        o.gap = !0;
      else {
        this.backtrack(o);
        return;
      }
    }
    if (v) {
      const {
        startPTS: p,
        endPTS: y,
        startDTS: E,
        endDTS: T
      } = v;
      c && (c.elementaryStreams[at.AUDIO] = {
        startPTS: p,
        endPTS: y,
        startDTS: E,
        endDTS: T
      }), o.setElementaryStreamInfo(at.AUDIO, p, y, E, T), this.bufferFragmentData(v, o, c, r);
    }
    if (g && u != null && u.samples.length) {
      const p = {
        id: e,
        frag: o,
        details: g,
        samples: u.samples
      };
      i.trigger(m.FRAG_PARSING_METADATA, p);
    }
    if (g && d) {
      const p = {
        id: e,
        frag: o,
        details: g,
        samples: d.samples
      };
      i.trigger(m.FRAG_PARSING_USERDATA, p);
    }
  }
  logMuxedErr(t) {
    this.warn(`${ut(t) ? "Media" : "Init"} segment with muxed audiovideo where only video expected: ${t.url}`);
  }
  _bufferInitSegment(t, e, i, s) {
    if (this.state !== w.PARSING)
      return;
    this.audioOnly = !!e.audio && !e.video, this.altAudio && !this.audioOnly && (delete e.audio, e.audiovideo && this.logMuxedErr(i));
    const {
      audio: r,
      video: a,
      audiovideo: o
    } = e;
    if (r) {
      const l = t.audioCodec;
      let h = Gi(r.codec, l);
      h === "mp4a" && (h = "mp4a.40.5");
      const d = navigator.userAgent.toLowerCase();
      if (this.audioCodecSwitch) {
        h && (h.indexOf("mp4a.40.5") !== -1 ? h = "mp4a.40.2" : h = "mp4a.40.5");
        const u = r.metadata;
        u && "channelCount" in u && (u.channelCount || 1) !== 1 && d.indexOf("firefox") === -1 && (h = "mp4a.40.5");
      }
      h && h.indexOf("mp4a.40.5") !== -1 && d.indexOf("android") !== -1 && r.container !== "audio/mpeg" && (h = "mp4a.40.2", this.log(`Android: force audio codec to ${h}`)), l && l !== h && this.log(`Swapping manifest audio codec "${l}" for "${h}"`), r.levelCodec = h, r.id = K.MAIN, this.log(`Init audio buffer, container:${r.container}, codecs[selected/level/parsed]=[${h || ""}/${l || ""}/${r.codec}]`), delete e.audiovideo;
    }
    if (a) {
      a.levelCodec = t.videoCodec, a.id = K.MAIN;
      const l = a.codec;
      if ((l == null ? void 0 : l.length) === 4)
        switch (l) {
          case "hvc1":
          case "hev1":
            a.codec = "hvc1.1.6.L120.90";
            break;
          case "av01":
            a.codec = "av01.0.04M.08";
            break;
          case "avc1":
            a.codec = "avc1.42e01e";
            break;
        }
      this.log(`Init video buffer, container:${a.container}, codecs[level/parsed]=[${t.videoCodec || ""}/${l}]${a.codec !== l ? " parsed-corrected=" + a.codec : ""}${a.supplemental ? " supplemental=" + a.supplemental : ""}`), delete e.audiovideo;
    }
    o && (this.log(`Init audiovideo buffer, container:${o.container}, codecs[level/parsed]=[${t.codecs}/${o.codec}]`), delete e.video, delete e.audio);
    const c = Object.keys(e);
    if (c.length) {
      if (this.hls.trigger(m.BUFFER_CODECS, e), !this.hls)
        return;
      c.forEach((l) => {
        const d = e[l].initSegment;
        d != null && d.byteLength && this.hls.trigger(m.BUFFER_APPENDING, {
          type: l,
          data: d,
          frag: i,
          part: null,
          chunkMeta: s,
          parent: i.type
        });
      });
    }
    this.tickImmediate();
  }
  getMainFwdBufferInfo() {
    const t = this.mediaBuffer && this.altAudio === 2 ? this.mediaBuffer : this.media;
    return this.getFwdBufferInfo(t, K.MAIN);
  }
  get maxBufferLength() {
    const {
      levels: t,
      level: e
    } = this, i = t == null ? void 0 : t[e];
    return i ? this.getMaxBufferLength(i.maxBitrate) : this.config.maxBufferLength;
  }
  backtrack(t) {
    this.couldBacktrack = !0, this.backtrackFragment = t, this.resetTransmuxer(), this.flushBufferGap(t), this.fragmentTracker.removeFragment(t), this.fragPrevious = null, this.nextLoadPosition = t.start, this.state = w.IDLE;
  }
  checkFragmentChanged() {
    const t = this.media;
    let e = null;
    if (t && t.readyState > 1 && t.seeking === !1) {
      const i = t.currentTime;
      if (q.isBuffered(t, i) ? e = this.getAppendedFrag(i) : q.isBuffered(t, i + 0.1) && (e = this.getAppendedFrag(i + 0.1)), e) {
        this.backtrackFragment = null;
        const s = this.fragPlaying, r = e.level;
        (!s || e.sn !== s.sn || s.level !== r) && (this.fragPlaying = e, this.hls.trigger(m.FRAG_CHANGED, {
          frag: e
        }), (!s || s.level !== r) && this.hls.trigger(m.LEVEL_SWITCHED, {
          level: r
        }));
      }
    }
  }
  get nextLevel() {
    const t = this.nextBufferedFrag;
    return t ? t.level : -1;
  }
  get currentFrag() {
    var t;
    if (this.fragPlaying)
      return this.fragPlaying;
    const e = ((t = this.media) == null ? void 0 : t.currentTime) || this.lastCurrentTime;
    return B(e) ? this.getAppendedFrag(e) : null;
  }
  get currentProgramDateTime() {
    var t;
    const e = ((t = this.media) == null ? void 0 : t.currentTime) || this.lastCurrentTime;
    if (B(e)) {
      const i = this.getLevelDetails(), s = this.currentFrag || (i ? De(null, i.fragments, e) : null);
      if (s) {
        const r = s.programDateTime;
        if (r !== null) {
          const a = r + (e - s.start) * 1e3;
          return new Date(a);
        }
      }
    }
    return null;
  }
  get currentLevel() {
    const t = this.currentFrag;
    return t ? t.level : -1;
  }
  get nextBufferedFrag() {
    const t = this.currentFrag;
    return t ? this.followingBufferedFrag(t) : null;
  }
  get forceStartLoad() {
    return this._forceStartLoad;
  }
}
class _f extends Bt {
  constructor(t, e) {
    super("key-loader", e), this.config = void 0, this.keyIdToKeyInfo = {}, this.emeController = null, this.config = t;
  }
  abort(t) {
    for (const i in this.keyIdToKeyInfo) {
      const s = this.keyIdToKeyInfo[i].loader;
      if (s) {
        var e;
        if (t && t !== ((e = s.context) == null ? void 0 : e.frag.type))
          return;
        s.abort();
      }
    }
  }
  detach() {
    for (const t in this.keyIdToKeyInfo) {
      const e = this.keyIdToKeyInfo[t];
      (e.mediaKeySessionContext || e.decryptdata.isCommonEncryption) && delete this.keyIdToKeyInfo[t];
    }
  }
  destroy() {
    this.detach();
    for (const t in this.keyIdToKeyInfo) {
      const e = this.keyIdToKeyInfo[t].loader;
      e && e.destroy();
    }
    this.keyIdToKeyInfo = {};
  }
  createKeyLoadError(t, e = L.KEY_LOAD_ERROR, i, s, r) {
    return new se({
      type: Y.NETWORK_ERROR,
      details: e,
      fatal: !1,
      frag: t,
      response: r,
      error: i,
      networkDetails: s
    });
  }
  loadClear(t, e, i) {
    if (this.emeController && this.config.emeEnabled && !this.emeController.getSelectedKeySystemFormats().length) {
      if (e.length)
        for (let s = 0, r = e.length; s < r; s++) {
          const a = e[s];
          if (t.cc <= a.cc && (!ut(t) || !ut(a) || t.sn < a.sn) || !i && s == r - 1)
            return this.emeController.selectKeySystemFormat(a).then((o) => {
              if (!this.emeController)
                return;
              a.setKeyFormat(o);
              const c = Hi(o);
              if (c)
                return this.emeController.getKeySystemAccess([c]);
            });
        }
      if (this.config.requireKeySystemAccessOnStart) {
        const s = hi(this.config);
        if (s.length)
          return this.emeController.getKeySystemAccess(s);
      }
    }
    return null;
  }
  load(t) {
    return !t.decryptdata && t.encrypted && this.emeController && this.config.emeEnabled ? this.emeController.selectKeySystemFormat(t).then((e) => this.loadInternal(t, e)) : this.loadInternal(t);
  }
  loadInternal(t, e) {
    var i, s;
    e && t.setKeyFormat(e);
    const r = t.decryptdata;
    if (!r) {
      const l = new Error(e ? `Expected frag.decryptdata to be defined after setting format ${e}` : `Missing decryption data on fragment in onKeyLoading (emeEnabled with controller: ${this.emeController && this.config.emeEnabled})`);
      return Promise.reject(this.createKeyLoadError(t, L.KEY_LOAD_ERROR, l));
    }
    const a = r.uri;
    if (!a)
      return Promise.reject(this.createKeyLoadError(t, L.KEY_LOAD_ERROR, new Error(`Invalid key URI: "${a}"`)));
    const o = Ks(r);
    let c = this.keyIdToKeyInfo[o];
    if ((i = c) != null && i.decryptdata.key)
      return r.key = c.decryptdata.key, Promise.resolve({
        frag: t,
        keyInfo: c
      });
    if (this.emeController && (s = c) != null && s.keyLoadPromise)
      switch (this.emeController.getKeyStatus(c.decryptdata)) {
        case "usable":
        case "usable-in-future":
          return c.keyLoadPromise.then((h) => {
            const {
              keyInfo: d
            } = h;
            return r.key = d.decryptdata.key, {
              frag: t,
              keyInfo: d
            };
          });
      }
    switch (this.log(`${this.keyIdToKeyInfo[o] ? "Rel" : "L"}oading${r.keyId ? " keyId: " + At(r.keyId) : ""} URI: ${r.uri} from ${t.type} ${t.level}`), c = this.keyIdToKeyInfo[o] = {
      decryptdata: r,
      keyLoadPromise: null,
      loader: null,
      mediaKeySessionContext: null
    }, r.method) {
      case "SAMPLE-AES":
      case "SAMPLE-AES-CENC":
      case "SAMPLE-AES-CTR":
        return r.keyFormat === "identity" ? this.loadKeyHTTP(c, t) : this.loadKeyEME(c, t);
      case "AES-128":
      case "AES-256":
      case "AES-256-CTR":
        return this.loadKeyHTTP(c, t);
      default:
        return Promise.reject(this.createKeyLoadError(t, L.KEY_LOAD_ERROR, new Error(`Key supplied with unsupported METHOD: "${r.method}"`)));
    }
  }
  loadKeyEME(t, e) {
    const i = {
      frag: e,
      keyInfo: t
    };
    if (this.emeController && this.config.emeEnabled) {
      var s;
      if (!t.decryptdata.keyId && (s = e.initSegment) != null && s.data) {
        const a = Yl(e.initSegment.data);
        if (a.length) {
          let o = a[0];
          o.some((c) => c !== 0) ? (this.log(`Using keyId found in init segment ${At(o)}`), ue.setKeyIdForUri(t.decryptdata.uri, o)) : (o = ue.addKeyIdForUri(t.decryptdata.uri), this.log(`Generating keyId to patch media ${At(o)}`)), t.decryptdata.keyId = o;
        }
      }
      if (!t.decryptdata.keyId && !ut(e))
        return Promise.resolve(i);
      const r = this.emeController.loadKey(i);
      return (t.keyLoadPromise = r.then((a) => (t.mediaKeySessionContext = a, i))).catch((a) => {
        throw t.keyLoadPromise = null, "data" in a && (a.data.frag = e), a;
      });
    }
    return Promise.resolve(i);
  }
  loadKeyHTTP(t, e) {
    const i = this.config, s = i.loader, r = new s(i);
    return e.keyLoader = t.loader = r, t.keyLoadPromise = new Promise((a, o) => {
      const c = {
        keyInfo: t,
        frag: e,
        responseType: "arraybuffer",
        url: t.decryptdata.uri
      }, l = i.keyLoadPolicy.default, h = {
        loadPolicy: l,
        timeout: l.maxLoadTimeMs,
        maxRetry: 0,
        retryDelay: 0,
        maxRetryDelay: 0
      }, d = {
        onSuccess: (u, f, g, v) => {
          const {
            frag: p,
            keyInfo: y
          } = g, E = Ks(y.decryptdata);
          if (!p.decryptdata || y !== this.keyIdToKeyInfo[E])
            return o(this.createKeyLoadError(p, L.KEY_LOAD_ERROR, new Error("after key load, decryptdata unset or changed"), v));
          y.decryptdata.key = p.decryptdata.key = new Uint8Array(u.data), p.keyLoader = null, y.loader = null, a({
            frag: p,
            keyInfo: y
          });
        },
        onError: (u, f, g, v) => {
          this.resetLoader(f), o(this.createKeyLoadError(e, L.KEY_LOAD_ERROR, new Error(`HTTP Error ${u.code} loading key ${u.text}`), g, st({
            url: c.url,
            data: void 0
          }, u)));
        },
        onTimeout: (u, f, g) => {
          this.resetLoader(f), o(this.createKeyLoadError(e, L.KEY_LOAD_TIMEOUT, new Error("key loading timed out"), g));
        },
        onAbort: (u, f, g) => {
          this.resetLoader(f), o(this.createKeyLoadError(e, L.INTERNAL_ABORTED, new Error("key loading aborted"), g));
        }
      };
      r.load(c, h, d);
    });
  }
  resetLoader(t) {
    const {
      frag: e,
      keyInfo: i,
      url: s
    } = t, r = i.loader;
    e.keyLoader === r && (e.keyLoader = null, i.loader = null);
    const a = Ks(i.decryptdata) || s;
    delete this.keyIdToKeyInfo[a], r && r.destroy();
  }
}
function Ks(n) {
  if (n.keyFormat !== bt.FAIRPLAY) {
    const t = n.keyId;
    if (t)
      return At(t);
  }
  return n.uri;
}
function ha(n) {
  const {
    type: t
  } = n;
  switch (t) {
    case tt.AUDIO_TRACK:
      return K.AUDIO;
    case tt.SUBTITLE_TRACK:
      return K.SUBTITLE;
    default:
      return K.MAIN;
  }
}
function Hs(n, t) {
  let e = n.url;
  return (e === void 0 || e.indexOf("data:") === 0) && (e = t.url), e;
}
class Df {
  constructor(t) {
    this.hls = void 0, this.loaders = /* @__PURE__ */ Object.create(null), this.variableList = null, this.onManifestLoaded = this.checkAutostartLoad, this.hls = t, this.registerListeners();
  }
  startLoad(t) {
  }
  stopLoad() {
    this.destroyInternalLoaders();
  }
  registerListeners() {
    const {
      hls: t
    } = this;
    t.on(m.MANIFEST_LOADING, this.onManifestLoading, this), t.on(m.LEVEL_LOADING, this.onLevelLoading, this), t.on(m.AUDIO_TRACK_LOADING, this.onAudioTrackLoading, this), t.on(m.SUBTITLE_TRACK_LOADING, this.onSubtitleTrackLoading, this), t.on(m.LEVELS_UPDATED, this.onLevelsUpdated, this);
  }
  unregisterListeners() {
    const {
      hls: t
    } = this;
    t.off(m.MANIFEST_LOADING, this.onManifestLoading, this), t.off(m.LEVEL_LOADING, this.onLevelLoading, this), t.off(m.AUDIO_TRACK_LOADING, this.onAudioTrackLoading, this), t.off(m.SUBTITLE_TRACK_LOADING, this.onSubtitleTrackLoading, this), t.off(m.LEVELS_UPDATED, this.onLevelsUpdated, this);
  }
  /**
   * Returns defaults or configured loader-type overloads (pLoader and loader config params)
   */
  createInternalLoader(t) {
    const e = this.hls.config, i = e.pLoader, s = e.loader, r = i || s, a = new r(e);
    return this.loaders[t.type] = a, a;
  }
  getInternalLoader(t) {
    return this.loaders[t.type];
  }
  resetInternalLoader(t) {
    this.loaders[t] && delete this.loaders[t];
  }
  /**
   * Call `destroy` on all internal loader instances mapped (one per context type)
   */
  destroyInternalLoaders() {
    for (const t in this.loaders) {
      const e = this.loaders[t];
      e && e.destroy(), this.resetInternalLoader(t);
    }
  }
  destroy() {
    this.variableList = null, this.unregisterListeners(), this.destroyInternalLoaders();
  }
  onManifestLoading(t, e) {
    const {
      url: i
    } = e;
    this.variableList = null, this.load({
      id: null,
      level: 0,
      responseType: "text",
      type: tt.MANIFEST,
      url: i,
      deliveryDirectives: null,
      levelOrTrack: null
    });
  }
  onLevelLoading(t, e) {
    const {
      id: i,
      level: s,
      pathwayId: r,
      url: a,
      deliveryDirectives: o,
      levelInfo: c
    } = e;
    this.load({
      id: i,
      level: s,
      pathwayId: r,
      responseType: "text",
      type: tt.LEVEL,
      url: a,
      deliveryDirectives: o,
      levelOrTrack: c
    });
  }
  onAudioTrackLoading(t, e) {
    const {
      id: i,
      groupId: s,
      url: r,
      deliveryDirectives: a,
      track: o
    } = e;
    this.load({
      id: i,
      groupId: s,
      level: null,
      responseType: "text",
      type: tt.AUDIO_TRACK,
      url: r,
      deliveryDirectives: a,
      levelOrTrack: o
    });
  }
  onSubtitleTrackLoading(t, e) {
    const {
      id: i,
      groupId: s,
      url: r,
      deliveryDirectives: a,
      track: o
    } = e;
    this.load({
      id: i,
      groupId: s,
      level: null,
      responseType: "text",
      type: tt.SUBTITLE_TRACK,
      url: r,
      deliveryDirectives: a,
      levelOrTrack: o
    });
  }
  onLevelsUpdated(t, e) {
    const i = this.loaders[tt.LEVEL];
    if (i) {
      const s = i.context;
      s && !e.levels.some((r) => r === s.levelOrTrack) && (i.abort(), delete this.loaders[tt.LEVEL]);
    }
  }
  load(t) {
    var e;
    const i = this.hls.config;
    let s = this.getInternalLoader(t);
    if (s) {
      const l = this.hls.logger, h = s.context;
      if (h && h.levelOrTrack === t.levelOrTrack && (h.url === t.url || h.deliveryDirectives && !t.deliveryDirectives)) {
        h.url === t.url ? l.log(`[playlist-loader]: ignore ${t.url} ongoing request`) : l.log(`[playlist-loader]: ignore ${t.url} in favor of ${h.url}`);
        return;
      }
      l.log(`[playlist-loader]: aborting previous loader for type: ${t.type}`), s.abort();
    }
    let r;
    if (t.type === tt.MANIFEST ? r = i.manifestLoadPolicy.default : r = nt({}, i.playlistLoadPolicy.default, {
      timeoutRetry: null,
      errorRetry: null
    }), s = this.createInternalLoader(t), B((e = t.deliveryDirectives) == null ? void 0 : e.part)) {
      let l;
      if (t.type === tt.LEVEL && t.level !== null ? l = this.hls.levels[t.level].details : t.type === tt.AUDIO_TRACK && t.id !== null ? l = this.hls.audioTracks[t.id].details : t.type === tt.SUBTITLE_TRACK && t.id !== null && (l = this.hls.subtitleTracks[t.id].details), l) {
        const h = l.partTarget, d = l.targetduration;
        if (h && d) {
          const u = Math.max(h * 3, d * 0.8) * 1e3;
          r = nt({}, r, {
            maxTimeToFirstByteMs: Math.min(u, r.maxTimeToFirstByteMs),
            maxLoadTimeMs: Math.min(u, r.maxTimeToFirstByteMs)
          });
        }
      }
    }
    const a = r.errorRetry || r.timeoutRetry || {}, o = {
      loadPolicy: r,
      timeout: r.maxLoadTimeMs,
      maxRetry: a.maxNumRetry || 0,
      retryDelay: a.retryDelayMs || 0,
      maxRetryDelay: a.maxRetryDelayMs || 0
    }, c = {
      onSuccess: (l, h, d, u) => {
        const f = this.getInternalLoader(d);
        this.resetInternalLoader(d.type);
        const g = l.data;
        h.parsing.start = performance.now(), Qt.isMediaPlaylist(g) || d.type !== tt.MANIFEST ? this.handleTrackOrLevelPlaylist(l, h, d, u || null, f) : this.handleMasterPlaylist(l, h, d, u);
      },
      onError: (l, h, d, u) => {
        this.handleNetworkError(h, d, !1, l, u);
      },
      onTimeout: (l, h, d) => {
        this.handleNetworkError(h, d, !0, void 0, l);
      }
    };
    s.load(t, o, c);
  }
  checkAutostartLoad() {
    if (!this.hls)
      return;
    const {
      config: {
        autoStartLoad: t,
        startPosition: e
      },
      forceStartLoad: i
    } = this.hls;
    (t || i) && (this.hls.logger.log(`${t ? "auto" : "force"} startLoad with configured startPosition ${e}`), this.hls.startLoad(e));
  }
  handleMasterPlaylist(t, e, i, s) {
    const r = this.hls, a = t.data, o = Hs(t, i), c = Qt.parseMasterPlaylist(a, o);
    if (c.playlistParsingError) {
      e.parsing.end = performance.now(), this.handleManifestParsingError(t, i, c.playlistParsingError, s, e);
      return;
    }
    const {
      contentSteering: l,
      levels: h,
      sessionData: d,
      sessionKeys: u,
      startTimeOffset: f,
      variableList: g
    } = c;
    this.variableList = g, h.forEach((E) => {
      const {
        unknownCodecs: T
      } = E;
      if (T) {
        const {
          preferManagedMediaSource: S
        } = this.hls.config;
        let {
          audioCodec: x,
          videoCodec: D
        } = E;
        for (let A = T.length; A--; ) {
          const _ = T[A];
          gi(_, "audio", S) ? (E.audioCodec = x = x ? `${x},${_}` : _, Xe.audio[x.substring(0, 4)] = 2, T.splice(A, 1)) : gi(_, "video", S) && (E.videoCodec = D = D ? `${D},${_}` : _, Xe.video[D.substring(0, 4)] = 2, T.splice(A, 1));
        }
      }
    });
    const {
      AUDIO: v = [],
      SUBTITLES: p,
      "CLOSED-CAPTIONS": y
    } = Qt.parseMasterPlaylistMedia(a, o, c);
    v.length && !v.some((T) => !T.url) && h[0].audioCodec && !h[0].attrs.AUDIO && (this.hls.logger.log("[playlist-loader]: audio codec signaled in quality level, but no embedded audio track signaled, create one"), v.unshift({
      type: "main",
      name: "main",
      groupId: "main",
      default: !1,
      autoselect: !1,
      forced: !1,
      id: -1,
      attrs: new lt({}),
      bitrate: 0,
      url: ""
    })), r.trigger(m.MANIFEST_LOADED, {
      levels: h,
      audioTracks: v,
      subtitles: p,
      captions: y,
      contentSteering: l,
      url: o,
      stats: e,
      networkDetails: s,
      sessionData: d,
      sessionKeys: u,
      startTimeOffset: f,
      variableList: g
    });
  }
  handleTrackOrLevelPlaylist(t, e, i, s, r) {
    const a = this.hls, {
      id: o,
      level: c,
      type: l
    } = i, h = Hs(t, i), d = B(c) ? c : B(o) ? o : 0, u = ha(i), f = Qt.parseLevelPlaylist(t.data, h, d, u, 0, this.variableList);
    if (l === tt.MANIFEST) {
      const g = {
        attrs: new lt({}),
        bitrate: 0,
        details: f,
        name: "",
        url: h
      };
      f.requestScheduled = e.loading.start + ja(f, 0), a.trigger(m.MANIFEST_LOADED, {
        levels: [g],
        audioTracks: [],
        url: h,
        stats: e,
        networkDetails: s,
        sessionData: null,
        sessionKeys: null,
        contentSteering: null,
        startTimeOffset: null,
        variableList: null
      });
    }
    e.parsing.end = performance.now(), i.levelDetails = f, this.handlePlaylistLoaded(f, t, e, i, s, r);
  }
  handleManifestParsingError(t, e, i, s, r) {
    this.hls.trigger(m.ERROR, {
      type: Y.NETWORK_ERROR,
      details: L.MANIFEST_PARSING_ERROR,
      fatal: e.type === tt.MANIFEST,
      url: t.url,
      err: i,
      error: i,
      reason: i.message,
      response: t,
      context: e,
      networkDetails: s,
      stats: r
    });
  }
  handleNetworkError(t, e, i = !1, s, r) {
    let a = `A network ${i ? "timeout" : "error" + (s ? " (status " + s.code + ")" : "")} occurred while loading ${t.type}`;
    t.type === tt.LEVEL ? a += `: ${t.level} id: ${t.id}` : (t.type === tt.AUDIO_TRACK || t.type === tt.SUBTITLE_TRACK) && (a += ` id: ${t.id} group-id: "${t.groupId}"`);
    const o = new Error(a);
    this.hls.logger.warn(`[playlist-loader]: ${a}`);
    let c = L.UNKNOWN, l = !1;
    const h = this.getInternalLoader(t);
    switch (t.type) {
      case tt.MANIFEST:
        c = i ? L.MANIFEST_LOAD_TIMEOUT : L.MANIFEST_LOAD_ERROR, l = !0;
        break;
      case tt.LEVEL:
        c = i ? L.LEVEL_LOAD_TIMEOUT : L.LEVEL_LOAD_ERROR, l = !1;
        break;
      case tt.AUDIO_TRACK:
        c = i ? L.AUDIO_TRACK_LOAD_TIMEOUT : L.AUDIO_TRACK_LOAD_ERROR, l = !1;
        break;
      case tt.SUBTITLE_TRACK:
        c = i ? L.SUBTITLE_TRACK_LOAD_TIMEOUT : L.SUBTITLE_LOAD_ERROR, l = !1;
        break;
    }
    h && this.resetInternalLoader(t.type);
    const d = {
      type: Y.NETWORK_ERROR,
      details: c,
      fatal: l,
      url: t.url,
      loader: h,
      context: t,
      error: o,
      networkDetails: e,
      stats: r
    };
    if (s) {
      const u = (e == null ? void 0 : e.url) || t.url;
      d.response = st({
        url: u,
        data: void 0
      }, s);
    }
    this.hls.trigger(m.ERROR, d);
  }
  handlePlaylistLoaded(t, e, i, s, r, a) {
    const o = this.hls, {
      type: c,
      level: l,
      levelOrTrack: h,
      id: d,
      groupId: u,
      deliveryDirectives: f
    } = s, g = Hs(e, s), v = ha(s);
    let p = typeof s.level == "number" && v === K.MAIN ? l : void 0;
    const y = t.playlistParsingError;
    if (y) {
      if (this.hls.logger.warn(`${y} ${t.url}`), !o.config.ignorePlaylistParsingErrors) {
        o.trigger(m.ERROR, {
          type: Y.NETWORK_ERROR,
          details: L.LEVEL_PARSING_ERROR,
          fatal: !1,
          url: g,
          error: y,
          reason: y.message,
          response: e,
          context: s,
          level: p,
          parent: v,
          networkDetails: r,
          stats: i
        });
        return;
      }
      t.playlistParsingError = null;
    }
    if (!t.fragments.length) {
      const E = t.playlistParsingError = new Error("No Segments found in Playlist");
      o.trigger(m.ERROR, {
        type: Y.NETWORK_ERROR,
        details: L.LEVEL_EMPTY_ERROR,
        fatal: !1,
        url: g,
        error: E,
        reason: E.message,
        response: e,
        context: s,
        level: p,
        parent: v,
        networkDetails: r,
        stats: i
      });
      return;
    }
    switch (t.live && a && (a.getCacheAge && (t.ageHeader = a.getCacheAge() || 0), (!a.getCacheAge || isNaN(t.ageHeader)) && (t.ageHeader = 0)), c) {
      case tt.MANIFEST:
      case tt.LEVEL:
        if (p) {
          if (!h)
            p = 0;
          else if (h !== o.levels[p]) {
            const E = o.levels.indexOf(h);
            E > -1 && (p = E);
          }
        }
        o.trigger(m.LEVEL_LOADED, {
          details: t,
          levelInfo: h || o.levels[0],
          level: p || 0,
          id: d || 0,
          stats: i,
          networkDetails: r,
          deliveryDirectives: f,
          withoutMultiVariant: c === tt.MANIFEST
        });
        break;
      case tt.AUDIO_TRACK:
        o.trigger(m.AUDIO_TRACK_LOADED, {
          details: t,
          track: h,
          id: d || 0,
          groupId: u || "",
          stats: i,
          networkDetails: r,
          deliveryDirectives: f
        });
        break;
      case tt.SUBTITLE_TRACK:
        o.trigger(m.SUBTITLE_TRACK_LOADED, {
          details: t,
          track: h,
          id: d || 0,
          groupId: u || "",
          stats: i,
          networkDetails: r,
          deliveryDirectives: f
        });
        break;
    }
  }
}
class de {
  /**
   * Get the video-dev/hls.js package version.
   */
  static get version() {
    return vi;
  }
  /**
   * Check if the required MediaSource Extensions are available.
   */
  static isMSESupported() {
    return jo();
  }
  /**
   * Check if MediaSource Extensions are available and isTypeSupported checks pass for any baseline codecs.
   */
  static isSupported() {
    return bf();
  }
  /**
   * Get the MediaSource global used for MSE playback (ManagedMediaSource, MediaSource, or WebKitMediaSource).
   */
  static getMediaSource() {
    return ge();
  }
  static get Events() {
    return m;
  }
  static get MetadataSchema() {
    return Mt;
  }
  static get ErrorTypes() {
    return Y;
  }
  static get ErrorDetails() {
    return L;
  }
  /**
   * Get the default configuration applied to new instances.
   */
  static get DefaultConfig() {
    return de.defaultConfig ? de.defaultConfig : uf;
  }
  /**
   * Replace the default configuration applied to new instances.
   */
  static set DefaultConfig(t) {
    de.defaultConfig = t;
  }
  /**
   * Creates an instance of an HLS client that can attach to exactly one `HTMLMediaElement`.
   * @param userConfig - Configuration options applied over `Hls.DefaultConfig`
   */
  constructor(t = {}) {
    this.config = void 0, this.userConfig = void 0, this.logger = void 0, this.coreComponents = void 0, this.networkControllers = void 0, this._emitter = new _r(), this._autoLevelCapping = -1, this._maxHdcpLevel = null, this.abrController = void 0, this.bufferController = void 0, this.capLevelController = void 0, this.latencyController = void 0, this.levelController = void 0, this.streamController = void 0, this.audioStreamController = void 0, this.subtititleStreamController = void 0, this.audioTrackController = void 0, this.subtitleTrackController = void 0, this.interstitialsController = void 0, this.gapController = void 0, this.emeController = void 0, this.cmcdController = void 0, this._media = null, this._url = null, this._sessionId = void 0, this.triggeringException = void 0, this.started = !1;
    const e = this.logger = Ol(t.debug || !1, "Hls instance", t.assetPlayerId), i = this.config = gf(de.DefaultConfig, t, e);
    this.userConfig = t, i.progressive && mf(i, e);
    const {
      abrController: s,
      bufferController: r,
      capLevelController: a,
      errorController: o,
      fpsController: c
    } = i, l = new o(this), h = this.abrController = new s(this), d = new Dc(this), u = i.interstitialsController, f = u ? this.interstitialsController = new u(this, de) : null, g = this.bufferController = new r(this, d), v = this.capLevelController = new a(this), p = new c(this), y = new Df(this), E = i.contentSteeringController, T = E ? new E(this) : null, S = this.levelController = new Af(this, T), x = new Sf(this), D = new _f(this.config, this.logger), A = this.streamController = new Rf(this, d, D), _ = this.gapController = new Ef(this, d);
    v.setStreamController(A), p.setStreamController(A);
    const R = [y, S, A];
    f && R.splice(1, 0, f), T && R.splice(1, 0, T), this.networkControllers = R;
    const b = [h, g, _, v, p, x, d];
    this.audioTrackController = this.createController(i.audioTrackController, R);
    const C = i.audioStreamController;
    C && R.push(this.audioStreamController = new C(this, d, D)), this.subtitleTrackController = this.createController(i.subtitleTrackController, R);
    const F = i.subtitleStreamController;
    F && R.push(this.subtititleStreamController = new F(this, d, D)), this.createController(i.timelineController, b), D.emeController = this.emeController = this.createController(i.emeController, b), this.cmcdController = this.createController(i.cmcdController, b), this.latencyController = this.createController(xf, b), this.coreComponents = b, R.push(l);
    const U = l.onErrorOut;
    typeof U == "function" && this.on(m.ERROR, U, l), this.on(m.MANIFEST_LOADED, y.onManifestLoaded, y);
  }
  createController(t, e) {
    if (t) {
      const i = new t(this);
      return e && e.push(i), i;
    }
    return null;
  }
  // Delegate the EventEmitter through the public API of Hls.js
  on(t, e, i = this) {
    this._emitter.on(t, e, i);
  }
  once(t, e, i = this) {
    this._emitter.once(t, e, i);
  }
  removeAllListeners(t) {
    this._emitter.removeAllListeners(t);
  }
  off(t, e, i = this, s) {
    this._emitter.off(t, e, i, s);
  }
  listeners(t) {
    return this._emitter.listeners(t);
  }
  emit(t, e, i) {
    return this._emitter.emit(t, e, i);
  }
  trigger(t, e) {
    if (this.config.debug)
      return this.emit(t, t, e);
    try {
      return this.emit(t, t, e);
    } catch (i) {
      if (this.logger.error("An internal error happened while handling event " + t + '. Error message: "' + i.message + '". Here is a stacktrace:', i), !this.triggeringException) {
        this.triggeringException = !0;
        const s = t === m.ERROR;
        this.trigger(m.ERROR, {
          type: Y.OTHER_ERROR,
          details: L.INTERNAL_EXCEPTION,
          fatal: s,
          event: t,
          error: i
        }), this.triggeringException = !1;
      }
    }
    return !1;
  }
  listenerCount(t) {
    return this._emitter.listenerCount(t);
  }
  /**
   * Dispose of the instance
   */
  destroy() {
    this.logger.log("destroy"), this.trigger(m.DESTROYING, void 0), this.detachMedia(), this.removeAllListeners(), this._autoLevelCapping = -1, this._url = null, this.networkControllers.forEach((e) => e.destroy()), this.networkControllers.length = 0, this.coreComponents.forEach((e) => e.destroy()), this.coreComponents.length = 0;
    const t = this.config;
    t.xhrSetup = t.fetchSetup = void 0, this.userConfig = null;
  }
  /**
   * Attaches Hls.js to a media element
   */
  attachMedia(t) {
    if (!t || "media" in t && !t.media) {
      const r = new Error(`attachMedia failed: invalid argument (${t})`);
      this.trigger(m.ERROR, {
        type: Y.OTHER_ERROR,
        details: L.ATTACH_MEDIA_ERROR,
        fatal: !0,
        error: r
      });
      return;
    }
    this.logger.log("attachMedia"), this._media && (this.logger.warn("media must be detached before attaching"), this.detachMedia());
    const e = "media" in t, i = e ? t.media : t, s = e ? t : {
      media: i
    };
    this._media = i, this.trigger(m.MEDIA_ATTACHING, s);
  }
  /**
   * Detach Hls.js from the media
   */
  detachMedia() {
    this.logger.log("detachMedia"), this.trigger(m.MEDIA_DETACHING, {}), this._media = null;
  }
  /**
   * Detach HTMLMediaElement, MediaSource, and SourceBuffers without reset, for attaching to another instance
   */
  transferMedia() {
    this._media = null;
    const t = this.bufferController.transferMedia();
    return this.trigger(m.MEDIA_DETACHING, {
      transferMedia: t
    }), t;
  }
  /**
   * Set the source URL. Can be relative or absolute.
   */
  loadSource(t) {
    this.stopLoad();
    const e = this.media, i = this._url, s = this._url = vr.buildAbsoluteURL(self.location.href, t, {
      alwaysNormalize: !0
    });
    this._autoLevelCapping = -1, this._maxHdcpLevel = null, this.logger.log(`loadSource:${s}`), e && i && (i !== s || this.bufferController.hasSourceTypes()) && (this.detachMedia(), this.attachMedia(e)), this.trigger(m.MANIFEST_LOADING, {
      url: t
    });
  }
  /**
   * Gets the currently loaded URL
   */
  get url() {
    return this._url;
  }
  /**
   * Whether or not enough has been buffered to seek to start position or use `media.currentTime` to determine next load position
   */
  get hasEnoughToStart() {
    return this.streamController.hasEnoughToStart;
  }
  /**
   * Get the startPosition set on startLoad(position) or on autostart with config.startPosition
   */
  get startPosition() {
    return this.streamController.startPositionValue;
  }
  /**
   * Start loading data from the stream source.
   * Depending on default config, client starts loading automatically when a source is set.
   *
   * @param startPosition - Set the start position to stream from.
   * Defaults to -1 (None: starts from earliest point)
   */
  startLoad(t = -1, e) {
    this.logger.log(`startLoad(${t + (e ? ", <skip seek to start>" : "")})`), this.started = !0, this.resumeBuffering();
    for (let i = 0; i < this.networkControllers.length && (this.networkControllers[i].startLoad(t, e), !(!this.started || !this.networkControllers)); i++)
      ;
  }
  /**
   * Stop loading of any stream data.
   */
  stopLoad() {
    this.logger.log("stopLoad"), this.started = !1;
    for (let t = 0; t < this.networkControllers.length && (this.networkControllers[t].stopLoad(), !(this.started || !this.networkControllers)); t++)
      ;
  }
  /**
   * Returns whether loading, toggled with `startLoad()` and `stopLoad()`, is active or not`.
   */
  get loadingEnabled() {
    return this.started;
  }
  /**
   * Returns state of fragment loading toggled by calling `pauseBuffering()` and `resumeBuffering()`.
   */
  get bufferingEnabled() {
    return this.streamController.bufferingEnabled;
  }
  /**
   * Resumes stream controller segment loading after `pauseBuffering` has been called.
   */
  resumeBuffering() {
    this.bufferingEnabled || (this.logger.log("resume buffering"), this.networkControllers.forEach((t) => {
      t.resumeBuffering && t.resumeBuffering();
    }));
  }
  /**
   * Prevents stream controller from loading new segments until `resumeBuffering` is called.
   * This allows for media buffering to be paused without interupting playlist loading.
   */
  pauseBuffering() {
    this.bufferingEnabled && (this.logger.log("pause buffering"), this.networkControllers.forEach((t) => {
      t.pauseBuffering && t.pauseBuffering();
    }));
  }
  get inFlightFragments() {
    const t = {
      [K.MAIN]: this.streamController.inFlightFrag
    };
    return this.audioStreamController && (t[K.AUDIO] = this.audioStreamController.inFlightFrag), this.subtititleStreamController && (t[K.SUBTITLE] = this.subtititleStreamController.inFlightFrag), t;
  }
  /**
   * Swap through possible audio codecs in the stream (for example to switch from stereo to 5.1)
   */
  swapAudioCodec() {
    this.logger.log("swapAudioCodec"), this.streamController.swapAudioCodec();
  }
  /**
   * When the media-element fails, this allows to detach and then re-attach it
   * as one call (convenience method).
   *
   * Automatic recovery of media-errors by this process is configurable.
   */
  recoverMediaError() {
    this.logger.log("recoverMediaError");
    const t = this._media, e = t == null ? void 0 : t.currentTime;
    this.detachMedia(), t && (this.attachMedia(t), e && this.startLoad(e));
  }
  removeLevel(t) {
    this.levelController.removeLevel(t);
  }
  /**
   * @returns a UUID for this player instance
   */
  get sessionId() {
    let t = this._sessionId;
    return t || (t = this._sessionId = yu()), t;
  }
  /**
   * @returns an array of levels (variants) sorted by HDCP-LEVEL, RESOLUTION (height), FRAME-RATE, CODECS, VIDEO-RANGE, and BANDWIDTH
   */
  get levels() {
    const t = this.levelController.levels;
    return t || [];
  }
  /**
   * @returns LevelDetails of last loaded level (variant) or `null` prior to loading a media playlist.
   */
  get latestLevelDetails() {
    return this.streamController.getLevelDetails() || null;
  }
  /**
   * @returns Level object of selected level (variant) or `null` prior to selecting a level or once the level is removed.
   */
  get loadLevelObj() {
    return this.levelController.loadLevelObj;
  }
  /**
   * Index of quality level (variant) currently played
   */
  get currentLevel() {
    return this.streamController.currentLevel;
  }
  /**
   * Set quality level index immediately. This will flush the current buffer to replace the quality asap. That means playback will interrupt at least shortly to re-buffer and re-sync eventually. Set to -1 for automatic level selection.
   */
  set currentLevel(t) {
    this.logger.log(`set currentLevel:${t}`), this.levelController.manualLevel = t, this.streamController.immediateLevelSwitch();
  }
  /**
   * Index of next quality level loaded as scheduled by stream controller.
   */
  get nextLevel() {
    return this.streamController.nextLevel;
  }
  /**
   * Set quality level index for next loaded data.
   * This will switch the video quality asap, without interrupting playback.
   * May abort current loading of data, and flush parts of buffer (outside currently played fragment region).
   * @param newLevel - Pass -1 for automatic level selection
   */
  set nextLevel(t) {
    this.logger.log(`set nextLevel:${t}`), this.levelController.manualLevel = t, this.streamController.nextLevelSwitch();
  }
  /**
   * Return the quality level of the currently or last (of none is loaded currently) segment
   */
  get loadLevel() {
    return this.levelController.level;
  }
  /**
   * Set quality level index for next loaded data in a conservative way.
   * This will switch the quality without flushing, but interrupt current loading.
   * Thus the moment when the quality switch will appear in effect will only be after the already existing buffer.
   * @param newLevel - Pass -1 for automatic level selection
   */
  set loadLevel(t) {
    this.logger.log(`set loadLevel:${t}`), this.levelController.manualLevel = t;
  }
  /**
   * get next quality level loaded
   */
  get nextLoadLevel() {
    return this.levelController.nextLoadLevel;
  }
  /**
   * Set quality level of next loaded segment in a fully "non-destructive" way.
   * Same as `loadLevel` but will wait for next switch (until current loading is done).
   */
  set nextLoadLevel(t) {
    this.levelController.nextLoadLevel = t;
  }
  /**
   * Return "first level": like a default level, if not set,
   * falls back to index of first level referenced in manifest
   */
  get firstLevel() {
    return Math.max(this.levelController.firstLevel, this.minAutoLevel);
  }
  /**
   * Sets "first-level", see getter.
   */
  set firstLevel(t) {
    this.logger.log(`set firstLevel:${t}`), this.levelController.firstLevel = t;
  }
  /**
   * Return the desired start level for the first fragment that will be loaded.
   * The default value of -1 indicates automatic start level selection.
   * Setting hls.nextAutoLevel without setting a startLevel will result in
   * the nextAutoLevel value being used for one fragment load.
   */
  get startLevel() {
    const t = this.levelController.startLevel;
    return t === -1 && this.abrController.forcedAutoLevel > -1 ? this.abrController.forcedAutoLevel : t;
  }
  /**
   * set  start level (level of first fragment that will be played back)
   * if not overrided by user, first level appearing in manifest will be used as start level
   * if -1 : automatic start level selection, playback will start from level matching download bandwidth
   * (determined from download of first segment)
   */
  set startLevel(t) {
    this.logger.log(`set startLevel:${t}`), t !== -1 && (t = Math.max(t, this.minAutoLevel)), this.levelController.startLevel = t;
  }
  /**
   * Whether level capping is enabled.
   * Default value is set via `config.capLevelToPlayerSize`.
   */
  get capLevelToPlayerSize() {
    return this.config.capLevelToPlayerSize;
  }
  /**
   * Enables or disables level capping. If disabled after previously enabled, `nextLevelSwitch` will be immediately called.
   */
  set capLevelToPlayerSize(t) {
    const e = !!t;
    e !== this.config.capLevelToPlayerSize && (e ? this.capLevelController.startCapping() : (this.capLevelController.stopCapping(), this.autoLevelCapping = -1, this.streamController.nextLevelSwitch()), this.config.capLevelToPlayerSize = e);
  }
  /**
   * Capping/max level value that should be used by automatic level selection algorithm (`ABRController`)
   */
  get autoLevelCapping() {
    return this._autoLevelCapping;
  }
  /**
   * Returns the current bandwidth estimate in bits per second, when available. Otherwise, `NaN` is returned.
   */
  get bandwidthEstimate() {
    const {
      bwEstimator: t
    } = this.abrController;
    return t ? t.getEstimate() : NaN;
  }
  set bandwidthEstimate(t) {
    this.abrController.resetEstimator(t);
  }
  get abrEwmaDefaultEstimate() {
    const {
      bwEstimator: t
    } = this.abrController;
    return t ? t.defaultEstimate : NaN;
  }
  /**
   * get time to first byte estimate
   * @type {number}
   */
  get ttfbEstimate() {
    const {
      bwEstimator: t
    } = this.abrController;
    return t ? t.getEstimateTTFB() : NaN;
  }
  /**
   * Capping/max level value that should be used by automatic level selection algorithm (`ABRController`)
   */
  set autoLevelCapping(t) {
    this._autoLevelCapping !== t && (this.logger.log(`set autoLevelCapping:${t}`), this._autoLevelCapping = t, this.levelController.checkMaxAutoUpdated());
  }
  get maxHdcpLevel() {
    return this._maxHdcpLevel;
  }
  set maxHdcpLevel(t) {
    fc(t) && this._maxHdcpLevel !== t && (this._maxHdcpLevel = t, this.levelController.checkMaxAutoUpdated());
  }
  /**
   * True when automatic level selection enabled
   */
  get autoLevelEnabled() {
    return this.levelController.manualLevel === -1;
  }
  /**
   * Level set manually (if any)
   */
  get manualLevel() {
    return this.levelController.manualLevel;
  }
  /**
   * min level selectable in auto mode according to config.minAutoBitrate
   */
  get minAutoLevel() {
    const {
      levels: t,
      config: {
        minAutoBitrate: e
      }
    } = this;
    if (!t) return 0;
    const i = t.length;
    for (let s = 0; s < i; s++)
      if (t[s].maxBitrate >= e)
        return s;
    return 0;
  }
  /**
   * max level selectable in auto mode according to autoLevelCapping
   */
  get maxAutoLevel() {
    const {
      levels: t,
      autoLevelCapping: e,
      maxHdcpLevel: i
    } = this;
    let s;
    if (e === -1 && t != null && t.length ? s = t.length - 1 : s = e, i)
      for (let r = s; r--; ) {
        const a = t[r].attrs["HDCP-LEVEL"];
        if (a && a <= i)
          return r;
      }
    return s;
  }
  get firstAutoLevel() {
    return this.abrController.firstAutoLevel;
  }
  /**
   * next automatically selected quality level
   */
  get nextAutoLevel() {
    return this.abrController.nextAutoLevel;
  }
  /**
   * this setter is used to force next auto level.
   * this is useful to force a switch down in auto mode:
   * in case of load error on level N, hls.js can set nextAutoLevel to N-1 for example)
   * forced value is valid for one fragment. upon successful frag loading at forced level,
   * this value will be resetted to -1 by ABR controller.
   */
  set nextAutoLevel(t) {
    this.abrController.nextAutoLevel = t;
  }
  /**
   * get the datetime value relative to media.currentTime for the active level Program Date Time if present
   */
  get playingDate() {
    return this.streamController.currentProgramDateTime;
  }
  get mainForwardBufferInfo() {
    return this.streamController.getMainFwdBufferInfo();
  }
  get maxBufferLength() {
    return this.streamController.maxBufferLength;
  }
  /**
   * Find and select the best matching audio track, making a level switch when a Group change is necessary.
   * Updates `hls.config.audioPreference`. Returns the selected track, or null when no matching track is found.
   */
  setAudioOption(t) {
    var e;
    return ((e = this.audioTrackController) == null ? void 0 : e.setAudioOption(t)) || null;
  }
  /**
   * Find and select the best matching subtitle track, making a level switch when a Group change is necessary.
   * Updates `hls.config.subtitlePreference`. Returns the selected track, or null when no matching track is found.
   */
  setSubtitleOption(t) {
    var e;
    return ((e = this.subtitleTrackController) == null ? void 0 : e.setSubtitleOption(t)) || null;
  }
  /**
   * Get the complete list of audio tracks across all media groups
   */
  get allAudioTracks() {
    const t = this.audioTrackController;
    return t ? t.allAudioTracks : [];
  }
  /**
   * Get the list of selectable audio tracks
   */
  get audioTracks() {
    const t = this.audioTrackController;
    return t ? t.audioTracks : [];
  }
  /**
   * index of the selected audio track (index in audio track lists)
   */
  get audioTrack() {
    const t = this.audioTrackController;
    return t ? t.audioTrack : -1;
  }
  /**
   * selects an audio track, based on its index in audio track lists
   */
  set audioTrack(t) {
    const e = this.audioTrackController;
    e && (e.audioTrack = t);
  }
  /**
   * get the complete list of subtitle tracks across all media groups
   */
  get allSubtitleTracks() {
    const t = this.subtitleTrackController;
    return t ? t.allSubtitleTracks : [];
  }
  /**
   * get alternate subtitle tracks list from playlist
   */
  get subtitleTracks() {
    const t = this.subtitleTrackController;
    return t ? t.subtitleTracks : [];
  }
  /**
   * index of the selected subtitle track (index in subtitle track lists)
   */
  get subtitleTrack() {
    const t = this.subtitleTrackController;
    return t ? t.subtitleTrack : -1;
  }
  get media() {
    return this._media;
  }
  /**
   * select an subtitle track, based on its index in subtitle track lists
   */
  set subtitleTrack(t) {
    const e = this.subtitleTrackController;
    e && (e.subtitleTrack = t);
  }
  /**
   * Whether subtitle display is enabled or not
   */
  get subtitleDisplay() {
    const t = this.subtitleTrackController;
    return t ? t.subtitleDisplay : !1;
  }
  /**
   * Enable/disable subtitle display rendering
   */
  set subtitleDisplay(t) {
    const e = this.subtitleTrackController;
    e && (e.subtitleDisplay = t);
  }
  /**
   * get mode for Low-Latency HLS loading
   */
  get lowLatencyMode() {
    return this.config.lowLatencyMode;
  }
  /**
   * Enable/disable Low-Latency HLS part playlist and segment loading, and start live streams at playlist PART-HOLD-BACK rather than HOLD-BACK.
   */
  set lowLatencyMode(t) {
    this.config.lowLatencyMode = t;
  }
  /**
   * Position (in seconds) of live sync point (ie edge of live position minus safety delay defined by ```hls.config.liveSyncDuration```)
   * @returns null prior to loading live Playlist
   */
  get liveSyncPosition() {
    return this.latencyController.liveSyncPosition;
  }
  /**
   * Estimated position (in seconds) of live edge (ie edge of live playlist plus time sync playlist advanced)
   * @returns 0 before first playlist is loaded
   */
  get latency() {
    return this.latencyController.latency;
  }
  /**
   * maximum distance from the edge before the player seeks forward to ```hls.liveSyncPosition```
   * configured using ```liveMaxLatencyDurationCount``` (multiple of target duration) or ```liveMaxLatencyDuration```
   * @returns 0 before first playlist is loaded
   */
  get maxLatency() {
    return this.latencyController.maxLatency;
  }
  /**
   * target distance from the edge as calculated by the latency controller
   */
  get targetLatency() {
    return this.latencyController.targetLatency;
  }
  set targetLatency(t) {
    this.latencyController.targetLatency = t;
  }
  /**
   * the rate at which the edge of the current live playlist is advancing or 1 if there is none
   */
  get drift() {
    return this.latencyController.drift;
  }
  /**
   * set to true when startLoad is called before MANIFEST_PARSED event
   */
  get forceStartLoad() {
    return this.streamController.forceStartLoad;
  }
  /**
   * ContentSteering pathways getter
   */
  get pathways() {
    return this.levelController.pathways;
  }
  /**
   * ContentSteering pathwayPriority getter/setter
   */
  get pathwayPriority() {
    return this.levelController.pathwayPriority;
  }
  set pathwayPriority(t) {
    this.levelController.pathwayPriority = t;
  }
  /**
   * returns true when all SourceBuffers are buffered to the end
   */
  get bufferedToEnd() {
    var t;
    return !!((t = this.bufferController) != null && t.bufferedToEnd);
  }
  /**
   * returns Interstitials Program Manager
   */
  get interstitialsManager() {
    var t;
    return ((t = this.interstitialsController) == null ? void 0 : t.interstitialsManager) || null;
  }
  /**
   * returns mediaCapabilities.decodingInfo for a variant/rendition
   */
  getMediaDecodingInfo(t, e = this.allAudioTracks) {
    const i = ka(e);
    return Ca(t, i, navigator.mediaCapabilities);
  }
}
de.defaultConfig = void 0;
const gr = new Map(
  Object.entries({
    M3U8: "application/vnd.apple.mpegurl",
    MP4: "video/mp4",
    MP3: "audio/mp3"
    /* MP3 */
  })
);
function wf(n) {
  var e;
  const t = (e = n.match(/[^/.\s]+$/)) == null ? void 0 : e[0].toUpperCase();
  return gr.get(t) ?? gr.get(
    "M3U8"
    /* M3U8 */
  );
}
function Cf(n, t) {
  const e = wf(n);
  return !e || e !== gr.get(
    "M3U8"
    /* M3U8 */
  ) ? !0 : !!t.canPlayType(e);
}
function Pf(n, t) {
  const { src: e } = t;
  if (!e || !e.length)
    return;
  if (Cf(e, n))
    t.src ? (n.setAttribute("src", e), n.load()) : n.removeAttribute("src");
  else {
    const s = new de();
    s.loadSource(e), s.attachMedia(n);
  }
}
var kf = Object.defineProperty, Of = Object.getOwnPropertyDescriptor, ae = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Of(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && kf(t, e, s), s;
};
let Vt = class extends ft {
  constructor() {
    super(...arguments), this.videoRef = Le(), this.viewMode = "default", this.paused = !1, this.noVideo = !1, this.currentTime = 0, this.playbackRate = 1, this.thumbnailTime = void 0, this.loadingImage = !1;
  }
  async play() {
    var n;
    this.videoRef.value && (this.videoRef.value.muted = !0, (n = this.videoRef.value.play()) == null || n.catch(() => {
      console.error("Failed to play video-slide video");
    }));
  }
  async pause() {
    var n;
    this.videoRef.value && (this.videoRef.value.muted = !0, (n = this.videoRef.value.play()) == null || n.then(() => {
      var t;
      (t = this.videoRef.value) == null || t.pause();
    }).catch(() => {
      console.error("Failed to pause video-slide video");
    }));
  }
  updateVideo() {
    this.videoRef.value && (this.playbackRate != this.videoRef.value.playbackRate && (this.videoRef.value.playbackRate = this.playbackRate), this.videoRef.value.paused != this.paused && (this.paused ? this.pause() : this.play()), this.currentTime && (this.paused || Math.abs(this.videoRef.value.currentTime - this.currentTime) > 1) && (this.videoRef.value.currentTime = this.currentTime));
  }
  thumbnailLoaded() {
    this.loadingImage = !1;
  }
  shouldUpdate(n) {
    let t = n.has("viewMode") || n.has("data") || n.has("noVideo");
    return this.noVideo && (n.has("currentTime") || n.has("loadingImage")) && !this.loadingImage && this.thumbnailTime !== this.currentTime ? (this.loadingImage = !0, this.thumbnailTime = this.currentTime ?? 0, t = !0) : (n.has("currentTime") || n.has("paused") || n.has("playbackRate")) && this.updateVideo(), t;
  }
  firstUpdated() {
    this.paused || this.play();
  }
  updated(n) {
    var t;
    n.has("data") && this.videoRef.value && Pf(this.videoRef.value, { src: (t = this.data) == null ? void 0 : t.src });
  }
  render() {
    var i;
    if (!this.data) return;
    const { src: n } = this.data, t = ((i = n.match(
      new RegExp("https://stream.mux.com/([a-zA-Z0-9]+).m3u8")
    )) == null ? void 0 : i[1]) ?? "";
    if (!t && this.noVideo) return;
    const e = `https://image.mux.com/${t ?? ""}/thumbnail.jpg?time=${this.thumbnailTime}&width=480&height=270`;
    return N`
      <div class="video-slide ${this.viewMode}">
        ${this.noVideo ? N`<img
              class="thumbnail"
              src=${e}
              @load=${this.thumbnailLoaded}
            />` : N`<video
              muted
              playsinline
              @loadeddata=${this.updateVideo}
              ${Re(this.videoRef)}
            ></video>`}
      </div>
    `;
  }
};
Vt.styles = St`
    .video-slide {
      background-color: var(--color-white);
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
    }

    video {
      width: 100%;
    }

    video::cue {
      opacity: 0;
    }

    .thumbnail {
      width: 100%;
    }
  `;
ae([
  P({ attribute: "view-mode" })
], Vt.prototype, "viewMode", 2);
ae([
  P({
    type: Boolean,
    attribute: "paused"
  })
], Vt.prototype, "paused", 2);
ae([
  P({
    type: Boolean,
    attribute: "no-video"
  })
], Vt.prototype, "noVideo", 2);
ae([
  P()
], Vt.prototype, "data", 2);
ae([
  P({ type: Number, attribute: "current-time" })
], Vt.prototype, "currentTime", 2);
ae([
  P({ type: Number, attribute: "playback-rate" })
], Vt.prototype, "playbackRate", 2);
ae([
  ne()
], Vt.prototype, "thumbnailTime", 2);
ae([
  ne()
], Vt.prototype, "loadingImage", 2);
Vt = ae([
  gt("bp-video-slide")
], Vt);
var Mf = Object.defineProperty, Ff = Object.getOwnPropertyDescriptor, Fe = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Ff(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Mf(t, e, s), s;
};
const $f = 680;
let pe = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    if (!this.data) return;
    const { usx: n } = this.data;
    return N`
      <bp-zoomable-slide
        ?hide-title=${this.hideTitle}
        ?title-wraps-2-lines=${this.titleWraps2Lines}
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">
          <slot name="title"></slot>
        </div>
        <div slot="content" style="width: ${$f}px">
          <bp-literary-design
            usx="${n}"
            .excludedKeyPaths=${this.excludedKeyPaths}
          />
        </div>
      </bp-zoomable-slide>
    `;
  }
};
Fe([
  P({ attribute: "view-mode" })
], pe.prototype, "viewMode", 2);
Fe([
  P()
], pe.prototype, "slideState", 2);
Fe([
  P({ attribute: "hide-title" })
], pe.prototype, "hideTitle", 2);
Fe([
  P({ attribute: "title-wraps-2-lines" })
], pe.prototype, "titleWraps2Lines", 2);
Fe([
  P()
], pe.prototype, "data", 2);
Fe([
  P({ attribute: "excluded-key-paths" })
], pe.prototype, "excludedKeyPaths", 2);
pe = Fe([
  gt("bp-literary-design-slide")
], pe);
var Nf = Object.defineProperty, Bf = Object.getOwnPropertyDescriptor, si = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Bf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Nf(t, e, s), s;
};
const Uf = 680;
let we = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    if (!this.data) return;
    const { usx: n, html: t } = this.data, e = n && n.length > 0, i = e ? `width: ${Uf}px` : "", s = e ? N`<bp-literary-design usx="${n}" />` : N`<bp-ephesians-literary-design .data="${t}" />`;
    return N`
      <bp-zoomable-slide
        ?hide-title=${this.hideTitle}
        ?title-wraps-2-lines=${this.titleWraps2Lines}
        ?large-content-mode=${!e}
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">
          <slot name="title"></slot>
        </div>
        <div slot="content" style="${i}">${s}</div>
      </bp-zoomable-slide>
    `;
  }
};
si([
  P({ attribute: "view-mode" })
], we.prototype, "viewMode", 2);
si([
  P()
], we.prototype, "slideState", 2);
si([
  P({ attribute: "hide-title" })
], we.prototype, "hideTitle", 2);
si([
  P({ attribute: "title-wraps-2-lines" })
], we.prototype, "titleWraps2Lines", 2);
si([
  P()
], we.prototype, "data", 2);
we = si([
  gt("bp-ephesians-literary-design-slide")
], we);
function qo(n) {
  return n == null || n === "" ? "0px" : `${String(n).replace(/px$/, "")}px`;
}
function da(n) {
  return n == null || n === "" ? 0 : Number(n.trim().replace("px", ""));
}
var Gf = Object.defineProperty, Kf = Object.getOwnPropertyDescriptor, ri = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Kf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Gf(t, e, s), s;
};
const Hf = 680;
let Ce = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    if (!this.data) return;
    this.style.setProperty(
      "--vertical-width",
      qo(Hf)
    );
    const { config: n } = this.data;
    return N`
      <bp-zoomable-slide
        ?hide-title=${this.hideTitle}
        ?title-wraps-2-lines=${this.titleWraps2Lines}
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">
          <slot name="title"></slot>
        </div>
        <div slot="content"><bp-macro-literary-design .data="${n}" /></div>
      </bp-zoomable-slide>
    `;
  }
};
ri([
  P({ attribute: "view-mode" })
], Ce.prototype, "viewMode", 2);
ri([
  P()
], Ce.prototype, "slideState", 2);
ri([
  P({ attribute: "hide-title" })
], Ce.prototype, "hideTitle", 2);
ri([
  P({ attribute: "title-wraps-2-lines" })
], Ce.prototype, "titleWraps2Lines", 2);
ri([
  P()
], Ce.prototype, "data", 2);
Ce = ri([
  gt("bp-macro-literary-design-slide")
], Ce);
var Vf = Object.defineProperty, Wf = Object.getOwnPropertyDescriptor, Xo = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Wf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Vf(t, e, s), s;
};
let ls = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return N`
      <div class="main-point-slide ${this.viewMode}">
        <div class="content">
          <slot></slot>
        </div>
      </div>
    `;
  }
};
ls.styles = St`
    .main-point-slide {
      background-color: var(--slide-accent-color);
      width: 100%;
      height: 100%;
      display: block;
    }

    .content {
      color: var(--color-white);
      font-size: var(--font-size-5xl);
      line-height: var(--line-height-snug);
      min-height: var(--slide-default-height);
      margin: 0 var(--size-7);
      display: grid;
      place-items: center;
    }
  `;
Xo([
  P({ attribute: "view-mode" })
], ls.prototype, "viewMode", 2);
ls = Xo([
  gt("bp-main-point-slide")
], ls);
var Yf = Object.defineProperty, zf = Object.getOwnPropertyDescriptor, xi = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? zf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Yf(t, e, s), s;
};
const jf = "*Key Words Adapted by Teacher";
let Pe = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default", this.multiVerseData = [], this.getMultiVerseContent = () => {
      var e;
      const n = /* @__PURE__ */ new Set([]), t = [];
      for (const i of this.multiVerseData) {
        let s = "", r = N``, a = N``;
        if (i.subtitle) {
          if (s = (e = i.subtitle.split(" ")) == null ? void 0 : e.map((o) => o.toLowerCase()).slice(0, 2).join("-"), n.has(s)) {
            const o = s;
            let c = 2;
            for (; n.has(s); )
              s = `${o}-${c}`, c += 1;
          }
          n.add(s), r = N`<div
          class="verse-subtitle"
          data-id="${s}"
        >
          ${i.subtitle}
        </div>`;
        }
        i.reference && i.translation && i.text && (a = N`<div
          data-id="${i.reference} (${i.translation})"
        >
          <div class="verse-header">
            ${i.reference}
            <sup class="translation">
              ${i.translation + (i.isAdapted ? "*" : "")}
            </sup>
          </div>
          <div class="verse-content">${dt(i.text)}</div>
        </div>`), t.push(N` ${r} ${a} `);
      }
      return N`${t}`;
    }, this.getAnyAdapted = () => this.multiVerseData.map((t) => t.isAdapted).reduce((t, e) => t || e) ? N`<div class="caption">${jf}</div>` : N``;
  }
  render() {
    var n;
    return (n = this.multiVerseData) != null && n.length ? N`
      <bp-scrollable-slide
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">${dt(this.slideTitle)}</div>
        <div slot="content" class="multi-verse-container">
          ${this.getMultiVerseContent()} ${this.getAnyAdapted()}
        </div>
      </bp-scrollable-slide>
    ` : null;
  }
};
Pe.styles = St`
    .translation {
      color: var(--color-gray);
      font-size: var(--font-size-xl);
      letter-spacing: var(--letter-spacing-wide);
      vertical-align: 6px;
      font-weight: var(--font-weight-semibold);
    }

    .multi-verse-container {
      display: flex;
      flex-direction: column;
      gap: var(--size-2);
    }

    .verse-subtitle {
      font-weight: var(--font-weight-bold);
      font-size: var(--font-size-xl);
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .verse-header {
      font-weight: var(--font-weight-semibold);
    }

    .caption {
      color: var(--color-gray);
      font-size: var(--font-size-xl);
      margin-top: var(--size-3);
    }

    sup {
      color: var(--color-black);
      font-size: var(--font-size-xl);
      vertical-align: 9px;
      font-weight: var(--font-weight-semibold);
    }
  `;
xi([
  P({ attribute: "view-mode" })
], Pe.prototype, "viewMode", 2);
xi([
  P()
], Pe.prototype, "slideState", 2);
xi([
  P({ attribute: "title" })
], Pe.prototype, "slideTitle", 2);
xi([
  P()
], Pe.prototype, "multiVerseData", 2);
Pe = xi([
  gt("bp-multi-verse-slide")
], Pe);
var qf = Object.defineProperty, Xf = Object.getOwnPropertyDescriptor, ni = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Xf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && qf(t, e, s), s;
};
let ve = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return N`
      <bp-scrollable-slide
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">${dt(this.slideTitle)}</div>
        <div slot="content">
          ${dt(this.content)}
          ${this.caption ? N`<div class="caption">${dt(this.caption)}</div>` : ""}
        </div>
      </bp-scrollable-slide>
    `;
  }
};
ve.styles = St`
    .caption {
      color: var(--color-gray);
      font-size: var(--font-size-xl);
      margin-top: var(--size-3);
    }

    sup {
      color: var(--color-black);
      font-size: var(--font-size-xl);
      vertical-align: 9px;
      font-weight: var(--font-weight-semibold);
    }

    ol {
      margin-left: var(--size-2);
    }
  `;
ni([
  P()
], ve.prototype, "slideState", 2);
ni([
  P({ attribute: "view-mode" })
], ve.prototype, "viewMode", 2);
ni([
  P({ attribute: "title" })
], ve.prototype, "slideTitle", 2);
ni([
  P({ attribute: "content" })
], ve.prototype, "content", 2);
ni([
  P({ attribute: "caption" })
], ve.prototype, "caption", 2);
ve = ni([
  gt("bp-paragraph-slide")
], ve);
const Qf = St`
  .question-slide {
    --question-slide-icon-container-width: 100px;
    background-color: var(--color-white);
    width: 100%;
    height: 100%;
    display: block;
  }

  .content-container {
    height: var(--slide-default-height);
    width: 100%;
    padding: 0 var(--size-7);
    box-sizing: border-box;
    display: grid;
    place-items: center;
  }

  .content {
    font-size: var(--font-size-5xl);
    line-height: var(--line-height-snug);
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: var(--size-3);
  }

  .icon-container {
    aspect-ratio: 1 / 1;
    color: var(--color-white);
    width: var(--question-slide-icon-container-width);
    flex-shrink: 0;
    align-self: flex-start;
    background-color: var(--slide-accent-color);
    border-radius: var(--radius-full);
    display: grid;
    place-items: center;
  }

  .icon {
    display: inline-block;
    fill: var(--icon-color, currentColor);
    height: var(--icon-size);
    width: var(--icon-size);
  }
`;
var Zf = Object.defineProperty, Jf = Object.getOwnPropertyDescriptor, Qo = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Jf(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Zf(t, e, s), s;
};
const tg = ga`<svg class="icon" aria-hidden="true" focusable="false" role="img" viewBox="0 0 512 512" style="--icon-color:var(--color-white); --icon-size:var(--size-6);"><path d="M448 0H64C28.63 0 0 28.62 0 63.1v287.1C0 387.4 28.63 415.1 64 415.1h96v83.1c0 9.873 11.25 15.52 19.12 9.649L304 415.1H448c35.38 0 64-28.63 64-63.1V63.1C512 28.62 483.4 0 448 0zM249.1 320C235.4 320 224 308.6 224 294S235.4 268 249.1 268C264.6 268 276 279.4 276 294S264.6 320 249.1 320zM307.7 203.4l-38.33 23.13v1.652c0 10.74-9.168 19.83-20 19.83c-10.83 0-20-9.088-20-19.83V214.1c0-6.609 3.332-13.22 10-17.35l47.5-28.09C292.7 166.2 296 160.4 296 153.8c0-9.914-8.334-18.17-18.33-18.17H234.3c-10 0-18.33 8.26-18.33 18.17c0 10.74-9.166 19.83-20 19.83S176 164.6 176 153.8C176 121.6 201.8 96 234.3 96h43.33C310.2 96 336 121.6 336 153.8C336 173.7 325.2 192.7 307.7 203.4z"/></path></svg>`;
let cs = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return N`
      <div class="question-slide ${this.viewMode}">
        <div class="content-container">
          <div class="content">
            <div class="icon-container">${tg}</div>
            <slot></slot>
          </div>
        </div>
      </div>
    `;
  }
};
cs.styles = Qf;
Qo([
  P({ attribute: "view-mode" })
], cs.prototype, "viewMode", 2);
cs = Qo([
  gt("bp-question-slide")
], cs);
const eg = St`
  .resource-slide {
    --resource-slide-icon-container-width: 100px;
    background-color: var(--slide-accent-color);
    width: 100%;
    height: 100%;
    display: block;
  }

  .content-container {
    height: var(--slide-default-height);
    width: 100%;
    padding: 0 var(--size-7);
    box-sizing: border-box;
    display: grid;
    place-items: center;
  }

  .content {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: var(--size-3);
  }

  .resource-info {
    color: var(--color-white);
    line-height: var(--line-height-normal);
    display: flex;
    flex-direction: column;
    gap: var(--size-1);
  }

  .resource-title {
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-5xl);
    line-height: var(--line-height-none);
  }

  .icon-container {
    aspect-ratio: 1 / 1;
    color: var(--color-white);
    width: var(--resource-slide-icon-container-width);
    flex-shrink: 0;
    align-self: flex-start;
    background-color: var(--color-white);
    border-radius: var(--radius-full);
    display: grid;
    place-items: center;
  }

  .icon {
    display: inline-block;
    fill: var(--icon-color, currentColor);
    height: var(--icon-size);
    width: var(--icon-size);
  }

  .resource-authors {
    list-style: none;
    margin-left: 0;
    padding-left: 0;
  }

  .author {
    color: var(--color-white);
    font-size: var(--font-size-4xl);
    line-height: var(--line-height-normal);
  }
`;
var ig = Object.defineProperty, sg = Object.getOwnPropertyDescriptor, Gr = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? sg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && ig(t, e, s), s;
};
const rg = ga`<svg class="icon" aria-hidden="true" focusable="false" role="img" viewBox="0 0 448 512" style="--icon-color:var(--slide-accent-color); --icon-size:var(--size-6);"><!--! Font Awesome Pro 6.1.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M448 336v-288C448 21.49 426.5 0 400 0H96C42.98 0 0 42.98 0 96v320c0 53.02 42.98 96 96 96h320c17.67 0 32-14.33 32-31.1c0-11.72-6.607-21.52-16-27.1v-81.36C441.8 362.8 448 350.2 448 336zM143.1 128h192C344.8 128 352 135.2 352 144C352 152.8 344.8 160 336 160H143.1C135.2 160 128 152.8 128 144C128 135.2 135.2 128 143.1 128zM143.1 192h192C344.8 192 352 199.2 352 208C352 216.8 344.8 224 336 224H143.1C135.2 224 128 216.8 128 208C128 199.2 135.2 192 143.1 192zM384 448H96c-17.67 0-32-14.33-32-32c0-17.67 14.33-32 32-32h288V448z"></path></svg>`;
let Si = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default", this.authors = [];
  }
  render() {
    return N`
      <div class="resource-slide ${this.viewMode}">
        <div class="content-container">
          <div class="content">
            <div class="icon-container">${rg}</div>
            <div class="resource-info">
              <div class="resource-title">
                <slot></slot>
              </div>
              <ul class="resource-authors">
                ${this.authors.map(
      (n) => N`<li class="author" key="${n}">${n}</li>`
    )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
Si.styles = eg;
Gr([
  P({ attribute: "view-mode" })
], Si.prototype, "viewMode", 2);
Gr([
  P()
], Si.prototype, "authors", 2);
Si = Gr([
  gt("bp-resource-slide")
], Si);
var ng = Object.defineProperty, ag = Object.getOwnPropertyDescriptor, ms = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? ag(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && ng(t, e, s), s;
};
let Ze = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return this.verseData ? N`
      <bp-scrollable-slide
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">
          ${this.verseData.reference}
          <sup class="translation">
            ${this.verseData.translation + (this.verseData.isAdapted ? "*" : "")}
          </sup>
        </div>
        <div slot="content">
          ${dt(this.verseData.text)}
          ${this.verseData.isAdapted ? N`<div class="caption">*Key Words Adapted by Teacher</div>` : ""}
        </div>
      </bp-scrollable-slide>
    ` : null;
  }
};
Ze.styles = St`
    .translation {
      color: var(--color-gray);
      font-size: var(--title-sup-size);
      letter-spacing: var(--letter-spacing-wide);
      transition: var(--title-transition);
    }

    .caption {
      color: var(--color-gray);
      font-size: var(--font-size-xl);
      margin-top: var(--size-3);
    }

    sup {
      color: var(--color-black);
      font-size: var(--font-size-xl);
      vertical-align: 9px;
      font-weight: var(--font-weight-semibold);
    }
  `;
ms([
  P({ attribute: "view-mode" })
], Ze.prototype, "viewMode", 2);
ms([
  P()
], Ze.prototype, "slideState", 2);
ms([
  P()
], Ze.prototype, "verseData", 2);
Ze = ms([
  gt("bp-single-verse-slide")
], Ze);
const og = St`
  :host {
    --min-width: var(--size-60);
  }

  .table {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  table {
    color: var(--color-black);
    border-collapse: collapse;
    background-color: var(--color-white);
    border: 1px solid var(--color-neutral-10);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: inset 0px 0px 0px 2px var(--color-neutral-10);
    font-size: 16px;
    line-height: var(--line-height-snug);
    min-width: var(--min-width);
  }

  table th {
    font-weight: 600;
    background-color: var(--color-neutral-10);
    color: var(--color-black);
    box-shadow: inset 0px 0px 0px 2px var(--color-neutral-10);
    padding: 16px 12px;
    text-align: left;
    vertical-align: center;
  }

  table td {
    color: var(--color-black);
    padding: 12px;
    text-align: left;
    vertical-align: top;
    border: 2px solid var(--color-neutral-10);
  }

  table td img {
    object-fit: cover;
  }

  a {
    color: var(--color-black);
  }

  table caption {
    display: none;
  }

  table tfoot td {
    font-size: var(--font-size-xs);
    color: var(--color-gray);
  }

  table tfoot a {
    color: var(--color-gray);
  }
`;
var lg = Object.defineProperty, cg = Object.getOwnPropertyDescriptor, ai = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? cg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && lg(t, e, s), s;
};
let ye = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default", this.hideTitle = !1, this.titleWraps2Lines = !1;
  }
  render() {
    if (this.data) {
      if (this.data.minWidth) {
        const n = qo(
          Math.min(da(this.data.minWidth), da(this.data.slideWidth))
        );
        n && this.style.setProperty("--min-width", n);
      }
      return this.data.slideWidth && this.style.setProperty("--table-width", this.data.slideWidth), N`
      <bp-zoomable-slide
        ?hide-title=${this.hideTitle}
        ?title-wraps-2-lines=${this.titleWraps2Lines}
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">
          <slot name="title"></slot>
        </div>
        <div slot="content" class="table">${dt(this.data.body)}</div>
      </bp-zoomable-slide>
    `;
    }
  }
};
ye.styles = [
  og,
  mr,
  St`
      .table {
        width: var(--table-width);
      }

      table {
        transition:
          color var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration),
          border var(--spotlight-transition-duration),
          box-shadow var(--spotlight-transition-duration);
      }

      a {
        transition: color var(--spotlight-transition-duration);
      }

      table th {
        transition:
          color var(--spotlight-transition-duration),
          background-color var(--spotlight-transition-duration),
          box-shadow var(--spotlight-transition-duration);
      }

      table td.spotlighted {
        border-width: 2.01px;
      }

      table td {
        transition:
          color var(--spotlight-transition-duration),
          border-color var(--spotlight-transition-duration),
          border-width 0s;
      }

      table tfoot {
        transition: color var(--spotlight-transition-duration);
      }
    `
];
ai([
  P({ attribute: "view-mode" })
], ye.prototype, "viewMode", 2);
ai([
  P()
], ye.prototype, "slideState", 2);
ai([
  P({ type: Boolean, attribute: "hide-title" })
], ye.prototype, "hideTitle", 2);
ai([
  P({ type: Boolean, attribute: "title-wraps-2-lines" })
], ye.prototype, "titleWraps2Lines", 2);
ai([
  P()
], ye.prototype, "data", 2);
ye = ai([
  gt("bp-table-slide")
], ye);
const hg = St`
  .title-slide {
    --title-slide-image-width: 680px;
    --title-slide-class-artwork-height: 70px;
    background-color: var(--color-white);
    width: 100%;
    height: 100%;
    display: flex;
    white-space: pretty;
  }

  .tall,
  .mobile-tall {
    flex-direction: column-reverse;
  }

  .content {
    flex-grow: 1;
    height: var(--slide-default-height);
    padding: var(--size-7);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 80%;
  }

  .tall .artwork-container,
  .mobile-tall .artwork-container {
    width: 100%;
  }

  .tall .content,
  .mobile-tall .content {
    width: 100%;
  }

  .artwork-container {
    width: var(--title-slide-image-width);
    height: var(--slide-default-height);
    background-color: var(--slide-accent-color);
    display: flex;
    align-self: center;
    justify-content: center;
  }

  .artwork {
    width: 100%;
    height: 100%;
    object-fit: cover;
    margin: 0px;
  }

  .secondary-content {
    display: flex;
    flex-direction: row;
    margin-top: auto;
  }

  .secondary-artwork {
    height: var(--title-slide-class-artwork-height);
    aspect-ratio: 1 / 1;
    border-radius: var(--radius-lg);
  }

  .secondary-title {
    margin-left: var(--size-1-5);
    display: flex;
    flex-direction: column;
    justify-content: space-around;
  }

  ::slotted([slot="session-number"]) {
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-3xl);
    line-height: var(--line-height-normal);
    color: var(--color-gray);
  }

  ::slotted([slot="session-name"]) {
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-7xl);
    line-height: var(--line-height-none);
    overflow-wrap: anywhere;
  }

  ::slotted([slot="class-name"]) {
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-3xl);
    line-height: var(--line-height-none);
    margin-bottom: var(--size-0-5);
  }

  ::slotted([slot="teacher-name"]) {
    font-weight: var(--font-weight-normal);
    font-size: var(--font-size-2xl);
    line-height: var(--line-height-none);
  }
`;
var dg = Object.defineProperty, ug = Object.getOwnPropertyDescriptor, ps = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? ug(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && dg(t, e, s), s;
};
let Je = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    const n = N`
      <img class="secondary-artwork" alt="" src="${this.iconSrc}" />
    `, t = N`
      <img class="artwork" src="${this.artworkSrc}" alt="" />
    `;
    return N`
      <div class="title-slide ${this.viewMode}">
        <div class="content">
          <slot name="session-number"></slot>
          <slot name="session-name"></slot>
          <div class="secondary-content">
            ${n}
            <div class="secondary-title">
              <slot name="class-name"></slot>
              <slot name="teacher-name"></slot>
            </div>
          </div>
        </div>
        <div
          class="artwork-container"
        >
          ${t}
        </div>
      </dkv>
    `;
  }
};
Je.styles = hg;
ps([
  P({ attribute: "view-mode" })
], Je.prototype, "viewMode", 2);
ps([
  P({ attribute: "icon-src" })
], Je.prototype, "iconSrc", 2);
ps([
  P({ attribute: "artwork-src" })
], Je.prototype, "artworkSrc", 2);
Je = ps([
  gt("bp-title-slide")
], Je);
const fg = St`
  .thank-you-slide {
    --thank-you-slide-icon-container-width: 80px;
    background-color: var(--color-white);
    width: 100%;
    height: 100%;
    display: block;
  }

  .content {
    height: var(--slide-default-height);
    padding: var(--size-15);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--size-1);
    text-align: center;
  }

  .title {
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-8xl);
    line-height: var(--line-height-normal);
  }

  .post-title {
    font-weight: var(--font-weight-normal);
    font-size: var(--font-size-5xl);
    line-height: var(--line-height-normal);
    line-height: var(--line-height-snug);
  }
`;
var gg = Object.defineProperty, mg = Object.getOwnPropertyDescriptor, Zo = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? mg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && gg(t, e, s), s;
};
let hs = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return N`
      <div class="thank-you-slide ${this.viewMode}">
        <div class="content-container">
          <div class="content">
            <div class="title">Thank You</div>
            <div class="post-title">
              Classroom is free because of the generous support of people like
              you.
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
hs.styles = fg;
Zo([
  P({ attribute: "view-mode" })
], hs.prototype, "viewMode", 2);
hs = Zo([
  gt("bp-thank-you-slide")
], hs);
var pg = Object.defineProperty, vg = Object.getOwnPropertyDescriptor, Ai = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? vg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && pg(t, e, s), s;
};
let ke = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default";
  }
  render() {
    return this.multiVerseData ? N`
      <bp-scrollable-slide
        view-mode="${this.viewMode}"
        .slideState=${this.slideState}
      >
        <div slot="title">${dt(this.slideTitle)}</div>
        <div slot="content" class="multi-verse-container">
          ${this.multiVerseData.map(
      (n) => N`
              <div data-id="${n.translation}">
                <div class="verse-header">${n.translation}</div>
                <div class="verse-content">${dt(n.text)}</div>
              </div>
            `
    )}
        </div>
      </bp-scrollable-slide>
    ` : null;
  }
};
ke.styles = St`
    .multi-verse-container {
      display: flex;
      flex-direction: column;
      gap: var(--size-2);
    }

    .verse-header {
      font-weight: var(--font-weight-semibold);
    }

    sup {
      color: var(--color-black);
      font-size: var(--font-size-xl);
      vertical-align: 9px;
      font-weight: var(--font-weight-semibold);
    }
  `;
Ai([
  P({ attribute: "view-mode" })
], ke.prototype, "viewMode", 2);
Ai([
  P()
], ke.prototype, "slideState", 2);
Ai([
  P({ attribute: "title" })
], ke.prototype, "slideTitle", 2);
Ai([
  P()
], ke.prototype, "multiVerseData", 2);
ke = Ai([
  gt("bp-verse-comparison-slide")
], ke);
var yg = Object.defineProperty, Eg = Object.getOwnPropertyDescriptor, vs = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Eg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && yg(t, e, s), s;
};
let ti = class extends ft {
  constructor() {
    super(...arguments), this.viewMode = "default", this.getWordDefinitionContent = () => {
      var i, s;
      let n = "";
      const t = [], e = /* @__PURE__ */ new Set();
      for (const r of this.wordDefinitionData ?? []) {
        r.language != n && (t.push(
          N`<div class="language">
            <span class="language-name"
              >${r.language.toUpperCase()}</span
            >
          </div>`
        ), n = r.language);
        const a = `card-${r.transliteration ?? r.definition}`;
        let o = a, c = 1;
        for (; e.has(o); )
          c++, o = a + "-" + c;
        e.add(o);
        const l = r.definition && (r.transliteration || r.original) ? N` = ` : null, h = (i = r.transliteration) != null && i.length ? N`<em>${r.transliteration}</em>` : null, d = r.language == "hebrew" || r.language == "aramaic" ? N`<bp-text-hebrew>${r.original}</bp-text-hebrew>` : r.language == "greek" ? N`<bp-text-greek>${r.original}</bp-text-greek>` : N``, u = r.original && r.language !== "latin" ? r.transliteration ? N` (<span class="word-definition-original"
                  >${d}</span
                >)` : N`<span class="word-definition-original"
                >${d}</span
              >` : null, f = N`${[
          r.definition,
          l,
          h,
          u
        ].filter((g) => g !== null)}`;
        t.push(
          N`<div data-id="${o}" class="word-definition-card">
          <div class="word-definition-title">${f}</div>
          ${(s = r.notes) != null && s.length ? r.notes.length > 1 ? N`<div class="word-notes">
                  <ul>
                    ${r.notes.map(
            (g) => N`<li>${dt(g)}</li>`
          )}
                  </ul>
                </div>` : N`<div class="word-notes">
                  ${dt(r.notes[0])}
                </div>` : ""}
        </div>`
        );
      }
      return N`${t}`;
    };
  }
  render() {
    var n;
    return N`
      <bp-zoomable-slide
        view-mode="${this.viewMode}"
        background-color="class-secondary"
        hide-shadow="true"
        hide-title="true"
        .slideState=${{
      ...this.slideState,
      transformState: {
        ...(n = this.slideState) == null ? void 0 : n.transformState,
        zoom: 1
      }
    }}
      >
        <div slot="content">
          <div class="word-definition-content">
            ${this.getWordDefinitionContent()}
          </div>
        </div>
      </bp-scrollable-slide>
    `;
  }
};
ti.styles = [
  St`
      .word-definition-content {
        width: calc(var(--slide-default-width) - var(--size-10));
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: var(--size-1);
      }
      .language-name {
        background-color: rgba(255, 255, 255, 0.75);
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
        letter-spacing: var(--letter-spacing-wider);
        padding: var(--size-1) var(--size-2);
      }
      .word-definition-card {
        --shadow-fade: var(--fade-amount, 1);
        --shadow-opacity: calc(0.5 - var(--shadow-fade) * 0.5);
        background-color: var(--color-white);
        color: var(--color-black);
        box-shadow: 8px 8px 0px rgba(255, 255, 255, var(--shadow-opacity));
        padding: var(--size-3);
        margin-bottom: var(--size-1);
        font-size: var(--font-size-5xl);
        transition:
          color var(--spotlight-transition-duration),
          background var(--spotlight-transition-duration),
          box-shadow var(--spotlight-transition-duration);
      }
      .word-definition-title {
        font-weight: var(--font-weight-semibold);
      }
      .word-definition-original {
        font-weight: var(--font-weight-normal);
      }
      .word-notes ul {
        margin: var(--size-1) 0 0;
      }
    `,
  mr
];
vs([
  P({ attribute: "view-mode" })
], ti.prototype, "viewMode", 2);
vs([
  P()
], ti.prototype, "slideState", 2);
vs([
  P()
], ti.prototype, "wordDefinitionData", 2);
ti = vs([
  gt("bp-word-definition-slide")
], ti);
const Tg = 2, Sg = 32;
class xg {
  constructor({
    slideRef: t,
    maxWindowHeight: e,
    minWindowHeight: i,
    verticalPadding: s = 0
  }) {
    this._initAnimation = !1, this._maxWindowHeight = 540, this._minWindowHeight = 540, this._scroll = 0, this._slideRef = t, this._verticalPadding = s, this._maxWindowHeight = e, this._minWindowHeight = i;
  }
  set contentEl(t) {
    this._contentEl = t;
  }
  get contentEl() {
    return this._contentEl;
  }
  get contentHeight() {
    var t;
    return (((t = this._contentEl) == null ? void 0 : t.offsetHeight) ?? 0) + 2 * this._verticalPadding;
  }
  set maxWindowHeight(t) {
    this._maxWindowHeight = t;
  }
  set minWindowHeight(t) {
    this._minWindowHeight = t;
  }
  get maxTranslateY() {
    return this.contentHeight + 2 * this._verticalPadding < this._minWindowHeight ? 0 : -1 * Math.max(0, this.contentHeight - this._maxWindowHeight);
  }
  get translateY() {
    return this._scroll * this.maxTranslateY;
  }
  get isScrolling() {
    return this.translateY < 0;
  }
  get isScrolledToBottom() {
    return this.translateY <= this.maxTranslateY;
  }
  getScrollValue(t, e) {
    if (!(t != null && t.length)) return null;
    const i = t.map((u) => {
      var f;
      return (f = this._contentEl) == null ? void 0 : f.querySelector(`[data-id="${u}"]`);
    }).filter((u) => !!u).map((u) => u);
    if (!(i != null && i.length) || !this._contentEl) return null;
    const { top: s, height: r } = this._contentEl.getBoundingClientRect(), {
      top: a,
      midY: o,
      bottom: c
    } = Ys(
      i.map(Ws)
    ), l = this._contentEl.offsetHeight / r;
    let h, d;
    switch (e) {
      case "top":
      case "top-left":
      case "top-right":
        h = (a - s) * l, d = Tg - this._verticalPadding;
        break;
      case "bottom":
      case "bottom-left":
      case "bottom-right":
        h = (c - s) * l, d = this._maxWindowHeight - Sg - this._verticalPadding;
        break;
      case "center":
      default:
        h = (o - s) * l, d = this._maxWindowHeight / 2 - this._verticalPadding;
        break;
    }
    return Math.min(
      1,
      Math.max(
        0,
        (h - d) / Math.abs(this.maxTranslateY)
      )
    );
  }
  update({
    scrollY: t = 0,
    scrollPoints: e = void 0,
    scrollAnchorPoint: i = void 0,
    minimizeTitle: s = void 0
  }) {
    if (setTimeout(() => this._initAnimation = !0, 50), this._scroll = this.getScrollValue(e, i) ?? t, this._slideRef.value) {
      const r = `
        ${this._initAnimation ? "" : "--scroll-transition: 0; --title-transition: 0;"}
        --content-translate-y: ${this.translateY}px;
        --scrim-opacity: ${this.isScrolledToBottom ? 0 : 1};
      `;
      this._slideRef.value.setAttribute("style", r), this.isScrolling || s ? this._slideRef.value.classList.add("title-minimized") : this._slideRef.value.classList.remove("title-minimized");
    }
  }
}
class Ag {
  constructor({ windowRef: t }) {
    this._initAnimation = !1, this._windowRef = t;
  }
  set contentEl(t) {
    this._contentEl = t;
  }
  update({ shown: t = void 0 }) {
    if (setTimeout(() => this._initAnimation = !0, 50), !!this._contentEl) {
      if (this._currentlyShown === t) {
        this.setAnchor();
        return;
      }
      if (this._currentlyShown) {
        const e = this._contentEl.querySelector(
          `[data-id="${this._currentlyShown}"]`
        );
        e == null || e.removeAttribute("show"), this._initAnimation ? e == null || e.removeAttribute("no-animation") : e == null || e.setAttribute("no-animation", "");
      }
      if (t) {
        const e = this._contentEl.querySelector(`[data-id="${t}"]`);
        if (!e) {
          this._currentlyShown = void 0;
          return;
        }
        e.setAttribute("show", ""), this._initAnimation ? e.removeAttribute("no-animation") : e.setAttribute("no-animation", "");
      }
      this._currentlyShown = t, this.setAnchor();
    }
  }
  setAnchor() {
    var e, i;
    const t = (e = this._contentEl) == null ? void 0 : e.querySelector(
      `[data-id="${this._currentlyShown}"]`
    );
    if (t && ((i = this._windowRef) != null && i.value)) {
      const {
        x: s,
        y: r,
        width: a,
        height: o
      } = t.getBoundingClientRect(), {
        x: c,
        y: l,
        width: h,
        height: d
      } = this._windowRef.value.getBoundingClientRect(), u = (r + o / 2 < l + d / 2 ? "bottom-" : "top-") + (s + a / 2 < c + h / 2 ? "left" : "right");
      t.setAttribute("anchor-position", u);
    }
  }
}
var bg = Object.defineProperty, Ig = Object.getOwnPropertyDescriptor, bi = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Ig(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && bg(t, e, s), s;
};
const Lg = 40, Rg = 540, _g = 106, Dg = 88, wg = 116, Cg = 98;
let Oe = class extends ft {
  constructor() {
    super(...arguments), this.slideHeight = Rg, this.slideRef = Le(), this.contentRef = Le(), this.windowRef = Le(), this.slideObserver = new Xi(this, {
      callback: (n) => {
        n.filter((t) => t.target.className.includes("scrollable-slide")).forEach((t) => {
          this.slideHeight = t.contentRect.height, this.scrollController.minWindowHeight = this.minContentWindowHeight, this.scrollController.maxWindowHeight = this.maxContentWindowHeight, this.updateState();
        });
      }
    }), this.backgroundColor = "white", this.hideShadow = !1, this.viewMode = "default", this.highlightController = new pa(), this.lookupController = new Ag({
      windowRef: this.windowRef
    }), this.scrollController = new xg({
      slideRef: this.slideRef,
      verticalPadding: Lg,
      minWindowHeight: this.minContentWindowHeight,
      maxWindowHeight: this.maxContentWindowHeight
    });
  }
  get minTitleHeight() {
    return this.viewMode === "default" ? Dg : Cg;
  }
  get maxTitleHeight() {
    return this.viewMode === "default" ? _g : wg;
  }
  get maxContentWindowHeight() {
    return this.slideHeight - this.minTitleHeight;
  }
  get minContentWindowHeight() {
    return this.slideHeight - this.maxTitleHeight;
  }
  handleContentUpdate(n) {
    var e;
    const t = (e = n.target) == null ? void 0 : e.assignedNodes({
      flatten: !0
    })[0];
    this.highlightController.contentEl = t, this.lookupController.contentEl = t, this.scrollController.contentEl = t, this.updateState();
  }
  updateState() {
    var n, t, e;
    this.highlightController.update(((n = this.slideState) == null ? void 0 : n.highlightState) || {}), this.lookupController.update(((t = this.slideState) == null ? void 0 : t.lookupState) || {}), this.scrollController.update(((e = this.slideState) == null ? void 0 : e.transformState) || {});
  }
  willUpdate(n) {
    n.has("slideState") && this.updateState();
  }
  render() {
    const n = "--scroll-transition: 0; --title-transition: 0;", t = pr("overflow-shadow", {
      "overflow-shadow-hidden": this.hideShadow
    });
    return N`
      <div
        ${Re(this.slideRef)}
        class="scrollable-slide ${this.viewMode} background-${this.backgroundColor}"
        style="${n}"
      >
        <slot name="title"></slot>
        <div class="content-window" ${Re(this.windowRef)}>
          <div class="transformed-content" ${Re(this.contentRef)}>
            <div class="content">
              <slot
                name="content"
                @slotchange=${this.handleContentUpdate}
              ></slot>
            </div>
          </div>
        </div>
        <div class="${t}"></div>
      </div>
    `;
  }
  firstUpdated() {
    var n;
    (n = this.slideRef) != null && n.value && this.slideObserver.observe(this.slideRef.value);
  }
};
Oe.styles = [
  ma,
  St`
      ::slotted([slot="content"]) {
        color: var(--color-black);
        font-family: var(--font-sans);
        font-size: var(--font-size-4xl);
        font-weight: var(--font-weight-normal);
        line-height: var(--line-height-snug);
        width: var(--slide-default-width);
        box-sizing: border-box;
        margin: var(--size-5) 0;
        padding: 0 var(--size-5);
        text-align: start;
        unicode-bidi: plaintext;
      }
    `
];
bi([
  P({ attribute: "background-color" })
], Oe.prototype, "backgroundColor", 2);
bi([
  P({
    type: Boolean,
    attribute: "hide-shadow"
  })
], Oe.prototype, "hideShadow", 2);
bi([
  P()
], Oe.prototype, "slideState", 2);
bi([
  P({ attribute: "view-mode" })
], Oe.prototype, "viewMode", 2);
Oe = bi([
  gt("bp-scrollable-slide")
], Oe);
const qi = (n) => {
  if (typeof n == "number") return n;
  if (/^[0-9]+(\.([0-9]+)?)?$/.test(n))
    return parseFloat(n);
  const t = n.match(
    new RegExp("([0-9]{1,2}):([0-9]{1,2})(.[0-9]+)?")
  );
  if (!t) return 0;
  const [e, i, s] = [t[1], t[2], t[3]];
  return 60 * parseInt(e) + parseInt(i) + parseFloat(s || "0");
};
async function Pg(n) {
  const { data: t } = await ei({
    query: ii`
      query GetVisual($id: ID!) {
        visual(id: $id) {
          id
          data {
            ... on DiagramVisualData {
              alt
              caption
              src
              title
            }
          }
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return t.visual;
}
async function kg(n) {
  const { data: t } = await ei({
    query: ii`
      query GetVisual($id: ID!) {
        visual(id: $id) {
          id
          data {
            ... on ImageVisualData {
              alt
              caption
              src
              title
            }
          }
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return t.visual;
}
async function Og(n) {
  const { data: t } = await ei({
    query: ii`
      query GetLiteraryDesign($id: ID!) {
        literaryDesign(id: $id) {
          caption
          id
          reference
          title
          usx
          html
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return { data: t.literaryDesign };
}
async function Mg(n) {
  const { data: t } = await ei({
    query: ii`
      query GetVisual($id: ID!) {
        visual(id: $id) {
          id
          data {
            ... on TableVisualData {
              body
              minWidth
              slideWidth
            }
          }
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return t.visual;
}
async function Fg(n) {
  const { data: t } = await ei({
    query: ii`
      query GetVisual($id: ID!) {
        visual(id: $id) {
          id
          data {
            ... on VideoVisualData {
              alt
              externalId
              src
              title
            }
          }
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return t.visual;
}
async function $g(n) {
  const { data: t } = await ei({
    query: ii`
      query GetVisual($id: ID!) {
        visual(id: $id) {
          id
          data {
            ... on MacroLiteraryDesign {
              caption
              config
              id
              reference
              title
              type
            }
          }
        }
      }
    `,
    variables: {
      id: n
    }
  });
  return t.visual;
}
const Ng = St`
  .slide {
    --slide-default-width: 960px;
    --slide-default-height: 540px;
    --slide-accent-color: var(--theme-artwork-primary-color, #104366);
    --slide-secondary-color: var(--theme-artwork-secondary-color, #e24213);
    --background-red: var(--slide-background-red, 255);
    --background-blue: var(--slide-background-blue, 255);
    --background-green: var(--slide-background-green, 255);
    --slide-current-height: var(--slide-default-height);
    width: var(--slide-default-width);
    height: var(--slide-current-height);
    display: block;
    position: relative;
  }

  .mobile,
  .mobile-tall {
    --font-size-2xs: 14px;
    --font-size-xs: 16px;
    --font-size-sm: 18px;
    --font-size-md: 20px;
    --font-size-lg: 22px;
    --font-size-xl: 24px;
    --font-size-2xl: 28px;
    --font-size-3xl: 32px;
    --font-size-4xl: 36px;
    --font-size-5xl: 40px;
    --font-size-6xl: 44px;
    --font-size-7xl: 48px;
    --font-size-8xl: 52px;
    --font-size-9xl: 56px;
    --font-size-10xl: 60px;
  }

  .tall,
  .mobile-tall {
    --slide-current-height: 100%;
  }
`;
function Vs(n) {
  const t = n.replace("#", "").trim();
  let e = 255, i = 255, s = 255;
  return t.length == 6 && (e = parseInt(t.substring(0, 2), 16), i = parseInt(t.substring(2, 4), 16), s = parseInt(t.substring(4, 6), 16)), t.length == 3 && (e = parseInt(t[0] + t[0], 16), i = parseInt(t[1] + t[1], 16), s = parseInt(t[2] + t[2], 16)), { red: e, green: i, blue: s };
}
var Bg = Object.defineProperty, Ug = Object.getOwnPropertyDescriptor, Ut = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? Ug(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && Bg(t, e, s), s;
};
const Gg = 10, Kg = 25, Hg = "#104366", Vg = "#e24213", Wg = [
  "imgArcId",
  "diagramArcId",
  "tableArcId",
  "videoArcId",
  "literaryDesignArcId",
  "macroLiteraryDesignArcId"
];
let Ct = class extends ft {
  constructor() {
    super(...arguments), this.primaryColor = Hg, this.secondaryColor = Vg, this.viewMode = "default", this.paused = !0, this.noVideo = !1, this.currentTime = 0, this.playbackRate = 1, this.store = /* @__PURE__ */ new Map([]);
  }
  updated(n) {
    var t;
    if (n.has("data"))
      for (const e of Wg) {
        const i = (t = this.data) == null ? void 0 : t[e];
        !i || this.store.get(i) || this.getData(e, i).then(({ data: s }) => {
          this.store.set(i, s), this.requestUpdate();
        }).catch(() => {
          this.retryFetch(i, e);
        });
      }
  }
  async getData(n, t) {
    switch (n) {
      case "diagramArcId":
        return Pg(t);
      case "literaryDesignArcId":
        return Og(t);
      case "macroLiteraryDesignArcId":
        return $g(t);
      case "tableArcId":
        return Mg(t);
      case "videoArcId":
        return Fg(t);
      default:
        return kg(t);
    }
  }
  retryFetch(n, t, e = 0) {
    if (e === Kg) return;
    const i = Gg * Math.pow(2, e);
    setTimeout(() => {
      this.getData(t, n).then(({ data: s }) => {
        this.store.set(n, s), this.requestUpdate();
      }).catch(() => this.retryFetch(n, t, e + 1));
    }, i);
  }
  get styles() {
    var i, s;
    if (!this.data) return "";
    const { red: n, green: t, blue: e } = ((i = this.data) == null ? void 0 : i.variant) == "main-point" ? Vs(this.primaryColor) : ((s = this.data) == null ? void 0 : s.variant) == "word-definition" ? Vs(this.secondaryColor) : Vs("#fff");
    return [
      `--slide-background-red: ${n};`,
      `--slide-background-green: ${t};`,
      `--slide-background-blue: ${e};`
    ].join(" ");
  }
  renderSlide() {
    var e, i, s, r, a, o, c, l, h, d, u, f, g, v, p, y, E, T, S, x, D, A, _, R, b, C, F, U, W, G, k, H, $, V, z, O, M, X, et, Q, J, pt, mt, Rt;
    if (!this.data) return N``;
    const n = !((e = this.data) != null && e.title) || this.data.title.length === 0;
    let t = this.data.variant;
    switch (t == "image" && this.slideState && (t = "diagram"), t) {
      case "title":
        return N`
          <bp-title-slide
            view-mode="${this.viewMode}"
            icon-src="${(s = (i = this.theme) == null ? void 0 : i.artwork) == null ? void 0 : s.class}"
            artwork-src="${(a = (r = this.theme) == null ? void 0 : r.artwork) == null ? void 0 : a.module}"
          >
            <div slot="session-number">${(o = this.data) == null ? void 0 : o.sessionNumber}</div>
            <div slot="session-name">${dt((c = this.data) == null ? void 0 : c.sessionName)}</div>
            <div slot="class-name">${(l = this.data) == null ? void 0 : l.className}</div>
            <div slot="teacher-name">${(h = this.data) == null ? void 0 : h.teacherName}</div>
          </bp-title-slide>
        `;
      case "image":
        return N`
          <bp-image-slide
            view-mode="${this.viewMode}"
            title="${(d = this.data) == null ? void 0 : d.title}"
            .data=${this.store.get(((u = this.data) == null ? void 0 : u.diagramArcId) ?? "") || this.store.get(((f = this.data) == null ? void 0 : f.imgArcId) ?? "")}
          >
          </bp-image-slide>
        `;
      case "question":
        return N` <bp-question-slide view-mode="${this.viewMode}">
          <div>${dt((g = this.data) == null ? void 0 : g.content)}</div>
        </bp-question-slide>`;
      case "resource":
        return N`
          <bp-resource-slide
            view-mode="${this.viewMode}"
            .authors=${(v = this.data) == null ? void 0 : v.authors}
          >
            <div>${dt((p = this.data) == null ? void 0 : p.title)}</div>
          </bp-resource-slide>
        `;
      case "paragraph":
        return N`
          <bp-paragraph-slide
            view-mode="${this.viewMode}"
            title="${(y = this.data) == null ? void 0 : y.title}"
            content="${(E = this.data) == null ? void 0 : E.content}"
            caption="${(T = this.data) == null ? void 0 : T.caption}"
            .slideState="${this.slideState}"
          />
        `;
      case "multi-verse":
        return N`
          <bp-multi-verse-slide
            view-mode="${this.viewMode}"
            title="${(S = this.data) == null ? void 0 : S.title}"
            .multiVerseData=${(x = this.data) == null ? void 0 : x.multiVerseData}
            .slideState="${this.slideState}"
          />
        `;
      case "verse-comparison":
        return N`
          <bp-verse-comparison-slide
            view-mode="${this.viewMode}"
            title="${(D = this.data) == null ? void 0 : D.title}"
            .multiVerseData=${(A = this.data) == null ? void 0 : A.multiVerseData}
            .slideState="${this.slideState}"
          />
        `;
      case "single-verse":
        return N`
          <bp-single-verse-slide
            view-mode="${this.viewMode}"
            .verseData=${(_ = this.data) == null ? void 0 : _.verseData}
            .slideState="${this.slideState}"
          />
        `;
      case "diagram":
        return N`
          <bp-diagram-slide
            view-mode="${this.viewMode}"
            .slideState="${this.slideState}"
            ?hide-title=${n}
            ?title-wraps-2-lines=${(R = this.data) == null ? void 0 : R.titleWraps2Lines}
            ?hide-shadow=${(b = this.data) == null ? void 0 : b.hideShadow}
            .data=${this.store.get(((C = this.data) == null ? void 0 : C.diagramArcId) ?? "") || this.store.get(((F = this.data) == null ? void 0 : F.imgArcId) ?? "")}
          >
            <div slot="title">${dt((U = this.data) == null ? void 0 : U.title)}</div>
          </bp-diagram-slide>
        `;
      case "table":
        return N`
          <bp-table-slide
            view-mode="${this.viewMode}"
            .slideState="${this.slideState}"
            ?hide-title=${n}
            ?title-wraps-2-lines=${(W = this.data) == null ? void 0 : W.titleWraps2Lines}
            .data=${this.store.get(((G = this.data) == null ? void 0 : G.tableArcId) ?? "")}
          >
            <div slot="title">${dt((k = this.data) == null ? void 0 : k.title)}</div>
          </bp-table-slide>
        `;
      case "literary-design":
        return N`
          <bp-literary-design-slide
            view-mode="${this.viewMode}"
            ?hide-title=${n}
            ?title-wraps-2-lines=${(H = this.data) == null ? void 0 : H.titleWraps2Lines}
            .slideState="${this.slideState}"
            excluded-key-paths="${JSON.stringify(
          (($ = this.data) == null ? void 0 : $.excludedKeyPaths) || []
        )}"
            .data=${this.store.get(((V = this.data) == null ? void 0 : V.literaryDesignArcId) ?? "")}
          >
            <div slot="title">${dt((z = this.data) == null ? void 0 : z.title)}</div>
          </bp-literary-design-slide>
        `;
      case "ephesians-literary-design":
        return N`
          <bp-ephesians-literary-design-slide
            view-mode="${this.viewMode}"
            ?hide-title=${n}
            ?title-wraps-2-lines=${(O = this.data) == null ? void 0 : O.titleWraps2Lines}
            .slideState="${this.slideState}"
            .data=${this.store.get(((M = this.data) == null ? void 0 : M.literaryDesignArcId) ?? "")}
          >
            <div slot="title">${dt((X = this.data) == null ? void 0 : X.title)}</div>
          </bp-ephesians-literary-design-slide>
        `;
      case "macro-literary-design":
        return N`
          <bp-macro-literary-design-slide
            view-mode="${this.viewMode}"
            ?hide-title=${n}
            ?title-wraps-2-lines=${(et = this.data) == null ? void 0 : et.titleWraps2Lines}
            .slideState="${this.slideState}"
            .data=${this.store.get(((Q = this.data) == null ? void 0 : Q.macroLiteraryDesignArcId) ?? "")}
          >
            <div slot="title">${dt((J = this.data) == null ? void 0 : J.title)}</div>
          </bp-macro-literary-design-slide>
        `;
      case "illustration":
      case "screen-recording":
        return N`
          <bp-video-slide
            view-mode="${this.viewMode}"
            current-time="${qi(this.currentTime)}"
            ?paused=${this.paused}
            ?no-video=${this.noVideo}
            playback-rate="${this.playbackRate}"
            .data=${this.store.get(((pt = this.data) == null ? void 0 : pt.videoArcId) ?? "")}
          />
        `;
      case "thank-you":
        return N`<bp-thank-you-slide view-mode="${this.viewMode}" />`;
      case "main-point":
        return N`
          <bp-main-point-slide view-mode="${this.viewMode}">
            <div>${dt((mt = this.data) == null ? void 0 : mt.content)}</div>
          </bp-main-point-slide>
        `;
      case "word-definition":
        return N`
          <bp-word-definition-slide
            view-mode="${this.viewMode}"
            .wordDefinitionData="${(Rt = this.data) == null ? void 0 : Rt.wordDefinitionData}"
            .slideState="${this.slideState}"
          >
          </bp-word-definition-slide>
        `;
      default:
        return N``;
    }
  }
  render() {
    return N`
      <div style="${this.styles}" class="${pr("slide", this.viewMode)}">
        ${this.renderSlide()}
      </div>
    `;
  }
};
Ct.styles = Ng;
Ut([
  P({ attribute: "primary-color" })
], Ct.prototype, "primaryColor", 2);
Ut([
  P({ attribute: "secondary-color" })
], Ct.prototype, "secondaryColor", 2);
Ut([
  P({ attribute: "view-mode" })
], Ct.prototype, "viewMode", 2);
Ut([
  P({ type: Object, attribute: "data" })
], Ct.prototype, "data", 2);
Ut([
  P({ type: Object, attribute: "slide-state" })
], Ct.prototype, "slideState", 2);
Ut([
  P({
    type: Boolean,
    attribute: "paused",
    converter: (n) => n === "true"
  })
], Ct.prototype, "paused", 2);
Ut([
  P({
    type: Boolean,
    attribute: "no-video",
    converter: (n) => n === "true"
  })
], Ct.prototype, "noVideo", 2);
Ut([
  P({ attribute: "current-time" })
], Ct.prototype, "currentTime", 2);
Ut([
  P({ type: Number, attribute: "playback-rate" })
], Ct.prototype, "playbackRate", 2);
Ut([
  P({ type: Object })
], Ct.prototype, "theme", 2);
Ut([
  ne()
], Ct.prototype, "store", 2);
Ct = Ut([
  gt("bp-slide")
], Ct);
const Yg = St`
  :host {
    --presentation-scale: 1;
  }

  .slide-presentation {
    background-color: var(--presentation-background-color, #fff);
    width: 100%;
    display: block;
    overflow: hidden;
    position: relative;
    z-index: 0; /* Fixes bug where border-radius would break on transforms. */
  }

  .decoration-rounded,
  .decoration-border,
  .decoration-box-shadow {
    border-radius: var(--size-1-5);
  }

  .decoration-border,
  .decoration-box-shadow {
    border: none;
  }

  .decoration-box-shadow {
    box-shadow: var(--shadow-md);
  }

  .default,
  .mobile {
    aspect-ratio: 16 / 9;
  }

  .tall {
    height: 100%;
  }

  .tall .scaled-slides {
    height: var(--tall-mode-unscaled-height);
  }

  .scaled-slides {
    transform: scale(var(--presentation-scale));
    transform-origin: top left;
    position: absolute;
    top: 0;
    left: var(--presentation-margin, 0);
  }
`;
var zg = Object.defineProperty, jg = Object.getOwnPropertyDescriptor, Lt = (n, t, e, i) => {
  for (var s = i > 1 ? void 0 : i ? jg(t, e) : t, r = n.length - 1, a; r >= 0; r--)
    (a = n[r]) && (s = (i ? a(t, e, s) : a(s)) || s);
  return i && s && zg(t, e, s), s;
};
const ua = 16 / 9, qg = 16 / 10, fa = 0.6, Xg = /* @__PURE__ */ new Set([
  "show-highlight",
  "hide-highlight",
  "scroll-and-highlight"
]);
function Jo(n) {
  if (!n) return { presentationSlides: [] };
  const t = JSON.parse(n);
  return t.presentationSlides ? t : t.length ? { presentationSlides: t.map(
    (i) => JSON.parse(i.config)
  ) } : { presentationSlides: [] };
}
let Tt = class extends ft {
  constructor() {
    super(...arguments), this.presentationRef = Le(), this.resizeController = new Xi(this, {
      callback: (n) => {
        n.length > 0 && n.filter(
          (t) => t.target.className.includes("slide-presentation")
        ).forEach((t) => {
          this.containerWidth = t.contentRect.width, this.containerAspectRatio = t.contentRect.height ? t.contentRect.width / t.contentRect.height : 16 / 9;
        });
      }
    }), this.viewMode = "default", this.paused = !0, this.noVideo = !1, this.currTime = 0, this.playbackRate = 1, this.containerWidth = 960, this.containerAspectRatio = 16 / 9, this.prevScale = null, this.prevAspect = null, this.slideViewMode = "default", this.prevSlideIndex = null, this.prevStateIndex = null, this.decoration = "none";
  }
  get presentationScale() {
    return this.containerWidth > 0 ? this.containerAspectRatio <= ua ? this.containerWidth / 960 : this.containerWidth / this.containerAspectRatio / 540 : 1;
  }
  get currSlideIndex() {
    if (!this.data?.presentationSlides?.length) return 0;
    let n = 0;
    for (; n < this.data.presentationSlides.length - 1 && !(qi(this.data.presentationSlides[n + 1].startTime) > this.currTime); )
      n++;
    return n;
  }
  get currSlide() {
    var n;
    return ((n = this.data) == null ? void 0 : n.presentationSlides?.[this.currSlideIndex]?.slide) ?? null;
  }
  get presentationMargin() {
    return Math.max(
      0,
      (this.containerAspectRatio - ua) / this.containerAspectRatio
    ) / 2 * this.containerWidth;
  }
  get presentationBackgroundColor() {
    var n, t, e, i, s, r, a;
    switch (((n = this.currSlide) == null ? void 0 : n.variant) ?? "title") {
      case "main-point":
        return ((i = (e = (t = this.theme) == null ? void 0 : t.artwork) == null ? void 0 : e.color) == null ? void 0 : i.primary) ?? "#fff";
      case "word-definition":
        return ((a = (r = (s = this.theme) == null ? void 0 : s.artwork) == null ? void 0 : r.color) == null ? void 0 : a.secondary) ?? "#fff";
      default:
        return "#fff";
    }
  }
  get currAnimations() {
    var n;
    return ((n = this.data) == null ? void 0 : n.presentationSlides?.[this.currSlideIndex]?.animations) ?? null;
  }
  get currStateIndex() {
    var t;
    if (!((t = this.currAnimations) != null && t.length) || this.currTime < qi(this.currAnimations[0].startTime))
      return null;
    let n = 0;
    for (; n < this.currAnimations.length - 1 && this.currTime >= qi(this.currAnimations[n + 1].startTime); )
      n++;
    return n;
  }
  get currSlideState() {
    var n;
    return (n = this.currAnimations) != null && n.length ? {
      highlightState: this.currHighlightState ?? void 0,
      transformState: this.currTransformState,
      spotlightState: this.currSpotlightState,
      lookupState: this.currLookupState
    } : null;
  }
  iterateToCurrAnimation(n) {
    var t;
    if (!(!((t = this.currAnimations) != null && t.length) || this.currStateIndex == null))
      for (let e = 0; e <= this.currStateIndex; e++)
        n(this.currAnimations[e]);
  }
  get currHighlightState() {
    const n = /* @__PURE__ */ new Set(), t = /* @__PURE__ */ new Set();
    if (this.currAnimations)
      for (const e of this.currAnimations)
        Xg.has(e.variant) && n.add(e.stringValue ?? "");
    return this.iterateToCurrAnimation(
      ({ variant: e, stringValue: i, stringArrayValue: s }) => {
        const r = s ?? [i];
        switch (e) {
          case "show-highlight":
          case "scroll-and-highlight":
            r.forEach((a) => {
              a && (t.add(a), n.delete(a));
            });
            break;
          case "hide-highlight":
            r.forEach((a) => {
              a && (t.delete(a), n.add(a));
            });
            break;
        }
      }
    ), {
      shown: Array.from(t.keys()),
      hidden: Array.from(n.keys())
    };
  }
  get currTransformState() {
    if (!this.currAnimations) return;
    let n = !1, t = 0, e, i, s = 0, r = 0, a, o;
    return this.iterateToCurrAnimation(
      ({ variant: c, numberValue: l, stringValue: h, stringArrayValue: d, extraArg: u }) => {
        const f = d ?? (h ? [h] : void 0);
        switch (c) {
          case "minimize-title":
            n = !0;
            break;
          case "expand-title":
            n = !1;
            break;
          case "zoom":
            t = l, e = void 0, i = void 0;
            break;
          case "zoom-to-fill":
            t = f ? void 0 : 1, e = f, i = void 0;
            break;
          case "zoom-to-fit":
            t = f ? void 0 : 0, e = void 0, i = f;
            break;
          case "zoom-to-cover":
            t = El, e = void 0, i = void 0, s = 0.5;
            break;
          case "scroll-y":
            r = r || 0, s = l, a = void 0, o = void 0;
            break;
          case "scroll-x":
            r = l, s = s || 0, a = void 0, o = void 0;
            break;
          case "scroll-point":
          case "scroll-and-spotlight":
          case "scroll-and-highlight":
            a = f, o = u, s = void 0, r = void 0;
            break;
        }
      }
    ), {
      minimizeTitle: n,
      zoom: t,
      zoomFillElements: e,
      zoomFitElements: i,
      scrollX: r,
      scrollY: s,
      scrollPoints: a,
      scrollAnchorPoint: o
    };
  }
  get currSpotlightState() {
    let n = [];
    return this.iterateToCurrAnimation(
      ({ variant: t, stringValue: e, stringArrayValue: i }) => {
        const s = i ?? [
          e ?? ""
        ];
        switch (t) {
          case "spotlight":
          case "scroll-and-spotlight":
            n = s;
            break;
          case "add-spotlight":
            n = n.concat(s);
            break;
          case "clear-spotlight":
            n = [];
            break;
        }
      }
    ), { spotlighted: n };
  }
  get currLookupState() {
    let n;
    return this.iterateToCurrAnimation(({ variant: t, stringValue: e }) => {
      switch (t) {
        case "lookup":
          n = e;
          break;
        case "clear-lookup":
          n = void 0;
          break;
      }
    }), { shown: n };
  }
  get themeStyles() {
    var t, e, i, s, r, a;
    const n = [];
    return (e = (t = this.theme) == null ? void 0 : t.artwork) != null && e.color && (n.push(
      `--theme-artwork-primary-color: ${(s = (i = this.theme) == null ? void 0 : i.artwork) == null ? void 0 : s.color.primary};`
    ), n.push(
      `--theme-artwork-secondary-color: ${(a = (r = this.theme) == null ? void 0 : r.artwork) == null ? void 0 : a.color.secondary};`
    )), n.join(" ");
  }
  shouldUpdate(n) {
    var t, e;
    return !!(n.has("data") || n.has("arcId") || n.has("viewMode") || n.has("decoration") || this.data && (((t = this.currSlide) == null ? void 0 : t.variant) === "illustration" || ((e = this.currSlide) == null ? void 0 : e.variant) === "screen-recording") && (n.has("currTime") || n.has("paused") || n.has("playbackRate")) || this.prevSlideIndex != this.currSlideIndex || this.prevStateIndex != this.currStateIndex || this.prevScale != this.presentationScale || this.prevAspect != this.containerAspectRatio);
  }
  willUpdate() {
    this.slideViewMode = this.containerAspectRatio > qg ? this.presentationScale > fa ? "default" : "mobile" : this.presentationScale > fa ? "tall" : "mobile-tall";
  }
  firstUpdated() {
    var n;
    (n = this.presentationRef) != null && n.value && this.resizeController.observe(this.presentationRef.value);
  }
  updated(n) {
    this.prevSlideIndex = this.currSlideIndex, this.prevStateIndex = this.currStateIndex, this.prevScale = this.presentationScale, this.prevAspect = this.containerAspectRatio, !(!n.has("arcId") || !this.arcId) && al(this.arcId).then(({ data: t }) => {
      this.data = Jo(JSON.stringify(t));
    }).catch(() => {
    });
  }
  render() {
    var t, e, i, s, r, a;
    const n = `
      ${this.themeStyles}
      --tall-mode-unscaled-height: ${100 / this.presentationScale}%;
      --presentation-margin: ${this.presentationMargin}px;
      --presentation-background-color: ${this.presentationBackgroundColor};
      --presentation-scale: ${this.presentationScale.toString()};
      --aspect: ${this.containerAspectRatio};
    `;
    return N`
      <div
        ${Re(this.presentationRef)}
        class="slide-presentation ${this.viewMode} decoration-${this.decoration}"
        style="${n}"
      >
        <div class="scaled-slides ${this.viewMode}">
          ${this.data ? N`
                <bp-slide
                  primary-color="${((i = (e = (t = this.theme) == null ? void 0 : t.artwork) == null ? void 0 : e.color) == null ? void 0 : i.primary) ?? "#104366"}"
                  secondary-color="${((a = (r = (s = this.theme) == null ? void 0 : s.artwork) == null ? void 0 : r.color) == null ? void 0 : a.secondary) ?? "#e24213"}"
                  view-mode="${this.slideViewMode}"
                  current-time="${this.currTime}"
                  paused="${this.paused}"
                  no-video="${this.noVideo}"
                  playback-rate="${this.playbackRate}"
                  .data=${this.currSlide}
                  .slideState=${this.currSlideState}
                  .theme=${this.theme}
                />
              ` : ""}
        </div>
      </div>
    `;
  }
};
Tt.styles = Yg;
Lt([
  P({ type: Object })
], Tt.prototype, "theme", 2);
Lt([
  P({ attribute: "view-mode" })
], Tt.prototype, "viewMode", 2);
Lt([
  P({
    type: Boolean,
    attribute: "paused",
    converter: (n) => n === "true"
  })
], Tt.prototype, "paused", 2);
Lt([
  P({
    type: Boolean,
    attribute: "no-video",
    converter: (n) => n === "true"
  })
], Tt.prototype, "noVideo", 2);
Lt([
  P({ type: Number, attribute: "current-time" })
], Tt.prototype, "currTime", 2);
Lt([
  P({ type: Number, attribute: "playback-rate" })
], Tt.prototype, "playbackRate", 2);
Lt([
  ne()
], Tt.prototype, "containerWidth", 2);
Lt([
  ne()
], Tt.prototype, "containerAspectRatio", 2);
Lt([
  ne()
], Tt.prototype, "presentationScale", 1);
Lt([
  ne()
], Tt.prototype, "slideViewMode", 2);
Lt([
  ne()
], Tt.prototype, "currSlideIndex", 1);
Lt([
  ne()
], Tt.prototype, "currStateIndex", 1);
Lt([
  P({ attribute: "arc-id" })
], Tt.prototype, "arcId", 2);
Lt([
  P({
    type: Object,
    attribute: "data",
    converter: Jo
  })
], Tt.prototype, "data", 2);
Lt([
  P({ attribute: "decoration" })
], Tt.prototype, "decoration", 2);
Tt = Lt([
  gt("bp-slide-presentation")
], Tt);
