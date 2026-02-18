#!/usr/bin/env python
"""快速验证脚本：读取最近10行数据 + 运行规则引擎"""
import sys
from pathlib import Path
import pandas as pd
import traceback

# =============== 配置区（按需修改）===============
DATA_PATH = Path("../data/reddit_cc.csv")  # 相对 scripts/ 的路径
TEXT_COLUMN = "body"  # 假设你要分析的是标题列，请根据实际情况修改
# ==============================================

try:
    # 1. 读取数据（自动处理常见编码）
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    print(f"✅ 成功加载 {len(df)} 行数据 | 列: {list(df.columns)}\n")

    # 2. 取最后10行
    test_data = df.tail(10)
    print("=" * 50)
    print("🔍 输入数据预览（前10行）:")
    print("=" * 50)
    print(test_data[[TEXT_COLUMN]].to_string(index=False) if TEXT_COLUMN in test_data.columns else test_data.head())
    print()

    # 3. 【关键】数据清洗：确保传入的是有效的字符串数据
    print("=" * 50)
    print("🧹 数据清洗中...")
    print("=" * 50)

    # 检查目标列是否存在
    if TEXT_COLUMN not in test_data.columns:
        print(f"⚠️ 警告: 找不到 '{TEXT_COLUMN}' 列，可用列: {list(test_data.columns)}")
        TEXT_COLUMN = input("请输入要分析的文本列名: ").strip()

    # 填充 NaN 和 None
    test_data = test_data.copy()
    test_data[TEXT_COLUMN] = test_data[TEXT_COLUMN].fillna("")

    # 转换为字符串
    test_data[TEXT_COLUMN] = test_data[TEXT_COLUMN].astype(str)

    # 移除空字符串（可选）
    original_len = len(test_data)
    test_data = test_data[test_data[TEXT_COLUMN].str.strip() != ""]
    filtered_len = len(test_data)

    print(f"✅ 清洗完成: 原始 {original_len} 行 → 有效 {filtered_len} 行")
    if filtered_len < original_len:
        print(f"   （过滤了 {original_len - filtered_len} 条空数据）")
    print()

    # 4. 运行引擎
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from crypto_go.CryptoRuleEngine import CryptoRuleEngine

    print("=" * 50)
    print("⚙️  运行规则引擎...")
    print("=" * 50)

    engine = CryptoRuleEngine()

    # 尝试调用并捕获详细错误
    try:
        result = engine.calculate_sentiment(test_data)
    except Exception as e:
        print(f"\n❌ 引擎执行出错:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        print(f"\n🔍 详细堆栈:")
        traceback.print_exc()
        print(f"\n💡 建议: 检查 CryptoRuleEngine.calculate_sentiment 的输入要求")
        sys.exit(1)

    # 5. 输出结果
    print("\n" + "=" * 50)
    print("🎯 规则引擎输出:")
    print("=" * 50)
    if hasattr(result, "head"):
        print(result.head(15))
    else:
        print(result)

    print(f"\n💡 共返回 {len(result) if hasattr(result, '__len__') else '未知'} 条结果 | 类型: {type(result).__name__}")

except Exception as e:
    print(f"\n❌ 执行出错: {type(e).__name__}: {e}")
    print("\n🔍 详细堆栈:")
    traceback.print_exc()
    sys.exit(1)