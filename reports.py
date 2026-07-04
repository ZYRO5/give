from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, Donation, Campaign, Donor
from app.utils.helpers import GeneratorUtilities, LoggerUtilities
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
logger = LoggerUtilities.setup_logger(__name__)


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary."""
    total_donors = db.query(func.count(Donor.id)).scalar()
    total_campaigns = db.query(func.count(Campaign.id)).scalar()
    total_donations = db.query(func.count(Donation.id)).scalar()
    total_raised = db.query(func.sum(Donation.amount)).scalar() or 0
    
    return {
        "total_donors": total_donors or 0,
        "total_campaigns": total_campaigns or 0,
        "total_donations": total_donations or 0,
        "total_raised": total_raised
    }


@router.get("/donors/report")
def get_donors_report(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get donors report."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    donors = db.query(Donor).filter(
        Donor.created_at >= start_date,
        Donor.created_at <= end_date
    ).all()
    
    report = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_donors": len(donors),
        "total_donated": sum(d.total_donated for d in donors),
        "average_donation_per_donor": sum(d.total_donated for d in donors) / len(donors) if donors else 0,
        "top_donors": [
            {
                "id": d.id,
                "name": db.query(User).filter(User.id == d.user_id).first().first_name,
                "total_donated": d.total_donated
            }
            for d in sorted(donors, key=lambda x: x.total_donated, reverse=True)[:10]
        ]
    }
    
    return report


@router.get("/campaigns/report")
def get_campaigns_report(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get campaigns report."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    campaigns = db.query(Campaign).filter(
        Campaign.created_at >= start_date,
        Campaign.created_at <= end_date
    ).all()
    
    report = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_campaigns": len(campaigns),
        "total_target_amount": sum(c.target_amount for c in campaigns),
        "total_raised": sum(c.raised_amount for c in campaigns),
        "average_campaign_raised": sum(c.raised_amount for c in campaigns) / len(campaigns) if campaigns else 0,
        "top_campaigns": [
            {
                "id": c.id,
                "title": c.title,
                "target": c.target_amount,
                "raised": c.raised_amount,
                "progress": (c.raised_amount / c.target_amount * 100) if c.target_amount > 0 else 0
            }
            for c in sorted(campaigns, key=lambda x: x.raised_amount, reverse=True)[:10]
        ]
    }
    
    return report


@router.get("/donations/report")
def get_donations_report(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """Get donations report."""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    donations = db.query(Donation).filter(
        Donation.created_at >= start_date,
        Donation.created_at <= end_date
    ).all()
    
    by_status = {}
    by_payment_method = {}
    
    for donation in donations:
        status = donation.status.value
        by_status[status] = by_status.get(status, 0) + donation.amount
        
        method = donation.payment_method.value
        by_payment_method[method] = by_payment_method.get(method, 0) + donation.amount
    
    report = {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_donations": len(donations),
        "total_amount": sum(d.amount for d in donations),
        "average_donation": sum(d.amount for d in donations) / len(donations) if donations else 0,
        "largest_donation": max((d.amount for d in donations), default=0),
        "by_status": by_status,
        "by_payment_method": by_payment_method
    }
    
    return report


@router.get("/financial/summary")
def get_financial_summary(db: Session = Depends(get_db)):
    """Get financial summary."""
    donations = db.query(Donation).filter(Donation.status == "completed").all()
    
    total_revenue = sum(d.amount for d in donations)
    
    # Group by month
    monthly_data = {}
    for donation in donations:
        month = donation.created_at.strftime("%Y-%m")
        if month not in monthly_data:
            monthly_data[month] = 0
        monthly_data[month] += donation.amount
    
    return {
        "total_revenue": total_revenue,
        "monthly_breakdown": monthly_data
    }


@router.get("/demographics/report")
def get_demographics_report(db: Session = Depends(get_db)):
    """Get demographics report."""
    donors = db.query(Donor).all()
    
    by_type = {}
    for donor in donors:
        dtype = donor.donor_type
        if dtype not in by_type:
            by_type[dtype] = {"count": 0, "total_donated": 0}
        by_type[dtype]["count"] += 1
        by_type[dtype]["total_donated"] += donor.total_donated
    
    return {
        "donor_types": by_type
    }


@router.get("/category/report")
def get_category_report(db: Session = Depends(get_db)):
    """Get category report."""
    campaigns = db.query(Campaign).all()
    
    by_category = {}
    for campaign in campaigns:
        cat = campaign.category
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total_raised": 0, "total_target": 0}
        by_category[cat]["count"] += 1
        by_category[cat]["total_raised"] += campaign.raised_amount
        by_category[cat]["total_target"] += campaign.target_amount
    
    return {
        "categories": by_category
    }


@router.get("/growth/report")
def get_growth_report(months: int = 12, db: Session = Depends(get_db)):
    """Get growth report."""
    growth_data = []
    
    for i in range(months):
        date = datetime.utcnow() - timedelta(days=30*i)
        month_key = date.strftime("%Y-%m")
        
        donors_count = db.query(func.count(Donor.id)).filter(
            func.to_char(Donor.created_at, 'YYYY-MM') == month_key
        ).scalar() or 0
        
        donations_count = db.query(func.count(Donation.id)).filter(
            func.to_char(Donation.created_at, 'YYYY-MM') == month_key
        ).scalar() or 0
        
        growth_data.append({
            "month": month_key,
            "donors": donors_count,
            "donations": donations_count
        })
    
    return {"growth": sorted(growth_data, key=lambda x: x["month"])}


@router.post("/generate/monthly")
def generate_monthly_report(year: int, month: int, db: Session = Depends(get_db)):
    """Generate monthly report."""
    from app.models.models import Report
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    donations = db.query(Donation).filter(
        Donation.created_at >= start_date,
        Donation.created_at <= end_date
    ).all()
    
    campaigns = db.query(Campaign).filter(
        Campaign.created_at >= start_date,
        Campaign.created_at <= end_date
    ).all()
    
    donors = db.query(Donor).filter(
        Donor.created_at >= start_date,
        Donor.created_at <= end_date
    ).all()
    
    report = Report(
        id=GeneratorUtilities.generate_uuid(),
        title=f"Monthly Report - {start_date.strftime('%B %Y')}",
        report_type="monthly",
        start_date=start_date,
        end_date=end_date,
        total_donors=len(donors),
        total_campaigns=len(campaigns),
        total_donations=len(donations),
        total_raised=sum(d.amount for d in donations),
        average_donation=sum(d.amount for d in donations) / len(donations) if donations else 0,
        largest_donation=max((d.amount for d in donations), default=0),
        generated_at=datetime.utcnow()
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    logger.log_audit("system", "report_generated", {"report_id": report.id})
    return {"message": "Report generated successfully", "report_id": report.id}


@router.get("/export/csv")
def export_report_csv(report_type: str, db: Session = Depends(get_db)):
    """Export report as CSV."""
    import csv
    import io
    
    output = io.StringIO()
    
    if report_type == "donations":
        donations = db.query(Donation).all()
        writer = csv.writer(output)
        writer.writerow(["ID", "Amount", "Status", "Payment Method", "Date"])
        for d in donations:
            writer.writerow([d.id, d.amount, d.status, d.payment_method, d.created_at])
    
    elif report_type == "campaigns":
        campaigns = db.query(Campaign).all()
        writer = csv.writer(output)
        writer.writerow(["ID", "Title", "Target", "Raised", "Status", "Date"])
        for c in campaigns:
            writer.writerow([c.id, c.title, c.target_amount, c.raised_amount, c.status, c.created_at])
    
    elif report_type == "donors":
        donors = db.query(Donor).all()
        writer = csv.writer(output)
        writer.writerow(["ID", "Type", "Total Donated", "Donation Count", "Date"])
        for d in donors:
            writer.writerow([d.id, d.donor_type, d.total_donated, d.donation_count, d.created_at])
    
    return {"csv": output.getvalue()}
