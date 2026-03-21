"""
業界ベンチマーク数値・成功事例データ定義
事例蓄積に伴い動的に更新される。初期値はフォールバックとして使用。
"""

# フォールバック用ベンチマーク基準値
FALLBACK_BENCHMARKS = {
    "プロフアクセス率": {"low": 0.5, "mid": 1.0, "high": 3.0},    # %
    "リンククリック率": {"low": 1.5, "mid": 3.0, "high": 5.0},    # %
    "反響率": {"low": 2.0, "mid": 5.0, "high": 8.0},              # %
}

# 運用プラン定義
PLAN_TYPES = {
    "スタンダード": {
        "price_monthly": 150000,
        "initial_cost": 100000,
        "follow_monthly": 100,
        "reel_monthly": 4,
        "reel_weekly": 1,
        "feed_monthly": 12,
        "feed_weekly": 3,
        "feed_design": "デザインなし（画像加工のみ）",
        "stories_weekly": 3,
        "stories_type": "交流ストーリーズ",
        "highlight": False,
        "cv_tactics": False,
    },
    "アドバンス": {
        "price_monthly": 350000,
        "initial_cost": 100000,
        "follow_monthly": 100,
        "reel_monthly": 12,
        "reel_weekly": 3,
        "feed_monthly": 12,
        "feed_weekly": 3,
        "feed_design": "フルデザイン投稿（ブランディング）",
        "stories_weekly": 3,
        "stories_type": "交流ストーリーズ",
        "highlight": True,
        "cv_tactics": True,
    },
}

# 施策の役割マトリクス（◎=高, ○=中, △=低, -=なし）
TACTIC_ROLE_MATRIX = {
    "スタンダード": {
        "フォロー施策":    {"ブランディング": "-", "ファン化": "-", "リーチ拡大": "◎", "CV創出": "○"},
        "フィード投稿":    {"ブランディング": "○", "ファン化": "○", "リーチ拡大": "◎", "CV創出": "△"},
        "リール投稿":      {"ブランディング": "◎", "ファン化": "○", "リーチ拡大": "○", "CV創出": "△"},
        "ストーリーズ投稿": {"ブランディング": "◎", "ファン化": "◎", "リーチ拡大": "△", "CV創出": "○"},
        "ハイライト":      {"ブランディング": "◎", "ファン化": "△", "リーチ拡大": "△", "CV創出": "◎"},
    },
    "アドバンス": {
        "フォロー施策":    {"ブランディング": "-", "ファン化": "-", "リーチ拡大": "◎", "CV創出": "○"},
        "フィード投稿":    {"ブランディング": "◎", "ファン化": "○", "リーチ拡大": "◎", "CV創出": "△"},
        "リール投稿":      {"ブランディング": "◎", "ファン化": "○", "リーチ拡大": "◎", "CV創出": "△"},
        "ストーリーズ投稿": {"ブランディング": "◎", "ファン化": "◎", "リーチ拡大": "△", "CV創出": "○"},
        "ハイライト":      {"ブランディング": "◎", "ファン化": "△", "リーチ拡大": "△", "CV創出": "◎"},
        "CV動線施策":      {"ブランディング": "◎", "ファン化": "○", "リーチ拡大": "△", "CV創出": "◎"},
    },
}

# LP/HP品質アラート判定基準
LP_QUALITY_ALERT = {
    "click_rate_ok_threshold": 1.5,   # リンククリック率がこれ以上ならクリックは十分
    "cv_rate_low_multiplier": 0.5,    # 反響率がベンチマークのこの倍率以下ならアラート
}

