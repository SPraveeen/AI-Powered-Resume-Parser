from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json

# Import our modules
from database import get_db, Resume
from models import ParsedResume, ResumeResponse
from resume_parser import ResumeParser
from file_processor import FileProcessor

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Resume Parser",
    description="An intelligent resume parsing system that extracts structured data from resumes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parser
parser = ResumeParser()

@app.get("/")
async def root():
    return {
        "message": "AI-Powered Resume Parser API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload-resume/",
            "get_resume": "/resume/{resume_id}",
            "list_resumes": "/resumes/",
            "search": "/search/"
        }
    }

@app.post("/upload-resume/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume file"""
    
    # Validate file type
    allowed_extensions = ['pdf', 'docx', 'txt']
    file_extension = file.filename.lower().split('.')[-1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        text = FileProcessor.process_file(file_content, file.filename)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in the uploaded file")
        
        # Parse the resume
        parsed_data = parser.parse_resume(text)
        
        # Save to database
        db_resume = Resume(
            filename=file.filename,
            original_text=text,
            parsed_data=parsed_data,
            name=parsed_data['contact_info']['name'],
            email=parsed_data['contact_info']['email'],
            phone=parsed_data['contact_info']['phone'],
            skills=', '.join(parsed_data['skills']) if parsed_data['skills'] else None,
            experience_years=parsed_data['experience_years']
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        return ResumeResponse(
            message="Resume uploaded and parsed successfully",
            resume_id=db_resume.id,
            parsed_data=parsed_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/resume/{resume_id}", response_model=ParsedResume)
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Get a specific resume by ID"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Convert parsed_data JSON to proper format
    parsed_data = resume.parsed_data or {}
    
    return ParsedResume(
        id=resume.id,
        filename=resume.filename,
        name=resume.name,
        email=resume.email,
        phone=resume.phone,
        skills=parsed_data.get('skills', []),
        experience=parsed_data.get('experience', []),
        education=parsed_data.get('education', []),
        experience_years=resume.experience_years,
        created_at=resume.created_at
    )

@app.get("/resumes/", response_model=List[ParsedResume])
async def list_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all resumes with pagination"""
    
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    
    result = []
    for resume in resumes:
        parsed_data = resume.parsed_data or {}
        result.append(ParsedResume(
            id=resume.id,
            filename=resume.filename,
            name=resume.name,
            email=resume.email,
            phone=resume.phone,
            skills=parsed_data.get('skills', []),
            experience=parsed_data.get('experience', []),
            education=parsed_data.get('education', []),
            experience_years=resume.experience_years,
            created_at=resume.created_at
        ))
    
    return result

@app.get("/search/")
async def search_resumes(
    skill: str = None,
    min_experience: int = None,
    name: str = None,
    db: Session = Depends(get_db)
):
    """Search resumes by various criteria"""
    
    query = db.query(Resume)
    
    if skill:
        query = query.filter(Resume.skills.ilike(f"%{skill}%"))
    
    if min_experience:
        query = query.filter(Resume.experience_years >= min_experience)
    
    if name:
        query = query.filter(Resume.name.ilike(f"%{name}%"))
    
    resumes = query.all()
    
    results = []
    for resume in resumes:
        parsed_data = resume.parsed_data or {}
        results.append({
            "id": resume.id,
            "filename": resume.filename,
            "name": resume.name,
            "email": resume.email,
            "skills": parsed_data.get('skills', []),
            "experience_years": resume.experience_years
        })
    
    return {"results": results, "count": len(results)}

@app.delete("/resume/{resume_id}")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
