from as3.core.models import *
from dateutil.relativedelta import relativedelta
from datetime import date

# TODO: CHANGE TOP_RESULTS QUERY*****

def get_student_performers_query(company_id, course_id, options):
    query = f"""
    SELECT * FROM (
        SELECT student.id sid, student.firstName sfname, 
        student.lastName slast, student.studentId ssid,
        grop.id gid, grop.name gname, team.id tid, team.name tname,
        course.id course_id, course.eventDate event_date,
        venue.id venue_id, venue.name venue_name, 
        country.name countryname, country.units countryunits,
        program.id program_id, program.name program_name,
        final_exercise.finalResult finalResult,
        final_exercise.slalom slalom, final_exercise.laneChange laneChange,
        final_exercise.revSlalom revSlalom, final_exercise.stress stress,
        final_exercise.penalty penalty, final_exercise.finalTime finaltime,
        company.id, company.name, dense_rank() over ( 
            partition by participation.idStudent order by course.eventDate desc )
        AS _RANK

        FROM {Participations._meta.db_table} participation
        INNER JOIN {DataFinalExerciseComputed._meta.db_table} AS final_exercise ON final_exercise.idParticipation = participation.id
        INNER JOIN {Courses._meta.db_table} course ON participation.idCourse=course.id
        INNER JOIN {Companies._meta.db_table} company ON participation.idCompany=company.id
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id

        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam

        WHERE 
            {f" company.id={company_id}" if company_id else ""}
            {f" AND " if company_id and course_id  else ""} {f" course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
        ORDER BY student.studentId ASC 
    ) AS top_results WHERE top_results._RANK = 1;
    """
    query = query.strip("\t \n")
    return query


def get_courses_query(company_id, options):
    query = f"""
            SELECT DISTINCT(course.id), course.eventDate, program.id, program.name, 
            venue.id, venue.name, country.id, country.name, country.units, count(student.id) student_count
                FROM {Participations._meta.db_table} participation 
                INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
                INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
                INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
                INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
                INNER JOIN {Venues._meta.db_table} venue ON venue.id = course.idVenue
                LEFT JOIN {Countries._meta.db_table} country ON venue.idCountry = country.id
                LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
                LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
                LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
                LEFT JOIN {Teams._meta.db_table} team ON team.id = team_students.idTeam
            WHERE
                {f"company.id={company_id}" if company_id else ""}
                {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' AND '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
                {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
                {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
                {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
                {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
            GROUP BY course.id HAVING student_count > 0
            ORDER BY course.eventDate DESC;
    """
    return query

def get_performances_query(company_id, course_id, options, ex = "Slalom"):
    query = f"""
    SELECT * FROM (
    SELECT CONCAT(student.firstName, ' ', student.lastName) sname, 
      Max(data_ex.pVehicle)*100 pVehicle, count(*) tries,
      dense_rank() over ( partition by participation.idStudent
         order by course.eventDate desc ) AS _RANK

    FROM {Participations._meta.db_table} participation 
    INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
    INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
    INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
    INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
    INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
    INNER JOIN {DataExercises._meta.db_table} data_ex on  data_ex.idParticipation = participation.id
    INNER JOIN {ExercisesSelected._meta.db_table} ex_sel ON ex_sel.id = data_ex.idExerciseSelected
    INNER JOIN {Exercises._meta.db_table} ex ON ex.id = ex_sel.idExercise 
     
    LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
    LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
    LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
    LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
    WHERE
        ex.name='{ex}'
        {f"AND company.id={company_id}" if company_id else ""}
        {f" AND course.id={course_id}" if course_id else ""}
        {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
        {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
        {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
        {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
        {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
            
        GROUP BY student.id
        ORDER BY student.firstName, student.lastName ASC 
    ) AS results WHERE results._RANK = 1 ;
    """
    query = query.strip("\t \n")
    return query

