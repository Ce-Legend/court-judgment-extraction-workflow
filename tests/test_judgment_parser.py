from pathlib import Path

from extractor.parser import JudgmentParser


def load_sample_text():
    return Path("examples/sample_judgment.txt").read_text(encoding="utf-8")


def test_parse_core_judgment_fields():
    parser = JudgmentParser()
    result = parser.parse({"full_text": load_sample_text()})

    assert result["case_no"] == "（2024）示例刑初001号"
    assert result["court"] == "某某市人民法院"
    assert result["case_reason"] == "故意伤害罪"
    assert result["defendant_gender"] == "男"
    assert result["injury_level"] == "轻伤二级"
    assert result["sentence"] == "1年6个月"
    assert result["trial_procedure"] == "一审"


def test_extract_compensation_amount():
    parser = JudgmentParser()
    text = "判令被告人赔偿被害人经济损失人民币12000元。"

    assert parser.extract_compensation(text) == "12000.00元"
