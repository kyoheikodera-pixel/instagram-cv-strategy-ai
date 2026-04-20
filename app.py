"""
Instagram CV戦略設計AI - メインアプリケーション
工務店特化 | KPIファネル逆算 | 成功事例ドリブン
"""
import sys
import streamlit as st

sys.path.insert(0, ".")

from modules.funnel import MonthlyData, calculate_funnel_metrics, reverse_calculate_targets, calculate_improvement_needed
from modules.analyzer import analyze_bottleneck
from modules.knowledge_manager import KnowledgeManager
from modules.strategy import generate_strategy, get_benchmark_rates_from_cases
from modules.report import create_funnel_chart, create_trend_chart, generate_markdown_report
from config.benchmarks import FALLBACK_BENCHMARKS, PLAN_TYPES

st.set_page_config(page_title="Instagram CV戦略設計AI", page_icon="📊", layout="wide")

# カスタムCSS（ダーク×ゴールドアクセント 高級テーマ）
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;600;700;800&display=swap');

/* ===== ベース ===== */
.stApp {
    background: #0a0e13;
    color: #e8ecf1;
    font-family: 'Noto Sans JP', sans-serif;
}

.main .block-container {
    background: linear-gradient(180deg, #10161e 0%, #0d1219 100%);
    border: 1px solid rgba(180, 160, 120, 0.08);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-top: 1rem;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
}

/* ===== テキスト階層 ===== */
h1 {
    color: #e8dcc8 !important;
    font-weight: 800 !important;
    letter-spacing: 1px;
    text-shadow: 0 2px 12px rgba(200, 175, 130, 0.15);
}
h2 {
    color: #c8b898 !important;
    font-weight: 700 !important;
    border-bottom: 1px solid rgba(180, 160, 120, 0.15);
    padding-bottom: 10px;
    letter-spacing: 0.5px;
}
h3 {
    color: #a8c4d8 !important;
    font-weight: 600 !important;
}
h4 {
    color: #a8c4d8 !important;
    font-weight: 500 !important;
}
p, li, span, label, .stMarkdown {
    color: #c0c8d4 !important;
}

/* ===== タブ ===== */
.stTabs [data-baseweb="tab-list"] {
    background: #12181f;
    border: 1px solid rgba(180, 160, 120, 0.1);
    border-radius: 12px;
    padding: 5px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: #8898a8 !important;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #c8b898 !important;
    background: rgba(180, 160, 120, 0.06);
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1a3048, #1e3f5a) !important;
    color: #e8dcc8 !important;
    border-radius: 9px;
    border: 1px solid rgba(180, 160, 120, 0.2);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

/* ===== ボタン ===== */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(135deg, #1a3048, #1e4060);
    color: #e8dcc8 !important;
    border: 1px solid rgba(180, 160, 120, 0.2);
    border-radius: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(135deg, #1e3f5a, #245070);
    border-color: rgba(200, 184, 152, 0.35);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
    transform: translateY(-1px);
}

/* ===== メトリクスカード ===== */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #12181f, #161e28);
    border: 1px solid rgba(180, 160, 120, 0.1);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
[data-testid="stMetricLabel"] {
    color: #c8b898 !important;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.3px;
}
[data-testid="stMetricValue"] {
    color: #e8ecf1 !important;
    font-weight: 700;
}
[data-testid="stMetricDelta"] {
    color: #7eb8d8 !important;
}

/* ===== テーブル ===== */
table {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
th {
    background: linear-gradient(135deg, #1a3048, #1e4060) !important;
    color: #e8dcc8 !important;
    font-weight: 600 !important;
    padding: 12px 16px !important;
    letter-spacing: 0.3px;
    border-bottom: 1px solid rgba(180, 160, 120, 0.15) !important;
}
td {
    background: #12181f !important;
    color: #d0d8e0 !important;
    padding: 11px 16px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
}
tr:hover td {
    background: #161e28 !important;
}

/* ===== DataFrame ===== */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(180, 160, 120, 0.08);
}

/* ===== 入力フォーム ===== */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 10px !important;
    border: 1px solid rgba(180, 160, 120, 0.12) !important;
    background: #12181f !important;
    color: #e0e4e8 !important;
    font-size: 0.95rem;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(180, 160, 120, 0.3) !important;
    box-shadow: 0 0 0 2px rgba(180, 160, 120, 0.1) !important;
}

/* ===== セレクトボックス・ラジオ ===== */
.stSelectbox > div > div {
    border-radius: 10px !important;
}
.stRadio > div {
    background: #12181f;
    border: 1px solid rgba(180, 160, 120, 0.08);
    border-radius: 10px;
    padding: 5px;
}

/* ===== Expander ===== */
.streamlit-expanderHeader {
    background: #12181f !important;
    border-radius: 10px !important;
    border: 1px solid rgba(180, 160, 120, 0.1) !important;
    color: #c8b898 !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
}

/* ===== アラート ===== */
.stAlert { border-radius: 10px !important; }

/* ===== Divider ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(180, 160, 120, 0.15), transparent);
    margin: 2rem 0;
}

/* ===== ファイルアップローダー ===== */
[data-testid="stFileUploader"] {
    background: #12181f;
    border: 1px dashed rgba(180, 160, 120, 0.15);
    border-radius: 12px;
    padding: 10px;
}

/* ===== サクセス・Info ===== */
.stSuccess { border-left: 3px solid #5a9e6f !important; }
.stInfo { border-left: 3px solid #4a8ab5 !important; }

/* ===== キャプション ===== */
.stCaption { color: #5a6a7a !important; }

/* ===== スクロールバー ===== */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e13; }
::-webkit-scrollbar-thumb { background: rgba(180, 160, 120, 0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(180, 160, 120, 0.25); }
</style>
""", unsafe_allow_html=True)

# ナレッジマネージャー初期化（コード更新時にリロード）
if "km" not in st.session_state or not hasattr(st.session_state.km, "save_past_operation"):
    st.session_state.km = KnowledgeManager()

km = st.session_state.km


def main():
    # ヘッダー
    st.markdown("""
    <div style="text-align:center;padding:28px 0 16px;">
        <div style="display:inline-block;border-bottom:1px solid rgba(180,160,120,0.2);padding-bottom:16px;">
            <h1 style="font-size:2.4rem;margin-bottom:6px;color:#e8dcc8 !important;font-weight:800;letter-spacing:2px;">
                Instagram CV戦略設計AI
            </h1>
            <p style="color:rgba(200,184,152,0.6);font-size:0.85rem;letter-spacing:4px;margin:0;font-weight:300;">
                KPI設計 ｜ ナレッジ活用 ｜ 成果事例活用 ｜ 戦略設計
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 戦略設計", "📂 戦略設計室", "📚 ナレッジ管理", "📋 成果事例一覧", "📒 過去運用事例"])

    with tab1:
        render_strategy_tab()
    with tab2:
        render_archive_tab()
    with tab3:
        render_knowledge_tab()
    with tab4:
        render_cases_tab()
    with tab5:
        render_past_operations_tab()


def render_strategy_tab():
    """戦略設計メインタブ"""
    st.header("Step 1: クライアント情報入力")

    col1, col2, col3 = st.columns(3)
    with col1:
        company_name = st.text_input("会社名", value="", placeholder="例: ゼロホーム様")
    with col2:
        area = st.text_input("エリア", value="", placeholder="例: 東京都")
    with col3:
        plan_type = st.selectbox("運用プラン", list(PLAN_TYPES.keys()))

    col4, col5, col6 = st.columns(3)
    with col4:
        followers = st.number_input("現在のフォロワー数", min_value=0, value=1000, step=100)
    with col5:
        target_cv = st.number_input("目標CV数（期間最終月の月間目標）", min_value=1, value=5, step=1)
    with col6:
        target_period = st.selectbox("目標達成期間", [
            "3ヶ月",
            "6ヶ月",
            "12ヶ月",
            "3ヶ月 + 6ヶ月",
            "3ヶ月 + 6ヶ月 + 12ヶ月（全期間）",
        ])

    # --- 月別データ入力 ---
    st.header("Step 2: 月別データ入力（1ヶ月から入力可能、3ヶ月以上推奨）")
    st.info("1ヶ月分のデータから分析可能です。アルゴリズム変動の影響を平滑化するため、3ヶ月以上のデータを推奨します。＋ボタンで追加入力も可能です。")

    input_mode = st.radio("入力方法", ["手動入力", "ファイル読み込み（CSV/Excel）⭐おすすめ"], horizontal=True, key="input_mode")

    monthly_data_list = []

    if input_mode == "ファイル読み込み（CSV/Excel）⭐おすすめ":
        monthly_data_list = _render_csv_input()
    else:
        monthly_data_list = _render_manual_input()

    # --- データが揃ったら自動で遷移率サマリーを表示 ---
    has_data = monthly_data_list and any(d.reach > 0 for d in monthly_data_list)
    if has_data:
        _render_data_summary(monthly_data_list)

    st.divider()

    # ファイル読み込みで有効データがあれば自動実行、手動入力はボタン
    auto_run = (input_mode == "ファイル読み込み（CSV/Excel）⭐おすすめ") and has_data
    manual_run = st.button("🚀 戦略設計を実行", type="primary", use_container_width=True)

    if auto_run or manual_run:
        # バリデーション
        if not company_name:
            st.error("会社名を入力してください。")
            return
        if not has_data:
            st.error("少なくとも1ヶ月分のリーチデータを入力してください。")
            return

        with st.spinner("ファネル分析中..."):
            # ファネル集計（直近1-3ヶ月のみを現状値として使用）
            # baseline_months = min(入力月数, 3)
            baseline = min(len(monthly_data_list), 3)
            metrics = calculate_funnel_metrics(monthly_data_list, baseline_months=baseline)

            # アカウント固有の成長率がある場合は表示
            if metrics.account_growth_months >= 4:
                st.info(f"📈 {metrics.account_growth_months}ヶ月分のデータからアカウント固有の成長率を算出しました（直近{baseline}ヶ月を現状値として使用）")

            # 事例ベースのベンチマーク算出
            benchmark_rates = get_benchmark_rates_from_cases(km, plan_type)
            if not benchmark_rates:
                benchmark_rates = {k: v["mid"] for k, v in FALLBACK_BENCHMARKS.items()}

            # 成長率の統合: アカウント固有 > 過去運用事例（業界平均）
            past_growth = km.get_growth_rates_from_past_ops()
            if past_growth:
                # アカウント固有の成長率があれば優先的に使用
                if metrics.account_growth_months >= 4:
                    account_g = {}
                    if metrics.account_growth_reach is not None:
                        account_g["reach"] = metrics.account_growth_reach
                    if metrics.account_growth_pa is not None:
                        account_g["profile_access"] = metrics.account_growth_pa
                    if metrics.account_growth_clicks is not None:
                        account_g["link_clicks"] = metrics.account_growth_clicks
                    if metrics.account_growth_cv is not None:
                        account_g["cv"] = metrics.account_growth_cv
                    if metrics.account_growth_pa_rate is not None:
                        account_g["profile_access_rate"] = metrics.account_growth_pa_rate
                    if metrics.account_growth_lc_rate is not None:
                        account_g["link_click_rate"] = metrics.account_growth_lc_rate
                    if metrics.account_growth_cv_rate is not None:
                        account_g["cv_rate"] = metrics.account_growth_cv_rate
                    # アカウント固有で上書き（業界平均をベースに）
                    merged = {**past_growth, **account_g}
                    benchmark_rates["_past_growth"] = merged
                else:
                    benchmark_rates["_past_growth"] = past_growth

            # 目標逆算（期間に応じたCV目標を段階設定）
            # 最終目標CVを基準に、期間に応じた中間目標を設定
            targets_3m = None
            targets_6m = None
            targets_12m = None

            # 現状CVからの段階的目標
            current_cv = metrics.avg_cv
            selected_periods = []
            if "3ヶ月" in target_period:
                selected_periods.append("3ヶ月後")
            if "6ヶ月" in target_period:
                selected_periods.append("6ヶ月後")
            if "12ヶ月" in target_period:
                selected_periods.append("12ヶ月後")

            # 最長期間で最終目標CV、短い期間は段階的に
            period_cv = _calc_staged_cv_targets(current_cv, target_cv, selected_periods)

            if "3ヶ月後" in period_cv:
                targets_3m = reverse_calculate_targets(metrics, period_cv["3ヶ月後"], "3ヶ月後", benchmark_rates)
            if "6ヶ月後" in period_cv:
                targets_6m = reverse_calculate_targets(metrics, period_cv["6ヶ月後"], "6ヶ月後", benchmark_rates)
            if "12ヶ月後" in period_cv:
                targets_12m = reverse_calculate_targets(metrics, period_cv["12ヶ月後"], "12ヶ月後", benchmark_rates)

            # 時系列整合性: 後の期間の値が前の期間より下がらないよう補正
            _ensure_monotonic_targets(targets_3m, targets_6m, targets_12m)

            # メインの目標（ギャップ分析用）
            main_targets = targets_12m or targets_6m or targets_3m
            gaps = calculate_improvement_needed(metrics, main_targets)

            # ボトルネック分析
            bottleneck = analyze_bottleneck(metrics, gaps, FALLBACK_BENCHMARKS)

        # --- 結果表示 ---
        st.header("📊 分析結果")

        # トレンドグラフ（左から3ヶ月前→2ヶ月前→1ヶ月前）
        st.subheader("月次トレンド")
        sorted_data = _sort_monthly_data(monthly_data_list)  # 時系列順
        trend_fig = create_trend_chart(sorted_data, company_name)
        st.plotly_chart(trend_fig, use_container_width=True)

        # ファネルグラフ
        st.subheader("KPI目標グラフ")
        funnel_fig = create_funnel_chart(metrics, targets_3m, targets_6m, company_name, targets_12m)
        st.plotly_chart(funnel_fig, use_container_width=True)

        # KPI目標テーブル
        st.subheader("📋 KPI目標数値テーブル")
        _render_kpi_table(metrics, targets_3m, targets_6m, targets_12m)

        # ボトルネック表示
        st.subheader("🔍 ボトルネック分析")
        col_bn1, col_bn2 = st.columns(2)
        with col_bn1:
            st.metric("最大のボトルネック", bottleneck.primary_bottleneck)
        with col_bn2:
            feasibility_colors = {"達成可能": "🟢", "努力目標": "🟡", "要検討": "🔴"}
            st.metric("達成可能性", f"{feasibility_colors.get(bottleneck.feasibility_score, '')} {bottleneck.feasibility_score}")

        # アラート
        if bottleneck.lp_quality_alert:
            st.warning(f"⚠️ **LP/HP品質アラート**\n\n{bottleneck.lp_alert_message}")
        if bottleneck.ad_ratio_alert:
            st.warning(f"⚠️ **広告リーチ比率アラート**\n\n{bottleneck.ad_alert_message}")

        # 改善優先順位
        st.subheader("📈 改善優先順位")
        for i, item in enumerate(bottleneck.bottleneck_ranking, 1):
            col_r1, col_r2, col_r3, col_r4 = st.columns([1, 3, 3, 2])
            with col_r1:
                st.write(f"**{i}.**")
            with col_r2:
                st.write(f"**{item['metric']}**")
            with col_r3:
                st.write(f"{item['current']:.2f}% → {item['target']:.2f}%")
            with col_r4:
                st.write(f"[{item['feasibility']}]")

        # AI打ち手提案
        st.subheader("🤖 AI打ち手提案")
        with st.spinner("Gemini AIが打ち手を分析中...（30秒程度）"):
            try:
                strategy_text = generate_strategy(
                    company_name=company_name,
                    area=area,
                    plan_type=plan_type,
                    followers=followers,
                    metrics=metrics,
                    bottleneck_result=bottleneck,
                    targets=main_targets,
                    gaps=gaps,
                    knowledge_mgr=km,
                )
                st.markdown(strategy_text)
            except Exception as e:
                strategy_text = ""
                st.error(f"AI生成エラー: {e}\n\n.envにGEMINI_API_KEYが設定されているか確認してください。")

        # Markdownレポート
        st.divider()
        st.subheader("📄 レポートダウンロード")
        report_md = generate_markdown_report(
            company_name=company_name,
            area=area,
            plan_type=plan_type,
            followers=followers,
            metrics=metrics,
            bottleneck_result=bottleneck,
            targets_3m=targets_3m,
            targets_6m=targets_6m,
            targets_12m=targets_12m,
            gaps=gaps,
            strategy_text=strategy_text,
            monthly_data=monthly_data_list,
        )
        dl_col, save_col = st.columns(2)
        with dl_col:
            st.download_button(
                label="📥 Markdownレポートをダウンロード",
                data=report_md,
                file_name=f"{company_name}_戦略設計レポート.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with save_col:
            if st.button("💾 この戦略設計をアーカイブ保存", use_container_width=True):
                archive = {
                    "company_name": company_name,
                    "area": area,
                    "plan_type": plan_type,
                    "followers": followers,
                    "metrics": {
                        "avg_reach": metrics.avg_reach,
                        "avg_profile_access": metrics.avg_profile_access,
                        "avg_link_clicks": metrics.avg_link_clicks,
                        "avg_cv": metrics.avg_cv,
                        "avg_cv_inquiry": metrics.avg_cv_inquiry,
                        "avg_cv_visit": metrics.avg_cv_visit,
                        "profile_access_rate": metrics.profile_access_rate,
                        "link_click_rate": metrics.link_click_rate,
                        "cv_rate": metrics.cv_rate,
                        "ad_ratio": metrics.ad_ratio,
                        "trend_reach": metrics.trend_reach,
                        "trend_profile_access": metrics.trend_profile_access,
                        "trend_link_clicks": metrics.trend_link_clicks,
                        "trend_cv": metrics.trend_cv,
                    },
                    "monthly_data": [
                        {"month": d.month, "reach": d.reach, "profile_access": d.profile_access,
                         "link_clicks": d.link_clicks, "cv": d.cv, "cv_inquiry": d.cv_inquiry,
                         "cv_visit": d.cv_visit}
                        for d in monthly_data_list
                    ],
                    "targets": {
                        "3ヶ月後": targets_3m and {"reach": targets_3m.target_reach, "profile_access": targets_3m.target_profile_access, "link_clicks": targets_3m.target_link_clicks, "cv": targets_3m.target_cv, "pa_rate": targets_3m.target_profile_access_rate, "lc_rate": targets_3m.target_link_click_rate, "cv_rate": targets_3m.target_cv_rate},
                        "6ヶ月後": targets_6m and {"reach": targets_6m.target_reach, "profile_access": targets_6m.target_profile_access, "link_clicks": targets_6m.target_link_clicks, "cv": targets_6m.target_cv, "pa_rate": targets_6m.target_profile_access_rate, "lc_rate": targets_6m.target_link_click_rate, "cv_rate": targets_6m.target_cv_rate},
                        "12ヶ月後": targets_12m and {"reach": targets_12m.target_reach, "profile_access": targets_12m.target_profile_access, "link_clicks": targets_12m.target_link_clicks, "cv": targets_12m.target_cv, "pa_rate": targets_12m.target_profile_access_rate, "lc_rate": targets_12m.target_link_click_rate, "cv_rate": targets_12m.target_cv_rate},
                    },
                    "bottleneck": bottleneck.primary_bottleneck,
                    "feasibility": bottleneck.feasibility_score,
                    "strategy_text": strategy_text,
                    "report_md": report_md,
                }
                aid = km.save_archive(archive)
                st.success(f"✅ 戦略設計をアーカイブしました (ID: {aid})。「📂 戦略設計室」タブで確認できます。")

        with st.expander("レポートプレビュー"):
            st.markdown(report_md)


def _ensure_monotonic_targets(t3, t6, t12):
    """後の期間の数値が前の期間より下がらないよう補正"""
    ordered = [(t3, "3m"), (t6, "6m"), (t12, "12m")]
    active = [t for t, _ in ordered if t is not None]

    for i in range(1, len(active)):
        prev = active[i - 1]
        curr = active[i]
        # 実数は必ず前期間以上
        curr.target_reach = max(curr.target_reach, prev.target_reach)
        curr.target_profile_access = max(curr.target_profile_access, prev.target_profile_access)
        curr.target_link_clicks = max(curr.target_link_clicks, prev.target_link_clicks)
        curr.target_cv = max(curr.target_cv, prev.target_cv)
        # 転換率も前期間以上
        curr.target_profile_access_rate = max(curr.target_profile_access_rate, prev.target_profile_access_rate)
        curr.target_link_click_rate = max(curr.target_link_click_rate, prev.target_link_click_rate)
        curr.target_cv_rate = max(curr.target_cv_rate, prev.target_cv_rate)


def _calc_staged_cv_targets(current_cv: float, final_target_cv: int, periods: list) -> dict:
    """期間に応じた段階的CV目標を算出

    設計方針:
    - 目標CV数 = 選択した最長期間の最終月に達成する月間CV目標
    - 短い期間は中間マイルストーンとして段階的に設定
    - 事例根拠: 建装様はAd移行後2ヶ月で初CV、6ヶ月で安定CV月1-2件
    - 現状CV=0の場合: 3ヶ月=まず1件を目指す
    """
    result = {}
    if not periods:
        return result

    period_months = {"3ヶ月後": 3, "6ヶ月後": 6, "12ヶ月後": 12}
    sorted_periods = sorted(periods, key=lambda p: period_months.get(p, 0))
    longest = sorted_periods[-1]
    longest_months = period_months[longest]

    # 最長期間 = 最終着地目標
    result[longest] = final_target_cv

    # 中間期間: 最終着地に向けた段階目標
    for p in sorted_periods[:-1]:
        p_months = period_months[p]
        # 現状→最終目標への進捗率（線形ではなく後半加速型）
        # 初期は基盤づくり、後半でCV加速するイメージ
        progress = (p_months / longest_months) ** 0.7  # 0.7乗で前半やや控えめ

        if current_cv < 1:
            staged = max(1, round(final_target_cv * progress))
        else:
            cv_gap = final_target_cv - current_cv
            staged = max(round(current_cv + cv_gap * progress), int(current_cv) + 1)

        result[p] = min(staged, final_target_cv)

    # 単一期間の場合はそのまま最終目標
    if len(sorted_periods) == 1:
        result[sorted_periods[0]] = final_target_cv

    return result


def _render_kpi_table(metrics, targets_3m, targets_6m, targets_12m):
    """KPI目標数値をテーブルで表示"""
    import pandas as pd

    def _fmt(val, is_rate=False):
        if val is None:
            return "-"
        if is_rate:
            return f"{val:.2f}%"
        if isinstance(val, float) and val < 10:
            return f"{val:.1f}"
        return f"{int(val):,}"

    def _delta(current, target, is_cv=False):
        """差分を表示"""
        if target is None or current is None:
            return ""
        diff = target - current
        sign = "+" if diff >= 0 else ""
        # CV数で現状が1未満の場合: 件数差で表示（%は無意味）
        if is_cv or current < 1:
            if isinstance(diff, float):
                return f"({sign}{diff:.1f})"
            return f"({sign}{diff})"
        if current == 0:
            return ""
        pct = diff / current * 100
        return f"({sign}{pct:.0f}%)"

    rows = []
    indicators = [
        ("リーチ数", "avg_reach", None, "target_reach", None, False),
        ("プロフアクセス数", "avg_profile_access", "profile_access_rate", "target_profile_access", "target_profile_access_rate", False),
        ("プロフアクセス率", "profile_access_rate", None, "target_profile_access_rate", None, True),
        ("リンククリック数", "avg_link_clicks", "link_click_rate", "target_link_clicks", "target_link_click_rate", False),
        ("リンククリック率", "link_click_rate", None, "target_link_click_rate", None, True),
        ("CV数", "avg_cv", "cv_rate", "target_cv", "target_cv_rate", False),
        ("反響率(CV率)", "cv_rate", None, "target_cv_rate", None, True),
    ]

    for label, m_key, _, t_key, t_rate_key, is_rate in indicators:
        current_val = getattr(metrics, m_key, 0)
        is_cv = (label == "CV数")
        row = {"指標": label, "現状": _fmt(current_val, is_rate)}

        for period_name, target in [("3ヶ月後", targets_3m), ("6ヶ月後", targets_6m), ("12ヶ月後", targets_12m)]:
            if target is None:
                continue
            if is_rate and t_rate_key:
                t_val = getattr(target, t_rate_key if t_rate_key else t_key, None)
            elif is_rate:
                t_val = getattr(target, t_key, None)
            else:
                t_val = getattr(target, t_key, None)
            delta = _delta(current_val, t_val, is_cv=is_cv)
            row[period_name] = f"{_fmt(t_val, is_rate)} {delta}"

        rows.append(row)

    df = pd.DataFrame(rows)

    # スタイル付きでMarkdownテーブルとして出力
    header = "| " + " | ".join(df.columns) + " |"
    separator = "|" + "---|" * len(df.columns)
    body_lines = []
    for _, row in df.iterrows():
        body_lines.append("| " + " | ".join(str(row[c]) for c in df.columns) + " |")

    table_md = "\n".join([header, separator] + body_lines)
    st.markdown(table_md)


def _yymm_display(yymm: str) -> str:
    """yymm形式を表示用に変換: 2512 → 25年12月"""
    s = str(yymm).strip()
    if len(s) == 4 and s.isdigit():
        return f"{s[:2]}年{s[2:]}月"
    return s


def _yymm_sort_key(yymm: str) -> int:
    """yymm形式をソート用の数値に変換"""
    import re
    s = str(yymm).strip()

    # 4桁数字(yymm): 2512→2512
    if s.isdigit() and len(s) == 4:
        return int(s)

    # 純粋な数字（6桁yyyymm等）
    if s.isdigit():
        return int(s[-4:]) if len(s) >= 4 else int(s)

    # 「Nヶ月前」形式
    m = re.match(r"(\d+)\s*[ヶケか]?\s*月前", s)
    if m:
        return 10000 - int(m.group(1))

    # 「運用開始月（23年8月）」のような形式 → 括弧内の年月を抽出
    m = re.search(r"(\d{2})年(\d{1,2})月", s)
    if m:
        yy = int(m.group(1))
        mm = int(m.group(2))
        return yy * 100 + mm

    # 「2025-12」形式
    m = re.search(r"(\d{4})-(\d{1,2})", s)
    if m:
        yy = int(m.group(1)) % 100
        mm = int(m.group(2))
        return yy * 100 + mm

    # 数字を含む場合はその数字を返す
    m = re.search(r"(\d+)", s)
    if m:
        return int(m.group(1))

    return 0


def _sort_monthly_data(data_list: list, remove_empty: bool = True) -> list:
    """月別データを時系列順（古い→新しい）にソート。空データは除外"""
    sorted_list = sorted(data_list, key=lambda d: _yymm_sort_key(d.month))
    if remove_empty:
        sorted_list = [d for d in sorted_list if d.reach > 0 or d.profile_access > 0 or d.link_clicks > 0 or d.cv > 0]
    return sorted_list


def _render_data_summary(monthly_data_list: list):
    """アップロード/入力データの遷移率サマリーを自動表示"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.header("📊 読み込みデータ サマリー")

    sorted_data = _sort_monthly_data(monthly_data_list)  # 時系列順（古い→新しい）
    months_display = [_yymm_display(d.month) for d in sorted_data]

    # --- 月別テーブル ---
    summary_rows = []
    for d in sorted_data:
        summary_rows.append({
            "月": _yymm_display(d.month),
            "リーチ数": f"{d.reach:,}",
            "プロフアクセス数": f"{d.profile_access:,}",
            "プロフアクセス率": f"{d.profile_access_rate:.2f}%",
            "クリック数": f"{d.link_clicks:,}",
            "クリック率": f"{d.link_click_rate:.2f}%",
            "CV数": d.cv,
            "反響率": f"{d.cv_rate:.2f}%",
        })
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    # --- 平均値 ---
    n = len(sorted_data)
    avg_reach = sum(d.reach for d in sorted_data) / n
    avg_pa = sum(d.profile_access for d in sorted_data) / n
    avg_clicks = sum(d.link_clicks for d in sorted_data) / n
    avg_cv = sum(d.cv for d in sorted_data) / n
    avg_pa_rate = (avg_pa / avg_reach * 100) if avg_reach > 0 else 0
    avg_lc_rate = (avg_clicks / avg_pa * 100) if avg_pa > 0 else 0
    avg_cv_rate = (avg_cv / avg_clicks * 100) if avg_clicks > 0 else 0

    st.subheader(f"📈 {n}ヶ月平均")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("平均リーチ", f"{avg_reach:,.0f}")
    with m2:
        st.metric("平均プロフアクセス", f"{avg_pa:,.0f}", f"率: {avg_pa_rate:.2f}%")
    with m3:
        st.metric("平均クリック", f"{avg_clicks:,.0f}", f"率: {avg_lc_rate:.2f}%")
    with m4:
        st.metric("平均CV", f"{avg_cv:.1f}", f"率: {avg_cv_rate:.2f}%")

    # --- ファネル図（ステップ形式で見やすく） ---
    st.subheader("🔽 ファネル（平均値ベース）")

    # 視覚的に見やすいファネル: 実数ではなく段階的な幅（100→75→50→25）で表示
    # 各ステージの実数・遷移率はテキストで表示
    funnel_stages = [
        ("リーチ", avg_reach, "-", 100, "#a8c4e0"),
        ("プロフアクセス", avg_pa, f"{avg_pa_rate:.2f}%", 70, "#6ca6d9"),
        ("クリック", avg_clicks, f"{avg_lc_rate:.2f}%", 45, "#3b82c4"),
        ("CV", avg_cv, f"{avg_cv_rate:.2f}%", 25, "#1a5276"),
    ]

    funnel_fig = go.Figure()
    for label, val, rate_text, visual_width, color in funnel_stages:
        display_text = f"<b>{val:,.0f}</b>" if val >= 1 else f"<b>{val:.1f}</b>"
        if rate_text != "-":
            display_text += f"　（遷移率 {rate_text}）"
        funnel_fig.add_trace(go.Bar(
            y=[label], x=[visual_width], orientation="h",
            marker=dict(color=color, line=dict(color="rgba(0,0,0,0)", width=0)),
            text=display_text,
            textposition="inside", textfont=dict(color="white", size=14),
            showlegend=False,
            hovertemplate=f"{label}: {val:,.1f}　{rate_text}<extra></extra>",
        ))
    funnel_fig.update_layout(
        height=300, barmode="overlay",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, 110]),
        yaxis=dict(autorange="reversed", tickfont=dict(size=14)),
        margin=dict(l=130, r=30, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(funnel_fig, use_container_width=True)

    # 遷移率フローカード
    st.markdown(
        f"""<div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;">
        <div style="text-align:center;background:#a8c4e0;border-radius:10px;padding:14px 20px;min-width:140px;">
            <div style="font-size:12px;color:#1a1a2e;">リーチ</div>
            <div style="font-size:20px;font-weight:bold;color:#1a1a2e;">{avg_reach:,.0f}</div>
        </div>
        <div style="font-size:28px;color:#888;">→</div>
        <div style="text-align:center;background:#6ca6d9;border-radius:10px;padding:14px 20px;min-width:140px;">
            <div style="font-size:12px;color:#fff;">プロフアクセス</div>
            <div style="font-size:20px;font-weight:bold;color:#fff;">{avg_pa:,.0f}</div>
            <div style="font-size:11px;color:#ffe0e0;">遷移率 {avg_pa_rate:.2f}%</div>
        </div>
        <div style="font-size:28px;color:#888;">→</div>
        <div style="text-align:center;background:#3b82c4;border-radius:10px;padding:14px 20px;min-width:140px;">
            <div style="font-size:12px;color:#fff;">クリック</div>
            <div style="font-size:20px;font-weight:bold;color:#fff;">{avg_clicks:,.0f}</div>
            <div style="font-size:11px;color:#ffe0e0;">遷移率 {avg_lc_rate:.2f}%</div>
        </div>
        <div style="font-size:28px;color:#888;">→</div>
        <div style="text-align:center;background:#1a5276;border-radius:10px;padding:14px 20px;min-width:140px;">
            <div style="font-size:12px;color:#fff;">CV</div>
            <div style="font-size:20px;font-weight:bold;color:#fff;">{avg_cv:.1f}</div>
            <div style="font-size:11px;color:#ffe0e0;">遷移率 {avg_cv_rate:.2f}%</div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # --- 月次トレンド（2行2列、見やすいレイアウト） ---
    st.subheader("📈 月次推移")

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("リーチ数", "プロフアクセス数 ＆ プロフアクセス率",
                        "クリック数 ＆ リンククリック率", "CV数 ＆ 反響率"),
        specs=[[{"secondary_y": False}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": True}]],
        vertical_spacing=0.18, horizontal_spacing=0.12,
    )

    x_labels = months_display
    many_months = len(x_labels) > 6  # 月が多い場合はテキスト省略

    # 棒グラフ: 月が多い場合はテキストを内部に、少ない場合は外部に
    bar_textpos = "inside" if many_months else "outside"
    bar_fontsize = 9 if many_months else 11
    # 折れ線: 月が多い場合はテキスト非表示（ホバーのみ）
    line_mode = "lines+markers" if many_months else "lines+markers+text"

    # リーチ（棒のみ）
    fig.add_trace(go.Bar(
        x=x_labels, y=[d.reach for d in sorted_data], name="リーチ",
        marker_color="#a8c4e0", text=[f"{d.reach:,}" for d in sorted_data],
        textposition=bar_textpos, textfont=dict(size=bar_fontsize), showlegend=False,
        hovertemplate="%{x}<br>リーチ: %{y:,}<extra></extra>",
    ), row=1, col=1)

    # プロフアクセス（棒 + 折れ線）
    fig.add_trace(go.Bar(
        x=x_labels, y=[d.profile_access for d in sorted_data], name="プロフアクセス",
        marker_color="#6ca6d9", text=[f"{d.profile_access:,}" for d in sorted_data],
        textposition=bar_textpos, textfont=dict(size=bar_fontsize), showlegend=False,
        hovertemplate="%{x}<br>プロフアクセス: %{y:,}<extra></extra>",
    ), row=1, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x_labels, y=[d.profile_access_rate for d in sorted_data], name="プロフアクセス率",
        mode=line_mode, text=[f"{d.profile_access_rate:.1f}%" for d in sorted_data],
        textposition="top right", textfont=dict(size=10, color="#ff6b6b"),
        line=dict(color="#ff6b6b", width=2.5), marker=dict(size=7, color="#ff6b6b"), showlegend=False,
        hovertemplate="%{x}<br>プロフアクセス率: %{text}<extra></extra>",
    ), row=1, col=2, secondary_y=True)

    # クリック（棒 + 折れ線）
    fig.add_trace(go.Bar(
        x=x_labels, y=[d.link_clicks for d in sorted_data], name="クリック",
        marker_color="#3b82c4", text=[f"{d.link_clicks:,}" for d in sorted_data],
        textposition=bar_textpos, textfont=dict(size=bar_fontsize), showlegend=False,
        hovertemplate="%{x}<br>クリック: %{y:,}<extra></extra>",
    ), row=2, col=1, secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x_labels, y=[d.link_click_rate for d in sorted_data], name="クリック率",
        mode=line_mode, text=[f"{d.link_click_rate:.1f}%" for d in sorted_data],
        textposition="top right", textfont=dict(size=10, color="#ff6b6b"),
        line=dict(color="#ff6b6b", width=2.5), marker=dict(size=7, color="#ff6b6b"), showlegend=False,
        hovertemplate="%{x}<br>クリック率: %{text}<extra></extra>",
    ), row=2, col=1, secondary_y=True)

    # CV（棒 + 折れ線）
    fig.add_trace(go.Bar(
        x=x_labels, y=[d.cv for d in sorted_data], name="CV",
        marker_color="#1a5276", text=[f"{d.cv}" for d in sorted_data],
        textposition=bar_textpos, textfont=dict(size=bar_fontsize), showlegend=False,
        hovertemplate="%{x}<br>CV: %{y}<extra></extra>",
    ), row=2, col=2, secondary_y=False)
    fig.add_trace(go.Scatter(
        x=x_labels, y=[d.cv_rate for d in sorted_data], name="反響率",
        mode=line_mode, text=[f"{d.cv_rate:.1f}%" for d in sorted_data],
        textposition="top right", textfont=dict(size=10, color="#ff6b6b"),
        line=dict(color="#ff6b6b", width=2.5), marker=dict(size=7, color="#ff6b6b"), showlegend=False,
        hovertemplate="%{x}<br>反響率: %{text}<extra></extra>",
    ), row=2, col=2, secondary_y=True)

    # X軸: カテゴリ型、月が多い場合はラベルを斜めに
    tick_angle = -45 if many_months else 0
    fig.update_xaxes(type="category", tickfont=dict(size=10), tickangle=tick_angle, row=1, col=1)
    fig.update_xaxes(type="category", tickfont=dict(size=10), tickangle=tick_angle, row=1, col=2)
    fig.update_xaxes(type="category", tickfont=dict(size=10), tickangle=tick_angle, row=2, col=1)
    fig.update_xaxes(type="category", tickfont=dict(size=10), tickangle=tick_angle, row=2, col=2)

    # Y軸
    fig.update_yaxes(title_text="実数", row=1, col=1)
    fig.update_yaxes(title_text="実数", row=1, col=2, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=1, col=2, secondary_y=True)
    fig.update_yaxes(title_text="実数", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=2, col=1, secondary_y=True)
    fig.update_yaxes(title_text="実数", row=2, col=2, secondary_y=False)
    fig.update_yaxes(title_text="率(%)", row=2, col=2, secondary_y=True)

    chart_height = 650 if not many_months else 750
    fig.update_layout(
        height=chart_height, showlegend=False,
        margin=dict(t=60, b=80 if many_months else 20),
        font=dict(size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ データ読み込み完了。下の分析が自動実行されます。")


def _render_manual_input() -> list:
    """手動入力フォーム（3ヶ月固定 + 追加可能）"""
    # 追加月数をセッションステートで管理
    if "extra_months" not in st.session_state:
        st.session_state.extra_months = 0

    base_count = 3
    total_months = base_count + st.session_state.extra_months
    monthly_data_list = []

    for i in range(total_months):
        # ラベル: 1ヶ月前, 2ヶ月前, ... N ヶ月前
        month_num = i + 1
        label = f"{month_num}ヶ月前"

        st.subheader(f"📅 {label}")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            reach = st.number_input(f"リーチ数 ({label})", min_value=0, value=0, step=1000, key=f"reach_{i}")
        with c2:
            pa = st.number_input(f"プロフアクセス数 ({label})", min_value=0, value=0, step=100, key=f"pa_{i}")
        with c3:
            clicks = st.number_input(f"リンククリック数 ({label})", min_value=0, value=0, step=10, key=f"clicks_{i}")
        with c4:
            cv_total = st.number_input(f"CV数 ({label})", min_value=0, value=0, step=1, key=f"cv_{i}")

        cv_col1, cv_col2 = st.columns(2)
        with cv_col1:
            cv_inq = st.number_input(f"  うち資料請求 ({label})", min_value=0, value=0, step=1, key=f"cv_inq_{i}")
        with cv_col2:
            cv_vis = st.number_input(f"  うち来場予約 ({label})", min_value=0, value=0, step=1, key=f"cv_vis_{i}")

        with st.expander(f"クリック内訳・広告リーチ（任意）- {label}"):
            cc1, cc2 = st.columns(2)
            with cc1:
                clicks_prof = st.number_input(f"プロフ経由クリック ({label})", min_value=0, value=0, step=1, key=f"clicks_prof_{i}")
            with cc2:
                clicks_story = st.number_input(f"ストーリー経由クリック ({label})", min_value=0, value=0, step=1, key=f"clicks_story_{i}")
            ac1, ac2 = st.columns(2)
            with ac1:
                reach_ad = st.number_input(f"広告リーチ数 ({label})", min_value=0, value=0, step=1000, key=f"reach_ad_{i}")
            with ac2:
                reach_org = st.number_input(f"オーガニックリーチ数 ({label})", min_value=0, value=0, step=1000, key=f"reach_org_{i}")

        md = MonthlyData(
            month=label,
            reach=reach,
            profile_access=pa,
            link_clicks=clicks,
            link_clicks_profile=clicks_prof if clicks_prof > 0 else None,
            link_clicks_story=clicks_story if clicks_story > 0 else None,
            cv=cv_total,
            cv_inquiry=cv_inq,
            cv_visit=cv_vis,
            reach_ad=reach_ad if reach_ad > 0 else None,
            reach_organic=reach_org if reach_org > 0 else None,
        )
        monthly_data_list.append(md)

    # ＋ボタンと−ボタン
    btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 6])
    with btn_col1:
        if st.button("➕ 月を追加", use_container_width=True):
            st.session_state.extra_months += 1
            st.rerun()
    with btn_col2:
        if st.session_state.extra_months > 0:
            if st.button("➖ 月を削除", use_container_width=True):
                st.session_state.extra_months -= 1
                st.rerun()

    st.caption(f"現在 {total_months}ヶ月分のデータを入力中")
    return monthly_data_list


def _render_csv_input() -> list:
    """CSVファイルから月別データを読み込む（横型・縦型フォーマット自動検出）"""
    import pandas as pd

    csv_format = st.radio("CSVフォーマット", ["縦型（カテゴリ×指標）", "横型（月×指標）"], horizontal=True, key="csv_fmt")

    if csv_format == "縦型（カテゴリ×指標）":
        st.markdown("""
**縦型フォーマット:** 行=指標、列=月ごとの値。各月のデータを列として追加。

| カテゴリ | 指標 | 2601 | 2602 | 2603 |
|---|---|---|---|---|
| リーチ | 合計 | 1490 | 2000 | 1800 |
| プロフ | プロフアクセス数 | 706 | 800 | 750 |
| リンククリック | リンククリック数 | 30 | 40 | 35 |
| リンククリック | プロフ | 30 | 35 | 30 |
| リンククリック | ストーリーズ/ハイライト | 0 | 5 | 5 |
| CV数 | CV件数 | 1 | 2 | 1 |
| ... | ... | ... | ... | ... |

> **月の表記:** yymm形式（4桁）。例: 2512 = 2025年12月、2603 = 2026年3月。yyyy-mmやyyyy/mm形式も自動変換されます。

> 💡 月の列は**1列以上**必要です。既存のスプレッドシートをそのまま使えます。
        """)

        # 縦型テンプレート
        v_template = "カテゴリ,指標,2601,2602,2603\n本数,フィード投稿数,0,0,0\n本数,リール投稿数,0,0,0\nフォロワー数,合計,0,0,0\nフォロワー数,月次増加数,0,0,0\nビュー,合計,0,0,0\nビュー,フィード計,0,0,0\nビュー,リール計,0,0,0\nビュー,平均,0,0,0\nリーチ,合計,0,0,0\nリーチ,フィード計,0,0,0\nリーチ,リール計,0,0,0\nリーチ,平均,0,0,0\nENG数,合計,0,0,0\nENG数,平均,0,0,0\n保存数,合計,0,0,0\n保存数,平均,0,0,0\nプロフ,プロフアクセス数,0,0,0\nリンククリック,リンククリック数,0,0,0\nリンククリック,プロフ,0,0,0\nリンククリック,ストーリーズ/ハイライト,0,0,0\nCV数,CV件数,0,0,0\nENG率,,0,0,0\n保存率,,0,0,0\n歩留変数,プロフアクセス率,0,0,0\n歩留変数,リンククリック率,0,0,0\n歩留変数,CV率,0,0,0\n"
        st.download_button("📥 縦型テンプレートをダウンロード", v_template, "縦型テンプレート.csv", "text/csv")

    else:
        st.markdown("""
**横型フォーマット:** 行=月、列=指標。

| 月 | リーチ数 | プロフアクセス数 | リンククリック数 | CV数 | ... |
|---|---|---|---|---|---|

> 💡 **最低1行（1ヶ月分）必要**です。
        """)
        h_template = "月,リーチ数,プロフアクセス数,リンククリック数,CV数,資料請求,来場予約,プロフ経由クリック,ストーリー経由クリック,広告リーチ数,オーガニックリーチ数\n2510,0,0,0,0,0,0,0,0,0,0\n2511,0,0,0,0,0,0,0,0,0,0\n2512,0,0,0,0,0,0,0,0,0,0\n2601,0,0,0,0,0,0,0,0,0,0\n2602,0,0,0,0,0,0,0,0,0,0\n2603,0,0,0,0,0,0,0,0,0,0\n"
        st.download_button("📥 横型テンプレートをダウンロード", h_template, "横型テンプレート.csv", "text/csv")

    uploaded_file = st.file_uploader(
        "ファイルをアップロード（CSV / Excel）",
        type=["csv", "xlsx", "xls"],
        key="monthly_file",
    )

    monthly_data_list = []
    if uploaded_file:
        fname = uploaded_file.name.lower()

        # Excel or CSV を自動判定して読み込み
        if fname.endswith((".xlsx", ".xls")):
            try:
                xls = pd.ExcelFile(uploaded_file)
                if len(xls.sheet_names) > 1:
                    sheet = st.selectbox("シートを選択", xls.sheet_names, key="sheet_select")
                else:
                    sheet = xls.sheet_names[0]
                df = pd.read_excel(uploaded_file, sheet_name=sheet)
                st.info(f"📗 Excelファイル読み込み完了（シート: {sheet}）")
            except Exception as e:
                st.error(f"Excel読み込みエラー: {e}")
                return []
        else:
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="shift_jis")

        st.dataframe(df, use_container_width=True)

        # --- フォーマット自動検出 + バリデーション ---
        detected, errors, warnings = _validate_and_detect_format(df, csv_format)

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
            return []

        for w in warnings:
            st.warning(f"⚠️ {w}")

        if detected == "vertical":
            st.info("📋 フォーマット検出: **縦型（カテゴリ×指標）**")
            monthly_data_list = _parse_vertical_csv(df)
        elif detected == "horizontal":
            st.info("📋 フォーマット検出: **横型（月×指標）**")
            monthly_data_list = _parse_horizontal_csv(df)

        # パース後のデータ検証
        if monthly_data_list:
            post_errors = _validate_parsed_data(monthly_data_list)
            for e in post_errors:
                st.warning(f"⚠️ {e}")

    return monthly_data_list


def _validate_and_detect_format(df, user_selected_format: str) -> tuple:
    """ファイルのフォーマットを自動検出し、バリデーションを実行"""
    import pandas as pd

    errors = []
    warnings = []

    if df.empty:
        return None, ["ファイルが空です。データが含まれているか確認してください。"], []

    if len(df.columns) < 2:
        return None, ["列数が足りません（最低2列必要）。正しいフォーマットか確認してください。"], []

    col_names = [str(c).strip() for c in df.columns]

    # --- 縦型の特徴チェック ---
    vertical_keywords_col0 = ["カテゴリ", "指標"]
    vertical_keywords_rows = ["リーチ", "プロフ", "CV", "リンククリック", "ビュー", "ENG", "フォロワー", "保存", "歩留"]
    vertical_keywords_section = ["実数値", "変数", "施策"]

    # 列名にカテゴリ/指標があるか
    is_vertical_header = any(kw in c for c in col_names for kw in vertical_keywords_col0)

    # 全列のデータに縦型キーワードが含まれるかチェック（Unnamed列も含む）
    all_cell_values = []
    for ci in range(min(3, len(df.columns))):  # 最初の3列を検査
        all_cell_values.extend([str(v).strip() for v in df.iloc[:, ci].dropna().tolist()])

    vertical_keyword_hits = sum(1 for v in all_cell_values if any(kw in v for kw in vertical_keywords_rows))
    vertical_section_hits = sum(1 for v in all_cell_values if any(kw in v for kw in vertical_keywords_section))
    is_vertical_content = vertical_keyword_hits >= 3 or (vertical_section_hits >= 2 and vertical_keyword_hits >= 1)

    # yymm形式の月列があるかチェック
    yymm_col_count = 0
    for c in df.columns:
        try:
            v = int(float(c))
            if 2300 <= v <= 2700:
                yymm_col_count += 1
        except (ValueError, TypeError):
            pass
    has_yymm_cols = yymm_col_count >= 1
    if has_yymm_cols and vertical_keyword_hits >= 1:
        is_vertical_content = True

    # --- 横型の特徴チェック ---
    horizontal_keywords = ["月", "リーチ数", "プロフアクセス数", "リンククリック数", "CV数",
                           "month", "reach", "profile_access", "link_clicks", "cv"]
    horizontal_col_hits = sum(1 for c in col_names if any(kw in c.lower() for kw in horizontal_keywords))
    is_horizontal = horizontal_col_hits >= 3

    # --- 判定 ---
    detected = None
    user_wants_vertical = "縦型" in user_selected_format

    if is_vertical_header or is_vertical_content:
        detected = "vertical"
        if not user_wants_vertical:
            warnings.append(
                f"このファイルは**縦型フォーマット**として検出されました（カテゴリ列キーワード{vertical_keyword_hits}件一致）。"
                "フォーマット選択が「横型」ですが、自動で縦型として処理します。"
            )
    elif is_horizontal:
        detected = "horizontal"
        if user_wants_vertical:
            warnings.append(
                "このファイルは**横型フォーマット**として検出されました。"
                "フォーマット選択が「縦型」ですが、自動で横型として処理します。"
            )
    else:
        # どちらにも該当しない
        errors.append(
            "ファイルのフォーマットを判定できませんでした。\n\n"
            "**縦型の場合:** 1列目が「カテゴリ」、2列目が「指標」、3列目以降が月データ。"
            "行に「リーチ」「プロフ」「CV数」等のキーワードが必要です。\n\n"
            "**横型の場合:** 列に「月」「リーチ数」「プロフアクセス数」「リンククリック数」「CV数」が必要です。\n\n"
            "テンプレートをダウンロードして確認してください。"
        )

    # --- 追加バリデーション ---
    if detected == "vertical":
        if yymm_col_count < 1:
            errors.append(f"yymm形式の月データ列が{yymm_col_count}列しかありません。最低1列（1ヶ月分）必要です。")
        elif yymm_col_count < 3:
            warnings.append("3ヶ月未満のデータのため、精度が低い可能性があります。3ヶ月以上のデータを推奨します。")

        # 必須行チェック（全列のデータを検査）
        required_categories = ["リーチ", "プロフ", "CV"]
        found = {kw: False for kw in required_categories}
        for v in all_cell_values:
            for kw in required_categories:
                if kw in v:
                    found[kw] = True
        missing_cats = [kw for kw, ok in found.items() if not ok]
        if missing_cats:
            errors.append(f"必須キーワードが見つかりません: {', '.join(missing_cats)}。カテゴリ列または指標列にこれらのキーワードが含まれているか確認してください。")

    elif detected == "horizontal":
        required = ["月", "リーチ数", "プロフアクセス数", "リンククリック数", "CV数"]
        # 英語名も許容
        alt_map = {"月": "month", "リーチ数": "reach", "プロフアクセス数": "profile_access",
                   "リンククリック数": "link_clicks", "CV数": "cv"}
        missing = []
        for req in required:
            if req not in col_names and alt_map.get(req, "") not in [c.lower() for c in col_names]:
                missing.append(req)
        if missing:
            errors.append(f"必須列が不足しています: {', '.join(missing)}")

        if len(df) < 1:
            errors.append(f"データ行が{len(df)}行しかありません。最低1行（1ヶ月分）必要です。")
        elif len(df) < 3:
            warnings.append("3ヶ月未満のデータのため、精度が低い可能性があります。3ヶ月以上のデータを推奨します。")

    return detected, errors, warnings


def _validate_parsed_data(monthly_data_list: list) -> list:
    """パース後のデータの整合性チェック"""
    warnings = []

    for d in monthly_data_list:
        # リーチが0なのに他の値がある
        if d.reach == 0 and (d.profile_access > 0 or d.link_clicks > 0 or d.cv > 0):
            warnings.append(f"[{d.month}] リーチ数が0ですが、他の指標に値があります。リーチ数が正しく読み込まれているか確認してください。")

        # プロフアクセス > リーチ（異常）
        if d.reach > 0 and d.profile_access > d.reach:
            warnings.append(f"[{d.month}] プロフアクセス数({d.profile_access:,})がリーチ数({d.reach:,})を超えています。数値を確認してください。")

        # クリック > プロフアクセス（異常）
        if d.profile_access > 0 and d.link_clicks > d.profile_access:
            warnings.append(f"[{d.month}] クリック数({d.link_clicks:,})がプロフアクセス数({d.profile_access:,})を超えています。数値を確認してください。")

        # CV > クリック（異常）
        if d.link_clicks > 0 and d.cv > d.link_clicks:
            warnings.append(f"[{d.month}] CV数({d.cv})がクリック数({d.link_clicks:,})を超えています。数値を確認してください。")

        # 遷移率が異常に高い
        if d.profile_access_rate > 50:
            warnings.append(f"[{d.month}] プロフアクセス率が{d.profile_access_rate:.1f}%と非常に高いです。リーチ数がビュー数と混同されていないか確認してください。")

    # 全月CVが0
    if all(d.cv == 0 for d in monthly_data_list):
        warnings.append("全ての月でCV数が0です。CVデータが正しく読み込まれているか確認してください。")

    return warnings


def _format_month_label(raw: str) -> str:
    """月ラベルをyymm形式に統一。例: 2512 = 2025年12月
    入力が既にyymmなら変換不要。2025-12やyyyymmならyymmに変換。
    """
    s = str(raw).strip()

    # 既に4桁数字(yymm) → そのまま
    if len(s) == 4 and s.isdigit():
        return s

    # yyyy-mm → yymm
    if len(s) >= 7 and s[4] == "-":
        try:
            yy = s[2:4]
            mm = s[5:7]
            return f"{yy}{mm}"
        except (IndexError, ValueError):
            pass

    # yyyymm(6桁) → yymm
    if len(s) == 6 and s.isdigit():
        return s[2:6]

    # yyyy/mm → yymm
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 2:
            try:
                yy = parts[0][-2:]
                mm = parts[1].zfill(2)
                return f"{yy}{mm}"
            except (IndexError, ValueError):
                pass

    # 「2025年12月」→ yymm
    import re
    m = re.match(r"(\d{4})年(\d{1,2})月", s)
    if m:
        return f"{m.group(1)[2:]}{m.group(2).zfill(2)}"

    # 変換できない場合はそのまま
    return s


def _parse_vertical_csv(df) -> list:
    """縦型CSV/Excelをパース（複数FMT対応 + チェック機能付き）

    対応FMT:
    - ハレノイエ式: カテゴリ=実数値、指標列にリーチ数/プロフアクセス数/∟プロフ/CV数等
    - 建装式: 同上だが運用前列あり、CV行なし、月列重複(2501と2501.1)
    - 旧FMT: カテゴリにリーチ/プロフ等、指標に合計/フィード計等
    """
    import pandas as pd
    import streamlit as st

    col_names = list(df.columns)

    # --- Step 1: 月データ列を特定（yymm形式の数値列のみ、Unnamed除外） ---
    month_cols = []
    seen_months = set()
    for c in col_names:
        # Unnamed列はスキップ
        if "unnamed" in str(c).lower():
            continue
        try:
            val = int(float(c))
            if 2300 <= val <= 2700 and val not in seen_months:
                month_cols.append(c)
                seen_months.add(val)
        except (ValueError, TypeError):
            pass

    # 月列をソート（非連続な列順に対応）
    month_cols.sort(key=lambda c: int(float(c)))

    if len(month_cols) < 1:
        st.error(f"月データ列が不足しています（{len(month_cols)}列）。yymm形式(例: 2501)の列が1つ以上必要です。")
        return []
    if len(month_cols) < 3:
        st.warning("3ヶ月未満のデータのため、精度が低い可能性があります。3ヶ月以上のデータを推奨します。")
        return []

    # --- Step 2: カテゴリ列・指標列を特定（複数FMT対応） ---
    # カテゴリ列: 「目標/実数値/本数/フォロワー/ビュー/リーチ/ENG/保存/プロフ/リンククリック/CV/歩留/変数/施策」等が入る列
    # 指標列: 「合計/リーチ数/プロフアクセス数/リンククリック数/CV件数」等が入る列（階層行 ∟〜 を含む）
    CAT_KEYWORDS = ["目標", "実数値", "本数", "フォロワー", "ビュー", "リーチ", "ENG", "保存",
                    "プロフ", "リンククリック", "CV", "歩留", "変数", "施策", "最終数値", "差分"]
    MET_KEYWORDS = ["合計", "フィード計", "リール計", "平均", "リーチ合計", "プロフアクセス数",
                    "リンククリック数", "CV数", "CV件数", "フィード投稿数", "リール投稿数",
                    "月次増加", "エリア内", "フィード平均", "リール平均", "ストーリーズ"]

    # 各列のキーワードヒット数を計算
    col_scores = {}
    for c in col_names:
        if c in month_cols:
            continue
        col_values = [str(v).strip() for v in df[c].dropna().tolist()]
        # 各カテゴリキーワードが含まれるセル数
        cat_hits = sum(1 for v in col_values for kw in CAT_KEYWORDS if kw in v)
        met_hits = sum(1 for v in col_values for kw in MET_KEYWORDS if kw in v)
        # 「∟」で始まる階層行は指標列の特徴
        hierarchy_hits = sum(1 for v in col_values if v.startswith(("∟", "└", "├")))
        col_scores[c] = {"cat": cat_hits, "met": met_hits + hierarchy_hits * 2}

    # カテゴリ列 = cat_hitsが最大、指標列 = met_hitsが最大（カテゴリ列とは別）
    cat_col = None
    best_cat_score = 0
    for c, scores in col_scores.items():
        if scores["cat"] > best_cat_score:
            best_cat_score = scores["cat"]
            cat_col = c

    met_col = None
    best_met_score = 0
    for c, scores in col_scores.items():
        if c == cat_col:
            continue
        if scores["met"] > best_met_score:
            best_met_score = scores["met"]
            met_col = c

    # フォールバック: 非月列から順に割り当て
    non_month = [c for c in col_names if c not in month_cols and "unnamed" not in str(c).lower()]
    if cat_col is None and non_month:
        cat_col = non_month[0]
    if met_col is None:
        for c in non_month:
            if c != cat_col:
                met_col = c
                break
        if met_col is None:
            met_col = cat_col

    # --- Step 3: 全行をパースして行マップを構築 ---
    row_map = []
    for idx, row in df.iterrows():
        cat = str(row.get(cat_col, "")).strip() if pd.notna(row.get(cat_col)) else ""
        met = str(row.get(met_col, "")).strip() if pd.notna(row.get(met_col)) else ""
        # 「∟」「└」を除去してクリーンなキーワードを作成
        met_clean = met.lstrip("∟└─├　 ")
        row_map.append({"idx": idx, "cat": cat, "met": met, "met_clean": met_clean, "row": row})

    def _safe_num(val):
        """セル値を安全に数値化"""
        try:
            if pd.isna(val):
                return 0.0
            s = str(val).replace(",", "").replace("%", "").strip()
            if s in ("", "-", "#DIV/0!", "#N/A", "#VALUE!"):
                return 0.0
            return float(s)
        except (ValueError, TypeError):
            return 0.0

    # 目標セクションの行範囲を特定（「目標」「(後伸び含む)」「最終数値」「差分」カテゴリ行）
    # これらのセクションの値は実績ではなく目標値
    EXCLUDE_SECTIONS = ["目標", "最終数値", "差分", "(後伸び", "（後伸び"]
    excluded_idx = set()
    current_section_excluded = False
    for r in row_map:
        cat = r["cat"]
        if cat:
            # 新しいカテゴリが始まったら判定更新
            current_section_excluded = any(ex in cat for ex in EXCLUDE_SECTIONS)
        if current_section_excluded:
            excluded_idx.add(r["idx"])

    # 変数セクション（歩留変数・ENG率・プロフアクセス率等）は実数として取らない
    variable_idx = set()
    current_section_variable = False
    for r in row_map:
        cat = r["cat"]
        if cat:
            current_section_variable = "変数" in cat or "歩留" in cat
        if current_section_variable:
            variable_idx.add(r["idx"])

    def _find_row(keywords: list, section: str = "実数") -> dict | None:
        """指標列のキーワードで行を検索

        section:
          "実数": 目標セクション・変数セクション・差分セクションを除外（実績のみ）
          "変数": 変数セクション（歩留変数）のみ対象
          None: 全行対象
        """
        for kw in keywords:
            kw_clean = kw.lstrip("∟└─├　 ").strip()
            kw_base = kw_clean.rstrip("数件率")
            for r in row_map:
                mc = r["met_clean"]
                mc_base = mc.rstrip("数件率")
                # 完全一致 or ベース一致
                if mc == kw_clean or mc_base == kw_base:
                    # セクションフィルタ
                    if section == "実数":
                        if r["idx"] in excluded_idx or r["idx"] in variable_idx:
                            continue
                    elif section == "変数":
                        if r["idx"] not in variable_idx:
                            continue
                    return r
        return None

    def _get_val(row_data: dict | None, month_col) -> float:
        if row_data is None:
            return 0.0
        return _safe_num(row_data["row"].get(month_col, 0))

    # --- Step 4: 各指標の行を事前に特定（1回だけ検索） ---
    row_reach = _find_row(["リーチ数", "リーチ合計", "リーチ"], section="実数")
    # リーチ合計行を優先（「リーチ合計」vs 集約列としての「リーチ」）
    if row_reach is None or row_reach.get("met_clean") == "リーチ":
        # 「リーチ」カテゴリ行で指標が「合計」の行を探す
        for r in row_map:
            if "リーチ" in r["cat"] and r["met_clean"] == "合計":
                if r["idx"] not in excluded_idx and r["idx"] not in variable_idx:
                    row_reach = r
                    break

    row_pa = _find_row(["プロフアクセス数", "プロフアクセス"], section="実数")
    row_clicks = _find_row(["リンククリック数", "リンククリック"], section="実数")
    row_clicks_prof = _find_row(["プロフ"], section=None)  # ∟プロフ（リンククリックの子行）
    row_clicks_story = _find_row(["ストーリーズ/ハイライト", "ストーリーズ", "ハイライト"], section=None)

    # CV行検索: CV件数を最優先、「CV」カテゴリで∟子行のCV件数も探す
    row_cv = _find_row(["CV件数", "CV数"], section="実数")
    if row_cv is None:
        # 「CV」を含むカテゴリ配下の行を探す（例: CV（LINE登録者）数）
        for r in row_map:
            if ("CV" in r["cat"]) and r["idx"] not in excluded_idx and r["idx"] not in variable_idx:
                if "件" in r["met_clean"] or r["met_clean"] in ("合計", "CV"):
                    row_cv = r
                    break

    row_followers = _find_row(["フォロワー数", "フォロワー"], section="実数")
    row_eng = _find_row(["ENG数", "ENG"], section="実数")
    row_views = _find_row(["ビュー数", "ビュー"], section="実数")

    # ∟プロフ行がリンククリックの子かプロフアクセスの子か判別
    # → リンククリック行の直後にあれば子行
    if row_clicks_prof and row_clicks:
        if abs(row_clicks_prof["idx"] - row_clicks["idx"]) > 3:
            row_clicks_prof = None  # 離れすぎている場合は別の「プロフ」行

    # --- Step 5: チェック結果を表示 ---
    st.markdown("##### 📋 指標検出チェック")
    check_items = [
        ("リーチ数", row_reach),
        ("プロフアクセス数", row_pa),
        ("リンククリック数", row_clicks),
        ("∟プロフ経由", row_clicks_prof),
        ("∟ストーリーズ/ハイライト", row_clicks_story),
        ("CV数", row_cv),
        ("フォロワー数", row_followers),
    ]

    check_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;">'
    for label, found in check_items:
        if found:
            src = f'行{found["idx"]}: {found["met"]}'
            check_html += f'<div style="background:#1a3020;border:1px solid #2a5a3a;border-radius:8px;padding:6px 12px;font-size:0.85rem;"><span style="color:#5aba6f;">✓</span> <span style="color:#c0c8d4;">{label}</span><br><span style="color:#6a8a6a;font-size:0.75rem;">{src}</span></div>'
        else:
            check_html += f'<div style="background:#3a2020;border:1px solid #5a3030;border-radius:8px;padding:6px 12px;font-size:0.85rem;"><span style="color:#ba5a5a;">✗</span> <span style="color:#c0c8d4;">{label}</span><br><span style="color:#8a6060;font-size:0.75rem;">未検出</span></div>'
    check_html += '</div>'
    st.markdown(check_html, unsafe_allow_html=True)

    if not row_reach and not row_pa:
        st.error("リーチ数・プロフアクセス数のどちらも検出できません。フォーマットを確認してください。")
        return []

    # --- Step 6: 月別データを抽出 ---
    monthly_data_list = []
    for mc in month_cols:
        reach = _get_val(row_reach, mc)
        pa = _get_val(row_pa, mc)
        clicks = _get_val(row_clicks, mc)
        clicks_prof = _get_val(row_clicks_prof, mc)
        clicks_story = _get_val(row_clicks_story, mc)
        cv = _get_val(row_cv, mc)

        # クリック合計がない場合、プロフ+ストーリーから算出
        if clicks == 0 and (clicks_prof > 0 or clicks_story > 0):
            clicks = clicks_prof + clicks_story

        md = MonthlyData(
            month=_format_month_label(mc),
            reach=int(reach),
            profile_access=int(pa),
            link_clicks=int(clicks),
            link_clicks_profile=int(clicks_prof) if clicks_prof > 0 else None,
            link_clicks_story=int(clicks_story) if clicks_story > 0 else None,
            cv=int(cv),
            cv_inquiry=0,
            cv_visit=0,
        )
        monthly_data_list.append(md)

    # --- Step 7: パース結果プレビュー + 整合性チェック ---
    valid_data = [d for d in monthly_data_list if d.reach > 0 or d.profile_access > 0 or d.link_clicks > 0 or d.cv > 0]
    st.success(f"✅ {len(valid_data)}ヶ月分の有効データを検出（全{len(monthly_data_list)}列中）")

    preview_data = []
    warnings = []
    for d in valid_data:
        row_dict = {
            "月": d.month,
            "リーチ": f"{d.reach:,}",
            "プロフアクセス": f"{d.profile_access:,}",
            "PA率": f"{d.profile_access_rate:.2f}%",
            "クリック": f"{d.link_clicks:,}",
            "CL率": f"{d.link_click_rate:.2f}%",
            "CV": d.cv,
            "CV率": f"{d.cv_rate:.2f}%",
        }
        preview_data.append(row_dict)

        # 整合性チェック
        if d.reach > 0 and d.profile_access > d.reach:
            warnings.append(f"[{d.month}] PA({d.profile_access:,}) > リーチ({d.reach:,})")
        if d.profile_access > 0 and d.link_clicks > d.profile_access:
            warnings.append(f"[{d.month}] クリック({d.link_clicks:,}) > PA({d.profile_access:,})")
        if d.profile_access_rate > 50:
            warnings.append(f"[{d.month}] PA率{d.profile_access_rate:.1f}%が異常に高い")

    st.dataframe(preview_data, use_container_width=True, hide_index=True)

    if warnings:
        with st.expander(f"⚠️ {len(warnings)}件の整合性警告"):
            for w in warnings:
                st.warning(w)

    return valid_data


def _parse_horizontal_csv(df) -> list:
    """横型CSV（行=月、列=指標）をパース（表記ゆれ対応）"""
    import pandas as pd

    # 列名の正規化（表記ゆれを幅広く吸収）
    col_map = {
        # 英語
        "month": "月", "reach": "リーチ数", "profile_access": "プロフアクセス数",
        "link_clicks": "リンククリック数", "cv": "CV数",
        "cv_inquiry": "資料請求", "cv_visit": "来場予約",
        "clicks_profile": "プロフ経由クリック", "clicks_story": "ストーリー経由クリック",
        "reach_ad": "広告リーチ数", "reach_organic": "オーガニックリーチ数",
        # 「数」なし表記
        "リーチ": "リーチ数", "プロフアクセス": "プロフアクセス数",
        "リンククリック": "リンククリック数", "CV": "CV数", "CV件数": "CV数",
        "CV件": "CV数", "cv数": "CV数", "Cv": "CV数",
        # よくある別名
        "プロフィールアクセス数": "プロフアクセス数", "プロフィールアクセス": "プロフアクセス数",
        "クリック数": "リンククリック数", "クリック": "リンククリック数",
        "Webクリック数": "リンククリック数", "Webクリック": "リンククリック数",
        "コンバージョン": "CV数", "コンバージョン数": "CV数",
        "反響数": "CV数", "反響": "CV数",
        "資料請求数": "資料請求", "来場予約数": "来場予約", "来場数": "来場予約", "来場": "来場予約",
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    import streamlit as st

    required = ["月", "リーチ数", "プロフアクセス数", "リンククリック数", "CV数"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"必須列が不足しています: {', '.join(missing)}")
        return []

    if len(df) < 1:
        st.error(f"最低1ヶ月分のデータが必要です（現在 {len(df)}行）")
        return []
    if len(df) < 3:
        st.warning("3ヶ月未満のデータのため、精度が低い可能性があります。3ヶ月以上のデータを推奨します。")

    st.success(f"✅ {len(df)}ヶ月分のデータを読み込みました（横型フォーマット）")

    def _safe_int(val, default=0):
        try:
            v = int(float(val))
            return v if v >= 0 else default
        except (ValueError, TypeError):
            return default

    monthly_data_list = []
    for _, row in df.iterrows():
        reach_ad = _safe_int(row.get("広告リーチ数", 0))
        reach_org = _safe_int(row.get("オーガニックリーチ数", 0))
        clicks_prof = _safe_int(row.get("プロフ経由クリック", 0))
        clicks_story = _safe_int(row.get("ストーリー経由クリック", 0))

        md = MonthlyData(
            month=_format_month_label(row.get("月", "")),
            reach=_safe_int(row.get("リーチ数")),
            profile_access=_safe_int(row.get("プロフアクセス数")),
            link_clicks=_safe_int(row.get("リンククリック数")),
            cv=_safe_int(row.get("CV数")),
            cv_inquiry=_safe_int(row.get("資料請求", 0)),
            cv_visit=_safe_int(row.get("来場予約", 0)),
            link_clicks_profile=clicks_prof if clicks_prof > 0 else None,
            link_clicks_story=clicks_story if clicks_story > 0 else None,
            reach_ad=reach_ad if reach_ad > 0 else None,
            reach_organic=reach_org if reach_org > 0 else None,
        )
        monthly_data_list.append(md)
    return monthly_data_list


def render_knowledge_tab():
    """ナレッジ管理タブ"""
    st.header("📚 ナレッジ管理")

    data_type = st.selectbox("登録するデータの種類", ["打ち手・施策", "成功事例"])

    import_method = st.radio(
        "インポート方法",
        ["フォーム入力", "テキスト貼り付け", "CSVアップロード", "ドキュメント/PDF", "画像/スクショ"],
        horizontal=True,
    )

    if import_method == "フォーム入力":
        if data_type == "打ち手・施策":
            _render_tactic_form()
        else:
            _render_case_form()

    elif import_method == "テキスト貼り付け":
        text = st.text_area("テキストを貼り付け", height=200, placeholder="施策の内容や事例をテキストで貼り付けてください")
        if st.button("インポート"):
            dtype = "tactic" if data_type == "打ち手・施策" else "case"
            tid = km.import_from_text(text, dtype)
            st.success(f"インポート完了 (ID: {tid})")

    elif import_method == "CSVアップロード":
        uploaded = st.file_uploader("CSVファイル", type=["csv"])
        if uploaded and st.button("インポート"):
            content = uploaded.read().decode("utf-8")
            dtype = "tactic" if data_type == "打ち手・施策" else "case"
            ids = km.import_from_csv(content, dtype)
            st.success(f"{len(ids)}件インポート完了")

    elif import_method == "ドキュメント/PDF":
        st.info("PDF・Markdown・テキスト・Word(.docx) ファイルをアップロードできます。テキストを自動抽出してナレッジに登録します。")
        uploaded = st.file_uploader(
            "ドキュメントをアップロード",
            type=["pdf", "md", "txt", "docx"],
            accept_multiple_files=True,
            key="doc_upload",
        )
        if uploaded and st.button("📄 ドキュメントをインポート"):
            dtype = "tactic" if data_type == "打ち手・施策" else "case"
            for f in uploaded:
                rid = km.import_from_document(f.read(), f.name, dtype)
                st.success(f"✅ {f.name} → インポート完了 (ID: {rid})")

    elif import_method == "画像/スクショ":
        st.info("画像・スクリーンショットをアップロードして、打ち手や事例に添付できます。")
        # 既存ナレッジに添付 or 新規作成
        attach_mode = st.radio("添付先", ["新規ナレッジとして登録", "既存ナレッジに添付"], horizontal=True, key="attach_mode")

        uploaded_images = st.file_uploader(
            "画像をアップロード",
            type=["png", "jpg", "jpeg", "gif", "webp", "bmp"],
            accept_multiple_files=True,
            key="img_upload",
        )

        if attach_mode == "新規ナレッジとして登録":
            caption = st.text_input("画像の説明（任意）", placeholder="例: 見学会デザイン改善のビフォーアフター")
            if uploaded_images and st.button("🖼️ 画像付きナレッジを登録"):
                dtype = "tactic" if data_type == "打ち手・施策" else "case"
                rid = km.import_from_text(caption or "画像ナレッジ", dtype)
                for img in uploaded_images:
                    km.save_file(img.read(), img.name, rid)
                st.success(f"✅ {len(uploaded_images)}枚の画像付きナレッジを登録しました (ID: {rid})")
        else:
            # 既存ナレッジ選択
            dtype = "tactic" if data_type == "打ち手・施策" else "case"
            if dtype == "tactic":
                items = km.get_all_tactics()
                options = {t["id"]: f"{t.get('tactic_name', '不明')}" for t in items}
            else:
                items = km.get_all_cases()
                options = {c["id"]: f"{c.get('company_name', '不明')}" for c in items}

            if options:
                selected_id = st.selectbox("添付先を選択", list(options.keys()), format_func=lambda x: options[x])
                if uploaded_images and st.button("🖼️ 画像を添付"):
                    for img in uploaded_images:
                        km.save_file(img.read(), img.name, selected_id)
                    st.success(f"✅ {len(uploaded_images)}枚の画像を添付しました")
            else:
                st.warning("添付先のナレッジがありません。先にナレッジを登録してください。")


def _render_tactic_form():
    """打ち手登録フォーム"""
    with st.form("tactic_form"):
        name = st.text_input("施策名", placeholder="例: ギフトカード訴求ストーリーズ")
        target = st.selectbox("対象指標", ["リーチ", "プロフアクセス率", "リンククリック率", "反響率"])
        desc = st.text_area("説明", placeholder="具体的な施策内容を記載")
        plan = st.multiselect("適用プラン", ["スタンダード", "アドバンス"], default=["アドバンス"])
        category = st.selectbox("カテゴリ", ["フィード", "リール", "ストーリーズ", "ハイライト", "総合", "その他"])
        impact = st.selectbox("期待効果", ["高", "中", "低"])
        source = st.text_input("出典", placeholder="例: 建装様事例")
        images = st.file_uploader("📷 画像を添付（任意）", type=["png", "jpg", "jpeg", "gif", "webp"], accept_multiple_files=True, key="tactic_imgs")

        if st.form_submit_button("登録"):
            tactic = {
                "target_metric": target,
                "tactic_name": name,
                "description": desc,
                "plan_type": plan,
                "category": category,
                "expected_impact": impact,
                "source": source,
            }
            tid = km.save_tactic(tactic)
            for img in (images or []):
                km.save_file(img.read(), img.name, tid)
            img_msg = f"（画像{len(images)}枚添付）" if images else ""
            st.success(f"施策を登録しました {img_msg} (ID: {tid})")


def _render_case_form():
    """事例登録フォーム"""
    with st.form("case_form"):
        name = st.text_input("会社名", placeholder="例: 建装様")
        area = st.text_input("エリア", placeholder="例: 山形")
        plan_hist = st.text_input("プラン履歴", placeholder="例: St(3ヶ月) → Ad(9ヶ月)")
        tactics = st.text_input("主要施策（カンマ区切り）", placeholder="例: フォロー施策,ストーリーズ施策")
        notes = st.text_area("備考・成果", placeholder="成果や学びを記載")
        images = st.file_uploader("📷 画像・スクショを添付（任意）", type=["png", "jpg", "jpeg", "gif", "webp"], accept_multiple_files=True, key="case_imgs")
        docs = st.file_uploader("📄 ドキュメント/PDFを添付（任意）", type=["pdf", "md", "txt", "docx"], accept_multiple_files=True, key="case_docs")

        if st.form_submit_button("登録"):
            case = {
                "company_name": name,
                "area": area,
                "plan_history": plan_hist,
                "monthly_data": [],
                "key_tactics": [t.strip() for t in tactics.split(",") if t.strip()],
                "notes": notes,
            }
            cid = km.save_case(case)
            for img in (images or []):
                km.save_file(img.read(), img.name, cid)
            for doc in (docs or []):
                meta = km.save_file(doc.read(), doc.name, cid)
                # PDFなどのテキストをnotesに追記
                if meta.get("extracted_text"):
                    case["notes"] = (case.get("notes", "") + "\n\n--- 添付ドキュメント ---\n" + meta["extracted_text"])[:2000]
                    km.save_case(case)
            file_count = len(images or []) + len(docs or [])
            file_msg = f"（ファイル{file_count}件添付）" if file_count else ""
            st.success(f"事例を登録しました {file_msg} (ID: {cid})")


def render_archive_tab():
    """戦略設計室タブ"""
    st.header("📂 戦略設計室")

    # --- 手動登録 ---
    with st.expander("➕ 過去の戦略設計を手動登録"):
        with st.form("archive_manual_form"):
            a_name = st.text_input("会社名", placeholder="例: ゼロホーム様")
            a_col1, a_col2, a_col3 = st.columns(3)
            with a_col1:
                a_area = st.text_input("エリア", placeholder="例: 東京都", key="arc_area")
            with a_col2:
                a_plan = st.selectbox("運用プラン", ["スタンダード", "アドバンス"], key="arc_plan")
            with a_col3:
                a_followers = st.number_input("フォロワー数", min_value=0, value=0, step=100, key="arc_followers")

            st.markdown("**現状数値（月間平均）**")
            ac1, ac2, ac3, ac4 = st.columns(4)
            with ac1:
                a_reach = st.number_input("リーチ数", min_value=0, value=0, step=1000, key="arc_reach")
            with ac2:
                a_pa = st.number_input("プロフアクセス数", min_value=0, value=0, step=100, key="arc_pa")
            with ac3:
                a_clicks = st.number_input("クリック数", min_value=0, value=0, step=10, key="arc_clicks")
            with ac4:
                a_cv = st.number_input("CV数", min_value=0, value=0, step=1, key="arc_cv")

            st.markdown("**目標KPI**")
            at1, at2, at3, at4 = st.columns(4)
            with at1:
                a_t_reach = st.number_input("目標リーチ", min_value=0, value=0, step=1000, key="arc_t_reach")
            with at2:
                a_t_pa = st.number_input("目標プロフアクセス", min_value=0, value=0, step=100, key="arc_t_pa")
            with at3:
                a_t_clicks = st.number_input("目標クリック", min_value=0, value=0, step=10, key="arc_t_clicks")
            with at4:
                a_t_cv = st.number_input("目標CV", min_value=0, value=0, step=1, key="arc_t_cv")

            a_bottleneck = st.selectbox("主要ボトルネック", ["プロフアクセス率", "リンククリック率", "反響率", "リーチ数", "なし"], key="arc_bn")
            a_strategy = st.text_area("打ち手・施策メモ", placeholder="実施した施策や成果を記載", key="arc_strategy")
            a_images = st.file_uploader("📷 画像・スクショを添付（任意）", type=["png", "jpg", "jpeg", "gif", "webp"], accept_multiple_files=True, key="arc_imgs")
            a_docs = st.file_uploader("📄 ドキュメント/PDF（任意）", type=["pdf", "md", "txt", "docx"], accept_multiple_files=True, key="arc_docs")

            if st.form_submit_button("💾 アーカイブに登録"):
                pa_rate = (a_pa / a_reach * 100) if a_reach > 0 else 0
                lc_rate = (a_clicks / a_pa * 100) if a_pa > 0 else 0
                cv_rate = (a_cv / a_clicks * 100) if a_clicks > 0 else 0
                archive = {
                    "company_name": a_name,
                    "area": a_area,
                    "plan_type": a_plan,
                    "followers": a_followers,
                    "metrics": {
                        "avg_reach": a_reach, "avg_profile_access": a_pa,
                        "avg_link_clicks": a_clicks, "avg_cv": a_cv,
                        "avg_cv_inquiry": 0, "avg_cv_visit": 0,
                        "profile_access_rate": pa_rate, "link_click_rate": lc_rate,
                        "cv_rate": cv_rate, "ad_ratio": None,
                        "trend_reach": "不明", "trend_profile_access": "不明",
                        "trend_link_clicks": "不明", "trend_cv": "不明",
                    },
                    "targets": {
                        "目標": {"reach": a_t_reach, "profile_access": a_t_pa,
                                "link_clicks": a_t_clicks, "cv": a_t_cv} if a_t_cv > 0 else None,
                    },
                    "bottleneck": a_bottleneck,
                    "feasibility": "不明",
                    "strategy_text": a_strategy,
                    "report_md": "",
                    "source": "手動登録",
                }
                aid = km.save_archive(archive)
                for img in (a_images or []):
                    km.save_file(img.read(), img.name, aid)
                for doc in (a_docs or []):
                    km.save_file(doc.read(), doc.name, aid)
                st.success(f"✅ アーカイブに登録しました (ID: {aid})")

    st.divider()

    # --- 一覧表示 ---
    archives = km.get_all_archives()
    if not archives:
        st.info("まだ戦略設計のアーカイブがありません。\n\n「🎯 戦略設計」タブで実行後に「💾 アーカイブ保存」するか、上のフォームから手動登録してください。")
        return

    # ========== ランキングダッシュボード ==========
    st.subheader("🏆 ランキングダッシュボード")

    import plotly.graph_objects as go

    names = [a.get("company_name", "不明") for a in archives]
    metrics_list = [a.get("metrics", {}) for a in archives]

    ranking_metric = st.selectbox("ランキング指標", [
        "CV数", "リーチ数", "プロフアクセス率", "リンククリック率", "反響率(CV率)", "フォロワー数",
    ], key="ranking_metric")

    metric_map = {
        "CV数": ("avg_cv", "CV数", "件"),
        "リーチ数": ("avg_reach", "リーチ数", ""),
        "プロフアクセス率": ("profile_access_rate", "プロフアクセス率", "%"),
        "リンククリック率": ("link_click_rate", "リンククリック率", "%"),
        "反響率(CV率)": ("cv_rate", "反響率", "%"),
        "フォロワー数": (None, "フォロワー数", ""),
    }
    m_key, m_label, m_unit = metric_map[ranking_metric]

    if m_key:
        values = [m.get(m_key, 0) for m in metrics_list]
    else:
        values = [a.get("followers", 0) for a in archives]

    # ソート（降順）
    sorted_pairs = sorted(zip(names, values, archives), key=lambda x: x[1], reverse=True)
    sorted_names = [p[0] for p in sorted_pairs]
    sorted_values = [p[1] for p in sorted_pairs]

    # ランキング棒グラフ（横向き）
    colors = []
    for i in range(len(sorted_names)):
        if i == 0:
            colors.append("#FFD700")   # 金
        elif i == 1:
            colors.append("#C0C0C0")   # 銀
        elif i == 2:
            colors.append("#CD7F32")   # 銅
        else:
            colors.append("#3b82c4")

    fig_rank = go.Figure(go.Bar(
        x=sorted_values[::-1],
        y=sorted_names[::-1],
        orientation="h",
        marker_color=colors[::-1],
        text=[f"{v:,.1f}{m_unit}" if isinstance(v, float) else f"{v:,}{m_unit}" for v in sorted_values[::-1]],
        textposition="outside",
    ))
    fig_rank.update_layout(
        title=f"🏆 {m_label} ランキング",
        height=max(300, len(archives) * 50 + 100),
        xaxis_title=m_label,
        margin=dict(l=150),
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    # ランキングテーブル
    rank_cols = st.columns([1, 3, 2, 2, 2, 2, 2])
    rank_cols[0].markdown("**順位**")
    rank_cols[1].markdown("**会社名**")
    rank_cols[2].markdown("**リーチ**")
    rank_cols[3].markdown("**プロフアクセス率**")
    rank_cols[4].markdown("**クリック率**")
    rank_cols[5].markdown("**CV率**")
    rank_cols[6].markdown("**CV数**")
    for i, (n, v, arc) in enumerate(sorted_pairs):
        m = arc.get("metrics", {})
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}"
        cols = st.columns([1, 3, 2, 2, 2, 2, 2])
        cols[0].write(medal)
        cols[1].write(n)
        cols[2].write(f"{m.get('avg_reach', 0):,.0f}")
        cols[3].write(f"{m.get('profile_access_rate', 0):.2f}%")
        cols[4].write(f"{m.get('link_click_rate', 0):.2f}%")
        cols[5].write(f"{m.get('cv_rate', 0):.2f}%")
        cols[6].write(f"{m.get('avg_cv', 0):.1f}")

    # ========== 全アカウント比較 ==========
    st.divider()
    st.subheader("📊 全アカウント比較")

    # 指標ごとに個別の横棒グラフ（2列×2行）
    from plotly.subplots import make_subplots

    compare_items = [
        ("リーチ数", "avg_reach", "#2a5a7e"),
        ("プロフアクセス数", "avg_profile_access", "#1e6fa0"),
        ("クリック数", "avg_link_clicks", "#2389bf"),
        ("CV数", "avg_cv", "#c8b898"),
    ]

    fig_compare = make_subplots(
        rows=2, cols=2,
        subplot_titles=[c[0] for c in compare_items],
        horizontal_spacing=0.2, vertical_spacing=0.18,
    )

    for idx, (label, key, color) in enumerate(compare_items):
        row = idx // 2 + 1
        col = idx % 2 + 1
        values = [m.get(key, 0) for m in metrics_list]
        # 降順ソート
        pairs = sorted(zip(names, values), key=lambda x: x[1], reverse=True)
        s_names = [p[0] for p in pairs]
        s_vals = [p[1] for p in pairs]

        fig_compare.add_trace(go.Bar(
            y=s_names[::-1], x=s_vals[::-1], orientation="h",
            marker=dict(color=color, line=dict(color="rgba(200,184,152,0.2)", width=1)),
            text=[f"{v:,.0f}" if v >= 1 else f"{v:.1f}" for v in s_vals[::-1]],
            textposition="outside", textfont=dict(color="#c8b898", size=11),
            showlegend=False,
            hovertemplate="%{y}<br>" + label + ": %{x:,.0f}<extra></extra>",
        ), row=row, col=col)

    fig_compare.update_layout(
        height=max(500, len(names) * 50 + 200),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c0c8d4", size=11),
        margin=dict(l=10, r=40, t=50, b=20),
    )
    fig_compare.update_xaxes(showgrid=True, gridcolor="rgba(180,160,120,0.06)", zeroline=False)
    fig_compare.update_yaxes(showgrid=False, tickfont=dict(size=11, color="#a0a8b4"))
    # サブプロットタイトルのスタイル
    for ann in fig_compare.layout.annotations:
        ann.font = dict(size=13, color="#c8b898")

    st.plotly_chart(fig_compare, use_container_width=True)

    # 遷移率比較（テーブル + バー可視化）
    st.markdown("#### 遷移率比較")

    rate_items = [
        ("プロフアクセス率", "profile_access_rate"),
        ("リンククリック率", "link_click_rate"),
        ("反響率(CV率)", "cv_rate"),
    ]

    # テーブル形式で表示
    rate_table_html = """
    <div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden;">
    <tr>
        <th style="background:#1a3048;color:#e8dcc8;padding:12px 16px;text-align:left;font-weight:600;border-bottom:1px solid rgba(180,160,120,0.15);">会社名</th>
    """
    for label, _ in rate_items:
        rate_table_html += f'<th style="background:#1a3048;color:#e8dcc8;padding:12px 16px;text-align:center;font-weight:600;border-bottom:1px solid rgba(180,160,120,0.15);">{label}</th>'
    rate_table_html += "</tr>"

    # 各アカウントの行
    for name_t, m in zip(names, metrics_list):
        rate_table_html += f'<tr><td style="background:#12181f;color:#d0d8e0;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04);font-weight:500;">{name_t}</td>'
        for _, key in rate_items:
            val = m.get(key, 0)
            # バー幅（最大値に対する比率）
            max_val = max(mm.get(key, 0) for mm in metrics_list) if metrics_list else 1
            bar_pct = min((val / max_val * 100) if max_val > 0 else 0, 100)
            bar_color = "#c8b898" if val == max_val and val > 0 else "#2a5a7e"
            val_color = "#e8dcc8" if val == max_val and val > 0 else "#c0c8d4"
            rate_table_html += f"""
            <td style="background:#12181f;padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;background:rgba(255,255,255,0.04);border-radius:4px;height:8px;overflow:hidden;">
                        <div style="width:{bar_pct:.0f}%;height:100%;background:{bar_color};border-radius:4px;"></div>
                    </div>
                    <span style="color:{val_color};font-weight:600;font-size:0.9rem;min-width:55px;text-align:right;">{val:.2f}%</span>
                </div>
            </td>"""
        rate_table_html += "</tr>"

    rate_table_html += "</table></div>"
    st.markdown(rate_table_html, unsafe_allow_html=True)

    # ========== 個別アーカイブ詳細 ==========
    st.divider()
    st.subheader(f"📋 アーカイブ詳細（{len(archives)}件）")

    for arc in archives:
        aid = arc.get("id", "")
        m = arc.get("metrics", {})
        created = arc.get("created_at", "")[:10]
        label = f"**{arc.get('company_name', '不明')}** | {arc.get('plan_type', '')} | {arc.get('area', '')} | {created}"

        with st.expander(label):
            # 基本情報
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            with info_col1:
                st.metric("フォロワー", f"{arc.get('followers', 0):,}")
            with info_col2:
                st.metric("ボトルネック", arc.get("bottleneck", "不明"))
            with info_col3:
                st.metric("達成可能性", arc.get("feasibility", "不明"))
            with info_col4:
                st.metric("登録元", arc.get("source", "自動生成"))

            # --- 個別ファネルグラフ ---
            categories = ["リーチ", "プロフアクセス", "クリック", "CV"]
            current_vals = [m.get("avg_reach", 0), m.get("avg_profile_access", 0), m.get("avg_link_clicks", 0), m.get("avg_cv", 0)]
            rates = ["", f"{m.get('profile_access_rate', 0):.2f}%", f"{m.get('link_click_rate', 0):.2f}%", f"{m.get('cv_rate', 0):.2f}%"]

            fig_ind = make_subplots(specs=[[{"secondary_y": True}]])
            fig_ind.add_trace(go.Bar(
                name="現状", x=categories, y=current_vals,
                text=[f"{v:,.0f}<br><b>{r}</b>" for v, r in zip(current_vals, rates)],
                textposition="outside", marker_color="#a8c4e0",
            ), secondary_y=False)

            # 目標値の棒を追加
            targets = arc.get("targets", {})
            target_colors = {"3ヶ月後": "#6ca6d9", "6ヶ月後": "#3b82c4", "12ヶ月後": "#1a5276", "目標": "#e74c3c"}
            for period, t_data in targets.items():
                if t_data is None:
                    continue
                t_vals = [t_data.get("reach", 0), t_data.get("profile_access", 0), t_data.get("link_clicks", 0), t_data.get("cv", 0)]
                t_rates_text = [
                    "",
                    f"{t_data.get('pa_rate', 0):.2f}%" if t_data.get("pa_rate") else "",
                    f"{t_data.get('lc_rate', 0):.2f}%" if t_data.get("lc_rate") else "",
                    f"{t_data.get('cv_rate', 0):.2f}%" if t_data.get("cv_rate") else "",
                ]
                fig_ind.add_trace(go.Bar(
                    name=f"目標: {period}", x=categories, y=t_vals,
                    text=[f"<b>{v:,.0f}</b><br>{r}" for v, r in zip(t_vals, t_rates_text)],
                    textposition="outside", marker_color=target_colors.get(period, "#888"),
                ), secondary_y=False)

            # 遷移率折れ線
            rate_cats = ["プロフアクセス率", "リンククリック率", "反響率"]
            rate_vals = [m.get("profile_access_rate", 0), m.get("link_click_rate", 0), m.get("cv_rate", 0)]
            fig_ind.add_trace(go.Scatter(
                name="遷移率", x=rate_cats, y=rate_vals,
                mode="lines+markers+text", text=[f"{v:.2f}%" for v in rate_vals],
                textposition="top center", line=dict(color="red", width=2, dash="dot"),
                marker=dict(size=10),
            ), secondary_y=True)

            fig_ind.update_layout(
                title=f"{arc.get('company_name', '')} ファネル分析", barmode="group", height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )
            fig_ind.update_yaxes(title_text="実数", secondary_y=False)
            fig_ind.update_yaxes(title_text="遷移率(%)", secondary_y=True)
            st.plotly_chart(fig_ind, use_container_width=True, key=f"chart_{aid}")

            # 打ち手
            strategy = arc.get("strategy_text", "")
            if strategy:
                with st.expander("🤖 打ち手・施策"):
                    st.markdown(strategy)

            # レポート出力
            report = arc.get("report_md", "")
            if not report:
                # 保存済みレポートがない場合、アーカイブデータから再生成
                report = _generate_archive_report(arc)

            with st.expander("📄 レポート全文"):
                st.markdown(report)

            st.download_button(
                label="📥 レポートをダウンロード",
                data=report,
                file_name=f"{arc.get('company_name', 'report')}_戦略設計レポート.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"dl_report_{aid}",
            )

            # 添付ファイル
            files = km.get_files_for(aid)
            if files:
                _render_attached_files(aid, f"arc_{aid}")

            # 編集・削除
            edit_col, del_col = st.columns(2)
            with edit_col:
                if st.button("✏️ 編集", key=f"edit_btn_{aid}", use_container_width=True):
                    st.session_state[f"editing_{aid}"] = True
            with del_col:
                if st.button("🗑️ 削除", key=f"del_arc_{aid}", use_container_width=True):
                    km.delete_archive(aid)
                    st.rerun()

            # 編集フォーム
            if st.session_state.get(f"editing_{aid}", False):
                _render_archive_edit_form(arc)


def _generate_archive_report(arc: dict) -> str:
    """アーカイブデータからMarkdownレポートを生成"""
    m = arc.get("metrics", {})
    company = arc.get("company_name", "不明")
    area = arc.get("area", "")
    plan = arc.get("plan_type", "")
    followers = arc.get("followers", 0)

    lines = []
    lines.append(f"# {company} Instagram CV戦略設計レポート")
    lines.append(f"\n**エリア**: {area} | **プラン**: {plan} | **フォロワー**: {followers:,}")
    lines.append(f"**作成日**: {arc.get('created_at', '')[:10]}")
    lines.append("")

    # 現状ファネル
    lines.append("## 現状ファネル数値")
    lines.append("")
    lines.append("| 指標 | 実数 | 転換率 | トレンド |")
    lines.append("|---|---|---|---|")
    lines.append(f"| リーチ数 | {m.get('avg_reach', 0):,.0f} | - | {m.get('trend_reach', '-')} |")
    lines.append(f"| プロフアクセス数 | {m.get('avg_profile_access', 0):,.0f} | {m.get('profile_access_rate', 0):.2f}% | {m.get('trend_profile_access', '-')} |")
    lines.append(f"| リンククリック数 | {m.get('avg_link_clicks', 0):,.0f} | {m.get('link_click_rate', 0):.2f}% | {m.get('trend_link_clicks', '-')} |")
    cv_detail = f"(資料請求:{m.get('avg_cv_inquiry', 0):.0f} / 来場:{m.get('avg_cv_visit', 0):.0f})" if m.get("avg_cv_inquiry") or m.get("avg_cv_visit") else ""
    lines.append(f"| CV数 | {m.get('avg_cv', 0):.1f} {cv_detail} | {m.get('cv_rate', 0):.2f}% | {m.get('trend_cv', '-')} |")

    # 月別データ
    monthly = arc.get("monthly_data", [])
    if monthly:
        lines.append("\n## 月別データ推移")
        lines.append("")
        lines.append("| 月 | リーチ数 | プロフアクセス数 | プロフアクセス率 | クリック数 | クリック率 | CV数 | 反響率 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for d in monthly:
            reach = d.get("reach", 0)
            pa = d.get("profile_access", 0)
            clicks = d.get("link_clicks", 0)
            cv = d.get("cv", 0)
            pa_rate = (pa / reach * 100) if reach > 0 else 0
            lc_rate = (clicks / pa * 100) if pa > 0 else 0
            cv_rate = (cv / clicks * 100) if clicks > 0 else 0
            lines.append(f"| {d.get('month', '')} | {reach:,} | {pa:,} | {pa_rate:.2f}% | {clicks:,} | {lc_rate:.2f}% | {cv} | {cv_rate:.2f}% |")

    # 目標KPI
    targets = arc.get("targets", {})
    active_targets = {k: v for k, v in targets.items() if v is not None}
    if active_targets:
        lines.append("\n## 目標KPI")
        lines.append("")
        header = ["指標"] + list(active_targets.keys())
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))
        for label, key in [("リーチ", "reach"), ("プロフアクセス", "profile_access"), ("クリック", "link_clicks"), ("CV", "cv")]:
            row = [label]
            for period, t in active_targets.items():
                val = t.get(key, 0)
                rate_key = {"profile_access": "pa_rate", "link_clicks": "lc_rate", "cv": "cv_rate"}.get(key)
                rate = f" ({t.get(rate_key, 0):.2f}%)" if rate_key and t.get(rate_key) else ""
                row.append(f"{val:,}{rate}")
            lines.append("| " + " | ".join(row) + " |")

    # ボトルネック
    lines.append(f"\n## ボトルネック分析")
    lines.append(f"\n**最大のボトルネック**: {arc.get('bottleneck', '不明')}")
    lines.append(f"**達成可能性**: {arc.get('feasibility', '不明')}")

    # 打ち手
    strategy = arc.get("strategy_text", "")
    if strategy:
        lines.append("\n## 打ち手・施策")
        lines.append(strategy)

    return "\n".join(lines)


def _render_archive_edit_form(arc: dict):
    """アーカイブ編集フォーム"""
    aid = arc["id"]
    m = arc.get("metrics", {})

    with st.form(f"edit_form_{aid}"):
        st.markdown("---")
        st.subheader("✏️ アーカイブ編集")

        e_col1, e_col2, e_col3 = st.columns(3)
        with e_col1:
            e_name = st.text_input("会社名", value=arc.get("company_name", ""), key=f"e_name_{aid}")
        with e_col2:
            e_area = st.text_input("エリア", value=arc.get("area", ""), key=f"e_area_{aid}")
        with e_col3:
            plan_options = ["スタンダード", "アドバンス"]
            current_plan = arc.get("plan_type", "アドバンス")
            e_plan = st.selectbox("プラン", plan_options, index=plan_options.index(current_plan) if current_plan in plan_options else 0, key=f"e_plan_{aid}")

        e_followers = st.number_input("フォロワー数", min_value=0, value=int(arc.get("followers", 0)), step=100, key=f"e_followers_{aid}")

        st.markdown("**現状数値（月間平均）**")
        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1:
            e_reach = st.number_input("リーチ数", min_value=0, value=int(m.get("avg_reach", 0)), step=1000, key=f"e_reach_{aid}")
        with ec2:
            e_pa = st.number_input("プロフアクセス数", min_value=0, value=int(m.get("avg_profile_access", 0)), step=100, key=f"e_pa_{aid}")
        with ec3:
            e_clicks = st.number_input("クリック数", min_value=0, value=int(m.get("avg_link_clicks", 0)), step=10, key=f"e_clicks_{aid}")
        with ec4:
            e_cv = st.number_input("CV数", min_value=0, value=int(m.get("avg_cv", 0)), step=1, key=f"e_cv_{aid}")

        ecv1, ecv2 = st.columns(2)
        with ecv1:
            e_cv_inq = st.number_input("うち資料請求", min_value=0, value=int(m.get("avg_cv_inquiry", 0)), step=1, key=f"e_cv_inq_{aid}")
        with ecv2:
            e_cv_vis = st.number_input("うち来場予約", min_value=0, value=int(m.get("avg_cv_visit", 0)), step=1, key=f"e_cv_vis_{aid}")

        # 目標KPI
        st.markdown("**目標KPI**")
        existing_targets = arc.get("targets", {})

        # 各期間の目標を編集可能に
        target_periods = ["3ヶ月後", "6ヶ月後", "12ヶ月後", "目標"]
        edited_targets = {}
        for period in target_periods:
            t_data = existing_targets.get(period)
            if t_data is not None or period in ["3ヶ月後", "6ヶ月後"]:
                with st.expander(f"📎 {period}の目標" + (" (設定済み)" if t_data else " (未設定)")):
                    default = t_data or {}
                    tc1, tc2, tc3, tc4 = st.columns(4)
                    with tc1:
                        t_r = st.number_input(f"目標リーチ ({period})", min_value=0, value=int(default.get("reach", 0)), step=1000, key=f"e_t_r_{period}_{aid}")
                    with tc2:
                        t_p = st.number_input(f"目標プロフアクセス ({period})", min_value=0, value=int(default.get("profile_access", 0)), step=100, key=f"e_t_p_{period}_{aid}")
                    with tc3:
                        t_c = st.number_input(f"目標クリック ({period})", min_value=0, value=int(default.get("link_clicks", 0)), step=10, key=f"e_t_c_{period}_{aid}")
                    with tc4:
                        t_cv = st.number_input(f"目標CV ({period})", min_value=0, value=int(default.get("cv", 0)), step=1, key=f"e_t_cv_{period}_{aid}")
                    if t_cv > 0 or t_r > 0:
                        t_pa_rate = (t_p / t_r * 100) if t_r > 0 else default.get("pa_rate", 0)
                        t_lc_rate = (t_c / t_p * 100) if t_p > 0 else default.get("lc_rate", 0)
                        t_cv_rate = (t_cv / t_c * 100) if t_c > 0 else default.get("cv_rate", 0)
                        edited_targets[period] = {"reach": t_r, "profile_access": t_p, "link_clicks": t_c, "cv": t_cv, "pa_rate": t_pa_rate, "lc_rate": t_lc_rate, "cv_rate": t_cv_rate}
                    else:
                        edited_targets[period] = None

        bn_options = ["プロフアクセス率", "リンククリック率", "反響率", "リーチ数", "なし"]
        current_bn = arc.get("bottleneck", "なし")
        e_bn = st.selectbox("ボトルネック", bn_options, index=bn_options.index(current_bn) if current_bn in bn_options else 0, key=f"e_bn_{aid}")

        e_strategy = st.text_area("打ち手・施策メモ", value=arc.get("strategy_text", ""), height=150, key=f"e_strategy_{aid}")

        # 画像・ドキュメント追加
        e_images = st.file_uploader("📷 画像を追加（任意）", type=["png", "jpg", "jpeg", "gif", "webp"], accept_multiple_files=True, key=f"e_imgs_{aid}")
        e_docs = st.file_uploader("📄 ドキュメントを追加（任意）", type=["pdf", "md", "txt", "docx"], accept_multiple_files=True, key=f"e_docs_{aid}")

        save_col, cancel_col = st.columns(2)
        submitted = st.form_submit_button("💾 保存", use_container_width=True)

    # キャンセルはフォーム外
    if st.button("❌ キャンセル", key=f"cancel_{aid}", use_container_width=True):
        st.session_state[f"editing_{aid}"] = False
        st.rerun()

    if submitted:
        pa_rate = (e_pa / e_reach * 100) if e_reach > 0 else 0
        lc_rate = (e_clicks / e_pa * 100) if e_pa > 0 else 0
        cv_rate = (e_cv / e_clicks * 100) if e_clicks > 0 else 0

        arc["company_name"] = e_name
        arc["area"] = e_area
        arc["plan_type"] = e_plan
        arc["followers"] = e_followers
        arc["metrics"] = {
            "avg_reach": e_reach, "avg_profile_access": e_pa,
            "avg_link_clicks": e_clicks, "avg_cv": e_cv,
            "avg_cv_inquiry": e_cv_inq, "avg_cv_visit": e_cv_vis,
            "profile_access_rate": pa_rate, "link_click_rate": lc_rate,
            "cv_rate": cv_rate,
            "ad_ratio": m.get("ad_ratio"),
            "trend_reach": m.get("trend_reach", "不明"),
            "trend_profile_access": m.get("trend_profile_access", "不明"),
            "trend_link_clicks": m.get("trend_link_clicks", "不明"),
            "trend_cv": m.get("trend_cv", "不明"),
        }
        arc["targets"] = edited_targets
        arc["bottleneck"] = e_bn
        arc["strategy_text"] = e_strategy

        km.save_archive(arc)

        for img in (e_images or []):
            km.save_file(img.read(), img.name, aid)
        for doc in (e_docs or []):
            km.save_file(doc.read(), doc.name, aid)

        st.session_state[f"editing_{aid}"] = False
        st.success("✅ 保存しました")
        st.rerun()


def render_cases_tab():
    """成果事例一覧タブ"""
    st.header("📋 蓄積データ一覧")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 打ち手・施策集")
        tactics = km.get_all_tactics()
        if tactics:
            for t in tactics:
                tid = t.get("id", "")
                files = km.get_files_for(tid)
                img_badge = f" 🖼️{len([f for f in files if f['file_type']=='image'])}" if any(f["file_type"] == "image" for f in files) else ""
                with st.expander(f"**{t.get('tactic_name', '不明')}** ({t.get('target_metric', '')}){img_badge}"):
                    st.write(f"**説明**: {t.get('description', '')}")
                    st.write(f"**プラン**: {', '.join(t.get('plan_type', []))}")
                    st.write(f"**カテゴリ**: {t.get('category', '')}")
                    st.write(f"**期待効果**: {t.get('expected_impact', '')}")
                    st.write(f"**出典**: {t.get('source', '')}")
                    _render_attached_files(tid, f"t_{tid}")
                    if st.button(f"削除", key=f"del_t_{tid}"):
                        km.delete_tactic(tid)
                        st.rerun()
        else:
            st.info("打ち手データがありません")

    with col2:
        st.subheader("📊 成功事例")
        cases = km.get_all_cases()
        if cases:
            for c in cases:
                cid = c.get("id", "")
                files = km.get_files_for(cid)
                img_badge = f" 🖼️{len([f for f in files if f['file_type']=='image'])}" if any(f["file_type"] == "image" for f in files) else ""
                doc_badge = f" 📄{len([f for f in files if f['file_type']=='document'])}" if any(f["file_type"] == "document" for f in files) else ""
                with st.expander(f"**{c.get('company_name', '不明')}** ({c.get('area', '')}){img_badge}{doc_badge}"):
                    st.write(f"**プラン履歴**: {c.get('plan_history', '')}")
                    st.write(f"**主要施策**: {', '.join(c.get('key_tactics', []))}")
                    st.write(f"**備考**: {c.get('notes', '')}")
                    if c.get("monthly_data"):
                        st.write("**月別データ:**")
                        for md in c["monthly_data"]:
                            st.json(md)
                    _render_attached_files(cid, f"c_{cid}")
                    if st.button(f"削除", key=f"del_c_{cid}"):
                        km.delete_case(cid)
                        st.rerun()
        else:
            st.info("事例データがありません")


def _render_attached_files(parent_id: str, key_prefix: str):
    """添付ファイル（画像・ドキュメント）を表示"""
    from pathlib import Path as _Path
    files = km.get_files_for(parent_id)
    if not files:
        return

    images = [f for f in files if f["file_type"] == "image"]
    docs = [f for f in files if f["file_type"] == "document"]

    if images:
        st.write("**📷 添付画像:**")
        img_cols = st.columns(min(len(images), 3))
        for i, img_meta in enumerate(images):
            img_path = _Path(img_meta["path"])
            if img_path.exists():
                with img_cols[i % 3]:
                    st.image(str(img_path), caption=img_meta["filename"], use_container_width=True)

    if docs:
        st.write("**📄 添付ドキュメント:**")
        for doc_meta in docs:
            doc_path = _Path(doc_meta["path"])
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                st.write(f"📎 {doc_meta['filename']} ({doc_meta['size_bytes']:,} bytes)")
                if doc_meta.get("extracted_text"):
                    with st.expander("抽出テキスト"):
                        st.text(doc_meta["extracted_text"][:500])
            with col_d2:
                if doc_path.exists():
                    st.download_button(
                        "⬇️", doc_path.read_bytes(), doc_meta["filename"],
                        key=f"dl_{key_prefix}_{doc_meta['file_id']}",
                    )


def render_past_operations_tab():
    """過去運用事例タブ"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.header("📒 過去運用事例")
    st.caption("過去に運用したアカウントの月別数値を登録し、成長率を戦略設計の参考にします")

    # --- 登録フォーム ---
    with st.expander("➕ 過去運用事例を登録"):
        with st.form("past_op_form"):
            po_name = st.text_input("会社名 / アカウント名", placeholder="例: 建装様")
            po_col1, po_col2, po_col3 = st.columns(3)
            with po_col1:
                po_area = st.text_input("エリア", placeholder="例: 山形", key="po_area")
            with po_col2:
                po_plan = st.selectbox("運用プラン", ["スタンダード", "アドバンス", "St→Ad移行", "その他"], key="po_plan")
            with po_col3:
                po_period = st.text_input("運用期間", placeholder="例: 2024年6月〜2025年3月", key="po_period")

            po_notes = st.text_area("備考・成果サマリー", placeholder="運用の概要、成果、学びを記載", key="po_notes")

            st.markdown("**月別データ（CSV/Excel or 手動入力）**")
            po_file = st.file_uploader("CSV/Excelで月別データをアップロード（任意）", type=["csv", "xlsx", "xls"], key="po_csv")

            st.markdown("手動入力の場合（カンマ区切りで月数分入力）:")
            po_months_str = st.text_input("月ラベル", placeholder="例: 2406,2407,2408,2409", key="po_months")
            po_reach_str = st.text_input("リーチ数", placeholder="例: 5000,8000,10000,12000", key="po_reach")
            po_pa_str = st.text_input("プロフアクセス数", placeholder="例: 300,500,700,900", key="po_pa")
            po_clicks_str = st.text_input("クリック数", placeholder="例: 10,15,20,25", key="po_clicks")
            po_cv_str = st.text_input("CV数", placeholder="例: 0,0,1,2", key="po_cv")

            po_images = st.file_uploader("📷 画像添付（任意）", type=["png", "jpg", "jpeg", "gif", "webp"], accept_multiple_files=True, key="po_imgs")

            if st.form_submit_button("💾 登録"):
                monthly_data = []

                if po_file:
                    # CSV/Excelから読み込み
                    import pandas as pd
                    fname = po_file.name.lower()
                    if fname.endswith((".xlsx", ".xls")):
                        df = pd.read_excel(po_file)
                    else:
                        try:
                            df = pd.read_csv(po_file, encoding="utf-8-sig")
                        except UnicodeDecodeError:
                            po_file.seek(0)
                            df = pd.read_csv(po_file, encoding="shift_jis")

                    cols = list(df.columns)
                    # 横型: 行=月
                    if "月" in cols or "month" in [c.lower() for c in cols]:
                        for _, row in df.iterrows():
                            monthly_data.append({
                                "month": _format_month_label(str(row.get("月", row.get("month", "")))),
                                "reach": int(float(row.get("リーチ数", row.get("reach", row.get("リーチ", 0))))),
                                "profile_access": int(float(row.get("プロフアクセス数", row.get("profile_access", row.get("プロフアクセス", 0))))),
                                "link_clicks": int(float(row.get("リンククリック数", row.get("link_clicks", row.get("クリック数", row.get("クリック", 0)))))),
                                "cv": int(float(row.get("CV数", row.get("cv", row.get("CV", 0))))),
                            })
                elif po_months_str.strip():
                    # 手動入力
                    months = [_format_month_label(m.strip()) for m in po_months_str.split(",")]
                    reaches = [int(x.strip()) for x in po_reach_str.split(",")] if po_reach_str.strip() else [0] * len(months)
                    pas = [int(x.strip()) for x in po_pa_str.split(",")] if po_pa_str.strip() else [0] * len(months)
                    clicks = [int(x.strip()) for x in po_clicks_str.split(",")] if po_clicks_str.strip() else [0] * len(months)
                    cvs = [int(x.strip()) for x in po_cv_str.split(",")] if po_cv_str.strip() else [0] * len(months)

                    for i, m in enumerate(months):
                        monthly_data.append({
                            "month": m,
                            "reach": reaches[i] if i < len(reaches) else 0,
                            "profile_access": pas[i] if i < len(pas) else 0,
                            "link_clicks": clicks[i] if i < len(clicks) else 0,
                            "cv": cvs[i] if i < len(cvs) else 0,
                        })

                op = {
                    "company_name": po_name,
                    "area": po_area,
                    "plan_type": po_plan,
                    "period": po_period,
                    "notes": po_notes,
                    "monthly_data": monthly_data,
                }
                oid = km.save_past_operation(op)
                for img in (po_images or []):
                    km.save_file(img.read(), img.name, oid)
                st.success(f"✅ 過去運用事例を登録しました (ID: {oid})")

    st.divider()

    # --- 成長率サマリー ---
    growth_rates = km.get_growth_rates_from_past_ops()
    if growth_rates:
        st.subheader("📈 過去運用事例から算出した月次成長率")
        st.caption("有効データのみから算出（トリム平均: 上下10%除外）。戦略設計のKPI目標に反映されます。")

        def _rate_val(key):
            r = growth_rates.get(key)
            return r * 100 if r is not None else None

        def _rate_n(key):
            return growth_rates.get(f"{key}_n", 0)

        # ファネル行: 実数の成長率
        st.markdown("#### 実数の月次成長率")
        funnel_data = [
            ("リーチ", "reach", "#a8c4e0"),
            ("プロフアクセス", "profile_access", "#6ca6d9"),
            ("クリック", "link_clicks", "#3b82c4"),
            ("CV", "cv", "#1a5276"),
        ]

        cards_html = ""
        for i, (label, key, color) in enumerate(funnel_data):
            val = _rate_val(key)
            n = _rate_n(key)
            if val is not None:
                sign = "+" if val >= 0 else ""
                val_str = f"{sign}{val:.1f}%"
                val_color = "#4ade80" if val >= 0 else "#f87171"
            else:
                val_str = "N/A"
                val_color = "#666"

            shadow = "text-shadow:0 0 8px rgba(74,222,128,0.5),0 1px 2px rgba(0,0,0,0.8);" if val_color == "#4ade80" else "text-shadow:0 0 8px rgba(248,113,113,0.5),0 1px 2px rgba(0,0,0,0.8);"
            cards_html += f"""
            <div style="flex:1;min-width:140px;background:{color};border-radius:12px;padding:20px 16px;text-align:center;border:1px solid rgba(255,255,255,0.1);">
                <div style="font-size:13px;color:rgba(255,255,255,0.8);margin-bottom:4px;font-weight:500;">{label}</div>
                <div style="font-size:28px;font-weight:bold;color:{val_color};line-height:1.2;{shadow}">{val_str}<span style="font-size:14px;color:rgba(255,255,255,0.5);">/月</span></div>
                <div style="font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px;">サンプル {n}件</div>
            </div>"""
            if i < len(funnel_data) - 1:
                cards_html += '<div style="font-size:28px;color:#555;padding:0 4px;">→</div>'

        st.markdown(f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:center;">{cards_html}</div>', unsafe_allow_html=True)

        st.markdown("")

        # 遷移率行
        st.markdown("#### 遷移率の月次変化率")
        rate_data = [
            ("プロフアクセス率", "profile_access_rate", "リーチ→プロフ"),
            ("リンククリック率", "link_click_rate", "プロフ→クリック"),
            ("反響率(CV率)", "cv_rate", "クリック→CV"),
        ]

        rate_cards_html = ""
        for label, key, desc in rate_data:
            val = _rate_val(key)
            n = _rate_n(key)
            if val is not None:
                sign = "+" if val >= 0 else ""
                val_str = f"{sign}{val:.1f}%"
                val_color = "#4ade80" if val >= 0 else "#f87171"
                bg = "#1e3a5f"
            else:
                val_str = "N/A"
                val_color = "#666"
                bg = "#2a2a2a"

            r_shadow = "text-shadow:0 0 8px rgba(74,222,128,0.5),0 1px 2px rgba(0,0,0,0.8);" if val_color == "#4ade80" else "text-shadow:0 0 8px rgba(248,113,113,0.5),0 1px 2px rgba(0,0,0,0.8);"
            rate_cards_html += f"""
            <div style="flex:1;min-width:160px;background:{bg};border:1px solid #334155;border-radius:12px;padding:18px 16px;text-align:center;">
                <div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">{desc}</div>
                <div style="font-size:13px;color:#e2e8f0;margin-bottom:6px;font-weight:500;">{label}</div>
                <div style="font-size:26px;font-weight:bold;color:{val_color};line-height:1.2;{r_shadow}">{val_str}<span style="font-size:13px;color:#64748b;">/月</span></div>
                <div style="font-size:10px;color:#64748b;margin-top:4px;">n={n}</div>
            </div>"""

        st.markdown(f'<div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">{rate_cards_html}</div>', unsafe_allow_html=True)

        st.markdown("")

        # CV発生率（特別枠）
        cv_occ = growth_rates.get("cv_occurrence_rate")
        cv_total_m = growth_rates.get("cv_months_total", 0)
        cv_pos_m = growth_rates.get("cv_months_positive", 0)
        if cv_occ is not None:
            cv_pct = cv_occ * 100
            bar_color = "#4ade80" if cv_pct >= 30 else "#fbbf24" if cv_pct >= 15 else "#f87171"
            st.markdown(f"""
            <div style="background:rgba(26,111,160,0.1);border:1px solid rgba(26,111,160,0.2);border-radius:12px;padding:16px 20px;max-width:500px;margin:0 auto;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-size:14px;color:#cbd5e1;">CV発生率（月間CVが1件以上ある月の割合）</span>
                    <span style="font-size:20px;font-weight:bold;color:{bar_color};">{cv_pct:.1f}%</span>
                </div>
                <div style="background:#334155;border-radius:6px;height:12px;overflow:hidden;">
                    <div style="background:{bar_color};height:100%;width:{min(cv_pct, 100):.0f}%;border-radius:6px;"></div>
                </div>
                <div style="font-size:11px;color:#64748b;margin-top:6px;text-align:right;">{cv_pos_m}/{cv_total_m}ヶ月でCV発生</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # データ品質
        ops_for_quality = km.get_all_past_operations()
        total = len(ops_for_quality)
        same_val_count = sum(1 for op in ops_for_quality
                            if len([m["reach"] for m in op.get("monthly_data", []) if m["reach"] > 0]) >= 3
                            and len(set(m["reach"] for m in op.get("monthly_data", []) if m["reach"] > 0)) <= 1)
        valid = total - same_val_count
        st.caption(f"データ品質: 全{total}件中 有効{valid}件 / 目標値コピー疑い{same_val_count}件（除外済み）")
        st.divider()

    # --- 一覧表示 ---
    ops = km.get_all_past_operations()
    if not ops:
        st.info("まだ過去運用事例が登録されていません。上のフォームから登録してください。")
        return

    st.subheader(f"📋 登録済み過去運用事例（{len(ops)}件）")

    for op in ops:
        oid = op.get("id", "")
        monthly = op.get("monthly_data", [])
        created = op.get("created_at", "")[:10]
        label = f"**{op.get('company_name', '不明')}** | {op.get('plan_type', '')} | {op.get('area', '')} | {op.get('period', '')} | 登録: {created}"

        with st.expander(label):
            st.write(f"**備考**: {op.get('notes', '')}")

            if monthly:
                # 月別テーブル
                st.markdown("**月別数値:**")
                table_rows = []
                for md in monthly:
                    r = md.get("reach", 0)
                    pa = md.get("profile_access", 0)
                    cl = md.get("link_clicks", 0)
                    cv = md.get("cv", 0)
                    pa_rate = (pa / r * 100) if r > 0 else 0
                    lc_rate = (cl / pa * 100) if pa > 0 else 0
                    cv_rate = (cv / cl * 100) if cl > 0 else 0
                    table_rows.append({
                        "月": _yymm_display(md.get("month", "")),
                        "リーチ": f"{r:,}",
                        "プロフアクセス": f"{pa:,}",
                        "PA率": f"{pa_rate:.2f}%",
                        "クリック": f"{cl:,}",
                        "CL率": f"{lc_rate:.2f}%",
                        "CV": cv,
                        "CV率": f"{cv_rate:.2f}%",
                    })
                st.dataframe(table_rows, use_container_width=True, hide_index=True)

                # 成長グラフ
                valid_monthly = [md for md in monthly if md.get("reach", 0) > 0]
                if len(valid_monthly) >= 2:
                    m_labels = [_yymm_display(md.get("month", "")) for md in valid_monthly]
                    fig = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=("実数推移", "遷移率推移"),
                        specs=[[{"secondary_y": False}, {"secondary_y": False}]],
                    )
                    colors = {"リーチ": "#a8c4e0", "プロフアクセス": "#6ca6d9", "クリック": "#3b82c4", "CV": "#1a5276"}
                    for name, key, color in [("リーチ", "reach", "#a8c4e0"), ("プロフアクセス", "profile_access", "#6ca6d9"),
                                              ("クリック", "link_clicks", "#3b82c4"), ("CV", "cv", "#1a5276")]:
                        fig.add_trace(go.Scatter(
                            x=m_labels, y=[md.get(key, 0) for md in valid_monthly],
                            name=name, mode="lines+markers", line=dict(color=color, width=2),
                            marker=dict(size=7),
                        ), row=1, col=1)

                    # 遷移率
                    for name, color, calc in [
                        ("プロフアクセス率", "#ff6b6b", lambda md: (md.get("profile_access", 0) / md.get("reach", 1) * 100) if md.get("reach", 0) > 0 else 0),
                        ("クリック率", "#ffa07a", lambda md: (md.get("link_clicks", 0) / md.get("profile_access", 1) * 100) if md.get("profile_access", 0) > 0 else 0),
                        ("CV率", "#98fb98", lambda md: (md.get("cv", 0) / md.get("link_clicks", 1) * 100) if md.get("link_clicks", 0) > 0 else 0),
                    ]:
                        fig.add_trace(go.Scatter(
                            x=m_labels, y=[calc(md) for md in valid_monthly],
                            name=name, mode="lines+markers", line=dict(color=color, width=2),
                            marker=dict(size=7),
                        ), row=1, col=2)

                    fig.update_xaxes(type="category", tickangle=-45 if len(m_labels) > 6 else 0)
                    fig.update_layout(height=350, legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig, use_container_width=True, key=f"po_chart_{oid}")

            # 添付ファイル
            files = km.get_files_for(oid)
            if files:
                _render_attached_files(oid, f"po_{oid}")

            if st.button("🗑️ 削除", key=f"del_po_{oid}"):
                km.delete_past_operation(oid)
                st.rerun()


if __name__ == "__main__":
    main()
