Brief about setup : - frontend is deployed on vercel , backend on render and database is postgresql deployed on render. You can install all requirements of frontend and backend and , start backend by navigate to "cd backend" folder and then run "python base.py". you can run frontend from root folder "npm run dev".
LOGIN PAGE
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1cfb8f31-ff63-4834-b9fe-a9059164d9fe" />

ADMIN PAGE
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/915841c6-4ef4-45bb-8ac9-2fef25e3396a" />






# Project Manager App - Setup Guide

A full-stack project management application with React frontend and Flask backend.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (for production) or SQLite (for local dev)

---

## 📦 Backend Setup

### 1. Navigate to backend folder
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv .venv
```

### 3. Activate virtual environment
**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables (optional)
Create a `.env` file in the backend folder:
```env
DATABASE_URL=sqlite:///instance/db.sqlite  # or your PostgreSQL URL
SECRET_KEY=your-secret-key
```

### 6. Create admin user
```bash
python create_admin.py
```

This creates two admin accounts:

- **Email:** `admin@gmail.com` | **Password:** `admin123`

### 7. Run the backend server
```bash
python app.py
```

Backend will run on: `http://127.0.0.1:5000`

---

## 🎨 Frontend Setup

### 1. Navigate to project root
```bash
cd ..
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
Create `.env.development` file in the root:
```env
VITE_API_URL=http://127.0.0.1:5000
```

### 4. Run the frontend
```bash
npm run dev
```

Frontend will run on: `http://localhost:5173`

---

## 🔐 Login Credentials

### Default Admin Account
- **Email:** `admin@gmail.com`
- **Password:** `admin123`

### Admin Capabilities
- Create/delete employees
- Assign roles (Admin, Project Manager, Developer)
- Create/manage projects
- Create/assign tasks
- View all data

---

## 👥 Creating Users

### Create a Project Manager

1. **Login as Admin** (`admin@gmail.com` / `admin123`)
2. Navigate to **Team** page
3. Click **"Add Employee"**
4. Fill in the form:
   - Employee ID: `2001`
   - First Name: `John`
   - Last Name: `Manager`
   - Email: `john.manager@company.com`
   - Phone: `1234567890`
   - Password: `manager123`
   - **Role:** Select `project_manager`
   - Admin: Leave unchecked (unless you want them to be admin too)
5. Click **"Create Employee"**

**Project Manager can:**
- Create and manage projects
- Create and assign tasks to developers
- View their own projects and tasks

---

### Create a Developer

1. **Login as Admin** (`admin@gmail.com` / `admin123`)
2. Navigate to **Team** page
3. Click **"Add Employee"**
4. Fill in the form:
   - Employee ID: `3001`
   - First Name: `Jane`
   - Last Name: `Developer`
   - Email: `jane.dev@company.com`
   - Phone: `9876543210`
   - Password: `dev123`
   - **Role:** Select `developer`
   - Admin: Leave unchecked
5. Click **"Create Employee"**

**Developer can:**
- View tasks assigned to them
- Update task status
- View project details

---

## 📋 User Roles & Permissions

| Role | Create Projects | Create Tasks | Assign Tasks | View All Data | Manage Users |
|------|----------------|--------------|--------------|---------------|--------------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Project Manager** | ✅ | ✅ | ✅ | Own projects only | ❌ |
| **Developer** | ❌ | ❌ | ❌ | Assigned tasks only | ❌ |
| **Employee** | ❌ | ❌ | ❌ | Limited | ❌ |

---

## 🌐 Production Deployment

### Backend (Render)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository
4. Set environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Random secret key
5. Deploy

### Frontend (Vercel)
1. Push code to GitHub
2. Import project on Vercel
3. Set environment variable:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com`)
4. Deploy

### Reset Admin Password in Production
If you need to reset admin passwords in production:
```bash
# Set your production database URL
$env:DATABASE_URL = "postgresql://user:pass@host:port/db"
python backend/reset_admin_password.py
```

---

## 🛠️ Common Commands

### Backend
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run server
python app.py

# Create admin
python create_admin.py

# Reset admin password (production)
python reset_admin_password.py
```

### Frontend
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📁 Project Structure

```
project-manager-react-flask-main/
├── backend/
│   ├── app.py              # Flask app entry point
│   ├── base.py             # Main Flask routes & logic
│   ├── models.py           # Database models
│   ├── config.py           # Configuration
│   ├── create_admin.py     # Admin creation script
│   ├── reset_admin_password.py  # Password reset script
│   └── requirements.txt    # Python dependencies
├── src/
│   ├── pages/              # React pages
│   ├── components/         # React components
│   └── App.tsx             # Main React app
├── .env.development        # Frontend dev environment
├── .env.production         # Frontend prod environment
└── package.json            # Node dependencies
```

---

## 🐛 Troubleshooting

### "Invalid salt" error on login
- Run `python backend/reset_admin_password.py` with your database URL

### Frontend can't connect to backend
- Check `VITE_API_URL` in `.env.development`
- Ensure backend is running on the correct port

### CORS errors
- Backend already configured for `http://localhost:5173` and Vercel
- Check `backend/base.py` CORS origins if using different domains

### Database not found
- Backend creates SQLite DB automatically in `instance/db.sqlite`
- For PostgreSQL, ensure `DATABASE_URL` is set correctly

---

## 📞 Support

For issues or questions, check the logs:
- **Backend logs:** Terminal where `python app.py` is running
- **Frontend logs:** Browser DevTools Console
- **Network errors:** Browser DevTools Network tab

---

## 🎯 Next Steps

1. ✅ Start backend server
2. ✅ Start frontend server
3. ✅ Login as admin
4. ✅ Create a project manager
5. ✅ Create a developer
6. ✅ Create a project
7. ✅ Create and assign tasks
8. 🚀 Start managing projects!
