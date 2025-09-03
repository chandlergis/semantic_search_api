#!/usr/bin/env python3
"""
测试文档重复检测算法改进
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.document_compare import DocumentComparator

def test_duplicate_detection():
    """测试相同的段落是否能正确检测"""
    
    # 创建两个文档，第一段完全相同，后面不同
    doc_a = """本研究系统探讨了在人工智能（AI）技术浪潮下，企业人力资源管理（HRM）的转型策 略。研
究首先分析了 AI 在招聘、培训、绩效管理等核心 HR 职能中的应用现状与伦理挑战； 其次，
通过对不同规模、行业及地域文化背景下企业应用 AI-HRM 的差异性比较，揭示了转 型路径的
多样性。在此基础上，本研究提出了一个包含基础准备、试点实施、规模化推广与 战略优化
的四阶段转型框架，并设计了相应的差异化实施策略。通过对 500 家企业的模拟调 研数据进
行实证分析，研究发现 AI 应用能显著提升 HR 运营效率（平均提升约 45%）与决策 质量（平
均提升约 38%），但企业在技术集成、数据隐私和投资回报方面仍面临严峻挑战。 最后，研究
从政策、教育及产业协同的角度，提出了构建未来人力资源管理新生态的系统性 建议。本研
究旨在为企业在 AI 时代的 HRM 转型提供兼具理论深度与实践价值的指导框架。"""

    doc_b = """本研究系统探讨了在人工智能（AI）技术浪潮下，企业人力资源管理（HRM）的转型策 略。研
究首先分析了 AI 在招聘、培训、绩效管理等核心 HR 职能中的应用现状与伦理挑战； 其
次， 通过对不同规模、行业及地域文化背景下企业应用 AI-HRM 的差异性比较，揭示了转 型
路径的 多样性。在此基础上，本研究提出了一个包含基础准备、试点实施、规模化推广与 战
略优化 的四阶段转型框架，并设计了相应的差异化实施策略。通过对 500 家企业的模拟调
研数据进 行实证分析，研究发现 AI 应用能显著提升 HR 运营效率（平均提升约 45%）与决
策 质量（平 均提升约 38%），但企业在技术集成、数据隐私和投资回报方面仍面临严峻挑
战。 最后，研究 从政策、教育及产业协同的角度，提出了构建未来人力资源管理新生态的系
统性 建议。本研 究旨在为企业在 AI 时代的 HRM 转型提供兼具理论深度与实践价值的指导
框架。研究现状分析：首先，本研究全面梳理了 AI 在招聘、培训、绩效管理等核心 HR 职能中
的应用现状，深入剖析了技术应用过程中涉及的算法偏见、隐私保护等伦理挑战，为后续策略
制定奠定了理论基础。
差异化分析：通过对不同规模、行业及地域文化背景下企业应用 AI-HRM 的差异性比较，本研
究识别了影响转型成效的关键因素，揭示了转型路径的多样性特征。研究发现，企业规模、行
业特征和组织文化显著影响 AI 技术的采纳模式和实施效果。
转型框架构建：在此基础上，本研究创新性地提出了一个涵盖战略规划、技术准备、试点验
证、规模推广与持续优化的五阶段渐进式转型框架，并针对不同类型企业设计了相应的差异化
实施策略和风险防控机制。
实证研究发现：通过对 500 家企业的深度调研和数据分析，研究验证了 AI 应用对 HR 管理效能
的积极作用。实证结果显示，AI 技术能显著提升 HR 运营效率（平均提升约 45%）与决策质量
（平均提升约 38%），同时在人才识别准确性方面提升了约 32%。然而，企业在技术集成、数据
治理、组织变革管理和投资回报评估方面仍面临诸多挑战。
生态建设建议：最后，研究从政策引导、人才培养、技术标准制定及产业协同发展的多维角
度，提出了构建 AI 时代人力资源管理新生态的系统性建议，包括建立跨部门协作机制、完善
相关法律法规、推进教育体系改革等具体措施。
研究价值：本研究构建的理论框架和实证发现，旨在为企业在 AI 时代的 HRM 数字化转型提供
兼具理论深度与实践指导价值的系统性解决方案，助力企业在智能化浪潮中实现人力资源管理
的创新突破"""

    print("=== 测试文档重复检测 ===")
    print("文档A长度:", len(doc_a))
    print("文档B长度:", len(doc_b))
    print()
    
    # 创建比较器
    comparator = DocumentComparator(
        similarity_threshold_high=0.85,  # 降低阈值以提高敏感度
        similarity_threshold_medium=0.6,
        chunk_size=200,  # 更小的分块大小
        max_workers=4
    )
    
    # 测试分块
    chunks_a = comparator.split_into_chunks(doc_a)
    chunks_b = comparator.split_into_chunks(doc_b)
    
    print("文档A分块:")
    for i, chunk in enumerate(chunks_a):
        print(f"  块{i}: {chunk['content'][:50]}... (长度: {len(chunk['content'])})")
    
    print("\n文档B分块:")
    for i, chunk in enumerate(chunks_b):
        print(f"  块{i}: {chunk['content'][:50]}... (长度: {len(chunk['content'])})")
    
    print(f"\n文档A分块数: {len(chunks_a)}")
    print(f"文档B分块数: {len(chunks_b)}")
    
    # 测试匹配
    matches = comparator.find_best_matches(chunks_a, chunks_b)
    
    print(f"\n找到匹配数: {len(matches)}")
    for match in matches:
        print(f"  匹配: {match['chunk_a_id']} -> {match['chunk_b_id']}, 相似度: {match['similarity']:.3f}, 类型: {match['match_type']}")
    
    # 测试整体相似度
    overall_similarity = comparator.calculate_similarity(doc_a, doc_b)
    print(f"\n整体相似度: {overall_similarity:.3f}")
    
    return len(matches) > 0

if __name__ == "__main__":
    success = test_duplicate_detection()
    if success:
        print("\n✅ 测试成功：重复内容被正确检测")
    else:
        print("\n❌ 测试失败：重复内容未被检测")
    sys.exit(0 if success else 1)