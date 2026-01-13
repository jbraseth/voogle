/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const k = window, ce = k.ShadowRoot && (k.ShadyCSS === void 0 || k.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, Oe = Symbol(), ue = /* @__PURE__ */ new WeakMap();
let Fe = class {
  constructor(e, r, a) {
    if (this._$cssResult$ = !0, a !== Oe) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = r;
  }
  get styleSheet() {
    let e = this.o;
    const r = this.t;
    if (ce && e === void 0) {
      const a = r !== void 0 && r.length === 1;
      a && (e = ue.get(r)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), a && ue.set(r, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const Ke = (t) => new Fe(typeof t == "string" ? t : t + "", void 0, Oe), Ze = (t, e) => {
  ce ? t.adoptedStyleSheets = e.map(((r) => r instanceof CSSStyleSheet ? r : r.styleSheet)) : e.forEach(((r) => {
    const a = document.createElement("style"), n = k.litNonce;
    n !== void 0 && a.setAttribute("nonce", n), a.textContent = r.cssText, t.appendChild(a);
  }));
}, me = ce ? (t) => t : (t) => t instanceof CSSStyleSheet ? ((e) => {
  let r = "";
  for (const a of e.cssRules) r += a.cssText;
  return Ke(r);
})(t) : t;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var B;
const I = window, fe = I.trustedTypes, Qe = fe ? fe.emptyScript : "", he = I.reactiveElementPolyfillSupport, ee = { toAttribute(t, e) {
  switch (e) {
    case Boolean:
      t = t ? Qe : null;
      break;
    case Object:
    case Array:
      t = t == null ? t : JSON.stringify(t);
  }
  return t;
}, fromAttribute(t, e) {
  let r = t;
  switch (e) {
    case Boolean:
      r = t !== null;
      break;
    case Number:
      r = t === null ? null : Number(t);
      break;
    case Object:
    case Array:
      try {
        r = JSON.parse(t);
      } catch {
        r = null;
      }
  }
  return r;
} }, Ne = (t, e) => e !== t && (e == e || t == t), G = { attribute: !0, type: String, converter: ee, reflect: !1, hasChanged: Ne }, re = "finalized";
let A = class extends HTMLElement {
  constructor() {
    super(), this._$Ei = /* @__PURE__ */ new Map(), this.isUpdatePending = !1, this.hasUpdated = !1, this._$El = null, this._$Eu();
  }
  static addInitializer(e) {
    var r;
    this.finalize(), ((r = this.h) !== null && r !== void 0 ? r : this.h = []).push(e);
  }
  static get observedAttributes() {
    this.finalize();
    const e = [];
    return this.elementProperties.forEach(((r, a) => {
      const n = this._$Ep(a, r);
      n !== void 0 && (this._$Ev.set(n, a), e.push(n));
    })), e;
  }
  static createProperty(e, r = G) {
    if (r.state && (r.attribute = !1), this.finalize(), this.elementProperties.set(e, r), !r.noAccessor && !this.prototype.hasOwnProperty(e)) {
      const a = typeof e == "symbol" ? Symbol() : "__" + e, n = this.getPropertyDescriptor(e, a, r);
      n !== void 0 && Object.defineProperty(this.prototype, e, n);
    }
  }
  static getPropertyDescriptor(e, r, a) {
    return { get() {
      return this[r];
    }, set(n) {
      const i = this[e];
      this[r] = n, this.requestUpdate(e, i, a);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) || G;
  }
  static finalize() {
    if (this.hasOwnProperty(re)) return !1;
    this[re] = !0;
    const e = Object.getPrototypeOf(this);
    if (e.finalize(), e.h !== void 0 && (this.h = [...e.h]), this.elementProperties = new Map(e.elementProperties), this._$Ev = /* @__PURE__ */ new Map(), this.hasOwnProperty("properties")) {
      const r = this.properties, a = [...Object.getOwnPropertyNames(r), ...Object.getOwnPropertySymbols(r)];
      for (const n of a) this.createProperty(n, r[n]);
    }
    return this.elementStyles = this.finalizeStyles(this.styles), !0;
  }
  static finalizeStyles(e) {
    const r = [];
    if (Array.isArray(e)) {
      const a = new Set(e.flat(1 / 0).reverse());
      for (const n of a) r.unshift(me(n));
    } else e !== void 0 && r.push(me(e));
    return r;
  }
  static _$Ep(e, r) {
    const a = r.attribute;
    return a === !1 ? void 0 : typeof a == "string" ? a : typeof e == "string" ? e.toLowerCase() : void 0;
  }
  _$Eu() {
    var e;
    this._$E_ = new Promise(((r) => this.enableUpdating = r)), this._$AL = /* @__PURE__ */ new Map(), this._$Eg(), this.requestUpdate(), (e = this.constructor.h) === null || e === void 0 || e.forEach(((r) => r(this)));
  }
  addController(e) {
    var r, a;
    ((r = this._$ES) !== null && r !== void 0 ? r : this._$ES = []).push(e), this.renderRoot !== void 0 && this.isConnected && ((a = e.hostConnected) === null || a === void 0 || a.call(e));
  }
  removeController(e) {
    var r;
    (r = this._$ES) === null || r === void 0 || r.splice(this._$ES.indexOf(e) >>> 0, 1);
  }
  _$Eg() {
    this.constructor.elementProperties.forEach(((e, r) => {
      this.hasOwnProperty(r) && (this._$Ei.set(r, this[r]), delete this[r]);
    }));
  }
  createRenderRoot() {
    var e;
    const r = (e = this.shadowRoot) !== null && e !== void 0 ? e : this.attachShadow(this.constructor.shadowRootOptions);
    return Ze(r, this.constructor.elementStyles), r;
  }
  connectedCallback() {
    var e;
    this.renderRoot === void 0 && (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (e = this._$ES) === null || e === void 0 || e.forEach(((r) => {
      var a;
      return (a = r.hostConnected) === null || a === void 0 ? void 0 : a.call(r);
    }));
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    var e;
    (e = this._$ES) === null || e === void 0 || e.forEach(((r) => {
      var a;
      return (a = r.hostDisconnected) === null || a === void 0 ? void 0 : a.call(r);
    }));
  }
  attributeChangedCallback(e, r, a) {
    this._$AK(e, a);
  }
  _$EO(e, r, a = G) {
    var n;
    const i = this.constructor._$Ep(e, a);
    if (i !== void 0 && a.reflect === !0) {
      const o = (((n = a.converter) === null || n === void 0 ? void 0 : n.toAttribute) !== void 0 ? a.converter : ee).toAttribute(r, a.type);
      this._$El = e, o == null ? this.removeAttribute(i) : this.setAttribute(i, o), this._$El = null;
    }
  }
  _$AK(e, r) {
    var a;
    const n = this.constructor, i = n._$Ev.get(e);
    if (i !== void 0 && this._$El !== i) {
      const o = n.getPropertyOptions(i), l = typeof o.converter == "function" ? { fromAttribute: o.converter } : ((a = o.converter) === null || a === void 0 ? void 0 : a.fromAttribute) !== void 0 ? o.converter : ee;
      this._$El = i, this[i] = l.fromAttribute(r, o.type), this._$El = null;
    }
  }
  requestUpdate(e, r, a) {
    let n = !0;
    e !== void 0 && (((a = a || this.constructor.getPropertyOptions(e)).hasChanged || Ne)(this[e], r) ? (this._$AL.has(e) || this._$AL.set(e, r), a.reflect === !0 && this._$El !== e && (this._$EC === void 0 && (this._$EC = /* @__PURE__ */ new Map()), this._$EC.set(e, a))) : n = !1), !this.isUpdatePending && n && (this._$E_ = this._$Ej());
  }
  async _$Ej() {
    this.isUpdatePending = !0;
    try {
      await this._$E_;
    } catch (r) {
      Promise.reject(r);
    }
    const e = this.scheduleUpdate();
    return e != null && await e, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var e;
    if (!this.isUpdatePending) return;
    this.hasUpdated, this._$Ei && (this._$Ei.forEach(((n, i) => this[i] = n)), this._$Ei = void 0);
    let r = !1;
    const a = this._$AL;
    try {
      r = this.shouldUpdate(a), r ? (this.willUpdate(a), (e = this._$ES) === null || e === void 0 || e.forEach(((n) => {
        var i;
        return (i = n.hostUpdate) === null || i === void 0 ? void 0 : i.call(n);
      })), this.update(a)) : this._$Ek();
    } catch (n) {
      throw r = !1, this._$Ek(), n;
    }
    r && this._$AE(a);
  }
  willUpdate(e) {
  }
  _$AE(e) {
    var r;
    (r = this._$ES) === null || r === void 0 || r.forEach(((a) => {
      var n;
      return (n = a.hostUpdated) === null || n === void 0 ? void 0 : n.call(a);
    })), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
  }
  _$Ek() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$E_;
  }
  shouldUpdate(e) {
    return !0;
  }
  update(e) {
    this._$EC !== void 0 && (this._$EC.forEach(((r, a) => this._$EO(a, this[a], r))), this._$EC = void 0), this._$Ek();
  }
  updated(e) {
  }
  firstUpdated(e) {
  }
};
A[re] = !0, A.elementProperties = /* @__PURE__ */ new Map(), A.elementStyles = [], A.shadowRootOptions = { mode: "open" }, he == null || he({ ReactiveElement: A }), ((B = I.reactiveElementVersions) !== null && B !== void 0 ? B : I.reactiveElementVersions = []).push("1.6.3");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var V;
const q = window, _ = q.trustedTypes, ge = _ ? _.createPolicy("lit-html", { createHTML: (t) => t }) : void 0, ae = "$lit$", h = `lit$${(Math.random() + "").slice(9)}$`, Te = "?" + h, Xe = `<${Te}>`, b = document, P = () => b.createComment(""), R = (t) => t === null || typeof t != "object" && typeof t != "function", ke = Array.isArray, Ye = (t) => ke(t) || typeof (t == null ? void 0 : t[Symbol.iterator]) == "function", W = `[ 	
\f\r]`, E = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, pe = /-->/g, be = />/g, g = RegExp(`>|${W}(?:([^\\s"'>=/]+)(${W}*=${W}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`, "g"), xe = /'/g, $e = /"/g, Me = /^(?:script|style|textarea|title)$/i, Le = (t) => (e, ...r) => ({ _$litType$: t, strings: e, values: r }), Nr = Le(1), Tr = Le(2), x = Symbol.for("lit-noChange"), v = Symbol.for("lit-nothing"), _e = /* @__PURE__ */ new WeakMap(), p = b.createTreeWalker(b, 129, null, !1);
function He(t, e) {
  if (!Array.isArray(t) || !t.hasOwnProperty("raw")) throw Error("invalid template strings array");
  return ge !== void 0 ? ge.createHTML(e) : e;
}
const er = (t, e) => {
  const r = t.length - 1, a = [];
  let n, i = e === 2 ? "<svg>" : "", o = E;
  for (let l = 0; l < r; l++) {
    const s = t[l];
    let c, d, u = -1, m = 0;
    for (; m < s.length && (o.lastIndex = m, d = o.exec(s), d !== null); ) m = o.lastIndex, o === E ? d[1] === "!--" ? o = pe : d[1] !== void 0 ? o = be : d[2] !== void 0 ? (Me.test(d[2]) && (n = RegExp("</" + d[2], "g")), o = g) : d[3] !== void 0 && (o = g) : o === g ? d[0] === ">" ? (o = n ?? E, u = -1) : d[1] === void 0 ? u = -2 : (u = o.lastIndex - d[2].length, c = d[1], o = d[3] === void 0 ? g : d[3] === '"' ? $e : xe) : o === $e || o === xe ? o = g : o === pe || o === be ? o = E : (o = g, n = void 0);
    const f = o === g && t[l + 1].startsWith("/>") ? " " : "";
    i += o === E ? s + Xe : u >= 0 ? (a.push(c), s.slice(0, u) + ae + s.slice(u) + h + f) : s + h + (u === -2 ? (a.push(void 0), l) : f);
  }
  return [He(t, i + (t[r] || "<?>") + (e === 2 ? "</svg>" : "")), a];
};
class O {
  constructor({ strings: e, _$litType$: r }, a) {
    let n;
    this.parts = [];
    let i = 0, o = 0;
    const l = e.length - 1, s = this.parts, [c, d] = er(e, r);
    if (this.el = O.createElement(c, a), p.currentNode = this.el.content, r === 2) {
      const u = this.el.content, m = u.firstChild;
      m.remove(), u.append(...m.childNodes);
    }
    for (; (n = p.nextNode()) !== null && s.length < l; ) {
      if (n.nodeType === 1) {
        if (n.hasAttributes()) {
          const u = [];
          for (const m of n.getAttributeNames()) if (m.endsWith(ae) || m.startsWith(h)) {
            const f = d[o++];
            if (u.push(m), f !== void 0) {
              const Je = n.getAttribute(f.toLowerCase() + ae).split(h), T = /([.?@])?(.*)/.exec(f);
              s.push({ type: 1, index: i, name: T[2], strings: Je, ctor: T[1] === "." ? ar : T[1] === "?" ? nr : T[1] === "@" ? ir : z });
            } else s.push({ type: 6, index: i });
          }
          for (const m of u) n.removeAttribute(m);
        }
        if (Me.test(n.tagName)) {
          const u = n.textContent.split(h), m = u.length - 1;
          if (m > 0) {
            n.textContent = _ ? _.emptyScript : "";
            for (let f = 0; f < m; f++) n.append(u[f], P()), p.nextNode(), s.push({ type: 2, index: ++i });
            n.append(u[m], P());
          }
        }
      } else if (n.nodeType === 8) if (n.data === Te) s.push({ type: 2, index: i });
      else {
        let u = -1;
        for (; (u = n.data.indexOf(h, u + 1)) !== -1; ) s.push({ type: 7, index: i }), u += h.length - 1;
      }
      i++;
    }
  }
  static createElement(e, r) {
    const a = b.createElement("template");
    return a.innerHTML = e, a;
  }
}
function y(t, e, r = t, a) {
  var n, i, o, l;
  if (e === x) return e;
  let s = a !== void 0 ? (n = r._$Co) === null || n === void 0 ? void 0 : n[a] : r._$Cl;
  const c = R(e) ? void 0 : e._$litDirective$;
  return (s == null ? void 0 : s.constructor) !== c && ((i = s == null ? void 0 : s._$AO) === null || i === void 0 || i.call(s, !1), c === void 0 ? s = void 0 : (s = new c(t), s._$AT(t, r, a)), a !== void 0 ? ((o = (l = r)._$Co) !== null && o !== void 0 ? o : l._$Co = [])[a] = s : r._$Cl = s), s !== void 0 && (e = y(t, s._$AS(t, e.values), s, a)), e;
}
class rr {
  constructor(e, r) {
    this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = r;
  }
  get parentNode() {
    return this._$AM.parentNode;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  u(e) {
    var r;
    const { el: { content: a }, parts: n } = this._$AD, i = ((r = e == null ? void 0 : e.creationScope) !== null && r !== void 0 ? r : b).importNode(a, !0);
    p.currentNode = i;
    let o = p.nextNode(), l = 0, s = 0, c = n[0];
    for (; c !== void 0; ) {
      if (l === c.index) {
        let d;
        c.type === 2 ? d = new N(o, o.nextSibling, this, e) : c.type === 1 ? d = new c.ctor(o, c.name, c.strings, this, e) : c.type === 6 && (d = new or(o, this, e)), this._$AV.push(d), c = n[++s];
      }
      l !== (c == null ? void 0 : c.index) && (o = p.nextNode(), l++);
    }
    return p.currentNode = b, i;
  }
  v(e) {
    let r = 0;
    for (const a of this._$AV) a !== void 0 && (a.strings !== void 0 ? (a._$AI(e, a, r), r += a.strings.length - 2) : a._$AI(e[r])), r++;
  }
}
class N {
  constructor(e, r, a, n) {
    var i;
    this.type = 2, this._$AH = v, this._$AN = void 0, this._$AA = e, this._$AB = r, this._$AM = a, this.options = n, this._$Cp = (i = n == null ? void 0 : n.isConnected) === null || i === void 0 || i;
  }
  get _$AU() {
    var e, r;
    return (r = (e = this._$AM) === null || e === void 0 ? void 0 : e._$AU) !== null && r !== void 0 ? r : this._$Cp;
  }
  get parentNode() {
    let e = this._$AA.parentNode;
    const r = this._$AM;
    return r !== void 0 && (e == null ? void 0 : e.nodeType) === 11 && (e = r.parentNode), e;
  }
  get startNode() {
    return this._$AA;
  }
  get endNode() {
    return this._$AB;
  }
  _$AI(e, r = this) {
    e = y(this, e, r), R(e) ? e === v || e == null || e === "" ? (this._$AH !== v && this._$AR(), this._$AH = v) : e !== this._$AH && e !== x && this._(e) : e._$litType$ !== void 0 ? this.g(e) : e.nodeType !== void 0 ? this.$(e) : Ye(e) ? this.T(e) : this._(e);
  }
  k(e) {
    return this._$AA.parentNode.insertBefore(e, this._$AB);
  }
  $(e) {
    this._$AH !== e && (this._$AR(), this._$AH = this.k(e));
  }
  _(e) {
    this._$AH !== v && R(this._$AH) ? this._$AA.nextSibling.data = e : this.$(b.createTextNode(e)), this._$AH = e;
  }
  g(e) {
    var r;
    const { values: a, _$litType$: n } = e, i = typeof n == "number" ? this._$AC(e) : (n.el === void 0 && (n.el = O.createElement(He(n.h, n.h[0]), this.options)), n);
    if (((r = this._$AH) === null || r === void 0 ? void 0 : r._$AD) === i) this._$AH.v(a);
    else {
      const o = new rr(i, this), l = o.u(this.options);
      o.v(a), this.$(l), this._$AH = o;
    }
  }
  _$AC(e) {
    let r = _e.get(e.strings);
    return r === void 0 && _e.set(e.strings, r = new O(e)), r;
  }
  T(e) {
    ke(this._$AH) || (this._$AH = [], this._$AR());
    const r = this._$AH;
    let a, n = 0;
    for (const i of e) n === r.length ? r.push(a = new N(this.k(P()), this.k(P()), this, this.options)) : a = r[n], a._$AI(i), n++;
    n < r.length && (this._$AR(a && a._$AB.nextSibling, n), r.length = n);
  }
  _$AR(e = this._$AA.nextSibling, r) {
    var a;
    for ((a = this._$AP) === null || a === void 0 || a.call(this, !1, !0, r); e && e !== this._$AB; ) {
      const n = e.nextSibling;
      e.remove(), e = n;
    }
  }
  setConnected(e) {
    var r;
    this._$AM === void 0 && (this._$Cp = e, (r = this._$AP) === null || r === void 0 || r.call(this, e));
  }
}
class z {
  constructor(e, r, a, n, i) {
    this.type = 1, this._$AH = v, this._$AN = void 0, this.element = e, this.name = r, this._$AM = n, this.options = i, a.length > 2 || a[0] !== "" || a[1] !== "" ? (this._$AH = Array(a.length - 1).fill(new String()), this.strings = a) : this._$AH = v;
  }
  get tagName() {
    return this.element.tagName;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e, r = this, a, n) {
    const i = this.strings;
    let o = !1;
    if (i === void 0) e = y(this, e, r, 0), o = !R(e) || e !== this._$AH && e !== x, o && (this._$AH = e);
    else {
      const l = e;
      let s, c;
      for (e = i[0], s = 0; s < i.length - 1; s++) c = y(this, l[a + s], r, s), c === x && (c = this._$AH[s]), o || (o = !R(c) || c !== this._$AH[s]), c === v ? e = v : e !== v && (e += (c ?? "") + i[s + 1]), this._$AH[s] = c;
    }
    o && !n && this.j(e);
  }
  j(e) {
    e === v ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
  }
}
class ar extends z {
  constructor() {
    super(...arguments), this.type = 3;
  }
  j(e) {
    this.element[this.name] = e === v ? void 0 : e;
  }
}
const tr = _ ? _.emptyScript : "";
class nr extends z {
  constructor() {
    super(...arguments), this.type = 4;
  }
  j(e) {
    e && e !== v ? this.element.setAttribute(this.name, tr) : this.element.removeAttribute(this.name);
  }
}
class ir extends z {
  constructor(e, r, a, n, i) {
    super(e, r, a, n, i), this.type = 5;
  }
  _$AI(e, r = this) {
    var a;
    if ((e = (a = y(this, e, r, 0)) !== null && a !== void 0 ? a : v) === x) return;
    const n = this._$AH, i = e === v && n !== v || e.capture !== n.capture || e.once !== n.once || e.passive !== n.passive, o = e !== v && (n === v || i);
    i && this.element.removeEventListener(this.name, this, n), o && this.element.addEventListener(this.name, this, e), this._$AH = e;
  }
  handleEvent(e) {
    var r, a;
    typeof this._$AH == "function" ? this._$AH.call((a = (r = this.options) === null || r === void 0 ? void 0 : r.host) !== null && a !== void 0 ? a : this.element, e) : this._$AH.handleEvent(e);
  }
}
class or {
  constructor(e, r, a) {
    this.element = e, this.type = 6, this._$AN = void 0, this._$AM = r, this.options = a;
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AI(e) {
    y(this, e);
  }
}
const ye = q.litHtmlPolyfillSupport;
ye == null || ye(O, N), ((V = q.litHtmlVersions) !== null && V !== void 0 ? V : q.litHtmlVersions = []).push("2.8.0");
const sr = (t, e, r) => {
  var a, n;
  const i = (a = r == null ? void 0 : r.renderBefore) !== null && a !== void 0 ? a : e;
  let o = i._$litPart$;
  if (o === void 0) {
    const l = (n = r == null ? void 0 : r.renderBefore) !== null && n !== void 0 ? n : null;
    i._$litPart$ = o = new N(e.insertBefore(P(), l), l, void 0, r ?? {});
  }
  return o._$AI(t), o;
};
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const M = window, de = M.ShadowRoot && (M.ShadyCSS === void 0 || M.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, ve = Symbol(), Ae = /* @__PURE__ */ new WeakMap();
let Ie = class {
  constructor(e, r, a) {
    if (this._$cssResult$ = !0, a !== ve) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
    this.cssText = e, this.t = r;
  }
  get styleSheet() {
    let e = this.o;
    const r = this.t;
    if (de && e === void 0) {
      const a = r !== void 0 && r.length === 1;
      a && (e = Ae.get(r)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), a && Ae.set(r, e));
    }
    return e;
  }
  toString() {
    return this.cssText;
  }
};
const lr = (t) => new Ie(typeof t == "string" ? t : t + "", void 0, ve), cr = (t, ...e) => {
  const r = t.length === 1 ? t[0] : e.reduce(((a, n, i) => a + ((o) => {
    if (o._$cssResult$ === !0) return o.cssText;
    if (typeof o == "number") return o;
    throw Error("Value passed to 'css' function must be a 'css' function result: " + o + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
  })(n) + t[i + 1]), t[0]);
  return new Ie(r, t, ve);
}, dr = (t, e) => {
  de ? t.adoptedStyleSheets = e.map(((r) => r instanceof CSSStyleSheet ? r : r.styleSheet)) : e.forEach(((r) => {
    const a = document.createElement("style"), n = M.litNonce;
    n !== void 0 && a.setAttribute("nonce", n), a.textContent = r.cssText, t.appendChild(a);
  }));
}, Ee = de ? (t) => t : (t) => t instanceof CSSStyleSheet ? ((e) => {
  let r = "";
  for (const a of e.cssRules) r += a.cssText;
  return lr(r);
})(t) : t;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var J;
const j = window, we = j.trustedTypes, vr = we ? we.emptyScript : "", Se = j.reactiveElementPolyfillSupport, te = { toAttribute(t, e) {
  switch (e) {
    case Boolean:
      t = t ? vr : null;
      break;
    case Object:
    case Array:
      t = t == null ? t : JSON.stringify(t);
  }
  return t;
}, fromAttribute(t, e) {
  let r = t;
  switch (e) {
    case Boolean:
      r = t !== null;
      break;
    case Number:
      r = t === null ? null : Number(t);
      break;
    case Object:
    case Array:
      try {
        r = JSON.parse(t);
      } catch {
        r = null;
      }
  }
  return r;
} }, qe = (t, e) => e !== t && (e == e || t == t), F = { attribute: !0, type: String, converter: te, reflect: !1, hasChanged: qe }, ne = "finalized";
class $ extends HTMLElement {
  constructor() {
    super(), this._$Ei = /* @__PURE__ */ new Map(), this.isUpdatePending = !1, this.hasUpdated = !1, this._$El = null, this._$Eu();
  }
  static addInitializer(e) {
    var r;
    this.finalize(), ((r = this.h) !== null && r !== void 0 ? r : this.h = []).push(e);
  }
  static get observedAttributes() {
    this.finalize();
    const e = [];
    return this.elementProperties.forEach(((r, a) => {
      const n = this._$Ep(a, r);
      n !== void 0 && (this._$Ev.set(n, a), e.push(n));
    })), e;
  }
  static createProperty(e, r = F) {
    if (r.state && (r.attribute = !1), this.finalize(), this.elementProperties.set(e, r), !r.noAccessor && !this.prototype.hasOwnProperty(e)) {
      const a = typeof e == "symbol" ? Symbol() : "__" + e, n = this.getPropertyDescriptor(e, a, r);
      n !== void 0 && Object.defineProperty(this.prototype, e, n);
    }
  }
  static getPropertyDescriptor(e, r, a) {
    return { get() {
      return this[r];
    }, set(n) {
      const i = this[e];
      this[r] = n, this.requestUpdate(e, i, a);
    }, configurable: !0, enumerable: !0 };
  }
  static getPropertyOptions(e) {
    return this.elementProperties.get(e) || F;
  }
  static finalize() {
    if (this.hasOwnProperty(ne)) return !1;
    this[ne] = !0;
    const e = Object.getPrototypeOf(this);
    if (e.finalize(), e.h !== void 0 && (this.h = [...e.h]), this.elementProperties = new Map(e.elementProperties), this._$Ev = /* @__PURE__ */ new Map(), this.hasOwnProperty("properties")) {
      const r = this.properties, a = [...Object.getOwnPropertyNames(r), ...Object.getOwnPropertySymbols(r)];
      for (const n of a) this.createProperty(n, r[n]);
    }
    return this.elementStyles = this.finalizeStyles(this.styles), !0;
  }
  static finalizeStyles(e) {
    const r = [];
    if (Array.isArray(e)) {
      const a = new Set(e.flat(1 / 0).reverse());
      for (const n of a) r.unshift(Ee(n));
    } else e !== void 0 && r.push(Ee(e));
    return r;
  }
  static _$Ep(e, r) {
    const a = r.attribute;
    return a === !1 ? void 0 : typeof a == "string" ? a : typeof e == "string" ? e.toLowerCase() : void 0;
  }
  _$Eu() {
    var e;
    this._$E_ = new Promise(((r) => this.enableUpdating = r)), this._$AL = /* @__PURE__ */ new Map(), this._$Eg(), this.requestUpdate(), (e = this.constructor.h) === null || e === void 0 || e.forEach(((r) => r(this)));
  }
  addController(e) {
    var r, a;
    ((r = this._$ES) !== null && r !== void 0 ? r : this._$ES = []).push(e), this.renderRoot !== void 0 && this.isConnected && ((a = e.hostConnected) === null || a === void 0 || a.call(e));
  }
  removeController(e) {
    var r;
    (r = this._$ES) === null || r === void 0 || r.splice(this._$ES.indexOf(e) >>> 0, 1);
  }
  _$Eg() {
    this.constructor.elementProperties.forEach(((e, r) => {
      this.hasOwnProperty(r) && (this._$Ei.set(r, this[r]), delete this[r]);
    }));
  }
  createRenderRoot() {
    var e;
    const r = (e = this.shadowRoot) !== null && e !== void 0 ? e : this.attachShadow(this.constructor.shadowRootOptions);
    return dr(r, this.constructor.elementStyles), r;
  }
  connectedCallback() {
    var e;
    this.renderRoot === void 0 && (this.renderRoot = this.createRenderRoot()), this.enableUpdating(!0), (e = this._$ES) === null || e === void 0 || e.forEach(((r) => {
      var a;
      return (a = r.hostConnected) === null || a === void 0 ? void 0 : a.call(r);
    }));
  }
  enableUpdating(e) {
  }
  disconnectedCallback() {
    var e;
    (e = this._$ES) === null || e === void 0 || e.forEach(((r) => {
      var a;
      return (a = r.hostDisconnected) === null || a === void 0 ? void 0 : a.call(r);
    }));
  }
  attributeChangedCallback(e, r, a) {
    this._$AK(e, a);
  }
  _$EO(e, r, a = F) {
    var n;
    const i = this.constructor._$Ep(e, a);
    if (i !== void 0 && a.reflect === !0) {
      const o = (((n = a.converter) === null || n === void 0 ? void 0 : n.toAttribute) !== void 0 ? a.converter : te).toAttribute(r, a.type);
      this._$El = e, o == null ? this.removeAttribute(i) : this.setAttribute(i, o), this._$El = null;
    }
  }
  _$AK(e, r) {
    var a;
    const n = this.constructor, i = n._$Ev.get(e);
    if (i !== void 0 && this._$El !== i) {
      const o = n.getPropertyOptions(i), l = typeof o.converter == "function" ? { fromAttribute: o.converter } : ((a = o.converter) === null || a === void 0 ? void 0 : a.fromAttribute) !== void 0 ? o.converter : te;
      this._$El = i, this[i] = l.fromAttribute(r, o.type), this._$El = null;
    }
  }
  requestUpdate(e, r, a) {
    let n = !0;
    e !== void 0 && (((a = a || this.constructor.getPropertyOptions(e)).hasChanged || qe)(this[e], r) ? (this._$AL.has(e) || this._$AL.set(e, r), a.reflect === !0 && this._$El !== e && (this._$EC === void 0 && (this._$EC = /* @__PURE__ */ new Map()), this._$EC.set(e, a))) : n = !1), !this.isUpdatePending && n && (this._$E_ = this._$Ej());
  }
  async _$Ej() {
    this.isUpdatePending = !0;
    try {
      await this._$E_;
    } catch (r) {
      Promise.reject(r);
    }
    const e = this.scheduleUpdate();
    return e != null && await e, !this.isUpdatePending;
  }
  scheduleUpdate() {
    return this.performUpdate();
  }
  performUpdate() {
    var e;
    if (!this.isUpdatePending) return;
    this.hasUpdated, this._$Ei && (this._$Ei.forEach(((n, i) => this[i] = n)), this._$Ei = void 0);
    let r = !1;
    const a = this._$AL;
    try {
      r = this.shouldUpdate(a), r ? (this.willUpdate(a), (e = this._$ES) === null || e === void 0 || e.forEach(((n) => {
        var i;
        return (i = n.hostUpdate) === null || i === void 0 ? void 0 : i.call(n);
      })), this.update(a)) : this._$Ek();
    } catch (n) {
      throw r = !1, this._$Ek(), n;
    }
    r && this._$AE(a);
  }
  willUpdate(e) {
  }
  _$AE(e) {
    var r;
    (r = this._$ES) === null || r === void 0 || r.forEach(((a) => {
      var n;
      return (n = a.hostUpdated) === null || n === void 0 ? void 0 : n.call(a);
    })), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
  }
  _$Ek() {
    this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
  }
  get updateComplete() {
    return this.getUpdateComplete();
  }
  getUpdateComplete() {
    return this._$E_;
  }
  shouldUpdate(e) {
    return !0;
  }
  update(e) {
    this._$EC !== void 0 && (this._$EC.forEach(((r, a) => this._$EO(a, this[a], r))), this._$EC = void 0), this._$Ek();
  }
  updated(e) {
  }
  firstUpdated(e) {
  }
}
$[ne] = !0, $.elementProperties = /* @__PURE__ */ new Map(), $.elementStyles = [], $.shadowRootOptions = { mode: "open" }, Se == null || Se({ ReactiveElement: $ }), ((J = j.reactiveElementVersions) !== null && J !== void 0 ? J : j.reactiveElementVersions = []).push("1.6.3");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var K, Z;
let L = class extends $ {
  constructor() {
    super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
  }
  createRenderRoot() {
    var e, r;
    const a = super.createRenderRoot();
    return (e = (r = this.renderOptions).renderBefore) !== null && e !== void 0 || (r.renderBefore = a.firstChild), a;
  }
  update(e) {
    const r = this.render();
    this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = sr(r, this.renderRoot, this.renderOptions);
  }
  connectedCallback() {
    var e;
    super.connectedCallback(), (e = this._$Do) === null || e === void 0 || e.setConnected(!0);
  }
  disconnectedCallback() {
    var e;
    super.disconnectedCallback(), (e = this._$Do) === null || e === void 0 || e.setConnected(!1);
  }
  render() {
    return x;
  }
};
L.finalized = !0, L._$litElement$ = !0, (K = globalThis.litElementHydrateSupport) === null || K === void 0 || K.call(globalThis, { LitElement: L });
const Ce = globalThis.litElementPolyfillSupport;
Ce == null || Ce({ LitElement: L });
((Z = globalThis.litElementVersions) !== null && Z !== void 0 ? Z : globalThis.litElementVersions = []).push("3.3.3");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Lr = (t) => (e) => typeof e == "function" ? ((r, a) => (customElements.define(r, a), a))(t, e) : ((r, a) => {
  const { kind: n, elements: i } = a;
  return { kind: n, elements: i, finisher(o) {
    customElements.define(r, o);
  } };
})(t, e);
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ur = (t, e) => e.kind === "method" && e.descriptor && !("value" in e.descriptor) ? { ...e, finisher(r) {
  r.createProperty(e.key, t);
} } : { kind: "field", key: Symbol(), placement: "own", descriptor: {}, originalKey: e.key, initializer() {
  typeof e.initializer == "function" && (this[e.key] = e.initializer.call(this));
}, finisher(r) {
  r.createProperty(e.key, t);
} }, mr = (t, e, r) => {
  e.constructor.createProperty(r, t);
};
function fr(t) {
  return (e, r) => r !== void 0 ? mr(t, e, r) : ur(t, e);
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function Hr(t) {
  return fr({ ...t, state: !0 });
}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
var Q;
((Q = window.HTMLSlotElement) === null || Q === void 0 ? void 0 : Q.prototype.assignedElements) != null;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const je = { CHILD: 2 }, De = (t) => (...e) => ({ _$litDirective$: t, values: e });
class ze {
  constructor(e) {
  }
  get _$AU() {
    return this._$AM._$AU;
  }
  _$AT(e, r, a) {
    this._$Ct = e, this._$AM = r, this._$Ci = a;
  }
  _$AS(e, r) {
    return this.update(e, r);
  }
  update(e, r) {
    return this.render(...r);
  }
}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
let ie = class extends ze {
  constructor(e) {
    if (super(e), this.et = v, e.type !== je.CHILD) throw Error(this.constructor.directiveName + "() can only be used in child bindings");
  }
  render(e) {
    if (e === v || e == null) return this.ft = void 0, this.et = e;
    if (e === x) return e;
    if (typeof e != "string") throw Error(this.constructor.directiveName + "() called with a non-string value");
    if (e === this.et) return this.ft;
    this.et = e;
    const r = [e];
    return r.raw = r, this.ft = { _$litType$: this.constructor.resultType, strings: r, values: [] };
  }
};
ie.directiveName = "unsafeHTML", ie.resultType = 1;
const qr = De(ie);
function hr(t) {
  return t && t.__esModule && Object.prototype.hasOwnProperty.call(t, "default") ? t.default : t;
}
var X = { exports: {} };
/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/
var Ue;
function gr() {
  return Ue || (Ue = 1, (function(t) {
    (function() {
      var e = {}.hasOwnProperty;
      function r() {
        for (var i = "", o = 0; o < arguments.length; o++) {
          var l = arguments[o];
          l && (i = n(i, a(l)));
        }
        return i;
      }
      function a(i) {
        if (typeof i == "string" || typeof i == "number")
          return i;
        if (typeof i != "object")
          return "";
        if (Array.isArray(i))
          return r.apply(null, i);
        if (i.toString !== Object.prototype.toString && !i.toString.toString().includes("[native code]"))
          return i.toString();
        var o = "";
        for (var l in i)
          e.call(i, l) && i[l] && (o = n(o, l));
        return o;
      }
      function n(i, o) {
        return o ? i ? i + " " + o : i + o : i;
      }
      t.exports ? (r.default = r, t.exports = r) : window.classNames = r;
    })();
  })(X)), X.exports;
}
var pr = gr();
const jr = /* @__PURE__ */ hr(pr);
class Dr {
  constructor({ spotlightContainerRef: e }) {
    this._spotlightContainerRef = e;
  }
  set contentEl(e) {
    this._contentEl = e;
  }
  update({ spotlighted: e = [] }) {
    if (!this._contentEl || !this._spotlightContainerRef.value) return;
    this._contentEl.querySelectorAll("[data-id]").forEach((a) => {
      const n = a.getAttribute("data-id");
      n && e.includes(n) ? a.classList.add("spotlighted") : a.classList.remove("spotlighted");
    }), e.length === 0 ? this._spotlightContainerRef.value.classList.remove(
      "spotlight-container-active"
    ) : this._spotlightContainerRef.value.classList.add(
      "spotlight-container-active"
    );
  }
}
const zr = cr`
  .spotlight-container {
    --fade-amount: 0;
  }

  .spotlight-container-active {
    --fade-amount: 0.8;
  }

  .spotlight-container {
    --spotlight-transition-duration: var(--duration-long);

    /* Adjustable Vars */
    --inverse-fade-amount: calc(1 - var(--fade-amount));
    --mixed-red: calc(var(--fade-amount) * var(--background-red));
    --mixed-green: calc(var(--fade-amount) * var(--background-green));
    --mixed-blue: calc(var(--fade-amount) * var(--background-blue));

    /* Utility Colors */
    --color-white: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-black: var(--color-neutral-90);
    --color-gray: var(--color-neutral-50);
    --color-brand: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(179 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(229 * var(--inverse-fade-amount) + var(--mixed-blue))
    );

    /* Color Rainbow */
    --color-neutral-05: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-10: rgb(
      calc(228 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(237 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-20: rgb(
      calc(193 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(201 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(208 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-30: rgb(
      calc(164 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(171 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(183 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-40: rgb(
      calc(137 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(146 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(158 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-50: rgb(
      calc(107 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(115 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(132 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-60: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(86 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(105 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-70: rgb(
      calc(62 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(64 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(84 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-80: rgb(
      calc(42 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(47 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(68 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-neutral-90: rgb(
      calc(24 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(29 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-05: rgb(
      calc(254 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(244 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-10: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(227 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(222 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-20: rgb(
      calc(241 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(184 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(181 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-30: rgb(
      calc(234 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(137 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-40: rgb(
      calc(220 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(104 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-50: rgb(
      calc(190 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(73 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(103 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-60: rgb(
      calc(151 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(42 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(78 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-70: rgb(
      calc(117 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(31 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(64 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-80: rgb(
      calc(86 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(57 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-red-90: rgb(
      calc(60 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(10 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(39 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-05: rgb(
      calc(254 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(238 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-10: rgb(
      calc(250 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(228 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(196 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-20: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(186 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(141 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-30: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(149 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(101 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-40: rgb(
      calc(214 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(117 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-50: rgb(
      calc(181 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(84 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(58 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-60: rgb(
      calc(145 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(46 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-70: rgb(
      calc(116 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(38 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(38 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-80: rgb(
      calc(87 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(25 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(31 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-orange-90: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(19 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-05: rgb(
      calc(251 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(249 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(235 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-10: rgb(
      calc(245 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(229 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(189 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-20: rgb(
      calc(232 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(194 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(129 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-30: rgb(
      calc(217 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(157 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-40: rgb(
      calc(203 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(51 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-50: rgb(
      calc(175 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(89 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-60: rgb(
      calc(141 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(61 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-70: rgb(
      calc(108 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(47 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(20 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-80: rgb(
      calc(80 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-yellow-90: rgb(
      calc(53 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(22 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(9 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-05: rgb(
      calc(242 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(240 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-10: rgb(
      calc(211 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(242 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(205 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-20: rgb(
      calc(151 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(214 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(156 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-30: rgb(
      calc(96 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(191 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(135 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-40: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(164 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-50: rgb(
      calc(58 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(128 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(96 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-60: rgb(
      calc(43 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(97 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(70 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-70: rgb(
      calc(32 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(75 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-80: rgb(
      calc(23 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(52 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-green-90: rgb(
      calc(14 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(34 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(39 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-05: rgb(
      calc(236 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-10: rgb(
      calc(185 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(239 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-20: rgb(
      calc(135 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(222 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(234 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-30: rgb(
      calc(76 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(193 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(209 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-40: rgb(
      calc(31 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(156 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(173 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-50: rgb(
      calc(9 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(141 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-60: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(98 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(111 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-70: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(77 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(88 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-80: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(54 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(62 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-turquoise-90: rgb(
      calc(0 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(41 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(48 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-05: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(252 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-10: rgb(
      calc(204 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-20: rgb(
      calc(145 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(209 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(234 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-30: rgb(
      calc(105 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(180 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(226 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-40: rgb(
      calc(84 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(150 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(207 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-50: rgb(
      calc(54 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(120 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(180 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-60: rgb(
      calc(36 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(87 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-70: rgb(
      calc(27 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(69 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(117 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-80: rgb(
      calc(21 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(79 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-cyan-90: rgb(
      calc(11 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(33 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-05: rgb(
      calc(245 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-10: rgb(
      calc(217 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(236 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(253 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-20: rgb(
      calc(172 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(204 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(251 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-30: rgb(
      calc(133 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(170 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-40: rgb(
      calc(114 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(230 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-50: rgb(
      calc(88 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(105 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(205 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-60: rgb(
      calc(64 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(76 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(166 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-70: rgb(
      calc(49 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(134 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-80: rgb(
      calc(35 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(97 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-blue-90: rgb(
      calc(19 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(63 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-05: rgb(
      calc(248 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(249 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(254 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-10: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(230 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(250 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-20: rgb(
      calc(196 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(195 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-30: rgb(
      calc(172 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(161 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(220 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-40: rgb(
      calc(152 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(130 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(213 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-50: rgb(
      calc(126 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(98 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(188 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-60: rgb(
      calc(93 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(72 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(151 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-70: rgb(
      calc(71 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(52 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(126 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-80: rgb(
      calc(51 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(37 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(96 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-violet-90: rgb(
      calc(29 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(23 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(75 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-05: rgb(
      calc(253 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-10: rgb(
      calc(247 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(225 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(245 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-20: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(182 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(225 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-30: rgb(
      calc(215 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(216 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-40: rgb(
      calc(189 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(114 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(203 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-50: rgb(
      calc(152 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(85 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(175 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-60: rgb(
      calc(113 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(60 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(146 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-70: rgb(
      calc(85 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(45 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(125 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-80: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(102 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-purple-90: rgb(
      calc(40 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(15 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(82 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-05: rgb(
      calc(249 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(241 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-10: rgb(
      calc(239 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(232 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(219 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-20: rgb(
      calc(215 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(202 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(176 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-30: rgb(
      calc(187 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(170 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(136 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-40: rgb(
      calc(163 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(145 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(110 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-50: rgb(
      calc(129 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(111 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(77 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-60: rgb(
      calc(100 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(85 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(55 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-70: rgb(
      calc(80 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(67 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(41 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-80: rgb(
      calc(59 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(49 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(28 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-tan-90: rgb(
      calc(37 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(30 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(17 * var(--inverse-fade-amount) + var(--mixed-blue))
    );

    /* Highlight Colors */
    --color-highlight-yellow-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(227 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(79 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-yellow-2: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(247 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-pink-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(61 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(201 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-pink-2: rgb(
      calc(230 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(128 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-orange-1: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(140 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(57 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-orange-2: rgb(
      calc(255 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(192 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(70 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-blue-1: rgb(
      calc(79 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(223 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-blue-2: rgb(
      calc(84 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(214 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-green-1: rgb(
      calc(41 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(248 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(62 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
    --color-highlight-green-2: rgb(
      calc(175 * var(--inverse-fade-amount) + var(--mixed-red)),
      calc(255 * var(--inverse-fade-amount) + var(--mixed-green)),
      calc(44 * var(--inverse-fade-amount) + var(--mixed-blue))
    );
  }

  .spotlighted {
    --fade-amount: 0;
    --inverse-fade-amount: 1;

    /* Utility Colors */
    --color-white: #ffffff;
    --color-black: var(--color-neutral-90);
    --color-gray: var(--color-neutral-50);
    --color-brand: #00b3e5;

    /* Color Rainbow */
    --color-neutral-05: #f9fafc;
    --color-neutral-10: #e4e8ed;
    --color-neutral-20: #c1c9d0;
    --color-neutral-30: #a4abb7;
    --color-neutral-40: #89929e;
    --color-neutral-50: #6b7384;
    --color-neutral-60: #4f5669;
    --color-neutral-70: #3e4054;
    --color-neutral-80: #2a2f44;
    --color-neutral-90: #181d36;
    --color-red-05: #fef8f4;
    --color-red-10: #f9e3de;
    --color-red-20: #f1b8b5;
    --color-red-30: #ea898c;
    --color-red-40: #dc6878;
    --color-red-50: #be4967;
    --color-red-60: #972a4e;
    --color-red-70: #751f40;
    --color-red-80: #561739;
    --color-red-90: #3c0a27;
    --color-orange-05: #fefaee;
    --color-orange-10: #fae4c4;
    --color-orange-20: #efba8d;
    --color-orange-30: #e69565;
    --color-orange-40: #d67552;
    --color-orange-50: #b5543a;
    --color-orange-60: #91362e;
    --color-orange-70: #742626;
    --color-orange-80: #57191f;
    --color-orange-90: #3b1113;
    --color-yellow-05: #fbf9eb;
    --color-yellow-10: #f5e5bd;
    --color-yellow-20: #e8c281;
    --color-yellow-30: #d99d52;
    --color-yellow-40: #cb7d33;
    --color-yellow-50: #af5922;
    --color-yellow-60: #8d3d17;
    --color-yellow-70: #6c2f14;
    --color-yellow-80: #502211;
    --color-yellow-90: #351609;
    --color-green-05: #f2fef0;
    --color-green-10: #d3f2cd;
    --color-green-20: #97d69c;
    --color-green-30: #60bf87;
    --color-green-40: #4fa478;
    --color-green-50: #3a8060;
    --color-green-60: #2b6146;
    --color-green-70: #204b3c;
    --color-green-80: #173634;
    --color-green-90: #0e2227;
    --color-turquoise-05: #ecfbfe;
    --color-turquoise-10: #b9eff7;
    --color-turquoise-20: #87deea;
    --color-turquoise-30: #4cc1d1;
    --color-turquoise-40: #1f9cad;
    --color-turquoise-50: #097d8d;
    --color-turquoise-60: #00626f;
    --color-turquoise-70: #004d58;
    --color-turquoise-80: #00363e;
    --color-turquoise-90: #002930;
    --color-cyan-05: #effcfc;
    --color-cyan-10: #ccf1fa;
    --color-cyan-20: #91d1ea;
    --color-cyan-30: #69b4e2;
    --color-cyan-40: #5496cf;
    --color-cyan-50: #3678b4;
    --color-cyan-60: #245791;
    --color-cyan-70: #1b4575;
    --color-cyan-80: #15314f;
    --color-cyan-90: #0b2131;
    --color-blue-05: #f5fbff;
    --color-blue-10: #d9ecfd;
    --color-blue-20: #acccfb;
    --color-blue-30: #85aaf1;
    --color-blue-40: #728ce6;
    --color-blue-50: #5869cd;
    --color-blue-60: #404ca6;
    --color-blue-70: #313c86;
    --color-blue-80: #232c61;
    --color-blue-90: #131e3f;
    --color-violet-05: #f8f9fe;
    --color-violet-10: #e6e6fa;
    --color-violet-20: #c4c3e8;
    --color-violet-30: #aca1dc;
    --color-violet-40: #9882d5;
    --color-violet-50: #7e62bc;
    --color-violet-60: #5d4897;
    --color-violet-70: #47347e;
    --color-violet-80: #332560;
    --color-violet-90: #1d174b;
    --color-purple-05: #fdf8ff;
    --color-purple-10: #f7e1f5;
    --color-purple-20: #e6b6e1;
    --color-purple-30: #d791d8;
    --color-purple-40: #bd72cb;
    --color-purple-50: #9855af;
    --color-purple-60: #713c92;
    --color-purple-70: #552d7d;
    --color-purple-80: #3b1e66;
    --color-purple-90: #280f52;
    --color-tan-05: #f9f7f1;
    --color-tan-10: #efe8db;
    --color-tan-20: #d7cab0;
    --color-tan-30: #bbaa88;
    --color-tan-40: #a3916e;
    --color-tan-50: #816f4d;
    --color-tan-60: #645537;
    --color-tan-70: #504329;
    --color-tan-80: #3b311c;
    --color-tan-90: #251e11;

    /* Highlight Colors */
    --color-highlight-yellow-1: #ffe34f;
    --color-highlight-yellow-2: #fff72c;
    --color-highlight-pink-1: #ff3dc9;
    --color-highlight-pink-2: #e680ff;
    --color-highlight-orange-1: #ff8c39;
    --color-highlight-orange-2: #ffc046;
    --color-highlight-blue-1: #4fdfff;
    --color-highlight-blue-2: #54ffd6;
    --color-highlight-green-1: #29f83e;
    --color-highlight-green-2: #afff2c;
  }
`;
var w = {};
const Pe = "__bp__";
let oe = {
  env: {
    API_URL: w.API_URL ?? "/services/graphql/",
    DEBUG: !0,
    LANGUAGE: w.LANGUAGE ?? "en",
    USER_API_URL: w.USER_API_URL ?? "/services/current-user/",
    NEWSLETTER_API_URL: w.NEWSLETTER_API_URL ?? "/services/newsletter/",
    ROOT: w.ROOT
  }
};
function se(t, e) {
  return oe.env[t] ?? e;
}
function br(t, e) {
  if (e) {
    for (const [r, a] of Object.entries(t.env))
      typeof e.env[r] > "u" && (e.env[r] = a);
    return e;
  }
  return t;
}
typeof window < "u" && (oe = window[Pe] = br(oe, window[Pe]));
function xr(...t) {
  return t.map((e) => e.replace(/^\/|\/$/g, "")).join("/");
}
function $r(t, e = se("ROOT", import.meta.url)) {
  const r = (e == null ? void 0 : e.replace(/[^/]+\/?$/, "")) ?? "";
  return xr(r, t);
}
function _r(t = 1e3) {
  return new Promise((e) => {
    setTimeout(e, t);
  });
}
const S = {
  Timeout: "TIMEOUT",
  NetworkFailure: "NETWORK_FAILURE",
  Aborted: "ABORTED"
};
class C extends Error {
  constructor(e, r, a) {
    super(e), this.reason = r, this.detail = a, this.name = "BpNetworkError";
  }
}
async function Br(t, e) {
  return new Promise((r, a) => {
    const n = $r(t);
    fetch(n, { signal: e }).then(async (i) => {
      const o = await i.text();
      i.ok || a(o), r(o);
    }).catch((i) => a(i));
  });
}
function Re(t, e) {
  return e && e.status >= 400 && e.status < 500 ? !1 : e && e.status >= 500 || t instanceof Error && (t.name === "AbortError" || t.name === "TypeError") ? !0 : t instanceof C ? t.reason === S.Timeout || t.reason === S.NetworkFailure : !0;
}
async function Be(t, e, r = {}) {
  var c;
  const { retries: a = 2, delay: n = 1e3, timeout: i = 3e4 } = r, o = async () => (await _r(n), Be(t, e, {
    retries: a - 1,
    delay: n * 2,
    timeout: i
  })), l = new AbortController(), s = setTimeout(() => l.abort(), i);
  e != null && e.signal && e.signal.addEventListener("abort", () => l.abort());
  try {
    const d = await fetch(t, {
      ...e,
      signal: l.signal
    });
    return clearTimeout(s), !d.ok && a > 0 && Re(null, d) ? o() : d;
  } catch (d) {
    if (clearTimeout(s), d instanceof Error && d.name === "AbortError") {
      if ((c = e == null ? void 0 : e.signal) != null && c.aborted)
        throw new C(
          `Request aborted: ${t}`,
          S.Aborted
        );
      if (a > 0)
        return o();
      throw new C(
        `Request timeout after ${i}ms: ${t}`,
        S.Timeout
      );
    }
    if (a > 0 && Re(d))
      return o();
    throw d instanceof Error ? new C(
      d.message,
      S.NetworkFailure,
      { url: t.toString() }
    ) : d;
  }
}
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const yr = (t) => t.strings === void 0;
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const U = (t, e) => {
  var r, a;
  const n = t._$AN;
  if (n === void 0) return !1;
  for (const i of n) (a = (r = i)._$AO) === null || a === void 0 || a.call(r, e, !1), U(i, e);
  return !0;
}, D = (t) => {
  let e, r;
  do {
    if ((e = t._$AM) === void 0) break;
    r = e._$AN, r.delete(t), t = e;
  } while ((r == null ? void 0 : r.size) === 0);
}, Ge = (t) => {
  for (let e; e = t._$AM; t = e) {
    let r = e._$AN;
    if (r === void 0) e._$AN = r = /* @__PURE__ */ new Set();
    else if (r.has(t)) break;
    r.add(t), wr(e);
  }
};
function Ar(t) {
  this._$AN !== void 0 ? (D(this), this._$AM = t, Ge(this)) : this._$AM = t;
}
function Er(t, e = !1, r = 0) {
  const a = this._$AH, n = this._$AN;
  if (n !== void 0 && n.size !== 0) if (e) if (Array.isArray(a)) for (let i = r; i < a.length; i++) U(a[i], !1), D(a[i]);
  else a != null && (U(a, !1), D(a));
  else U(this, t);
}
const wr = (t) => {
  var e, r, a, n;
  t.type == je.CHILD && ((e = (a = t)._$AP) !== null && e !== void 0 || (a._$AP = Er), (r = (n = t)._$AQ) !== null && r !== void 0 || (n._$AQ = Ar));
};
class Sr extends ze {
  constructor() {
    super(...arguments), this._$AN = void 0;
  }
  _$AT(e, r, a) {
    super._$AT(e, r, a), Ge(this), this.isConnected = e._$AU;
  }
  _$AO(e, r = !0) {
    var a, n;
    e !== this.isConnected && (this.isConnected = e, e ? (a = this.reconnected) === null || a === void 0 || a.call(this) : (n = this.disconnected) === null || n === void 0 || n.call(this)), r && (U(this, e), D(this));
  }
  setValue(e) {
    if (yr(this._$Ct)) this._$Ct._$AI(e, this);
    else {
      const r = [...this._$Ct._$AH];
      r[this._$Ci] = e, this._$Ct._$AI(r, this, 0);
    }
  }
  disconnected() {
  }
  reconnected() {
  }
}
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Gr = () => new Cr();
class Cr {
}
const Y = /* @__PURE__ */ new WeakMap(), Vr = De(class extends Sr {
  render(t) {
    return v;
  }
  update(t, [e]) {
    var r;
    const a = e !== this.G;
    return a && this.G !== void 0 && this.ot(void 0), (a || this.rt !== this.lt) && (this.G = e, this.dt = (r = t.options) === null || r === void 0 ? void 0 : r.host, this.ot(this.lt = t.element)), v;
  }
  ot(t) {
    var e;
    if (typeof this.G == "function") {
      const r = (e = this.dt) !== null && e !== void 0 ? e : globalThis;
      let a = Y.get(r);
      a === void 0 && (a = /* @__PURE__ */ new WeakMap(), Y.set(r, a)), a.get(this.G) !== void 0 && this.G.call(this.dt, void 0), a.set(this.G, t), t !== void 0 && this.G.call(this.dt, t);
    } else this.G.value = t;
  }
  get rt() {
    var t, e, r;
    return typeof this.G == "function" ? (e = Y.get((t = this.dt) !== null && t !== void 0 ? t : globalThis)) === null || e === void 0 ? void 0 : e.get(this.G) : (r = this.G) === null || r === void 0 ? void 0 : r.value;
  }
  disconnected() {
    this.rt === this.lt && this.ot(void 0);
  }
  reconnected() {
    this.ot(this.lt);
  }
}), H = {
  ServerError: "SERVER_ERROR",
  ClientError: "CLIENT_ERROR",
  JsonParseError: "JSON_PARSE_ERROR",
  MissingUrl: "MISSING_URL"
};
class le extends C {
  constructor(e, r, a) {
    super(e, r, a), this.name = "BpApiClientError";
  }
}
function Ve(t) {
  return t.reduce((e, r) => `${e}${r}`, "");
}
async function Ur(t) {
  try {
    return await t.json();
  } catch {
    throw new le(
      `Invalid JSON response from "${t.url}"`,
      H.JsonParseError
    );
  }
}
async function Pr(t = {}) {
  const e = se("API_URL");
  if (!e)
    throw new le(
      "API URL missing",
      H.MissingUrl
    );
  const r = new Headers(t.headers);
  r.set("Content-Type", "application/json"), r.set("X-BibleProject-Language", se("LANGUAGE") ?? "en");
  const a = await Be(e, {
    ...t,
    mode: "cors",
    headers: r
  }), n = await Ur(a);
  if (!a.ok) {
    const i = a.status >= 500 ? H.ServerError : H.ClientError;
    throw new le(
      `Application error code ${a.status} for "${a.url}"`,
      i,
      n
    );
  }
  return n;
}
async function We(t, e) {
  return Pr({
    method: "POST",
    body: JSON.stringify(t),
    ...e
  });
}
async function Wr(t) {
  const { data: e } = await We({
    query: Ve`
      query GetTeacherNotes($sessionId: ID!) {
        teacherNotes(sessionId: $sessionId) {
          contentHtml
          id
        }
      }
    `,
    variables: {
      sessionId: t
    }
  });
  return {
    data: e.teacherNotes
  };
}
async function Jr(t) {
  const { data: e } = await We({
    query: Ve`
      query GetSlides($sessionId: ID!) {
        unstable_slides(sessionId: $sessionId) {
          data
        }
      }
    `,
    variables: {
      sessionId: t
    }
  });
  return {
    data: {
      presentationSlides: JSON.parse(e.unstable_slides.data)
    }
  };
}
export {
  v as A,
  Dr as S,
  zr as a,
  Tr as b,
  jr as c,
  Gr as d,
  Lr as e,
  Br as f,
  se as g,
  Vr as h,
  cr as i,
  $r as j,
  Wr as k,
  De as l,
  Sr as m,
  fr as n,
  qr as o,
  Ve as p,
  We as q,
  Jr as r,
  L as s,
  Hr as t,
  Nr as x
};