def get_performamces_avg_query(company_id, course_id, options, ex = "Slalom"):
    query = f"""
    WITH squery AS (
      SELECT * FROM (
        SELECT CONCAT(student.firstName, ' ', student.lastName), 
        Max(data_ex.pVehicle)*100 pVehicle, count(*) tries,
         dense_rank() over ( partition by participation.idStudent
         order by course.eventDate desc ) AS _RANK

        FROM {Participations._meta.db_table} participation 
        INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {DataExercises._meta.db_table} data_ex on data_ex.idParticipation = participation.id
        INNER JOIN {ExercisesSelected._meta.db_table} ex_sel ON ex_sel.id = data_ex.idExerciseSelected
        INNER JOIN {Exercises._meta.db_table} ex ON ex.id = ex_sel.idExercise 
        
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            ex.name='{ex}'
            {f"AND company.id={company_id}" if company_id else ""}
            {f" AND course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
            
        GROUP BY student.id
        ORDER BY student.firstName
    ) AS results WHERE results._RANK = 1
   )
    
    SELECT AVG(pVehicle), AVG(tries)
    FROM squery;
    """
    return query

def get_performances_gp_met_std_query(company_id, course_id, options, ex = "Slalom"):
    query = f"""
    WITH squery AS (
        SELECT * FROM (
        SELECT student.id, count(*) gp_count,
            dense_rank() over ( partition by participation.idStudent
            order by course.eventDate desc ) AS _RANK
                
        FROM {Participations._meta.db_table} participation 
        INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {DataExercises._meta.db_table} data_ex on data_ex.idParticipation = participation.id
        INNER JOIN {ExercisesSelected._meta.db_table} ex_sel ON ex_sel.id = data_ex.idExerciseSelected
        INNER JOIN {Exercises._meta.db_table} ex ON ex.id = ex_sel.idExercise 
        
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            ex.name='{ex}' 
            AND data_ex.pVehicle >= 0.8 AND data_ex.pExercise >= 0.01 AND data_ex.penalties = 0

            {f"AND company.id={company_id}" if company_id else ""}
                {f" AND course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
            
        GROUP BY student.id
        ORDER BY student.firstName
        ) AS top_results WHERE top_results._RANK = 1
    )
    SELECT  AVG(gp_count)
    FROM squery;
    """
    return query

def get_performers_average_query(company_id, course_id, options):
    query = f"""
    SELECT favg, mresult, scount, coursecount FROM (
        SELECT AVG(final_exercise.finalResult) favg, MAX(final_exercise.finalResult) mresult, 
		  COUNT(*) scount, Count(DISTINCT(course.id)) coursecount,
        dense_rank() over ( partition by participation.idStudent order by course.eventDate desc ) AS _RANK

        FROM {Participations._meta.db_table} participation
        INNER JOIN {DataFinalExerciseComputed._meta.db_table} AS final_exercise ON final_exercise.idParticipation = participation.id
        INNER JOIN {Courses._meta.db_table} course ON participation.idCourse=course.id
        INNER JOIN {Companies._meta.db_table} company ON participation.idCompany=company.id
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id

        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            {f"company.id={company_id}" if company_id else ""}
            {f" AND " if company_id and course_id  else ""} {f" course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
    ) AS top_results WHERE top_results._RANK = 1;
    """
    query = query.strip("\t \n")
    return query


def get_performers_stress_avg_query(company_id, course_id, options):
    query = f"""
    SELECT * FROM (
        SELECT final_exercise.stress, AVG(final_exercise.finalResult),
        dense_rank() over ( partition by participation.idStudent order by course.eventDate desc ) AS _RANK

        FROM {Participations._meta.db_table} participation
        INNER JOIN {DataFinalExerciseComputed._meta.db_table} AS final_exercise ON final_exercise.idParticipation = participation.id
        INNER JOIN {Courses._meta.db_table} course ON participation.idCourse=course.id
        INNER JOIN {Companies._meta.db_table} company ON participation.idCompany=company.id
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            {f"company.id={company_id}" if company_id else ""}
            {f" AND " if company_id and course_id  else ""} {f" course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
        GROUP BY final_exercise.stress
    ) AS top_results WHERE top_results._RANK = 1; 
    """
    query = query.strip("\t \n")
    return query


