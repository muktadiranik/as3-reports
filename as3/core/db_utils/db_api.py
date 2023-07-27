from as3.core.models import (
    Companies, Students, Courses, 
    Programs, Venues, Vehicles, Countries
)

def get_companies():    
    items = []
    query = Companies.objects.filter(active = True)
    for company in query:
        items.append({
            "id": company.id,
            "name": company.name
        })
    return items


def course_exists(event_date, program_name, venue_name):
    if not event_date or not program_name or not venue_name:
        return False
    
    program = Programs.objects.filter(name = program_name)
    if not program.exists():
        return False
    
    venue = Venues.objects.filter(name = venue_name)
    if not venue.exists():
        return False
    
    course = Courses.objects.filter(eventDate = event_date, idProgram = program[0], idVenue = venue[0])
    if course.exists():
        return True
   
    return False


def get_vehicles(): 
    items = []
    query = Vehicles.objects.filter(active = True)
    for vehicle in query:
        items.append({
            "id": vehicle.id,
            "name": vehicle.name,
            "make": vehicle.make,
            "latAcc": vehicle.latAcc,
            "model": vehicle.model,
        })
    return items

        
def get_students():
    items = []
    for student in Students.objects.filter(active = True):
        items.append({
            "id": student.id,
            "student_id": student.studentId,
            "first_name": student.firstName,
            "last_name": student.lastName,
            "birthday": student.birthday,
        })
    return items
        
        
def get_countries():
    items = []
    query = Countries.objects.filter(active = True)
    for country in query:
        items.append({
            "id": country.id,
            "name": country.name,
            "unit": country.unit
        })
    return items