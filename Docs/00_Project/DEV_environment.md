# 🔹 Phase 0 — Baseline Snapshot & VM Validation

We do **NOT** modify system state yet.  
This phase ensures:

- Recoverability
- Known-good baseline
- Correct VM configuration
- No hidden instability

---

# 1️⃣ Context / Assumptions

- Kali VM already installed in **VirtualBox**
- You can log into Kali locally
- SSH may or may not be enabled yet
- No additional tools installed yet

---

# 2️⃣ Goals of Phase 0

1. Ensure VM is stable
2. Ensure networking works
3. Verify disk space
4. Verify memory allocation
5. Create a VirtualBox snapshot
6. Record baseline system metadata

---

# 3️⃣ Step-by-Step Commands & Actions

---

## Step 0.1 — Verify System Boot & Kernel

Inside Kali terminal:

```bash
uname -a
```

**Purpose:**
- Shows kernel version, architecture, and build info.

**Syntax:**
- `uname` → system info
- `-a` → show all available fields

You should see:
- `x86_64`
- Linux kernel version
- Kali build info

---

## Step 0.2 — Verify OS Release

```bash
cat /etc/os-release
```

**Purpose:**
- Confirms Kali version
- Useful for reproducibility documentation

**Syntax:**
- `cat` → print file contents
- `/etc/os-release` → OS metadata file

---

## Step 0.3 — Check Disk Space

```bash
df -h
```

**Purpose:**
- Ensure enough storage for:
  - Python builds
  - Docker images
  - CTF binaries
  - Logs

**Syntax:**
- `df` → disk filesystem usage
- `-h` → human readable (GB/MB)

Recommended:
- At least **40GB available**

---

## Step 0.4 — Check Memory

```bash
free -h
```

**Purpose:**
- Confirm RAM assigned to VM

**Syntax:**
- `free` → memory usage
- `-h` → human readable

Recommended:
- Minimum: 4GB
- Ideal: 8GB+

---

## Step 0.5 — Verify Network Connectivity

Test outbound:

```bash
ping -c 4 google.com
```

**Purpose:**
- Confirm internet connectivity

**Syntax:**
- `ping` → ICMP test
- `-c 4` → send 4 packets then stop

You should see 0% packet loss.

---

## Step 0.6 — Verify Package System Works

```bash
sudo apt update
```

**Purpose:**
- Verify repository connectivity
- Ensure no broken sources

We are NOT upgrading yet.
Just verifying.

---

## Step 0.7 — Record Baseline System State (Important)

Create baseline log:

```bash
mkdir -p ~/baseline_logs
```

Now record system info:

```bash
uname -a > ~/baseline_logs/system_info.txt
cat /etc/os-release >> ~/baseline_logs/system_info.txt
df -h >> ~/baseline_logs/system_info.txt
free -h >> ~/baseline_logs/system_info.txt
```

**Purpose:**
- Creates forensic baseline
- Helps debug later environment drift

---

## Step 0.8 — Shutdown VM

Inside Kali:

```bash
sudo shutdown now
```

**Purpose:**
- Ensure filesystem is clean before snapshot

---

# 4️⃣ VirtualBox Snapshot (Manual Step)

On host machine:

1. Open VirtualBox
2. Select Kali VM
3. Click **Snapshots**
4. Click **Take Snapshot**
5. Name it:

```
kali-clean-base
```

Optional description:

```
Fresh Kali install before dev tooling
```

---

# 5️⃣ Phase 0 Validation Checklist

Confirm:

- [ ] VM boots cleanly
- [ ] Disk ≥ 40GB free
- [ ] RAM ≥ 4GB
- [ ] Internet works
- [ ] apt update works
- [ ] Baseline logs saved
- [ ] Snapshot created

---

# 6️⃣ Why This Matters (Tech Lead Insight)

Autonomous agent development causes:

- Environment drift
- Library conflicts
- System instability
- Dependency corruption

Snapshots are your rollback parachute.

Skipping this is how projects get stuck.

---
# chatgpt response

