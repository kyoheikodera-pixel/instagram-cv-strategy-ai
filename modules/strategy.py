"""
AI打ち手提案モジュール
ナレッジ・成功事例ドリブンで提案し、不足分をGemini AIで補完
"""
from modules.gemini_client import generate
from config.prompts import build_strategy_prompt
from modules.funnel import FunnelMetrics, FunnelTargets
from modules.analyzer import BottleneckResult
from modules.knowledge_manager import KnowledgeManager


def generate_strategy(
    company_name: str,
    area: str,
    plan_type: str,
    followers: int,
    metrics: FunnelMetrics,
    bottleneck_result: BottleneckResult,
    targets: FunnelTargets,
    gaps: dict,
    knowledge_mgr: KnowledgeManager,
) -> str:
    """戦略提案を生成（ナレッジ参照 + AI補完）"""

    # ナレッジからコンテキストを構築
    knowledge_context = _build_knowledge_context(
        bottleneck_result, plan_type, knowledge_mgr
    )

    # プロンプト構築
    prompt = build_strategy_prompt(
        company_name=company_name,
        area=area,
        plan_type=plan_type,
        followers=followers,
        metrics=metrics,
        bottleneck_result=bottleneck_result,
        targets=targets,
        gaps=gaps,
        knowledge_context=knowledge_context,
    )

    # Gemini AIで生成
    result = generate(prompt, temperature=0.5)
    return result


def _build_knowledge_context(
    bottleneck: BottleneckResult,
    plan_type: str,
    km: KnowledgeManager,
) -> str:
    """ナレッジDBから関連する事例・打ち手を検索してコンテキストを構築"""
    lines = []

    # ボトルネック指標に関連する打ち手を検索
    primary_metric = bottleneck.primary_bottleneck
    tactics = km.search_tactics(target_metric=primary_metric, plan_type=plan_type)
    if tactics:
        lines.append(f"### {primary_metric}改善に実績のある施策:")
        for t in tactics:
            lines.append(f"- **{t['tactic_name']}**: {t['description']} (効果: {t['expected_impact']}, 出典: {t['source']})")

    # 全ボトルネック指標の打ち手も追加
    for item in bottleneck.bottleneck_ranking:
        metric = item["metric"]
        if metric == primary_metric:
            continue
        other_tactics = km.search_tactics(target_metric=metric, plan_type=plan_type)
        if other_tactics:
            lines.append(f"\n### {metric}改善に実績のある施策:")
            for t in other_tactics[:3]:
                lines.append(f"- **{t['tactic_name']}**: {t['description']} (出典: {t['source']})")

    # 類似事例を検索
    cases = km.get_all_cases()
    if cases:
        lines.append("\n### 参考事例:")
        for c in cases:
            notes = c.get("notes", "")
            lines.append(f"- **{c['company_name']}** ({c.get('area', '不明')}): {notes}")

    return "\n".join(lines) if lines else ""


def get_benchmark_rates_from_cases(km: KnowledgeManager, plan_type: str) -> dict:
    """成果事例 + 過去運用事例の両方からベンチマーク転換率を算出

    算出ロジック:
    1. 成果事例(cases) + 過去運用事例(past_operations)の全データを統合
    2. 過去運用事例は月別の実数からPA率・クリック率・CV率を計算
    3. IQR法で外れ値を除外
    4. 外れ値除外後のQ3（上位25%値）を目標ベンチマークとして採用
       → 中央値だと「平均的」すぎる。Q3=「成功アカウントの水準」
    """
    rates = {"プロフアクセス率": [], "リンククリック率": [], "反響率": []}

    # 成果事例(cases)から
    cases = km.get_all_cases()
    for case in cases:
        for md in case.get("monthly_data", []):
            if md.get("profile_access_rate") and md.get("profile_access_rate") > 0:
                rates["プロフアクセス率"].append(md["profile_access_rate"])
            if md.get("link_click_rate") and md.get("link_click_rate") > 0:
                rates["リンククリック率"].append(md["link_click_rate"])
            if md.get("cv_rate") and md.get("cv", 0) > 0:
                rates["反響率"].append(md["cv_rate"])

    # 過去運用事例(past_operations)から計算
    # 同一値パターン（目標コピー）のアカウントは除外
    ops = km.get_all_past_operations()
    for op in ops:
        monthly = op.get("monthly_data", [])
        if len(monthly) < 2:
            continue

        # 各指標で全月同じ値なら目標コピーとみなしスキップ
        skip_keys = set()
        for key in ["reach", "profile_access", "link_clicks", "cv"]:
            values = [m.get(key, 0) for m in monthly if m.get(key, 0) > 0]
            if len(values) >= 3 and len(set(values)) <= 1:
                skip_keys.add(key)

        for md in monthly:
            reach = md.get("reach", 0)
            pa = md.get("profile_access", 0)
            clicks = md.get("link_clicks", 0)
            cv = md.get("cv", 0)

            if reach > 0 and pa > 0 and "reach" not in skip_keys and "profile_access" not in skip_keys:
                rates["プロフアクセス率"].append(pa / reach * 100)
            if pa > 0 and clicks > 0 and "profile_access" not in skip_keys and "link_clicks" not in skip_keys:
                rates["リンククリック率"].append(clicks / pa * 100)
            if clicks > 0 and cv > 0 and "link_clicks" not in skip_keys and "cv" not in skip_keys:
                rates["反響率"].append(cv / clicks * 100)

    result = {}
    for key, vals in rates.items():
        if not vals:
            continue
        filtered = _remove_outliers(vals)
        if not filtered:
            filtered = vals

        sorted_vals = sorted(filtered)
        n = len(sorted_vals)
        # Q3（上位25%値）を採用 = 成功アカウントの水準
        q3_idx = min(n * 3 // 4, n - 1)
        result[key] = sorted_vals[q3_idx]
        # データ数も付与
        result[f"{key}_n"] = n

    return result


def _remove_outliers(values: list) -> list:
    """IQR法で外れ値を除外"""
    if len(values) < 4:
        # データが少ない場合は最大値と最小値を除外（簡易）
        if len(values) <= 2:
            return values
        sorted_v = sorted(values)
        return sorted_v[:-1]  # 最大値のみ除外

    sorted_v = sorted(values)
    q1_idx = len(sorted_v) // 4
    q3_idx = (len(sorted_v) * 3) // 4
    q1 = sorted_v[q1_idx]
    q3 = sorted_v[q3_idx]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [v for v in sorted_v if lower <= v <= upper]
