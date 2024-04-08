from fastapi import FastAPI, HTTPException, Query, APIRouter
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional

client = MongoClient("mongodb+srv://chirag:chirag123@cluster0.qhxmewv.mongodb.net/")
db = client.get_database("info")
collection = db.get_collection("students")

app = APIRouter()

class Address(BaseModel):
    city: str | None = None
    country: str | None = None

class Student(BaseModel):
    name: str | None = None
    age: int | None = None
    address: Address | None = None

@app.post("/students", status_code=201)
async def create_student(student: Student):
    student_data = student.dict()
    inserted_student = collection.insert_one(student_data)
    return {"id": str(inserted_student.inserted_id)}

@app.get("/students", status_code=200)
async def list_students(country: str = Query(None), age: int = Query(None)):
    filters = {}
    if country:
        filters["address.country"] = country
    if age:
        filters["age"] = {"$gte": age}

    students = list(collection.find(filters, {"_id": 0}))
    return {"data": students}

@app.get("/students/{id}", status_code=200)
async def get_student(id: str):
    student = collection.find_one({"_id": ObjectId(id)}, {"_id": 0})
    if student:
        return student
    raise HTTPException(status_code=404, detail="Student not found")


@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student_update: Student):
    # Check if student exists
    student = collection.find_one({"_id": ObjectId(id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Extract the fields to be updated
    student_data = student_update.model_dump(exclude_unset=True)
    if not student_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # Update the student in the database
    updated_student = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": student_data}
    )
    
    # Check if the update was successful
    
    # if updated_student.modified_count:
    #     return {"message": "Student updated successfully"}
    # else:
    #     raise HTTPException(status_code=500, detail="Failed to update student")
    return {}
   

@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    deleted_student = collection.delete_one({"_id": ObjectId(id)})
    if deleted_student.deleted_count:
        return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail="Student not found")
