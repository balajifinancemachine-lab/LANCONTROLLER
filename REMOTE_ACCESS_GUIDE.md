# LANController: Complete Multi-Device & Remote Setup Manual

Welcome to **LANController**, the zero-branding autonomous remote management and MDM (Mobile Device Management) platform.

This guide details how to install, manage, and access your office/home network from anywhere, with zero or minimal technical configuration.

---

## ⚡ Standalone Architecture
`LANController.pyw` is a **100% self-contained, single-file executable**.
- **Self-Healing Dependencies**: Automatically bootstraps required libraries (`pillow`, `pystray`, `qrcode`, `cryptography`) on startup.
- **Zero External Dependencies**: Works out-of-the-box on clean Windows 10/11 and Windows Server installations.
- **Embedded Assets**: Includes embedded high-DPI branding and automatic configuration generation.

---

## 🚀 Scenario 1: Accessing Your Office PC From Home (Zero Router Changes)

This is the recommended, most secure way to control your office PCs and Android devices from home:

### On Your Office PC (Current Computer)
1. Launch `LANController.pyw`.
2. Ensure the server is running (Service status: **Running**).
3. Tailscale is installed on this machine:
   - Your Office Tailscale IP: `100.113.51.119`
   - Your Office MagicDNS: `dilip.taila95d71.ts.net`
   - Account: `finance.balaji.jmd@gmail.com`

### On Your Home PC (Different Location)
1. Download Tailscale from: [https://tailscale.com/download](https://tailscale.com/download)
2. Log in using the **exact same account**: `finance.balaji.jmd@gmail.com`
3. Open your browser on your Home PC and visit:
   ```
   https://100.113.51.119/
   ```
   *(or `https://dilip.taila95d71.ts.net/`)*
4. Log in with your admin username and password. You now have full desktop control, terminal access, and file transfer over your office PC!

---

## 🌐 Scenario 2: Accessing Without Tailscale (Direct Public Internet)

If you cannot install Tailscale on your Home PC:

1. **Enable Port Forwarding on Office Router:**
   - Open your office router admin settings (`http://192.168.0.1`).
   - Add a Port Forward rule:
     - **External Port:** 443 (or custom port, e.g. 8443)
     - **Internal IP:** `192.168.0.158` (Office PC)
     - **Internal Port:** 443
     - **Protocol:** TCP
2. **Accessing from Home:**
   - Open browser on Home PC and go to:
     ```
     https://103.235.2.100/
     ```
   *(Note: If your ISP provides dynamic IPs, set up a free Dynamic DNS hostname like DuckDNS or No-IP).*

---

## 💻 Scenario 3: Deploying to Other Office/Client PCs

### 1. Normal User Mode (LANController_Client.exe)
- **Privileges Required:** Standard User (NO Admin Rights Needed).
- **Behavior:** Injects pre-configured connection policy into the PE header. Normal users simply double-click and run.
- **Features:** Remote desktop, interactive terminal, file manager.

### 2. Administrator Service Mode (LANController_Service_x64.exe)
- **Privileges Required:** Administrator.
- **Behavior:** Installs as an autonomous background Windows Service. Survives reboots and user logouts.
- **Features:** Full unattended remote access, pre-boot control, user switching.

---

## 📱 Scenario 4: Managing Android Mobile Devices (MDM)
1. Open the **Deploy & Packaging** tab in `LANController.pyw`.
2. Click **Generate Android Pairing QR Code** (or copy pairing URL).
3. Install the **MeshCentral Agent** app from Google Play Store or APK on the Android phone.
4. Scan the QR code or paste the pairing URL.
5. Grant permissions:
   - Device Administration & Remote Screen viewing
   - Background service execution
6. The phone now appears in your LANController management console!
