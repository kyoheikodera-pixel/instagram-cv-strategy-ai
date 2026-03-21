"""
ナレッジインポート・管理モジュール
打ち手・施策集と成功事例を管理
画像・PDF・ドキュメントのアップロードにも対応
"""
import base64
import csv
import io
import json
import os
import shutil
import uuid
from pathlib import Path

from config.benchmarks import INITIAL_CASES, INITIAL_TACTICS

BASE_DIR = Path(__file__).resolve().parent.parent
TACTICS_DIR = BASE_DIR / "data" / "knowledge_store" / "tactics"
CASES_DIR = BASE_DIR / "data" / "knowledge_store" / "cases"
FILES_DIR = BASE_DIR / "data" / "knowledge_store" / "files"
ARCHIVES_DIR = BASE_DIR / "data" / "knowledge_store" / "archives"
PAST_OPS_DIR = BASE_DIR / "data" / "knowledge_store" / "past_operations"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
DOC_EXTENSIONS = {".pdf", ".md", ".txt", ".docx"}


class KnowledgeManager:
    """ナレッジの読み込み・検索・保存を管理"""

    def __init__(self):
        TACTICS_DIR.mkdir(parents=True, exist_ok=True)
        CASES_DIR.mkdir(parents=True, exist_ok=True)
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
        PAST_OPS_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_initial_data()

    def _ensure_initial_data(self):
        """初期データがなければ書き込み"""
        if not list(CASES_DIR.glob("*.json")):
            for case in INITIAL_CASES:
                self.save_case(case)
        if not list(TACTICS_DIR.glob("*.json")):
            for tactic in INITIAL_TACTICS:
                self.save_tactic(tactic)

    # =====================
    # 打ち手
    # =====================
    def save_tactic(self, tactic: dict) -> str:
        tid = tactic.get("id", f"tactic_{uuid.uuid4().hex[:8]}")
        tactic["id"] = tid
        path = TACTICS_DIR / f"{tid}.json"
        path.write_text(json.dumps(tactic, ensure_ascii=False, indent=2), encoding="utf-8")
        return tid

    def get_all_tactics(self) -> list:
        tactics = []
        for f in TACTICS_DIR.glob("*.json"):
            tactics.append(json.loads(f.read_text(encoding="utf-8")))
        return tactics

    def search_tactics(self, target_metric: str = None, plan_type: str = None) -> list:
        all_tactics = self.get_all_tactics()
        results = []
        for t in all_tactics:
            if target_metric and t.get("target_metric") != target_metric:
                if target_metric not in t.get("target_metric", ""):
                    continue
            if plan_type and plan_type not in t.get("plan_type", []):
                continue
            results.append(t)
        return results

    def delete_tactic(self, tid: str):
        path = TACTICS_DIR / f"{tid}.json"
        if path.exists():
            path.unlink()
        self._delete_attached_files(tid)

    # =====================
    # 事例
    # =====================
    def save_case(self, case: dict) -> str:
        cid = case.get("id", f"case_{uuid.uuid4().hex[:8]}")
        case["id"] = cid
        path = CASES_DIR / f"{cid}.json"
        path.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
        return cid

    def get_all_cases(self) -> list:
        cases = []
        for f in CASES_DIR.glob("*.json"):
            cases.append(json.loads(f.read_text(encoding="utf-8")))
        return cases

    def delete_case(self, cid: str):
        path = CASES_DIR / f"{cid}.json"
        if path.exists():
            path.unlink()
        self._delete_attached_files(cid)

    # =====================
    # 戦略設計アーカイブ
    # =====================
    def save_archive(self, archive: dict) -> str:
        """戦略設計結果をアーカイブ保存"""
        aid = archive.get("id", f"archive_{uuid.uuid4().hex[:8]}")
        archive["id"] = aid
        if "created_at" not in archive:
            from datetime import datetime
            archive["created_at"] = datetime.now().isoformat()
        path = ARCHIVES_DIR / f"{aid}.json"
        path.write_text(json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
        return aid

    def get_all_archives(self) -> list:
        archives = []
        for f in ARCHIVES_DIR.glob("*.json"):
            archives.append(json.loads(f.read_text(encoding="utf-8")))
        # 作成日時の新しい順
        archives.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return archives

    def get_archive(self, aid: str) -> dict | None:
        path = ARCHIVES_DIR / f"{aid}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None

    def delete_archive(self, aid: str):
        path = ARCHIVES_DIR / f"{aid}.json"
        if path.exists():
            path.unlink()
        self._delete_attached_files(aid)

    # =====================
    # 過去運用事例
    # =====================
    def save_past_operation(self, op: dict) -> str:
        """過去運用事例を保存（月別数値を含む成長記録）"""
        oid = op.get("id", f"pastop_{uuid.uuid4().hex[:8]}")
        op["id"] = oid
        if "created_at" not in op:
            from datetime import datetime
            op["created_at"] = datetime.now().isoformat()
        path = PAST_OPS_DIR / f"{oid}.json"
        path.write_text(json.dumps(op, ensure_ascii=False, indent=2), encoding="utf-8")
        return oid

    def get_all_past_operations(self) -> list:
        ops = []
        for f in PAST_OPS_DIR.glob("*.json"):
            ops.append(json.loads(f.read_text(encoding="utf-8")))
        ops.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return ops

    def delete_past_operation(self, oid: str):
        path = PAST_OPS_DIR / f"{oid}.json"
        if path.exists():
            path.unlink()
        self._delete_attached_files(oid)

    def get_growth_rates_from_past_ops(self) -> dict:
        """過去運用事例から月次成長率を算出（戦略設計の参考値）
        - 全月同じ値（目標コピー）のデータは除外
        - 異常な成長率（±500%超）は除外
        - 有効データのみから中央値を算出
        """
        ops = self.get_all_past_operations()
        growth = {"reach": [], "profile_access": [], "link_clicks": [], "cv": [],
                  "profile_access_rate": [], "link_click_rate": [], "cv_rate": []}

        for op in ops:
            monthly = op.get("monthly_data", [])
            if len(monthly) < 2:
                continue

            # 全月同じ値のデータを除外（目標値コピーの可能性）
            skip_keys = set()
            for key in ["reach", "profile_access", "link_clicks", "cv"]:
                values = [m.get(key, 0) for m in monthly if m.get(key, 0) > 0]
                if len(values) >= 3 and len(set(values)) <= 1:
                    skip_keys.add(key)

            for i in range(1, len(monthly)):
                prev = monthly[i - 1]
                curr = monthly[i]
                for key in ["reach", "profile_access", "link_clicks", "cv"]:
                    if key in skip_keys:
                        continue
                    pv = prev.get(key, 0)
                    cv_val = curr.get(key, 0)
                    # 0→0は無変動なので除外
                    if pv == 0 and cv_val == 0:
                        continue
                    if pv > 0:
                        rate = (cv_val - pv) / pv
                        # CVは小さな数値（1→0=-100%）で成長率が極端になるため
                        # CV=1以下の変動は除外（統計的に意味がない）
                        if key == "cv" and pv <= 1:
                            continue
                        # 異常値除外（±300%超）
                        if -3.0 <= rate <= 3.0:
                            growth[key].append(rate)

                # 遷移率の変化
                for rate_key, num_key, den_key in [
                    ("profile_access_rate", "profile_access", "reach"),
                    ("link_click_rate", "link_clicks", "profile_access"),
                    ("cv_rate", "cv", "link_clicks"),
                ]:
                    if num_key in skip_keys or den_key in skip_keys:
                        continue
                    p_den = prev.get(den_key, 0)
                    c_den = curr.get(den_key, 0)
                    p_num = prev.get(num_key, 0)
                    c_num = curr.get(num_key, 0)
                    # 分母・分子が両方0のペアは除外
                    if p_den == 0 or c_den == 0:
                        continue
                    if p_num == 0 and c_num == 0:
                        continue
                    p_rate = p_num / p_den
                    c_rate = c_num / c_den
                    if p_rate > 0:
                        change = (c_rate - p_rate) / p_rate
                        if -3.0 <= change <= 3.0:
                            growth[rate_key].append(change)

        # トリム平均を返す（上下10%を除外した平均。外れ値に強い）
        result = {}
        for key, vals in growth.items():
            if vals:
                sorted_v = sorted(vals)
                n = len(sorted_v)
                trim = max(1, n // 10)  # 上下10%
                trimmed = sorted_v[trim:n - trim] if n > 4 else sorted_v
                if trimmed:
                    result[key] = sum(trimmed) / len(trimmed)
                else:
                    result[key] = sorted_v[n // 2]
                result[f"{key}_n"] = n

        # CV補足: 月間CV発生率（CV>0の月の割合）を追加
        cv_months_total = 0
        cv_months_positive = 0
        for op in ops:
            monthly = op.get("monthly_data", [])
            for md in monthly:
                if md.get("reach", 0) > 0 or md.get("link_clicks", 0) > 0:
                    cv_months_total += 1
                    if md.get("cv", 0) > 0:
                        cv_months_positive += 1
        if cv_months_total > 0:
            result["cv_occurrence_rate"] = cv_months_positive / cv_months_total
            result["cv_months_total"] = cv_months_total
            result["cv_months_positive"] = cv_months_positive

        return result

    # =====================
    # ファイル管理（画像・PDF・ドキュメント）
    # =====================
    def save_file(self, file_bytes: bytes, filename: str, parent_id: str) -> dict:
        """ファイルを保存し、メタデータを返す"""
        ext = Path(filename).suffix.lower()
        file_id = f"file_{uuid.uuid4().hex[:8]}"
        safe_name = f"{file_id}{ext}"

        # 親ID別ディレクトリに保存
        parent_dir = FILES_DIR / parent_id
        parent_dir.mkdir(parents=True, exist_ok=True)
        file_path = parent_dir / safe_name
        file_path.write_bytes(file_bytes)

        # テキスト抽出（PDF・テキスト系）
        extracted_text = ""
        if ext == ".pdf":
            extracted_text = self._extract_pdf_text(file_bytes)
        elif ext in {".md", ".txt"}:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")[:2000]
        elif ext == ".docx":
            extracted_text = self._extract_docx_text(file_bytes)

        file_type = "image" if ext in IMAGE_EXTENSIONS else "document"

        meta = {
            "file_id": file_id,
            "filename": filename,
            "saved_as": safe_name,
            "file_type": file_type,
            "extension": ext,
            "size_bytes": len(file_bytes),
            "parent_id": parent_id,
            "path": str(file_path),
            "extracted_text": extracted_text[:2000] if extracted_text else "",
        }
        # メタデータJSONも保存
        meta_path = parent_dir / f"{file_id}.meta.json"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        return meta

    def get_files_for(self, parent_id: str) -> list:
        """特定のナレッジに紐づくファイル一覧を取得"""
        parent_dir = FILES_DIR / parent_id
        if not parent_dir.exists():
            return []
        files = []
        for f in parent_dir.glob("*.meta.json"):
            files.append(json.loads(f.read_text(encoding="utf-8")))
        return files

    def get_file_path(self, parent_id: str, file_id: str) -> Path | None:
        """ファイルの実パスを取得"""
        parent_dir = FILES_DIR / parent_id
        meta_path = parent_dir / f"{file_id}.meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            return Path(meta["path"])
        return None

    def delete_file(self, parent_id: str, file_id: str):
        """個別ファイルを削除"""
        parent_dir = FILES_DIR / parent_id
        meta_path = parent_dir / f"{file_id}.meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            file_path = Path(meta["path"])
            if file_path.exists():
                file_path.unlink()
            meta_path.unlink()

    def _delete_attached_files(self, parent_id: str):
        """親ナレッジ削除時に紐づくファイルも全削除"""
        parent_dir = FILES_DIR / parent_id
        if parent_dir.exists():
            shutil.rmtree(parent_dir)

    def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """PDFからテキスト抽出"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages[:10]:  # 最大10ページ
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            return "\n".join(text_parts)[:2000]
        except Exception:
            return "(PDF読み取りエラー)"

    def _extract_docx_text(self, docx_bytes: bytes) -> str:
        """DOCXからテキスト抽出（簡易）"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(io.BytesIO(docx_bytes)) as z:
                xml_content = z.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                texts = [node.text for node in tree.iter(f"{{{ns['w']}}}t") if node.text]
                return " ".join(texts)[:2000]
        except Exception:
            return "(DOCX読み取りエラー)"

    # =====================
    # インポート（テキスト・CSV）
    # =====================
    def import_from_text(self, text: str, data_type: str) -> str:
        if data_type == "tactic":
            tactic = {
                "id": f"tactic_{uuid.uuid4().hex[:8]}",
                "target_metric": "不明",
                "tactic_name": "インポートされた施策",
                "description": text[:500],
                "plan_type": ["スタンダード", "アドバンス"],
                "category": "その他",
                "expected_impact": "不明",
                "source": "テキストインポート",
            }
            return self.save_tactic(tactic)
        else:
            case = {
                "id": f"case_{uuid.uuid4().hex[:8]}",
                "company_name": "インポート事例",
                "area": "不明",
                "plan_history": "不明",
                "monthly_data": [],
                "key_tactics": [],
                "notes": text[:500],
            }
            return self.save_case(case)

    def import_from_csv(self, csv_content: str, data_type: str) -> list:
        reader = csv.DictReader(io.StringIO(csv_content))
        ids = []
        for row in reader:
            if data_type == "tactic":
                tactic = {
                    "target_metric": row.get("target_metric", row.get("対象指標", "不明")),
                    "tactic_name": row.get("tactic_name", row.get("施策名", "不明")),
                    "description": row.get("description", row.get("説明", "")),
                    "plan_type": row.get("plan_type", row.get("プラン", "スタンダード,アドバンス")).split(","),
                    "category": row.get("category", row.get("カテゴリ", "その他")),
                    "expected_impact": row.get("expected_impact", row.get("期待効果", "不明")),
                    "source": row.get("source", row.get("出典", "CSVインポート")),
                }
                ids.append(self.save_tactic(tactic))
            else:
                case = {
                    "company_name": row.get("company_name", row.get("会社名", "不明")),
                    "area": row.get("area", row.get("エリア", "不明")),
                    "plan_history": row.get("plan_history", row.get("プラン履歴", "不明")),
                    "monthly_data": [],
                    "key_tactics": row.get("key_tactics", row.get("主要施策", "")).split(","),
                    "notes": row.get("notes", row.get("備考", "")),
                }
                ids.append(self.save_case(case))
        return ids

    def import_from_document(self, file_bytes: bytes, filename: str, data_type: str) -> str:
        """PDF/Markdown/テキスト/DOCXからインポート（テキスト抽出→ナレッジ登録）"""
        ext = Path(filename).suffix.lower()

        # テキスト抽出
        if ext == ".pdf":
            text = self._extract_pdf_text(file_bytes)
        elif ext == ".docx":
            text = self._extract_docx_text(file_bytes)
        elif ext in {".md", ".txt"}:
            text = file_bytes.decode("utf-8", errors="ignore")[:2000]
        else:
            text = f"(未対応形式: {ext})"

        # ナレッジとして登録
        record_id = self.import_from_text(text, data_type)

        # 元ファイルも添付保存
        self.save_file(file_bytes, filename, record_id)

        return record_id
