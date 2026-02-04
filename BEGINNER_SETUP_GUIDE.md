# Complete Beginner's Setup Guide
## DataCenter Intelligence Platform - Step-by-Step Instructions

**For people who have never used Python before** 👋

---

## What We're Going to Do

1. Check if Python is installed (2 minutes)
2. Install Python if needed (5 minutes)
3. Open a terminal/command prompt (1 minute)
4. Navigate to the project folder (2 minutes)
5. Install the required software (3-5 minutes)
6. Run the application (1 minute)
7. Open it in your web browser (1 minute)

**Total time: 15-20 minutes**

---

## Step 1: Check if Python is Already Installed

### On Windows:

1. **Press the Windows key** (on your keyboard)
2. **Type:** `cmd`
3. **Press Enter** - A black window will open (this is the "Command Prompt")
4. **Type this command and press Enter:**
   ```
   python --version
   ```

5. **What you'll see:**
   - ✅ If you see something like `Python 3.11.5` or `Python 3.9.7` → **Great! Python is installed. Skip to Step 3.**
   - ❌ If you see an error like `'python' is not recognized` → **Go to Step 2 to install Python**

### On Mac:

1. **Press Command + Space** (opens Spotlight search)
2. **Type:** `terminal`
3. **Press Enter** - A white or black window will open
4. **Type this command and press Enter:**
   ```
   python3 --version
   ```

5. **What you'll see:**
   - ✅ If you see something like `Python 3.11.5` or `Python 3.9.7` → **Great! Python is installed. Skip to Step 3.**
   - ❌ If you see an error → **Go to Step 2 to install Python**

### On Linux:

1. **Press Ctrl + Alt + T** (opens Terminal)
2. **Type this command and press Enter:**
   ```
   python3 --version
   ```

3. **What you'll see:**
   - ✅ If you see something like `Python 3.11.5` or `Python 3.9.7` → **Great! Python is installed. Skip to Step 3.**
   - ❌ If you see an error → **Go to Step 2 to install Python**

---

## Step 2: Install Python (if needed)

### On Windows:

1. **Go to:** https://www.python.org/downloads/
2. **Click the big yellow button** that says "Download Python 3.X.X"
3. **Wait for the download** (about 25 MB)
4. **Double-click the downloaded file** (in your Downloads folder)
5. **IMPORTANT:** Check the box that says **"Add Python to PATH"** ✅
6. **Click "Install Now"**
7. **Wait 2-3 minutes** for installation to complete
8. **Click "Close"**
9. **Restart your Command Prompt** (close and open it again)
10. **Test it worked:**
    ```
    python --version
    ```
    You should see: `Python 3.X.X`

### On Mac:

**Option 1: Using Homebrew (Recommended)**

1. **Open Terminal** (Command + Space, type "terminal", press Enter)
2. **Install Homebrew** by copying this entire command and pressing Enter:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. **Wait for it to install** (2-3 minutes)
4. **Install Python:**
   ```bash
   brew install python3
   ```
5. **Test it worked:**
   ```bash
   python3 --version
   ```

**Option 2: Download Directly**

1. **Go to:** https://www.python.org/downloads/macos/
2. **Click "Download Python 3.X.X"**
3. **Open the downloaded .pkg file**
4. **Follow the installation wizard** (keep clicking "Continue" then "Install")
5. **Test it worked:**
   ```bash
   python3 --version
   ```

### On Linux (Ubuntu/Debian):

1. **Open Terminal** (Ctrl + Alt + T)
2. **Update package list:**
   ```bash
   sudo apt update
   ```
3. **Install Python:**
   ```bash
   sudo apt install python3 python3-pip -y
   ```
4. **Test it worked:**
   ```bash
   python3 --version
   ```

---

## Step 3: Open Terminal/Command Prompt

### Windows:
1. **Press Windows key**
2. **Type:** `cmd`
3. **Press Enter**

### Mac:
1. **Press Command + Space**
2. **Type:** `terminal`
3. **Press Enter**

### Linux:
1. **Press Ctrl + Alt + T**

---

## Step 4: Navigate to the Project Folder

You need to tell the computer where the project files are.

### Find the Project Location

The project is located at:
```
/home/user/datacenterdatabase
```

### Navigate There:

**On Windows:**
```
cd C:\Users\user\datacenterdatabase
```
*(Replace `C:\Users\user` with your actual path if different)*

**On Mac/Linux:**
```bash
cd /home/user/datacenterdatabase
```

**Or, if you don't know the path:**

