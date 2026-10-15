# LANCONTROL: Complete Multi-Device & Remote Setup Manual

Welcome to **LANCONTROL**, the zero-branding autonomous remote management and MDM (Mobile Device Management) platform.

This guide details how to install and access your office/home network from anywhere, with zero or minimal technical configuration.

---

## 🚀 Scenario 1: Accessing Your Office PC From Home (Zero Router Changes)

This is the recommended, most secure way to control your office PCs and Android devices from home:

### On Your Office PC (Current Computer)
1. Launch `lancontrol_manager.pyw`.
2. Ensure the server is running (Service status: **Running**).
3. Tailscale is already installed on this machine:
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
     - **External Port:** 443 (or any custom port, e.g. 8443)
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

### 1. Normal User Mode (LANCONTROL_Client.exe)
- **Privileges Required:** Standard User (NO Admin Rights Needed).
- **Behavior:** Injects pre-configured connection policy into the PE header. Normal users simply double-click and run.
- **Features:** Remote desktop, interactive terminal, file manager.

### 2. Administrator Service Mode (LANCONTROL_Service_x64.exe)
- **Privileges Required:** Administrator (One-time setup).
- **Behavior:** Installs silent persistent Windows Service with boot auto-start.
- **Features:** Full SYSTEM control, background CMD/PowerShell, Task Manager, Sleep/Reboot, wake-on-LAN.

---

## 📱 Scenario 4: Managing Android Phones & Tablets

1. In `lancontrol_manager.pyw`, go to **Endpoint Client & Agent Generator** tab.
2. Select target host:
   - If phone has Tailscale: Select **`[Tailscale IP]`**.
   - If phone is on remote mobile data (without Tailscale): Select **`[Detect Public WAN IP]`**.
3. Click **`Download Android APK`** and install the APK on the Android device.
4. Open the LANCONTROL app on Android, tap **Scan QR Code**, and scan the on-screen code.
5. The Android device will now appear on your web dashboard with full remote screen view and device controls!

---

## ⚡ 1-Click Automated Setup for a New Office / New PC

To deploy this entire server setup onto a completely fresh machine:
1. Copy the `MESHCONTROL` folder to the new PC.
2. Run `lancontrol_manager.pyw`.
3. Click **`⚡ 1-CLICK AUTOMATED SETUP (ANY PC / ANY OFFICE)`**.
4. The system will automatically:
   - Configure local files & ports
   - Check Node.js and dependencies
   - Install & start Windows Service
   - Enable Boot & Login Autostart
   - Configure Windows Firewall rules
   - Launch the management console in your browser.
