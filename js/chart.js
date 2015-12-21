function clicked(row, column) {
   switch (document.getElementsByTagName("table")[0].rows[row].cells[column].getAttribute("bgcolor")) {
    case "white":
        document.getElementsByTagName("table")[0].rows[row].cells[column].setAttribute("bgcolor", "lime");
        break;
    case "lime":
        document.getElementsByTagName("table")[0].rows[row].cells[column].setAttribute("bgcolor", "red");
        break;
    case "red":
        document.getElementsByTagName("table")[0].rows[row].cells[column].setAttribute("bgcolor", "white");
        break;
      }
    }
  
function getTest() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "cgi/chartboard.py?action=load_chart&chartname=hello", true);
    xhr.onload = function (e) {
	if (xhr.readyState === 4) {
	    if (xhr.status === 200) {
		console.log(xhr.responseText);
            } else {
		console.error(xhr.statusText);
            }
	}
    };
    xhr.onerror = function (e) {
	console.error(xhr.statusText);
    }; 
    xhr.send(null);}
  
  
function createChart(chartname) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "cgi/chartboard.py?action=create_chart", true);
    xhr.onload = function (e) {
	if (xhr.readyState === 4) {
	    if (xhr.status === 200) {
		console.log(xhr.responseText);
            } else {
		console.error(xhr.statusText);
            }
	}
    };
    xhr.onerror = function (e) {
	console.error(xhr.statusText);
    }; 
    xhr.send('{"CHARTNAME":' + '"' + chartname + '"}');}
  
function createColumn(chartname, columnname) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "cgi/chartboard.py?action=create_column", true);
    xhr.onload = function (e) {
	if (xhr.readyState === 4) {
	    if (xhr.status === 200) {
		console.log(xhr.responseText);
            } else {
		console.error(xhr.statusText);
            }
	}
    };
    xhr.onerror = function (e) {
	console.error(xhr.statusText);
    }; 
    xhr.send('{"CHARTNAME":' + '"' + chartname + '",' + '"COLUMNNAME":' + '"' + columnname + '"}');}
