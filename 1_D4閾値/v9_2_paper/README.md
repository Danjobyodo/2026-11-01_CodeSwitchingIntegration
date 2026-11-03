# 原稿 v9.2

v9_1_paperを保持した新規原稿。`main_v9_2.tex` では、垂直ホロノミー0への制限、フラックス除去後のCZ残差、対照実験が非可換性だけを分離しないことを統一した。欠けていた測定回路図を `fig_x_stabilizer.tex` として追加し、外部dsfont依存を太字1の指示関数に置換した。

この環境でpdfLaTeXによる組版を確認した。青字の未完了本番値・挿図placeholderは残しており、投稿完成原稿とは呼ばない。研究1の新規本番とuniform/rgbの密検証の後に置き換える。旧記録の「独立実装との一致」は表現の独立性であり、共有する故障表まで独立に検証した意味ではない。

```bash
cd 1_D4閾値/v9_2_paper
pdflatex -interaction=nonstopmode -halt-on-error main_v9_2.tex
pdflatex -interaction=nonstopmode -halt-on-error main_v9_2.tex
```

証明中の振幅比は台Bと移動後の台の両方に属する点だけで使うと明記し、台が互いに素の場合はcase(ii)の議論を使うようにした。
