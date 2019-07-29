function updateBase(squareID, colour) {
    const targetBase = document.getElementById(squareID);
    targetBase.style.backgroundColor = colour;
}


let n = 20;

for (let i = 1; i <= n; i++) {
    const element = "square" + i;
    var colourListener = firebase.database().ref("bases/" + element + "/currentColour");
    colourListener.on('value', function (snapshot) {
        updateBase(element, snapshot.val());
    });
}