# Phase 1 — OS Stabilization + Core Packages + uv/pipx (Option C)

## Context / Assumptions
- Phase 0 is done (baseline + snapshot).
- You prefer **Option C**: **no pyenv**, keep **system Python**, use **uv** for per-project Python/deps *if needed*, and **pipx** for global CLI tools.
- You are logged into the Kali VM as your normal user with `sudo` access.

**Stop condition:** I will not move to Phase 2 until you confirm Phase 1 is complete.

---

## 1) Update OS packages

### 1.1 Refresh package index
```bash
sudo apt update
```
- **Purpose:** Download latest package lists from configured repos.
- **Syntax:** `apt update` updates metadata only (does not install/upgrade).

### 1.2 Full upgrade (Kali-friendly)
```bash
sudo apt full-upgrade -y
```
- **Purpose:** Upgrade everything, allowing dependency changes/removals when needed (common in Kali).
- **Syntax:**  
  - `full-upgrade` may remove/replace packages to satisfy dependencies  
  - `-y` auto-answers “yes”

### 1.3 Clean up unused dependencies
```bash
sudo apt autoremove -y
```
- **Purpose:** Remove orphaned packages no longer required after upgrades.
- **Syntax:** `autoremove` targets unused dependencies.

### 1.4 Reboot to load new kernel/services
```bash
sudo reboot
```
- **Purpose:** Ensure kernel + services are running on updated versions.
- **Syntax:** `reboot` restarts immediately.

---

## 2) Install core build toolchain + Python build prerequisites

> Even without pyenv, these are still valuable because many Python packages compile native extensions, and uv-managed Python may need build deps.

### 2.1 Install build tools
```bash
sudo apt install -y build-essential
```
- **Purpose:** Installs compiler toolchain (gcc/make/etc.).
- **Syntax:** `apt install -y <pkgs…>`

### 2.2 Install libraries commonly needed for Python + native wheels
```bash
sudo apt install -y \
  libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev \
  libffi-dev liblzma-dev xz-utils tk-dev
```
- **Purpose:** Enables SSL, compression, sqlite, ffi, lzma/xz, tkinter support and helps build native deps.
- **Syntax:** `\` continues the command across lines.

---

## 3) Install core utilities (dev ergonomics + parsing tools)

```bash
sudo apt install -y \
  curl wget git git-lfs \
  unzip zip \
  tmux zsh \
  ripgrep fd-find bat fzf \
  jq yq \
  ca-certificates software-properties-common
```
- **Purpose:**  
  - `curl/wget`: download scripts/resources  
  - `git/git-lfs`: source control + large files  
  - `tmux`: persistent SSH sessions  
  - `ripgrep/fd/bat/fzf`: fast navigation/search  
  - `jq/yq`: JSON/YAML manipulation  
  - `ca-certificates`: TLS trust store for HTTPS
- **Syntax:** One `apt install` with many packages is faster and consistent.

---

## 4) Install monitoring/network basics (for agent safety)

```bash
sudo apt install -y \
  htop btop iotop iftop net-tools
