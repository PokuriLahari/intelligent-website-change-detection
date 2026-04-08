# ☁️ AWS Deployment Guide (Free Tier)

This guide walks you through deploying your **WatchDog Website Monitor** to AWS using the **Amazon EC2 Free Tier**. This approach requires **zero code changes**.

---

## Step 1: Launch an EC2 Instance

1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Search for **EC2** in the top search bar and click on it.
3. Click the orange **Launch instance** button.
4. **Name:** Enter a name like `website-monitor-server`.
5. **AMI (OS):** Select **Ubuntu**, then choose **Ubuntu Server 22.04 LTS** or **24.04 LTS** (ensure it says "Free tier eligible").
6. **Instance Type:** Select **t2.micro** or **t3.micro** (Free tier eligible).
7. **Key Pair (Login):** 
   - Click **Create new key pair**.
   - Name it `monitor-key`.
   - Leave it as RSA / .pem.
   - Click **Create key pair** (this downloads a file to your computer; keep it safe!).

## Step 2: Configure Network & Security Group

Scroll down clearly to **Network settings**:
1. Check **Allow SSH traffic** from **Anywhere**.
2. Check **Allow HTTPS traffic from the internet**.
3. Check **Allow HTTP traffic from the internet**.
4. Click **Edit** in the Network settings panel, scroll down to bottom, and click **Add security group rule**.
   - Type: **Custom TCP**
   - Port range: **5000**
   - Source type: **Anywhere** (0.0.0.0/0)
   *(This allows you to view the Flask dashboard externally).*
5. Click **Launch instance** at the bottom right.

---

## Step 3: Connect to Your Server

1. Once the instance says "Running" on the EC2 Dashboard, click on its **Instance ID**.
2. Click the **Connect** button at the top.
3. Use **EC2 Instance Connect** (the easiest way directly in your browser) and click **Connect**.
   *(Alternatively, you can SSH from your local terminal using the `.pem` key you downloaded).*

---

## Step 4: Prepare the Server

In the black SSH terminal, run the following commands to update the server and install Python:

```bash
# Update server
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git -y
```

---

## Step 5: Get Your Code on the Server

You have two options: Git (recommended) or SCP.

**Option A (Using Git if your code is on GitHub):**
```bash
git clone https://github.com/YourUsername/website-monitor.git
cd website-monitor
```

**Option B (Uploading files directly if not using Git):**
You can zip your local project (excluding `.venv`, `__pycache__`) and upload it securely. An easy way without the command line is dropping a zip in AWS CloudShell or copying via SCP:
```bash
scp -i monitor-key.pem -r .\website-monitor ubuntu@YOUR_PUBLIC_IP:~
```

---

## Step 6: Setup & Run the App

Once inside your `website-monitor` folder on the server:

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create your `.env` file:**
```bash
nano .env
```
Paste your email config into the file:
```env
SMTP_USER=your-email@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx
ALERT_FROM=your-email@gmail.com
ALERT_TO=your-email@gmail.com
```
Press `CTRL + O`, `Enter` to save, and `CTRL + X` to exit.

3. **Run the server in the background:**
To keep the app running even after you close the terminal window, use `nohup`:
```bash
nohup python3 app.py > output.log 2>&1 &
```

---

## Step 7: Access Your Dashboard!

1. Go back to your AWS EC2 Dashboard.
2. Find the **Public IPv4 address** of your instance (e.g., `3.141.59.26`).
3. Open your browser and go to:
   **http://YOUR_PUBLIC_IP:5000**

You should see your WatchDog Website Monitor 🐕 running live on the cloud!

---

### Helpful Commands for the Server:
*   **See logs:** `cat output.log`
*   **Stop the app:** 
    ```bash
    pkill -f "python3 app.py"
    ```
*   **Restart the app:** Kill it, then run the `nohup` command again.
