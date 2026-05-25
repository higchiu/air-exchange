# 室内 TVOC 传感器选型与接入

本文档说明本项目的 TVOC 显示逻辑、推荐硬件，以及 Guition ESP32-S3-4848S040 上的接线与配置思路。

相关固件：

| 文件 | 作用 |
|------|------|
| [`packages/tvoc_sensor.yaml`](../packages/tvoc_sensor.yaml) | 从 HA 订阅 TVOC 等级（1–6） |
| [`packages/main_page_logic.yaml`](../packages/main_page_logic.yaml) | 圆章绿/黄/红阈值 |
| [`secrets.yaml.example`](../secrets.yaml.example) | `tvoc_entity_id` |

---

## 本项目对 TVOC 的要求

- 屏上显示 **整数等级 1–6**，单位文案为 **「等级」**（非 µg/m³）。
- 固件默认 **不直连 VOC 芯片**，而是订阅 Home Assistant 实体 `tvoc_entity_id`。
- 配色阈值（与 PM2.5 / CO₂ 共用「浅底 + 彩色数字」风格）：

| 等级 | 显示 |
|------|------|
| ≤ 2 | 绿 |
| 3–4 | 黄 |
| ≥ 5 | 红 |

已有传感器分工（同机 I2C / UART）：

| 指标 | 器件 | 说明 |
|------|------|------|
| 温湿度 | SHT31 ×2 | I2C |
| CO₂ | SCD30 | I2C；**不能**代替 TVOC |
| PM2.5 | PMS5003 | UART |
| TVOC | **待选** | 见下文推荐 |

---

## 推荐方案（首选）

### Sensirion **SGP41** 或 **SGP40**（I2C）

