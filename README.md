# 🛳️ Flask Container Info App

This is a simple Flask web app that displays the hostname of the container or machine it is running on. It's styled with CSS and provides a minimal frontend to demonstrate hostname retrieval via a REST API.

---

## 🚀 Features

- 🧠 Built with **Flask**
- 🎨 Styled using custom **CSS**
- 🔍 Fetches container or system **hostname** using a `/hostname` API
- 🐳 Fully **Dockerized** with `Dockerfile` and `docker-compose.yml`
- 🌐 Accessible via `http://localhost:5000`

---

## 🧠 How It Works

1. The Flask app serves an HTML page at `/`.
2. The frontend uses JavaScript to fetch the current hostname from `/hostname`.
3. The hostname is rendered dynamically in the UI.
4. When containerized, this will show the Docker container hostname.

---

