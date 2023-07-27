from django.db import models
from django.utils.translation import gettext_lazy as _
from as3.core.models.base import (
    Courses, Courses, Participations,
    Exercises, Vehicles
)

class ExercisesSelected(models.Model):
    idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, db_column='idCourse', db_index = True)
    idExercise = models.ForeignKey(Exercises, on_delete=models.PROTECT, db_column='idExercise', db_index = True)
    chord = models.FloatField()
    mo = models.FloatField()
    
    class Meta:
        unique_together = (
            ("idCourse", "idExercise")
        )
        db_table = 'api_basic_exercisesselected'
        verbose_name = _('ExerciseSelected')
        verbose_name_plural = _('ExercisesSelected')

class DataExercises(models.Model):
    idParticipation = models.ForeignKey(Participations, on_delete=models.PROTECT, db_column='idParticipation', db_index = True) 
    # idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, db_column='idCourse', db_index = True)
    # idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, db_column='idStudent', db_index = True)
    idExerciseSelected = models.ForeignKey(ExercisesSelected, on_delete=models.PROTECT, null = True, db_column='idExerciseSelected')
    idVehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT, null = True, db_column='idVehicle')
    speedReq = models.IntegerField()
    v1 = models.FloatField()
    v2 = models.FloatField()
    v3 = models.FloatField()
    penalties = models.BooleanField()
    pExercise = models.FloatField(default = 0.0, null = True, blank = True)
    pVehicle = models.FloatField(default = 0.0, null = True, blank = True)
    
    def save(self, *args, **kwargs):
        self.pExercise = round(self.pExercise, 2)
        self.pVehicle = round(self.pVehicle, 2)
        super(DataExercises, self).save(*args, **kwargs)
    class Meta:
        db_table = 'api_basic_dataexercises'
        verbose_name = _('DataExercise')
        verbose_name_plural = _('DataExercises')
        
class DataFinalExercise(models.Model):
    idParticipation = models.ForeignKey(Participations, on_delete=models.PROTECT, db_column='idParticipation', db_index = True) 
    # idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, null = True, db_column='idCourse', db_index = True)
    # idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, null = True, db_column='idStudent', db_index = True)
    idVehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT, null = True, db_column='idVehicle', db_index = True)
    stressLevel = models.IntegerField()
    revSlalom = models.FloatField(blank=True, null=True)
    slalom = models.FloatField(blank=True, null=True)
    laneChange = models.FloatField(blank=True, null=True)
    cones = models.IntegerField()
    gates = models.IntegerField()
    time = models.FloatField()

    def save(self, *args, **kwargs):
        self.revSlalom = round(self.revSlalom, 2)
        self.slalom = round(self.slalom, 2)
        self.laneChange = round(self.laneChange, 2)
        self.time = round(self.time, 2)
        super(DataFinalExercise, self).save(*args, **kwargs)

    class Meta:
        db_table = 'api_basic_datafinalexercise'
        verbose_name = _('DataFinalExercise')
        verbose_name_plural = _('DataFinalExercises')

class DataFinalExerciseComputed(models.Model):
    idParticipation = models.ForeignKey(Participations, on_delete=models.PROTECT, db_column='idParticipation', db_index = True) 
    # idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, null = True, db_column='idCourse', db_index = True)
    # idStudent = models.ForeignKey(Students, on_delete=models.PROTECT, null = True, db_column='idStudent', db_index = True)
    idVehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT, null = True, db_column='idVehicle', db_index = True)
    stress = models.IntegerField()
    revSlalom = models.FloatField()
    slalom = models.FloatField()
    laneChange = models.FloatField()
    penalty = models.IntegerField()
    finalTime = models.FloatField()
    finalResult = models.FloatField()
    
    def save(self, *args, **kwargs):
        self.revSlalom = round(self.revSlalom, 2)
        self.finalTime = round(self.finalTime, 2)
        self.finalResult = round(self.finalResult, 2)
        super(DataFinalExerciseComputed, self).save(*args, **kwargs)
    class Meta:
        # unique_together = (
        #     ("idCourse", "idStudent")
        # )
        db_table = 'api_basic_datafinalexercisepc'
        verbose_name = _('DataFinalExercisePc')
        verbose_name_plural = _('DataFinalExercisesPc')