```
- **Purpose:** Quickly diagnose “agent went crazy” scenarios (CPU, disk IO, network, processes).
- **Syntax:** Same as above.

---

## 5) Verify system Python (we keep OS Python as baseline)

### 5.1 Confirm version
```bash
python3 --version
```
- **Purpose:** Confirm distro Python baseline (you expect 3.13.x).
- **Syntax:** `--version` prints interpreter version.

### 5.2 Confirm path (avoid shadowed Python)
```bash
which python3
```
- **Purpose:** Ensure you’re using `/usr/bin/python3` (system-managed).
- **Syntax:** `which <cmd>` prints resolved executable path.

---

## 6) Install pipx (global Python CLI tools, isolated)(Should execute those command in a virtual environment)

### 6.1 Ensure pip is present/up to date
```bash
python3 -m pip install --upgrade pip
```
- **Purpose:** Upgrade pip for reliability (even if you rarely use it).
- **Syntax:** `python3 -m pip` runs pip bound to that interpreter.

### 6.2 Install pipx
```bash
python3 -m pip install pipx
```
- **Purpose:** Install `pipx` to manage CLI tools in isolated envs.
- **Syntax:** Standard pip install (system-level; acceptable because it’s a tool, but we’ll still avoid global deps later).

### 6.3 Add pipx binaries to PATH
```bash
pipx ensurepath
```
- **Purpose:** Ensures `~/.local/bin` is on your PATH.
- **Syntax:** `ensurepath` modifies shell config if needed.

### 6.4 Reload shell config
```bash
source ~/.bashrc
```
- **Purpose:** Apply PATH changes without logging out.
- **Syntax:** `source <file>` loads shell settings into current session.

### 6.5 Verify pipx works
```bash
pipx --version
```
- **Purpose:** Confirm installation success.

---

## 7) Install uv (fast deps + optional per-project Python)

### 7.1 Install uv
```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```
- **Purpose:** Installs `uv` to `~/.local/bin` (typical).
- **Syntax:**  
  - `-L` follow redirects  
  - `-s` silent  
  - pipe to `sh` executes installer

### 7.2 Reload shell PATH (if needed)
```bash
source ~/.bashrc
```

### 7.3 Verify uv
```bash
uv --version
```

### 7.4 Verify uv’s Python awareness (no install required yet)
```bash
uv python list
```
- **Purpose:** Confirms uv can manage Python versions if we later need to pin (e.g., 3.12) for compatibility.
- **Syntax:** `uv python <subcommand>`

---

## 8) Install global dev CLIs via pipx (safe and isolated, installed later in project level)

```bash
pipx install ruff
pipx install pytest
pipx install ipython
pipx install mypy
pipx install pre-commit
```
- **Purpose:** Tools available anywhere without contaminating project venvs.
- **Syntax:** `pipx install <package>` creates an isolated venv per tool.

### 8.1 Verify a couple tools
```bash
ruff --version
pytest --version
pre-commit --version
```

---

## 9) Optional guardrail: prevent accidental global pip installs (recommended)

### 9.1 Add a “pip safety alias” (bash)
```bash
printf "\n# Safety: discourage global pip installs\nalias pip=\"echo '❌ Use uv/venv (or pipx). Avoid global pip installs.'\"\n" >> ~/.bashrc
source ~/.bashrc
```
- **Purpose:** Prevent muscle-memory `pip install ...` from polluting system.
- **Syntax:**  
  - `printf >> ~/.bashrc` appends text  
  - `alias` overrides `pip` in shell (does not affect `python3 -m pip`)

---

## 10) Phase 1 validation (quick health checks)

```bash
git --version
tmux -V
htop --version
```
- **Purpose:** Confirm core tools are present.

---

## 11) Snapshot (strongly recommended)

### 11.1 Shutdown cleanly
```bash
sudo shutdown now
```
- **Purpose:** Ensure filesystem is consistent before snapshot.

### 11.2 VirtualBox snapshot (manual)
- Name: `kali-phase1-os-stable-uv-ready`

---

## Phase 1 completion checklist
Please confirm:
- [ ] `apt full-upgrade` finished with no repo errors
- [ ] Reboot done
- [ ] Core packages installed
- [ ] `python3 --version` shows expected 3.13.x
- [ ] `pipx --version` works
- [ ] `uv --version` works and `uv python list` runs
- [ ] (Optional) pip alias added
- [ ] Snapshot taken

Once you confirm, we’ll proceed to **Phase 2** (SSH hardening + shell ergonomics) and I’ll keep the same command-by-command style.

# chatgpt response

# Phase 2 — SSH Hardening & Shell Productivity Layer

---

## Context / Assumptions

- Phase 1 is complete (OS stable + uv + pipx ready).
- You are using **VirtualBox Kali VM**.
- You may connect:
  - From host → Kali via SSH
  - From VSCode Remote-SSH
  - From Antigravity over SSH
- We are still in **One-VM model**.

Goal of Phase 2:

> Make remote development reliable, secure, and ergonomic.

We will do:

1. SSH server validation + hardening
2. SSH key-based login setup (recommended)
3. tmux configuration
4. zsh optional improvement
5. Quality-of-life shell tooling
6. Optional firewall configuration

We will go step-by-step.

---

# 🔹 2.1 Install & Verify SSH Server

---

## Step 2.1.1 — Install SSH Server

```bash
sudo apt install -y openssh-server
```

### Purpose

Installs OpenSSH daemon (`sshd`) so you can connect remotely.

### Syntax

- `apt install -y` installs without interactive prompts.

---

## Step 2.1.2 — Enable SSH at Boot

```bash
sudo systemctl enable ssh
```

### Purpose

Ensures SSH starts automatically when VM boots.

### Syntax

- `systemctl enable <service>` registers service for auto-start.

---

## Step 2.1.3 — Start SSH Immediately

```bash
sudo systemctl start ssh
```

### Purpose

Starts SSH service now without reboot.

---

## Step 2.1.4 — Verify SSH Status

```bash
sudo systemctl status ssh
```

Expected:

```
Active: active (running)
```

Exit with `q`.

---

# 🔹 2.2 Check VM IP Address

We need this for remote SSH access.

```bash
ip a
```

Look for something like:

```
inet 192.168.x.x
```

This is your Kali VM IP.

---

# 🔹 2.3 Test SSH Locally (Self-test)

Inside Kali:

```bash
ssh localhost
```

If it connects and prompts password, SSH is working.

Exit:

```bash
exit
```

---

# 🔹 2.4 Configure SSH Hardening (Basic Safe Defaults)

---

## Step 2.4.1 — Edit SSH Config

```bash
sudo nano /etc/ssh/sshd_config
```

Modify or ensure these settings:

```
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

