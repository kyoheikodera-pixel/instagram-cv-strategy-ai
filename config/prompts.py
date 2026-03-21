"""
Gemini AIプロンプトテンプレート
工務店Instagram CV戦略設計に特化
"""

STRATEGY_PROMPT = """あなたは工務店専門のInstagramマーケティング戦略コンサルタントです。
以下のクライアント情報とファネル分析結果に基づいて、具体的な打ち手を提案してください。

## クライアント情報
- 会社名: {company_name}
- エリア: {area}
- 運用プラン: {plan_type}
- フォロワー数: {followers:,}

## 現状ファネル数値（直近3ヶ月平均）
- リーチ数: {avg_reach:,.0f}
- プロフアクセス数: {avg_profile_access:,.0f} ({profile_access_rate:.2f}%)
- リンククリック数: {avg_link_clicks:,.0f} ({link_click_rate:.2f}%)
- CV数: {avg_cv:.1f} ({cv_rate:.2f}%)
  - 資料請求: {avg_cv_inquiry:.1f}件 / 来場予約: {avg_cv_visit:.1f}件
{ad_ratio_info}

## ボトルネック分析結果
- 最大のボトルネック: {primary_bottleneck}
- 課題ランキング:
{bottleneck_ranking}

## 課題の詳細
{issues_detail}

{lp_alert_info}
{ad_alert_info}

## 目標KPI（{period}）
- CV目標: {target_cv}件/月
- 必要リーチ: {target_reach:,}
- 必要プロフアクセス: {target_profile_access:,} ({target_pa_rate:.2f}%)
- 必要リンククリック: {target_link_clicks:,} ({target_lc_rate:.2f}%)
- 必要反響率: {target_cv_rate:.2f}%

## 蓄積済みの成功事例・打ち手ナレッジ
{knowledge_context}

## 指示
上記を踏まえ、以下の形式で回答してください:

### 1. 課題の深堀り
ボトルネックとなっている指標について、なぜその数値が低いのか根本原因を3つ挙げてください。

### 2. 打ち手提案（優先度順に3〜5つ）
各打ち手について以下を記載:
- **施策名**: 具体的な施策名
- **対象指標**: どの指標を改善するか
- **具体的アクション**: 何をどうやるか
- **期待効果**: どの程度の改善が見込めるか
- **実行可能性**: {plan_type}プランで実行可能か
- **参考事例**: ナレッジに該当事例があれば引用

### 3. 実行スケジュール案
{period}の期間で、どの順番で施策を実行すべきか月次で提案してください。

### 4. 注意事項
目標達成に向けてリスクや注意すべきポイントがあれば記載してください。
"""


def build_strategy_prompt(
    company_name: str,
    area: str,
    plan_type: str,
    followers: int,
    metrics,
    bottleneck_result,
    targets,
    gaps: dict,
    knowledge_context: str = "",
) -> str:
    """戦略提案プロンプトを構築"""

    # ボトルネックランキング
    ranking_text = ""
    for i, item in enumerate(bottleneck_result.bottleneck_ranking, 1):
        ranking_text += f"  {i}. {item['metric']}: 現状{item['current']:.2f}% → 目標{item['target']:.2f}% (改善必要: +{item['gap_pct']:.1f}%) [{item['feasibility']}]\n"

    # 課題詳細
    issues_text = ""
    for issue in bottleneck_result.issues:
        primary_mark = "★" if issue.get("is_primary") else ""
        issues_text += f"\n{primary_mark}【{issue['level1']}】{issue['level1_detail']}\n"
        for l2 in issue["level2"]:
            issues_text += f"  - {l2['cause']}\n"
            for sc in l2["sub_causes"]:
                issues_text += f"    - {sc}\n"

    # LPアラート
    lp_info = ""
    if bottleneck_result.lp_quality_alert:
        lp_info = f"\n⚠️ LP/HP品質アラート:\n{bottleneck_result.lp_alert_message}\n"

    # 広告アラート
    ad_alert_info = ""
    if bottleneck_result.ad_ratio_alert:
        ad_alert_info = f"\n⚠️ 広告リーチ比率アラート:\n{bottleneck_result.ad_alert_message}\n"

    # 広告比率情報
    ad_ratio_info = ""
    if metrics.ad_ratio is not None:
        ad_ratio_info = f"- 広告リーチ比率: {metrics.ad_ratio:.1f}% (広告: {metrics.avg_reach_ad:,.0f} / オーガニック: {metrics.avg_reach_organic:,.0f})"

    return STRATEGY_PROMPT.format(
        company_name=company_name,
        area=area,
        plan_type=plan_type,
        followers=followers,
        avg_reach=metrics.avg_reach,
        avg_profile_access=metrics.avg_profile_access,
        profile_access_rate=metrics.profile_access_rate,
        avg_link_clicks=metrics.avg_link_clicks,
        link_click_rate=metrics.link_click_rate,
        avg_cv=metrics.avg_cv,
        cv_rate=metrics.cv_rate,
        avg_cv_inquiry=metrics.avg_cv_inquiry,
        avg_cv_visit=metrics.avg_cv_visit,
        ad_ratio_info=ad_ratio_info,
        primary_bottleneck=bottleneck_result.primary_bottleneck,
        bottleneck_ranking=ranking_text,
        issues_detail=issues_text,
        lp_alert_info=lp_info,
        ad_alert_info=ad_alert_info,
        period=targets.period,
        target_cv=targets.target_cv,
        target_reach=targets.target_reach,
        target_profile_access=targets.target_profile_access,
        target_pa_rate=targets.target_profile_access_rate,
        target_link_clicks=targets.target_link_clicks,
        target_lc_rate=targets.target_link_click_rate,
        target_cv_rate=targets.target_cv_rate,
        knowledge_context=knowledge_context if knowledge_context else "（まだ蓄積データなし）",
    )
