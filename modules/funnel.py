"""
ファネル逆算計算エンジン
リーチ → プロフアクセス → リンククリック → CV の各段階を計算
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MonthlyData:
    """1ヶ月分の運用データ"""
    month: str
    reach: int = 0
    reach_ad: Optional[int] = None
    reach_organic: Optional[int] = None
    profile_access: int = 0
    link_clicks: int = 0
    link_clicks_profile: Optional[int] = None
    link_clicks_story: Optional[int] = None
    cv: int = 0
    cv_inquiry: int = 0        # 資料請求
    cv_visit: int = 0          # 来場予約

    @property
    def profile_access_rate(self) -> float:
        """プロフアクセス率(%)"""
        return (self.profile_access / self.reach * 100) if self.reach > 0 else 0.0

    @property
    def link_click_rate(self) -> float:
        """リンククリック率(%) 対プロフアクセス"""
        return (self.link_clicks / self.profile_access * 100) if self.profile_access > 0 else 0.0

    @property
    def cv_rate(self) -> float:
        """反響率(CV率)(%) 対リンククリック"""
        return (self.cv / self.link_clicks * 100) if self.link_clicks > 0 else 0.0

    @property
    def ad_ratio(self) -> Optional[float]:
        """広告リーチ比率(%)"""
        if self.reach_ad is not None and self.reach > 0:
            return self.reach_ad / self.reach * 100
        return None


@dataclass
class FunnelMetrics:
    """ファネル集計結果（3ヶ月平均ベース）"""
    avg_reach: float = 0.0
    avg_profile_access: float = 0.0
    avg_link_clicks: float = 0.0
    avg_cv: float = 0.0
    avg_cv_inquiry: float = 0.0
    avg_cv_visit: float = 0.0

    profile_access_rate: float = 0.0
    link_click_rate: float = 0.0
    cv_rate: float = 0.0

    avg_reach_ad: Optional[float] = None
    avg_reach_organic: Optional[float] = None
    ad_ratio: Optional[float] = None

    # トレンド: "上昇" / "横ばい" / "下降"
    trend_reach: str = "横ばい"
    trend_profile_access: str = "横ばい"
    trend_link_clicks: str = "横ばい"
    trend_cv: str = "横ばい"

    # アカウント固有の月次成長率（4ヶ月以上のデータがある場合に算出）
    account_growth_reach: Optional[float] = None
    account_growth_pa: Optional[float] = None
    account_growth_clicks: Optional[float] = None
    account_growth_cv: Optional[float] = None
    account_growth_pa_rate: Optional[float] = None
    account_growth_lc_rate: Optional[float] = None
    account_growth_cv_rate: Optional[float] = None
    account_growth_months: int = 0  # 成長率算出に使用した月数


@dataclass
class FunnelTargets:
    """目標KPI（逆算結果）"""
    target_cv: int = 0
    target_reach: int = 0
    target_profile_access: int = 0
    target_link_clicks: int = 0

    target_profile_access_rate: float = 0.0
    target_link_click_rate: float = 0.0
    target_cv_rate: float = 0.0

    period: str = "3ヶ月後"


def calculate_funnel_metrics(monthly_data: list[MonthlyData], baseline_months: int = 3) -> FunnelMetrics:
    """ファネル集計を算出

    Args:
        monthly_data: 古い→新しい順のデータリスト
        baseline_months: 現状値の算出に使用する直近月数（1-3）

    設計:
    - 現状値（avg_*）: 直近1-3ヶ月のみの平均（最新の状態を反映）
    - 成長率（account_growth_*）: 4ヶ月以上ある場合、全期間から算出
    - トレンド: 全期間のデータから判定
    """
    n = len(monthly_data)
    if n == 0:
        return FunnelMetrics()

    metrics = FunnelMetrics()

    # --- 現状値: 直近baseline_months月のみの平均 ---
    baseline_months = min(max(baseline_months, 1), 3)
    recent = monthly_data[-baseline_months:]  # 最新N月
    nr = len(recent)

    metrics.avg_reach = sum(d.reach for d in recent) / nr
    metrics.avg_profile_access = sum(d.profile_access for d in recent) / nr
    metrics.avg_link_clicks = sum(d.link_clicks for d in recent) / nr
    metrics.avg_cv = sum(d.cv for d in recent) / nr
    metrics.avg_cv_inquiry = sum(d.cv_inquiry for d in recent) / nr
    metrics.avg_cv_visit = sum(d.cv_visit for d in recent) / nr

    # 転換率算出（直近平均ベース）
    if metrics.avg_reach > 0:
        metrics.profile_access_rate = metrics.avg_profile_access / metrics.avg_reach * 100
    if metrics.avg_profile_access > 0:
        metrics.link_click_rate = metrics.avg_link_clicks / metrics.avg_profile_access * 100
    if metrics.avg_link_clicks > 0:
        metrics.cv_rate = metrics.avg_cv / metrics.avg_link_clicks * 100

    # 広告リーチ集計（直近のみ）
    ad_data = [d for d in recent if d.reach_ad is not None]
    if ad_data:
        metrics.avg_reach_ad = sum(d.reach_ad for d in ad_data) / len(ad_data)
        org_data = [d for d in recent if d.reach_organic is not None]
        if org_data:
            metrics.avg_reach_organic = sum(d.reach_organic for d in org_data) / len(org_data)
        if metrics.avg_reach > 0 and metrics.avg_reach_ad is not None:
            metrics.ad_ratio = metrics.avg_reach_ad / metrics.avg_reach * 100

    # --- トレンド判定: 全期間のデータから ---
    if n >= 2:
        metrics.trend_reach = _detect_trend([d.reach for d in monthly_data])
        metrics.trend_profile_access = _detect_trend([d.profile_access for d in monthly_data])
        metrics.trend_link_clicks = _detect_trend([d.link_clicks for d in monthly_data])
        metrics.trend_cv = _detect_trend([d.cv for d in monthly_data])

    # --- アカウント固有の成長率: 4ヶ月以上ある場合に算出 ---
    if n >= 4:
        growth = _calculate_account_growth(monthly_data)
        metrics.account_growth_reach = growth.get("reach")
        metrics.account_growth_pa = growth.get("profile_access")
        metrics.account_growth_clicks = growth.get("link_clicks")
        metrics.account_growth_cv = growth.get("cv")
        metrics.account_growth_pa_rate = growth.get("profile_access_rate")
        metrics.account_growth_lc_rate = growth.get("link_click_rate")
        metrics.account_growth_cv_rate = growth.get("cv_rate")
        metrics.account_growth_months = n

    return metrics


def _calculate_account_growth(monthly_data: list[MonthlyData]) -> dict:
    """アカウント固有の月次成長率を算出（トリム平均）"""
    growth = {"reach": [], "profile_access": [], "link_clicks": [], "cv": [],
              "profile_access_rate": [], "link_click_rate": [], "cv_rate": []}

    for i in range(1, len(monthly_data)):
        prev = monthly_data[i - 1]
        curr = monthly_data[i]

        # 実数の成長率
        for key, prev_val, curr_val in [
            ("reach", prev.reach, curr.reach),
            ("profile_access", prev.profile_access, curr.profile_access),
            ("link_clicks", prev.link_clicks, curr.link_clicks),
            ("cv", prev.cv, curr.cv),
        ]:
            if prev_val > 0 and curr_val >= 0:
                rate = (curr_val - prev_val) / prev_val
                if -3.0 <= rate <= 3.0:
                    growth[key].append(rate)

        # 遷移率の変化
        if prev.reach > 0 and curr.reach > 0 and prev.profile_access > 0:
            prev_rate = prev.profile_access / prev.reach
            curr_rate = curr.profile_access / curr.reach
            change = (curr_rate - prev_rate) / prev_rate
            if -3.0 <= change <= 3.0:
                growth["profile_access_rate"].append(change)

        if prev.profile_access > 0 and curr.profile_access > 0 and prev.link_clicks > 0:
            prev_rate = prev.link_clicks / prev.profile_access
            curr_rate = curr.link_clicks / curr.profile_access
            change = (curr_rate - prev_rate) / prev_rate
            if -3.0 <= change <= 3.0:
                growth["link_click_rate"].append(change)

        if prev.link_clicks > 0 and curr.link_clicks > 0 and prev.cv > 0:
            prev_rate = prev.cv / prev.link_clicks
            curr_rate = curr.cv / curr.link_clicks
            change = (curr_rate - prev_rate) / prev_rate
            if -3.0 <= change <= 3.0:
                growth["cv_rate"].append(change)

    # トリム平均
    result = {}
    for key, vals in growth.items():
        if vals:
            sorted_v = sorted(vals)
            n = len(sorted_v)
            trim = max(1, n // 10)
            trimmed = sorted_v[trim:n - trim] if n > 4 else sorted_v
            result[key] = sum(trimmed) / len(trimmed) if trimmed else sorted_v[n // 2]
    return result


def reverse_calculate_targets(
    current_metrics: FunnelMetrics,
    target_cv: int,
    period: str,
    benchmark_rates: Optional[dict] = None,
) -> FunnelTargets:
    """
    目標CV数からファネルを逆算して各指標の目標値を算出

    設計方針:
    1. 過去運用事例の月次成長率を使って「期間後にどこまで伸びるか」を算出
    2. 転換率を最大限改善した上で、必要リーチを逆算
    3. リーチ増加は過去成長率ベースで現実的な範囲に収める
    4. 目標CVが現実的に達成不可能な場合は、達成可能な最大値を設定
    """
    targets = FunnelTargets(target_cv=target_cv, period=period)
    period_months = {"3ヶ月後": 3, "6ヶ月後": 6, "12ヶ月後": 12}.get(period, 6)

    # 過去成長率を取得
    past_growth = benchmark_rates.get("_past_growth", {}) if benchmark_rates else {}

    # 各指標の月次成長率（過去事例 or デフォルト）
    # 94社実データに基づく現実的なデフォルト:
    # - リーチ: 3ヶ月中央値×1.04 → 月+1.3%相当
    # - PA:    3ヶ月中央値×1.08 だが51%が横ばい/低下 → 月+1%（控えめ）
    # - クリック: 施策次第で大きく伸びる → 月+2%
    growth_reach = past_growth.get("reach", 0.015)          # リーチ: 月+1.5%
    growth_pa = past_growth.get("profile_access", 0.01)     # PA: 月+1% （伸びづらい）
    growth_clicks = past_growth.get("link_clicks", 0.02)    # クリック: 月+2%
    growth_pa_rate = past_growth.get("profile_access_rate", 0.003)  # PA率: 月+0.3%
    growth_lc_rate = past_growth.get("link_click_rate", 0.01)       # クリック率: 月+1%
    growth_cv_rate = past_growth.get("cv_rate", 0.01)               # CV率: 月+1%

    # マイナス成長はデフォルト値に置き換え（改善を前提）
    # PAは伸びづらいため、マイナス成長の下限も抑えめ
    growth_reach = max(growth_reach, 0.005)     # 最低月+0.5%
    growth_pa = max(growth_pa, 0.003)           # 最低月+0.3%（実データ反映）
    growth_clicks = max(growth_clicks, 0.01)    # 最低月+1%
    growth_pa_rate = max(growth_pa_rate, 0.0)
    growth_lc_rate = max(growth_lc_rate, 0.0)
    growth_cv_rate = max(growth_cv_rate, 0.0)

    # 他社事例ベンチマーク（Q3値）を取得
    bm_pa_rate = benchmark_rates.get("プロフアクセス率", 10.0) if benchmark_rates else 10.0
    bm_lc_rate = benchmark_rates.get("リンククリック率", 4.0) if benchmark_rates else 4.0
    bm_cv_rate = benchmark_rates.get("反響率", 2.5) if benchmark_rates else 2.5

    # --- Step 1: 実数の成長予測（過去事例ベース）を最優先で算出 ---
    # 実数の成長 = 運用の直接的な成果（投稿数・フォロー施策・広告等）
    projected_reach = current_metrics.avg_reach * ((1 + growth_reach) ** period_months)
    projected_pa = current_metrics.avg_profile_access * ((1 + growth_pa) ** period_months)
    projected_clicks = current_metrics.avg_link_clicks * ((1 + growth_clicks) ** period_months)

    # --- Step 2: 転換率は補助的に改善（実数成長の結果として） ---
    # ベンチマーク（他社Q3）に向けて控えめに接近
    approach_ratio = {"3ヶ月後": 0.2, "6ヶ月後": 0.35, "12ヶ月後": 0.5}.get(period, 0.35)

    def _project_rate(current: float, growth: float, benchmark: float) -> float:
        if current <= 0:
            return max(benchmark * approach_ratio, 0.5)
        growth_projected = current * ((1 + growth) ** period_months)
        if benchmark <= current:
            return max(growth_projected, current)
        gap = benchmark - current
        benchmark_target = current + gap * approach_ratio
        return max(growth_projected, benchmark_target)

    projected_pa_rate = _project_rate(current_metrics.profile_access_rate, growth_pa_rate, bm_pa_rate)
    projected_lc_rate = _project_rate(current_metrics.link_click_rate, growth_lc_rate, bm_lc_rate)
    projected_cv_rate = _project_rate(current_metrics.cv_rate, growth_cv_rate, bm_cv_rate)

    # 最低保証 + ベンチマーク上限（他社Q3を超える目標は非現実的）
    projected_pa_rate = min(max(projected_pa_rate, 1.0), bm_pa_rate * 1.1)
    projected_lc_rate = min(max(projected_lc_rate, 1.0), bm_lc_rate * 1.1)
    projected_cv_rate = min(max(projected_cv_rate, 0.5), bm_cv_rate * 1.1)

    # --- Step 3: CV目標から逆算（実数成長ベース） ---
    # まず実数成長でどこまでCVが出るか計算
    projected_cv_from_growth = projected_clicks * (projected_cv_rate / 100)

    if projected_cv_from_growth >= target_cv:
        # 実数成長だけで目標達成可能 → そのまま採用
        needed_reach = projected_reach
        needed_pa = projected_pa
        needed_clicks = projected_clicks
    else:
        # 実数成長だけでは不足 → 不足分を「実数70% + 転換率30%」で分担
        # 実数ブーストは伸びやすさに応じて配分（PAは伸びづらいので控えめ）
        shortfall = target_cv / max(projected_cv_from_growth, 0.01)

        # 実数側の追加成長（70%の重み） = shortfall ^ 0.7
        volume_boost_base = shortfall ** 0.7
        # 指標別の伸びやすさ係数（実データ反映: PAは控えめ）
        volume_boost_reach = volume_boost_base ** 1.0      # 標準
        volume_boost_pa = volume_boost_base ** 0.7         # PAは70%のペースで抑制（伸びづらい）
        volume_boost_clicks = volume_boost_base ** 1.2     # クリックは1.2倍ペース（伸ばしやすい）

        # 転換率側の追加改善（30%の重み）
        rate_boost = shortfall ** 0.3

        # 実数をブースト（PAは控えめ）
        needed_reach = projected_reach * volume_boost_reach
        needed_pa = projected_pa * volume_boost_pa
        needed_clicks = projected_clicks * volume_boost_clicks

        # 転換率を控えめにブースト（ベンチマーク上限を超えない）
        max_rate_boost = {"3ヶ月後": 1.2, "6ヶ月後": 1.4, "12ヶ月後": 1.6}.get(period, 1.4)
        rate_boost = min(rate_boost, max_rate_boost)
        projected_pa_rate = min(projected_pa_rate * rate_boost, bm_pa_rate * 1.1)
        projected_lc_rate = min(projected_lc_rate * rate_boost, bm_lc_rate * 1.1)
        projected_cv_rate = min(projected_cv_rate * rate_boost, bm_cv_rate * 1.1)

        # 逆算で整合性を取る（PAが足りなければリーチで補う）
        needed_clicks = max(needed_clicks, target_cv / (projected_cv_rate / 100))
        needed_pa = max(needed_pa, needed_clicks / (projected_lc_rate / 100))
        needed_reach = max(needed_reach, needed_pa / (projected_pa_rate / 100))

    # --- Step 4: 各実数の成長上限で制限（指標ごとに異なる上限） ---
    # 94社の実データに基づく累積成長率（アカウント単位）:
    # - リーチ: 3mo Q3=×1.44, Q90=×2.28 → 伸びやすい
    # - PA:   3mo 中央値×1.08, Q3=×1.26, Q90=×1.64
    #         6mo 中央値×1.18, Q3=×1.54, Q90=×2.67
    #         ※半数以上のアカウントが横ばい or 低下 → 最も伸びづらい
    # - クリック: 3mo Q3=×2.0 → 施策次第で大きく伸びる
    #
    # 上限はQ3〜Q90の間（成功アカウントが届く水準）:
    max_growth_reach = {"3ヶ月後": 1.5, "6ヶ月後": 2.0, "12ヶ月後": 3.0}.get(period, 2.0)
    # PA実データ厳格: 3mo=Q3×1.26〜Q90×1.64、6mo=Q3×1.54〜Q90×2.67
    max_growth_pa = {"3ヶ月後": 1.3, "6ヶ月後": 1.6, "12ヶ月後": 2.2}.get(period, 1.6)
    max_growth_clicks = {"3ヶ月後": 2.0, "6ヶ月後": 3.0, "12ヶ月後": 5.0}.get(period, 3.0)

    # --- PAの絶対天井（3つの条件の最小値） ---
    # 条件1: 成長率上限（現状 × max_growth_pa）
    # 条件2: PA率上限（リーチ × PA率Q90の1.1倍）= リーチに対する率上限
    # 条件3: ハードキャップ（PA率 25%を絶対超えない = 実データ最大値32%以下）
    def _calc_pa_ceiling(reach_val):
        caps = []
        # 条件1: 成長率上限
        if current_metrics.avg_profile_access > 0:
            caps.append(current_metrics.avg_profile_access * max_growth_pa)
        # 条件2: リーチに対するPA率上限（ベンチマーク×1.1）
        caps.append(reach_val * (bm_pa_rate * 1.1 / 100))
        # 条件3: ハードキャップ（PA率25%、工務店業界の実データ最大に基づく）
        caps.append(reach_val * 0.25)
        return min(caps) if caps else float("inf")

    # 各実数に上限適用
    if current_metrics.avg_reach > 0:
        needed_reach = min(needed_reach, current_metrics.avg_reach * max_growth_reach)
    # PAは絶対天井で制限
    needed_pa = min(needed_pa, _calc_pa_ceiling(needed_reach))
    if current_metrics.avg_link_clicks > 0:
        needed_clicks = min(needed_clicks, current_metrics.avg_link_clicks * max_growth_clicks)

    # 順算で整合性チェック（上限を超えない範囲で）
    pa_from_reach = needed_reach * (projected_pa_rate / 100)
    pa_from_reach = min(pa_from_reach, _calc_pa_ceiling(needed_reach))
    needed_pa = max(needed_pa, pa_from_reach)
    # 最終PA天井を再度適用（max() で上がった分を抑える）
    needed_pa = min(needed_pa, _calc_pa_ceiling(needed_reach))

    clicks_from_pa = needed_pa * (projected_lc_rate / 100)
    if current_metrics.avg_link_clicks > 0:
        clicks_from_pa = min(clicks_from_pa, current_metrics.avg_link_clicks * max_growth_clicks)
    needed_clicks = max(needed_clicks, clicks_from_pa)

    # --- Step 5: CV数をCV率×クリック数で整合的に算出 ---
    # CV率が一定なら、クリック数が増えればCVも比例して増える
    achievable_cv = needed_clicks * (projected_cv_rate / 100)
    # 目標CVと達成可能CVの小さい方を採用（現実的な値）
    final_cv = min(target_cv, max(int(round(achievable_cv)), target_cv))
    # ただし目標CVが小さい場合はそのまま
    if target_cv <= achievable_cv:
        final_cv = target_cv
    else:
        final_cv = max(int(round(achievable_cv)), 1)

    targets.target_cv = final_cv
    targets.target_reach = max(int(needed_reach), 1)
    targets.target_profile_access = max(int(needed_pa), 1)
    targets.target_link_clicks = max(int(needed_clicks), 1)
    targets.target_profile_access_rate = round(projected_pa_rate, 2)
    targets.target_link_click_rate = round(projected_lc_rate, 2)
    targets.target_cv_rate = round(projected_cv_rate, 2)

    return targets


def calculate_improvement_needed(
    current: FunnelMetrics,
    targets: FunnelTargets,
) -> dict:
    """現状と目標のギャップ（改善必要幅）を算出"""
    gaps = {}

    def _gap(current_val, target_val, label):
        if current_val == 0:
            return {"label": label, "current": current_val, "target": target_val,
                    "gap": target_val, "gap_pct": float("inf"), "feasibility": "要検討"}
        pct = (target_val - current_val) / current_val * 100
        if pct <= 20:
            feasibility = "達成可能"
        elif pct <= 50:
            feasibility = "努力目標"
        else:
            feasibility = "要検討"
        return {"label": label, "current": round(current_val, 2), "target": round(target_val, 2),
                "gap": round(target_val - current_val, 2), "gap_pct": round(pct, 1), "feasibility": feasibility}

    gaps["リーチ数"] = _gap(current.avg_reach, targets.target_reach, "リーチ数")
    gaps["プロフアクセス数"] = _gap(current.avg_profile_access, targets.target_profile_access, "プロフアクセス数")
    gaps["プロフアクセス率"] = _gap(current.profile_access_rate, targets.target_profile_access_rate, "プロフアクセス率(%)")
    gaps["リンククリック数"] = _gap(current.avg_link_clicks, targets.target_link_clicks, "リンククリック数")
    gaps["リンククリック率"] = _gap(current.link_click_rate, targets.target_link_click_rate, "リンククリック率(%)")
    gaps["CV数"] = _gap(current.avg_cv, targets.target_cv, "CV数")
    gaps["反響率"] = _gap(current.cv_rate, targets.target_cv_rate, "反響率(%)")

    return gaps


def _detect_trend(values: list) -> str:
    """数値リストからトレンドを判定"""
    if len(values) < 2:
        return "横ばい"
    first_half = sum(values[:len(values)//2]) / max(len(values)//2, 1)
    second_half = sum(values[len(values)//2:]) / max(len(values) - len(values)//2, 1)
    if first_half == 0:
        return "横ばい"
    change_rate = (second_half - first_half) / first_half
    if change_rate > 0.1:
        return "上昇"
    elif change_rate < -0.1:
        return "下降"
    return "横ばい"
