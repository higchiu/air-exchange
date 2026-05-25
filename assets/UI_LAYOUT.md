# main_page 布局说明

| 文件 | 用途 |
|------|------|
| [`bg-640.png`](bg-640.png) | 固件 `main_page` 全屏背景（640×640 源图，烧录缩放到 480×480） |
| [`element.jpg`](element.jpg) | **仅作开发对照**：各控件在日立参考 UI 上的位置，不烧录进设备 |

固件实现见 `packages/main_page_ui.yaml`、`packages/main_page_logic.yaml`。

预览 HTML（与固件坐标同步）：[`panel-bg-480.html`](panel-bg-480.html) — 在 **640×640 设计稿**上排版，CSS `scale(0.75)` 得到 480 预览。

## 坐标体系

| 文件 | 分辨率 | 说明 |
|------|--------|------|
| `bg-640.png` | 640×640 | 背景源图 |
| `packages/main_page_coords_640.yaml` | 640 | 控件 x/y/宽高（与背景 1:1） |
| `packages/main_page_ui.yaml` | 480 | `round(640 × 0.75)` 烧录坐标 |
| ESPHome `resize: 480x480` | 480 | 背景与屏同比例缩小 |

改布局时：**先改 640 坐标**，再运行 `python3 scripts/scale_ui_coords.py` 查 480 对照值，更新 `main_page_ui.yaml`。

## 背景区域（640 设计稿）

| 区域 | x, y, w, h |
|------|------------|
| 房屋（室内） | 11, 117, 389, 389 |
| 右侧胶囊（室外） | 469, 117, 149, 310 |

（480 屏上约为上表 ×0.75）

## 已实现（当前版本）

### 顶部
- 左：Wi-Fi 信号图标（按 dBm 切换 `mdi_wifi_strength_*`）
- 右：时间 `MM月dd日 HH:mm`（SNTP / HA 时间）

### 室内（房屋区域）
- 温湿度：`temp_indoor` / `humidity_indoor`（SHT31）
- PM2.5 / CO₂ / TVOC：**一行两个**（圆内数值，圆外右侧名称 + 单位；第 1 行 PM2.5 + CO₂，第 2 行 TVOC）
  - PM2.5：`pm25`（PMS5003），单位 μg/m³
  - CO₂：`co2_indoor`（SCD30），单位 ppm
  - TVOC 等级：`tvoc_level`（HA），单位「等级」
- 圆章底色：绿 / 黄 / 红（见下表）

### 室外（右侧胶囊）
- 温湿度：`temp_outdoor` / `humidity_outdoor`（室外 SHT31）
- PM2.5：`pm25_city`（同城联网，HA），配色同 PM2.5

### 配色阈值（µg/m³ / ppm / 等级）

| 指标 | 绿 | 黄 | 红 |
|------|----|----|-----|
| PM2.5 | &lt;35 | 35–75 | ≥75 |
| CO₂ | &lt;800 | 800–1200 | ≥1200 |
| TVOC | ≤2 | 3–4 | ≥5 |

## 待开发（element.jpg 底部栏）

- 运转模式 / 风量 / 附加功能
- 报警、滤网提醒、电源键

副页 `ctrl_page`：送风/排风 ±10%、Info；`main_page` 右下角 **More** 或左右滑动进入。
