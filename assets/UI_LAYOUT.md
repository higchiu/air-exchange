# main_page 布局说明

| 文件 | 用途 |
|------|------|
| [`bg-640.png`](bg-640.png) | 固件 `main_page` 全屏背景（640×640 源图，烧录缩放到 480×480） |
| [`element.jpg`](element.jpg) | **仅作开发对照**：各控件在日立参考 UI 上的位置，不烧录进设备 |

固件实现见 `packages/main_page_ui.yaml`、`packages/main_page_logic.yaml`。

## 已实现（当前版本）

### 顶部
- 左：Wi-Fi 信号图标（按 dBm 切换 `mdi_wifi_strength_*`）
- 右：时间 `MM月dd日 HH:mm`（SNTP / HA 时间）

### 室内（房屋区域）
- 温湿度：`temp_indoor` / `humidity_indoor`（SHT31）
- PM2.5：`pm25`（PMS5003），徽章底色绿 / 黄 / 红
- CO₂：`co2_indoor`（SCD30），绿 &lt;800 / 黄 800–1200 / 红 ≥1200 ppm
- TVOC 等级：`tvoc_level`（HA 订阅），绿 1–2 / 黄 3–4 / 红 5–6 级

### 室外（右侧胶囊）
- 温湿度：`temp_outdoor` / `humidity_outdoor`（室外 SHT31）
- PM2.5：`pm25_city`（同城联网，HA），配色同 PM2.5

### 配色阈值（µg/m³ / ppm / 级）

| 指标 | 绿 | 黄 | 红 |
|------|----|----|-----|
| PM2.5 | &lt;35 | 35–75 | ≥75 |
| CO₂ | &lt;800 | 800–1200 | ≥1200 |
| TVOC | ≤2 | 3–4 | ≥5 |

## 待开发（element.jpg 底部栏）

- 运转模式 / 风量 / 附加功能
- 报警、滤网提醒、电源键

副页 `ctrl_page`：送风/排风 ±10%、Info；`main_page` 右下角 **More** 或左右滑动进入。
