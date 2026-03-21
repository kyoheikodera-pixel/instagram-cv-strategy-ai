"""
レポート生成モジュール（Plotlyグラフ + Markdown）
棒グラフ + 折れ線グラフ、遷移率表示対応
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from modules.funnel import FunnelMetrics, FunnelTargets


def create_funnel_chart(
    current: FunnelMetrics,
    target_3m: FunnelTargets = None,
    target_6m: FunnelTargets = None,
    company_name: str = "",
    target_12m: FunnelTargets = None,
) -> go.Figure:
    """棒グラフ + 折れ線グラフ + 遷移率表示"""

    categories = ["リーチ数", "プロフアクセス数", "クリック数", "CV"]

    # --- 棒グラフ用データ ---
    current_values = [current.avg_reach, current.avg_profile_access, current.avg_link_clicks, current.avg_cv]
    current_rates = ["", f"{current.profile_access_rate:.2f}%", f"{current.link_click_rate:.2f}%", f"{current.cv_rate:.2f}%"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 現状（棒）
    fig.add_trace(go.Bar(
        name="現状（3ヶ月平均）",
        x=categories, y=current_values,
        text=[f"{v:,.0f}<br><b>{r}</b>" for v, r in zip(current_values, current_rates)],
        textposition="outside", marker_color="#a8c4e0",
    ), secondary_y=False)

    # 3ヶ月後目標（棒）
    if target_3m:
        vals = [target_3m.target_reach, target_3m.target_profile_access, target_3m.target_link_clicks, target_3m.target_cv]
        rates = ["", f"{target_3m.target_profile_access_rate:.2f}%", f"{target_3m.target_link_click_rate:.2f}%", f"{target_3m.target_cv_rate:.2f}%"]
        fig.add_trace(go.Bar(
            name="目標：3ヶ月後", x=categories, y=vals,
            text=[f"<b>{v:,.0f}</b><br><b>{r}</b>" for v, r in zip(vals, rates)],
            textposition="outside", textfont=dict(color="red"), marker_color="#6ca6d9",
        ), secondary_y=False)

    # 6ヶ月後目標（棒）
    if target_6m:
        vals = [target_6m.target_reach, target_6m.target_profile_access, target_6m.target_link_clicks, target_6m.target_cv]
        rates = ["", f"{target_6m.target_profile_access_rate:.2f}%", f"{target_6m.target_link_click_rate:.2f}%", f"{target_6m.target_cv_rate:.2f}%"]
        fig.add_trace(go.Bar(
            name="目標：6ヶ月後", x=categories, y=vals,
            text=[f"<b>{v:,.0f}</b><br><b>{r}</b>" for v, r in zip(vals, rates)],
            textposition="outside", textfont=dict(color="red"), marker_color="#3b82c4",
        ), secondary_y=False)

    # 12ヶ月後目標（棒）
    if target_12m:
        vals = [target_12m.target_reach, target_12m.target_profile_access, target_12m.target_link_clicks, target_12m.target_cv]
        rates = ["", f"{target_12m.target_profile_access_rate:.2f}%", f"{target_12m.target_link_click_rate:.2f}%", f"{target_12m.target_cv_rate:.2f}%"]
        fig.add_trace(go.Bar(
            name="目標：12ヶ月後", x=categories, y=vals,
            text=[f"<b>{v:,.0f}</b><br><b>{r}</b>" for v, r in zip(vals, rates)],
            textposition="outside", textfont=dict(color="darkred"), marker_color="#1a5276",
        ), secondary_y=False)

    # --- 遷移率の折れ線グラフ（右Y軸） ---
    rate_categories = ["プロフアクセス率", "リンククリック率", "反響率(CV率)"]

    current_rate_vals = [current.profile_access_rate, current.link_click_rate, current.cv_rate]
    fig.add_trace(go.Scatter(
        name="遷移率：現状", x=rate_categories, y=current_rate_vals,
        mode="lines+markers+text", text=[f"{v:.2f}%" for v in current_rate_vals],
        textposition="top center", line=dict(color="#a8c4e0", width=2, dash="dot"),
        marker=dict(size=10),
    ), secondary_y=True)

    if target_3m:
        t_rates = [target_3m.target_profile_access_rate, target_3m.target_link_click_rate, target_3m.target_cv_rate]
        fig.add_trace(go.Scatter(
            name="遷移率：3ヶ月後", x=rate_categories, y=t_rates,
            mode="lines+markers+text", text=[f"{v:.2f}%" for v in t_rates],
            textposition="top center", line=dict(color="#6ca6d9", width=2, dash="dot"),
            marker=dict(size=10),
        ), secondary_y=True)

    if target_6m:
        t_rates = [target_6m.target_profile_access_rate, target_6m.target_link_click_rate, target_6m.target_cv_rate]
        fig.add_trace(go.Scatter(
            name="遷移率：6ヶ月後", x=rate_categories, y=t_rates,
            mode="lines+markers+text", text=[f"{v:.2f}%" for v in t_rates],
            textposition="top center", line=dict(color="#3b82c4", width=2, dash="dot"),
            marker=dict(size=10),
        ), secondary_y=True)

    if target_12m:
        t_rates = [target_12m.target_profile_access_rate, target_12m.target_link_click_rate, target_12m.target_cv_rate]
        fig.add_trace(go.Scatter(
            name="遷移率：12ヶ月後", x=rate_categories, y=t_rates,
            mode="lines+markers+text", text=[f"{v:.2f}%" for v in t_rates],
            textposition="top center", line=dict(color="#1a5276", width=2, dash="dot"),
            marker=dict(size=10),
        ), secondary_y=True)

    fig.update_layout(
        title=f"{company_name} Instagram KPI戦略設計",
        barmode="group", height=550,
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )
    fig.update_yaxes(title_text="実数", secondary_y=False)
    fig.update_yaxes(title_text="遷移率(%)", secondary_y=True)

    return fig


def create_trend_chart(monthly_data: list, company_name: str = "") -> go.Figure:
    """月次トレンド: 棒グラフ + 折れ線グラフ + 遷移率表示
    monthly_dataは古い→新しい順で渡す。数値が全て0の月は除外。
    """
    def _yymm_disp(s):
        s = str(s).strip()
        if len(s) == 4 and s.isdigit():
            return f"{s[:2]}年{s[2:]}月"
        return s

    # 数値が全て0の月を除外
    monthly_data = [d for d in monthly_data if d.reach > 0 or d.profile_access > 0 or d.link_clicks > 0 or d.cv > 0]
    months = [_yymm_disp(d.month) for d in monthly_data]

    many = len(months) > 6

    # テキスト表示制御: 月が多い場合は棒テキストを非表示、折れ線もホバーのみ
    bar_text_mode = "none" if many else "outside"
    line_mode = "lines+markers" if many else "lines+markers+text"
    bar_fontsize = 9
    line_fontsize = 9

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("リーチ数", "プロフアクセス数 & プロフアクセス率", "クリック数 & リンククリック率", "CV数 & 反響率"),
        specs=[[{"secondary_y": True}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": True}]],
        vertical_spacing=0.18, horizontal_spacing=0.12,
    )

    # --- リーチ数 ---
    reach_vals = [d.reach for d in monthly_data]
    fig.add_trace(go.Bar(x=months, y=reach_vals, name="リーチ数",
                         marker_color="#a8c4e0", text=[f"{v:,.0f}" for v in reach_vals],
                         textposition=bar_text_mode, textfont=dict(size=bar_fontsize),
                         hovertemplate="%{x}<br>リーチ: %{y:,}<extra></extra>",
                         showlegend=True),
                  row=1, col=1, secondary_y=False)

    # --- プロフアクセス数 + 率 ---
    pa_vals = [d.profile_access for d in monthly_data]
    pa_rates = [d.profile_access_rate for d in monthly_data]
    fig.add_trace(go.Bar(x=months, y=pa_vals, name="プロフアクセス数",
                         marker_color="#6ca6d9", text=[f"{v:,.0f}" for v in pa_vals],
                         textposition=bar_text_mode, textfont=dict(size=bar_fontsize),
                         hovertemplate="%{x}<br>PA: %{y:,}<extra></extra>",
                         showlegend=True),
                  row=1, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=pa_rates, name="プロフアクセス率",
                             mode=line_mode, text=[f"{v:.1f}%" for v in pa_rates],
                             textposition="top right", textfont=dict(size=line_fontsize, color="#ff6b6b"),
                             line=dict(color="#ff6b6b", width=2),
                             marker=dict(size=6, color="#ff6b6b"),
                             hovertemplate="%{x}<br>PA率: %{text}<extra></extra>",
                             showlegend=True),
                  row=1, col=2, secondary_y=True)

    # --- クリック数 + 率 ---
    click_vals = [d.link_clicks for d in monthly_data]
    click_rates = [d.link_click_rate for d in monthly_data]
    fig.add_trace(go.Bar(x=months, y=click_vals, name="クリック数",
                         marker_color="#3b82c4", text=[f"{v:,.0f}" for v in click_vals],
                         textposition=bar_text_mode, textfont=dict(size=bar_fontsize),
                         hovertemplate="%{x}<br>クリック: %{y:,}<extra></extra>",
                         showlegend=True),
                  row=2, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=click_rates, name="リンククリック率",
                             mode=line_mode, text=[f"{v:.1f}%" for v in click_rates],
                             textposition="top right", textfont=dict(size=line_fontsize, color="#ff6b6b"),
                             line=dict(color="#ff6b6b", width=2),
                             marker=dict(size=6, color="#ff6b6b"),
                             hovertemplate="%{x}<br>CL率: %{text}<extra></extra>",
                             showlegend=True),
                  row=2, col=1, secondary_y=True)

    # --- CV数 + 反響率 ---
    cv_vals = [d.cv for d in monthly_data]
    cv_rates = [d.cv_rate for d in monthly_data]
    fig.add_trace(go.Bar(x=months, y=cv_vals, name="CV数",
                         marker_color="#1a5276", text=[f"{v}" for v in cv_vals],
                         textposition=bar_text_mode, textfont=dict(size=bar_fontsize),
                         hovertemplate="%{x}<br>CV: %{y}<extra></extra>",
                         showlegend=True),
                  row=2, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=cv_rates, name="反響率",
                             mode=line_mode, text=[f"{v:.1f}%" for v in cv_rates],
                             textposition="top right", textfont=dict(size=line_fontsize, color="#ff6b6b"),
                             line=dict(color="#ff6b6b", width=2),
                             marker=dict(size=6, color="#ff6b6b"),
                             hovertemplate="%{x}<br>CV率: %{text}<extra></extra>",
                             showlegend=True),
                  row=2, col=2, secondary_y=True)

    # X軸
    tick_angle = -45 if many else -30
    tick_size = 9 if many else 10
    fig.update_xaxes(type="category", tickfont=dict(size=tick_size), tickangle=tick_angle, row=1, col=1)
    fig.update_xaxes(type="category", tickfont=dict(size=tick_size), tickangle=tick_angle, row=1, col=2)
    fig.update_xaxes(type="category", tickfont=dict(size=tick_size), tickangle=tick_angle, row=2, col=1)
    fig.update_xaxes(type="category", tickfont=dict(size=tick_size), tickangle=tick_angle, row=2, col=2)

    # Y軸
    fig.update_yaxes(title_text="実数", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="実数", row=1, col=2, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=1, col=2, secondary_y=True)
    fig.update_yaxes(title_text="実数", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=2, col=1, secondary_y=True)
    fig.update_yaxes(title_text="実数", row=2, col=2, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=2, col=2, secondary_y=True)

    chart_height = 700 if many else 600
    fig.update_layout(
        title=f"{company_name} 直近{len(monthly_data)}ヶ月 月次トレンド",
        height=chart_height, showlegend=False,
        margin=dict(t=60, b=100 if many else 60, l=50, r=50),
        font=dict(size=11),
    )
    return fig


def generate_markdown_report(
    company_name: str,
    area: str,
    plan_type: str,
    followers: int,
    metrics: FunnelMetrics,
    bottleneck_result,
    targets_3m: FunnelTargets = None,
    targets_6m: FunnelTargets = None,
    targets_12m: FunnelTargets = None,
    gaps: dict = None,
    strategy_text: str = "",
    monthly_data: list = None,
) -> str:
    """Markdownレポートを生成"""
    lines = []
    lines.append(f"# {company_name} Instagram CV戦略設計レポート")
    lines.append(f"\n**エリア**: {area} | **プラン**: {plan_type} | **フォロワー**: {followers:,}")
    lines.append("")

    # 現状サマリー
    lines.append("## 現状ファネル数値（直近3ヶ月平均）")
    lines.append("")
    lines.append("| 指標 | 実数 | 転換率 | トレンド |")
    lines.append("|---|---|---|---|")
    lines.append(f"| リーチ数 | {metrics.avg_reach:,.0f} | - | {metrics.trend_reach} |")
    lines.append(f"| プロフアクセス数 | {metrics.avg_profile_access:,.0f} | {metrics.profile_access_rate:.2f}% | {metrics.trend_profile_access} |")
    lines.append(f"| リンククリック数 | {metrics.avg_link_clicks:,.0f} | {metrics.link_click_rate:.2f}% | {metrics.trend_link_clicks} |")
    lines.append(f"| CV数 | {metrics.avg_cv:.1f} (資料請求:{metrics.avg_cv_inquiry:.1f} / 来場:{metrics.avg_cv_visit:.1f}) | {metrics.cv_rate:.2f}% | {metrics.trend_cv} |")

    if metrics.ad_ratio is not None:
        lines.append(f"\n**広告リーチ比率**: {metrics.ad_ratio:.1f}% (広告: {metrics.avg_reach_ad:,.0f} / オーガニック: {metrics.avg_reach_organic:,.0f})")

    # 月別データ
    if monthly_data:
        lines.append("\n## 月別データ推移")
        lines.append("")
        lines.append("| 月 | リーチ数 | プロフアクセス数 | プロフアクセス率 | クリック数 | クリック率 | CV数 | 反響率 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for d in monthly_data:
            if isinstance(d, dict):
                reach = d.get("reach", 0)
                pa = d.get("profile_access", 0)
                clicks = d.get("link_clicks", 0)
                cv = d.get("cv", 0)
                month = d.get("month", "")
            else:
                reach = d.reach
                pa = d.profile_access
                clicks = d.link_clicks
                cv = d.cv
                month = d.month
            pa_rate = (pa / reach * 100) if reach > 0 else 0
            lc_rate = (clicks / pa * 100) if pa > 0 else 0
            cv_rate = (cv / clicks * 100) if clicks > 0 else 0
            lines.append(f"| {month} | {reach:,} | {pa:,} | {pa_rate:.2f}% | {clicks:,} | {lc_rate:.2f}% | {cv} | {cv_rate:.2f}% |")

    # 目標KPI
    lines.append("\n## 目標KPI")
    lines.append("")

    # ヘッダー構築
    header_cols = ["指標", "現状"]
    if targets_3m:
        header_cols.append("3ヶ月後目標")
    if targets_6m:
        header_cols.append("6ヶ月後目標")
    if targets_12m:
        header_cols.append("12ヶ月後目標")

    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "---|" * len(header_cols))

    def _target_cell(t):
        if t is None:
            return ""
        return (
            f"リーチ: {t.target_reach:,}\n"
            f"プロフアクセス: {t.target_profile_access:,} ({t.target_profile_access_rate:.2f}%)\n"
            f"クリック: {t.target_link_clicks:,} ({t.target_link_click_rate:.2f}%)\n"
            f"CV: {t.target_cv} ({t.target_cv_rate:.2f}%)"
        )

    for label, cur, t3, t6, t12 in [
        ("リーチ数", f"{metrics.avg_reach:,.0f}", targets_3m and f"{targets_3m.target_reach:,}", targets_6m and f"{targets_6m.target_reach:,}", targets_12m and f"{targets_12m.target_reach:,}"),
        ("プロフアクセス数", f"{metrics.avg_profile_access:,.0f}", targets_3m and f"{targets_3m.target_profile_access:,} ({targets_3m.target_profile_access_rate:.2f}%)", targets_6m and f"{targets_6m.target_profile_access:,} ({targets_6m.target_profile_access_rate:.2f}%)", targets_12m and f"{targets_12m.target_profile_access:,} ({targets_12m.target_profile_access_rate:.2f}%)"),
        ("クリック数", f"{metrics.avg_link_clicks:,.0f}", targets_3m and f"{targets_3m.target_link_clicks:,} ({targets_3m.target_link_click_rate:.2f}%)", targets_6m and f"{targets_6m.target_link_clicks:,} ({targets_6m.target_link_click_rate:.2f}%)", targets_12m and f"{targets_12m.target_link_clicks:,} ({targets_12m.target_link_click_rate:.2f}%)"),
        ("CV数", f"{metrics.avg_cv:.1f}", targets_3m and f"{targets_3m.target_cv} ({targets_3m.target_cv_rate:.2f}%)", targets_6m and f"{targets_6m.target_cv} ({targets_6m.target_cv_rate:.2f}%)", targets_12m and f"{targets_12m.target_cv} ({targets_12m.target_cv_rate:.2f}%)"),
    ]:
        row = [label, cur]
        if targets_3m:
            row.append(t3 or "-")
        if targets_6m:
            row.append(t6 or "-")
        if targets_12m:
            row.append(t12 or "-")
        lines.append("| " + " | ".join(row) + " |")

    # ボトルネック分析
    lines.append("\n## ボトルネック分析")
    lines.append(f"\n**最大のボトルネック**: {bottleneck_result.primary_bottleneck}")
    lines.append(f"**達成可能性**: {bottleneck_result.feasibility_score}")
    lines.append("\n### 改善優先順位:")
    for i, item in enumerate(bottleneck_result.bottleneck_ranking, 1):
        lines.append(f"{i}. **{item['metric']}**: {item['current']:.2f}% → {item['target']:.2f}% (改善必要: +{item['gap_pct']:.1f}%) [{item['feasibility']}]")

    # アラート
    if bottleneck_result.lp_quality_alert:
        lines.append(f"\n> ⚠️ **LP/HP品質アラート**\n> {bottleneck_result.lp_alert_message}")
    if bottleneck_result.ad_ratio_alert:
        lines.append(f"\n> ⚠️ **広告リーチ比率アラート**\n> {bottleneck_result.ad_alert_message}")

    # 課題の階層分析
    lines.append("\n## 課題の階層分析")
    for issue in bottleneck_result.issues:
        primary_mark = "★ " if issue.get("is_primary") else ""
        lines.append(f"\n### {primary_mark}{issue['level1']}")
        lines.append(f"{issue['level1_detail']}")
        for l2 in issue["level2"]:
            lines.append(f"- **{l2['cause']}**")
            for sc in l2["sub_causes"]:
                lines.append(f"  - {sc}")

    # AI打ち手提案
    if strategy_text:
        lines.append("\n## AI打ち手提案")
        lines.append(strategy_text)

    return "\n".join(lines)
