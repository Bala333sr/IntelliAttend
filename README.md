# IntelliAttend - Smart Attendance Management System

IntelliAttend is a comprehensive attendance management system that leverages Bluetooth proximity verification to ensure accurate attendance tracking in educational environments.

## Project Structure

The project is organized into separate components following professional software development practices:

- [`/backend`](backend/) - Server-side API and business logic
- [`/frontend`](frontend/) - Web-based user interfaces
- [`/mobile`](mobile/) - Android mobile application
- [`/database`](database/) - Database schema and setup scripts
- [`/docs`](docs/) - Comprehensive documentation
- [`/scripts`](scripts/) - Utility and setup scripts

For detailed information about this structure, see the [Documentation Index](docs/README.md).

## Recent Restructuring

The project has been recently restructured to follow professional software development practices. See the [Documentation Index](docs/README.md) for summaries and change logs.

## System Components

### Mobile Application
- Android app for student attendance tracking
- Bluetooth Low Energy (BLE) beacon scanning
- Environmental data collection (GPS, WiFi, Bluetooth)
- Secure authentication

### Web Portal
- Admin dashboard for system management
- Student portal for attendance viewing
- SmartBoard display for real-time class attendance
- System monitoring interface

### Backend Services
- REST API for data exchange
- QR code generation and management
- Bluetooth proximity verification coordination
- Database management

### Database
- Student and professor information
- Class schedules and attendance records
- Bluetooth beacon registrations
- QR code tokens and authentication data

## Technologies Used

- **Mobile**: Kotlin, Android SDK, Bluetooth LE
- **Frontend**: HTML/CSS/JavaScript, Tailwind CSS
- **Backend**: Python, Flask
- **Database**: SQLite
- **Communication**: REST API, Bluetooth, QR Codes

## Getting Started

1. **Backend Setup**: See [backend/README.md](backend/README.md)
2. **Frontend Setup**: See [frontend/README.md](frontend/README.md)
3. **Mobile Setup**: See [mobile/README.md](mobile/README.md)
4. **Database Setup**: See [database/README.md](database/README.md)

## Documentation

Browse all guides in the [Documentation Index](docs/README.md), which categorizes geofencing, real-time presence, mobile, database/hierarchy, production/testing, and integration documents.

## Scripts

Utility and setup scripts are available in the [`/scripts`](scripts/) directory.

## 📋 Overview

IntelliAttend is a comprehensive smart attendance system that leverages QR codes, biometric verification, geofencing, and Bluetooth proximity detection to provide secure and accurate attendance tracking. The system features a multi-tier architecture with dedicated portals for faculty, students, and administrators.

## 🌟 Key Features

### Faculty Portal
- Generate time-limited QR codes for attendance sessions
- View real-time attendance data
- Manage class schedules and student records
- Generate detailed attendance reports

### Student Portal
- Scan QR codes for attendance marking
- Multi-factor verification (QR + biometric + location + Bluetooth)
- View personal attendance records
- Receive real-time attendance notifications

### Admin Dashboard
- **Complete System Management**:
  - Faculty, student, and class management
  - Classroom geofencing configuration
  - Device validation with MAC addresses/UUIDs
  - Substitute faculty assignment
  - Attendance and leave management
- **Advanced Features**:
  - Real-time system monitoring
  - Comprehensive reporting and analytics
  - Device management and tracking
  - Security and access control

### SmartBoard Integration
- Dedicated interface for classroom displays
- Automatic QR code generation and refresh
- Real-time attendance visualization
- Default OTP (000000) for quick session start

## 🛠️ Technical Architecture

### Backend
- **Framework**: Flask (Python 3.8+)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with role-based access control
- **Security**: Rate limiting, input validation, secure password hashing

### Frontend
- **Faculty Portal**: HTML5, CSS3, JavaScript
- **Student Portal**: Mobile-responsive design
- **Admin Dashboard**: Comprehensive management interface
- **SmartBoard**: Dedicated classroom display interface

### Core Components
1. **QR Code Generation**: Dynamic QR codes with 5-second refresh
2. **Biometric Verification**: Integration-ready fingerprint/face recognition
3. **Geofencing**: Location-based attendance validation
4. **Bluetooth Proximity**: Device proximity detection
5. **Session Management**: Thread-safe concurrent session handling

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- MySQL database server
- Redis server (for production rate limiting)
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/intelliattend.git
   cd intelliattend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up the database**:
   ```bash
   python server/reset_db.py
   python server/setup_db.py
   ```

5. **Start the application**:
   ```bash
   python server/app.py
   ```

### Default Access Credentials

**Faculty Login**:
- Email: `john.smith@university.edu`
- Password: `F@cultY2024!` (or DEFAULT_FACULTY_PASSWORD from .env)

**Student Login**:
- Email: `student1@student.edu`
- Password: `Stud3nt2024!` (or DEFAULT_STUDENT_PASSWORD from .env)

**SmartBoard Default OTP**: `000000`

**Admin Portal**:
- **Unified Admin Dashboard**: `http://localhost:5002/admin/unified_dashboard.html`
- Username: `admin@admin.edu`
- Password: `admin123`

## 📊 API Endpoints

### Authentication
- `POST /api/faculty/login` - Faculty login
- `POST /api/student/login` - Student login
- `POST /api/admin/login` - Admin login

### QR Code Management
- `POST /api/faculty/generate-otp` - Generate OTP for QR session
- `POST /api/verify-otp` - Start attendance session
- `GET /api/qr/current/<session_id>` - Get current QR code
- `POST /api/session/stop/<session_id>` - Stop attendance session

### Attendance Processing
- `POST /api/attendance/scan` - Process attendance scan

### Admin APIs
- `GET /api/admin/faculty` - List all faculty
- `POST /api/admin/faculty` - Create new faculty
- `GET /api/admin/faculty/<id>` - Get faculty details
- `PUT /api/admin/faculty/<id>` - Update faculty
- `DELETE /api/admin/faculty/<id>` - Delete faculty

*(Similar endpoints for students, classes, classrooms, devices, and attendance records)*

## 🧪 Testing

Run the test suite to verify system functionality:
```bash
python test_app.py
```

## 📈 Production Deployment

### Environment Configuration
1. Set `FLASK_CONFIG=production` in .env
2. Configure Redis for rate limiting
3. Set up proper SSL certificates for HTTPS
4. Configure database connection pooling
5. Implement proper logging and monitoring

### Security Considerations
- Use strong, randomly generated secrets
- Implement proper firewall rules
- Regular security audits and penetration testing
- Keep dependencies updated
- Implement proper backup and disaster recovery

## 📚 Documentation

See the [Documentation Index](docs/README.md) for all manuals, summaries, and guides.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please open an issue on the GitHub repository or contact the development team.

## 🙏 Acknowledgments

- Thanks to all contributors who helped improve the system
- Special recognition for the security and performance enhancements
- Gratitude to the testing team for identifying critical issues

---
**IntelliAttend - Making attendance smart, secure, and reliable**