def get_performers_passcount_query(company_id, course_id, options):
    query = f"""
    SELECT * FROM (
        SELECT COUNT(*),
        dense_rank() over ( partition by participation.idStudent order by course.eventDate desc ) AS _RANK

        FROM {Participations._meta.db_table} participation
        INNER JOIN {DataFinalExerciseComputed._meta.db_table} AS final_exercise ON final_exercise.idParticipation = participation.id
        INNER JOIN {Courses._meta.db_table} course ON participation.idCourse=course.id
        INNER JOIN {Companies._meta.db_table} company ON participation.idCompany=company.id
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        
        WHERE
            final_exercise.finalResult >= 80
            {f"AND company.id={company_id}" if company_id else ""}
            {f" AND course.id={course_id}" if course_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
        ) AS top_results WHERE top_results._RANK = 1;
    """
    query = query.strip("\t \n")
    return query


def get_expired_students_query(company_id, options):
    last_18months = date.today() - relativedelta(months=18)
    query = f"""
    SELECT * FROM (
        SELECT  student.id, CONCAT(student.firstName, ' ', student.lastName), MAX(course.eventDate) AS last_course_date,
        dense_rank() over ( partition by participation.idStudent order by course.eventDate desc ) AS _RANK

        FROM {Participations._meta.db_table} participation 
        INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            {f"company.id={company_id}" if company_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
        GROUP BY student.id
        HAVING last_course_date <= '{last_18months}'
        ORDER BY student.firstName, student.lastName ASC 
    ) AS top_results WHERE top_results._RANK = 1 
    """
    query = query.strip("\t \n")
    return query

def get_to_be_expired_students_query(company_id, options):
    last_18months = date.today() - relativedelta(months=18)
    last_12months = date.today() - relativedelta(months=12)
    
    query = f"""
    SELECT * FROM (
        SELECT student.id, CONCAT(student.firstName, ' ', student.lastName), MAX(course.eventDate) last_course_date,
        dense_rank() over ( partition by participation.idStudent order by course.eventDate desc ) AS _RANK
        FROM {Participations._meta.db_table} participation 
        INNER JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
        INNER JOIN {Students._meta.db_table} student ON student.id = participation.idStudent 
        INNER JOIN {Courses._meta.db_table} course ON course.id = participation.idCourse
        INNER JOIN {Programs._meta.db_table} program ON  program.id = course.idProgram
        INNER JOIN {Venues._meta.db_table} venue ON  venue.id = course.idVenue
        INNER JOIN {Countries._meta.db_table} country ON  venue.idCountry = country.id
        LEFT JOIN {GroupStudents._meta.db_table} group_students ON  group_students.idStudent = student.id
        LEFT JOIN {Groups._meta.db_table} grop ON grop.id = group_students.idGroup
        LEFT JOIN {TeamStudents._meta.db_table} team_students ON  team_students.idStudent = student.id
        LEFT JOIN {Teams._meta.db_table} team ON  team.id = team_students.idTeam
        WHERE
            {f"company.id={company_id}" if company_id else ""}
            {f"AND course.eventDate BETWEEN '{options['event_date_start_obj']}' and '{options['event_date_end_obj']}'" if options['event_date_start_obj'] and options['event_date_end_obj'] else ""}
            {f"AND program.id in ({options['programs']})" if options['programs'] else ""}
            {f"AND venue.id in ({options['locations']})" if options['locations'] else ""}
            {f"AND grop.id in ({options['groups']})" if options['groups'] else ""}
            {f"AND team.id in ({options['teams']})" if options['teams'] else ""}
        GROUP BY student.id
        HAVING last_course_date >= '{last_18months}' AND last_course_date <= '{last_12months}'
        ORDER BY student.firstName, student.lastName ASC 
    ) AS top_results WHERE top_results._RANK = 1 
    """
    query = query.strip("\t \n")
    return query
 