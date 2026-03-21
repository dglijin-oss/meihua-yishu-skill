#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
梅花易数排盘工具 v2.0.0
天工长老开发

功能：梅花易数起卦、互卦、变卦、体用分析、自动化断卦
v2.0.0 新增：外应断卦、卦例库、断语细化、吉凶评分
"""

import argparse
import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============== 基础数据 ==============

# 八卦
BA_GUA = ['乾', '兑', '离', '震', '巽', '坎', '艮', '坤']

# 八卦数（先天数）
BA_GUA_NUM = {'乾': 1, '兑': 2, '离': 3, '震': 4, '巽': 5, '坎': 6, '艮': 7, '坤': 8}

# 八卦五行
BA_GUA_WUXING = {
    '乾': '金', '兑': '金', '离': '火', '震': '木',
    '巽': '木', '坎': '水', '艮': '土', '坤': '土'
}

# 八卦象意
BA_GUA_XIANG = {
    '乾': {'象': '天', '人': '父', '身': '头', '性': '健'},
    '兑': {'象': '泽', '人': '少女', '身': '口', '性': '悦'},
    '离': {'象': '火', '人': '中女', '身': '目', '性': '丽'},
    '震': {'象': '雷', '人': '长男', '身': '足', '性': '动'},
    '巽': {'象': '风', '人': '长女', '身': '股', '性': '入'},
    '坎': {'象': '水', '人': '中男', '身': '耳', '性': '陷'},
    '艮': {'象': '山', '人': '少男', '身': '手', '性': '止'},
    '坤': {'象': '地', '人': '母', '身': '腹', '性': '顺'},
}

# 六十四卦名
LIU_SHI_SI_GUA = {
    '乾乾': '乾为天', '乾兑': '天泽履', '乾离': '天火同人', '乾震': '天雷无妄',
    '乾巽': '天风姤', '乾坎': '天水讼', '乾艮': '天山遁', '乾坤': '天地否',
    '兑乾': '泽天夬', '兑兑': '兑为泽', '兑离': '泽火革', '兑震': '泽雷随',
    '兑巽': '泽风大过', '兑坎': '泽水困', '兑艮': '泽山咸', '兑坤': '泽地萃',
    '离乾': '火天大有', '离兑': '火泽睽', '离离': '离为火', '离震': '火雷噬嗑',
    '离巽': '火风鼎', '离坎': '火水未济', '离艮': '火山旅', '离坤': '火地晋',
    '震乾': '雷天大壮', '震兑': '雷泽归妹', '震离': '雷火丰', '震震': '震为雷',
    '震巽': '雷风恒', '震坎': '雷水解', '震艮': '雷山小过', '震坤': '雷地豫',
    '巽乾': '风天小畜', '巽兑': '风泽中孚', '巽离': '风火家人', '巽震': '风雷益',
    '巽巽': '巽为风', '巽坎': '风水涣', '巽艮': '风山渐', '巽坤': '风地观',
    '坎乾': '水天需', '坎兑': '水泽节', '坎离': '水火既济', '坎震': '水雷屯',
    '坎巽': '水风井', '坎坎': '坎为水', '坎艮': '水山蹇', '坎坤': '水地比',
    '艮乾': '山天大畜', '艮兑': '山泽损', '艮离': '山火贲', '艮震': '山雷颐',
    '艮巽': '山风蛊', '艮坎': '山水蒙', '艮艮': '艮为山', '艮坤': '山地剥',
    '坤乾': '地天泰', '坤兑': '地泽临', '坤离': '地火明夷', '坤震': '地雷复',
    '坤巽': '地风升', '坤坎': '地水师', '坤艮': '地山谦', '坤坤': '坤为地',
}

# 五行生克
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}


class MeiHuaPan:
    """梅花易数排盘类"""
    
    @classmethod
    def number_to_gua(cls, num: int) -> int:
        """数字转八卦（先天数）"""
        gua = num % 8
        if gua == 0:
            gua = 8
        return gua
    
    @classmethod
    def get_gua_name(cls, shang: int, xia: int) -> str:
        """获取卦名"""
        shang_gua = BA_GUA[shang - 1]
        xia_gua = BA_GUA[xia - 1]
        key = shang_gua + xia_gua
        return LIU_SHI_SI_GUA.get(key, '未知卦')
    
    @classmethod
    def get_hu_gua(cls, shang: int, xia: int) -> Tuple[int, int]:
        """
        计算互卦
        互卦：取本卦的 234 爻为下卦，345 爻为上卦
        """
        # 简化：直接用卦数计算
        # 实际需要根据爻位计算，这里用近似
        hu_shang = (xia + 1) % 8 + 1
        hu_xia = (shang + 1) % 8 + 1
        if hu_shang == 0:
            hu_shang = 8
        if hu_xia == 0:
            hu_xia = 8
        return hu_shang, hu_xia
    
    @classmethod
    def get_bian_gua(cls, shang: int, xia: int, dong_yao: int) -> Tuple[int, int]:
        """
        计算变卦
        dong_yao: 动爻位置（1-6）
        """
        # 动爻变阴阳，对应卦数变化
        if dong_yao <= 3:
            # 下卦动
            new_xia = 9 - xia  # 变卦
            new_shang = shang
        else:
            # 上卦动
            new_shang = 9 - shang
            new_xia = xia
        
        return new_shang, new_xia
    
    @classmethod
    def get_ti_yong(cls, shang: int, xia: int, dong_yao: int) -> Dict:
        """
        确定体用
        动爻所在卦为用卦，另一卦为体卦
        """
        if dong_yao <= 3:
            # 下卦动，下卦为用，上卦为体
            ti_gua = shang
            yong_gua = xia
        else:
            # 上卦动，上卦为用，下卦为体
            ti_gua = xia
            yong_gua = shang
        
        ti_wuxing = BA_GUA_WUXING[BA_GUA[ti_gua - 1]]
        yong_wuxing = BA_GUA_WUXING[BA_GUA[yong_gua - 1]]
        
        # 体用生克
        if ti_wuxing == yong_wuxing:
            sheng_ke = '比和'
            ji_xiong = '吉'
        elif WUXING_SHENG.get(ti_wuxing) == yong_wuxing:
            sheng_ke = '体生用'
            ji_xiong = '凶'
        elif WUXING_SHENG.get(yong_wuxing) == ti_wuxing:
            sheng_ke = '用生体'
            ji_xiong = '大吉'
        elif WUXING_KE.get(ti_wuxing) == yong_wuxing:
            sheng_ke = '体克用'
            ji_xiong = '吉'
        elif WUXING_KE.get(yong_wuxing) == ti_wuxing:
            sheng_ke = '用克体'
            ji_xiong = '凶'
        else:
            sheng_ke = '未知'
            ji_xiong = '平'
        
        return {
            '体卦': BA_GUA[ti_gua - 1],
            '体卦数': ti_gua,
            '体卦五行': ti_wuxing,
            '用卦': BA_GUA[yong_gua - 1],
            '用卦数': yong_gua,
            '用卦五行': yong_wuxing,
            '体用关系': sheng_ke,
            '吉凶': ji_xiong
        }
    
    @classmethod
    def get_duan_yu(cls, ti_yong: Dict, ben_gua: str, hu_gua: str, bian_gua: str) -> List[str]:
        """生成断语（v1.0.0）"""
        duan_yu = []
        
        # 体用关系断语
        if ti_yong['吉凶'] == '大吉':
            duan_yu.append(f"用生体，大吉，事易成，有贵人相助")
        elif ti_yong['吉凶'] == '吉':
            duan_yu.append(f"{ti_yong['体用关系']}，吉，事可成")
        elif ti_yong['吉凶'] == '凶':
            duan_yu.append(f"{ti_yong['体用关系']}，凶，事多阻，需谨慎")
        
        # 卦名断语
        if '泰' in ben_gua:
            duan_yu.append("地天泰，三阳开泰，万事亨通")
        elif '否' in ben_gua:
            duan_yu.append("天地否，闭塞不通，宜守不宜攻")
        elif '既济' in ben_gua:
            duan_yu.append("水火既济，事已成，宜守成")
        elif '未济' in ben_gua:
            duan_yu.append("火水未济，事未成，需努力")
        elif '乾' in ben_gua:
            duan_yu.append("乾为天，刚健中正，自强不息")
        elif '坤' in ben_gua:
            duan_yu.append("坤为地，厚德载物，顺势而为")
        
        # 变卦断语
        if ben_gua != bian_gua:
            duan_yu.append(f"变卦{bian_gua}，事情将有变化")
        
        if not duan_yu:
            duan_yu.append("卦象平稳，顺势而为")
        
        return duan_yu
    
    @classmethod
    def get_wai_ying_v3(cls, ben_gua: str, ti_yong: Dict) -> Dict:
        """
        v2.0.0 外应断卦
        
        外应：起卦时的外在征应（声音、颜色、人物、动物等）
        此处为简化版，根据卦象推断可能的外应
        
        参数：
            ben_gua: 本卦名
            ti_yong: 体用信息
        
        返回：
            外应信息
        """
        wai_ying = {
            '外应类型': [],
            '外应详解': [],
            '外应吉凶': '中'
        }
        
        # 根据体卦推断外应
        ti_gua = ti_yong.get('体卦', '')
        
        ti_gua_wai_ying = {
            '乾': {'象': '金玉之声', '色': '白', '物': '圆形物', '事': '贵人'},
            '兑': {'象': '口舌之声', '色': '白', '物': '金属物', '事': '少女'},
            '离': {'象': '火光之色', '色': '红', '物': '文书', '事': '中女'},
            '震': {'象': '雷动之声', '色': '青', '物': '木器', '事': '长男'},
            '巽': {'象': '风行之声', '色': '绿', '物': '绳索', '事': '长女'},
            '坎': {'象': '水流之声', '色': '黑', '物': '液体', '事': '中男'},
            '艮': {'象': '山止之象', '色': '黄', '物': '土石', '事': '少男'},
            '坤': {'象': '地载之象', '色': '黑', '物': '方形物', '事': '老母'},
        }
        
        if ti_gua in ti_gua_wai_ying:
            ying = ti_gua_wai_ying[ti_gua]
            wai_ying['外应类型'].append(f"体卦{ti_gua}外应：{ying['象']}")
            wai_ying['外应详解'].append(f"• 颜色：{ying['色']}")
            wai_ying['外应详解'].append(f"• 物品：{ying['物']}")
            wai_ying['外应详解'].append(f"• 人物：{ying['事']}")
        
        # 根据卦名推断外应
        if '乾' in ben_gua:
            wai_ying['外应类型'].append("乾卦外应：见贵人、闻金声")
        elif '坤' in ben_gua:
            wai_ying['外应类型'].append("坤卦外应：见老妇、得布帛")
        elif '震' in ben_gua:
            wai_ying['外应类型'].append("震卦外应：闻雷声、见木器")
        elif '巽' in ben_gua:
            wai_ying['外应类型'].append("巽卦外应：闻风声、得绳索")
        elif '坎' in ben_gua:
            wai_ying['外应类型'].append("坎卦外应：闻水声、见液体")
        elif '离' in ben_gua:
            wai_ying['外应类型'].append("离卦外应：见火光、得文书")
        elif '艮' in ben_gua:
            wai_ying['外应类型'].append("艮卦外应：见山石、得土石")
        elif '兑' in ben_gua:
            wai_ying['外应类型'].append("兑卦外应：闻歌声、见少女")
        
        # 外应吉凶
        if ti_yong['吉凶'] in ['大吉', '吉']:
            wai_ying['外应吉凶'] = '吉'
        elif ti_yong['吉凶'] == '凶':
            wai_ying['外应吉凶'] = '凶'
        
        return wai_ying
    
    @classmethod
    def get_gua_li_v3(cls, ben_gua: str, hu_gua: str, bian_gua: str) -> Dict:
        """
        v2.0.0 卦例库匹配
        
        根据卦名匹配经典卦例
        
        参数：
            ben_gua: 本卦
            hu_gua: 互卦
            bian_gua: 变卦
        
        返回：
            卦例信息
        """
        gua_li = {
            '卦例': None,
            '典故': None,
            '启示': None
        }
        
        # 经典卦例库
        gua_li_db = {
            '地天泰': {
                '卦例': '泰卦三阳开泰',
                '典故': '周文王演易，泰卦亨通',
                '启示': '小往大来，吉亨，宜把握良机'
            },
            '天地否': {
                '卦例': '否卦闭塞不通',
                '典故': '孔子厄于陈蔡，得否卦',
                '启示': '大往小来，宜守不宜攻'
            },
            '水火既济': {
                '卦例': '既济事已成',
                '典故': '诸葛亮借东风，事已成',
                '启示': '初吉终乱，宜守成'
            },
            '火水未济': {
                '卦例': '未济事未成',
                '典故': '姜子牙钓鱼，待时而动',
                '启示': '虽不当位，刚柔应也，需努力'
            },
            '乾为天': {
                '卦例': '乾卦六龙御天',
                '典故': '尧舜禅让，天道酬勤',
                '启示': '天行健，君子以自强不息'
            },
            '坤为地': {
                '卦例': '坤卦厚德载物',
                '典故': '文王演易，地道光也',
                '启示': '地势坤，君子以厚德载物'
            },
            '水雷屯': {
                '卦例': '屯卦万事开头难',
                '典故': '刘备起兵，艰难创业',
                '启示': '刚柔始交而难生，宜守'
            },
            '山水蒙': {
                '卦例': '蒙卦启蒙教育',
                '典故': '孔子杏坛讲学',
                '启示': '匪我求童蒙，童蒙求我'
            },
            '泽火革': {
                '卦例': '革卦改革变革',
                '典故': '商鞅变法',
                '启示': '天地革而四时成，适时变革'
            },
            '火风鼎': {
                '卦例': '鼎卦鼎新革故',
                '典故': '伊尹辅商汤',
                '启示': '君子以正位凝命'
            },
        }
        
        if ben_gua in gua_li_db:
            gua_li['卦例'] = gua_li_db[ben_gua]['卦例']
            gua_li['典故'] = gua_li_db[ben_gua]['典故']
            gua_li['启示'] = gua_li_db[ben_gua]['启示']
        
        return gua_li
    
    @classmethod
    def get_ji_xiong_ping_fen_v3(cls, ti_yong: Dict, ben_gua: str, hu_gua: str, bian_gua: str) -> int:
        """
        v2.0.0 吉凶量化评分
        
        参数：
            ti_yong: 体用信息
            ben_gua: 本卦
            hu_gua: 互卦
            bian_gua: 变卦
        
        返回：
            吉凶评分（0-100）
        """
        score = 50  # 基础分
        
        # 体用关系评分
        if ti_yong['吉凶'] == '大吉':
            score += 30
        elif ti_yong['吉凶'] == '吉':
            score += 20
        elif ti_yong['吉凶'] == '凶':
            score -= 20
        
        # 卦名评分
        ji_gua = ['泰', '大有', '谦', '豫', '随', '蛊', '临', '观', '贲', '复', '无妄', '大畜', '颐', '大过', '坎', '离', '咸', '恒', '遁', '大壮', '晋', '明夷', '家人', '睽', '蹇', '解', '损', '益', '夬', '姤', '萃', '升', '困', '井', '革', '鼎', '震', '艮', '渐', '归妹', '丰', '旅', '巽', '兑', '涣', '节', '中孚', '小过', '既济']
        xiong_gua = ['否', '屯', '蒙', '需', '讼', '师', '比', '小畜', '履', '同人', '姤', '萃', '升', '困', '井', '革', '鼎', '震', '艮', '渐', '归妹', '丰', '旅', '巽', '兑', '涣', '节', '中孚', '小过', '未济']
        
        for gua in ji_gua:
            if gua in ben_gua:
                score += 10
                break
        
        for gua in xiong_gua:
            if gua in ben_gua:
                score -= 10
                break
        
        # 变卦评分
        if ben_gua != bian_gua:
            # 有变卦，看变化方向
            if '泰' in bian_gua or '大有' in bian_gua:
                score += 15
            elif '否' in bian_gua or '未济' in bian_gua:
                score -= 15
        
        return max(0, min(100, score))


def meihua_pan(
    numbers: Optional[str] = None,
    date_str: Optional[str] = None,
    fang_wei: Optional[str] = None,
    question: str = '通用'
) -> Dict:
    """
    梅花易数排盘主函数
    """
    # 起卦方式
    if numbers:
        # 数字起卦
        num_list = [int(x.strip()) for x in numbers.split(',')]
        if len(num_list) >= 2:
            shang_gua = MeiHuaPan.number_to_gua(num_list[0])
            xia_gua = MeiHuaPan.number_to_gua(num_list[1])
            if len(num_list) >= 3:
                dong_yao = MeiHuaPan.number_to_gua(num_list[2])
            else:
                dong_yao = (num_list[0] + num_list[1]) % 6
                if dong_yao == 0:
                    dong_yao = 6
        else:
            total = sum(num_list)
            shang_gua = MeiHuaPan.number_to_gua(total)
            xia_gua = MeiHuaPan.number_to_gua(total + 100)
            dong_yao = MeiHuaPan.number_to_gua(total + 50)
        qi_gua = '数字'
    elif date_str:
        # 时间起卦
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        
        shang_gua = (year + month + day) % 8
        if shang_gua == 0:
            shang_gua = 8
        xia_gua = (year + month + day + hour) % 8
        if xia_gua == 0:
            xia_gua = 8
        dong_yao = (year + month + day + hour) % 6
        if dong_yao == 0:
            dong_yao = 6
        qi_gua = '时间'
    elif fang_wei:
        # 方位起卦（简化）
        fang_wei_map = {'东': 4, '东南': 5, '南': 3, '西南': 8, 
                       '西': 2, '西北': 1, '北': 6, '东北': 7}
        shang_gua = fang_wei_map.get(fang_wei, 1)
        xia_gua = (shang_gua + 3) % 8 + 1
        dong_yao = shang_gua % 6
        if dong_yao == 0:
            dong_yao = 6
        qi_gua = '方位'
    else:
        # 随机起卦
        shang_gua = random.randint(1, 8)
        xia_gua = random.randint(1, 8)
        dong_yao = random.randint(1, 6)
        qi_gua = '随机'
    
    # 卦名
    ben_gua = MeiHuaPan.get_gua_name(shang_gua, xia_gua)
    
    # 互卦
    hu_shang, hu_xia = MeiHuaPan.get_hu_gua(shang_gua, xia_gua)
    hu_gua = MeiHuaPan.get_gua_name(hu_shang, hu_xia)
    
    # 变卦
    bian_shang, bian_xia = MeiHuaPan.get_bian_gua(shang_gua, xia_gua, dong_yao)
    bian_gua = MeiHuaPan.get_gua_name(bian_shang, bian_xia)
    
    # 体用
    ti_yong = MeiHuaPan.get_ti_yong(shang_gua, xia_gua, dong_yao)
    
    # 断语（v1.0.0）
    duan_yu = MeiHuaPan.get_duan_yu(ti_yong, ben_gua, hu_gua, bian_gua)
    
    # v2.0.0 外应断卦
    wai_ying = MeiHuaPan.get_wai_ying_v3(ben_gua, ti_yong)
    
    # v2.0.0 卦例库
    gua_li = MeiHuaPan.get_gua_li_v3(ben_gua, hu_gua, bian_gua)
    
    # v2.0.0 吉凶评分
    ji_xiong_ping_fen = MeiHuaPan.get_ji_xiong_ping_fen_v3(ti_yong, ben_gua, hu_gua, bian_gua)
    
    result = {
        '起卦方式': qi_gua,
        '本卦': ben_gua,
        '上卦': BA_GUA[shang_gua - 1],
        '下卦': BA_GUA[xia_gua - 1],
        '动爻': dong_yao,
        '互卦': hu_gua,
        '变卦': bian_gua,
        '体用': ti_yong,
        '问事类型': question,
        '断语': duan_yu,
        '外应': wai_ying,
        '卦例': gua_li,
        '吉凶评分': ji_xiong_ping_fen,
    }
    
    return result


def format_output(result: Dict) -> str:
    """格式化输出"""
    output = []
    
    output.append("【梅花易数排盘】")
    output.append(f"• 起卦方式：{result['起卦方式']}")
    output.append("")
    output.append("【本卦】")
    output.append(f"• 卦名：{result['本卦']}")
    output.append(f"• 上卦：{result['上卦']}")
    output.append(f"• 下卦：{result['下卦']}")
    output.append(f"• 动爻：第{result['动爻']}爻")
    output.append("")
    output.append("【互卦】")
    output.append(f"• 卦名：{result['互卦']}")
    output.append("")
    output.append("【变卦】")
    output.append(f"• 卦名：{result['变卦']}")
    output.append("")
    output.append("【体用分析】")
    ti_yong = result['体用']
    output.append(f"• 体卦：{ti_yong['体卦']}（{ti_yong['体卦五行']}）")
    output.append(f"• 用卦：{ti_yong['用卦']}（{ti_yong['用卦五行']}）")
    output.append(f"• 体用关系：{ti_yong['体用关系']}")
    output.append(f"• 吉凶：{ti_yong['吉凶']}")
    output.append("")
    output.append("【断卦分析】")
    for duan in result['断语']:
        output.append(f"• {duan}")
    
    # v2.0.0 吉凶评分
    if result.get('吉凶评分'):
        score = result['吉凶评分']
        if score >= 70:
            ping_ji = '大吉'
        elif score >= 55:
            ping_ji = '吉'
        elif score >= 45:
            ping_ji = '平'
        elif score >= 30:
            ping_ji = '凶'
        else:
            ping_ji = '大凶'
        output.append("")
        output.append("【吉凶评分】v2.0.0")
        output.append(f"• 评分：{score}/100（{ping_ji}）")
    
    # v2.0.0 外应断卦
    if result.get('外应'):
        wai_ying = result['外应']
        output.append("")
        output.append("【外应断卦】v2.0.0")
        if wai_ying.get('外应类型'):
            for ying in wai_ying['外应类型']:
                output.append(f"• {ying}")
        if wai_ying.get('外应详解'):
            for xiang in wai_ying['外应详解']:
                output.append(f"  {xiang}")
        output.append(f"• 外应吉凶：{wai_ying.get('外应吉凶', '中')}")
    
    # v2.0.0 卦例库
    if result.get('卦例'):
        gua_li = result['卦例']
        if gua_li.get('卦例') or gua_li.get('典故') or gua_li.get('启示'):
            output.append("")
            output.append("【卦例参考】v2.0.0")
            if gua_li.get('卦例'):
                output.append(f"• 卦例：{gua_li['卦例']}")
            if gua_li.get('典故'):
                output.append(f"• 典故：{gua_li['典故']}")
            if gua_li.get('启示'):
                output.append(f"• 启示：{gua_li['启示']}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='梅花易数排盘工具 v2.0.0')
    parser.add_argument('--numbers', '-n', type=str, help='数字起卦 (逗号分隔，至少 2 个数字)')
    parser.add_argument('--date', '-d', type=str, help='时间起卦 (YYYY-MM-DD HH:MM)')
    parser.add_argument('--fangwei', '-f', type=str, help='方位起卦 (东/南/西/北/东南/西南/西北/东北)')
    parser.add_argument('--question', '-q', type=str, default='通用', help='问事类型')
    parser.add_argument('--json', '-j', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--random', '-r', action='store_true', help='随机起卦')
    
    args = parser.parse_args()
    
    try:
        if args.random:
            result = meihua_pan()
        else:
            result = meihua_pan(args.numbers, args.date, args.fangwei, args.question)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_output(result))
            
    except Exception as e:
        print(f"排盘错误：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
