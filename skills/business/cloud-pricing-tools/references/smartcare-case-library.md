# SmartCare 案例库索引（售前资料素材源）

案例库存放路径：`/home/ubuntu/cloud-docs/SmartCare案例集/`

## 目录结构

```
/home/ubuntu/cloud-docs/SmartCare案例集/
├── 北区/                           (19MB, 40+ 案例)
│   ├── SmartCare-案例集-北区-V1.1.pptx
│   └── 案例集.md                    (索引：LZ/WA/迁移/大数据/DR/信创)
├── 东1组/                          (15MB, 15+ 案例)
│   ├── SmartCare-案例集-东1组-v1.0.pptx
│   └── 案例集.md                    (索引：MSP/LZ/IaC/迁移/大数据/治理)
└── 东2组/                          (9.2MB, 7+ 案例)
    ├── SmartCare-案例集-东2-202607.pptx
    └── 案例集.md                    (索引：多云运维MSP/LZ/M365)
```

## 按方向抽取案例速查

| 售前方向 | 主要来源 | 代表客户 |
|---|---|---|
| Landing Zone | 北区/东1组/东2组 | 外服云/Veolia/Cabot/安联/无印良品/Evirth |
| Well-Architected | 北区/东1组 | EPSON/诺基亚/阿斯利康/越秀/伊利 |
| 云迁移 | 北区/东1组 | 爱茉莉/史泰博/巴斯夫/卡尔史托斯/Peet Coffee |
| 大数据迁移 | 北区/东1组 | 万师傅/格力IoT/叮咚买菜/好特卖/杰竞科技 |
| 容灾 DR | 北区 | 百济神州 |
| IaC | 北区/东1组 | Lilly/石基/Goto/Cabot |
| 信创改造 | 北区 | 数字广东 |
| 运维 MSP | 东1组/东2组 | PepsiCo/Sanofi/McDonald/Mondelez/BASF |
| HRO/PE/SRE | 东1组 | Adidas |
| M365 迁移 | 东2组 | Carlyle |

## 使用方式

当用户要求"按 XX 方向整理售前资料"时：
1. 确定对应案例集目录（北区/东1组/东2组）
2. 读取该目录的 `案例集.md` 索引
3. 根据方向匹配代表客户和案例
4. 如需详细内容，用 `pptx_read.py` 读取原始 PPT 对应 slide
5. 整理成售前可用素材（方案/报价/能力证明）

## PPT 读取命令

```bash
# 读取案例集索引
python /home/ubuntu/.hermes/skills/productivity/powerpoint/scripts/pptx_read.py \
  /home/ubuntu/cloud-docs/SmartCare案例集/北区/doc_6453705e8224_SmartCare-案例集-北区-V1.1.pptx \
  --outline | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'Slide {s[\"index\"]}: {s[\"texts\"][0][:60] if s[\"texts\"] else \"(无标题)\"}') for s in d['slides']]"
```
