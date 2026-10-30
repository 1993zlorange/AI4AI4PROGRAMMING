"""F001 项目治理校验器：只读检查功能登记、归属、命名和文档模板链路。"""

# 人类可读 CLI 文本保留中文；该例外不影响被检查项目文件。

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import tomllib

CONFIG_PATTERN = re.compile(r"```project-supervision\s*\n(.*?)\n```", re.DOTALL)
DATE_DOCUMENT_PATTERN = re.compile(r"^\d{8}-.+-.+\.[A-Za-z0-9]+$")
FIXED_DOCUMENT_NAMES = {
    "AGENTS.md",
    "README.md",
    "PROGRAMMING_STANDARDS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "package.json",
    "SKILL.md",
    "openai.yaml",
    ".gitignore",
    ".editorconfig",
    ".env.example",
}
IGNORED_PARTS = {".git", ".venv", "node_modules", "__pycache__", "output"}


class GovernanceValidationError(ValueError):
    """表示项目治理配置或登记无法安全读取。"""


def parse_args() -> argparse.Namespace:
    """解析显式项目根；工具只读，保留 --check 作为统一入口。"""
    parser = argparse.ArgumentParser(description="F001 项目治理只读校验器")
    parser.add_argument(
        "--project-root", type=Path, required=True, help="包含根级 AGENTS.md 的项目根"
    )
    parser.add_argument("--check", action="store_true", help="执行只读检查")
    return parser.parse_args()


def load_project_config(project_root: Path) -> dict[str, object]:
    """从根级 AGENTS 读取 project-supervision TOML 配置。"""
    agents_path = project_root / "AGENTS.md"
    text = agents_path.read_text(encoding="utf-8")
    match = CONFIG_PATTERN.search(text)
    if match is None:
        raise GovernanceValidationError(
            "根级 AGENTS.md 缺少 project-supervision 配置块"
        )
    try:
        value = tomllib.loads(match.group(1))
    except tomllib.TOMLDecodeError as exc:
        raise GovernanceValidationError(
            f"project-supervision 配置无法解析：{exc}"
        ) from exc
    return value


def resolve_inside(root: Path, value: object, field_name: str) -> Path:
    """将配置相对路径解析并限制在项目根内。"""
    if not isinstance(value, str) or not value.strip():
        raise GovernanceValidationError(f"配置字段 {field_name} 缺失")
    candidate = Path(value)
    if candidate.is_absolute():
        raise GovernanceValidationError(f"配置字段 {field_name} 必须使用相对路径")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise GovernanceValidationError(f"配置字段 {field_name} 越出项目根") from exc
    return resolved


def load_json_file(path: Path, label: str) -> dict[str, Any]:
    """读取 JSON 兼容 YAML，避免引入 YAML 运行时依赖。"""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GovernanceValidationError(f"无法读取 {label}：{exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceValidationError(f"{label} 根节点必须是对象")
    return value


def is_within(root: Path, candidate: Path) -> bool:
    """返回候选路径是否位于根目录以内。"""
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def relative_paths(
    value: object, label: str, engineering_root: Path
) -> tuple[list[Path], list[str]]:
    """验证工程相对路径列表并返回解析路径。"""
    if not isinstance(value, list) or not value:
        return [], [f"{label} 必须是非空路径数组"]
    paths: list[Path] = []
    errors: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label} 包含无效路径")
            continue
        path = Path(item)
        if path.is_absolute() or not is_within(
            engineering_root, engineering_root / path
        ):
            errors.append(f"{label} 越出工程根：{item}")
            continue
        paths.append((engineering_root / path).resolve())
    return paths, errors


