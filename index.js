function testFunction() {
    // Functin tested working
    const myElement = document.getElementById("square8");
    myElement.style.backgroundColor = "#FF00FF";
}

function updateBase(squareID, colour) {
    const targetBase = document.getElementById(squareID);
    targetBase.style.backgroundColor = colour;
}

var interval = setInterval(function () {
    const squareID = "Placeholder";
    const colour = "Placeholder";
    updateBase(squareID, colour);
}, 5000);