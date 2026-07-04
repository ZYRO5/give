# Donor Platform

A comprehensive full-stack web application for managing donors, campaigns, and donations. This platform provides tools for nonprofits to manage their fundraising efforts effectively.

## Features

### Backend (FastAPI)
- **User Management**: Registration, authentication, profile management
- **Campaign Management**: Create, update, and manage fundraising campaigns
- **Donation Tracking**: Record and manage donations with multiple payment methods
- **Donor Management**: Maintain donor profiles and giving history
- **Reporting & Analytics**: Comprehensive reports and dashboard analytics
- **Email Notifications**: Automated email notifications for donations and updates
- **Tax Certificates**: Generate tax certificates for donors
- **Activity Logging**: Track user activities and audit trails

### Frontend (React + TypeScript)
- **Responsive Design**: Mobile-friendly UI with Tailwind CSS
- **Dashboard**: Interactive dashboard with analytics and charts
- **User Authentication**: Secure login and registration
- **Campaign Management**: Create and manage fundraising campaigns
- **Donor Profiles**: Manage donor information and giving history
- **Reports & Analytics**: Visual reports with charts and statistics
- **Notifications**: Real-time notifications for important events

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Cache**: Redis
- **Task Queue**: Celery

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Forms**: React Hook Form

## Project Structure

```
donor-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── users.py
│   │   │   ├── campaigns.py
│   │   │   ├── donations.py
│   │   │   ├── donors.py
│   │   │   └── reports.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   ├── utils/
│   │   ├── middleware/
│   │   ├── database/
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UI.tsx
│   │   │   ├── Charts.tsx
│   │   │   └── Layout.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   └── CampaignsPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── store.ts
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Installation

### Prerequisites
- Docker and Docker Compose
- OR
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Redis 7

### Using Docker Compose

```bash
cd donor-platform
docker-compose up -d
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
export DATABASE_URL=postgresql://user:password@localhost/donor_db
python -m app.database.init

# Run server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Users
- `POST /api/v1/users/register` - Register new user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/{user_id}/change-password` - Change password

### Campaigns
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns` - List campaigns
- `GET /api/v1/campaigns/{campaign_id}` - Get campaign details
- `PUT /api/v1/campaigns/{campaign_id}` - Update campaign
- `DELETE /api/v1/campaigns/{campaign_id}` - Delete campaign
- `GET /api/v1/campaigns/{campaign_id}/analytics` - Get campaign analytics

### Donations
- `POST /api/v1/donations` - Record donation
- `GET /api/v1/donations` - List donations
- `GET /api/v1/donations/{donation_id}` - Get donation details
- `POST /api/v1/donations/{donation_id}/confirm` - Confirm donation
- `POST /api/v1/donations/{donation_id}/refund` - Refund donation

### Donors
- `POST /api/v1/donors` - Create donor profile
- `GET /api/v1/donors` - List donors
- `GET /api/v1/donors/{donor_id}` - Get donor details
- `GET /api/v1/donors/{donor_id}/statistics` - Get donor statistics
- `POST /api/v1/donors/{donor_id}/tax-certificate` - Generate tax certificate

### Reports
- `GET /api/v1/reports/dashboard/summary` - Dashboard summary
- `GET /api/v1/reports/donors/report` - Donors report
- `GET /api/v1/reports/campaigns/report` - Campaigns report
- `GET /api/v1/reports/donations/report` - Donations report
- `GET /api/v1/reports/financial/summary` - Financial summary

## Configuration

### Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**
```
DATABASE_URL=postgresql://user:password@localhost/donor_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

**Frontend (.env)**
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Building for Production

### Backend

```bash
docker build -f backend/Dockerfile -t donor-platform-backend:latest backend/
```

### Frontend

```bash
docker build -f frontend/Dockerfile -t donor-platform-frontend:latest frontend/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@donorplatform.com or open an issue on GitHub.

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced reporting with PDF export
- [ ] Recurring donations
- [ ] Volunteer management
- [ ] Multi-currency support
- [ ] Payment gateway integration (Stripe, PayPal)
- [ ] Social media sharing
- [ ] AI-powered donor insights
- [ ] GraphQL API
- [ ] Webhook support

---

Built with ❤️ for nonprofits