def validate_features(
    project_root: Path, config: dict[str, object]
) -> tuple[list[str], Path]:
    """验证功能三元组、路径存在性和功能文件登记。"""
    engineering_root = resolve_inside(
        project_root, config.get("engineering_root"), "engineering_root"
    )
    registry_path = resolve_inside(
        project_root, config.get("feature_registry"), "feature_registry"
    )
    registry = load_json_file(registry_path, "功能登记")
    required = registry.get("required_fields")
    features = registry.get("features")
    if not isinstance(required, list) or not isinstance(features, list):
        return [
            "功能登记必须包含 required_fields 数组和 features 数组"
        ], engineering_root
    id_pattern = re.compile(str(registry.get("feature_id_pattern", r"F\d{3}")))
    code_pattern = re.compile(
        str(registry.get("feature_code_pattern", r"[A-Z][A-Z0-9_]+"))
    )
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    registered_files: set[Path] = set()
    errors: list[str] = []
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            errors.append(f"features[{index}] 必须是对象")
            continue
        missing = [field for field in required if not feature.get(field)]
        if missing:
            errors.append(
                f"features[{index}] 缺少字段：{', '.join(str(item) for item in missing)}"
            )
        feature_id = str(feature.get("feature_id", ""))
        feature_code = str(feature.get("feature_code", ""))
        if not id_pattern.fullmatch(feature_id):
            errors.append(f"features[{index}] feature_id 格式错误：{feature_id}")
        if not code_pattern.fullmatch(feature_code):
            errors.append(f"features[{index}] feature_code 格式错误：{feature_code}")
        if feature_id in seen_ids:
            errors.append(f"重复 feature_id：{feature_id}")
        if feature_code in seen_codes:
            errors.append(f"重复 feature_code：{feature_code}")
        seen_ids.add(feature_id)
        seen_codes.add(feature_code)
        implementation_paths, path_errors = relative_paths(
            feature.get("implementation_paths"),
            f"features[{index}].implementation_paths",
            engineering_root,
        )
        test_paths, test_errors = relative_paths(
            feature.get("test_paths"), f"features[{index}].test_paths", engineering_root
        )
        errors.extend(path_errors + test_errors)
        for path in implementation_paths + test_paths:
            if not path.exists():
                errors.append(
                    f"features[{index}] 登记路径不存在：{path.relative_to(engineering_root).as_posix()}"
                )
            registered_files.add(path)
    extensions = {str(value) for value in registry.get("functional_extensions", [])}
    for root_name in ("apps", "packages", "scripts", "database"):
        source_root = engineering_root / root_name
        if not source_root.exists():
            continue
        for path in source_root.rglob("*"):
            if (
                not path.is_file()
                or path.suffix not in extensions
                or any(part in IGNORED_PARTS for part in path.parts)
            ):
                continue
            if path.resolve() not in registered_files:
                errors.append(
                    f"功能性文件未登记功能三元组：{path.relative_to(engineering_root).as_posix()}"
                )
    return errors, engineering_root


def validate_layout(
    project_root: Path, config: dict[str, object], engineering_root: Path
) -> list[str]:
    """检查工程顶层目录允许列表和必要治理资产。"""
    errors: list[str] = []
    registry_path = resolve_inside(
        project_root, config.get("feature_registry"), "feature_registry"
    )
    registry = load_json_file(registry_path, "功能登记")
    allowed = registry.get("allowed_engineering_top_level")
    if not isinstance(allowed, list) or not all(
        isinstance(item, str) for item in allowed
    ):
        return ["功能登记缺少 allowed_engineering_top_level 字符串数组"]
    allowed_names = set(allowed)
    for child in engineering_root.iterdir():
        if (
            child.is_dir()
            and child.name not in allowed_names
            and not child.name.startswith(".")
        ):
            errors.append(f"未登记工程顶层目录：{child.name}")
    for field_name in (
        "project_management_root",
        "scripts_root",
        "skill_promotion_registry",
    ):
        path = resolve_inside(project_root, config.get(field_name), field_name)
        if not path.exists():
            errors.append(
                f"配置目标不存在：{field_name} -> {path.relative_to(project_root).as_posix()}"
            )
    release = resolve_inside(project_root, config.get("release_root"), "release_root")
    if release.exists() and not release.is_dir():
        errors.append("发布位置不是目录")
    if config.get("release_manifest"):
        manifest = resolve_inside(
            project_root, config["release_manifest"], "release_manifest"
        )
        if not release.is_dir() or not manifest.is_file():
            errors.append("已声明发布产物或清单不存在")
    return errors


def validate_documents(project_root: Path, config: dict[str, object]) -> list[str]:
    """检查项目级文档命名和文档型 Skill 的模板链路。"""
    errors: list[str] = []
    management_root = resolve_inside(
        project_root, config.get("project_management_root"), "project_management_root"
    )
    templates_root = resolve_inside(
        management_root, config.get("templates_dir"), "templates_dir"
    )
    skills_root = resolve_inside(
        project_root, config.get("project_skills_root"), "project_skills_root"
    )
    # 模板目录只在实际项目Skill需要具体模板时建立，不为空结构强建。
    if skills_root.exists():
        for skill_file in skills_root.rglob("SKILL.md"):
            content = skill_file.read_text(encoding="utf-8")
            if "## 文档输出" not in content:
                continue
            assets = skill_file.parent / "assets"
            if not assets.is_dir() or not any(assets.iterdir()):
                errors.append(
                    f"文档型项目 Skill 缺少 assets 模板：{skill_file.relative_to(project_root).as_posix()}"
                )
            if "assets/" not in content:
                errors.append(
                    f"文档型项目 Skill 未引用模板路径：{skill_file.relative_to(project_root).as_posix()}"
                )
    for path in management_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".html"}:
            continue
        if path.name in FIXED_DOCUMENT_NAMES or path.parent == templates_root:
            continue
        if not DATE_DOCUMENT_PATTERN.fullmatch(path.name):
            errors.append(
                f"项目管理文档未采用日期化命名：{path.relative_to(project_root).as_posix()}"
            )
    return errors


