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
    specification = importlib.util.spec_from_file_location(
        "f001_governance_validate", MODULE_PATH
    )
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
            "effective_date": "2026-10-29",
            "timezone": "Asia/Shanghai",
            "project_id": "sample",
            "profile": "software",
            "legacy_paths": [],
            "current_artifacts": {},
            "types": {
                "log": {
                    "aliases": ["日志", "项目日志"],
                    "directory": "records/logs",
                    "filename_body": "项目进度",
                    "label": "日志",
                }
            },
        }
        self.save_policy()

    def save_policy(self) -> None:
        self.registry.write_text(
            json.dumps({"record_policy": self.policy}), encoding="utf-8"
        )

    def entry(
        self,
        identity: str = "event-1",
        event: str = "task-finished",
        attempt: str = "1",
        recorded: str = "2026-10-29T10:00:00+08:00",
        occurred: str = "",
    ) -> str:
        payload = {
            "entry_id": identity,
            "event_key": event,
            "attempt_id": attempt,
            "recorded_at": recorded,
            "occurred_at": occurred,
            "status": "completed",
            "requirement_id": "REQ-1",
        }
        return (
            "<!-- daily-entry "
            + json.dumps(payload)
            + " -->\n"
            + '<a id="entry-'
            + identity
            + '"></a>\n## 实际结果\n需求已满足。\n'
        )

    def record(
        self,
        relative: str = "records/logs/20261029-项目进度-日志.md",
        *,
        entries: str | None = None,
        day: str = "2026-10-29",
        record_type: str = "log",
        extra: str = "",
    ) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = (
            "---\nschema_version: daily-record/1.0\nproject_id: sample\nrecord_date: "
            + day
            + "\nrecord_type: "
            + record_type
            + "\nrecord_profile: software\ntimezone: Asia/Shanghai\n"
            + extra
            + "---\n\n"
        )
        path.write_text(
            header + (self.entry() if entries is None else entries), encoding="utf-8"
        )
        return path

    def errors(self) -> list[str]:
        return self.module.validate_daily_records(self.root, self.config)

    def test_canonical_daily_record_passes(self) -> None:
        self.record()
        self.assertEqual(self.errors(), [])

    def test_alias_cross_directory_and_format_does_not_split_day(self) -> None:
        self.record()
        self.record(
            "different/20261029-另一个任务-项目日志.html",
            record_type="项目日志",
            entries=self.entry("event-2", "other-task"),
        )
        errors = self.errors()
        self.assertTrue(any("多个可写文件" in value for value in errors), errors)
        self.assertTrue(any("规范落点" in value for value in errors), errors)

    def test_arbitrary_extension_is_not_a_second_active_record_dimension(self) -> None:
        self.record()
        self.record(
            "different/20261029-另一个任务-日志.notes",
            entries=self.entry("event-2", "other-task"),
        )
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
        self.record(
            "other/20261028-旧任务-日志.md",
            day="2026-10-28",
            entries=self.entry(recorded="2026-10-28T10:00:00+08:00"),
        )
        self.assertTrue(any("规范落点" in value for value in self.errors()))

    def test_archived_original_does_not_create_second_active_file(self) -> None:
        self.record()
        self.record("history/20261029-旧快照-日志.md", extra="record_state: archived\n")
        self.policy["legacy_paths"] = ["history/20261029-旧快照-日志.md"]
        self.save_policy()
        self.assertEqual(self.errors(), [])

    def test_daily_schema_in_output_is_not_hidden_as_raw_trace(self) -> None:
        self.record()
        self.record(
            "output/trace/session/20261029-任务B-项目日志.md",
            record_type="项目日志",
            entries=self.entry("event-2", "other-task"),
        )
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
        self.record(
            "other/20261029-任务B-项目日志.md",
            record_type="项目日志",
            entries=self.entry("event-2", "other-task"),
            extra="record_state: archived\n",
        )
        errors = self.errors()
        self.assertTrue(any("不能自标归档" in value for value in errors), errors)
        self.assertTrue(any("多个可写文件" in value for value in errors), errors)

    def test_missing_profile_is_not_accepted_as_appendable_record(self) -> None:
        path = self.record()
        path.write_text(
            path.read_text(encoding="utf-8").replace("record_profile: software\n", ""),
            encoding="utf-8",
        )
        self.assertTrue(any("profile" in value for value in self.errors()))

    def test_readonly_export_references_matching_master(self) -> None:
        self.record()
        self.record(
            "exports/20261029-项目进度-日志.html",
            extra="derived_from: records/logs/20261029-项目进度-日志.md\n",
        )
        self.assertEqual(self.errors(), [])

    def test_export_cannot_use_arbitrary_existing_file_as_master(self) -> None:
        (self.root / "README.md").write_text("不是日记录", encoding="utf-8")
        self.record(
            "exports/20261029-项目进度-日志.html", extra="derived_from: README.md\n"
        )
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
        self.record(
            entries=self.entry(
                recorded="2026-10-28T18:00:00+00:00",
                occurred="2026-10-27T12:00:00+00:00",
            )
        )
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
        self.policy["current_artifacts"] = {
            "progress": "records/logs/20261029-项目进度-日志.md#entry-event-1"
        }
        self.save_policy()
        self.assertEqual(self.errors(), [])
        self.policy["current_artifacts"]["progress"] = (
            "records/logs/20261029-项目进度-日志.md#missing"
        )
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


