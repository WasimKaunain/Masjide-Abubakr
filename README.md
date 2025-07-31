# 🕌 Masjide AbuBakr – Mosque Foundation Donation Web App

A modern, secure, and responsive web application designed to support mosque fundraising efforts. Built with simplicity, transparency, and community trust in mind.

🌐 Live App: [https://masjide-abubakr.onrender.com](https://masjide-abubakr.onrender.com)

---

## 📌 Features

- 💳 **Online Donation Form** – Accepts donations with purpose selection (e.g., Zakat, Sadaqah, Masjid Development).
- 📊 **Admin Dashboard** – View and manage donations (with authentication).
- 📜 **Transaction History** – Keeps a log of all donations made.
- 🔐 **Secure Handling** – Sensitive keys and credentials are managed using environment variables.
- 🎨 **User-Friendly Interface** – Clean and mobile-responsive UI for all age groups.

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Jinja2 templates)
- **Backend**: Python, Flask
- **Database**: SQLite (can be extended to MySQL/PostgreSQL)
- **Hosting**: Render
- **Others**: Git, Jinja2, Python `venv`

---

## 📂 Project Structure

Mosque-Donation/
├── app.py
├── requirements.txt
├── render.yaml
├── templates/
│ └── *.html
├── static/
│ ├── css/
│ ├── js/
│ └── images/
├── utils/
│ └── helpers.py
├── secrets/
│ └── config.json
├── Frontend/
├── Backend/
└── venv/ (ignored from Git)



---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Mosque-Donation.git
cd Mosque-Donation
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the App Locally
```bash 
python app.py
App will run on: http://127.0.0.1:5000/
```

🔐 Environment & Secrets
Sensitive keys, emails, and credentials are stored in:

secrets/config.json

.env (if extended with dotenv)

Make sure not to push these files to version control.


📧 Contact
For support, improvements, or collaboration, feel free to reach out:

📩 Email: [wasimkonain@gmail.com]

📱 WhatsApp/Telegram: [+91-7488789638]

🤝 Acknowledgments
JazakAllah Khair to all contributors and donors.

Inspired by community needs and built with love.


📜 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it for non-commercial purposes.


