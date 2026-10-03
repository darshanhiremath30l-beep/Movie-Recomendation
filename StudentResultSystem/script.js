// Function to update the student photo dynamically based on name input
function updatePhotoPreview() {
    var name = document.getElementById("studentName").value;
    var img = document.getElementById("studentPhotoPreview");
    if (name.trim() === "") {
        img.src = "https://ui-avatars.com/api/?name=Student&size=100&background=ccc&color=fff";
    } else {
        img.src = "https://ui-avatars.com/api/?name=" + encodeURIComponent(name) + "&size=100&background=random";
    }
}

// Function to validate marks
function validateMarks(marksArray) {
    for (var i = 0; i < marksArray.length; i++) {
        var mark = marksArray[i];
        // Ensure marks are valid numbers and between 0 and 100
        if (isNaN(mark) || mark < 0 || mark > 100) {
            return false;
        }
    }
    return true;
}

// Function for total calculation
function calculateTotal(marksArray) {
    var total = 0;
    for (var i = 0; i < marksArray.length; i++) {
        total += marksArray[i];
    }
    return total;
}

// Function for average calculation
function calculateAverage(total, count) {
    return total / count;
}

// Function to classify grade based on control statements
function determineGrade(average) {
    if (average >= 90) {
        return "A";
    } else if (average >= 80) {
        return "B";
    } else if (average >= 70) {
        return "C";
    } else if (average >= 60) {
        return "D";
    } else {
        return "F";
    }
}

// Main function to process the results
function processResults(event) {
    // Prevent default form submission
    event.preventDefault();

    // 1. Get student details from the DOM (Keyboard input)
    var name = document.getElementById("studentName").value;
    var rollNo = document.getElementById("rollNo").value;

    // 2. Accept marks through keyboard input and store in array
    var subjects = ["Mathematics", "Science", "English", "History", "Computer Science"];
    var marks = [
        parseFloat(document.getElementById("mathMarks").value),
        parseFloat(document.getElementById("sciMarks").value),
        parseFloat(document.getElementById("engMarks").value),
        parseFloat(document.getElementById("histMarks").value),
        parseFloat(document.getElementById("compMarks").value)
    ];

    // 3. Add validation for marks (Expressions and control statements)
    if (!validateMarks(marks)) {
        alert("Error: All marks must be numeric values between 0 and 100.");
        return;
    }

    // 4. Calculate total and average
    var totalMarks = calculateTotal(marks);
    var averageMarks = calculateAverage(totalMarks, marks.length);

    // 5. Determine Grade classification
    var finalGrade = determineGrade(averageMarks);

    // 6. Object creation and modification to store the final result
    var studentResult = {
        studentName: name,
        rollNumber: rollNo,
        subjectMarks: {},
        total: totalMarks,
        average: averageMarks.toFixed(2),
        grade: finalGrade
    };

    // Dynamically adding subject marks to the object using a loop
    for (var i = 0; i < subjects.length; i++) {
        studentResult.subjectMarks[subjects[i]] = marks[i];
    }

    // 7. Display the final formatted result report on the webpage (Screen output)
    displayReport(studentResult, subjects);
}

// Function to generate a formatted result report
function displayReport(resultObj, subjects) {
    var container = document.getElementById("reportContainer");
    container.className = ""; // Remove 'hidden' class

    var photoSrc = document.getElementById("studentPhotoPreview").src;

    // Construct the HTML report using string concatenation
    var htmlContent = "<div class='report-header'>";
    htmlContent += "<img src='" + photoSrc + "' alt='Student Photo' style='border-radius: 50%; width: 80px; height: 80px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);' />";
    htmlContent += "<h2>Official Result Report</h2>";
    htmlContent += "<p><strong>Name:</strong> " + resultObj.studentName + " | <strong>Roll No:</strong> " + resultObj.rollNumber + "</p>";
    htmlContent += "</div>";

    htmlContent += "<table class='report-table'>";
    htmlContent += "<tr><th>Subject</th><th>Marks Obtained</th></tr>";
    
    // Loop through subjects to populate table rows
    for (var i = 0; i < subjects.length; i++) {
        var subjectName = subjects[i];
        var subjectMark = resultObj.subjectMarks[subjectName];
        htmlContent += "<tr><td>" + subjectName + "</td><td>" + subjectMark + " / 100</td></tr>";
    }
    htmlContent += "</table>";

    // Summary table
    htmlContent += "<table class='summary-table'>";
    htmlContent += "<tr><td>Total Marks:</td><td>" + resultObj.total + " / 500</td></tr>";
    htmlContent += "<tr><td>Average Percentage:</td><td>" + resultObj.average + "%</td></tr>";
    htmlContent += "<tr><td>Final Grade:</td><td class='grade-" + resultObj.grade + "'>" + resultObj.grade + "</td></tr>";
    htmlContent += "</table>";

    // Output to screen
    container.innerHTML = htmlContent;
}

// Function to clear the report when form is reset
function clearReport() {
    var container = document.getElementById("reportContainer");
    container.innerHTML = "";
    container.className = "hidden";
    
    // Reset the photo preview
    document.getElementById("studentPhotoPreview").src = "https://ui-avatars.com/api/?name=Student&size=100&background=ccc&color=fff";
}
