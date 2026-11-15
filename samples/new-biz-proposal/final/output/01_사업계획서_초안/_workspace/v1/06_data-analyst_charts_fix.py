"""data-analyst 차트 수정본 (v1d 시장, v1c 포지셔닝). 원본 01_data-analyst_charts.py 복사본. 코호트 차트는 본문에서 제외되어 제거. 실행: uv run --with matplotlib --with pandas python <this file>"""
import sys
sys.path.insert(0, ".claude/skills/data-file-analysis/scripts")
import pandas as pd
import matplotlib.pyplot as plt
from kr_chart_style import apply_style, PALETTE as P, save_fig as _sf
from pathlib import Path
def save_fig(fig, path, **kw):
    if Path(path).exists():
        print("[skip existing]", path); plt.close(fig); return
    _sf(fig, path, **kw)

apply_style()
OUT = "output/01_사업계획서_초안/assets/charts"
N = 1
df = pd.read_csv("context/(4.6)네이버API - brand_analysis_summary.csv")
COH = ["10대 체육 수험생", "20대 체육 전공자", "30대 스포츠 동호인"]

# ---------- (a) 시장 규모: STORM 글로벌 시리즈 (CSV는 PDF 본문과 모순되어 미사용) ----------
yrs = [2023, 2024, 2025, 2026, 2027, 2028]
val = [357.0, 384.0, 404.8, 444.5, 488.1, 535.9]
cagr = (val[-1] / val[0]) ** (1 / 5) - 1          # 2023~2028, 5년
fig, ax = plt.subplots(figsize=(8, 4.5))
cols = [P["PRIMARY"]] + [P["SECONDARY"]] * 5
bars = ax.bar([str(y) for y in yrs], val, color=cols, width=0.62)
for b, i in zip(bars, range(6)):
    if i >= 1:   # 추정·전망은 옅게 + 빗금
        b.set_alpha(0.55); b.set_hatch("//"); b.set_edgecolor("white")
    ax.text(b.get_x() + b.get_width() / 2, val[i] + 8, f"{val[i]:,.0f}", ha="center", fontsize=10.5, color=P["PRIMARY"], fontweight="bold")
ax.set_ylim(0, 680); ax.set_ylabel("글로벌 시장 규모 (십억 달러)")
ax.yaxis.grid(True); ax.set_axisbelow(True)
ax.text(0, 20, "실적", ha="center", color="white", fontsize=9.5, fontweight="bold")
for i in range(1, 6):
    ax.text(i, 20, "추정" if i == 1 else "전망", ha="center", color=P["PRIMARY"], fontsize=9.5)
ax.annotate(f"2023~2028 연평균 약 {cagr*100:.1f}% (파생)\n2030년 전망 662십억 달러(9.4% CAGR, 보고서 수치)",
            xy=(5, 536), xytext=(1.0, 585), fontsize=9.5, color=P["PRIMARY"],
            arrowprops=dict(arrowstyle="-", color=P["NEUTRAL"]))
save_fig(fig, f"{OUT}/chart_market-growth_v{N}d.png",
         title="글로벌 애슬레저 시장, 2028년 5,360억 달러 전망",
         source="출처: 해외 시장조사기관 추정치 2차 인용(Athleisure Industry Statistics and Facts 2025 등), 원출처 확인 필요.\n2023 실적·2024 추정·2025~2028 전망, CAGR은 파생 계산")

# ---------- (b) 포지셔닝 맵 (가중평균, 점 크기=n) ----------
w = df.assign(p=df.avg_price_score * df.total_items, f=df.avg_performance_score * df.total_items)
g = w.groupby("brand").agg(n=("total_items", "sum"), p=("p", "sum"), f=("f", "sum"))
g["p"] /= g.n; g["f"] /= g.n
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.set_xlim(2.74, 3.32); ax.set_ylim(3.0, 3.48)
shade = {"젝시믹스": P["PRIMARY"], "나이키": P["NEUTRAL"], "아디다스": "#A9B1C0", "룰루레몬": "#6B7690", "안다르": "#C3C9D4"}
for b, r in g.iterrows():
    ax.scatter(r.p, r.f, s=r.n / 3.2, color=shade[b], alpha=0.9, edgecolor="white", linewidth=1.5, zorder=3)
off = {"젝시믹스": (0.02, 0.055), "나이키": (-0.07, 0.025), "아디다스": (0.075, -0.01), "룰루레몬": (0.0, 0.05), "안다르": (0.025, -0.012)}
lab = {"나이키": "나이키", "아디다스": "아디다스"}
for b, r in g.iterrows():
    dx, dy = off[b]
    ax.text(r.p + dx, r.f + dy, f"{b}\n(n={int(r.n):,})", ha="center", va="center", fontsize=9.5, color=P["PRIMARY"], fontweight="bold" if b == "젝시믹스" else "normal")
ax.set_xlabel("평균 가격 점수 (척도·방향 미기재, 룰루레몬이 가장 낮음)")
ax.set_ylabel("평균 성능 점수 (척도 미기재)")
ax.grid(True)
save_fig(fig, f"{OUT}/chart_positioning-map_v{N}c.png",
         title="성능 인식 격차 0.1~0.3점, 가격 점수는 한 브랜드만 낮음",
         source="출처: 네이버 쇼핑 수집 점수 요약 CSV(brand_analysis_summary.csv), 코호트 3종 합산 아이템 수 가중평균(파생, 코호트별 타사 평균 대비 격차와 다름).\n점 크기=아이템 수. 젝시믹스 대비 성능 격차: 나이키 0.13, 아디다스 0.15, 룰루레몬 0.27, 안다르 0.30. 점수 척도·산출 방식 미기재")

