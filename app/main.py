import os
import time
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dbuser:StrongPasswd2026!@postgres:5432/apartment_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Resident(Base):
    __tablename__ = "residents"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    apartment_no = Column(String(20))
    phone = Column(String(15))
    service_fee = Column(Numeric(10, 2), default=500000)
    fee_status = Column(String(20), default="Chưa thanh toán")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    resident_name = Column(String(100))
    apartment_no = Column(String(20))
    content = Column(Text)
    status = Column(String(20), default="Đang xử lý")

# Tự động kết nối DB khi sẵn sàng
for _ in range(15):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception:
        time.sleep(2)

app = FastAPI(title="Hệ thống Quản lý Chung cư")
Instrumentator().instrument(app).expose(app)
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    residents = db.query(Resident).all()
    notifications = db.query(Notification).order_by(Notification.id.desc()).all()
    complaints = db.query(Complaint).order_by(Complaint.id.desc()).all()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "residents": residents, 
        "notifications": notifications, 
        "complaints": complaints
    })

@app.post("/resident/add")
def add_resident(
    full_name: str = Form(...), apartment_no: str = Form(...), 
    phone: str = Form(...), service_fee: float = Form(500000), 
    fee_status: str = Form("Chưa thanh toán"), db: Session = Depends(get_db)
):
    res = Resident(full_name=full_name, apartment_no=apartment_no, phone=phone, service_fee=service_fee, fee_status=fee_status)
    db.add(res)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/notification/add")
def add_notification(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    notif = Notification(title=title, content=content)
    db.add(notif)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/complaint/add")
def add_complaint(resident_name: str = Form(...), apartment_no: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    comp = Complaint(resident_name=resident_name, apartment_no=apartment_no, content=content, status="Đang xử lý")
    db.add(comp)
    db.commit()
    return RedirectResponse(url="/", status_code=303)