class ResearchLogContractTests(unittest.TestCase):
    """研究派生合同在临时项目中测试，不修改普通软件配置。"""

    save_policy = DailyRecordPolicyTests.save_policy
    entry = DailyRecordPolicyTests.entry
    record = DailyRecordPolicyTests.record
    errors = DailyRecordPolicyTests.errors

    def setUp(self) -> None:
        DailyRecordPolicyTests.setUp(self)
        self.policy.update(
            profile="research",
            log_contract="group-meeting/1.0",
            log_contract_effective_date="2026-10-30",
        )
        self.save_policy()
        sources = self.root / "sources"
        sources.mkdir()
        (sources / "points.md").write_text(
            '<a id="point"></a>研究要点', encoding="utf-8"
        )
        (sources / "results.csv").write_text(
            "method,value\nbase,1\nnew,0.9\n", encoding="utf-8"
        )

    def research_payload(self) -> dict:
        return {
            "entry_id": "research-1",
            "event_key": "comparison-result",
            "attempt_id": "1",
            "recorded_at": "2026-10-30T10:00:00+08:00",
            "status": "completed",
            "report_contract": "group-meeting/1.0",
            "work_kind": "performance",
            "research_point": "模型计算效率",
            "research_source": "sources/points.md#point",
            "guide_questions": ["4.1.Q1"],
            "research_question": "相同输入下计算代价如何变化",
            "actions": "在共同条件下比较两种方法",
            "result": "本次局部指标下降",
            "interpretation": "局部计算有所改善",
            "limitations": "仅限当前输入规模",
            "next_step": "分析不同规模是否保持趋势",
            "evidence": ["sources/results.csv"],
            "comparison_conditions": "相同输入和计时范围",
            "metrics": "局部耗时相对变化为-10%，仅本输入范围",
        }

    def write_research(self, payload: dict, appendix: str = "") -> Path:
        entry = (
            "<!-- daily-entry "
            + json.dumps(payload, ensure_ascii=False)
            + ' -->\n<a id="entry-'
            + payload["entry_id"]
            + '"></a>\n研究结果\n'
            + appendix
        )
        path = self.record(
            "records/logs/20261030-项目进度-日志.md", entries=entry, day="2026-10-30"
        )
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "record_profile: software", "record_profile: research"
            ),
            encoding="utf-8",
        )
        return path

    def test_research_two_level_mapping_and_negative_result_pass(self) -> None:
        self.write_research(self.research_payload())
        self.assertEqual(self.errors(), [])

    def test_missing_contract_cannot_evade_requirements(self) -> None:
        payload = self.research_payload()
        del payload["report_contract"]
        self.write_research(payload)
        self.assertTrue(any("合同" in error for error in self.errors()))

    def test_missing_guide_or_question_out_of_range_fails(self) -> None:
        payload = self.research_payload()
        payload["guide_questions"] = ["4.1.Q15"]
        self.write_research(payload)
        self.assertTrue(any("题号无效" in error for error in self.errors()))
        payload["guide_questions"] = []
        self.write_research(payload)
        self.assertTrue(any("两层映射" in error for error in self.errors()))

    def test_missing_question_actions_or_boundary_fails(self) -> None:
        for field in (
            "research_question",
            "actions",
            "result",
            "interpretation",
            "limitations",
            "next_step",
        ):
            with self.subTest(field=field):
                payload = self.research_payload()
                payload[field] = "待填写"
                self.write_research(payload)
                self.assertTrue(any(field in error for error in self.errors()))

    def test_performance_and_analysis_need_conditions_and_metrics(self) -> None:
        for kind in ("performance", "analysis"):
            payload = self.research_payload()
            payload["work_kind"] = kind
            del payload["metrics"]
            del payload["comparison_conditions"]
            self.write_research(payload)
            errors = self.errors()
            self.assertTrue(any("metrics" in error for error in errors))
            self.assertTrue(any("comparison_conditions" in error for error in errors))

    def test_engineering_work_cannot_hide_in_appendix_or_kind(self) -> None:
        payload = self.research_payload()
        payload["work_kind"] = "method"
        self.write_research(
            payload, "## 附录\npytest检查通过，完成需求登记和角色交接。"
        )
        self.assertTrue(any("正文或附录" in error for error in self.errors()))
        payload["work_kind"] = "engineering"
        self.write_research(payload)
        self.assertTrue(any("work_kind" in error for error in self.errors()))

    def test_missing_local_evidence_or_source_anchor_fails(self) -> None:
        payload = self.research_payload()
        payload["research_source"] = "sources/points.md#missing"
        payload["evidence"] = ["sources/missing.csv"]
        self.write_research(payload)
        errors = self.errors()
        self.assertTrue(any("锚点不存在" in error for error in errors))
        self.assertTrue(any("入口不存在" in error for error in errors))

    def test_bare_numbers_and_nonfinite_metrics_are_not_research_expression(
        self,
    ) -> None:
        payload = self.research_payload()
        payload["result"] = 0
        payload["metrics"] = {"difference": float("nan")}
        self.write_research(payload)
        errors = self.errors()
        self.assertTrue(any("result" in error for error in errors))
        self.assertTrue(any("metrics" in error for error in errors))

    def test_contract_scalar_fields_reject_container_or_numeric_values(self) -> None:
        scalar_fields = (
            "research_point",
            "research_source",
            "research_question",
            "actions",
            "result",
            "interpretation",
            "limitations",
            "next_step",
            "comparison_conditions",
            "metrics",
        )
        for field in scalar_fields:
            for wrong in (["看似完整的文字"], {"value": "看似完整的文字"}, 0):
                with self.subTest(field=field, wrong=wrong):
                    payload = self.research_payload()
                    payload[field] = wrong
                    self.write_research(payload)
                    self.assertTrue(any(field in error for error in self.errors()))

    def test_software_log_is_not_forced_to_provide_research_fields(self) -> None:
        self.policy["profile"] = "software"
        self.save_policy()
        self.record()
        self.assertEqual(self.errors(), [])

    def test_software_log_must_reference_a_requirement(self) -> None:
        self.policy["profile"] = "software"
        self.save_policy()
        path = self.record()
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                '"requirement_id": "REQ-1"', '"requirement_id": ""'
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("requirement_id" in error for error in self.errors()))


