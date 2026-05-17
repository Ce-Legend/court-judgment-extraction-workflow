# -*- coding: utf-8 -*-
"""
文本解析器 - 从判决书文本中提取结构化信息
新手提示：这个模块使用正则表达式从判决书中提取关键信息
"""

import re
from utils.logger import logger
from utils.helper import clean_text

class JudgmentParser:
    """判决书解析器"""
    
    def __init__(self):
        """初始化解析器"""
        # 中文数字映射
        self.cn_num_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '十': 10, '百': 100, '千': 1000, '万': 10000,
        }
    
    def parse(self, case_data):
        """
        解析案件数据
        
        参数：
            case_data: 包含full_text的案件数据
        
        返回：
            解析后的结构化数据
        """
        try:
            text = case_data.get("full_text", "")
            
            if not text:
                logger.warning("⚠️ 文本为空，无法解析")
                return case_data
            
            # 提取各个字段
            parsed = case_data.copy()
            
            # 1. 案号
            if not parsed.get("case_no"):
                parsed["case_no"] = self.extract_case_no(text)
            
            # 2. 法院
            if not parsed.get("court"):
                parsed["court"] = self.extract_court(text)
            
            # 3. 裁判日期
            if not parsed.get("date"):
                parsed["date"] = self.extract_date(text)
            
            # 4. 案由
            parsed["case_reason"] = self.extract_case_reason(text)
            
            # 5. 被告人性别
            parsed["defendant_gender"] = self.extract_gender(text)
            
            # 6. 被害人伤害程度
            parsed["injury_level"] = self.extract_injury_level(text)
            
            # 7. 赔偿金额
            parsed["compensation"] = self.extract_compensation(text)
            
            # 8. 判决刑期
            parsed["sentence"] = self.extract_sentence(text)
            
            # 9. 判决结果
            parsed["verdict"] = self.extract_verdict(text)
            
            # 10. 审理程序
            parsed["trial_procedure"] = self.extract_trial_procedure(text)
            
            logger.debug(f"✅ 解析完成：{parsed.get('case_no', 'Unknown')}")
            
            return parsed
            
        except Exception as e:
            logger.error(f"❌ 解析失败：{str(e)}")
            return case_data
    
    def extract_case_no(self, text):
        """提取案号"""
        # 案号格式：（2020）京0101刑初123号
        patterns = [
            r'[（(]\d{4}[）)][\u4e00-\u9fa5\d]+号',
            r'案号[：:]\s*[（(]\d{4}[）)][\u4e00-\u9fa5\d]+号',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return clean_text(match.group())
        
        return ""
    
    def extract_court(self, text):
        """提取法院名称"""
        # 法院名称通常在开头
        patterns = [
            r'([\u4e00-\u9fa5]+人民法院)',
            r'([\u4e00-\u9fa5]+法院)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:500])  # 只在前500字符中查找
            if match:
                return clean_text(match.group(1))
        
        return ""
    
    def extract_date(self, text):
        """提取裁判日期"""
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
        ]
        
        # 从文本末尾开始查找（日期通常在末尾）
        for pattern in patterns:
            matches = re.findall(pattern, text[-1000:])
            if matches:
                # 返回最后一个日期
                last_match = matches[-1]
                return f"{last_match[0]}-{last_match[1].zfill(2)}-{last_match[2].zfill(2)}"
        
        return ""
    
    def extract_case_reason(self, text):
        """提取案由"""
        # 查找"故意伤害"相关
        patterns = [
            r'(故意伤害罪)',
            r'案由[：:]\s*([\u4e00-\u9fa5]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:1000])
            if match:
                if '故意伤害' in match.group():
                    return "故意伤害罪"
        
        return "故意伤害罪"  # 默认值（因为我们就是搜这个关键词）
    
    def extract_gender(self, text):
        """提取被告人性别"""
        # 查找"被告人...男/女"
        patterns = [
            r'被告人[^，。]+?[，、\s](男|女)[，、\s]',
            r'被告[：:][^，。]*?[，、\s](男|女)[，、\s]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text[:2000])
            if match:
                return match.group(1)
        
        return ""
    
    def extract_injury_level(self, text):
        """提取伤害程度"""
        # 查找伤害等级
        if re.search(r'重伤二级|重伤Ⅱ级', text):
            return "重伤二级"
        elif re.search(r'重伤一级|重伤Ⅰ级', text):
            return "重伤一级"
        elif re.search(r'重伤', text):
            return "重伤"
        elif re.search(r'轻伤二级|轻伤Ⅱ级', text):
            return "轻伤二级"
        elif re.search(r'轻伤一级|轻伤Ⅰ级', text):
            return "轻伤一级"
        elif re.search(r'轻伤', text):
            return "轻伤"
        elif re.search(r'轻微伤', text):
            return "轻微伤"
        
        return ""
    
    def extract_compensation(self, text):
        """提取赔偿金额"""
        # 查找赔偿金额
        patterns = [
            r'赔偿[^。，]*?(\d+(?:\.\d+)?)\s*(?:元|万元)',
            r'经济损失[^。，]*?(\d+(?:\.\d+)?)\s*(?:元|万元)',
            r'(?:赔偿|支付|给付)[^。，]*?人民币\s*(\d+(?:\.\d+)?)\s*(?:元|万元)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match)
                    if '万元' in text[text.find(match):text.find(match)+20]:
                        amount *= 10000
                    amounts.append(amount)
                except:
                    continue
        
        if amounts:
            # 返回最大的金额
            return f"{max(amounts):.2f}元"
        
        return ""
    
    def extract_sentence(self, text):
        """提取判决刑期"""
        # 查找刑期
        sentences = []
        
        # 有期徒刑
        patterns = [
            r'判处(?:被告人)?[^。，]*?有期徒刑([^。，]*?)(?:[，。、]|$)',
            r'有期徒刑\s*([^。，]+?)(?:[，。、]|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                sentence_text = match
                
                # 提取年月
                years = 0
                months = 0
                
                # 查找年
                year_match = re.search(r'(\d+|[一二三四五六七八九十]+)年', sentence_text)
                if year_match:
                    years = self.cn_to_num(year_match.group(1))
                
                # 查找月
                month_match = re.search(r'(\d+|[一二三四五六七八九十]+)个?月', sentence_text)
                if month_match:
                    months = self.cn_to_num(month_match.group(1))
                
                if years > 0 or months > 0:
                    result = []
                    if years > 0:
                        result.append(f"{years}年")
                    if months > 0:
                        result.append(f"{months}个月")
                    
                    sentence_str = "".join(result)
                    
                    # 检查是否有缓刑
                    if '缓刑' in sentence_text:
                        # 提取缓刑期
                        probation_match = re.search(r'缓刑\s*(\d+|[一二三四五六七八九十]+)年', sentence_text)
                        if probation_match:
                            probation_years = self.cn_to_num(probation_match.group(1))
                            sentence_str += f"（缓刑{probation_years}年）"
                    
                    sentences.append(sentence_str)
        
        # 拘役
        detention_match = re.search(r'拘役\s*(\d+|[一二三四五六七八九十]+)个?月', text)
        if detention_match:
            months = self.cn_to_num(detention_match.group(1))
            sentences.append(f"拘役{months}个月")
        
        # 免予刑事处罚
        if re.search(r'免予刑事处罚', text):
            sentences.append("免予刑事处罚")
        
        if sentences:
            return sentences[0]  # 返回第一个找到的刑期
        
        return ""
    
    def extract_verdict(self, text):
        """提取判决结果"""
        # 查找判决主文
        verdict_match = re.search(r'(?:本院认为|判决如下)[：:]([\s\S]*?)(?:审判|书记|$)', text)
        
        if verdict_match:
            verdict_text = verdict_match.group(1)
            # 限制长度
            if len(verdict_text) > 500:
                verdict_text = verdict_text[:500] + "..."
            return clean_text(verdict_text)
        
        return ""
    
    def extract_trial_procedure(self, text):
        """提取审理程序"""
        if re.search(r'二审|上诉|发回重审', text[:1000]):
            return "二审"
        elif re.search(r'再审|申诉', text[:1000]):
            return "再审"
        else:
            return "一审"
    
    def cn_to_num(self, cn_str):
        """
        中文数字转阿拉伯数字
        
        参数：
            cn_str: 中文数字字符串（如"三"、"十五"）或阿拉伯数字字符串
        
        返回：
            整数
        """
        # 如果已经是数字，直接返回
        if cn_str.isdigit():
            return int(cn_str)
        
        # 简单的中文数字转换
        try:
            # 单个字符
            if len(cn_str) == 1:
                return self.cn_num_map.get(cn_str, 0)
            
            # 十几
            if cn_str.startswith('十'):
                if len(cn_str) == 1:
                    return 10
                else:
                    return 10 + self.cn_num_map.get(cn_str[1], 0)
            
            # 二十、三十等
            if '十' in cn_str:
                parts = cn_str.split('十')
                tens = self.cn_num_map.get(parts[0], 1) * 10
                ones = self.cn_num_map.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
                return tens + ones
            
            return 0
            
        except:
            return 0


def parse_judgment(case_data):
    """
    便捷函数：解析判决书
    
    参数：
        case_data: 案件数据
    
    返回：
        解析后的数据
    """
    parser = JudgmentParser()
    return parser.parse(case_data)

