"""F002 的最小回归测试。"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ENGINEERING_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ENGINEERING_ROOT.parents[1]
MODULE_PATH = ENGINEERING_ROOT / "scripts" / "f002_skill_promotion_audit.py"


def load_module() -> object:
    """从工程脚本目录加载待测模块。"""
    specification = importlib.util.spec_from_file_location("f002_skill_promotion_audit", MODULE_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("无法加载 F002")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class SkillPromotionAuditTests(unittest.TestCase):
    """验证空登记保持项目级状态且不执行全局安装。"""

    def test_empty_promotion_registry_passes(self) -> None:
        """没有候选 Skill 时审计应成功并保持只读。"""
        module = load_module()
        self.assertEqual(module.run(PROJECT_ROOT), 0)


if __name__ == "__main__":
    unittest.main()
