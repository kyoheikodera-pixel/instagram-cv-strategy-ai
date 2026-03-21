"""
過去運用事例の一括取り込みスクリプト v2
- 目標行と実績行を区別（実績=「本数」セクション以降の実データ行を優先）
- CV件数 > CV数 の優先順位
- 異常値検出・エラーゾーン分離
- 重複データ検出
"""
import sys
import os
import re
import glob
import json
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from modules.knowledge_manager import KnowledgeManager

ERROR_DIR = Path(__file__).parent / "data" / "knowledge_store" / "past_operations_errors"
ERROR_DIR.mkdir(parents=True, exist_ok=True)


def extract_company_name(filename: str) -> str:
    m = re.search(r"\u3010(.+?)\u3011", filename)
    if m:
        return m.group(1)
    return os.path.splitext(os.path.basename(filename))[0]


def parse_kpi_excel(filepath: str) -> tuple:
    """KPIシートExcelを解析。(data_dict, errors_list) を返す"""
    errors = []
    try:
        xls = pd.ExcelFile(filepath)
        df = pd.read_excel(filepath, sheet_name=xls.sheet_names[0])
    except Exception as e:
        return None, [f"読み込みエラー: {e}"]

    cols = list(df.columns)
    if len(cols) < 4:
        return None, [f"列が少なすぎます: {len(cols)}列"]

    # 月データ列を特定
    month_cols = []
    for c in cols:
        try:
            val = int(c)
            if 2300 <= val <= 2700:
                month_cols.append(c)
        except (ValueError, TypeError):
            pass

    if not month_cols:
        return None, ["月データ列(yymm形式)が見つかりません"]

    # カテゴリ列・指標列を特定
    text_cols = [c for c in cols if c not in month_cols and "unnamed" not in str(c).lower()]
    if len(text_cols) >= 2:
        cat_col, met_col = text_cols[0], text_cols[1]
    elif len(text_cols) == 1:
        cat_col = met_col = text_cols[0]
    else:
        return None, ["カテゴリ/指標列を特定できません"]

    def safe_num(val, default=0.0):
        try:
            if pd.isna(val):
                return default
            s = str(val).replace(",", "").replace("%", "").strip()
            if s in ("", "-", "\u2015", "\uff0d"):
                return default
            return float(s)
        except (ValueError, TypeError):
            return default

    def get_all_rows():
        """全行のカテゴリ・指標をリスト化"""
        rows = []
        for idx, row in df.iterrows():
            cat = str(row.get(cat_col, "")).strip() if pd.notna(row.get(cat_col)) else ""
            met = str(row.get(met_col, "")).strip() if pd.notna(row.get(met_col)) else ""
            rows.append({"idx": idx, "cat": cat, "met": met, "row": row})
        return rows

    all_rows = get_all_rows()

    # 目標セクション = row 0~5付近（「目標」「(後伸び含む)」がカテゴリにある行）
    # 実績セクション = 「本数」以降
    # 実績の主要指標は「プロフ」「リンククリック」「CV数」がカテゴリ列にある行
    target_rows = set()
    actual_start = 0
    for r in all_rows:
        combined = r["cat"] + r["met"]
        if "目標" in r["cat"] or "(後伸び" in r["cat"] or "（後伸び" in r["cat"]:
            target_rows.add(r["idx"])
        if "本数" in combined or "フォロワー" in combined:
            actual_start = r["idx"]
            break

    # 目標セクションより前の行で、カテゴリが空の行も目標とみなす
    for r in all_rows:
        if r["idx"] < actual_start:
            target_rows.add(r["idx"])

    def find_value_strict(cat_kw, met_kw, month_col) -> float:
        """カテゴリ×指標で検索。実績行（目標セクション外）のみ対象"""
        candidates = []
        ck = cat_kw.rstrip("\u6570\u4ef6\u7387")
        mk = met_kw.rstrip("\u6570\u4ef6\u7387")

        for r in all_rows:
            if r["idx"] in target_rows:
                continue  # 目標行は無視

            cat = r["cat"]
            met = r["met"]
            cat_base = cat.rstrip("\u6570\u4ef6\u7387")
            met_base = met.rstrip("\u6570\u4ef6\u7387")

            match = False
            # パターン1: カテゴリ=cat_kw, 指標=met_kw
            if (cat_base == ck or ck in cat_base or cat_kw in cat) and \
               (met_base == mk or mk in met_base or met_kw in met):
                match = True
            # パターン2: カテゴリ空、指標にmet_kwが含まれる（前のカテゴリを継承）
            # → ここでは使わない（曖昧すぎる）

            if match:
                val = safe_num(r["row"].get(month_col, 0))
                candidates.append({"val": val, "idx": r["idx"], "cat": cat, "met": met})

        if candidates:
            return candidates[0]["val"]
        return 0.0

    def find_flex(searches, month_col):
        for cat, met in searches:
            v = find_value_strict(cat, met, month_col)
            if v > 0:
                return v
        return 0.0

    # 月別データを抽出
    monthly_data = []
    for mc in month_cols:
        reach = find_flex([
            ("\u30ea\u30fc\u30c1", "\u5408\u8a08"), ("\u30ea\u30fc\u30c1", "\u30ea\u30fc\u30c1"),
        ], mc)
        pa = find_flex([
            ("\u30d7\u30ed\u30d5", "\u30d7\u30ed\u30d5\u30a2\u30af\u30bb\u30b9"),
        ], mc)
        # CV件数を優先（実績セクション内のCV数行）
        cv = find_flex([
            ("CV\u6570", "CV\u4ef6\u6570"), ("CV", "CV\u4ef6"), ("CV\u6570", "CV"),
        ], mc)

        clicks = find_flex([
            ("\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af", "\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af"),
            ("\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af", "\u5408\u8a08"),
        ], mc)
        clicks_prof = find_flex([("\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af", "\u30d7\u30ed\u30d5")], mc)
        clicks_story = find_flex([
            ("\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af", "\u30b9\u30c8\u30fc\u30ea\u30fc\u30ba"),
            ("\u30ea\u30f3\u30af\u30af\u30ea\u30c3\u30af", "\u30cf\u30a4\u30e9\u30a4\u30c8"),
        ], mc)
        followers = find_flex([
            ("\u30d5\u30a9\u30ed\u30ef\u30fc", "\u5408\u8a08"), ("\u30d5\u30a9\u30ed\u30ef\u30fc", "\u30d5\u30a9\u30ed\u30ef\u30fc"),
        ], mc)

        if clicks == 0 and (clicks_prof > 0 or clicks_story > 0):
            clicks = clicks_prof + clicks_story

        monthly_data.append({
            "month": str(mc),
            "reach": int(reach),
            "profile_access": int(pa),
            "link_clicks": int(clicks),
            "link_clicks_profile": int(clicks_prof) if clicks_prof > 0 else None,
            "link_clicks_story": int(clicks_story) if clicks_story > 0 else None,
            "cv": int(cv),
            "followers": int(followers),
        })

    # 空月を除外
    monthly_data = [md for md in monthly_data
                    if md["reach"] > 0 or md["profile_access"] > 0
                    or md["link_clicks"] > 0 or md["cv"] > 0]

    if not monthly_data:
        return None, ["有効な数値データが見つかりません"]

    # === 異常値検出 ===
    data_errors = []

    for md in monthly_data:
        m = md["month"]
        # CV > 100は異常（月間100件以上のCVは工務店では非現実的）
        if md["cv"] > 100:
            data_errors.append(f"[{m}] CV={md['cv']}件は異常値（月100件超）。目標値を実績として取得した可能性")
            md["cv"] = 0  # リセット

        # リーチ > 1,000,000 は異常
        if md["reach"] > 1000000:
            data_errors.append(f"[{m}] リーチ={md['reach']:,}は異常値（100万超）")

        # プロフアクセス > リーチ
        if md["reach"] > 0 and md["profile_access"] > md["reach"]:
            data_errors.append(f"[{m}] プロフアクセス({md['profile_access']:,}) > リーチ({md['reach']:,})")

        # クリック > プロフアクセス
        if md["profile_access"] > 0 and md["link_clicks"] > md["profile_access"]:
            data_errors.append(f"[{m}] クリック({md['link_clicks']:,}) > プロフアクセス({md['profile_access']:,})")

    # 同じ値の繰り返し検出（目標値をコピーした可能性）
    for key in ["reach", "profile_access", "link_clicks", "cv"]:
        values = [md[key] for md in monthly_data if md[key] > 0]
        if len(values) >= 3:
            # 全て同じ値
            if len(set(values)) == 1:
                data_errors.append(f"{key}が全月同じ値({values[0]})。目標値をコピーした可能性")
            # 80%以上が同じ値
            from collections import Counter
            most_common_val, most_common_count = Counter(values).most_common(1)[0]
            if most_common_count >= len(values) * 0.8 and len(values) >= 4:
                data_errors.append(f"{key}の{most_common_count}/{len(values)}月が同じ値({most_common_val})。データの正確性を確認")

    company = extract_company_name(filepath)
    period_months = [str(md["month"]) for md in monthly_data]
    period_str = f"{period_months[0]}~{period_months[-1]}" if period_months else ""

    result = {
        "company_name": company,
        "area": "",
        "plan_type": "不明",
        "period": period_str,
        "notes": f"KPIシートから自動取り込み。{len(monthly_data)}ヶ月分。",
        "monthly_data": monthly_data,
        "source_file": os.path.basename(filepath),
        "import_errors": data_errors,
    }

    return result, data_errors


