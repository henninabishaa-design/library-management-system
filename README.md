# Library Management System — deployment

This is the Python HTTP-server version of the Library Management System, prepared to run on Render.

## Deploy

1. Create a GitHub repository and upload `library.py`, `requirements.txt`, and `render.yaml` to the repository root.
2. Sign in to Render and choose **New → Blueprint** (or create a Web Service connected to the repository).
3. If using Blueprint, select the repository containing `render.yaml` and apply it. If creating a Web Service manually, select Python and use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python library.py`
   - Plan: Free
4. Wait for the deployment to finish, then open the public `https://...onrender.com` URL shown by Render.

## Important data note

The current app stores books in a Python list in memory. Book changes can be lost whenever the service restarts or redeploys, and multiple app instances would not share the same data. This is suitable for a demo, but use a persistent database (for example SQLite on a correctly configured persistent disk or a hosted PostgreSQL database) before relying on it for real library records.
