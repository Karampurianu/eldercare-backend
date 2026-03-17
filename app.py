from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np

app = FastAPI(title="Elderly Fall Detection System")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates (for website)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load YOLO model
MODEL_PATH = "runs/detect/fall_detection_combined3/weights/best.pt"
model = YOLO(MODEL_PATH)

# ---------------- WEBSITE ROUTES ---------------- #

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin123":
        return templates.TemplateResponse("upload.html", {"request": request})
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password"}
    )


@app.post("/detect-fall", response_class=HTMLResponse)
async def website_detect(request: Request, file: UploadFile = File(...)):

    contents = await file.read()
    img_array = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "result": "Invalid Image"}
        )

    fall_detected = run_model(frame)

    message = "🚨 Fall Detected" if fall_detected else "✅ Normal"

    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "result": message}
    )


# ---------------- MOBILE API ROUTE ---------------- #

@app.post("/api/detect-fall")
async def mobile_detect(file: UploadFile = File(...)):

    contents = await file.read()
    img_array = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        return JSONResponse({"status": "error"})

    fall_detected = run_model(frame)

    if fall_detected:
        return JSONResponse({"status": "fall"})
    else:
        return JSONResponse({"status": "normal"})


# ---------------- COMMON MODEL FUNCTION ---------------- #

def run_model(frame):
    results = model(frame, conf=0.5)

    for r in results:
        if r.boxes is None:
            continue

        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls == 0 and conf > 0.6:
                return True

    return False