def main():
    folder = r"C:\Users\koder\Documents\shosan\AI\Instagram_KPIシート-20260321T055909Z-3-001\Instagram_KPIシート"
    files = glob.glob(os.path.join(folder, "*.xlsx"))
    print(f"[FOLDER] {len(files)} Excel files found\n")

    km = KnowledgeManager()

    # 既存データを全削除して再取り込み
    existing_ops = km.get_all_past_operations()
    for op in existing_ops:
        km.delete_past_operation(op["id"])
    print(f"Cleared {len(existing_ops)} existing records\n")

    success = 0
    error_count = 0
    skip_count = 0
    error_records = []

    for f in sorted(files):
        company = extract_company_name(f)
        basename = os.path.basename(f)

        # 管理表系はスキップ
        if "管理表" in basename or "更新必須" in basename:
            print(f"[SKIP] {company} (management file)")
            skip_count += 1
            continue

        result, data_errors = parse_kpi_excel(f)

        if result is None:
            print(f"[FAIL] {company}: {', '.join(data_errors)}")
            error_records.append({"company": company, "file": basename, "errors": data_errors, "type": "parse_error"})
            error_count += 1
            continue

        if data_errors:
            # エラーはあるがデータはある → エラーゾーン + 正常登録の両方
            print(f"[WARN] {company}: {len(data_errors)} issues found")
            for e in data_errors:
                print(f"       - {e}")
            error_records.append({"company": company, "file": basename, "errors": data_errors,
                                  "type": "data_warning", "data": result})

        oid = km.save_past_operation(result)
        months_count = len(result["monthly_data"])
        total_cv = sum(md.get("cv", 0) for md in result["monthly_data"])
        status = "[OK]  " if not data_errors else "[WARN]"
        print(f"{status} {company}: {months_count}mo, CV={total_cv}, ID={oid}")
        success += 1

    # エラーゾーンに記録を保存
    if error_records:
        error_path = ERROR_DIR / "import_errors.json"
        error_path.write_text(json.dumps(error_records, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"OK:    {success}")
    print(f"WARN:  {len([e for e in error_records if e['type'] == 'data_warning'])}")
    print(f"FAIL:  {error_count}")
    print(f"SKIP:  {skip_count}")
    print(f"TOTAL: {success + error_count + skip_count}")
    if error_records:
        print(f"\nError details saved to: {ERROR_DIR / 'import_errors.json'}")


if __name__ == "__main__":
    main()
