function subTicket(parentWrapper) {
	let target = parentWrapper.getElementsByClassName("ticket-value").item(0);
	let price = parseFloat(parentWrapper.parentElement.parentElement.getElementsByClassName("ticket-price").item(0).innerHTML);
	let num = parseFloat(parentWrapper.parentElement.parentElement.getElementsByClassName("ticket-num").item(0).innerHTML);
	let purchase_num = document.getElementById("purchase-num");
	let purchase_price = document.getElementById("purchase-price");
	let book_num = document.getElementById("book-num");
	
	if(target.value <= 4) {
		parentWrapper.getElementsByClassName("add-ticket").item(0).disabled = false;
	}
	if(target.value <= 1) {
		parentWrapper.getElementsByClassName("sub-ticket").item(0).disabled = true;
	}
	target.value--;
	
	purchase_num.innerHTML = (parseFloat(purchase_num.innerHTML) - 1);
	book_num.innerHTML = (parseFloat(book_num.innerHTML) - 1);
	purchase_price.innerHTML = `${(parseFloat(purchase_price.innerHTML) - price).toFixed(2)} \u20AC`;
	
	if ((parseFloat(book_num.innerHTML) - 1) < 0) {
		document.getElementById("purchase_button").disabled = true;
		document.getElementById("book_button").disabled = true;
	}
}

function addTicket(parentWrapper) {
	let target = parentWrapper.getElementsByClassName("ticket-value").item(0);
	let price = parseFloat(parentWrapper.parentElement.parentElement.getElementsByClassName("ticket-price").item(0).innerHTML);
	let num = parseFloat(parentWrapper.parentElement.parentElement.getElementsByClassName("ticket-num").item(0).innerHTML);
	let purchase_num = document.getElementById("purchase-num");
	let purchase_price = document.getElementById("purchase-price");
	let book_num = document.getElementById("book-num");
	
	if(target.value >= 0) {
		parentWrapper.getElementsByClassName("sub-ticket").item(0).disabled = false;
	}
	if(target.value >= 3) {
		parentWrapper.getElementsByClassName("add-ticket").item(0).disabled = true;
	}
	target.value++;
	
	purchase_num.innerHTML = (parseFloat(purchase_num.innerHTML) + 1);
	book_num.innerHTML = (parseFloat(book_num.innerHTML) + 1);
	purchase_price.innerHTML = `${(parseFloat(purchase_price.innerHTML) + price).toFixed(2)} \u20AC`;
	
	if ((parseFloat(book_num.innerHTML) + 1) > 0) {
		document.getElementById("purchase_button").disabled = false;
		document.getElementById("book_button").disabled = false;
	}
}

function showQR(qrcode) {
	qrModalImage.setAttribute("src",qrcode);
}