# 初期蓄積済み事例データ
INITIAL_CASES = [
    {
        "id": "case_kensou",
        "company_name": "建装様",
        "area": "山形",
        "plan_history": "St(3ヶ月) → Ad(9ヶ月)",
        "monthly_data": [
            {"month": "2025-06", "plan": "スタンダード", "cv": 0, "cv_detail": {}},
            {"month": "2025-07", "plan": "スタンダード", "cv": 0, "cv_detail": {}},
            {"month": "2025-08", "plan": "スタンダード", "cv": 0, "cv_detail": {}},
            {"month": "2025-09", "plan": "アドバンス", "cv": 0, "cv_detail": {}},
            {"month": "2025-10", "plan": "アドバンス", "cv": 0, "cv_detail": {}},
            {"month": "2025-11", "plan": "アドバンス", "cv": 1, "cv_detail": {}},
            {"month": "2025-12", "plan": "アドバンス", "cv": 2, "cv_detail": {}},
            {"month": "2026-01", "plan": "アドバンス", "cv": 1, "cv_detail": {}},
            {"month": "2026-02", "plan": "アドバンス", "cv": 2, "cv_detail": {}},
            {"month": "2026-03", "plan": "アドバンス", "cv": 2, "cv_detail": {}},
        ],
        "followers_start": 1800,
        "key_tactics": ["フォロー施策", "ストーリーズ施策", "リポスト施策"],
        "notes": "St3ヶ月でリーチ10,000安定→Ad移行後2ヶ月目から安定CV月1-2件。再現性◎",
    },
    {
        "id": "case_zerohome",
        "company_name": "ゼロホーム様",
        "area": "不明",
        "plan_history": "アドバンス",
        "monthly_data": [
            {
                "month": "直近3ヶ月平均",
                "plan": "アドバンス",
                "reach": 388941,
                "profile_access": 2455,
                "profile_access_rate": 0.63,
                "link_clicks": 39,
                "link_click_rate": 1.5,
                "cv": 3,
                "cv_rate": 7.69,
            },
        ],
        "targets": {
            "3ヶ月後": {
                "reach": 400000, "profile_access": 2636,
                "profile_access_rate": 0.659, "link_clicks": 58,
                "link_click_rate": 2.2, "cv": 5, "cv_rate": 8.5,
            },
            "6ヶ月後": {
                "reach": 426417, "profile_access": 2857,
                "profile_access_rate": 0.67, "link_clicks": 80,
                "link_click_rate": 2.5, "cv": 8, "cv_rate": 10.0,
            },
        },
        "key_tactics": [],
        "notes": "戦略設計のテンプレート事例。ファネル逆算モデルの原型。",
    },
    {
        "id": "case_rgraph",
        "company_name": "アールグラフ様",
        "area": "大阪",
        "plan_history": "アドバンス",
        "monthly_data": [
            {
                "month": "2024-09", "plan": "アドバンス",
                "reach": 198347, "link_clicks": 201,
                "link_clicks_profile": None, "link_clicks_story": None,
                "cv": 6, "cv_detail": {"資料請求": 5, "来場": 1},
                "cv_rate": 2.9,
            },
            {
                "month": "2024-10", "plan": "アドバンス",
                "reach": 240059, "link_clicks": 268,
                "link_clicks_profile": None, "link_clicks_story": None,
                "cv": 6, "cv_detail": {"資料請求": 4, "来場": 2},
                "cv_rate": 2.2,
            },
            {
                "month": "2024-11", "plan": "アドバンス",
                "reach": 212112, "link_clicks": 233,
                "link_clicks_profile": 198, "link_clicks_story": 35,
                "cv": 3, "cv_detail": {"資料請求": 2, "来場": 1},
                "cv_rate": 1.2,
            },
        ],
        "kpi_targets": {"link_clicks_monthly": 200, "link_clicks_profile": 160, "link_clicks_story": 40},
        "key_tactics": [
            "猫専門住宅コンテンツ", "保存版投稿", "見学会デザイン改善",
            "複数形式訴求（フィード+リール+ストーリーズ）", "ピン止め投稿",
        ],
        "notes": "クリック目標達成でもCV未達→LP/HP品質の課題。コンテンツ一貫性がCV率に影響。",
    },
    {
        "id": "case_alnetto",
        "company_name": "アルネット様",
        "area": "不明",
        "plan_history": "不明",
        "monthly_data": [
            {
                "month": "CV2件時", "plan": "不明",
                "reach": 182168, "reach_ad": 25920, "reach_organic": 17280,
                "reach_ad_ratio": 60.0,
                "profile_access": 2965, "profile_access_rate": 17.16,
                "link_clicks": 96, "link_click_rate": 3.24,
                "cv": 2, "cv_rate": 2.08,
            },
            {
                "month": "CV5件時", "plan": "不明",
                "reach": 455421, "reach_ad": 64800, "reach_organic": 43200,
                "reach_ad_ratio": 60.0,
                "profile_access": 7412, "profile_access_rate": 17.16,
                "link_clicks": 240, "link_click_rate": 3.24,
                "cv": 5, "cv_rate": 2.08,
            },
        ],
        "key_tactics": [],
        "notes": "プロフアクセス率17.16%は非常に高い（ブランド力指標）。広告60%/オーガニック40%。CVR2.08%安定。",
    },
]