class MinimalProcessRecordTests(unittest.TestCase):
    save_policy = DailyRecordPolicyTests.save_policy
    entry = DailyRecordPolicyTests.entry
    record = DailyRecordPolicyTests.record
    errors = DailyRecordPolicyTests.errors

    def setUp(self) -> None:
        DailyRecordPolicyTests.setUp(self)
        self.policy.update(
            process_record_profile="minimal",
            enabled_daily_types=["requirement", "log"],
            minimal_records_effective_date="2026-10-30",
        )
        for kind, label in {
            "requirement": "需求记录",
            "change": "变更记录",
            "supervision": "监督记录",
            "reflection": "反思",
            "quality": "质量记录",
            "cost": "成本记录",
            "work-contract": "工作契约",
            "handoff": "交接书",
        }.items():
            self.policy["types"][kind] = {
                "aliases": [label],
                "directory": "records/" + kind,
                "filename_body": "固定主体",
                "label": label,
            }
        self.save_policy()

    def test_minimal_keeps_requirement_and_actual_progress(self) -> None:
        entries = self.entry(recorded="2026-10-30T10:00:00+08:00")
        self.record(
            "records/logs/20261030-项目进度-日志.md", day="2026-10-30", entries=entries
        )
        self.record(
            "records/requirement/20261030-固定主体-需求记录.md",
            day="2026-10-30",
            record_type="requirement",
            entries=self.entry(
                "requirement-1", "requirement-1", recorded="2026-10-30T10:00:00+08:00"
            ),
        )
        self.assertEqual(self.errors(), [])

    def test_new_disabled_daily_types_rejected(self) -> None:
        for kind in (
            "change",
            "supervision",
            "reflection",
            "quality",
            "cost",
            "work-contract",
            "handoff",
        ):
            with self.subTest(kind=kind):
                label = self.policy["types"][kind]["label"]
                path = self.record(
                    f"records/{kind}/20261030-固定主体-{label}.md",
                    record_type=kind,
                    day="2026-10-30",
                    entries=self.entry(recorded="2026-10-30T10:00:00+08:00"),
                )
                self.assertTrue(
                    any("精简模式停用日记录类型" in error for error in self.errors())
                )
                path.unlink()

    def test_existing_pre_minimal_change_is_preserved(self) -> None:
        self.record(
            "records/change/20261029-固定主体-变更记录.md", record_type="change"
        )
        self.assertEqual(self.errors(), [])

    def test_renaming_management_report_in_disabled_home_does_not_escape(self) -> None:
        path = self.root / "records/quality/20261030-检查整理-说明.md"
        path.parent.mkdir(parents=True)
        path.write_text("# 日常管理报告\n过程内容", encoding="utf-8")
        self.assertTrue(any("不能改名报告逃逸" in error for error in self.errors()))

    def test_undated_management_report_does_not_escape_minimal_mode(self) -> None:
        path = self.root / "管理报告.md"
        path.write_text("# 例行监督报告\n操作流水", encoding="utf-8")
        self.assertTrue(any("不能改名报告逃逸" in error for error in self.errors()))

    def test_real_template_acceptance_and_delivery_homes_keep_entity_documents(
        self,
    ) -> None:
        actual = json.loads(
            (ENGINEERING_ROOT / "config/feature-registry.yaml").read_text(
                encoding="utf-8"
            )
        )
        for kind in ("work-contract", "handoff", "decision"):
            self.policy["types"][kind] = actual["record_policy"]["types"][kind]
        self.save_policy()
        files = {
            "projectname/achieve/03-测试与验收/20261030-登录功能-正式验收报告.md": "# 登录功能正式验收报告\n真实用户功能和独立验收意见。",
            "projectname/achieve/04-交付与阶段/20261030-产品使用-用户手册.md": "# 产品使用手册\n实际功能使用步骤。",
        }
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.assertEqual(self.errors(), [])

    def test_formal_acceptance_and_raw_run_are_not_removed(self) -> None:
        path = self.root / "delivery/20261030-产品版本-正式验收报告.md"
        path.parent.mkdir()
        path.write_text("# 正式验收结论\n真实产品结果", encoding="utf-8")
        raw = self.root / "output/run/20261030-内部检查-质量记录.txt"
        raw.parent.mkdir(parents=True)
        raw.write_text("原始运行信息", encoding="utf-8")
        self.assertEqual(self.errors(), [])