def record_metadata(text: str) -> dict[str, str]:
    """读取日记录使用的简单标量 frontmatter，不执行 YAML 对象。"""
    if not text.startswith("---\n"):
        return {}
    front, separator, _ = text[4:].partition("\n---")
    if not separator:
        return {}
    result: dict[str, str] = {}
    for line in front.splitlines():
        key, colon, value = line.partition(":")
        if colon and re.fullmatch(r"[a-z_]+", key.strip()):
            result[key.strip()] = value.strip().strip("\"'")
    return result


def record_aliases(policy: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    """将同用途类型归一；配置中同一别名不能指向两个类型。"""
    aliases: dict[str, str] = {}
    errors: list[str] = []
    types = policy.get("types", {})
    if not isinstance(types, dict):
        return {}, ["record_policy.types 必须是对象"]
    for canonical, item in types.items():
        if not isinstance(item, dict):
            errors.append(f"记录类型配置无效：{canonical}")
            continue
        values = [canonical, item.get("label", "")] + list(item.get("aliases", []))
        for alias in values:
            if not isinstance(alias, str) or not alias:
                continue
            previous = aliases.setdefault(alias.casefold(), canonical)
            if previous != canonical:
                errors.append(f"记录类型别名冲突：{alias}")
    return aliases, errors


def artifact_target(project_root: Path, reference: str) -> tuple[Path, str]:
    """把文件与锚点分开解析，并拒绝越出当前项目。"""
    relative, _, anchor = reference.partition("#")
    return resolve_inside(project_root, relative, "current_artifacts"), anchor


def validate_current_artifacts(project_root: Path, policy: dict[str, Any]) -> list[str]:
    """每种当前成果只有一个可解析目标，既有历史链接不在此补写。"""
    entries = policy.get("current_artifacts", {})
    if not isinstance(entries, dict):
        return ["record_policy.current_artifacts 必须是对象"]
    errors: list[str] = []
    for kind, reference in entries.items():
        if not isinstance(reference, str) or not reference.strip():
            errors.append(f"当前成果入口必须为唯一相对路径：{kind}")
            continue
        target, anchor = artifact_target(project_root, reference)
        if not target.is_file():
            errors.append(f"当前成果入口不存在：{kind} -> {reference}")
        elif anchor:
            text = target.read_text(encoding="utf-8-sig")
            if not re.search(r"id=[\"\']" + re.escape(anchor) + r"[\"\']", text):
                errors.append(f"当前成果入口锚点不存在：{reference}")
    return errors


def recorded_day(value: str) -> str:
    """由带时区时间取得上海记录日，不依赖执行主机本地时区。"""
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.utcoffset() is None:
        raise ValueError("记录时间缺少时区")
    return moment.astimezone(timezone(timedelta(hours=8))).date().isoformat()


RESEARCH_KINDS = {
    "literature",
    "method",
    "performance",
    "analysis",
    "writing",
    "research_blocker",
}
GUIDE_QUESTION_LIMITS = {1: 14, 2: 16, 3: 17, 4: 14, 5: 14, 6: 15, 7: 14}
ENGINEERING_PROCESS = re.compile(
    r"pytest|\bruff\b|\bmypy\b|代码正确性|工程检查|单元测试|静态检查|语法检查|"
    r"需求登记|登记需求|角色交接|流程登记|哈希核对|校验和对账|"
    r"(?:建立|生成|创建)(?:工作契约|成果卡|管理报告)|(?:测试|检查)通过数",
    re.IGNORECASE,
)


def meaningful_research_value(value: object) -> bool:
    """只判断字段真实可读，不能以字段齐全代替科学真实性判断。"""
    if isinstance(value, str):
        cleaned = value.strip()
        return (
            bool(cleaned)
            and cleaned
            not in {"待填写", "待补充", "TODO", "暂无", "无科研变化", "无科研进展"}
            and not re.fullmatch(r"<[^>]*>", cleaned)
        )
    if isinstance(value, list):
        return bool(value) and all(meaningful_research_value(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(
            meaningful_research_value(item) for item in value.values()
        )
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_research_reference(
    project_root: Path, reference: object, label: str
) -> list[str]:
    """科研日志来源限定为项目内真实文件，锚点有值时也须可定位。"""
    if not isinstance(reference, str) or not reference.strip():
        return [f"科研日志{label}须提供真实来源"]
    try:
        return validate_current_artifacts(
            project_root, {"current_artifacts": {label: reference}}
        )
    except (GovernanceValidationError, UnicodeError, OSError) as exc:
        return [f"科研日志{label}来源无效：{exc}"]


def validate_research_log_entry(
    project_root: Path, entry: dict[str, Any], policy: dict[str, Any]
) -> list[str]:
    """科研派生日志按组会问题合同检查；普通软件日志不受本合同约束。"""
    identity = str(entry.get("entry_id", ""))
    errors: list[str] = []
    contract = policy.get("log_contract", "group-meeting/1.0")
    if contract != "group-meeting/1.0" or entry.get("report_contract") != contract:
        errors.append(f"科研日志缺少group-meeting/1.0合同：{identity}")
    if entry.get("work_kind") not in RESEARCH_KINDS:
        errors.append(f"科研日志work_kind不是研究工作类型：{identity}")
    required = (
        "research_point",
        "research_source",
        "research_question",
        "actions",
        "result",
        "interpretation",
        "limitations",
        "next_step",
        "evidence",
    )
    for field in required:
        value = entry.get(field)
        readable = meaningful_research_value(value)
        if field != "evidence":
            readable = isinstance(value, str) and readable
        if not readable:
            errors.append(f"科研日志缺少真实{field}：{identity}")
    errors.extend(
        validate_research_reference(
            project_root, entry.get("research_source"), "research_source"
        )
    )
    questions = entry.get("guide_questions")
    if not isinstance(questions, list) or not questions:
        errors.append(f"科研日志缺少guide_questions两层映射：{identity}")
    else:
        for question in questions:
            match = (
                re.fullmatch(r"4\.([1-7])\.Q([1-9]\d*)", question)
                if isinstance(question, str)
                else None
            )
            if (
                match is None
                or int(match.group(2)) > GUIDE_QUESTION_LIMITS[int(match.group(1))]
            ):
                errors.append(f"科研日志guide_questions题号无效：{identity}")
    evidence = entry.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"科研日志evidence须为非空来源数组：{identity}")
    else:
        for reference in evidence:
            errors.extend(
                validate_research_reference(project_root, reference, "evidence")
            )
    if entry.get("work_kind") in {"performance", "analysis"}:
        for field in ("comparison_conditions", "metrics"):
            value = entry.get(field)
            if not isinstance(value, str) or not meaningful_research_value(value):
                errors.append(f"性能/分析日志缺少非空字符串{field}：{identity}")
    return errors


def validate_daily_records(project_root: Path, config: dict[str, object]) -> list[str]:
    """F001: 校验当前日记录的唯一落点、条目身份与真实记录日。"""
    registry = load_json_file(
        resolve_inside(
            project_root,
            config.get("record_policy_registry", config.get("feature_registry")),
            "record_policy_registry",
        ),
        "日记录配置",
    )
    policy = registry.get("record_policy")
    if policy is None:
        return []
    if not isinstance(policy, dict):
        return ["record_policy 必须是对象"]
    aliases, errors = record_aliases(policy)
    try:
        effective = date.fromisoformat(str(policy["effective_date"]))
    except (KeyError, ValueError):
        return errors + ["record_policy.effective_date 必须为真实日期"]
    if policy.get("timezone") != "Asia/Shanghai" or not policy.get("project_id"):
        errors.append("日记录配置必须声明project_id与Asia/Shanghai时区")
    errors.extend(validate_current_artifacts(project_root, policy))
    types = policy.get("types", {})
    if not isinstance(types, dict):
        return errors
    legacy_values = policy.get("legacy_paths", [])
    if not isinstance(legacy_values, list):
        return errors + ["legacy_paths必须为精确历史文件数组"]
    legacy_paths: list[Path] = []
    for item in legacy_values:
        old = resolve_inside(project_root, item, "legacy_paths")
        if not old.is_file():
            errors.append(
                f"legacy_paths仅允许存在的精确文件，不能豁免目录或未来新稿：{item}"
            )
        else:
            legacy_paths.append(old)
    minimal = policy.get("process_record_profile") == "minimal"
    enabled = policy.get("enabled_daily_types", ["requirement", "log"])
    if minimal and (
        not isinstance(enabled, list) or set(enabled) != {"requirement", "log"}
    ):
        return errors + ["minimal模式仅允许requirement和log两类日记录"]
    try:
        minimal_date = date.fromisoformat(
            str(policy.get("minimal_records_effective_date", "2026-10-30"))
        )
    except ValueError:
        return errors + ["minimal_records_effective_date必须为真实日期"]
    # 仅专用过程目录按位置判断；契约/交接可能共用正式03/04目录，不能封锁整个成果目录。
    disabled_directories = {
        resolve_inside(project_root, item.get("directory"), "record_type.directory")
        for kind, item in types.items()
        if minimal
        and kind in {"supervision", "reflection", "change", "cost", "quality"}
        and kind not in enabled
    }
    process_report_names = re.compile(
        r"监督(?:记录|报告|简报)|工作契约|交接(?:书|记录|报告)|"
        r"(?:质量|成本|变更|反思)(?:检查|统计)?(?:记录|报告)|管理报告"
    )
    targets: dict[tuple[str, str, str], Path] = {}
    entry_ids: set[str] = set()
    events: set[tuple[str, str, str]] = set()
    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project_root)
        if any(
            part in (IGNORED_PARTS - {"output"}) | {"release"}
            for part in relative.parts
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeError:
            # 非文本原件/媒体不是可编辑日记录；其来源由正式交付入口管理。
            continue
        metadata = record_metadata(text)
        schema = metadata.get("schema_version", "")
        declared = schema.startswith("daily-record/")
        # output仅豁免原始运行对象；显式日记录不能通过藏入trace目录拆分。
        if "output" in relative.parts and not declared:
            continue
        registered_legacy = path.resolve() in legacy_paths
        date_match = re.match(r"^(\d{8})-", path.name)
        inferred = next(
            (
                canonical
                for alias, canonical in sorted(
                    aliases.items(), key=lambda pair: -len(pair[0])
                )
                if path.stem.casefold() == alias
                or path.stem.casefold().endswith("-" + alias)
            ),
            None,
        )
        if minimal and not registered_legacy and not declared:
            try:
                candidate_day = (
                    datetime.strptime(date_match.group(1), "%Y%m%d")
                    .replace(tzinfo=timezone.utc)
                    .date()
                    if date_match
                    else None
                )
            except ValueError:
                candidate_day = None
            heading = next(
                (line for line in text.splitlines() if line.startswith("# ")), ""
            )
            disabled_home = any(
                path.resolve().is_relative_to(home) for home in disabled_directories
            )
            renamed_process = process_report_names.search(path.stem + " " + heading)
            new_or_undated = candidate_day is None or candidate_day >= minimal_date
            if new_or_undated and (
                (inferred is not None and inferred not in enabled)
                or disabled_home
                or renamed_process
            ):
                errors.append(
                    f"精简模式停用独立过程成稿，不能改名报告逃逸：{relative.as_posix()}"
                )
        if not declared:
            if not inferred:
                continue
            if not date_match:
                if not registered_legacy:
                    errors.append(
                        f"已识别记录类型缺少规范日期且未登记历史来源：{relative.as_posix()}"
                    )
                continue
            try:
                dated = (
                    datetime.strptime(date_match.group(1), "%Y%m%d")
                    .replace(tzinfo=timezone.utc)
                    .date()
                )
            except ValueError:
                errors.append(f"日记录日期无效：{relative.as_posix()}")
                continue
            if dated < effective or registered_legacy:
                continue
            errors.append(
                f"启用后的记录缺少daily-record/1.0元数据：{relative.as_posix()}"
            )
            continue
        if schema != "daily-record/1.0":
            errors.append(f"不支持的日记录schema：{relative.as_posix()}")
            continue
        canonical = aliases.get(
            metadata.get(
                "record_type", metadata.get("canonical_record_type", "")
            ).casefold()
        )
        if canonical is None:
            errors.append(f"未知日记录类型：{relative.as_posix()}")
            continue
        try:
            day = date.fromisoformat(metadata.get("record_date", "")).isoformat()
        except ValueError:
            errors.append(f"日记录日期无效：{relative.as_posix()}")
            continue
        if (
            metadata.get("timezone") != "Asia/Shanghai"
            or metadata.get("project_id") != policy.get("project_id")
            or metadata.get("record_profile") != policy.get("profile")
        ):
            errors.append(f"日记录项目/时区/profile与配置不一致：{relative.as_posix()}")
        archived = metadata.get("record_state") == "archived"
        if archived and not registered_legacy:
            errors.append(
                f"归档日记录未登记精确历史原件，不能自标归档豁免：{relative.as_posix()}"
            )
        readonly = (archived and registered_legacy) or bool(
            metadata.get("derived_from")
        )
        if metadata.get("derived_from"):
            source, _ = artifact_target(project_root, metadata["derived_from"])
            if not source.is_file() or source.resolve() == path.resolve():
                errors.append(f"日记录导出来源无效：{relative.as_posix()}")
            else:
                source_metadata = record_metadata(
                    source.read_text(encoding="utf-8-sig")
                )
                source_type = aliases.get(
                    source_metadata.get("record_type", "").casefold()
                )
                if (
                    source_metadata.get("schema_version") != "daily-record/1.0"
                    or source_metadata.get("derived_from")
                    or source_type != canonical
                    or source_metadata.get("record_date") != day
                    or source_metadata.get("project_id") != metadata.get("project_id")
                    or source_metadata.get("record_profile")
                    != metadata.get("record_profile")
                ):
                    errors.append(f"日记录导出来源身份不匹配：{relative.as_posix()}")
        research_contract = False
        if canonical == "log" and policy.get("profile") == "research":
            try:
                contract_start = date.fromisoformat(
                    str(policy.get("log_contract_effective_date", "2026-10-30"))
                )
                research_contract = date.fromisoformat(day) >= contract_start
            except ValueError:
                errors.append("科研日志合同启用日无效")
            if (
                research_contract
                and not (archived and registered_legacy)
                and ENGINEERING_PROCESS.search(text)
            ):
                errors.append(
                    f"科研日志正文或附录含工程检查/登记交接过程：{relative.as_posix()}"
                )
        if (
            minimal
            and date.fromisoformat(day) >= minimal_date
            and canonical not in enabled
            and not (archived and registered_legacy)
        ):
            errors.append(
                f"精简模式停用日记录类型：{canonical} / {relative.as_posix()}"
            )
        if readonly:
            continue
        definition = types[canonical]
        directory = resolve_inside(
            project_root, definition.get("directory"), "record_type.directory"
        )
        filename = f"{day.replace('-', '')}-{definition.get('filename_body')}-{definition.get('label')}.md"
        if path.resolve() != (directory / filename).resolve():
            errors.append(f"日记录不在唯一规范落点：{relative.as_posix()}")
        key = (str(policy["project_id"]), day, canonical)
        if key in targets:
            errors.append(
                f"同日同类型存在多个可写文件：{relative.as_posix()} / {targets[key].relative_to(project_root).as_posix()}"
            )
        targets[key] = path
        matches = re.findall(r"<!--\s*daily-entry\s+(\{.*?\})\s*-->", text, re.DOTALL)
        if not matches:
            errors.append(f"日记录没有真实独立条目：{relative.as_posix()}")
        for raw in matches:
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                errors.append(f"日记录条目JSON无效：{relative.as_posix()}")
                continue
            if not isinstance(entry, dict):
                errors.append(f"日记录条目不是对象：{relative.as_posix()}")
                continue
            if canonical == "log":
                if policy.get("profile") == "research" and research_contract:
                    errors.extend(
                        validate_research_log_entry(project_root, entry, policy)
                    )
                elif policy.get(
                    "profile"
                ) == "software" and not meaningful_research_value(
                    entry.get("requirement_id")
                ):
                    errors.append("软件日志条目须绑定需求/用户功能requirement_id")
            entry_id = entry.get("entry_id")
            if not isinstance(entry_id, str) or not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9_.:-]*", entry_id
            ):
                errors.append(f"日记录条目ID无效：{relative.as_posix()}")
                continue
            if entry_id in entry_ids:
                errors.append(f"重复日记录条目ID：{entry_id}")
            entry_ids.add(entry_id)
            anchor = "entry-" + entry_id
            if len(re.findall(r"id=[\"\']" + re.escape(anchor) + r"[\"\']", text)) != 1:
                errors.append(f"日记录条目锚点缺失或重复：{entry_id}")
            event = entry.get("event_key")
            if not isinstance(event, str) or not event:
                errors.append(f"日记录条目缺少event_key：{entry_id}")
            else:
                event_key = (canonical, event, str(entry.get("attempt_id", "")))
                if event_key in events:
                    errors.append(f"重复日记录事件：{event}")
                events.add(event_key)
            try:
                if recorded_day(str(entry.get("recorded_at", ""))) != day:
                    errors.append(f"日记录条目记录日不一致：{entry_id}")
                if entry.get("occurred_at"):
                    recorded_day(str(entry["occurred_at"]))
            except ValueError:
                errors.append(f"日记录条目时间无效：{entry_id}")
    return errors


