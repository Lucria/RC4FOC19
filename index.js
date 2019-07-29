function testFunction() {
    // Functin tested working
    const myElement = document.getElementById("square1");
    myElement.style.backgroundColor = "#FF00FF";
    var database = firebase.database();
    writeUserData("square1", "cyan");
    console.log("DONE");
}

function writeUserData(squareID, colour) {
    firebase.database().ref('bases/' + squareID).set({
        currentColour: colour,
    });
}

function updateBase(squareID, colour) {
    const targetBase = document.getElementById(squareID);
    targetBase.style.backgroundColor = colour;
}

var colourListener = firebase.database().ref("bases/square1/currentColour");
colourListener.on('value', function (snapshot) {
    updateBase(postElement, snapshot.val());
});

var interval = setInterval(function () {
    const squareID = "Placeholder";
    const colour = "Placeholder";
    updateBase(squareID, colour);
}, 5000);