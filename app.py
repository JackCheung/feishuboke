import requests
from flask import Flask, render_template, abort
from config import Config

app = Flask(__name__)

# 获取飞书多维表格数据

def get_feishu_records():
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{Config.BASE_ID}/tables/{Config.TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("data", {}).get("items", [])
    return []

def get_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {
        "app_id": Config.FEISHU_APP_ID,
        "app_secret": Config.FEISHU_APP_SECRET
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json().get("tenant_access_token", "")
    return ""

@app.route('/')
def index():
    records = get_feishu_records()
    posts = []
    for r in records:
        fields = r.get("fields", {})
        posts.append({
            "id": r.get("record_id"),
            "title": fields.get("标题", ""),
            "quote": fields.get("金句输出", ""),
            "comment": fields.get("黄叔点评", ""),
            "summary": fields.get("概要内容输出", "")[:100]
        })
    return render_template('index.html', posts=posts)

@app.route('/detail/<record_id>')
def detail(record_id):
    records = get_feishu_records()
    for r in records:
        if r.get("record_id") == record_id:
            fields = r.get("fields", {})
            return render_template('detail.html',
                                   title=fields.get("标题", ""),
                                   quote=fields.get("金句输出", ""),
                                   comment=fields.get("黄叔点评", ""),
                                   content=fields.get("概要内容输出", ""))
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)