| 项 | 说明 |
|------|------|
| 接口 | I²C，地址通常 **0x59** |
| ESPHome | [`sgp4x` 组件](https://esphome.io/components/sensor/sgp4x/)，自动识别 SGP40 / SGP41 |
| 输出 | **VOC Index**（约 0–500，**相对指数**，适合趋势与分档，非绝对 TVOC 浓度） |
| 温湿度补偿 | 建议用 **室内 SHT31** 作为 `compensation` 源（你方已有） |
| SGP41 vs SGP40 | SGP41 多 NOx 通道；仅关心异味/VOC 档位时 **SGP40 模块往往够用且更便宜** |

**采购注意**

- 工作电压 **3.3V**（勿接 5V 到信号脚）。
- 选带 **Sensirion 原装芯片** 的 breakout 模块（Adafruit、Seeed、立创等均可）。
- 模块宜有 **I2C 上拉**（多数成品板已带）。

**不推荐**

- **CCS811**：基线漂移大、产品周期老，社区与 ESPHome 支持均弱于 SGP4x。
- **MQ 系列气敏**：功耗高、交叉敏感大，不适合作为「等级」显示源。

---

## 备选：Bosch BME680 / BME688

一体化温湿度 + 气压 + 气体电阻，经 **BSEC** 输出 IAQ 指数。

| 优点 | 缺点（对本项目） |
|------|------------------|
| 单芯片 | 已有 SHT31 + SCD30，功能重叠 |
| IAQ 0–500 与 VOC 趋势相关 | 需 `bme680_bsec` / `bme68x_bsec2`，配置与 RAM 更重 |
| | 仍需映射到 1–6 等级 |

除非希望 **减少传感器数量**，否则优先 **SGP4x**。

---

## 方案对比简表

| 传感器 | VOC 表现 | ESPHome | 与本项目匹配 |
|--------|----------|---------|----------------|
| **SGP41 / SGP40** | ★★★★★ | `sgp4x` 原生 | **最佳** |
| SGP30 | ★★★★☆ | 旧平台，仍可用 | 可用 |
| BME680 + BSEC | ★★★★☆ | `bme680_bsec` 等 | 冗余 |
| CCS811 | ★★★☆☆ | 有支持 | 不推荐 |
| MQ 系 | ★☆☆☆☆ | 不推荐 | 不推荐 |

---

## Guition 4848S040 接线（直连 ESP 时）

整机默认开发板见 [PINOUT.txt](../PINOUT.txt)。

| SGP4x 引脚 | 接法 |
|------------|------|
| VCC | 3.3V（与 SHT / SCD30 同域规划） |
| GND | GND |
| SDA | **GPIO19**（`bus_a`） |
| SCL | **GPIO45**（`bus_a`） |

**I2C 地址参考**（`esphome run i2c-scan.yaml` 确认）：

| 地址 | 设备 |
|------|------|
| 0x44 / 0x45 | SHT31 室内 / 室外 |
| 0x5D | GT911 触摸 |
| 0x61 | SCD30 |
| 0x20 | MCP23017 |
| **0x59** | SGP40 / SGP41 |

触摸与传感器共用总线时，建议 I2C **100kHz**（硬件包已配置），走线尽量短。

---

## 接入路径 A：继续走 Home Assistant（当前固件）

保持 [`packages/tvoc_sensor.yaml`](../packages/tvoc_sensor.yaml) 不变，在 HA 中提供 **1–6** 的 `sensor.xxx`，写入 `secrets.yaml`：

```yaml
tvoc_entity_id: "sensor.indoor_tvoc_level"
```

### VOC Index → 1–6 等级（HA Template 示例）

SGP4x 输出为 `sensor.voc_index`（名称自定）。上电稳定 **24–48h** 后，按室内环境微调阈值：

```yaml
template:
  - sensor:
      - name: "室内 TVOC 等级"
        unique_id: indoor_tvoc_level
        unit_of_measurement: "等级"
        state: >
          {% set v = states('sensor.voc_index') | float(0) %}
          {% if v < 80 %} 1
          {% elif v < 120 %} 2
          {% elif v < 160 %} 3
          {% elif v < 200 %} 4
          {% elif v < 250 %} 5
          {% else %} 6
          {% endif %}
```

将 `sensor.indoor_tvoc_level`（或你命名的实体）填入 `tvoc_entity_id`。

---

## 接入路径 B：ESPHome 本机读 SGP4x（可选扩展）

若希望 TVOC 与温湿度同机、少依赖 HA，可在 `packages/sensors.yaml` 同总线增加（示例，需自行合并到工程并去掉纯 HA 订阅或做双源）：

```yaml
sensor:
  - platform: sgp4x
    i2c_id: bus_a
    voc:
      name: "voc_index"
      id: voc_index
    compensation:
      temperature_source: temp_indoor      # 与现有 SHT31 id 对齐
      humidity_source: humidity_indoor
    update_interval: 30s

  - platform: template
    id: tvoc_level
    # ... lambda 将 id(voc_index).state 映射为 1–6 ...
```

屏显仍使用 `tvoc_level` + `main_page_refresh` 即可。具体 id 名须与 [`packages/sensors.yaml`](../packages/sensors.yaml) 一致。

---

## 路径 C：不增加 ESP 传感器

继续使用商用空气检测仪、网关或其它 HA 集成，只要实体值为 **1–6** 且 `unit_of_measurement` 与 HA 展示习惯一致即可。优点是零硬件改动；缺点是校准与协议不可控。

---

## 使用与维护建议

1. **VOC Index 是相对量**：适合判断「比平常高不高」、烹饪/清洁后是否回落，不宜当法定 TVOC µg/m³。
2. **补偿**：务必用室内温湿度（SHT31）喂给 `sgp4x` 的 `compensation`。
3. **首次上电**：指数会经历学习/稳定期，阈值映射宜在稳定后再定。
4. **与 CO₂ 联动**：CO₂ 高 + VOC 高 → 加大新风；仅 VOC 高（如酒精、清洁剂）→ 也可短时通风。自动化在 HA 完成即可。

---

## 参考链接

- [ESPHome — SGP4x](https://esphome.io/components/sensor/sgp4x/)
- [ESPHome Devices — Guition 4848S040](https://devices.esphome.io/devices/guition-esp32-s3-4848s040/)
- [Sensirion SGP41 数据手册](https://sensirion.com/products/catalog/SGP41/)
- 本项目配色与布局：[UI_LAYOUT.md](../assets/UI_LAYOUT.md)
