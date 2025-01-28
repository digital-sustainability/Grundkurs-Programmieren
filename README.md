# Unterlagen

## Einführung

In diesem Projekt werden die Unterlagen für den Grundkurs Programmieren der Universität Bern verwaltet. Diese sind Semester unabhängig, sprich alle Ordner, und dementsprechend Verlinkungen, haben den Aufbau WEEK_XX. Beim Erstellen der Semester Unterlagen (siehe nächster Punkt) werden diese mit den tatsächlichen Wochen des Semesters ersetzt. Weiter werden alle Musterlöschen entfernt.

## Semester Unterlagen erstellen

Um die Unterlagen für das aktuelle Semester zu erstellen müssen folgende Schritte durchgeführt werden:

1. Unter folgendem [Link](https://github.com/grundkurs-programmieren/unterlagen/settings/variables/actions) muss eine JSON Datei hinterlegt werden für das Mapping WEEK_XX -> DD.MM.YYYY mit dem Namen `SEMESTER_WEEKS_XX`
2. Unter folgendem [Link](https://github.com/grundkurs-programmieren/unterlagen/actions/workflows/create-student-version.yml) kann ein neuer Workflow gestartet werden (Run Workflow)
3. Der abgeschlossene Workflow generiert/überschreibt den Ordner student_versions/{SEMESTER} mit den Unterlagen für das aktuelle Semester.
   <br> Zusätzlich generiert der Workflow drei verschiedene Artefakte, die auch die Unterlagen für das Semester beinhalten.

## Arbeiten mit dem Projekt

### Renkulab (empfohlen)

Starten Sie eine neue Session. Denken Sie daran am Ende der Session Ihre Arbeit via Git Commit **und** Push zu speichern.

### Lokal

Sollten Sie **lokal** an den Unterlagen arbeiten, dann führen Sie vor dem ersten Git Commit **unbedingt** folgenden Befehl aus:

```bash
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=INFO
```

Damit wird sichergestellt, dass die Output Zellen der Notebooks nicht in unserem Repository landen.
Mehr Informationen finden Sie [hier](https://stackoverflow.com/a/64513642).