def validate_technical_documents(engineering_root: Path) -> list[str]:
    """检查当前技术对象归属及精确来源绑定，不评价科学结论。"""
    import hashlib

    registry = next(
        (
            engineering_root / name
            for name in ("configs/features.yaml", "config/feature-registry.yaml")
            if (engineering_root / name).is_file()
        ),
        None,
    )
    if registry is None:
        return []
    policy = json.loads(registry.read_text(encoding="utf-8-sig")).get(
        "technical_documents", {}
    )
    if not policy.get("enabled"):
        return []
    root = engineering_root.resolve()
    home = (root / policy.get("root", "docs")).resolve()
    if not home.is_relative_to(root):
        return ["技术文档目录越界"]
    errors = []
    reader = policy.get("profile") == "reader"
    reader_entries = {
        "README.md",
        "项目技术说明.md",
        "使用指南.md",
        "结果说明与适用范围.md",
    }
    if reader:
        if set(policy.get("root_entries", [])) != reader_entries:
            errors.append("读者文档入口必须是规定的四份文档")
        state = policy.get("delivery_state", "ready")
        if state not in {"ready", "not_started"}:
            errors.append("读者文档交付状态无效")
        required = reader_entries if state == "ready" else {"README.md"}
        for filename in sorted(required):
            if not (home / filename).is_file():
                errors.append("缺少读者文档：" + filename)
        if state == "not_started" and (home / "README.md").is_file():
            navigation = (home / "README.md").read_text(encoding="utf-8-sig")
            if not any(word in navigation for word in ("尚未建立", "尚无", "未建立")):
                errors.append("未开始文档须在README明确尚未建立")
    pins = policy.get("pinned_paths", {})
    baseline = set(policy.get("baseline_paths", []))
    identities = set()
    for relative, expected in pins.items():
        source = (root / relative).resolve()
        if (
            not source.is_relative_to(home)
            or not source.is_file()
            or hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n") if policy.get("pin_hash_mode") == "text-lf" else source.read_bytes()).hexdigest() != expected
        ):
            errors.append("技术原件来源绑定改变或缺失：" + relative)
    for path in home.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(home):
            errors.append("技术文档链接越界：" + relative)
            continue
        if relative in pins or relative in baseline or path.name == ".gitkeep":
            continue
        local = path.relative_to(home)
        if (
            path.parent == home and path.name not in policy.get("root_entries", [])
        ) or (
            len(local.parts) > 1
            and local.parts[0] not in policy.get("stable_directories", [])
        ):
            errors.append("技术文档缺少明确对象归属：" + relative)
        if path.suffix in {".diff", ".txt"} or any(
            path.name.endswith("-" + kind + ".md")
            for kind in (
                "工作契约",
                "工程交付记录",
                "检查记录",
                "修订记录",
                "技术诊断",
                "工程复验记录",
                "源码记录",
            )
        ):
            errors.append("过程材料、补丁或源码快照不得进入当前docs：" + relative)
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8-sig")
            if reader:
                # 读者文档不使用机器元数据头。旧精确绑定原件已在前面排除。
                if re.match(r"\A---\s*\n.*?\n---\s*\n", text, re.DOTALL):
                    errors.append("读者正文不得包含frontmatter机器元数据：" + relative)
                body = re.sub(
                    r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL
                )
                machine_fields = re.search(
                    r"(?mi)^\s*(?:[-*]\s*)?(?:sha256|source_sha256|schema_version|run_id|entry_id|object_id|implementation_paths)\s*[:=|]",
                    body,
                )
                machine_block = re.search(
                    r"(?mi)^```(?:json|yaml|toml|python|jsonl)\s*$", body
                )
                process_output = re.search(
                    r"\b[0-9]+\s+passed\b|\b[0-9a-fA-F]{64}\b", body
                )
                if machine_fields or machine_block or process_output:
                    errors.append(
                        "机器字段、代码清单或检查成绩不得进入读者正文：" + relative
                    )
            if "daily-record/1.0" in text[:512]:
                errors.append("日记录不得进入docs：" + relative)
            for line in text[:1500].splitlines():
                if line.startswith("object_id:"):
                    identity = line.partition(":")[2].strip()
                    if identity in identities:
                        errors.append("技术对象存在多个当前正文：" + identity)
                    identities.add(identity)
    return errors