class ReaderDocumentV2Tests(unittest.TestCase):
    """四份读者文档保持入口完整且不把机器资料搬入正文。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "engineering"
        (self.root / "configs").mkdir(parents=True)
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.module = (
            globals()["GOVERNANCE"]
            if "GOVERNANCE" in globals()
            else globals()["load_module"]()
        )
        self.names = [
            "README.md",
            "项目技术说明.md",
            "使用指南.md",
            "结果说明与适用范围.md",
        ]
        self.policy = {
            "enabled": True,
            "profile": "reader",
            "root": "docs",
            "root_entries": self.names,
            "stable_directories": [],
            "baseline_paths": [],
            "pinned_paths": {},
        }
        self.save()
        for name in self.names:
            (self.docs / name).write_text(
                "# 面向读者\n\n讲清问题、实际操作与结果边界。\n", encoding="utf-8"
            )

    def save(self) -> None:
        (self.root / "configs/features.yaml").write_text(
            json.dumps({"technical_documents": self.policy}, ensure_ascii=False),
            encoding="utf-8",
        )

    def errors(self) -> list[str]:
        return self.module.validate_technical_documents(self.root)

    def test_four_reader_documents_pass_and_missing_one_is_visible(self) -> None:
        self.assertEqual(self.errors(), [])
        (self.docs / "使用指南.md").unlink()
        self.assertTrue(any("缺少读者文档" in x for x in self.errors()))

    def test_machine_fields_and_test_output_do_not_become_reader_body(self) -> None:
        for body in ["run_id: example", "```json\n{}\n```", "27 passed"]:
            with self.subTest(body=body):
                (self.docs / "项目技术说明.md").write_text(body, encoding="utf-8")
                self.assertTrue(any("不得进入读者正文" in x for x in self.errors()))

    def test_reader_does_not_accept_frontmatter_machine_identity(self) -> None:
        (self.docs / "项目技术说明.md").write_text(
            "---\nobject_id: technical-description\n---\n\n# 技术说明\n实际问题及方案。",
            encoding="utf-8",
        )
        self.assertTrue(any("frontmatter" in x for x in self.errors()))

    def test_not_started_requires_only_honest_navigation(self) -> None:
        self.policy["delivery_state"] = "not_started"
        self.save()
        for name in self.names:
            if name != "README.md":
                (self.docs / name).unlink()
        (self.docs / "README.md").write_text("# 导航\n正文尚未建立。", encoding="utf-8")
        self.assertEqual(self.errors(), [])
        (self.docs / "README.md").write_text("# 项目已经全部完成", encoding="utf-8")
        self.assertTrue(any("明确尚未建立" in x for x in self.errors()))

    def test_extra_api_document_is_not_another_current_entry(self) -> None:
        (self.docs / "api.md").write_text("# 另一个当前接口正文", encoding="utf-8")
        self.assertTrue(any("明确对象归属" in x for x in self.errors()))

    def test_unselected_release_and_templates_are_not_empty_requirements(self) -> None:
        registry = self.root / "configs/features.yaml"
        data = json.loads(registry.read_text(encoding="utf-8"))
        data["allowed_engineering_top_level"] = ["configs", "docs", "scripts"]
        registry.write_text(json.dumps(data), encoding="utf-8")
        (self.root / "scripts").mkdir()
        (self.root / "configs/skill-promotion.yaml").write_text("{}", encoding="utf-8")
        records = self.root.parent / "records"
        records.mkdir()
        cfg = {
            "feature_registry": "engineering/configs/features.yaml",
            "project_management_root": "records",
            "scripts_root": "engineering/scripts",
            "release_root": "engineering/release",
            "skill_promotion_registry": "engineering/configs/skill-promotion.yaml",
            "templates_dir": "templates",
            "project_skills_root": "engineering/.codex/skills",
        }
        self.assertEqual(
            self.module.validate_layout(self.root.parent, cfg, self.root), []
        )
        self.assertEqual(self.module.validate_documents(self.root.parent, cfg), [])
        cfg["release_manifest"] = "engineering/release/manifest.json"
        self.assertTrue(
            any(
                "已声明发布产物" in x
                for x in self.module.validate_layout(self.root.parent, cfg, self.root)
            )
        )

    def test_exact_legacy_source_pin_remains_readonly(self) -> None:
        import hashlib

        path = self.docs / "api.md"
        path.write_text("# 旧接口来源\nrun_id: old", encoding="utf-8")
        self.policy["pinned_paths"] = {
            "docs/api.md": hashlib.sha256(path.read_bytes()).hexdigest()
        }
        self.save()
        self.assertEqual(self.errors(), [])
        path.write_text("改写旧来源", encoding="utf-8")
        self.assertTrue(any("来源绑定改变" in x for x in self.errors()))


class AchievementFolderOwnershipTests(unittest.TestCase):
    """新增成果先有文件夹归属。旧精确文件原位兼容。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.engineering = self.repo / "projectname/project"
        (self.engineering / "configs").mkdir(parents=True)
        self.home = self.repo / "projectname/achieve/07-成果表达"
        self.module = (
            globals()["GOVERNANCE"]
            if "GOVERNANCE" in globals()
            else globals()["load_module"]()
        )
        self.spec = {
            "path": "../achieve/07-成果表达",
            "entry_filenames": ["README.md"],
            "baseline_paths": [],
            "folders": {
                "专题成果": {
                    "purpose": "同类成果",
                    "object_entry_filenames": ["README.md"],
                    "object_child_folders": {
                        "可编辑源": "完整可编辑源",
                        "figures": "对象图",
                        "附件": "用户要求的附件",
                    },
                }
            },
        }
        self.policy = {
            "enabled": True,
            "roots": [self.spec],
            "rejected_types": ["修改说明", "逐句对照", "编译检查"],
        }
        self.save()

    def save(self) -> None:
        (self.engineering / "configs/features.yaml").write_text(
            json.dumps({"achievement_layout": self.policy}, ensure_ascii=False),
            encoding="utf-8",
        )

    def put(self, relative: str) -> Path:
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("实际材料", encoding="utf-8")
        return path

    def errors(self) -> list[str]:
        return self.module.validate_achievement_layout(self.engineering)

    def test_missing_classifications_do_not_create_empty_directories(self) -> None:
        self.assertEqual(self.errors(), [])
        self.assertFalse(self.home.exists())
        self.put("README.md")
        self.assertEqual(self.errors(), [])
        self.assertFalse((self.home / "专题成果").exists())

    def test_new_loose_file_at_root_is_rejected(self) -> None:
        self.put("新报告.pdf")
        self.assertTrue(any("散放" in e for e in self.errors()))

    def test_object_source_tree_and_requested_qa_keep_their_ownership(self) -> None:
        for relative in [
            "专题成果/稳定研究对象/report.pdf",
            "专题成果/稳定研究对象/可编辑源/chapters/main.tex",
            "专题成果/稳定研究对象/figures/result.png",
            "专题成果/稳定研究对象/用户专项-问答稿.md",
            "专题成果/稳定研究对象/附件/独立评审.md",
        ]:
            self.put(relative)
        self.assertEqual(self.errors(), [])

    def test_unknown_folder_and_deeper_child_are_rejected(self) -> None:
        self.put("未登记类别/对象/稿件.docx")
        self.put("专题成果/稳定对象/未登记深层/extra/file.pdf")
        errors = self.errors()
        self.assertTrue(any("分类归属" in e for e in errors))
        self.assertTrue(any("未知深层" in e for e in errors))

    def test_explicit_object_child_override_accepts_existing_package(self) -> None:
        self.spec["folders"]["专题成果"]["objects"] = {
            "当前稿": {"child_folders": {"chapters": "章节源", "fonts": "必要字体"}}
        }
        self.save()
        self.put("专题成果/当前稿/chapters/chapter.tex")
        self.put("专题成果/当前稿/fonts/font.ttf")
        self.assertEqual(self.errors(), [])
        self.put("专题成果/其他稿/chapters/chapter.tex")
        self.assertTrue(any("未知深层" in e for e in self.errors()))

    def test_process_artifacts_are_not_another_public_result(self) -> None:
        self.put("专题成果/稳定对象/本轮-修改说明.md")
        self.put("专题成果/稳定对象/可编辑源/report.log")
        self.assertTrue(any("过程稿或编译证据" in e for e in self.errors()))

    def test_precise_legacy_files_do_not_exempt_the_whole_folder(self) -> None:
        self.put("旧目录/原稿.md")
        self.spec["baseline_paths"] = ["旧目录/原稿.md"]
        self.save()
        self.assertEqual(self.errors(), [])
        self.put("旧目录/新稿.md")
        self.assertTrue(any("分类归属" in e for e in self.errors()))

    def test_agent_or_date_is_not_a_stable_object(self) -> None:
        self.put("专题成果/MB-X01/稿件.pdf")
        self.put("专题成果/20261030-临时任务/稿件.pdf")
        self.assertTrue(any("日期任务或Agent" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
