"""F001 的最小回归测试。"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ENGINEERING_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ENGINEERING_ROOT.parents[1]
MODULE_PATH = ENGINEERING_ROOT / "scripts" / "f001_governance_validate.py"


def load_module() -> object:
    """从工程脚本目录加载待测模块。"""
    specification = importlib.util.spec_from_file_location("f001_governance_validate", MODULE_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("无法加载 F001")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class GovernanceValidationTests(unittest.TestCase):
    """验证当前模板的治理资产能通过只读校验。"""

    def test_current_template_passes(self) -> None:
        """当前模板配置、功能登记和已登记治理脚本保持一致。"""
        module = load_module()
        self.assertEqual(module.run(PROJECT_ROOT), 0)


class DailyRecordPolicyTests(unittest.TestCase):
    """临时项目验证日文件实际行为，避免触碰模板真实记录。"""

    def setUp(self) -> None:
        self.module = load_module()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = {"record_policy_registry": "config/feature-registry.yaml"}
        self.registry = self.root / self.config["record_policy_registry"]
        self.registry.parent.mkdir()
        self.policy = {
            "effective_date": "2026-10-29", "timezone": "Asia/Shanghai",
            "project_id": "sample", "profile": "software", "legacy_paths": [],
            "current_artifacts": {},
            "types": {"log": {"aliases": ["日志", "项目日志"], "directory": "records/logs",
                               "filename_body": "项目进度", "label": "日志"}},
        }
        self.save_policy()

    def save_policy(self) -> None:
        self.registry.write_text(json.dumps({"record_policy": self.policy}), encoding="utf-8")

    def entry(self, identity: str = "event-1", event: str = "task-finished", attempt: str = "1",
              recorded: str = "2026-10-29T10:00:00+08:00", occurred: str = "") -> str:
        payload = {"entry_id": identity, "event_key": event, "attempt_id": attempt,
                   "recorded_at": recorded, "occurred_at": occurred,
                   "status": "completed", "requirement_id": "REQ-1"}
        return ("<!-- daily-entry " + json.dumps(payload) + " -->\n"
                + '<a id="entry-' + identity + '"></a>\n## 实际结果\n需求已满足。\n')

    def record(self, relative: str = "records/logs/20261029-项目进度-日志.md", *,
               entries: str | None = None, day: str = "2026-10-29", record_type: str = "log",
               extra: str = "") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = ("---\nschema_version: daily-record/1.0\nproject_id: sample\nrecord_date: " + day
                  + "\nrecord_type: " + record_type + "\nrecord_profile: software\ntimezone: Asia/Shanghai\n" + extra + "---\n\n")
        path.write_text(header + (self.entry() if entries is None else entries), encoding="utf-8")
        return path

    def errors(self) -> list[str]:
        return self.module.validate_daily_records(self.root, self.config)

    def test_canonical_daily_record_passes(self) -> None:
        self.record()
        self.assertEqual(self.errors(), [])

    def test_alias_cross_directory_and_format_does_not_split_day(self) -> None:
        self.record()
        self.record("different/20261029-另一个任务-项目日志.html", record_type="项目日志",
                    entries=self.entry("event-2", "other-task"))
        errors = self.errors()
        self.assertTrue(any("多个可写文件" in value for value in errors), errors)
        self.assertTrue(any("规范落点" in value for value in errors), errors)

    def test_arbitrary_extension_is_not_a_second_active_record_dimension(self) -> None:
        self.record()
        self.record("different/20261029-另一个任务-日志.notes", entries=self.entry("event-2", "other-task"))
        self.assertTrue(any("多个可写文件" in value for value in self.errors()))

    def test_legacy_before_effective_date_keeps_original_place(self) -> None:
        path = self.root / "history/20261028-旧任务-日志.md"
        path.parent.mkdir()
        path.write_text("历史原文，没有日记录schema。", encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_new_unschemed_record_cannot_hide_as_legacy(self) -> None:
        path = self.root / "records/20261029-新任务-项目日志.txt"
        path.parent.mkdir()
        path.write_text("新任务", encoding="utf-8")
        self.assertTrue(any("缺少daily-record" in value for value in self.errors()))

    def test_declared_daily_schema_is_checked_even_with_old_date(self) -> None:
        self.record("other/20261028-旧任务-日志.md", day="2026-10-28",
                    entries=self.entry(recorded="2026-10-28T10:00:00+08:00"))
        self.assertTrue(any("规范落点" in value for value in self.errors()))

    def test_archived_original_does_not_create_second_active_file(self) -> None:
        self.record()
        self.record("history/20261029-旧快照-日志.md", extra="record_state: archived\n")
        self.policy["legacy_paths"] = ["history/20261029-旧快照-日志.md"]
        self.save_policy()
        self.assertEqual(self.errors(), [])

    def test_daily_schema_in_output_is_not_hidden_as_raw_trace(self) -> None:
        self.record()
        self.record("output/trace/session/20261029-任务B-项目日志.md", record_type="项目日志",
                    entries=self.entry("event-2", "other-task"))
        self.assertTrue(any("多个可写文件" in value for value in self.errors()))

    def test_directory_legacy_exemption_is_rejected(self) -> None:
        folder = self.root / "history"
        folder.mkdir()
        (folder / "20261029-新稿-日志.md").write_text("新活动记录", encoding="utf-8")
        self.policy["legacy_paths"] = ["history"]
        self.save_policy()
        errors = self.errors()
        self.assertTrue(any("精确文件" in value for value in errors), errors)
        self.assertTrue(any("缺少daily-record" in value for value in errors), errors)

    def test_undated_known_record_requires_explicit_legacy_registration(self) -> None:
        target = self.root / "history/任务B-日志.md"
        target.parent.mkdir()
        target.write_text("不能省略日期规避规则", encoding="utf-8")
        self.assertTrue(any("缺少规范日期" in value for value in self.errors()))
        self.policy["legacy_paths"] = ["history/任务B-日志.md"]
        self.save_policy()
        self.assertEqual(self.errors(), [])

    def test_plain_record_label_without_date_cannot_bypass_policy(self) -> None:
        (self.root / "日志.md").write_text("没有日期的日志", encoding="utf-8")
        self.assertTrue(any("缺少规范日期" in value for value in self.errors()))

    def test_new_record_cannot_self_mark_archived_to_bypass_duplicate(self) -> None:
        self.record()
        self.record("other/20261029-任务B-项目日志.md", record_type="项目日志",
                    entries=self.entry("event-2", "other-task"), extra="record_state: archived\n")
        errors = self.errors()
        self.assertTrue(any("不能自标归档" in value for value in errors), errors)
        self.assertTrue(any("多个可写文件" in value for value in errors), errors)

    def test_missing_profile_is_not_accepted_as_appendable_record(self) -> None:
        path = self.record()
        path.write_text(path.read_text(encoding="utf-8").replace("record_profile: software\n", ""), encoding="utf-8")
        self.assertTrue(any("profile" in value for value in self.errors()))

    def test_readonly_export_references_matching_master(self) -> None:
        self.record()
        self.record("exports/20261029-项目进度-日志.html",
                    extra="derived_from: records/logs/20261029-项目进度-日志.md\n")
        self.assertEqual(self.errors(), [])

    def test_export_cannot_use_arbitrary_existing_file_as_master(self) -> None:
        (self.root / "README.md").write_text("不是日记录", encoding="utf-8")
        self.record("exports/20261029-项目进度-日志.html", extra="derived_from: README.md\n")
        self.assertTrue(any("来源身份不匹配" in value for value in self.errors()))

    def test_duplicate_entry_and_event_rejected(self) -> None:
        self.record(entries=self.entry() + self.entry())
        errors = self.errors()
        self.assertTrue(any("重复日记录条目ID" in value for value in errors), errors)
        self.assertTrue(any("重复日记录事件" in value for value in errors), errors)

    def test_real_attempts_can_share_event_with_distinct_identity(self) -> None:
        self.record(entries=self.entry() + self.entry("event-2", attempt="2"))
        self.assertEqual(self.errors(), [])

    def test_recorded_time_uses_shanghai_not_host_day(self) -> None:
        self.record(entries=self.entry(recorded="2026-10-28T18:00:00+00:00",
                                       occurred="2026-10-27T12:00:00+00:00"))
        self.assertEqual(self.errors(), [])

    def test_wrong_day_and_naive_time_rejected(self) -> None:
        self.record(entries=self.entry(recorded="2026-10-29T18:00:00+00:00"))
        self.assertTrue(any("记录日不一致" in value for value in self.errors()))
        self.record(entries=self.entry(recorded="2026-10-29T10:00:00"))
        self.assertTrue(any("时间无效" in value for value in self.errors()))

    def test_empty_day_file_rejected(self) -> None:
        self.record(entries="")
        self.assertTrue(any("没有真实独立条目" in value for value in self.errors()))

    def test_current_artifact_requires_existing_file_and_anchor(self) -> None:
        self.record()
        self.policy["current_artifacts"] = {"progress": "records/logs/20261029-项目进度-日志.md#entry-event-1"}
        self.save_policy()
        self.assertEqual(self.errors(), [])
        self.policy["current_artifacts"]["progress"] = "records/logs/20261029-项目进度-日志.md#missing"
        self.save_policy()
        self.assertTrue(any("锚点不存在" in value for value in self.errors()))

    def test_policy_refuses_escaping_current_artifact(self) -> None:
        self.policy["current_artifacts"] = {"progress": "../outside.md"}
        self.save_policy()
        with self.assertRaises(self.module.GovernanceValidationError):
            self.errors()

    def test_explicit_legacy_registration_is_not_implicit_directory_guess(self) -> None:
        old = self.root / "known/20261029-导入历史-日志.md"
        old.parent.mkdir()
        old.write_text("导入历史", encoding="utf-8")
        self.policy["legacy_paths"] = ["known/20261029-导入历史-日志.md"]
        self.save_policy()
        self.assertEqual(self.errors(), [])
        other = self.root / "known/20261029-另一个任务-项目日志.md"
        other.write_text("新任务", encoding="utf-8")
        self.assertTrue(any("缺少daily-record" in value for value in self.errors()))


if __name__ == "__main__":
    unittest.main()
