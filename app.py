import os
import sqlite3
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------- CONFIG ----------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DB_NAME = "database.db"

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        place TEXT,
        detail TEXT,
        contact TEXT,
        image TEXT
    )
    """)

    conn.commit()
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            place TEXT,
            detail TEXT,
            contact TEXT,
            image TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    q = request.args.get("q", "")
    conn = get_db()
    c = conn.cursor()

    if q:
        like = f"%{q}%"
        c.execute("""
            SELECT * FROM posts
            WHERE item_name LIKE ? OR place LIKE ?
            ORDER BY id DESC
        """, (like, like))
    else:
        c.execute("SELECT * FROM posts ORDER BY id DESC")

    posts = c.fetchall()
    conn.close()

    html = f"""
<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>เว็บประกาศของหาย</title>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
body {{
    font-family: 'Prompt', sans-serif;
    background:#f4f6f8;
    padding:20px;
}}
.post {{
    background:#fff;
    padding:15px;
    border-radius:14px;
    margin:15px 0;
    box-shadow:0 4px 10px rgba(0,0,0,.08);
}}
.search-box {{
    max-width:420px;
    position:relative;
}}
.search-box input {{
    width:100%;
    padding:12px 45px 12px 18px;
    border-radius:999px;
    border:1px solid #ddd;
}}
.search-box button {{
    position:absolute;
    right:6px;
    top:50%;
    transform:translateY(-50%);
    background:none;
    border:none;
    font-size:18px;
}}
button {{
    padding:8px 14px;
    border-radius:999px;
    border:none;
    background:#4CAF50;
    color:white;
}}
</style>
</head>
<body>

<h1>เว็บประกาศของหาย</h1>

<form method="get">
  <div class="search-box">
    <input name="q" value="{q}" placeholder="ค้นจากชื่อของหรือสถานที่">
    <button>🔍</button>
  </div>
</form>

<hr>

<h3>เพิ่มประกาศ</h3>
<form method="post" action="/add" enctype="multipart/form-data">
  <input name="item_name" placeholder="ชื่อของ" required><br><br>
  <input name="place" placeholder="สถานที่ที่หาย" required><br><br>
  <textarea name="detail" placeholder="รายละเอียด" required></textarea><br><br>
  <input name="contact" placeholder="ติดต่อ" required><br><br>
  <input type="file" name="image"><br><br>
  <button>บันทึกประกาศ</button>
</form>

<hr>
<h2>รายการของหาย</h2>
"""

    for p in posts:
    img = ""
    if p[5]:
        img = f"<img src='/static/uploads/{p[5]}' width='200'><br>"

    html += f"""
<div class="post">
  {img}
  <b>ชื่อของ:</b> {p[1]}<br>
  <b>สถานที่:</b> {p[2]}<br>
  <b>รายละเอียด:</b> {p[3]}<br>
  <b>ติดต่อ:</b> {p[4]}<br><br>

  <form method="post" action="/delete/{p[0]}" onsubmit="return confirm('ยืนยันการลบ?');">
    <button style="background:#e74c3c;">ลบ</button>
  </form>
</div>
"""

    html += "</body></html>"
    return html

# ---------- ADD ----------
@app.route("/add", methods=["POST"])
def add():
    data = request.form
    image = request.files.get("image")
    filename = None

    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO posts (item_name, place, detail, contact, image)
        VALUES (?,?,?,?,?)
    """, (data["item_name"], data["place"], data["detail"], data["contact"], filename))
    conn.commit()
    conn.close()

    return redirect("/")

# ---------- DELETE ----------
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT image FROM posts WHERE id=?", (id,))
    img = c.fetchone()
    if img and img[0]:
        path = os.path.join(UPLOAD_FOLDER, img[0])
        if os.path.exists(path):
            os.remove(path)

    c.execute("DELETE FROM posts WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
