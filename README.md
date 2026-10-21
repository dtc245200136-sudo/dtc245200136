# Hệ Thống Quản Lý Cư Dân & Căn Hộ Chung Cư (BuildingHub) - Đề 36

Hệ thống quản lý chung cư toàn diện được đóng gói và vận hành hoàn toàn trên môi trường **Docker Compose** với 9 containers, tích hợp giải pháp giám sát hiệu năng thời gian thực (Prometheus, Grafana), thu thập log tập trung (Loki, Promtail) và áp dụng các tiêu chuẩn an toàn bảo mật (Security Hardening).

---

## 1. Kiến trúc hệ thống & Công nghệ sử dụng

* **Web Application:** Python FastAPI, Jinja2 Templates, Bootstrap 5.
* **Cơ sở dữ liệu:** PostgreSQL 15 (Chạy trên phân vùng mạng cô lập nội bộ).
* **Quản trị Database:** pgAdmin 4 (Web interface).
* **Cổng giao tiếp & Reverse Proxy:** Nginx (Cấu hình HTTPS tự cấp chứng chỉ, Security Headers).
* **Thu thập & Giám sát Metrics:** Prometheus, cAdvisor, Node Exporter.
* **Thu thập & Quản lý Log tập trung:** Promtail (Collector), Grafana Loki (Log Aggregation).
* **Trực quan hóa dữ liệu (Visualization):** Grafana Dashboard (Tích hợp PromQL & LogQL).

---

## 2. Danh sách cổng dịch vụ (Port Mapping)

| Tên Dịch Vụ | Tên Container | Cổng Host | Chức Năng |
| :--- | :--- | :--- | :--- |
| **Nginx Gateway** | `apartment_nginx` | `80`, `443` | Điểm tiếp nhận chính (Redirect HTTPS, Reverse Proxy) |
| **FastAPI Backend** | `apartment_web` | *Nội bộ (8000)* | Xử lý logic nghiệp vụ và giao diện ứng dụng |
| **PostgreSQL DB** | `apartment_db` | *Nội bộ (5432)* | Lưu trữ dữ liệu an toàn trong mạng riêng |
| **pgAdmin 4** | `apartment_pgadmin` | `5050` | Giao diện quản trị cơ sở dữ liệu trực quan |
| **Grafana** | `apartment_grafana` | `3000` | Bảng điều khiển giám sát hệ thống |
| **Prometheus** | `apartment_prometheus`| `9090` | Thu thập và xử lý chuỗi dữ liệu Metrics |
| **Loki** | `apartment_loki` | `3100` | Lưu trữ và xử lý truy vấn LogQL |
| **cAdvisor** | `apartment_cadvisor` | `8080` | Thu thập thông số phần cứng container |
| **Promtail** | `apartment_promtail` | *Nội bộ* | Đọc file log từ Nginx và đẩy về Loki |

---

## 3. Tiêu chuẩn An toàn & Bảo mật (Security Hardening)

Hệ thống được thiết kế và triển khai tuân theo các nguyên tắc bảo mật công nghiệp:

1. **Non-root Container User:**
   * Dịch vụ web ứng dụng được cấu hình chạy dưới người dùng bị giới hạn quyền `appuser` (UID: `1001`, GID: `1001`), ngăn chặn rủi ro leo thang đặc quyền khi bị tấn công.
   * *Lệnh kiểm tra:*
     ```bash
     docker exec -it apartment_web id
     ```
     *(Kết quả xác nhận: `uid=1001(appuser) gid=1001(appgroup)`)*

2. **Cô lập cơ sở dữ liệu (Network Isolation):**
   * PostgreSQL chỉ kết nối trong mạng nội bộ riêng biệt `backend_net` (`internal: true`), hoàn toàn không mở cổng kết nối trực tiếp (Port binding) ra ngoài máy Host.
   * *Lệnh kiểm tra:*
     ```bash
     docker inspect apartment_db --format='{{json .NetworkSettings.Networks}}'
     ```

3. **Cấu hình Nginx Security Response Headers:**
   * Nginx tự động đính kèm các trường header bảo vệ nhằm hạn chế các lỗ hổng Clickjacking, MIME-sniffing, và XSS:
     * `X-Frame-Options: SAMEORIGIN`
     * `X-Content-Type-Options: nosniff`
     * `X-XSS-Protection: 1; mode=block`
   * *Lệnh kiểm tra:*
     ```bash
     curl -I http://localhost
     ```

---

## 4. Giám sát & Quản trị hệ thống

### 4.1. Hệ thống Log tập trung (Loki & Promtail)
* Thu thập toàn bộ Access Log và Error Log của Nginx theo thời gian thực.
* Câu lệnh truy vấn LogQL mẫu trên Grafana:
  ```logql
  {job="nginx"}
