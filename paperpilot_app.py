import re
import sys
import unittest
from pathlib import Path
from typing import Callable

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    tk = None
    filedialog = None
    messagebox = None
    ttk = None

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    TkinterDnD = None
    DND_FILES = None

INVALID_FILENAME_CHARS = r'<>:"/\\|?*'


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def safe_filename(text: str, max_len: int = 180) -> str:
    text = normalize_spaces(text)
    for ch in INVALID_FILENAME_CHARS:
        text = text.replace(ch, "_")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip(" ._")
    return text[:max_len].strip(" ._") or "untitled"


def looks_like_bad_title(text: str) -> bool:
    low = normalize_spaces(text).lower()
    bad_words = [
        "abstract", "introduction", "keywords", "ieee", "journal",
        "transactions", "www.", "doi", "copyright"
    ]
    if any(word in low for word in bad_words):
        return True
    if len(low) < 15:
        return True
    if low.count(" ") < 3:
        return True
    return False


def extract_title_from_pdf(pdf_path: str) -> str:
    if fitz is None:
        raise ImportError("PyMuPDF가 설치되지 않았습니다. 먼저 'python -m pip install pymupdf' 를 실행하세요.")

    with fitz.open(pdf_path) as doc:
        meta = doc.metadata or {}
        meta_title = normalize_spaces(meta.get("title", "") or "")
        if meta_title and not looks_like_bad_title(meta_title):
            return meta_title

        if len(doc) == 0:
            raise ValueError("빈 PDF입니다.")

        page = doc[0]
        page_dict = page.get_text("dict")
        spans = []

        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                line_text_parts = []
                max_size = 0.0
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        line_text_parts.append(text)
                        max_size = max(max_size, float(span.get("size", 0) or 0))
                line_text = normalize_spaces(" ".join(line_text_parts))
                if line_text:
                    spans.append((max_size, line_text))

        spans.sort(key=lambda x: x[0], reverse=True)
        candidates = []
        for size, text in spans[:20]:
            if not looks_like_bad_title(text):
                candidates.append((size, text))

        if candidates:
            top_size = candidates[0][0]
            merged = [text for size, text in candidates if size >= top_size * 0.8]
            title = normalize_spaces(" ".join(merged[:3]))
            if title and not looks_like_bad_title(title):
                return title

        plain_text = page.get_text("text")
        for line in plain_text.splitlines():
            line = normalize_spaces(line)
            if line and not looks_like_bad_title(line):
                return line

    raise ValueError("제목을 찾지 못했습니다.")


def resolve_duplicate_path(path: Path) -> Path:
    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def rename_pdf_to_title(pdf_path: str, title_getter: Callable[[str], str] = extract_title_from_pdf) -> tuple[str, str]:
    src = Path(pdf_path)
    if not src.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {src}")
    if src.suffix.lower() != ".pdf":
        raise ValueError("PDF 파일만 처리할 수 있습니다.")

    title = title_getter(str(src))
    new_name = safe_filename(title) + ".pdf"
    dst = resolve_duplicate_path(src.with_name(new_name))

    if dst == src:
        return src.name, src.name

    src.rename(dst)
    return src.name, dst.name


def split_dnd_files(data: str) -> list[str]:
    if not data:
        return []
    results = []
    token = ""
    in_brace = False
    for ch in data:
        if ch == "{":
            in_brace = True
            if token.strip():
                results.extend(token.strip().split())
                token = ""
            continue
        if ch == "}":
            in_brace = False
            if token:
                results.append(token)
                token = ""
            continue
        if ch == " " and not in_brace:
            if token:
                results.append(token)
                token = ""
            continue
        token += ch
    if token:
        results.append(token)
    return [x.strip().strip('"') for x in results if x.strip()]