1. **Open File Explorer (Windows) or Finder (Mac)**
2. **Find the `datacenterdatabase` folder**
3. **Drag and drop the folder** into your terminal window
4. The path will appear automatically!
5. Just type `cd ` (with a space) before the path and press Enter

---

## Step 5: Install Required Software

Now we'll install all the software packages the application needs.

### Copy and Paste This Command:

**On Windows:**
```
pip install -r requirements.txt
```

**On Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

### Press Enter and Wait

You'll see a lot of text scrolling by - this is normal! It's downloading and installing packages.

**This will take 2-5 minutes depending on your internet speed.**

### What You'll See:

```
Collecting Flask>=3.0.0
Downloading Flask-3.0.0-py3-none-any.whl
Collecting pandas>=2.0.0
Downloading pandas-2.0.0-cp311-cp311-win_amd64.whl
...
Successfully installed Flask-3.0.0 pandas-2.0.0 ...
```

### If You Get an Error:

**Error: "pip is not recognized" or "command not found"**

**Fix for Windows:**
```
python -m pip install -r requirements.txt
```

**Fix for Mac/Linux:**
```bash
python3 -m pip install -r requirements.txt
```

**Error: "Permission denied" or "Access denied"**

**Fix for Mac/Linux:**
```bash
pip3 install --user -r requirements.txt
```

**Fix for Windows:** Right-click Command Prompt and select "Run as Administrator", then try again.

---

## Step 6: Run the Application

Almost there! Now we start the web application.

### Type This Command:

**On Windows:**
```
python app.py
```

**On Mac/Linux:**
```bash
python3 app.py
```

### Press Enter

### What You'll See:

```
Initializing database...
Running initial data update...
Scraping ERCOT data...
Scraping PJM data...
Found 11 data center projects
Background update worker started (interval: 6 hours)
Starting Flask application...
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**This means it's working!** 🎉

**Don't close this window!** The application is running here. If you close it, the application stops.

---

## Step 7: Open the Application in Your Browser

### Open Your Web Browser

Use **Chrome**, **Firefox**, **Safari**, **Edge**, or any modern browser.

### Type This in the Address Bar:

```
http://localhost:5000
```

**Or try:**
```
http://127.0.0.1:5000
```

### Press Enter

**You should see the DataCenter Intelligence Platform home page!** 🎉

---

## What You'll See in the Application

### Home Page
- Statistics box showing total projects, capacity, etc.
- Feature descriptions
- "Launch Dashboard" button

### Click Around:
- **Dashboard** → Interactive map with data centers
- **Operators** → Companies and their projects
- **Analytics** → Charts and graphs

### Try the Filters:
- Filter by state (Texas, Virginia, etc.)
- Filter by status (Operational, Construction, etc.)
- Filter by verification status

---

## Common Questions

### Q: How do I stop the application?

**A:** In the terminal/command prompt window where it's running:
- **Press Ctrl + C** (works on Windows, Mac, Linux)
- You'll see: `KeyboardInterrupt` or `Shutting down...`
- The application has stopped

### Q: How do I run it again later?

**A:**
1. Open terminal/command prompt
2. Navigate to the folder: `cd /home/user/datacenterdatabase`
3. Run: `python app.py` (or `python3 app.py` on Mac/Linux)
4. Open browser to: `http://localhost:5000`

### Q: Can other people access this on my network?

**A:** Yes! If you want others on your WiFi to access it:
1. Find your computer's IP address:
   - **Windows:** `ipconfig` (look for "IPv4 Address")
   - **Mac/Linux:** `ifconfig` or `ip addr` (look for "inet")
2. They can visit: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`

### Q: Can I access this from the internet?

**A:** Not by default (for security). You'd need to:
- Deploy to a cloud service (Heroku, AWS, etc.)
- See `WEB_APP_README.md` section "Deployment" for instructions

### Q: Where is the data stored?

**A:** In a file called `datacenter_intelligence.db` in the same folder. It's a database file.

### Q: How often does it update?

**A:** Automatically every 6 hours. Or click the "Update Data" button in the top-right to update manually.

---

## Troubleshooting Common Issues

### Problem: "Port 5000 is already in use"

**This means:** Something else is using port 5000

**Solution:** Use a different port
```bash
# On Windows
python app.py --port 5001

# On Mac/Linux
python3 app.py --port 5001
```
Then visit: `http://localhost:5001`

### Problem: Page won't load / "Connection refused"

**Checklist:**
1. ✓ Is the application still running in the terminal? (you should see text there)
2. ✓ Did you type the address correctly? `http://localhost:5000`
3. ✓ Try `http://127.0.0.1:5000` instead
4. ✓ Check if there are any error messages in the terminal

### Problem: "ModuleNotFoundError: No module named 'flask'"

