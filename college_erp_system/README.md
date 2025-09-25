# 🎓 College ERP (Enterprise Resource Planning) System

A comprehensive web-based College Management System built with Django that streamlines academic and administrative workflows for students, teachers, and administrators.

## ✨ Features

### 👨‍🎓 Student Portal
- **Dashboard**: Overview of attendance, upcoming exams, pending fees, and notifications
- **Timetable**: View personal class schedule and syllabus
- **Attendance**: Track attendance records and percentage by subject  
- **Exam Management**: View upcoming exams, schedules, and exam instructions
- **Results**: Access published exam results and grades
- **Fee Management**: View fee status, payment history, and pending dues
- **Notifications**: Receive institutional updates, announcements, and alerts
- **Profile**: Manage personal information and academic details

### 👨‍🏫 Teacher Portal
- **Dashboard**: Overview of assigned classes and subjects
- **Timetable Management**: View and manage teaching schedule
- **Attendance System**: Mark and manage student attendance
- **Exam Management**: Create, schedule, and manage examinations
- **Grade Management**: Enter and publish student grades
- **Class Management**: Manage assigned classes and students
- **Notifications**: Send announcements to students

### 🛠️ Admin Panel
- **User Management**: Complete CRUD operations for students, teachers, and admin users
- **Academic Management**: Manage departments, courses, classes, and subjects
- **Role-based Access Control**: Secure permission management
- **System Configuration**: Configure academic years, semesters, and institutional settings
- **Reports & Analytics**: Generate comprehensive academic and administrative reports
- **Notification System**: Broadcast announcements and updates

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Django 5.2.6
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.1.3
- **Database**: SQLite (Development) / PostgreSQL/MySQL (Production)
- **Authentication**: Django's built-in authentication with custom user model
- **API**: Django REST Framework 3.16.1
- **Icons**: Bootstrap Icons 1.7.2
- **File Handling**: Pillow for image processing

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd college_erp_system
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Create sample data (optional)**
```bash
python manage.py create_sample_data
```

7. **Run the development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Open your browser and go to `http://127.0.0.1:8000/`
- Use the demo credentials or create your own users

## 👥 Demo Users

After running the sample data command, you can use these credentials:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Teacher | teacher1 | teacher123 |
| Student | student1 | student123 |

## 📁 Project Structure

```
college_erp_system/
├── college_erp/                # Main project directory
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI application
├── accounts/                   # User authentication app
│   ├── models.py              # Custom User model
│   ├── views.py               # Authentication views
│   └── admin.py               # Admin configuration
├── academics/                  # Academic management app
│   ├── models.py              # Academic models (Course, Class, etc.)
│   ├── admin.py               # Admin interface
│   └── management/            # Management commands
├── students/                   # Student portal app
│   ├── models.py              # Student and Notification models
│   ├── views.py               # Student dashboard and features
│   └── urls.py                # Student URL patterns
├── teachers/                   # Teacher portal app
├── administration/            # Admin portal app
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── accounts/             # Authentication templates
│   ├── students/             # Student portal templates
│   ├── teachers/             # Teacher portal templates
│   └── administration/       # Admin portal templates
├── static/                    # Static files (CSS, JS, Images)
├── media/                     # User uploaded files
└── requirements.txt          # Python dependencies
```

## 🗃️ Database Models

### Core Models

#### User (Custom)
- Extended Django's AbstractUser
- User types: Student, Teacher, Administrator
- Profile information and contact details

#### Academic Models
- **Department**: Academic departments
- **Course**: Individual courses/subjects
- **Class**: Student classes with sections
- **Subject**: Course assignments to classes
- **Timetable**: Class schedules
- **TimeSlot**: Time periods for classes

#### Assessment Models
- **Exam**: Examination management
- **Result**: Student exam results
- **Attendance**: Daily attendance tracking

#### Financial Models
- **Fee**: Student fee management
- **Payment tracking and status**

#### Communication Models
- **Notification**: System announcements
- **Targeted messaging system**

## 🔒 Security Features

- **Role-based Access Control**: Different permissions for each user type
- **Authentication**: Secure login/logout system
- **Authorization**: Route-level permission checking  
- **CSRF Protection**: Cross-site request forgery protection
- **Input Validation**: Form and data validation
- **SQL Injection Prevention**: Django ORM protection

## 🎨 User Interface

- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Intuitive Navigation**: Role-based sidebar navigation
- **Modern UI**: Clean and professional design
- **Interactive Elements**: Dynamic content with AJAX
- **Data Visualization**: Charts and progress indicators
- **Accessibility**: Screen reader friendly

## 📊 Key Features Implementation

### Dashboard System
Each user type has a customized dashboard showing:
- **Students**: Attendance percentage, upcoming exams, fee status, notifications
- **Teachers**: Class overview, attendance summary, exam schedules
- **Administrators**: System statistics, user management, reports

### Attendance Management
- **Real-time Tracking**: Mark attendance during class
- **Automated Calculations**: Attendance percentage computation
- **Report Generation**: Subject-wise and overall attendance reports
- **Alert System**: Low attendance notifications

### Examination System
- **Exam Scheduling**: Create and manage exam timetables
- **Result Management**: Enter and publish results
- **Grade Calculation**: Automatic grade computation
- **Performance Analytics**: Student performance tracking

### Fee Management
- **Multiple Fee Types**: Tuition, library, lab, exam fees
- **Payment Tracking**: Status monitoring and history
- **Due Date Management**: Automatic overdue detection
- **Receipt Generation**: Digital payment receipts

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
Create a `.env` file with:
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@host:port/dbname
ALLOWED_HOSTS=yourdomain.com
```

2. **Database Configuration**
- Configure PostgreSQL/MySQL for production
- Run migrations: `python manage.py migrate`

3. **Static Files**
```bash
python manage.py collectstatic
```

4. **Web Server**
- Configure Apache/Nginx
- Use Gunicorn for WSGI server

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "college_erp.wsgi:application"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📝 API Documentation

The system includes REST API endpoints for:
- User authentication
- Academic data management
- Student information
- Attendance tracking
- Exam results

API documentation available at `/api/docs/` (when DRF is configured)

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

For coverage:
```bash
pip install coverage
coverage run manage.py test
coverage report
```

## 📈 Future Enhancements

- **Mobile Application**: React Native/Flutter app
- **SMS Integration**: Automated SMS notifications
- **Email System**: Email notifications and reports
- **Advanced Analytics**: Machine learning insights
- **Document Management**: Digital document storage
- **Online Payments**: Payment gateway integration
- **Video Conferencing**: Integrated online classes
- **Library Management**: Book tracking and management

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**
```bash
python manage.py makemigrations --empty appname
python manage.py migrate
```

2. **Static Files Not Loading**
```bash
python manage.py collectstatic --clear
```

3. **Permission Denied**
- Check user roles and permissions
- Ensure proper authentication

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@collegeerp.com
- Documentation: [Link to detailed docs]

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the UI framework
- Contributors and testers

---

**College ERP System** - Streamlining Education Management 🎓

***Thank YOU***