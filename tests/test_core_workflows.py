import unittest
from pathlib import Path

from src.file_tool.cleanup import build_cleanup_rows
from src.file_tool.normalize import normalize_filename
from src.file_tool.scanner import scan_files
from src.file_tool.year_planner import build_year_plan


SAMPLE_ROOT = Path("data/sample_files")


class CoreWorkflowTests(unittest.TestCase):
    def test_normalize_filename_keeps_extension_and_removes_noise(self) -> None:
        self.assertEqual(
            normalize_filename("  Resume Final Copy V2.PDF  "),
            "resume.pdf",
        )

    def test_scan_files_reads_committed_sample_files(self) -> None:
        accepted, skipped = scan_files(SAMPLE_ROOT)

        self.assertEqual({path.name for path in accepted}, {"photo.png", "test_file.md"})
        self.assertEqual(skipped, [])

    def test_cleanup_audit_classifies_sample_files_as_personal_files(self) -> None:
        rows = build_cleanup_rows(SAMPLE_ROOT)
        actions_by_name = {row["name"]: row["action"] for row in rows}

        self.assertEqual(actions_by_name["photo.png"], "KEEP_PERSONAL_FILE")
        self.assertEqual(actions_by_name["test_file.md"], "KEEP_PERSONAL_FILE")

    def test_year_plan_routes_sample_media_and_document(self) -> None:
        rows = build_year_plan(SAMPLE_ROOT)
        rows_by_name = {Path(row["source_path"]).name: row for row in rows}

        self.assertEqual(rows_by_name["photo.png"]["bucket"], "06_MEDIA")
        self.assertEqual(rows_by_name["photo.png"]["action"], "MOVE_TO_YEAR_TOPIC")
        self.assertEqual(rows_by_name["test_file.md"]["bucket"], "_INBOX_REVIEW")
        self.assertEqual(rows_by_name["test_file.md"]["action"], "REVIEW_CLASSIFY_TO_YEAR")


if __name__ == "__main__":
    unittest.main()
