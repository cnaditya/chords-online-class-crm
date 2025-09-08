# Chords Online Class CRM

A complete Streamlit-based CRM system for managing online music students, built for Aditya and Brahmani's music academy.

## Features

- **Multi-Instructor Support**: Separate sections for Aditya and Brahmani with admin oversight
- **Student Management**: Complete student profiles with contact details and preferences
- **Package Management**: 1-month to 1-year packages with class tracking
- **Payment Tracking**: Fee management with automated WhatsApp receipts
- **Class Scheduling**: Recurring and ad-hoc class scheduling
- **Attendance Tracking**: Mark attendance and track class usage
- **Materials Management**: Upload and share lesson videos/materials
- **WhatsApp Integration**: Automated reminders and receipts via Fast2SMS
- **Reports & Analytics**: Student progress and business insights

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Initialize Database**
   ```bash
   alembic upgrade head
   ```

4. **Run Application**
   ```bash
   streamlit run app.py
   ```

5. **Default Login Credentials**
   - Admin: `admin` / `admin123`
   - Aditya: `aditya` / `instructor123`
   - Brahmani: `brahmani` / `instructor123`

## Configuration

### Environment Variables (.env)
- `DATABASE_URL`: Database connection string
- `FAST2SMS_API_KEY`: Fast2SMS API key for WhatsApp
- `SECRET_KEY`: Application secret key
- `TIMEZONE`: Default timezone (Asia/Kolkata)
- `UPLOAD_DIR`: Directory for file uploads

### Fast2SMS WhatsApp Templates
- **Fee Reminder** (ID: 5170): Automated package expiry reminders
- **Payment Receipt** (ID: 5171): Automated payment confirmations

## Database Schema

- **Users**: Authentication and role management
- **Students**: Student profiles and contact information
- **Enrollments**: Package subscriptions and progress tracking
- **Payments**: Fee payments and receipt management
- **ClassSchedule**: Class timing and recurrence rules
- **Attendance**: Class attendance and lesson notes
- **Materials**: Lesson videos and study materials
- **NotificationLog**: WhatsApp notification tracking

## Architecture

- **Frontend**: Streamlit web application
- **Backend**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: bcrypt password hashing
- **Notifications**: Fast2SMS WhatsApp API integration
- **Storage**: Local file storage (extensible to S3)
- **Migrations**: Alembic database migrations

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Production (Streamlit Cloud)
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Set environment variables in Streamlit Cloud settings
4. Deploy application

### Docker Deployment
```bash
# Build image
docker build -t chords-crm .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data chords-crm
```

## Package Options

- **1 Month - 8 Classes**: Short-term package
- **3 Months - 24 Classes**: Popular choice
- **6 Months - 48 Classes**: Extended learning
- **1 Year - 96 Classes**: Complete course

Students can attend 1 or 2 classes per week based on their package.

## Instruments Supported

- Piano
- Keyboard
- Guitar
- Carnatic Vocal

## Support

For technical support or feature requests, contact the development team.

## License

Private software for Chords Music Academy. All rights reserved.