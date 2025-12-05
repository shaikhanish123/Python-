from fastapi import FastAPI, HTTPException
import requests
import json
import os

app = FastAPI()

CACHE_FILE = "cache.json"

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def fetch_data():
    try:
        posts = requests.get(
            "https://jsonplaceholder.typicode.com/posts",
            timeout=5
        ).json()

        users = requests.get(
            "https://jsonplaceholder.typicode.com/users",
            timeout=5
        ).json()

        cache = {"posts": posts, "users": users}
        save_cache(cache)
        return cache

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/refresh")
def refresh_data():
    return fetch_data()


@app.get("/posts")
def list_posts(userId: int = None):
    data = load_cache().get("posts", [])

    if userId:
        data = [p for p in data if p["userId"] == userId]

    return data


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    data = load_cache().get("posts", [])

    for p in data:
        if p["id"] == post_id:
            return p

    raise HTTPException(status_code=404, detail="Post not found")
