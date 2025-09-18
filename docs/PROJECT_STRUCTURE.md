# IntelliAttend Project Structure

This document explains the restructured organization of the IntelliAttend project, which has been separated into distinct components following professional software development practices.

## New Project Structure

```
IntelliAttend/
├── backend/          # Server-side API and business logic
├── frontend/         # Web-based user interfaces
├── mobile/           # Android mobile application
├── database/         # Database schema and setup scripts
├── docs/             # Comprehensive documentation
├── scripts/          # Utility and setup scripts
├── requirements.txt  # Python dependencies
├── .gitignore        # Git ignore rules
└── README.md         # Main project documentation
```

## Component Breakdown

### Backend (`/backend`)
Contains all server-side components including the main Flask application, API endpoints, and business logic.

**Key files:**
- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `generate_qr.py` - QR code generation utilities
- `setup_db.py` - Database setup scripts
- `QR_DATA/` - QR code storage directory

### Frontend (`/frontend`)
Contains all web-based user interfaces including HTML templates, CSS, JavaScript, and static assets.

**Key files:**
- `templates/` - HTML templates for different user roles
- `public/` - Static assets
- `package.json` - Node.js dependencies and scripts

### Mobile (`/mobile`)
Contains the Android mobile application source code.

**Key files:**
- `app/` - Main Android application source code

### Database (`/database`)
Contains database schema definitions and setup scripts.

**Key files:**
- `database_schema.sql` - Database schema definition
- `database_setup.py` - Database initialization script

### Documentation (`/docs`)
Contains all project documentation including technical specifications, user guides, and implementation details.

**Key files:**
- `TECHNICAL_SPECIFICATION.md` - Complete technical specification
- `ADMIN_GUIDE.md` - Administrator user guide
- `RUNNING_INSTRUCTIONS.md` - System startup instructions

### Scripts (`/scripts`)
Contains utility and setup scripts for system management and testing.

**Key files:**
- `install.py` - Installation script
- `start_system.py` - System startup script
- Various test scripts

## Benefits of This Structure

1. **Separation of Concerns**: Each component has a distinct responsibility
2. **Scalability**: Components can be developed, tested, and deployed independently
3. **Maintainability**: Changes to one component have minimal impact on others
4. **Team Collaboration**: Different teams can work on different components simultaneously
5. **Technology Flexibility**: Each component can use the most appropriate technology stack

## Development Workflow

1. **Backend Development**: Work in the `/backend` directory
2. **Frontend Development**: Work in the `/frontend` directory
3. **Mobile Development**: Work in the `/mobile` directory
4. **Database Changes**: Modify files in the `/database` directory
5. **Documentation**: Update files in the `/docs` directory
6. **Utilities**: Add scripts to the `/scripts` directory

## Deployment Considerations

- Each component can be deployed to different servers or services
- The backend can be deployed to a cloud platform (AWS, Azure, GCP)
- The frontend can be served through a CDN
- The mobile app can be distributed through app stores
- The database can be hosted on a dedicated database service

## Version Control

With this structure, it's easier to:
- Set up different deployment pipelines for each component
- Implement component-specific testing strategies
- Manage dependencies for each component separately
- Track changes and releases for each component independently