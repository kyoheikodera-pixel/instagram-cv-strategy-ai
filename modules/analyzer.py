"""
ボトルネック分析・LP品質アラート・課題特定モジュール
"""
from dataclasses import dataclass
from modules.funnel import FunnelMetrics, FunnelTargets


@dataclass
class BottleneckResult:
    """ボトルネック分析結果"""
    primary_bottleneck: str           # 最大のボトルネック指標
    bottleneck_ranking: list          # ボトルネック優先順位リスト
    lp_quality_alert: bool            # LP/HP品質アラートフラグ
    lp_alert_message: str             # アラートメッセージ
    ad_ratio_alert: bool              # 広告比率アラートフラグ
    ad_alert_message: str             # 広告アラートメッセージ
    feasibility_score: str            # 達成可能性 ("達成可能"/"努力目標"/"要検討")
    issues: list                      # 課題リスト（第1階層・第2階層）


def analyze_bottleneck(
    current: FunnelMetrics,
    gaps: dict,
    benchmarks: dict,
) -> BottleneckResult:
    """ファネルのボトルネックを特定し、課題を階層分析する"""

    # 各指標のギャップを改善必要度でランキング
    # 実数と遷移率の両方を評価し、実数を重視（重み: 実数70%, 遷移率30%）
    all_metrics = [
        ("リーチ数", 0.7),
        ("プロフアクセス数", 0.7),
        ("リンククリック数", 0.7),
        ("CV数", 0.7),
        ("プロフアクセス率", 0.3),
        ("リンククリック率", 0.3),
        ("反響率", 0.3),
    ]
    ranking = []
    for metric, weight in all_metrics:
        if metric in gaps:
            gap_info = gaps[metric]
            gap_pct = gap_info["gap_pct"] if gap_info["gap_pct"] != float("inf") else 999
            weighted_score = gap_pct * weight
            ranking.append({
                "metric": metric,
                "current": gap_info["current"],
                "target": gap_info["target"],
                "gap_pct": gap_pct,
                "weighted_score": weighted_score,
                "feasibility": gap_info["feasibility"],
                "type": "実数" if weight == 0.7 else "遷移率",
            })

    ranking.sort(key=lambda x: x["weighted_score"], reverse=True)
    # ボトルネックは加重スコア最大の指標
    primary = ranking[0]["metric"] if ranking else "不明"

    # LP/HP品質アラート判定
    lp_alert = False
    lp_message = ""
    click_rate_benchmark = benchmarks.get("リンククリック率", {}).get("mid", 3.0)
    cv_rate_benchmark = benchmarks.get("反響率", {}).get("mid", 5.0)

    if current.link_click_rate >= click_rate_benchmark and current.cv_rate < cv_rate_benchmark * 0.5:
        lp_alert = True
        lp_message = (
            f"リンククリック率 {current.link_click_rate:.2f}% はベンチマーク({click_rate_benchmark}%)以上ですが、"
            f"反響率 {current.cv_rate:.2f}% が低い状態です。\n"
            "Instagram側の施策は機能しています。遷移先（LP/HP）の品質に課題がある可能性があります。\n"
            "改善ポイント: ファーストビューの訴求力、CTAボタンの配置・文言、フォーム入力の簡易化、"
            "ページ表示速度、モバイル最適化"
        )

    # 広告比率アラート
    ad_alert = False
    ad_message = ""
    if current.ad_ratio is not None:
        if current.ad_ratio < 30:
            ad_alert = True
            ad_message = (
                f"広告リーチ比率 {current.ad_ratio:.1f}% が低い状態です。\n"
                "オーガニックリーチ中心のため、ターゲット外のユーザーにリーチしている可能性があります。\n"
                "広告予算の増額でターゲット精度の高いリーチを増やすことを検討してください。"
            )

    # 達成可能性の総合評価
    feasibility_counts = {"達成可能": 0, "努力目標": 0, "要検討": 0}
    for g in gaps.values():
        f = g.get("feasibility", "達成可能")
        if f in feasibility_counts:
            feasibility_counts[f] += 1

    if feasibility_counts["要検討"] >= 2:
        overall_feasibility = "要検討"
    elif feasibility_counts["努力目標"] >= 2:
        overall_feasibility = "努力目標"
    else:
        overall_feasibility = "達成可能"

    # 課題の階層分析
    issues = _generate_issues(current, gaps, primary)

    return BottleneckResult(
        primary_bottleneck=primary,
        bottleneck_ranking=ranking,
        lp_quality_alert=lp_alert,
        lp_alert_message=lp_message,
        ad_ratio_alert=ad_alert,
        ad_alert_message=ad_message,
        feasibility_score=overall_feasibility,
        issues=issues,
    )


