# Student Complaint Management System

This project was developed as part of training conducted by **Edunet Foundation** on **Full Stack Web Development**.

## 📌 Project Overview
The Student Complaint Management System is a web-based application built using **Django** that allows students to raise complaints related to college services such as canteen, technical issues, sports, events, etc.  
The system ensures proper communication between students, staff, and administrators.

## 👥 User Roles
- **Student**
  - Login using roll number/username
  - Raise complaints
  - Track complaint status

- **Staff**
  - View assigned complaints
  - Update complaint status

- **Admin**
  - Manage users
  - Assign complaints to staff
  - Monitor all complaints

## 🛠️ Technologies Used
- Frontend: HTML, CSS, JavaScript
- Backend: Python, Django
- Database: SQLite
- Version Control: Git & GitHub

## ⚙️ Features
- Role-based authentication
- Separate dashboards for Student, Staff, and Admin
- Complaint tracking system
- Secure login system

## 🚀 How to Run the Project
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
