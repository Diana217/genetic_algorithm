from collections import namedtuple
from random import choice, choices, randrange
from copy import deepcopy
from typing import List

START_POPULATION = 100
ELITE_POPULATION = 10
CHILDREN_PER_GENE = (START_POPULATION - ELITE_POPULATION) // ELITE_POPULATION
MAX_STEPS = 200

weekdays = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
times = {1: "8:40-10:15", 2: "10:35-12:10", 3: "12:20-13:55", }

Classroom = namedtuple("Classroom", "room is_big")
Time = namedtuple("Time", "weekday time")
Teacher = namedtuple("Teacher", "name")
Subject = namedtuple("Subject", "name")
Group = namedtuple("Group", "name")
Lesson = namedtuple("Lesson", "teacher subject group is_lecture per_week")
Gene = namedtuple("Gene", "lessons classrooms times")

Classroom.__repr__ = lambda c: f"{c.room} - {'lecture auditorium' if c.is_big else 'seminar auditorium'}"
Teacher.__repr__ = lambda t: f"{t.name}"
Subject.__repr__ = lambda s: f"{s.name}"
Group.__repr__ = lambda g: f"{g.name}"
Lesson.__repr__ = lambda l: f"{l.teacher} | {l.subject} | {l.group} | " \
                            f"{'Lecture' if l.is_lecture else 'Seminar'} {l.per_week}/week"

def gen_repr(g: Gene):
    output = ""
    for i in range(len(g.lessons)):
        output += f"{g.lessons[i]},   {g.classrooms[i]},   {g.times[i]}\n"
    return output
Gene.__repr__ = lambda g: gen_repr(g)

# data for schedule
classrooms = [
    Classroom(1, True),
    Classroom(2, True),
    Classroom(3, True),
    Classroom(4, False),
    Classroom(5, False),
    Classroom(6, False)
]

schedule = [Time(w, n) for w in range(1, len(weekdays.keys()) + 1)
            for n in range(1, len(times.keys()) + 1)]

teachers = [Teacher(name) for name in
            ("Krivolap", "Hlybovets", "Doroshenko", "Tkachenko", 
             "Shishatska", "Voloshin", "Trotsenko", "Krasovska", 
             "Pashko", "Vergunova", "Bobyl", "Taranukha", 
             "Krak", "Stadnik" )]

subjects = [Subject(name) for name in
            ("Mobile platforms", "Intelligent systems", "Methods of parallel calculations", "Information Technology", 
             "Project management", "Decision making theory", "Systems modeling methods", "English", 
             "Statistical modeling", "Intelligent data analysis", "Complexity of algorithms", "Neural networks",
             "Computer linguistics", "Problems of artificial intelligence", "Software development", "Computer algorithms" )]

groups = [Group(name) for name in
          ("MI", "TTP-41", "TTP-42", "TK-41", "TK-42" )]

lessons = [
    #  MI
    Lesson(teachers[11], subjects[15], groups[0], False, 1),
    Lesson(teachers[10], subjects[11], groups[0], False, 1),
    Lesson(teachers[9], subjects[10], groups[0], True, 2),
    Lesson(teachers[3], subjects[3], groups[0:5], True, 2),
    Lesson(teachers[10], subjects[11], groups[0], True, 1),
    Lesson(teachers[11], subjects[12], groups[0], True, 1),
    Lesson(teachers[0], subjects[3], groups[0:5], False, 1),
    Lesson(teachers[7], subjects[7], groups[0:5], True, 1),
    Lesson(teachers[8], subjects[8], groups[0:5], True, 1),
    Lesson(teachers[6], subjects[6], groups[0:5], True, 1),
    Lesson(teachers[5], subjects[5], groups[0:5], True, 1),
    Lesson(teachers[1], subjects[1], groups[0:5], True, 1),
    #  TTP
    Lesson(teachers[0], subjects[0], groups[1:3], False, 1),
    Lesson(teachers[2], subjects[2], groups[1:3], True, 1),
    Lesson(teachers[3], subjects[0], groups[1:3], True, 1),
    Lesson(teachers[4], subjects[4], groups[1:3], True, 1),
    Lesson(teachers[8], subjects[3], groups[1:3], True, 1),
    #  TK
    Lesson(teachers[12], subjects[13], groups[3:5], True, 1),
    Lesson(teachers[11], subjects[13], groups[3:5], False, 1),
    Lesson(teachers[13], subjects[14], groups[3:5], True, 1),
    Lesson(teachers[13], subjects[14], groups[4:5], False, 1),
    Lesson(teachers[8], subjects[9], groups[3:5], True, 1),
    Lesson(teachers[8], subjects[9], groups[3:5], False, 1),
]

def create_population(lessons_: List[Lesson], classrooms_: List[Classroom], times: List[Time]) -> List[Gene]:
    """Create starting population."""
    population = []
    for _ in range(START_POPULATION):
        g_rooms = choices(classrooms_, k=len(lessons_))
        g_times = choices(times, k=len(lessons_))
        population.append(Gene(lessons_, g_rooms, g_times))

    return population

GROUP_LESSONS_COUNT = sum([len(lesson.group) for lesson in lessons]) #  62
def heuristic(gene: Gene) -> int:
    """Value function for gene."""
    output = 0
    booked_rooms = set()
    teacher_times = set()
    group_time = set()
    for i in range(len(gene.lessons)):
        if gene.lessons[i].is_lecture and not gene.classrooms[i].is_big:
            output += 1
        teacher_times.add((gene.lessons[i].teacher, gene.times[i]))
        booked_rooms.add((gene.classrooms[i], gene.times[i]))
        group_time.update([(str(gr), gene.times[i]) for gr in gene.lessons[i].group])
    output += (len(gene.lessons) - len(booked_rooms))
    output += (len(gene.lessons) - len(teacher_times))
    output += GROUP_LESSONS_COUNT - len(group_time)
    return output


def mutate(gene: Gene, classrooms_: List[Classroom], times: List[Time]) -> Gene:
    """Make random mutations."""
    gene = deepcopy(gene)
    rand_class = randrange(0, len(gene.lessons))
    rand_time = randrange(0, len(gene.lessons))
    gene.classrooms[rand_class] = choice(classrooms_)
    gene.times[rand_time] = choice(times)
    return gene


def children(gens: List[Gene], classrooms_, times):
    new_pop = []
    for g in gens:
        for _ in range(CHILDREN_PER_GENE):
            new_pop.append(mutate(g, classrooms_, times))
    return new_pop

def print_schedule(solution: Gene, ):
    for day in weekdays:
        print('\n' + '=' * 100)
        print(f"{weekdays[day].upper()}")
        for time in times:
            print('\n\n' + times[time])
            for c in classrooms:
                print(f'\n{c}', end='\t\t')
                for i in range(len(solution.lessons)):
                    if solution.times[i].weekday == day and solution.times[i].time == time and \
                            solution.classrooms[i].room == c.room:
                        print(solution.lessons[i], end='')
                        
population = create_population(lessons, classrooms, schedule)

steps = 0
while heuristic(population[0]) and MAX_STEPS-steps:
    population.sort(key=heuristic)
    population = population[:ELITE_POPULATION]
    population += children(population, classrooms, schedule)
    steps += 1
    #print(steps)

solution = population[0]
print_schedule(solution)