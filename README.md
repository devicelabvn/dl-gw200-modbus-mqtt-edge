# DL-GW200 & DL-RS485 Industrial Modbus Gateway: Multi-Master Caching, Flash Store-and-Forward & MQTT Edge Payload Spec

> **Tài liệu đặc tả kỹ thuật mở (Open Engineering Reference): Kiến trúc Modbus Multi-Master Read-Cache (`< 2ms`), bộ đệm NOR Flash Store-and-Forward (`100.000` bản ghi), cấu trúc JSON Payload MQTT TLS 1.3 và hướng dẫn chuyển đổi phần cứng tương đương thay thế Moxa NPort / USR-TCP232 trên dòng thiết bị `DL-GW200`, `DL-GW400` và `DL-RS485`.**
>
> - **Đơn vị nghiên cứu & sản xuất:** **[DeviceLab](https://devicelab.vn/)** (CÔNG TY TNHH ĐẦU TƯ CÔNG NGHỆ ALPHA TECH - MST: `0111171963`)
> - **Chuyên gia biên soạn & kiểm chứng (E-E-A-T):**
>   - **[Đinh Mạnh Thảo](https://devicelab.vn/tac-gia/dinh-manh-thao/)** ([English Profile](https://devicelab.vn/en/author/dinh-manh-thao/)) - Kỹ sư Trưởng R&D Hệ thống Nhúng & Giao thức Công nghiệp (PTIT)
>   - **[Trung Nguyễn](https://devicelab.vn/tac-gia/trung-nguyen/)** ([English Profile](https://devicelab.vn/en/author/trung-nguyen/)) - Kỹ sư Trưởng Thiết kế Phần cứng & Chống nhiễu EMC/RF (ĐHBK Hà Nội - HUST)
> - **Trang thông số phần cứng chính thức:**
>   - [Bộ IoT Gateway RS485 Sang MQTT DL-GW200](https://devicelab.vn/san-pham/dl-gw200/) ([English Datasheet](https://devicelab.vn/en/products/dl-gw200/))
>   - [Bộ Chuyển Đổi RS485 Sang Ethernet DL-RS485 (Cách Ly 3.0kV)](https://devicelab.vn/san-pham/dl-rs485/) ([English Datasheet](https://devicelab.vn/en/products/dl-rs485/))
>   - [Edge IoT Gateway 4 Cổng RS485 Cách Ly DL-GW400](https://devicelab.vn/san-pham/dl-gw400/) ([English Datasheet](https://devicelab.vn/en/products/dl-gw400/))
>   - [IoT Gateway Công Nghiệp OEM Cho Nhà Tích Hợp Hệ Thống (SI)](https://devicelab.vn/gateway-oem-cho-nha-tich-hop/) ([English OEM Solution](https://devicelab.vn/en/oem-gateway-system-integrators/))

---

## 1. Phân Vai Kỹ Thuật Giữa `DL-RS485`, `DL-GW200` và `DL-GW400` Trong Tủ Điện Nhà Máy

Khi triển khai thu thập dữ liệu từ biến tần (VFD), PLC, đồng hồ điện 3 pha và cảm biến công nghiệp, việc lựa chọn đúng giữa **[bộ chuyển đổi RS485 sang Ethernet](https://devicelab.vn/kien-thuc/bo-chuyen-doi-rs485-sang-ethernet/)** và **[Modbus Gateway công nghiệp](https://devicelab.vn/kien-thuc/gateway-modbus-rs485/)** quyết định trực tiếp độ ổn định của đường bus vật lý:

| Tiêu Chí Kỹ Thuật | `DeviceLab DL-RS485` (Isolated Serial-to-Ethernet & Modbus Gateway) | `DeviceLab DL-GW200` (Industrial Modbus-to-MQTT / 4G Edge Gateway) | `DeviceLab DL-GW400` (4-Port Multi-Bus Linux/RTOS Edge Gateway) |
| :--- | :--- | :--- | :--- |
| **Vai trò cốt lõi** | Cầu nối `RS485 <-> Ethernet LAN` trong nội khu nhà máy; chuyển đổi `Modbus TCP <-> Modbus RTU` hoặc `Virtual COM`. | Đọc tự động biến tần, PLC, công tơ qua `RS485`, lưu đệm Flash và đẩy `MQTT TLS 1.3` qua `4G LTE / LAN` lên Cloud. | Thu thập đồng thời 4 nhánh `RS485` độc lập (`up to 128 Slaves`), xử lý biên (`Node-RED / Python / C`) cho tủ trung tâm. |
| **Cách ly & Chống nhiễu phần cứng** | Cách ly quang `3.0kVrms`, nguồn DC-DC cách ly độc lập, chống sét `TVS 600W` + `GDT`, cầu chì tự phục hồi `PTC`. | Cách ly quang `3.0kVrms` trên cổng RS485, chống sét lan truyền `IEC 61000-4-5`, khe SIM công nghiệp chống rung. | `4x RS485` cách ly quang `3.0kVrms` từng cổng độc lập (`Port-to-Port Isolation`), `2x Ethernet LAN`. |
| **Cơ chế chống nghẽn Bus (`Multi-Master`)** | Hỗ trợ đồng thời tới **08 kết nối Modbus TCP Master** (`SCADA`, `HMI`, `MES`) truy vấn 1 nhánh RS485 qua bộ điều phối hàng đợi. | **Polling Engine + RAM Read-Cache (`< 2ms`):** Phản hồi tức thì cho cả SCADA nội bộ (`Modbus TCP`) và Cloud (`MQTT`). | **4 luồng Polling song song (Concurrent Multi-bus Polling):** Tốc độ quét nhanh gấp 4 lần so với gom chung 1 bus. |
| **Lưu đệm khi đứt mạng (`Store & Forward`)** | Bộ đệm gói tin RAM chống xé khung (`Frame Splitting`) theo khoảng lặng `t3.5`. | **NOR Flash 100.000 bản ghi** kèm nhãn thời gian thực `RTC`; tự động truyền bù (`Backfill`) khi có mạng 4G/LAN lại. | **Flash / eMMC công nghiệp + SQLite Ring Buffer** lưu trữ hàng triệu bản ghi và truyền bù đa giao thức. |
| **Trang thông số & Báo giá** | [Xem chi tiết DL-RS485](https://devicelab.vn/san-pham/dl-rs485/) | [Xem chi tiết DL-GW200](https://devicelab.vn/san-pham/dl-gw200/) | [Xem chi tiết DL-GW400](https://devicelab.vn/san-pham/dl-gw400/) |

> 📖 **Phân tích chuyên sâu:** [Phân biệt Transparent Converter và Modbus Gateway RS485](https://devicelab.vn/kien-thuc/phan-biet-transparent-va-modbus-gateway-rs485/) · [Bộ chuyển đổi Modbus RTU sang TCP công nghiệp: Kiến trúc & Triển khai](https://devicelab.vn/kien-thuc/bo-chuyen-doi-modbus-rtu-sang-tcp/) · [Bộ chuyển đổi RS485 sang Ethernet có bộ đệm dữ liệu Store & Forward](https://devicelab.vn/kien-thuc/bo-chuyen-doi-rs485-sang-ethernet-co-bo-dem-du-lieu/)

---

## 2. Cơ Chế Modbus Multi-Master Read-Cache (`< 2ms`) Chống Xung Đột Đường Truyền RS485

Trên đường bus vật lý RS485 Half-Duplex (2 dây `A+`, `B-`), tại một thời điểm chỉ cho phép **duy nhất 01 Master** phát lệnh hỏi. Nếu vừa có màn hình HMI tại tủ điện, vừa có máy chủ SCADA phòng điều khiển (`Modbus TCP`) và luồng đọc đẩy lên Cloud (`MQTT`) cùng truy vấn xuống bus RS485 qua bộ chuyển đổi Transparent thông thường, các khung truyền sẽ đè lên nhau gây lỗi `CRC Error` và `Response Timeout`.

Trên **[Gateway Modbus sang MQTT DL-GW200](https://devicelab.vn/kien-thuc/gateway-modbus-sang-mqtt/)** và **[DL-RS485](https://devicelab.vn/san-pham/dl-rs485/)**, bài toán này được xử lý triệt để bằng kiến trúc **Multi-Master Read-Cache & Priority Write Queue**:

```text
  [HMI Tại Tủ]      [SCADA Nội Bộ (Modbus TCP:502)]      [Cloud IIoT (MQTT TLS:8883)]
       │                           │                                   │
       ▼                           ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│        TẦNG RAM READ-CACHE & COMMAND ARBITER TRÊN DL-GW200 / DL-RS485       │
│  - Lệnh ĐỌC (FC 01/02/03/04): Trả lời tức thì từ bảng RAM Cache trong < 2ms │
│    kèm kiểm tra tuổi dữ liệu (Cache TTL: 200ms – 2000ms).                   │
│  - Lệnh GHI (FC 05/06/15/16): Đưa vào hàng đợi ưu tiên cao (Priority Queue),│
│    chèn vào ngay giữa 2 chu kỳ Polling và cập nhật ngược lại RAM Cache.     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ (Duy nhất 1 luồng tuần tự, bảo toàn khoảng lặng t3.5)
                                   ▼
             [Bus RS485 Cách Ly Quang 3.0kV: Biến tần, PLC, Đồng hồ điện]
```

> 📂 Xem tệp cấu hình mẫu Multi-Master Cache tại: [`configs/dl_gw200_multimaster_cache_config.json`](./configs/dl_gw200_multimaster_cache_config.json) và [`configs/dl_rs485_modbus_tcp_rtu_bridge.json`](./configs/dl_rs485_modbus_tcp_rtu_bridge.json)

---

## 3. Đặc Tả Gói Tin JSON Payload MQTT Thời Gian Thực & Bản Tin Truyền Bù (`Backfill`)

### 3.1. Gói tin Telemetry Thời gian thực (`Topic: devicelab/{device_id}/telemetry`)

Dữ liệu đọc từ các Slave Modbus RTU được chuẩn hóa thành kiểu số thực (`Float32` / `Int32` đã nhân hệ số `scale`), gắn nhãn thời gian thực `ISO-8601` và `Unix Epoch Milliseconds` từ chip `RTC DS3231SN`:

```json
{
  "schema_ver": "2.1",
  "device_id": "DL-GW200-HN08",
  "model": "DL-GW200",
  "fw_ver": "v3.4.2-rtos",
  "seq": 108452,
  "ts_iso": "2026-11-01T14:30:00.000+07:00",
  "ts_unix_ms": 1793518200000,
  "is_backfill": false,
  "uplink": {
    "interface": "4g_lte",
    "rssi_dbm": -65,
    "flash_queue_depth": 0
  },
  "slaves": [
    {
      "unit_id": 1,
      "alias": "INVT_GD200A_PUMP_01",
      "poll_status": "OK",
      "poll_latency_ms": 18,
      "tags": {
        "freq_run_hz": 47.50,
        "current_out_a": 34.2,
        "voltage_out_v": 382.0,
        "dc_bus_v": 538.4,
        "fault_code": 0
      }
    },
    {
      "unit_id": 2,
      "alias": "SCHNEIDER_PM2230_MAIN",
      "poll_status": "OK",
      "poll_latency_ms": 22,
      "tags": {
        "v_l1_n": 221.4,
        "v_l2_n": 220.8,
        "v_l3_n": 221.9,
        "i_avg_a": 128.5,
        "kw_total": 81.42,
        "pf_total": 0.96,
        "kwh_import": 458920.5
      }
    }
  ]
}
```

### 3.2. Gói tin Truyền bù khi khôi phục mạng (`Topic: devicelab/{device_id}/backfill`)

Khi mất kết nối Internet/4G hoặc MQTT Broker bảo trì, `DL-GW200` tự động nén các bản ghi vào vùng nhớ vòng **NOR Flash (100.000 bản ghi)**. Ngay khi phiên kết nối `MQTT TLS 1.3 (QoS 1)` được thiết lập lại, thiết bị đẩy bù theo lô (`Batch Backfill`) với cờ `"is_backfill": true` và chuỗi số thứ tự `"seq"` liên tục để Server dễ dàng chống trùng lặp (`Idempotent Deduplication`):

> 📂 Xem mẫu gói tin truyền bù tại: [`payloads/dl_gw200_store_forward_backfill_batch.json`](./payloads/dl_gw200_store_forward_backfill_batch.json)  
> 🐍 Xem mã nguồn Python xử lý nhận dữ liệu và khử trùng lặp tại: [`examples/mqtt_tls_ingestor_backfill_handler.py`](./examples/mqtt_tls_ingestor_backfill_handler.py)

---

## 4. Bảng Đối Chiếu Thay Thế Tương Đương `Moxa NPort 5150 / 5130 / 5232`, `USR-TCP232` & `ZLAN5143D`

Trong các dự án cải tạo tủ điện nhà máy (`Retrofit`) hoặc lập hồ sơ thầu M&E, kỹ sư thường gặp tình trạng các mã Serial Server nhập khẩu (`Moxa NPort 5130 / 5150 / 5232`) có thời gian đặt hàng kéo dài `6–10 tuần` và giá thành cao, trong khi các dòng giá rẻ (`USR-TCP232-304 / 410S`, `ZLAN5143D`, `ATC-1200`) lại **không có cách ly quang (Non-isolated)** nên dễ treo cổng hoặc cháy chip UART khi lắp cạnh biến tần.

Dưới đây là bảng tra cứu chuyển đổi chân đấu nối (`Pinout Migration`) sang **[DeviceLab DL-RS485](https://devicelab.vn/san-pham/dl-rs485/)** (luôn sẵn hàng tại Hà Nội, cách ly quang `3.0kVrms` tiêu chuẩn):

| Mã Thiết Bị Cũ Cần Thay Thế | Kiểu Cổng & Hạn Chế Thực Tế | Mã Thay Thế Tương Đương Tại DeviceLab | Sơ Đồ Chuyển Đổi Đấu Nối Sang Cầu Đấu Rời `DL-RS485` |
| :--- | :--- | :--- | :--- |
| **`Moxa NPort 5130` / `NPort 5150`** | Cổng `DB9 Male` (phải hàn giắc DB9, bản tiêu chuẩn không có cách ly quang 3kV). | **[`DL-RS485`](https://devicelab.vn/san-pham/dl-rs485/)** (1 cổng RS485/RS422 cách ly `3.0kVrms`, vỏ DIN-Rail). | - Chân `Pin 3 (Data+)` trên DB9 Moxa -> Đấu vào chân **`A+`** trên `DL-RS485`<br>- Chân `Pin 4 (Data-)` trên DB9 Moxa -> Đấu vào chân **`B-`** trên `DL-RS485`<br>- Chân `Pin 5 (GND)` trên DB9 Moxa -> Đấu vào chân **`GND_ISO`** trên `DL-RS485` |
| **`Moxa NPort 5232` / `NPort 5450`** | 2–4 cổng RS485, thời gian nhập hàng lâu, chi phí đầu tư cao. | **[`DL-GW400`](https://devicelab.vn/san-pham/dl-gw400/)** (4 cổng RS485 cách ly độc lập `3.0kVrms`) hoặc `2x DL-RS485`. | Đấu trực tiếp từng cặp dây xoắn `A+ / B- / GND_ISO` vào 4 cầu đấu Phoenix rời rạc trên `DL-GW400`. |
| **`USR-TCP232-304` / `USR-TCP232-410S` / `USR-DR302`** | Không có cách ly quang `3.0kV` và nguồn cách ly DC-DC; hay bị treo khi đóng cắt khởi động từ / biến tần. | **[`DL-RS485`](https://devicelab.vn/san-pham/dl-rs485/)** (nếu truyền LAN nội bộ) hoặc **[`DL-GW200`](https://devicelab.vn/san-pham/dl-gw200/)** (nếu đẩy MQTT / 4G). | Giữ nguyên dây `A+`, `B-` và bổ sung đấu dây bọc kim/mass tín hiệu vào chân `GND_ISO` + chân tiếp địa vỏ tủ `PE` để kích hoạt tầng chống sét `TVS 600W`. |
| **`ZLAN5143D` / `ATC-1000` / `ATC-1200`** | Không có bộ nhớ đệm Flash lưu trữ ngoại tuyến (`Store & Forward`) khi đứt mạng LAN. | **[`DL-GW200`](https://devicelab.vn/san-pham/dl-gw200/)** (lưu đệm `100.000` bản ghi Flash + Multi-Master Cache). | Chuyển dây `A+`, `B-` sang cổng `RS485-1` của `DL-GW200`; bật tính năng `Modbus TCP Server Bridge (Port 502)` trên Web GUI. |

> 📖 **Đọc bài phân tích chi tiết:** [Giải pháp thay thế Moxa NPort 5150, 5130, 5232 & USR-TCP232 bằng bộ chuyển đổi cách ly công nghiệp](https://devicelab.vn/kien-thuc/giai-phap-thay-the-moxa-nport-5150-usr-tcp232-cho-tu-dien-cong-nghiep/) ([English Guide](https://devicelab.vn/en/articles/moxa-nport-5150-usr-tcp232-alternative-industrial-isolated-converter/)) · [So sánh Gateway COTS (Moxa, USR, 3Onedata) với Gateway tùy biến theo dự án](https://devicelab.vn/kien-thuc/so-sanh-gateway-cots-moxa-usr-3onedata-voi-gateway-tuy-bien/)

---

## 5. Danh Mục Tài Liệu Kỹ Thuật Chuyên Sâu Trên `devicelab.vn`

### A. Cụm Bộ Chuyển Đổi RS485 Sang Ethernet & Modbus Gateway (`Cluster 1`)
- [Bộ chuyển đổi RS485 sang Ethernet công nghiệp: Tiêu chí chọn & Sơ đồ đấu nối](https://devicelab.vn/kien-thuc/bo-chuyen-doi-rs485-sang-ethernet/) ([English](https://devicelab.vn/en/articles/rs485-to-ethernet-converter-selection-guide/))
- [Modbus Gateway RS485 & 4G công nghiệp: Kiến trúc & Cách chọn](https://devicelab.vn/kien-thuc/gateway-modbus-rs485/) ([English](https://devicelab.vn/en/articles/modbus-rs485-gateway-selection-and-customization/))
- [Top 5 bộ chuyển đổi RS485 sang Ethernet công nghiệp tốt nhất](https://devicelab.vn/kien-thuc/top-bo-chuyen-doi-rs485-sang-ethernet-cong-nghiep/)
- [Bảng giá bộ chuyển đổi RS485 sang Ethernet theo 3 phân khúc](https://devicelab.vn/kien-thuc/gia-bo-chuyen-doi-rs485-sang-ethernet/)
- [So sánh bộ chuyển đổi RS485 dân dụng và công nghiệp: Khác biệt từ bo mạch](https://devicelab.vn/kien-thuc/so-sanh-bo-chuyen-doi-rs485-dan-dung-va-cong-nghiep/)
- [Hướng dẫn cấu hình bộ chuyển đổi RS485 sang Ethernet qua Web GUI](https://devicelab.vn/kien-thuc/huong-dan-cau-hinh-bo-chuyen-doi-rs485-sang-ethernet/)
- [Cài đặt Virtual COM Port cho bộ chuyển đổi RS485 sang Ethernet](https://devicelab.vn/kien-thuc/cai-dat-virtual-com-port-rs485-ethernet/)
- [Kỹ thuật chống nhiễu RS485 bằng cách ly quang 3.0kV và xử lý nhiễu biến tần](https://devicelab.vn/kien-thuc/chong-nhieu-rs485-cach-ly-quang/)
- [Tiêu chuẩn chọn bộ chuyển đổi RS485 cho hồ sơ thầu M&E](https://devicelab.vn/kien-thuc/tieu-chuan-chon-bo-chuyen-doi-rs485-cho-ho-so-thau-me/)

### B. Cụm Thiết Kế Mạch PCB, Sản Xuất PCBA & Lập Trình Nhúng OEM/ODM (`Cluster 6, 7, 8`)
- [Dịch vụ thiết kế mạch điện tử & Layout PCB chuẩn công nghiệp](https://devicelab.vn/thiet-ke-mach-dien-tu/) · [Bài Pillar: Dịch vụ thiết kế PCB & Vẽ mạch nguyên lý](https://devicelab.vn/kien-thuc/dich-vu-thiet-ke-pcb/) ([English](https://devicelab.vn/en/articles/custom-pcb-design-service-vietnam/))
- [Gia công PCB & Hàn mạch SMT/PCBA chính xác cao](https://devicelab.vn/gia-cong-pcb/) · [Bài Pillar: Sản xuất bo mạch điện tử công nghiệp](https://devicelab.vn/kien-thuc/san-xuat-bo-mach-dien-tu-cong-nghiep/) ([English](https://devicelab.vn/en/articles/electronic-circuit-board-manufacturing-vietnam/))
- [Dịch vụ lập trình Firmware nhúng C/C++ & RTOS](https://devicelab.vn/phat-trien-firmware/) · [Bài Pillar: Công ty lập trình nhúng & Thiết kế Firmware IoT](https://devicelab.vn/kien-thuc/cong-ty-lap-trinh-nhung-firmware-iot/) ([English](https://devicelab.vn/en/articles/embedded-systems-programming-company-vietnam/))
- [Build vs Buy phần cứng IIoT: Phân tích TCO & MOQ cho doanh nghiệp](https://devicelab.vn/kien-thuc/cots-vs-custom-industrial-iot/)

---

## 6. Liên Hệ Đội Ngũ Kỹ Sư R&D DeviceLab (Đặt Mẫu PoC / Mượn Thiết Bị Test 7 Ngày)

- **Đơn vị sản xuất:** CÔNG TY TNHH ĐẦU TƯ CÔNG NGHỆ ALPHA TECH (**[DeviceLab](https://devicelab.vn/)**) - Mã số thuế: `0111171963`
- **Địa chỉ Phòng Lab:** Số 32/4, Hà Trì 4, Phường Hà Đông, TP. Hà Nội, Việt Nam
- **Hotline / Zalo Kỹ sư trưởng ([Đinh Mạnh Thảo](https://devicelab.vn/tac-gia/dinh-manh-thao/)):** `0982 503 355`
- **Email:** `contact@devicelab.vn` | `hi@devicelab.vn`
- **Gửi yêu cầu báo giá dự án SI / OEM:** [https://devicelab.vn/gui-yeu-cau/](https://devicelab.vn/gui-yeu-cau/)

---

## Industrial IoT Hardware, Telemetry & Custom R&D Reference Index (DeviceLab Vietnam)

Official open engineering reference hubs, hardware datasheets, and compliance application notes maintained by **DeviceLab R&D Center** (Hanoi, Vietnam):

### 1. Industrial RS485, Modbus RTU/TCP & Edge Gateways
- [Bộ chuyển đổi RS485 sang Ethernet công nghiệp (Cách ly 3.0kV & Modbus RTU/TCP)](https://devicelab.vn/kien-thuc/bo-chuyen-doi-rs485-sang-ethernet/)
- [Thiết bị chuyển đổi tín hiệu RS485 cách ly DL-RS485 (Datasheet & Sơ đồ đấu nối)](https://devicelab.vn/san-pham/dl-rs485/)
- [Cẩm nang chọn Gateway Modbus RS485 sang Ethernet/4G LTE công nghiệp](https://devicelab.vn/kien-thuc/gateway-modbus-rs485/)
- [Bộ chuyển đổi Modbus RTU sang Modbus TCP: Kiến trúc Polling & Multi-Master](https://devicelab.vn/kien-thuc/bo-chuyen-doi-modbus-rtu-sang-tcp/)
- [Tiêu chuẩn cáp tín hiệu RS485 chống nhiễu 120 Ohm (22AWG/24AWG STP)](https://devicelab.vn/kien-thuc/cap-tin-hieu-rs485-chong-nhieu-tieu-chuan-chon/)
- [Đối chiếu thay thế Moxa MGate MB3180, Advantech EKI-1221, USR & 3onedata](https://devicelab.vn/kien-thuc/so-sanh-thay-the-modbus-gateway-moxa-mgate-advantech-usr-3onedata/)
- [Bộ chuyển đổi 4-20mA Analog sang RS485 Modbus & Module Remote I/O](https://devicelab.vn/kien-thuc/bo-chuyen-doi-4-20ma-analog-sang-rs485-remote-io-modbus/)
- [Industrial RS485 to Ethernet Converter Selection Guide (English)](https://devicelab.vn/en/articles/rs485-to-ethernet-converter-selection-guide/)

### 2. Circular 10/2021/TT-BTNMT Environmental Telemetry & SCADA RTU
- [Giải pháp Datalogger quan trắc môi trường tự động chuẩn Thông tư 10/2021/TT-BTNMT](https://devicelab.vn/datalogger-quan-trac-moi-truong-tt10/)
- [Kiến trúc trạm quan trắc nước thải tự động, liên tục & kết nối FTP Sở TN&MT](https://devicelab.vn/kien-thuc/datalogger-quan-trac-nuoc-thai-tu-dong/)
- [Thiết bị Datalogger quan trắc môi trường DL-ENV10 (Datasheet PDF)](https://devicelab.vn/san-pham/dl-env10/)
- [Quy chuẩn nước thải công nghiệp QCVN 40:2025/BTNMT & lộ trình quan trắc tự động](https://devicelab.vn/kien-thuc/quy-chuan-nuoc-thai-cong-nghiep-qcvn-40-quan-trac-tu-dong/)
- [Data logger nhiệt độ đa kênh PT100 (RTD 3 dây) & bộ ghi nhiệt độ công nghiệp](https://devicelab.vn/kien-thuc/data-logger-nhiet-do-da-kenh-pt100-bo-ghi-nhiet-do-cong-nghiep/)
- [Tủ RTU & Thiết bị Remote Terminal Unit SCADA cho nhà máy nước, thủy điện](https://devicelab.vn/kien-thuc/tu-rtu-thiet-bi-remote-terminal-unit-scada-nha-may-nuoc-thuy-dien/)
- [Hệ thống quan trắc nước ngầm tự động giếng khoan chuẩn Nghị định 53/2024/NĐ-CP](https://devicelab.vn/kien-thuc/he-thong-quan-trac-nuoc-ngam-tu-dong/)
- [Giải pháp thay thế Datalogger Campbell Scientific CR1000X / CR300 OEM Việt Nam](https://devicelab.vn/kien-thuc/giai-phap-thay-the-datalogger-campbell-cr1000x-cr300-oem-viet-nam/)
- [Circular 10 Environmental Monitoring Datalogger Solution (English)](https://devicelab.vn/en/environmental-monitoring-datalogger/)

### 3. 3-Phase Power Metering, Solar Zero Export & PLC OEE Telemetry
- [Hệ thống giám sát điện năng nhà máy 3 pha & quản lý năng lượng EMS ISO 50001](https://devicelab.vn/giam-sat-dien-nang-nha-may/)
- [Hướng dẫn chọn đồng hồ đo điện 3 pha RS485 Modbus & thanh ghi chuẩn](https://devicelab.vn/kien-thuc/dong-ho-do-dien-3-pha-rs485-giam-sat-dien-nang/)
- [Bộ điều khiển công suất phát PPC, SmartLogger 3000 & Zero Export SCADA EVN](https://devicelab.vn/kien-thuc/bo-dieu-khien-cong-suat-phat-ppc-smartlogger-3000-zero-export-evn/)
- [Thiết bị thu thập dữ liệu PLC (Siemens, Mitsubishi, Delta) & IoT Gateway](https://devicelab.vn/kien-thuc/thiet-bi-thu-thap-du-lieu-plc-iot-gateway/)
- [Hệ thống giám sát máy móc sản xuất Andon OEE thời gian thực](https://devicelab.vn/kien-thuc/he-thong-giam-sat-may-moc-san-xuat-andon-oee/)

### 4. Custom PCB Design, Turnkey PCBA SMT & Embedded Firmware R&D (Hanoi, Vietnam)
- [Dịch vụ thiết kế mạch điện tử theo yêu cầu & phát triển phần cứng công nghiệp](https://devicelab.vn/thiet-ke-mach-dien-tu/)
- [Công ty thiết kế mạch điện tử tại Hà Nội: Năng lực Lab R&D, EMC & Sản xuất OEM](https://devicelab.vn/kien-thuc/cong-ty-thiet-ke-mach-dien-tu-ha-noi/)
- [Dịch vụ thiết kế PCB 2-8 lớp & vẽ mạch nguyên lý chuẩn IPC-2221](https://devicelab.vn/kien-thuc/dich-vu-thiet-ke-pcb/)
- [Quy trình đặt làm mạch điện tử theo yêu cầu từ EVT/DVT đến sản xuất hàng loạt](https://devicelab.vn/kien-thuc/lam-mach-dien-tu-theo-yeu-cau/)
- [Gia công PCB & hàn mạch điện tử SMT (PCBA) trọn gói tại Việt Nam](https://devicelab.vn/gia-cong-pcb/)
- [Dịch vụ lập trình Firmware nhúng (STM32, ESP32, FreeRTOS, Embedded Linux)](https://devicelab.vn/phat-trien-firmware/)
- [Công ty lập trình nhúng, Firmware & IoT công nghiệp tại Việt Nam](https://devicelab.vn/kien-thuc/cong-ty-lap-trinh-nhung-firmware-iot/)
- [Custom PCB Design & Turnkey Electronics Engineering in Vietnam (English)](https://devicelab.vn/en/custom-pcb-design/)

### 5. Community Engineering Publications (Viblo, Dev.to & Tinh Tế)
- [Viblo: Kỹ thuật chống nhiễu RS485, tính toán Bias & cách ly 2500Vrms](https://viblo.asia/p/ky-thuat-chong-nhieu-rs485-trong-nha-may-tinh-toan-dien-tro-pull-uppull-down-va-cach-ly-quang-2500vrms-bA46807wLKv)
- [Viblo: Kiến trúc Store-and-Forward & Ring-Buffer Flash cho Datalogger Thông tư 10](https://viblo.asia/p/kien-truc-store-and-forward-cho-datalogger-quan-trac-moi-truong-thong-tu-102021tt-btnmt-chong-mat-du-lieu-khi-dut-cap-4g-kNLr3eobVgA)
- [Viblo: Đọc đồng hồ điện 3 pha Selec, Schneider, Eastron qua RS485 & MQTT](https://viblo.asia/p/doc-dong-ho-dien-3-pha-selec-schneider-eastron-qua-modbus-rtu-va-day-mqtt-len-cloud-bang-python-c-OXLA0WqvJGr)
- [Viblo: Checklist 12 điểm kiểm tra Schematic & Layout PCB công nghiệp vượt chuẩn EMC](https://viblo.asia/p/checklist-12-diem-kiem-tra-schematic-layout-pcb-cong-nghiep-truoc-khi-gui-fab-de-vuot-bai-test-emc-iec-61000-4-wd43EXawLX9)
- [Dev.to: Designing Industrial RS485 Circuits for High-EMI Factory Environments](https://dev.to/devicelabvn/designing-industrial-rs485-circuits-for-high-emi-factory-environments-2500vrms-isolation-600w-2114)
- [Dev.to: Store-and-Forward Telemetry Architecture for Environmental Monitoring Dataloggers](https://dev.to/devicelabvn/store-and-forward-telemetry-architecture-for-environmental-monitoring-dataloggers-circular-4b2i)