class PaperRenamerGUI:
    def __init__(self):
        if tk is None:
            raise ImportError("tkinter를 찾을 수 없습니다. 공식 Python 설치본으로 다시 설치하거나 'python -m tkinter'로 확인하세요.")

        base_cls = TkinterDnD.Tk if TkinterDnD is not None else tk.Tk
        self.root = base_cls()
        self.root.title("PaperPilot - 논문 파일명 변경")
        self.root.geometry("860x620")
        self.root.minsize(780, 540)

        self.files: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="논문 PDF 제목 기반 파일명 변경", font=("맑은 고딕", 17, "bold"))
        title.pack(anchor="w")

        desc = ttk.Label(
            frame,
            text="PDF 파일을 드래그 앤 드롭하거나 추가 버튼으로 넣으면 제목을 추출해 파일명을 자동으로 바꿉니다.",
        )
        desc.pack(anchor="w", pady=(6, 14))

        drop_outer = ttk.LabelFrame(frame, text="드래그 앤 드롭 영역", padding=10)
        drop_outer.pack(fill="x", pady=(0, 12))

        self.drop_label = tk.Label(
            drop_outer,
            text="여기로 PDF 파일을 끌어다 놓으세요",
            relief="groove",
            bd=2,
            height=4,
            bg="#f7f7f7",
            font=("맑은 고딕", 12)
        )
        self.drop_label.pack(fill="x")

        if TkinterDnD is not None and DND_FILES is not None:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.handle_drop)
            self.drop_label.dnd_bind("<<DropEnter>>", self.handle_drop_enter)
            self.drop_label.dnd_bind("<<DropLeave>>", self.handle_drop_leave)
        else:
            self.drop_label.configure(text="tkinterdnd2 미설치: 버튼으로만 추가 가능\n설치 명령: python -m pip install tkinterdnd2")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(0, 12))

        ttk.Button(btn_frame, text="PDF 추가", command=self.add_files).pack(side="left")
        ttk.Button(btn_frame, text="선택 항목 제거", command=self.remove_selected).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="전체 지우기", command=self.clear_files).pack(side="left")
        ttk.Button(btn_frame, text="파일명 변경 실행", command=self.rename_selected_files).pack(side="right")

        columns = ("현재 파일명", "예상 제목")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        self.tree.heading("현재 파일명", text="현재 파일명")
        self.tree.heading("예상 제목", text="예상 제목")
        self.tree.column("현재 파일명", width=250, anchor="w")
        self.tree.column("예상 제목", width=560, anchor="w")
        self.tree.pack(fill="both", expand=False)

        self.status_var = tk.StringVar(value="PDF를 추가하세요.")
        ttk.Label(frame, textvariable=self.status_var).pack(anchor="w", pady=(10, 8))

        ttk.Label(frame, text="처리 로그").pack(anchor="w")
        self.log = tk.Text(frame, height=12, wrap="word")
        self.log.pack(fill="both", expand=True, pady=(4, 0))

    def handle_drop_enter(self, _event=None):
        self.drop_label.configure(bg="#e8f4ff")
        return _event.action if _event else None

    def handle_drop_leave(self, _event=None):
        self.drop_label.configure(bg="#f7f7f7")
        return _event.action if _event else None

    def handle_drop(self, event):
        self.drop_label.configure(bg="#f7f7f7")
        paths = split_dnd_files(event.data)
        pdf_paths = [p for p in paths if p.lower().endswith(".pdf")]
        self._add_pdf_paths(pdf_paths)
        return event.action

    def _add_pdf_paths(self, selected: list[str]) -> None:
        if not selected:
            return

        added = 0
        for file_path in selected:
            if file_path not in self.files:
                self.files.append(file_path)
                try:
                    title = extract_title_from_pdf(file_path)
                except Exception as e:
                    title = f"제목 추출 실패: {e}"
                self.tree.insert("", "end", values=(Path(file_path).name, title), iid=file_path)
                added += 1

        self.status_var.set(f"선택된 PDF {len(self.files)}개")
        self.log.insert("end", f"추가됨: {added}개\n")
        self.log.see("end")

    def add_files(self) -> None:
        if filedialog is None:
            return

        selected = filedialog.askopenfilenames(
            title="논문 PDF 선택",
            filetypes=[("PDF files", "*.pdf")],
        )
        self._add_pdf_paths(list(selected))

    def remove_selected(self) -> None:
        selected_items = self.tree.selection()
        for item in selected_items:
            if item in self.files:
                self.files.remove(item)
            self.tree.delete(item)
        self.status_var.set(f"선택된 PDF {len(self.files)}개")

    def clear_files(self) -> None:
        self.files.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_var.set("PDF를 추가하세요.")

    def rename_selected_files(self) -> None:
        if not self.files:
            if messagebox:
                messagebox.showwarning("알림", "먼저 PDF를 추가하세요.")
            return

        success = 0
        fail = 0
        self.log.delete("1.0", "end")

        for file_path in list(self.files):
            try:
                old_name, new_name = rename_pdf_to_title(file_path)
                self.log.insert("end", f"성공: {old_name} -> {new_name}\n")
                success += 1
            except Exception as e:
                self.log.insert("end", f"실패: {Path(file_path).name} | {e}\n")
                fail += 1

        self.log.insert("end", f"\n완료: 성공 {success}개, 실패 {fail}개\n")
        self.log.see("end")
        self.clear_files()

        if messagebox:
            messagebox.showinfo("완료", f"성공 {success}개, 실패 {fail}개")

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    gui = PaperRenamerGUI()
    gui.run()
    return 0


class PaperRenamerTests(unittest.TestCase):
    def test_normalize_spaces(self):
        self.assertEqual(normalize_spaces("  A\n\nB   C  "), "A B C")

    def test_safe_filename(self):
        self.assertEqual(safe_filename('My: Paper/Title?'), 'My_ Paper_Title')

    def test_looks_like_bad_title_short(self):
        self.assertTrue(looks_like_bad_title("Short title"))

    def test_looks_like_bad_title_good(self):
        self.assertFalse(looks_like_bad_title("Modeling and Analysis of a Proposed Magnetic Bearing System"))

    def test_resolve_duplicate_path(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "paper.pdf"
            base.write_text("x", encoding="utf-8")
            resolved = resolve_duplicate_path(base)
            self.assertEqual(resolved.name, "paper_2.pdf")

    def test_rename_pdf_to_title(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "download.pdf"
            src.write_text("dummy", encoding="utf-8")

            def fake_title_getter(_path: str) -> str:
                return "A Great Paper on Magnetic Bearings"

            old_name, new_name = rename_pdf_to_title(str(src), title_getter=fake_title_getter)
            self.assertEqual(old_name, "download.pdf")
            self.assertEqual(new_name, "A Great Paper on Magnetic Bearings.pdf")
            self.assertTrue((Path(tmp) / new_name).exists())

    def test_rename_pdf_to_title_non_pdf(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "note.txt"
            src.write_text("dummy", encoding="utf-8")
            with self.assertRaises(ValueError):
                rename_pdf_to_title(str(src), title_getter=lambda _: "Anything")

    def test_split_dnd_files_with_braces(self):
        data = '{C:/test folder/a.pdf} {C:/b.pdf}'
        self.assertEqual(split_dnd_files(data), ['C:/test folder/a.pdf', 'C:/b.pdf'])

    def test_split_dnd_files_plain(self):
        data = 'C:/a.pdf C:/b.pdf'
        self.assertEqual(split_dnd_files(data), ['C:/a.pdf', 'C:/b.pdf'])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.main(argv=[sys.argv[0]])
    else:
        main()
