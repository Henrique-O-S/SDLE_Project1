function updateQuantity(itemId) {
    const quantityElement = document.getElementById(`quantity_input_${itemId}`);
    const newQuantity = quantityElement.value;

    // Perform any validation or data update logic here (e.g., update the server).
    // For this example, we'll simply update the displayed quantity.

    const quantityDisplayElement = document.getElementById(`quantity_${itemId}`);
    quantityDisplayElement.textContent = newQuantity;
}

