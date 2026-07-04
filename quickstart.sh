#!/bin/bash
# Quick Start Script for Donor Platform

echo "🚀 DONOR PLATFORM - QUICK START"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo -e "${BLUE}[1/5] Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker Compose
echo -e "${BLUE}[2/5] Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose not found. Installing...${NC}"
fi
echo -e "${GREEN}✓ Docker Compose ready${NC}"

# Copy environment file
echo -e "${BLUE}[3/5] Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}   ⚠️  Please edit .env with your configuration:${NC}"
    echo "   - Update RAZORPAY_KEY_ID and RAZORPAY_SECRET_KEY"
    echo "   - Configure SMTP settings for email"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Build Docker images
echo -e "${BLUE}[4/5] Building Docker images...${NC}"
docker-compose build

# Start services
echo -e "${BLUE}[5/5] Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check status
echo ""
echo -e "${GREEN}======================================"
echo "✅ DONOR PLATFORM STARTED SUCCESSFULLY!"
echo "======================================${NC}"
echo ""
echo "🌐 URLs:"
echo "  Frontend:  ${BLUE}http://localhost:3000${NC}"
echo "  Backend:   ${BLUE}http://localhost:8000${NC}"
echo "  API Docs:  ${BLUE}http://localhost:8000/docs${NC}"
echo "  Database:  ${BLUE}localhost:5432${NC}"
echo "  Redis:     ${BLUE}localhost:6379${NC}"
echo ""
echo "📧 Default Admin Account:"
echo "  Email:     ${BLUE}admin@donorplatform.com${NC}"
echo "  Password:  ${BLUE}secure-password-change-this${NC}"
echo ""
echo "💳 Payment Details:"
echo "  Owner:     ${BLUE}Pallapu Vinod${NC}"
echo "  Email:     ${BLUE}vinod1914581@gmail.com${NC}"
echo "  Account:   ${BLUE}42818590419 (SBI)${NC}"
echo ""
echo "📚 Documentation:"
echo "  Setup Guide:            ${BLUE}SETUP.md${NC}"
echo "  Configuration Guide:    ${BLUE}CONFIG_GUIDE.md${NC}"
echo "  Payment Setup:          ${BLUE}PAYMENT_SETUP.md${NC}"
echo "  Owner Configuration:    ${BLUE}PAYMENT_OWNER_CONFIG.md${NC}"
echo "  Project Summary:        ${BLUE}COMPLETION_SUMMARY.md${NC}"
echo ""
echo "🛑 To stop services: ${BLUE}docker-compose down${NC}"
echo "📊 View logs:         ${BLUE}docker-compose logs -f${NC}"
echo ""
