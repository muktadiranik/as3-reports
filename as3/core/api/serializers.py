from rest_framework.serializers import ModelSerializer, ReadOnlyField, Serializer
from rest_framework import serializers
from as3.core.models import Courses,  Exercises, ExercisesSelected, Vehicles, Comments, \
    Countries, Venues, Programs, DataExercises, DataFinalExercise, Students, \
    Companies, Users
    
class Userserilaizer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("username", "id", "email", "active", "name", )
  
class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'


class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicles
        fields = ["id", "name", "latAcc", "type", "make", "image"]


class ExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercises
        fields = '__all__'


class ExercisesSelectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExercisesSelected
        fields = '__all__'

class CommentssSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'


class VenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = (
            "id", "name", "state", "address1", 
            "address2", "phone", "email"
        )


class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = '__all__'


class ProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = ("id", "name", "durationDays")


class DataExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExercises
        fields = '__all__'


class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'


class FullDataExercisesSerializer(serializers.ModelSerializer):
    idStudent = StudentsSerializer(read_only=True)

    class Meta:
        model = DataExercises
        fields = '__all__'


class DataFinalExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFinalExercise
        fields = '__all__'


class CompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ("id", "name", "contact")

