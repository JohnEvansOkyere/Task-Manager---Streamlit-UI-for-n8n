# 🚀 Task Manager - Simple Version

**No Docker, No CI/CD - Just Python!**

A clean, simple task management app with FastAPI backend and Streamlit frontend.

## ⚡ Super Quick Start (3 Steps)

### 1️⃣ Update Your Webhook URL

Open `backend/main.py` and update line 21:
```python
N8N_WEBHOOK_URL = "https://your-ngrok-url.com/webhook/your-webhook-id"
```

### 2️⃣ Install & Run Backend

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start the backend API
python main.py
```

Backend will run at: **http://localhost:8000**  
API Docs at: **http://localhost:8000/docs**

### 3️⃣ Install & Run Frontend (New Terminal)

```bash
# Install frontend dependencies
cd frontend
pip install -r requirements.txt

# Start the Streamlit app
streamlit run app.py
```

Frontend will open at: **http://localhost:8501**

**That's it! 🎉**

---

## 📁 Project Structure

```
task_manager_simple/
├── backend/
│   ├── main.py              # FastAPI application (300 lines)
│   └── requirements.txt     # 4 dependencies
├── frontend/
│   ├── app.py              # Streamlit UI (350 lines)
│   └── requirements.txt    # 2 dependencies
└── README.md
```

**Total: 2 files to run, 6 dependencies. That's it!**

---

## 🎯 Features

### What You Can Do:
- ✅ Create tasks with status, description, deadline
- ✅ View all tasks (with filtering)
- ✅ Update task status
- ✅ Delete tasks
- ✅ See task statistics
- ✅ Send natural language commands

### How It Works:
```
Streamlit UI → FastAPI Backend → n8n Webhook → Google Sheets
```

---

## 🔧 Configuration

**Only 1 thing to configure:**

Edit `backend/main.py` line 21:
```python
N8N_WEBHOOK_URL = "https://your-complete-webhook-url/webhook/id"
```

That's it! No `.env` files, no Docker config, no complex setup.

---

## 📖 API Endpoints

Backend automatically provides:
- `GET /health` - Check if n8n is connected
- `GET /api/v1/tasks` - Get all tasks
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{name}` - Update task
- `DELETE /api/v1/tasks/{name}` - Delete task
- `POST /api/v1/message` - Natural language
- `GET /api/v1/stats` - Statistics

**Full docs:** http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Make sure you updated the webhook URL in main.py
# Check if port 8000 is available
```

### Frontend can't connect?
```bash
# Make sure backend is running first
# Check http://localhost:8000/health
```

### n8n connection fails?
```bash
# Test your webhook URL directly:
curl -X POST https://your-url.com/webhook/id \
  -H "Content-Type: application/json" \
  -d '{"action":"sendMessage","sessionId":"test","chatInput":"hello"}'
```

---

## 🎨 Customization

### Want to change the backend port?

Edit `backend/main.py`, last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
```

Then update `frontend/app.py` line 12:
```python
API_URL = "http://localhost:8001"  # Match backend port
```

### Want to add features?

- **Backend**: Edit `backend/main.py` - add new endpoints
- **Frontend**: Edit `frontend/app.py` - add new UI components

Both files are simple and well-commented!

---

## 📊 Why This Architecture?

### Why FastAPI Backend?

Instead of connecting Streamlit directly to n8n, we use FastAPI because:

1. **Separation of Concerns**
   - Frontend focuses on UI
   - Backend handles business logic
   - Clean API contracts

2. **Reusability**
   - API can be used by multiple frontends
   - Mobile app? Just connect to the API
   - Other tools? Same API

3. **Professional Practice**
   - This is how real applications are built
   - Shows you understand proper architecture
   - Great for portfolios and interviews

4. **Features**
   - Auto-generated API documentation
   - Request validation
   - Better error handling
   - Easy to test

### Simple vs Complex Version

**This Simple Version:**
- ✅ No Docker needed
- ✅ No CI/CD setup
- ✅ Runs directly with Python
- ✅ Perfect for learning and development
- ✅ Easy to understand and modify

**Complex Version (in task_manager_project):**
- ✅ Docker containerization
- ✅ CI/CD pipelines
- ✅ Production-ready
- ✅ Comprehensive testing
- ✅ Advanced features

**Choose based on your needs:**
- **Learning/Development?** → Use this simple version
- **Production deployment?** → Use the complex version

---

## 🎓 What You Learn

This project demonstrates:

1. **API Design** - RESTful endpoints with FastAPI
2. **Frontend Development** - Interactive UI with Streamlit
3. **Integration** - Connecting services (n8n, Google Sheets)
4. **Architecture** - Proper separation of concerns
5. **Python Skills** - Modern Python practices

---

## 🚀 Next Steps

1. **Try it out** - Create some tasks!
2. **Explore the API** - Visit http://localhost:8000/docs
3. **Modify it** - Add your own features
4. **Learn from it** - Read the code (it's well-commented)
5. **Build on it** - Add authentication, database, etc.

---

## 💡 Pro Tips

### Running in Background

**Backend:**
```bash
nohup python backend/main.py > backend.log 2>&1 &
```

**Frontend:**
```bash
nohup streamlit run frontend/app.py > frontend.log 2>&1 &
```

### Auto-reload During Development

Backend auto-reloads by default with uvicorn.

For frontend, save files and Streamlit will ask to rerun.

### Test the API

```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "My First Task",
    "status": "TODO",
    "description": "Testing the API"
  }'

# Get all tasks
curl http://localhost:8000/api/v1/tasks
```

---

## ❓ FAQ

**Q: Do I need Docker?**  
A: No! This version runs directly with Python.

**Q: Do I need CI/CD?**  
A: No! That's for production. This is for development.

**Q: Can I deploy this?**  
A: Yes! But for production, use the Docker version.

**Q: Why FastAPI instead of direct connection?**  
A: Better architecture, reusability, and professionalism.

**Q: Is this good enough for my portfolio?**  
A: Yes! Shows you understand proper API design and architecture.

---

## 📧 Need Help?

- Backend not working? Check `backend/main.py` line 21 (webhook URL)
- Frontend issues? Make sure backend is running first
- API questions? Check http://localhost:8000/docs

---

**Built with ❤️ for simplicity**

*No Docker. No complexity. Just code and run!* 🚀