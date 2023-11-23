let prefix = "PAGE-"

function turnOffAll(){
	const pages = document.querySelectorAll("."+prefix);
	for (const page of pages) {
		console.log(page)
		setPageOff(page)
	}
}

function setPageOff(element){
	if (element.style.display === "block") {
	  element.style.display = "none";
	}
}

function setPageOn(element){
	turnOffAll()
	if (element.style.display === "none") {
	  element.style.display = "block";
	}
}

function changePage(id){
	let element = document.getElementById(prefix+id)
	setPageOn(element);
}