def _generate_issues(current: FunnelMetrics, gaps: dict, primary_bottleneck: str) -> list:
    """課題を第1階層・第2階層で生成"""
    issues = []

    # リーチの課題
    reach_gap = gaps.get("リーチ数", {})
    if reach_gap.get("gap_pct", 0) > 10:
        issue = {
            "level1": "リーチ数不足",
            "level1_detail": f"現状 {reach_gap.get('current', 0):,.0f} → 目標 {reach_gap.get('target', 0):,.0f} (改善必要: +{reach_gap.get('gap_pct', 0):.1f}%)",
            "level2": [
                {"cause": "リール再生数が低い", "sub_causes": ["素材の質", "冒頭のフック不足", "再生時間が短い"]},
                {"cause": "フィード投稿のリーチが低い", "sub_causes": ["ハッシュタグ戦略の見直し", "保存数が少ない", "発見タブ未掲載"]},
                {"cause": "フォロー施策の効果不足", "sub_causes": ["ターゲットエリア外のフォロー", "フォロー数が少ない"]},
            ],
            "is_primary": primary_bottleneck == "プロフアクセス率",
        }
        issues.append(issue)

    # プロフアクセス率の課題
    pa_gap = gaps.get("プロフアクセス率", {})
    if pa_gap.get("gap_pct", 0) > 10:
        issue = {
            "level1": "プロフアクセス率が低い",
            "level1_detail": f"現状 {pa_gap.get('current', 0):.2f}% → 目標 {pa_gap.get('target', 0):.2f}%",
            "level2": [
                {"cause": "投稿からプロフへの誘導が弱い", "sub_causes": ["キャプション文言の誘導不足", "アカウント名の認知度不足"]},
                {"cause": "フィードの統一感不足", "sub_causes": ["デザインテーマの不統一", "投稿内容のブランディング不足"]},
                {"cause": "リールの最終画面でプロフ誘導がない", "sub_causes": ["CTA不足", "プロフリンクの案内なし"]},
            ],
            "is_primary": primary_bottleneck == "プロフアクセス率",
        }
        issues.append(issue)

    # リンククリック率の課題
    lc_gap = gaps.get("リンククリック率", {})
    if lc_gap.get("gap_pct", 0) > 10:
        issue = {
            "level1": "リンククリック率が低い",
            "level1_detail": f"現状 {lc_gap.get('current', 0):.2f}% → 目標 {lc_gap.get('target', 0):.2f}%",
            "level2": [
                {"cause": "ハイライトが未設置/不十分", "sub_causes": ["CV導線ハイライトがない", "ハイライトの内容が古い"]},
                {"cause": "ストーリーズの誘導が弱い", "sub_causes": ["誘導先がバラバラ", "GIF等の活用不足", "訴求文言が弱い"]},
                {"cause": "プロフィールの誘導が弱い", "sub_causes": ["リンク数が多すぎる", "キャプション文言での誘導不足"]},
                {"cause": "クリックするベネフィットが弱い", "sub_causes": ["特典訴求がない", "限定感の演出不足"]},
            ],
            "is_primary": primary_bottleneck == "リンククリック率",
        }
        issues.append(issue)

    # 反響率の課題
    cv_gap = gaps.get("反響率", {})
    if cv_gap.get("gap_pct", 0) > 10:
        issue = {
            "level1": "反響率(CV率)が低い",
            "level1_detail": f"現状 {cv_gap.get('current', 0):.2f}% → 目標 {cv_gap.get('target', 0):.2f}%",
            "level2": [
                {"cause": "LP/HPの品質課題", "sub_causes": ["ファーストビューの訴求力不足", "CTAが見つけにくい", "フォーム入力が煩雑"]},
                {"cause": "ユーザーの動線が分散", "sub_causes": ["複数の遷移先がありユーザーが迷う", "インスタ→別経路でCV（偶発的）"]},
                {"cause": "コンテンツと遷移先の一貫性不足", "sub_causes": ["投稿内容とLP訴求のミスマッチ", "期待値と実際の乖離"]},
            ],
            "is_primary": primary_bottleneck == "反響率",
        }
        issues.append(issue)

    return issues