# 初期蓄積済み打ち手データ
INITIAL_TACTICS = [
    {
        "id": "tactic_story_gift",
        "target_metric": "リンククリック率",
        "tactic_name": "ギフトカード訴求ストーリーズ",
        "description": "ギフトカード（5,000円等）のベネフィット訴求をストーリーズに盛り込み、リンククリックを促進",
        "plan_type": ["アドバンス"],
        "category": "ストーリーズ",
        "expected_impact": "高",
        "source": "建装様事例",
    },
    {
        "id": "tactic_qa_box",
        "target_metric": "リンククリック率",
        "tactic_name": "質問箱でユーザー巻き込み",
        "description": "質問箱を使ってアクティブユーザーを増やし、ストーリーズ閲覧者を増加させる",
        "plan_type": ["スタンダード", "アドバンス"],
        "category": "ストーリーズ",
        "expected_impact": "中",
        "source": "ナレッジ",
    },
    {
        "id": "tactic_cat_content",
        "target_metric": "リーチ",
        "tactic_name": "猫専門住宅コンテンツ",
        "description": "猫専門住宅の事例リールを投稿し、ストーリーズで猫LPリンクを添付。ニッチコンテンツでリーチ拡大",
        "plan_type": ["アドバンス"],
        "category": "リール",
        "expected_impact": "高",
        "source": "アールグラフ様事例",
    },
    {
        "id": "tactic_save_post",
        "target_metric": "リーチ",
        "tactic_name": "保存版投稿（狭小住宅・お客様の声）",
        "description": "保存数を稼ぐ投稿で発見タブ掲載を狙う。狭小住宅×お客様の声の組み合わせが効果的",
        "plan_type": ["スタンダード", "アドバンス"],
        "category": "フィード",
        "expected_impact": "高",
        "source": "アールグラフ様事例（保存数13件で年間最多）",
    },
    {
        "id": "tactic_design_improvement",
        "target_metric": "リンククリック率",
        "tactic_name": "広告デザイン改善（情報量削減・優先度付け）",
        "description": "見学会訴求の1枚目情報量を削減し視認性を向上。情報に優先度をつけたデザインでクリック率向上",
        "plan_type": ["アドバンス"],
        "category": "フィード",
        "expected_impact": "高",
        "source": "アールグラフ様事例（9月CV0→10月CV2）",
    },
    {
        "id": "tactic_multi_format",
        "target_metric": "反響率",
        "tactic_name": "複数形式での訴求（フィード+リール+ストーリーズ）",
        "description": "同一テーマをフィード・リール・ストーリーズの3形式で訴求し、ユーザーの接触機会を最大化",
        "plan_type": ["アドバンス"],
        "category": "総合",
        "expected_impact": "高",
        "source": "アールグラフ様事例",
    },
    {
        "id": "tactic_highlight_setup",
        "target_metric": "リンククリック率",
        "tactic_name": "ハイライト設置・整備",
        "description": "CV動線用ハイライトを設置。voice・見学会・資料請求等カテゴリ別に整備",
        "plan_type": ["アドバンス"],
        "category": "ハイライト",
        "expected_impact": "高",
        "source": "建装様事例・アールグラフ様事例",
    },
    {
        "id": "tactic_repost",
        "target_metric": "反響率",
        "tactic_name": "リポスト施策",
        "description": "過去の高パフォーマンス投稿をリポストし、新規フォロワーへ再露出させる",
        "plan_type": ["スタンダード", "アドバンス"],
        "category": "フィード",
        "expected_impact": "中",
        "source": "建装様事例（再現性のあるCV施策として活用）",
    },
    {
        "id": "tactic_pinned_post",
        "target_metric": "リンククリック率",
        "tactic_name": "ピン止め投稿3つ固定",
        "description": "プロフィール上部にピン止め投稿を3つ固定。見学会・資料請求・保存版投稿を設置",
        "plan_type": ["スタンダード", "アドバンス"],
        "category": "フィード",
        "expected_impact": "中",
        "source": "競合分析（成功アカウント共通項）",
    },
    {
        "id": "tactic_content_consistency",
        "target_metric": "反響率",
        "tactic_name": "コンテンツ一貫性の確立",
        "description": "リール・フィード・ストーリーで訴求内容と付随コンテンツを統一し、ユーザーの理解を促進",
        "plan_type": ["スタンダード", "アドバンス"],
        "category": "総合",
        "expected_impact": "高",
        "source": "アールグラフ様事例（一貫性不足→統一後CV獲得）",
    },
]