**This means:** The packages didn't install correctly

**Solution:** Try installing again:
```bash
# On Windows
python -m pip install Flask Flask-CORS

# On Mac/Linux
python3 -m pip install Flask Flask-CORS
```

### Problem: Application starts but shows no data

**This means:** The initial data scraping failed (maybe no internet?)

**What to do:**
1. Check your internet connection
2. Wait 30 seconds - initial data load takes time
3. Click the "Update Data" button in the top-right
4. Look at the terminal for error messages

### Problem: Map doesn't show

**This means:** Geocoding might have failed

**What to do:**
1. Check if you can see projects in the table below the map
2. Projects need both latitude and longitude to appear on map
3. The map requires internet to load (uses OpenStreetMap tiles)

---

## Next Steps

Once everything is working:

### 1. Explore the Application
- Click through all the pages
- Try different filters on the Dashboard
- Export some data (CSV, JSON)
- Watch for real-time notifications

### 2. Read the Documentation
- **`WEB_APP_README.md`** - Complete guide with all features
- **`POWER_CONFIGURATION_GUIDE.md`** - Power architecture guide
- **`PROJECT_SUMMARY.md`** - Project overview

### 3. Customize (Optional)
- Want to change update frequency? Edit line in `app.py`: `AUTO_UPDATE_INTERVAL_HOURS = 6`
- Want different colors? Edit `static/css/style.css`
- Want more features? Check the "Future Enhancements" section in `WEB_APP_README.md`

---

## Video Tutorial (If You're Still Stuck)

If you're having trouble, here's what the process looks like:

### Windows Visual Guide:

1. **Open Command Prompt:**
   - Start Menu → Type "cmd" → Press Enter
   - You see: `C:\Users\YourName>`

2. **Check Python:**
   - Type: `python --version`
   - You see: `Python 3.11.5`

3. **Go to folder:**
   - Type: `cd path\to\datacenterdatabase`
   - You see: `C:\...\datacenterdatabase>`

4. **Install packages:**
   - Type: `pip install -r requirements.txt`
   - You see: Lots of downloading text, then "Successfully installed..."

5. **Run app:**
   - Type: `python app.py`
   - You see: "Running on http://127.0.0.1:5000"

6. **Open browser:**
   - Open Chrome/Firefox/Edge
   - Type in address bar: `localhost:5000`
   - Press Enter
   - **You see: The website!** 🎉

---

## Still Need Help?

### Screenshots/Screen Recording

If you're stuck, take a screenshot of:
1. The terminal/command prompt window showing the error
2. The browser showing what you see

This will help diagnose the issue!

### Common Beginner Mistakes (Don't Worry, Everyone Makes These!)

1. ❌ Closing the terminal → Application stops
   - ✅ Keep the terminal open in the background

2. ❌ Typing `http://localhost:5000` into Google search
   - ✅ Type it into the address bar at the top

3. ❌ Forgetting `http://` part
   - ✅ Include it: `http://localhost:5000`

4. ❌ Installing packages in wrong folder
   - ✅ Make sure you're in the `datacenterdatabase` folder (`cd` command)

5. ❌ Using `python` on Mac/Linux instead of `python3`
   - ✅ On Mac/Linux, use `python3` and `pip3`

---

## Quick Reference Card

**Print this and keep it handy:**

```
╔════════════════════════════════════════════════════╗
║     DATACENTER INTELLIGENCE - QUICK START         ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  1. Open Terminal/Command Prompt                   ║
║                                                    ║
║  2. Navigate to folder:                            ║
║     cd /home/user/datacenterdatabase               ║
║                                                    ║
║  3. Run application:                               ║
║     python app.py                                  ║
║     (or python3 app.py on Mac/Linux)               ║
║                                                    ║
║  4. Open browser to:                               ║
║     http://localhost:5000                          ║
║                                                    ║
║  5. To stop: Press Ctrl + C in terminal            ║
║                                                    ║
╠════════════════════════════════════════════════════╣
║  Troubleshooting:                                  ║
║  • Port in use? Try: python app.py --port 5001     ║
║  • Module not found? Run: pip install -r ...       ║
║  • Permission denied? Use: pip install --user ...  ║
╚════════════════════════════════════════════════════╝
```

---

## You've Got This! 💪

Python and web development might seem scary at first, but you're just following a recipe. Each command does something specific:

- `cd` = "Change Directory" (move to a folder)
- `pip install` = "Download and install software"
- `python app.py` = "Run this program"

After you do it once, it becomes easy!

**Welcome to the world of Python and web applications!** 🎉

---

*Last Updated: 2026-01-30*