### What These Do

| Setting | Meaning |
|----------|----------|
| PermitRootLogin no | Prevent root login |
| PasswordAuthentication yes | Allow password login (we'll switch later if desired) |
| PubkeyAuthentication yes | Allow key-based login |
| MaxAuthTries 3 | Limit brute-force attempts |
| ClientAliveInterval 300 | Keepalive |
| ClientAliveCountMax 2 | Disconnect dead sessions |

Save and exit.

---

## Step 2.4.2 — Restart SSH

```bash
sudo systemctl restart ssh
```

---

# 🔹 2.5 Optional but Recommended — Setup SSH Key Authentication

This improves both:

- Security
- VSCode reliability
- Antigravity remote sessions

---

## Step 2.5.1 — On Your Host Machine (NOT inside Kali)

Generate key if not existing:

```bash
ssh-keygen -t ed25519
```

Press enter for defaults.

---

## Step 2.5.2 — Copy Key to Kali

From host:

```bash
ssh-copy-id username@KALI_IP
```

Replace:

- `username` with Kali username
- `KALI_IP` with VM IP

---

## Step 2.5.3 — Test Key Login

```bash
ssh username@KALI_IP
```

If it logs in without password → success.

---

## Optional: Disable Password Login (After Confirming Keys Work)

Edit SSH config again:

```bash
sudo nano /etc/ssh/sshd_config
```

Set:

```
PasswordAuthentication no
```

Restart:

```bash
sudo systemctl restart ssh
```

---

# 🔹 2.6 Install tmux (Persistent SSH Sessions)

You installed tmux earlier, now configure minimal setup.

---

## Step 2.6.1 — Create Basic tmux Config

```bash
nano ~/.tmux.conf
```

Add:

```
set -g mouse on
set -g history-limit 10000
setw -g mode-keys vi
```

Save and exit.

---

## Step 2.6.2 — Test tmux

```bash
tmux
```

Detach with:

```
Ctrl + B then D
```

Reattach:

```bash
tmux attach
```

---

# 🔹 2.7 Optional — Switch to zsh (Recommended but Optional)

Check if zsh installed:

```bash
zsh --version
```

Switch shell:

```bash
chsh -s $(which zsh)
```

Log out and back in.

---

# 🔹 2.8 Install fzf Keybinding Support

```bash
$(brew --prefix 2>/dev/null)/opt/fzf/install || /usr/share/doc/fzf/examples/install 2>/dev/null || true
```

If that fails, we skip for now.

Not critical.

---

# 🔹 2.9 Install UFW Firewall (Optional but Clean)

If VM exposed on network, do:

```bash
sudo apt install -y ufw
sudo ufw allow ssh
sudo ufw enable
```

Check status:

```bash
sudo ufw status
```

---

# 🔹 2.10 Validate Remote Dev Readiness

From host:

```bash
ssh username@KALI_IP
```

Then:

```bash
tmux
htop
```

Everything should work.

---

# Phase 2 Completion Checklist

Confirm:

- [ ] SSH service running
- [ ] Can SSH from host
- [ ] Key-based login working (if configured)
- [ ] tmux works
- [ ] Optional zsh works
- [ ] No connection drops

---

🚦 Stop here.

Confirm Phase 2 completion and report:

- Any SSH errors?
- What network mode are you using in VirtualBox? (NAT or Bridged)

# chatgpt response

Great — then Phase 3 will use **Kali repo `docker.io`**.

## Phase 3 — Step-by-step (Docker install + safety defaults)

Run these **in order** on the Kali VM. I’ll stop after Phase 3 for your confirmation.

---

### 3.1 Install Docker + Compose

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
```

- **Purpose:** installs Docker daemon/CLI and Compose.
- **Syntax:** `apt install -y <pkgs>` installs packages without prompts.

---

### 3.2 Enable + start Docker service

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

- **Purpose:** auto-start Docker on boot, start now, confirm it’s running.
- **Syntax:** `systemctl enable/start/status <service>` manages systemd services.

(Exit status view with `q`.)

---

### 3.3 Allow non-root docker (recommended for dev)

```bash
sudo usermod -aG docker $USER
newgrp docker
```

- **Purpose:** lets your user run `docker` without `sudo`.
- **Syntax:**  
  - `usermod -aG docker $USER` appends your user to docker group  
  - `newgrp docker` refreshes group membership in current shell (or log out/in)

Validate:

```bash
docker ps
```

---

### 3.4 Sanity check with a test container

```bash
docker run --rm hello-world
```

- **Purpose:** confirms daemon, image pull, networking, container lifecycle.
- **Syntax:** `--rm` cleans up container automatically.

---

### 3.5 Configure safe logging limits (prevents disk blow-ups)

```bash
sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json
```

Put this in the file:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

- **Purpose:** caps per-container logs to avoid runaway disk usage.

---

### 3.6 Quick test: run a resource-limited container

```bash
docker run -it --rm --memory="512m" --cpus="1.0" ubuntu bash
```

Inside the container:

```bash
free -h
exit
```

- **Purpose:** verifies you can enforce CPU/RAM constraints for risky workloads.
- **Syntax:** `--memory`, `--cpus` apply cgroup limits.

---

### 3.7 Create a sandbox folder + minimal compose template

```bash
mkdir -p ~/sandbox/docker
nano ~/sandbox/docker/docker-compose.yml
```

Paste:

```yaml
version: "3.8"
services:
  ctf-web:
    image: php:8.2-apache
    ports:
      - "8080:80"
    mem_limit: 512m
    cpus: 1.0
```

Start it:

```bash
cd ~/sandbox/docker
docker compose up -d
docker ps
```

Stop it:

```bash
docker compose down
```

- **Purpose:** establishes a repeatable pattern for web targets/services.

---

### 3.8 Snapshot (strongly recommended)

```bash
sudo shutdown now
```

Then take a VirtualBox snapshot named:

- `kali-phase3-docker-ready`

---

## Phase 3 completion checklist

Reply “done” when these are true:

- `systemctl status docker` shows **active (running)**
- `docker ps` works without sudo
- `hello-world` succeeds
- compose test runs and tears down cleanly
- snapshot created

Once you confirm, we’ll move to **Phase 4 (VSCode Server + Antigravity integration)**.