def validate_achievement_layout(engineering_root: Path) -> list[str]:
    """可选的新增成果归属检查。旧精确基线不迁移，不要求所有分类目录存在。"""
    registry = next(
        (
            engineering_root / name
            for name in ("configs/features.yaml", "config/feature-registry.yaml")
            if (engineering_root / name).is_file()
        ),
        None,
    )
    if registry is None:
        return []
    policy = json.loads(registry.read_text(encoding="utf-8-sig")).get(
        "achievement_layout", {}
    )
    if not policy.get("enabled"):
        return []
    repo = engineering_root.parent.parent.resolve()
    errors = []
    covered = set()
    process_suffixes = {
        ".diff",
        ".patch",
        ".log",
        ".aux",
        ".bcf",
        ".blg",
        ".toc",
        ".fls",
        ".fdb_latexmk",
    }
    for spec in policy.get("roots", []):
        home = (engineering_root / spec["path"]).resolve()
        if Path(spec["path"]).is_absolute() or not home.is_relative_to(repo):
            errors.append("成果归属根目录越界：" + str(spec["path"]))
            continue
        baseline = set(spec.get("baseline_paths", []))
        legacy_dirs = set()
        for relative in baseline:
            value = Path(relative)
            if (
                value.is_absolute()
                or not (home / value).resolve().is_relative_to(home)
                or any(c in relative for c in "*?[")
            ):
                errors.append("成果旧基线必须是精确相对文件：" + relative)
                continue
            legacy_dirs.update(
                parent.as_posix() for parent in value.parents if parent != Path(".")
            )
        folders = spec.get("folders", {})
        if not isinstance(folders, dict) or not all(
            isinstance(v, dict) and v.get("purpose") for v in folders.values()
        ):
            errors.append("成果分类必须声明唯一用途")
            continue
        if not home.exists():
            continue
        if not home.is_dir():
            errors.append("成果归属根不是文件夹：" + str(spec["path"]))
            continue
        for path in home.rglob("*"):
            relative = path.relative_to(home).as_posix()
            if path.is_symlink() or not path.resolve().is_relative_to(home):
                errors.append("成果链接越界或未经登记：" + relative)
                continue
            if path.is_file() and relative in baseline:
                continue
            parts = path.relative_to(home).parts
            if path.is_file():
                identity = path.resolve()
                if identity in covered:
                    errors.append("成果文件匹配多个受管根：" + relative)
                covered.add(identity)
            if len(parts) == 1:
                if path.is_file() and path.name not in spec.get(
                    "entry_filenames", ["README.md"]
                ):
                    errors.append("成果根目录不允许新文件散放：" + relative)
                elif (
                    path.is_dir()
                    and parts[0] not in folders
                    and relative not in legacy_dirs
                ):
                    errors.append("未知成果文件夹：" + relative)
                continue
            category = folders.get(parts[0])
            if category is None:
                if not path.is_dir() or relative not in legacy_dirs:
                    errors.append("文件没有成果分类归属：" + relative)
                continue
            if len(parts) == 2:
                if path.is_file() and path.name not in category.get(
                    "object_entry_filenames", ["README.md"]
                ):
                    errors.append("成果必须进入稳定对象文件夹：" + relative)
                elif (
                    path.is_dir()
                    and re.match(
                        r"(?i)^(?:(?:PI|MB|EX|CR)-[EPX][0-9]+|agent[0-9_-]*|task[-_].*|[0-9]{8}(?:[-_].*)?)$",
                        parts[1],
                    )
                    and relative not in legacy_dirs
                ):
                    errors.append("成果对象不能按日期任务或Agent分散：" + relative)
                continue
            if re.match(
                r"(?i)^(?:(?:PI|MB|EX|CR)-[EPX][0-9]+|agent[0-9_-]*|task[-_].*|[0-9]{8}(?:[-_].*)?)$",
                parts[1],
            ):
                errors.append("成果对象不能按日期任务或Agent分散：" + relative)
            if len(parts) >= 4 or (len(parts) == 3 and path.is_dir()):
                object_spec = category.get("objects", {}).get(parts[1], {})
                child_folders = object_spec.get(
                    "child_folders",
                    object_spec.get(
                        "object_child_folders", category.get("object_child_folders", {})
                    ),
                )
                if parts[2] not in child_folders:
                    errors.append("未知深层成果文件夹归属：" + relative)
            if path.is_file() and (
                path.suffix.lower() in process_suffixes
                or any(
                    path.stem == kind or path.stem.endswith("-" + kind)
                    for kind in policy.get("rejected_types", [])
                )
            ):
                errors.append("过程稿或编译证据不应新增到成果区：" + relative)
    return errors


def run(project_root: Path) -> int:
    """执行只读治理检查并返回稳定退出码。"""
    try:
        config = load_project_config(project_root)
        feature_errors, engineering_root = validate_features(project_root, config)
        errors = (
            feature_errors
            + validate_layout(project_root, config, engineering_root)
            + validate_documents(project_root, config)
            + validate_daily_records(project_root, config)
            + validate_technical_documents(engineering_root)
            + validate_achievement_layout(engineering_root)
        )
    except (GovernanceValidationError, OSError, UnicodeError, TypeError) as exc:
        errors = [str(exc)]
    for message in errors:
        print(f"ERROR: {message}")
    print(f"F001 治理校验完成：ERROR={len(errors)}")
    return 1 if errors else 0


def main() -> int:
    """解析参数并执行检查。"""
    args = parse_args()
    root = args.project_root.resolve()
    if not root.is_dir():
        print(f"ERROR: 项目根不存在：{root}")
        return 2
    return run(root)


if __name__ == "__main__":
    raise SystemExit(main())
