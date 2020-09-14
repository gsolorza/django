// ref: http://stackoverflow.com/a/1293163/2343
// This will parse a delimited string into an array of
// arrays. The default delimiter is the comma, but this
// can be overriden in the second argument.
function CSVToArray( strData, strDelimiter ){
    // Check to see if the delimiter is defined. If not,
    // then default to comma.
    strDelimiter = (strDelimiter || ",");

    // Create a regular expression to parse the CSV values.
    var objPattern = new RegExp(
        (
            // Delimiters.
            "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +

            // Quoted fields.
            "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

            // Standard fields.
            "([^\"\\" + strDelimiter + "\\r\\n]*))"
        ),
        "gi"
        );


    // Create an array to hold our data. Give the array
    // a default empty first row.
    var arrData = [[]];

    // Create an array to hold our individual pattern
    // matching groups.
    var arrMatches = null;


    // Keep looping over the regular expression matches
    // until we can no longer find a match.
    while (arrMatches = objPattern.exec( strData )){

        // Get the delimiter that was found.
        var strMatchedDelimiter = arrMatches[ 1 ];

        // Check to see if the given delimiter has a length
        // (is not the start of string) and if it matches
        // field delimiter. If id does not, then we know
        // that this delimiter is a row delimiter.
        if (
            strMatchedDelimiter.length &&
            strMatchedDelimiter !== strDelimiter
            ){

            // Since we have reached a new row of data,
            // add an empty row to our data array.
            arrData.push( [] );

        }

        var strMatchedValue;

        // Now that we have our delimiter out of the way,
        // let's check to see which kind of value we
        // captured (quoted or unquoted).
        if (arrMatches[ 2 ]){

            // We found a quoted value. When we capture
            // this value, unescape any double quotes.
            strMatchedValue = arrMatches[ 2 ].replace(
                new RegExp( "\"\"", "g" ),
                "\""
                );

        } else {

            // We found a non-quoted value.
            strMatchedValue = arrMatches[ 3 ];

        }


        // Now that we have our value string, let's add
        // it to the data array.
        arrData[ arrData.length - 1 ].push( strMatchedValue );
    }

    // Return the parsed data.
    return( arrData );
}


if (document.getElementById("file") !== null) {
    document.getElementById("file").oninput = function() { 
        var filename = document.querySelector("#file").files[0].name;
        document.querySelector("#file-label").innerHTML = filename;
        command_list = document.querySelector("#command-list")

        while (command_list.firstChild) {
            command_list.removeChild(command_list.firstChild);
        }

        var element = document.querySelector("#file").files[0].text();
        element.then((value) => {
            var result = CSVToArray(value);
            result.shift();
            var deviceTypeList = []
            result.forEach((item) => {
                if (item[0].length > 1) {
                    var deviceType = item[0];
                    deviceTypeList.push(deviceType);
                }
            });
            var d = new Set(deviceTypeList);
            d.forEach(device => {
                createCommandSelection("select", "#command-list", {
                    id: "select_commands_"+device,
                    multiple: true,
                    name: device,
                    "data-actions-box": "true"
                });
                createCommandSelection("optgroup", "#select_commands_"+device, {
                    id: "opt_commands_"+device,
                    label: "commands_"+device,
                    name: device,
                });
                createCommandList("option", "#opt_commands_"+device, device);
                $('select').selectpicker();
            }
        )})
    }
}

function createCommandList(newElement, parent, device_type) {
    
    var commands = JSON.parse(document.getElementById('commands').textContent);
    commands[device_type].forEach((command) => {
        const span = document.createElement(newElement);
        const node = document.createTextNode(command);
        span.appendChild(node);
        const element = document.querySelector(parent);
        element.appendChild(span);
    })
}

function createCommandSelection(newElement, parent, attributes="") {
    const span = document.createElement(newElement);
    if(attributes) {
        Object.keys(attributes).forEach(attribute => {
            span.setAttribute(attribute, attributes[attribute])
        })
    } 
    const element = document.querySelector(parent);
    element.appendChild(span);
}

function createDownloadLink(newElement, parent, attributes="", text="") {
    const span = document.createElement(newElement);
    if(attributes) {
        Object.keys(attributes).forEach(attribute => {
            span.setAttribute(attribute, attributes[attribute])
        })
    } 
    const element = document.querySelector(parent);
    if(text) {
        const textNode = document.createTextNode(text);
        span.appendChild(textNode)
    }
    element.appendChild(span);
}

function publishResult(text) {
    const span = document.createElement("small");
    const node = document.createTextNode(text);
    span.appendChild(node);
    const element = document.querySelector("#result");
    element.appendChild(span);
}


function updateProgress(progressUrl) {
    var progressBar = document.getElementById("progress-bar");
    var state = document.getElementById("state");
    fetch(progressUrl)
        .then(response => response.json())
        .then(json =>  {
            if (json.state === "PENDING") {
                state.innerHTML = "Connecting to Devices";
                setTimeout(updateProgress, 500, progressUrl);
            } else if (json.state != "SUCCESS" ) {  
                state.innerHTML = "Connecting to Devices";          
                progressBar.style.width = json.progress_percentage + "%";
                progressBar.innerHTML = json.progress_percentage + "%";

                const progress = json.progress;
                const elementResult = document.querySelector("#result");
                
                while (elementResult.firstChild) {
                    elementResult.removeChild(elementResult.firstChild);
                }

                publishResult(progress)

                setTimeout(updateProgress, 500, progressUrl);
            } else if (json.state === "SUCCESS") {
                var metaData = JSON.parse(document.getElementById('metaData').textContent);
                state.innerHTML = `State: ${json.state}`;
                progressBar.style.width = "100%";
                progressBar.innerHTML = "100%";
                fileName = metaData.clientName + "_" + metaData.taskId
                createDownloadLink("a", "#download", {
                    href: "/device/download?filename="+fileName+".zip",
                    id: "downloadFileLink"
                })
                createDownloadLink("button", "#downloadFileLink", {
                    type: "button",
                    class: "btn btn-outline-secondary download"
                }, "Download")
                window.scrollTo(0, document.querySelector("#downloadFileLink").offsetTop);
            }
        })
        .catch(err => console.error(err));       
}

if (document.getElementById("metaData") !== null) {
    var metaData = JSON.parse(document.getElementById('metaData').textContent);
    var progressUrl = `http://localhost:8000/device/progress?task_id=${metaData.taskId}`;
    updateProgress(progressUrl);
}

if (document.querySelector("#error-message") !== null) {
    $(document).ready(function(){
        $("#error-message").fadeOut(5000);
      });
}

