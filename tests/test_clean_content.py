from merge_and_clean import clean_content


def test_clean_content_removes_navigation_noise():
    raw = """
    欢迎您 使用帮助
    某某市人民法院
    刑事判决书
    案 由
    被告人李某犯故意伤害罪。
    被告人李某犯故意伤害罪。
    """

    cleaned = clean_content(raw)

    assert "使用帮助" not in cleaned
    assert "案 由" not in cleaned
    assert "某某市人民法院" in cleaned
    assert cleaned.count("被告人李某犯故意伤害罪。") == 1
