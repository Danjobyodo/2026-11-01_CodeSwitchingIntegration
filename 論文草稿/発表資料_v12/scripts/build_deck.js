const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require(process.env.APPLY_THEME || "./apply_theme.js");

const THEME = {
  name: "Magic State Indigo",
  headFontFace: "Meiryo", bodyFontFace: "Meiryo",
  colors: { dk1: "1A1C2E", lt1: "FFFFFF", dk2: "1B1F3B", lt2: "EEF1F8",
            accent1: "1B1F3B", accent2: "1FA99B", accent3: "E8A33D", accent4: "5B6BB5", accent5: "C8504B", accent6: "8A8FA8",
            hlink: "1FA99B", folHlink: "5B6BB5" },
};
const HEX = THEME.colors;

async function icon(Comp, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "D4 符号の code switching と非 Clifford 回路の厳密シミュレーション";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "Dark", background: { color: C.text2 },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.3, w: 8.8, h: 1.6, fontSize: 30, bold: true, color: C.background1, valign: "bottom", align: "left" }, text: "" } }],
  });
  pres.defineSlideMaster({
    title: "Content", background: { color: C.background1 },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.7, fontSize: 22, bold: true, color: C.text2, valign: "middle", align: "left" }, text: "" } }],
    slideNumber: { x: 9.2, y: 5.25, w: 0.5, h: 0.25, fontSize: 10, color: C.accent6 },
  });

  const card = (s, x, y, w, h, fill, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
    { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: name });
  const circleIcon = async (s, x, y, d, Comp, bg, fg, name) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg }, objectName: name + " circle" });
    const pad = d * 0.24;
    s.addImage({ data: await icon(Comp, fg), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, altText: name, objectName: name + " icon" });
  };

  // ---------- 1. title
  pres.addSection({ title: "導入" });
  let s = pres.addSlide({ masterName: "Dark", sectionTitle: "導入" });
  s.addText("Clifford 階層安定化子符号の\ncode switching を厳密に評価する", { placeholder: "title" });
  s.addText("D4 符号による T 魔法状態の準備と、非 Clifford 回路の目的に応じた古典シミュレーション",
    { x: 0.6, y: 3.05, w: 8.8, h: 0.7, fontSize: 16, color: HEX.accent2, isTextBox: true, objectName: "subtitle" });
  s.addText("3 つのシミュレーション研究と 2 つの成果の要約", { x: 0.6, y: 4.6, w: 8.8, h: 0.4, fontSize: 12, color: "C9CCDA", isTextBox: true, objectName: "tagline" });
  await circleIcon(s, 8.5, 0.5, 0.9, fa.FaAtom, HEX.accent2, HEX.dk2, "atom");
  s.addNotes("量子計算機で「高価な部品」である T ゲートを安く作る新しい方法（code switching）を、近似なしのシミュレーションで評価した研究の要約です。成果は二つ：方式そのものの評価と、それを可能にした古典シミュレーション手法です。");

  // ---------- 2. background
  pres.addSection({ title: "前提と問題" });
  s = pres.addSlide({ masterName: "Content", sectionTitle: "前提と問題" });
  s.addText("量子誤り訂正には「安いゲート」と「高いゲート」がある", { placeholder: "title" });
  const cols = [
    { ic: fa.FaShieldAlt, head: "量子誤り訂正", body: "物理量子ビットの誤り率は 10⁻³ 程度。多数の物理ビットで 1 論理ビットを符号化し、パリティ検査（シンドローム）で誤りを見つけて直す。古典の誤り訂正符号と同じ発想", col: HEX.accent4 },
    { ic: fa.FaCogs, head: "Clifford：安い", body: "表面符号などで低コストに実行でき、古典計算機でも多項式時間でシミュレーションできる（Gottesman–Knill）。ただしこれだけでは万能な量子計算にならない", col: HEX.accent2 },
    { ic: fa.FaMagic, head: "T ゲート：高い", body: "万能性に必須だが表面符号では直接できない。標準解の「魔法状態蒸留」は雑音のある状態 15 個から良い状態 1 個を作る。計算全体の資源の大部分を占めうる", col: HEX.accent3 },
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.2, 2.85, 3.0, HEX.lt2, "card " + (i + 1));
    await circleIcon(s, x + 0.2, 1.38, 0.6, cols[i].ic, cols[i].col, "FFFFFF", cols[i].head);
    s.addText(cols[i].head, { x: x + 0.9, y: 1.38, w: 1.85, h: 0.6, fontSize: 14, bold: true, color: HEX.dk2, valign: "middle", margin: 0, isTextBox: true, objectName: "card head " + (i + 1) });
    s.addText(cols[i].body, { x: x + 0.2, y: 2.1, w: 2.5, h: 2.0, fontSize: 12.5, color: HEX.dk1, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "card body " + (i + 1) });
  }
  card(s, 0.5, 4.4, 9.0, 0.6, HEX.dk2, "question box");
  s.addText([{ text: "問い：", options: { bold: true, color: HEX.accent3 } }, { text: "T ゲート（魔法状態）を蒸留より安く作れないか？", options: { color: "FFFFFF" } }],
    { x: 0.7, y: 4.4, w: 8.6, h: 0.6, fontSize: 15, valign: "middle", margin: 0, isTextBox: true, objectName: "question" });
  s.addNotes("量子ビットは雑音に弱いので、古典の誤り訂正符号と同じく冗長に符号化して検査で誤りを直します。符号の上で安く実行できるのは Clifford と呼ばれるゲートだけで、これは古典計算機でも効率よくシミュレーションできます。万能な量子計算には T ゲートが必要ですが、表面符号では直接できず、魔法状態蒸留という高価な手順で作ります。ここが研究の出発点です。");

  // ---------- 3. problem
  s = pres.addSlide({ masterName: "Content", sectionTitle: "前提と問題" });
  s.addText("新しい道具：D4 符号との code switching", { placeholder: "title" });
  s.addText("Kobayashi–Zhu–Hsin（2025）の提案：T を直接実行できる符号に一時的に乗り換える",
    { x: 0.5, y: 1.0, w: 9.0, h: 0.35, fontSize: 13, color: HEX.accent6, margin: 0, isTextBox: true, objectName: "lead" });
  const steps = ["表面符号に\n論理状態を準備", "D4 符号へ切り替え\n（d ラウンド測定）", "全量子ビットに\n一斉に T を作用", "表面符号に戻る\n→ T 魔法状態"];
  for (let i = 0; i < 4; i++) {
    const y = 1.5 + i * 0.88;
    s.addShape(pres.shapes.OVAL, { x: 0.5, y, w: 0.5, h: 0.5, fill: { color: i === 2 ? HEX.accent3 : HEX.accent2 }, line: { color: i === 2 ? HEX.accent3 : HEX.accent2 }, objectName: "step num " + (i + 1) });
    s.addText(String(i + 1), { x: 0.5, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "step label " + (i + 1) });
    s.addText(steps[i], { x: 1.15, y: y - 0.08, w: 2.9, h: 0.66, fontSize: 12.5, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true, objectName: "step text " + (i + 1) });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: 0.75, y: y + 0.52, w: 0, h: 0.34, line: { color: HEX.accent6, width: 1.5, endArrowType: "triangle" }, objectName: "step arrow " + (i + 1) });
  }
  card(s, 4.4, 1.5, 5.1, 3.5, HEX.lt2, "difficulty card");
  await circleIcon(s, 4.6, 1.65, 0.55, fa.FaExclamationTriangle, HEX.accent5, "FFFFFF", "difficulty");
  s.addText("なぜ評価が難しいか", { x: 5.3, y: 1.65, w: 4.0, h: 0.55, fontSize: 15, bold: true, color: HEX.dk2, valign: "middle", margin: 0, isTextBox: true, objectName: "difficulty head" });
  s.addText([
    { text: "検査演算子そのものが非 Clifford（CZ 付き）で、測定回路に CCZ が入る → 高速な安定化子シミュレータがそのままでは使えない", options: { bullet: true, breakLine: true } },
    { text: "誤りがあると検査どうしが非可換になり、測定結果が確率的になる → 「誤り→シンドローム」の古典的なモデルでは近似できない", options: { bullet: true, breakLine: true } },
    { text: "汎用シミュレータは非 Clifford ゲート数に指数的なコスト", options: { bullet: true } },
  ], { x: 4.65, y: 2.35, w: 4.65, h: 2.6, fontSize: 13, color: HEX.dk1, valign: "top", margin: 0, paraSpaceAfter: 8, isTextBox: true, objectName: "difficulty list" });
  s.addNotes("新しい方法では、表面符号から D4 符号という特殊な符号に一時的に乗り換えます。D4 符号では T ゲートを全量子ビットに一斉にかけるだけで実行でき、終わったら表面符号に戻ります。問題は評価の難しさで、D4 符号の検査自体が非 Clifford で、誤りがあると検査どうしが打ち消し合う（非可換）ため、通常の高速シミュレータも古典的な近似も使えません。");

  // ---------- 4. contribution II
  pres.addSection({ title: "成果" });
  s = pres.addSlide({ masterName: "Content", sectionTitle: "成果" });
  s.addText("成果 II：目的に応じて厳密かつ効率的な表現を選ぶ", { placeholder: "title" });
  s.addText("共通原理（Takada–Bartlett–Williamson 2026）：誤りを Clifford 部分に通すと Pauli 型の項に化ける → 各測定は「確定」か「50%」の二択 → 多項式時間で厳密に標本化できる",
    { x: 0.5, y: 0.98, w: 9.0, h: 0.55, fontSize: 12, color: HEX.dk1, margin: 0, isTextBox: true, objectName: "principle" });
  const meth = [
    { ic: fa.FaCube, head: "Twisted frame", tag: "本研究で新規", use: "D4 符号の記憶実験", how: "状態を GF(2) 上のアフィン空間＋二次形式で保持", cost: "L=9（729 量子ビット）\n6.3 ms / ショット" },
    { ic: fa.FaExchangeAlt, head: "演算子レベル Pauli proxy", tag: "厳密性の条件を定式化", use: "理想的な T を含む切り替え", how: "十分条件 C1–C3 を立て、全サイズで数値検査", cost: "d=7\n約 21 ms / ショット" },
    { ic: fa.FaMicrochip, head: "回路レベル Pauli proxy", tag: "最大 1,007 量子ビットに適用", use: "ゲート単位の雑音での資源見積もり", how: "非 Clifford ゲートを誤りに応じた Clifford 補正に置き換え", cost: "d=9（全ゲートに雑音）\n約 0.1 s / ショット" },
  ];
  for (let i = 0; i < 3; i++) {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.65, 2.85, 2.75, HEX.lt2, "method card " + (i + 1));
    await circleIcon(s, x + 0.18, 1.8, 0.55, meth[i].ic, i === 0 ? HEX.accent3 : HEX.accent2, "FFFFFF", meth[i].head);
    s.addText([{ text: meth[i].head, options: { bold: true, fontSize: 12.5, color: HEX.dk2, breakLine: true } }, { text: meth[i].tag, options: { fontSize: 10, color: i === 0 ? "B27610" : "16796F" } }],
      { x: x + 0.82, y: 1.78, w: 1.95, h: 0.62, valign: "middle", margin: 0, isTextBox: true, objectName: "method head " + (i + 1) });
    s.addText([{ text: "用途：", options: { bold: true } }, { text: meth[i].use, options: { breakLine: true } }, { text: meth[i].how }],
      { x: x + 0.18, y: 2.5, w: 2.5, h: 1.1, fontSize: 11, color: HEX.dk1, valign: "top", margin: 0, paraSpaceAfter: 4, isTextBox: true, objectName: "method body " + (i + 1) });
    s.addText(meth[i].cost, { x: x + 0.18, y: 3.62, w: 2.5, h: 0.65, fontSize: 11, bold: true, color: HEX.dk2, valign: "top", margin: 0, isTextBox: true, objectName: "method cost " + (i + 1) });
  }
  card(s, 0.5, 4.55, 9.0, 0.55, HEX.dk2, "validation box");
  await circleIcon(s, 0.62, 4.6, 0.45, fa.FaCheckCircle, HEX.accent2, "FFFFFF", "validated");
  s.addText("相互検証：密な状態ベクトル・総当たり・独立なエンジン・真の非 Clifford 回路と照合し、数百万の出力で不一致 0",
    { x: 1.2, y: 4.55, w: 8.2, h: 0.55, fontSize: 12, color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true, objectName: "validation text" });
  s.addNotes("鍵になったのは、誤りを Clifford の部分に通すと扱いやすい Pauli 型の項に化けるという性質です。これで各測定は確定か五分五分かの二択になり、厳密に、しかも多項式時間で標本化できます。同じ原理でも、問いに合わせて状態の持ち方を選ぶと桁違いに速くなります。記憶実験用に新しく作った twisted frame は、同じ問題で Pauli proxy より数倍から数十倍速く、逆に切り替え全体やゲート単位の雑音は Pauli proxy でしか扱えません。三つの実装は互いに、また独立な参照と照合して不一致ゼロでした。");

  // ---------- 5. results I-1,2
  s = pres.addSlide({ masterName: "Content", sectionTitle: "成果" });
  s.addText("成果 I-①②：D4 符号も切り替え全体も閾値は約 2%", { placeholder: "title" });
  const ps = ["0.80", "1.04", "1.35", "1.75", "2.28", "2.96", "3.85", "5.00"];
  const series = [
    { name: "d=3", labels: ps, values: [.02125, .03695, .06555, .11270, .18850, .28220, .41840, .53540] },
    { name: "d=5", labels: ps, values: [.00775, .01775, .04135, .09565, .19140, .36260, .53790, .66195] },
    { name: "d=7", labels: ps, values: [.00505, .00950, .03250, .08745, .22220, .44270, .61985, .71680] },
  ];
  s.addChart(pres.charts.LINE, series, {
    x: 0.4, y: 1.05, w: 5.4, h: 4.0, objectName: "switching chart",
    showTitle: true, title: "code switching 全体の論理誤り率（現象論的雑音）", titleFontSize: 12, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    chartColors: [HEX.accent4, HEX.accent2, HEX.accent3], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 6,
    valAxisLogScaleBase: 10, valAxisMinVal: 0.001, valAxisMaxVal: 1, valAxisLabelFormatCode: "0.000",
    showValAxisTitle: true, valAxisTitle: "論理誤り率", valAxisTitleFontSize: 10, valAxisTitleColor: HEX.accent6,
    showCatAxisTitle: true, catAxisTitle: "物理誤り率 p（%）", catAxisTitleFontSize: 10, catAxisTitleColor: HEX.accent6,
    catAxisLabelColor: HEX.accent6, valAxisLabelColor: HEX.accent6, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "DADDE8", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: HEX.dk1, legendFontFace: "+mn-lt",
  });
  const stats = [
    { big: "2.0–2.25%", small: "D4 符号の記憶実験の閾値の目安\n（L=3–9 の曲線の交点）" },
    { big: "1.9–2.2%", small: "切り替え全体の交点（d=3–7）\n交点より左では d を大きくすると改善" },
    { big: "10 倍超", small: "T の直前に残った誤りによる増幅\n（p=0.8%, d=7、理想化した場合との比）" },
  ];
  for (let i = 0; i < 3; i++) {
    const y = 1.1 + i * 1.32;
    s.addText(stats[i].big, { x: 6.1, y, w: 3.4, h: 0.6, fontSize: 28, bold: true, color: i === 2 ? HEX.accent5 : HEX.accent2, margin: 0, valign: "bottom", isTextBox: true, objectName: "stat big " + (i + 1) });
    s.addText(stats[i].small, { x: 6.1, y: y + 0.62, w: 3.4, h: 0.6, fontSize: 11, color: HEX.dk1, margin: 0, valign: "top", isTextBox: true, objectName: "stat small " + (i + 1) });
  }
  s.addNotes("左の図は切り替え全体の論理誤り率です。曲線の交点より左、つまり物理誤り率が約 2% より小さいと、符号を大きくするほど誤りが減ります。これが閾値の目安です。D4 符号単体の記憶実験でも約 2% でした。一方、T を作用させる直前に残った誤りが増幅されることも分かり、その寄与は理想化した場合の 10 倍を超えます。なお交点はサイズとともに少しずつ下がっており、漸近的な閾値ではなく有限サイズの値です。");

  // ---------- 6. results I-3
  s = pres.addSlide({ masterName: "Content", sectionTitle: "成果" });
  s.addText("成果 I-③：今回の回路では魔法状態蒸留に勝てなかった", { placeholder: "title" });
  const bars = [["A, p=3e-4", 10.0], ["A, p=5e-4", 9.63], ["B, p=1e-3", 9.57], ["A, p=2e-4", 8.75], ["A, p=1e-4", 4.23], ["B, p=5e-4", 2.68], ["B, p=1e-4 ※", 2.30], ["A, p=1e-3", 2.29], ["B, p=2e-4", 1.60], ["B, p=3e-4", 1.59]];
  s.addChart(pres.charts.BAR, [{ name: "体積比の下限", labels: bars.map(b => b[0]), values: bars.map(b => b[1]) }], {
    x: 0.4, y: 1.05, w: 5.4, h: 4.05, barDir: "bar", objectName: "cost chart",
    showTitle: true, title: "体積比 Kobayashi 方式 ÷ 蒸留（目標 10⁻⁴）", titleFontSize: 12, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    chartColors: [HEX.accent4], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", dataLabelFontSize: 10, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 12, valAxisMajorUnit: 2, catAxisLabelColor: HEX.accent6, valAxisLabelColor: HEX.accent6,
    catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "DADDE8", size: 0.5 }, catGridLine: { style: "none" }, showLegend: false,
  });
  s.addText("A：アイドル雑音あり、B：なし。値は「データで否定されない最小サイズ」での下限（※はデータで確定した値）。1 を超えると蒸留が有利",
    { x: 0.5, y: 5.05, w: 5.3, h: 0.45, fontSize: 9.5, color: HEX.accent6, margin: 0, isTextBox: true, objectName: "chart note" });
  const st6 = [
    { big: "0 / 40", small: "優位だった条件（シナリオ 2 × p 5 点 × 目標 4 つ）。29 はデータで負けが確定、11 は未決着", col: HEX.accent5 },
    { big: "≥ 1.59 倍", small: "目標 10⁻⁴ の全 10 条件で必要な体積（データで確定した唯一の条件は 2.30 倍）", col: HEX.dk2 },
  ];
  for (let i = 0; i < 2; i++) {
    const y = 1.1 + i * 1.3;
    s.addText(st6[i].big, { x: 6.1, y, w: 3.4, h: 0.55, fontSize: 28, bold: true, color: st6[i].col, margin: 0, valign: "bottom", isTextBox: true, objectName: "cost stat big " + (i + 1) });
    s.addText(st6[i].small, { x: 6.1, y: y + 0.58, w: 3.4, h: 0.65, fontSize: 11, color: HEX.dk1, margin: 0, valign: "top", isTextBox: true, objectName: "cost stat small " + (i + 1) });
  }
  card(s, 6.1, 3.75, 3.4, 1.3, HEX.lt2, "bottleneck card");
  s.addText([{ text: "原因：切り替えの窓", options: { bold: true, color: HEX.dk2, breakLine: true } },
             { text: "T を作用させる前後で入る誤りが、計算したサイズ（d≤9）では d を大きくしても十分に下がらない", options: { color: HEX.dk1 } }],
    { x: 6.25, y: 3.82, w: 3.1, h: 1.16, fontSize: 11, valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true, objectName: "bottleneck text" });
  s.addNotes("ゲート単位の雑音で、T 魔法状態 1 個を作る費用を、量子ビット数×時間の体積で 15-to-1 蒸留と比べました。554 万ショットのデータに対して、停止規則に依存しない統計手法で「データで保証できること」と「モデルの予測」を分けて判定しています。結果、40 条件で優位な条件はなく、目標 10⁻⁴ ではどの条件でも 1.59 倍以上の体積が必要でした。原因は T の前後の切り替えの窓で入る誤りで、サイズを大きくしても十分に減りません。ただしこれは今回組んだ回路と復号器での結論で、方式一般の優劣ではありません。");

  // ---------- 7. significance
  pres.addSection({ title: "まとめ" });
  s = pres.addSlide({ masterName: "Dark", sectionTitle: "まとめ" });
  s.addText("意義と今後", { x: 0.6, y: 0.35, w: 8.8, h: 0.7, fontSize: 30, bold: true, color: "FFFFFF", margin: 0, isTextBox: true, objectName: "closing title" });
  const sig = [
    { ic: fa.FaSearch, head: "意義", items: ["非 Clifford な符号の切り替えを、近似なしでゲート単位の雑音まで評価", "負けた原因（切り替えの窓）を特定し、改善の標的を定量化", "目的に応じた厳密シミュレーションの手法は、他の非 Clifford プロトコルにも使える"] },
    { ic: fa.FaRoute, head: "今後", items: ["窓の改善（復号器、flag 付き CCZ）で蒸留との損益分岐点を探る", "複数の対角ゲート（T, CS）を 1 回の切り替えでまとめて実行し、窓のコストを分け合う", "D4 符号の高統計の本番計算、より大きいサイズ（d≥11）"] },
  ];
  for (let i = 0; i < 2; i++) {
    const x = 0.6 + i * 4.5;
    card(s, x, 1.3, 4.2, 3.7, "2A2F55", "closing card " + (i + 1));
    await circleIcon(s, x + 0.25, 1.48, 0.6, sig[i].ic, i === 0 ? HEX.accent2 : HEX.accent3, HEX.dk2, sig[i].head);
    s.addText(sig[i].head, { x: x + 1.0, y: 1.48, w: 3.0, h: 0.6, fontSize: 18, bold: true, color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true, objectName: "closing head " + (i + 1) });
    s.addText(sig[i].items.map((t, k) => ({ text: t, options: { bullet: true, breakLine: k < 2 } })),
      { x: x + 0.25, y: 2.3, w: 3.75, h: 2.55, fontSize: 13, color: "E6E8F2", valign: "top", margin: 0, paraSpaceAfter: 10, isTextBox: true, objectName: "closing list " + (i + 1) });
  }
  s.addNotes("意義は三つです。非 Clifford な符号の切り替えを近似なしで回路レベルまで評価したこと、負けた原因を特定して何をどれだけ改善すればよいかを示したこと、そしてシミュレーション手法そのものが他の非 Clifford プロトコルにも使えることです。今後は窓の改善と、複数の非 Clifford ゲートを 1 回の切り替えでまとめて実行して窓のコストを分け合う方向で、蒸留に勝てる条件を探します。");

  await pres.writeFile({ fileName: "D4_code_switching_summary.pptx" });
  await applyTheme("D4_code_switching_summary.pptx", THEME);
  console.log("written");
})();
